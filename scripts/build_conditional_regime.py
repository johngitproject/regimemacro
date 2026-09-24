"""Lecture conditionnelle : le sens du chomage attendu depend du regime.

Pour chaque rapport emploi (UNEMP released, 48) :
  - jambe chomage : ecart = forecast - previous, sens_u (hausse/baisse/stable, seuil 0.1)
  - jambe inflation appariee : dernier ecart CPI headline YoY connu AVANT le rapport
    (as-of strict, jamais de lookahead) -> sens_pi (seuil 0.2), sinon plat
  - quadrant : uH/uB/uS x piH/piB/piS  (ex : uH+piB = easing propre, uH+piH = dilemme)
  - regime prevalent (fed_stance a la veille) : stance_label, side, real_gap,
    phase Fed (dernier geste : hiking/hold/easing), guidance en vigueur
  - surprise du rapport (hawkish/dovish/inline, UNEMP inverse) — distingue
    l'attendu (ecart) du constate (surprise), ex : ete-24 = stable attendu + hausse constatee
  - outcomes marches : forwards ES/NQ 5/20/60 sessions depuis le close RTH J
    (J doit exister, jamais interpole) + variation 10Y 20/60j depuis J

Sorties :
  donnees/regime/conditional_regime.csv (48 lignes)
  donnees/regime/conditional_regime_report.md (stats poolees u-hausse vs reste,
      quadrant x regime avec N affiches, n<5 = episode uniquement + 4 archetypes)

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/build_conditional_regime.py
"""
import csv
import os
from statistics import mean, median

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
SRC = os.path.join(REGIME, "sources")


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(x):
    try:
        return float(x) if x not in (None, "") else None
    except ValueError:
        return None


def side(label):
    if label in ("restrictif", "nettement restrictif"):
        return "R"
    if label in ("accommodant", "nettement accommodant"):
        return "A"
    return "N" if label == "neutre" else ""


def main():
    cal = load_csv(os.path.join(REGIME, "calendar_macro_2022_2026.csv"))
    une = sorted([r for r in cal if r["event_type"] == "UNEMP" and r["status"] == "released"],
                 key=lambda r: r["date_et"])
    cpi = sorted([r for r in cal if r["event_type"] == "CPI" and r["variant"] == "headline_yoy"
                  and r["status"] == "released"], key=lambda r: r["date_et"])
    fed = sorted([r for r in cal if r["event_type"] == "FED" and r["variant"] == "target_upper"
                  and r["status"] == "released"], key=lambda r: r["date_et"])
    stance = sorted(load_csv(os.path.join(REGIME, "fed_stance.csv")),
                    key=lambda r: (r["date_et"], r["variant"]))
    idx = load_csv(os.path.join(REGIME, "index_daily.csv"))
    px = load_csv(os.path.join(SRC, "market_pricing_daily.csv"))
    closes = {}
    for r in idx:
        closes.setdefault(r["inst"], {})[r["date"]] = float(r["rth_close"])
    days = {i: sorted(v) for i, v in closes.items()}
    pos = {i: {d: k for k, d in enumerate(dd)} for i, dd in days.items()}
    tnx = {r["date"]: float(r["tnx"]) for r in px if r.get("tnx")}
    tdays = sorted(tnx)
    tpos = {d: k for k, d in enumerate(tdays)}

    rows = []
    for u in une:
        J = u["date_et"][:10]
        # arrondi : les soustractions flottantes (ex 3.8-3.7=0.0999...) cassent
        # les seuils exacts (0.1) sans cela — bug constate sur jan-24/dec-25
        ue = round(num(u["forecast"]) - num(u["previous"]), 4)
        sens_u = "H" if ue >= 0.1 else ("B" if ue <= -0.1 else "S")
        # jambe inflation : dernier CPI headline connu strictement avant J 08:30
        cands = [r for r in cpi if r["date_et"] < u["date_et"]]
        if cands:
            c = cands[-1]
            pe = round(num(c["forecast"]) - num(c["previous"]), 4)
            sens_pi = "H" if pe >= 0.2 else ("B" if pe <= -0.2 else "S")
            pi_ref = f"{c['date_et'][:10]} ({c['previous']}->{c['forecast']})"
        else:
            pe, sens_pi, pi_ref = None, "?", ""
        s = num(u["surprise"])
        sens_s = "" if s is None else ("hawkish" if s <= -0.1 else ("dovish" if s >= 0.1 else "inline"))
        # regime : dernier event <= J, phase = dernier geste Fed < J
        st = [r for r in stance if r["date_et"][:10] <= J]
        st = st[-1] if st else None
        fz = [r for r in fed if r["date_et"] < u["date_et"]]
        if fz:
            dec = num(fz[-1]["actual"]) - num(fz[-1]["previous"])
            phase = "hiking" if dec > 0 else ("easing" if dec < 0 else "hold")
            phase_ref = fz[-1]["date_et"][:10]
        else:
            phase, phase_ref = "?", ""
        out = {"date_et": u["date_et"], "ref_period": u["ref_period"],
               "u_prev": u["previous"], "u_fc": u["forecast"], "u_actual": u["actual"],
               "u_ecart": f"{ue:+g}", "u_sens": sens_u,
               "pi_ref": pi_ref, "pi_ecart": "" if pe is None else f"{pe:+g}",
               "pi_sens": sens_pi, "quadrant": f"u{sens_u}+pi{sens_pi}",
               "stance_label": st["stance_label"] if st else "",
               "side": side(st["stance_label"]) if st else "",
               "real_gap_bps": st["real_gap_bps"] if st else "",
               "fed_phase": phase, "fed_phase_ref": phase_ref,
               "guidance": f"{st['guidance_stance']} ({st['guidance_date']})" if st else "",
               "surprise": u["surprise"], "sens_surprise": sens_s}
        for inst, col in (("ES", "es"), ("NQ", "nq")):
            if J not in pos[inst]:
                out.update({f"{col}_fwd{h}": "" for h in (5, 20, 60)})
                continue
            i0 = pos[inst][J]
            for h in (5, 20, 60):
                out[f"{col}_fwd{h}"] = "" if i0 + h >= len(days[inst]) else \
                    f"{(closes[inst][days[inst][i0 + h]] / closes[inst][J] - 1) * 100:+.2f}"
        if J in tpos:
            i0 = tpos[J]
            for h in (20, 60):
                out[f"tnx_chg{h}"] = "" if i0 + h >= len(tdays) else \
                    f"{(tnx[tdays[i0 + h]] - tnx[J]) * 100:+.0f}"
        else:
            out["tnx_chg20"] = out["tnx_chg60"] = ""
        rows.append(out)

    with open(os.path.join(REGIME, "conditional_regime.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"ecrit conditional_regime.csv : {len(rows)} rapports emploi")

    def agg(vals):
        vals = [v for v in vals if v is not None]
        if len(vals) < 5:
            return f"N={len(vals)} (episode uniquement)"
        return f"N={len(vals)} moy={mean(vals):+.2f} med={median(vals):+.2f}"

    lines = ["# Chomage attendu en hausse : ca veut dire quoi selon le regime ?",
             "",
             "48 rapports emploi. Quadrant = sens_u (seuil 0.1) x sens_pi CPI headline as-of (seuil 0.2).",
             "Outcomes : forwards ES/NQ 5/20/60j depuis close RTH J + 10Y 20/60j. n<5 = episode, pas de stat.",
             ""]
    lines.append("## Hausse du chomage attendue (uH) vs reste")
    for col, lbl in (("es_fwd20", "ES 20j %"), ("es_fwd60", "ES 60j %"),
                     ("nq_fwd20", "NQ 20j %"), ("tnx_chg20", "10Y 20j bp")):
        uh = [num(r[col]) for r in rows if r["u_sens"] == "H"]
        rest = [num(r[col]) for r in rows if r["u_sens"] != "H"]
        lines.append(f"- {lbl} | uH : {agg(uh)} || reste : {agg(rest)}")
    lines.append("")
    lines.append("## Quadrant x side (forwards ES 20j, puis 60j)")
    quads = sorted({r["quadrant"] for r in rows})
    for q in quads:
        for sd in ("R", "A", "N", ""):
            sub = [r for r in rows if r["quadrant"] == q and r["side"] == sd]
            if not sub:
                continue
            v20 = [num(r["es_fwd20"]) for r in sub]
            v60 = [num(r["es_fwd60"]) for r in sub]
            tag = f"{q} / side {sd or '?'}"
            if len([v for v in v20 if v is not None]) < 5:
                dates = ", ".join(r["date_et"][:10] for r in sub)
                lines.append(f"- {tag} : N={len(sub)} (episode : {dates})")
            else:
                lines.append(f"- {tag} : ES20 {agg(v20)} | ES60 {agg(v60)}")
    lines.append("")
    lines.append("## 4 archetypes : meme signal uH, 4 sens differents selon regime")
    arch = [("2022-11-04", "uH attendu + hiking + inflation qui plafonne (piS) = fin de cycle : "
             "le marche lit la fin des hikes -> haussier malgre le signal 'faiblesse'"),
            ("2024-01-05", "uH attendu + plateau restrictif + inflation qui baisse (piS) : "
             "easing en vue -> haussier"),
            ("2024-12-06", "uH attendu + inflation attendue EN HAUSSE (piH 2.4->2.6) en plein "
             "easing : dilemme stagflation -> baissier + taux qui montent"),
            ("2025-12-16", "uH attendu + piH (2.9->3.1), stance deja accommodante : "
             "plus de marge dovish -> chop puis negatif a 60j")]
    for d, note in arch:
        r = next((x for x in rows if x["date_et"].startswith(d)), None)
        if r is None:
            lines.append(f"- {d} : absent (!)")
            continue
        lines.append(f"- {d} [{r['quadrant']} / {r['side']}, phase {r['fed_phase']}, "
                     f"guidance {r['guidance']}] : {note}")
        lines.append(f"  u {r['u_prev']}->{r['u_fc']} (actual {r['u_actual']}), "
                     f"pi [{r['pi_ref']}], surprise {r['surprise']} ({r['sens_surprise']})")
        lines.append(f"  ES fwd 5/20/60 : {r['es_fwd5']} / {r['es_fwd20']} / {r['es_fwd60']} %, "
                     f"10Y 20/60j : {r['tnx_chg20']} / {r['tnx_chg60']} bp")
    lines.append("")
    rep = os.path.join(REGIME, "conditional_regime_report.md")
    with open(rep, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"ecrit {rep}")


if __name__ == "__main__":
    main()
