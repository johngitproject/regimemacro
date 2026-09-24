"""Le marche price-t-il le changement attendu ? Drifts 20j/5j/1j avant l'event.

Filtre d'entree (releases avec vrai changement attendu) :
  |forecast - previous| >= seuil de materialite, sinon exclue (bruit de consensus).
  Seuils : CPI/PCE 0.2 pt, NFP 20 K, UNEMP 0.1 pt, FED 0.25 pt.
  Sens attendu : hausse / baisse.

Pour chaque release retenue (J = date event, V = dernier close < J) :
  - drifts ES/NQ (%) et TNX (bp) sur 20j / 5j / 1j avant V, sessions de trading
    (jours manquants = horizon vide, jamais interpole)
  - sens surprise hawkish/dovish/inline (seuils CPI/PCE 0.1, UNEMP 0.1 inverse,
    NFP 30K, FED 0.1) + alignement vs derive 20j (AVEC/CONTRE/n.d.)
  - moves jour J (close J vs V ; J manquant = vide)

Colonnes drift : driftES20/5/1, driftNQ20/5/1 (%), driftTNX20/5/1 (bp),
chacune avec sa base (<debut>_<fin> ou vide).

Analyses :
  1. Drift moyen par sens attendu x horizon x actif + concordance 10Y
     (signe drift == direction taux attendue ? hausse -> up sauf UNEMP)
  2. Correlation drift 5j/1j x surprise signee, par type d'event
  3. Amplitude jour J croisee (changement attendu x alignement 20j)

Sorties :
  donnees/regime/pre_drift_change.csv (une ligne par release avec changement attendu)
  donnees/regime/pre_drift_change_report.md

Stats par event (dedup date+type : headline_yoy > core_yoy > mom).

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/build_predrift_change.py
"""
import csv
import os
from statistics import mean, median

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
SRC = os.path.join(REGIME, "sources")

MAT = {"CPI": 0.2, "PCE": 0.2, "NFP": 20.0, "UNEMP": 0.1, "FED": 0.25}
SEUIL = {"CPI": 0.1, "PCE": 0.1, "NFP": 30.0, "UNEMP": 0.1, "FED": 0.1}
FLAT_BP = 15.0
PRIO = {"headline_yoy": 0, "core_yoy": 1, "change_K": 0, "rate": 0,
        "target_upper": 0, "headline_mom": 2, "core_mom": 2}


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(x):
    try:
        return float(x) if x not in (None, "") else None
    except ValueError:
        return None


def before(lst, day):
    c = [d for d in lst if d < day]
    return c[-1] if c else None


def drift(day, n, series, lut, plut):
    """Rend (valeur_veille, valeur_debut) ou ("", "") si indisponible."""
    v = before(series, day)
    if v is None or plut[v] < n:
        return "", ""
    return lut[v], lut[series[plut[v] - n]]


def main():
    cal = [r for r in load_csv(os.path.join(REGIME, "calendar_macro_2022_2026.csv"))
           if r["status"] == "released" and r["forecast"] not in (None, "")
           and r["previous"] not in (None, "")]
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
    for r in sorted(cal, key=lambda x: (x["date_et"], x["variant"])):
        J = r["date_et"][:10]
        fc, pv = num(r["forecast"]), num(r["previous"])
        ecart = fc - pv
        if abs(ecart) < MAT[r["event_type"]]:
            continue  # pas de vrai changement attendu
        out = {"date_et": r["date_et"], "event_type": r["event_type"],
               "variant": r["variant"], "ref_period": r["ref_period"],
               "previous": r["previous"], "forecast": r["forecast"],
               "actual": r["actual"], "ecart_attendu": f"{ecart:+g}",
               "sens_attendu": "hausse" if ecart > 0 else "baisse",
               "surprise": r["surprise"], "unit": r["unit"]}
        s = num(r["surprise"])
        sev = SEUIL[r["event_type"]]
        if s is None:
            out["sens"] = ""
        elif r["event_type"] == "UNEMP":
            out["sens"] = "hawkish" if s <= -sev else ("dovish" if s >= sev else "inline")
        else:
            out["sens"] = "hawkish" if s >= sev else ("dovish" if s <= -sev else "inline")
        for inst in ("ES", "NQ"):
            vdate = before(days[inst], J)
            for h in (20, 5, 1):
                col = f"drift{inst}{h}"
                if vdate is None or pos[inst][vdate] < h:
                    out[col], out[col + "_base"] = "", ""
                    continue
                d0 = days[inst][pos[inst][vdate] - h]
                out[col] = f"{(closes[inst][vdate] / closes[inst][d0] - 1) * 100:+.2f}"
                out[col + "_base"] = f"{d0}>{vdate}"
        for h in (20, 5, 1):
            vdate = before(tdays, J)
            col = f"driftTNX{h}"
            if vdate is None or tpos[vdate] < h:
                out[col], out[col + "_base"] = "", ""
                continue
            d0 = tdays[tpos[vdate] - h]
            out[col] = f"{(tnx[vdate] - tnx[d0]) * 100:+.0f}"
            out[col + "_base"] = f"{d0}>{vdate}"
        d20 = num(out["driftTNX20"])
        drift20 = "" if d20 is None else ("dovish" if d20 <= -FLAT_BP else
                                          ("hawkish" if d20 >= FLAT_BP else "flat"))
        out["drift20"] = drift20
        if out["sens"] in (None, "", "inline") or not drift20 or drift20 == "flat":
            out["alignement"] = "n.d."
        elif (drift20 == "dovish") != (out["sens"] == "dovish"):
            out["alignement"] = "CONTRE"
        else:
            out["alignement"] = "AVEC"
        for inst, col in (("ES", "jday_es"), ("NQ", "jday_nq")):
            v = before(days[inst], J)
            out[col] = "" if (v is None or J not in pos[inst]) else \
                f"{(closes[inst][J] / closes[inst][v] - 1) * 100:+.2f}"
        tv = before(tdays, J)
        out["jday_tnx"] = "" if (tv is None or J not in tpos) else \
            f"{(tnx[J] - tnx[tv]) * 100:+.0f}"
        rows.append(out)

    with open(os.path.join(REGIME, "pre_drift_change.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"ecrit pre_drift_change.csv : {len(rows)} lignes (releases avec changement attendu)")

    # --- dedup par event pour les stats (headline > core > mom) ---
    best = {}
    for r in rows:
        k = (r["date_et"], r["event_type"])
        if k not in best or PRIO.get(r["variant"], 9) < PRIO.get(best[k]["variant"], 9):
            best[k] = r
    ev = sorted(best.values(), key=lambda x: (x["date_et"], x["event_type"]))
    print(f"events uniques : {len(ev)}")

    # --- controles : cas connus ---
    print("controles :")
    for d, v in (("2022-07-13", "CPI"), ("2022-11-10", "CPI"), ("2025-02-12", "CPI"),
                 ("2024-09-18", "FED")):
        for r in ev:
            if r["date_et"].startswith(d) and r["event_type"] == v:
                print(f"  {d} {v}: {r['sens_attendu']} ({r['previous']}->{r['forecast']}) "
                      f"es20={r['driftES20']}% es5={r['driftES5']}% es1={r['driftES1']}% "
                      f"tnx20={r['driftTNX20']}bp tnx5={r['driftTNX5']}bp tnx1={r['driftTNX1']}bp "
                      f"-> {r['alignement']} J: es={r['jday_es']}%")

    # --- analyse 1 : drift moyen par sens attendu ---
    def agg(vals):
        vals = [v for v in vals if v is not None]
        if len(vals) < 5:
            return f"N={len(vals)} (insuffisant)"
        return f"N={len(vals)} moy={mean(vals):+.2f} med={median(vals):+.2f}"

    lines = ["# Le marche price-t-il le changement attendu ? (20j / 5j / 1j)",
             "",
             "Filtre : |forecast - previous| >= seuil (CPI/PCE 0.2, NFP 20K, UNEMP 0.1, FED 0.25).",
             "Drifts ancrés veille (dernier close < J), sessions de trading, jamais interpolés.",
             ""]
    for evt in ("CPI", "PCE", "NFP", "UNEMP", "FED"):
        sub = [r for r in ev if r["event_type"] == evt]
        if not sub:
            continue
        lines.append(f"## {evt} ({len(sub)} events avec changement attendu)")
        for sens in ("hausse", "baisse"):
            s2 = [r for r in sub if r["sens_attendu"] == sens]
            lines.append(f"### attendu {sens} : N={len(s2)}")
            for col, lbl in (("driftES20", "ES 20j %"), ("driftES5", "ES 5j %"),
                             ("driftES1", "ES 1j %"), ("driftTNX20", "10Y 20j bp"),
                             ("driftTNX5", "10Y 5j bp"), ("driftTNX1", "10Y 1j bp")):
                lines.append(f"- {lbl} : {agg([num(r[col]) for r in s2])}")
        att = []
        for r in sub:
            d20 = num(r["driftTNX20"])
            if d20 is None or abs(d20) < FLAT_BP:
                continue
            want_up = (r["sens_attendu"] == "hausse") != (r["event_type"] == "UNEMP")
            att.append((d20 > 0) == want_up)
        if att:
            lines.append(f"- concordance 10Y 20j (signe drift == sens taux attendu) : "
                         f"{sum(att)}/{len(att)} = {sum(att) / len(att):.0%}")
        lines.append("")

    # --- analyse 2 : correlation drift x surprise signee par type ---
    lines.append("## Correlation drift x surprise signee (surprise signee : UNEMP inversee)")
    for evt in ("CPI", "PCE", "NFP", "UNEMP", "FED"):
        sub = [r for r in ev if r["event_type"] == evt]
        parts = []
        for col in ("driftTNX5", "driftTNX1", "driftES5", "driftES1"):
            xy = [(num(r[col]), float(r["surprise"]) * (-1 if r["event_type"] == "UNEMP" else 1))
                  for r in sub if num(r[col]) is not None and num(r["surprise"]) is not None]
            if len(xy) < 5:
                parts.append(f"{col}: N={len(xy)} (insuffisant)")
                continue
            mx, my = mean([a for a, _ in xy]), mean([b for _, b in xy])
            cov = sum((a - mx) * (b - my) for a, b in xy) / len(xy)
            sx = (sum((a - mx) ** 2 for a, _ in xy) / len(xy)) ** 0.5
            sy = (sum((b - my) ** 2 for _, b in xy) / len(xy)) ** 0.5
            parts.append(f"{col}: N={len(xy)} r={cov / sx / sy:+.2f}" if sx and sy else f"{col}: sd=0")
        lines.append(f"- {evt} : " + " | ".join(parts))
    lines.append("")

    # --- analyse 3 : amplitude jour J (changement attendu x alignement) ---
    lines.append("## Amplitude jour J par alignement (sous-ensemble avec changement attendu)")
    for col, lbl, seu in (("jday_es", "ES jour J (%)", 0.5), ("jday_nq", "NQ jour J (%)", 0.5),
                          ("jday_tnx", "10Y jour J (bp)", 5.0)):
        lines.append(f"### {lbl}")
        for sel in ("CONTRE", "AVEC", "n.d."):
            vals = [abs(num(r[col])) for r in ev
                    if r["alignement"] == sel and num(r[col]) is not None]
            if len(vals) < 5:
                lines.append(f"- {sel} : N={len(vals)} (insuffisant)")
            else:
                lines.append(f"- {sel} : N={len(vals)} |J| moy={mean(vals):+.2f} "
                             f"med={median(vals):+.2f} gros(>{seu:g})="
                             f"{sum(1 for v in vals if v > seu) / len(vals):.0%}")
        lines.append("")
    rep = os.path.join(REGIME, "pre_drift_change_report.md")
    with open(rep, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"ecrit {rep}")


if __name__ == "__main__":
    main()
