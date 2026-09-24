"""Joint seuils SEP + surprises macro + pricing -> stance + dashboard.

Deux jauges (parametres affiches, usage interpretatif, pas un signal) :
  1) Taylor 1999 contemporain (reference) :
       taylor = r* + pi + 0.5 * (pi - 2) + 1.0 * (u* - u)
       pi = dernier core PCE YoY publie ; montre le retard/avance vs la regle
       (ex : mi-2022 prescription ~9 % = behind the curve, lecture standard).
  2) Stance operative = ecart de taux REEL ex-ante a r* reel :
       real_gap = (target_mid - pi_exp) - (r* - 2)   [en points]
       pi_exp = mediane SEP inflation PCE de l'annee en cours (previsions Fed),
                repli = dernier core PCE actual (attentes adaptatives, flagge).
     labels : >= +1.00 nettement restrictif | +0.25..+1.00 restrictif |
              -0.25..+0.25 neutre | -1.00..-0.25 accommodant | < -1.00 nettement accommodant

Anti-lookahead strict : target prevailing = dernier FED strictement avant eval
(sauf lignes FED : champ previous = pre-decision) ; pi/u = derniers publies
(release datetime <= eval) ; thresholds = dernier SEP <= jour d'eval ;
pricing = dernier close strictement avant le jour d'eval.

Entrees : calendar_macro_2022_2026.csv, fed_thresholds.csv, fed_dots.csv,
          fomc_guidance.csv, sources/market_pricing_daily.csv
Sortie  : donnees/regime/fed_stance.csv (1 ligne par event released)

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/build_fed_layer.py
"""
import csv
import json
import os

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


def label(stance):
    if stance is None:
        return ""
    if stance >= 100:
        return "nettement restrictif"
    if stance >= 25:
        return "restrictif"
    if stance > -25:
        return "neutre"
    if stance > -100:
        return "accommodant"
    return "nettement accommodant"


def main():
    cal = sorted([r for r in load_csv(os.path.join(REGIME, "calendar_macro_2022_2026.csv"))
                  if r["status"] == "released"],
                 key=lambda r: (r["date_et"], r["variant"]))
    thr = load_csv(os.path.join(REGIME, "fed_thresholds.csv"))
    dots = load_csv(os.path.join(REGIME, "fed_dots.csv"))
    guid = {g["date_et"][:10]: g for g in load_csv(os.path.join(REGIME, "fomc_guidance.csv"))}
    pricing = sorted(load_csv(os.path.join(SRC, "market_pricing_daily.csv")),
                     key=lambda r: r["date"])

    lr = {}  # meeting_date -> {var LR: median}
    for r in thr:
        if r["horizon"] == "LR":
            lr.setdefault(r["meeting_date"], {})[r["var"]] = float(r["median"])
    dot_cy = {}  # meeting_date -> {horizon: median} (ffr, hors LR)
    pce_cy = {}  # meeting_date -> {horizon: median} (pce headline, hors LR)
    for r in thr:
        if r["horizon"] == "LR":
            continue
        if r["var"] == "ffr":
            dot_cy.setdefault(r["meeting_date"], {})[r["horizon"]] = float(r["median"])
        elif r["var"] == "pce":
            pce_cy.setdefault(r["meeting_date"], {})[r["horizon"]] = float(r["median"])
    sep_days = sorted(lr)

    fed_rows = sorted([r for r in cal if r["event_type"] == "FED" and r["variant"] == "target_upper"],
                      key=lambda r: r["date_et"])
    # seed : target pre-2022 (0-0.25 depuis mars 2020) depuis l'historique FRED vendoré
    with open(os.path.join(SRC, "fred-us-macro-history.json"), encoding="utf-8") as fh:
        hist = json.load(fh)
    dff = [o for s in hist["series"] if s["id"] == "DFEDTARU" for o in s["observations"]]
    seed = max((o["date"], o["value"]) for o in dff if o["date"] <= "2021-12-31" and o["value"] is not None)[1]
    fed_rows = [{"date_et": "2021-12-31 16:00", "actual": str(seed)}] + fed_rows
    print(f"seed target fin 2021 : {seed} (DFEDTARU vendoré)")
    pce_rows = sorted([r for r in cal if r["event_type"] == "PCE" and r["variant"] == "core_yoy"
                       and r["actual"] != ""], key=lambda r: r["date_et"])
    u_rows = sorted([r for r in cal if r["event_type"] == "UNEMP" and r["actual"] != ""],
                    key=lambda r: r["date_et"])

    def asof(rows, dt, key="actual"):
        best = None
        for r in rows:
            if r["date_et"] <= dt and r[key] not in (None, ""):
                best = r
        return best

    def asof_sep(day):
        best = None
        for d in sep_days:
            if d <= day:
                best = d
        return best

    def asof_price(day):
        best = None
        for r in pricing:
            if r["date"] < day:
                best = r
        return best

    def asof_guid(day):
        best = None
        for gday in sorted(guid):
            if gday <= day:
                best = guid[gday]
        return best

    out = []
    for ev in cal:
        dt, day = ev["date_et"], ev["date_et"][:10]
        if ev["event_type"] == "FED" and ev["variant"] == "target_upper":
            tgt = num(ev["previous"])  # pre-decision
        else:
            # strictement avant : un FOMC 14h00 le meme jour qu'un CPI 8h30 est exclu
            f = asof([r for r in fed_rows if r["date_et"] < dt], dt)
            tgt = num(f["actual"]) if f is not None else None
        p = asof(pce_rows, dt)
        u = asof(u_rows, dt)
        pi = num(p["actual"]) if p else None
        uu = num(u["actual"]) if u else None
        sep = asof_sep(day)
        rs = lr.get(sep, {}).get("ffr") if sep else None
        us = lr.get(sep, {}).get("unrate") if sep else None
        taylor = None
        if None not in (rs, pi, us, uu):
            taylor = rs + pi + 0.5 * (pi - 2.0) + 1.0 * (us - uu)
        mid = tgt - 0.125 if tgt is not None else None
        taylor_gap = (mid - taylor) * 100 if None not in (mid, taylor) else None
        # anticipations d'inflation : mediane SEP PCE annee en cours, sinon core actual
        pexp, pexp_src = None, ""
        if sep and day[:4] in pce_cy.get(sep, {}):
            pexp, pexp_src = pce_cy[sep][day[:4]], "SEP"
        elif pi is not None:
            pexp, pexp_src = pi, "core_actual_repli"
        real_gap = None
        if None not in (mid, pexp, rs):
            real_gap = ((mid - pexp) - (rs - 2.0)) * 100
        cys = dot_cy.get(sep, {}) if sep else {}
        yr = day[:4]
        g = asof_guid(day)
        pr = asof_price(day)
        out.append({
            "date_et": dt, "event_type": ev["event_type"], "variant": ev["variant"],
            "ref_period": ev["ref_period"], "target_upper": "" if tgt is None else f"{tgt:g}",
            "r_star": "" if rs is None else f"{rs:g}",
            "u_star": "" if us is None else f"{us:g}",
            "pce_core": "" if pi is None else f"{pi:g}",
            "unrate": "" if uu is None else f"{uu:g}",
            "pce_gap": "" if pi is None else f"{round(pi - 2.0, 2):g}",
            "u_gap": "" if None in (uu, us) else f"{round(uu - us, 2):g}",
            "taylor": "" if taylor is None else f"{round(taylor, 2):g}",
            "taylor_gap_bps": "" if taylor_gap is None else f"{taylor_gap:+.0f}",
            "pi_exp": "" if pexp is None else f"{pexp:g}",
            "pi_exp_src": pexp_src,
            "real_gap_bps": "" if real_gap is None else f"{real_gap:+.0f}",
            "stance_label": label(real_gap),
            "dot_cy": "" if yr not in cys else f"{cys[yr]:g}",
            "dot_cy_year": yr if yr in cys else "",
            "sep_ref": sep or "",
            "guidance_stance": (g["stance_draft"] + "?" if g and g["statut"] == "draft_a_valider" else "") if g else "",
            "guidance_date": g["date_et"][:10] if g else "",
            "zq": pr["zq"] if pr and pr.get("zq") else "",
            "irx": pr["irx"] if pr and pr.get("irx") else "",
            "fvx": pr["fvx"] if pr and pr.get("fvx") else "",
            "tnx": pr["tnx"] if pr and pr.get("tnx") else "",
            "effr": pr["effr"] if pr and pr.get("effr") else "",
            "pricing_date": pr["date"] if pr else "",
        })

    with open(os.path.join(REGIME, "fed_stance.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print(f"ecrit fed_stance.csv : {len(out)} lignes {Counter(r['stance_label'] for r in out)}")
    print("sans taylor :", sum(1 for r in out if not r["taylor"]),
          "| sans real_gap :", sum(1 for r in out if not r["real_gap_bps"]))
    for probe in ("2022-07-13 08:30", "2023-12-13 14:00", "2025-09-11 08:30"):
        r = next((x for x in out if x["date_et"].startswith(probe[:10])
                  and x["event_type"] == ("FED" if "14:00" in probe else "CPI")), None)
        if r:
            print(f"  {r['date_et']} {r['event_type']}: target={r['target_upper']} r*={r['r_star']} "
                  f"u*={r['u_star']} pi_core={r['pce_core']} u={r['unrate']} "
                  f"taylor={r['taylor']} (gap {r['taylor_gap_bps']}bp) "
                  f"pi_exp={r['pi_exp']}[{r['pi_exp_src']}] real_gap={r['real_gap_bps']}bp "
                  f"{r['stance_label']} guidance={r['guidance_stance']} zq={r['zq']} tnx={r['tnx']}")


if __name__ == "__main__":
    main()
