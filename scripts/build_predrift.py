"""Derive pre-news 20 seances + sens vs surprise + amplitude jour J.

Pour chaque release avec surprise (calendar_macro, released) :
  - drift_es / drift_nq : close RTH veille vs close RTH 20 seances avant (%)
  - drift_tnx_bp : tnx veille vs tnx 20 seances avant (bp)
  - sens surprise -> hawkish/dovish/inline (seuils : CPI/PCE 0.1, UNEMP 0.1, NFP 30K, FED 0.1 ;
    UNEMP inverse : surprise + = dovish)
  - derive pre-news (via tnx, bande plate +/-15 bp) : dovish / hawkish / flat
  - alignement : CONTRE (drift dovish + surprise hawkish ou inverse),
    AVEC (meme sens), n.d. (flat/inline/donnee manquante)
  - move jour J : ES/NQ close J vs veille (%, RTH capte la news 8h30 et FOMC 14h00),
    tnx J vs veille (bp)

Sorties :
  donnees/regime/pre_drift_20j.csv (une ligne par release avec surprise)
  donnees/regime/pre_drift_report.md (avec/contre x amplitude jour J)

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/build_predrift.py
"""
import csv
import os
from statistics import mean, median

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
SRC = os.path.join(REGIME, "sources")

SEUIL = {"CPI": 0.1, "PCE": 0.1, "NFP": 30.0, "UNEMP": 0.1, "FED": 0.1}
DRIFT_FLAT_BP = 15.0


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(x):
    try:
        return float(x) if x not in (None, "") else None
    except ValueError:
        return None


def main():
    cal = [r for r in load_csv(os.path.join(REGIME, "calendar_macro_2022_2026.csv"))
           if r["status"] == "released" and r["surprise"] not in (None, "")]
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

    def before(lst, day):
        c = [d for d in lst if d < day]
        return c[-1] if c else None

    rows = []
    for r in sorted(cal, key=lambda x: (x["date_et"], x["variant"])):
        J = r["date_et"][:10]
        s = num(r["surprise"])
        sev = SEUIL[r["event_type"]]
        if r["event_type"] == "UNEMP":
            sens = "hawkish" if s <= -sev else ("dovish" if s >= sev else "inline")
        else:
            sens = "hawkish" if s >= sev else ("dovish" if s <= -sev else "inline")
        out = {"date_et": r["date_et"], "event_type": r["event_type"], "variant": r["variant"],
               "ref_period": r["ref_period"], "surprise": r["surprise"], "unit": r["unit"],
               "sens": sens}
        # drifts 20 seances avant la veille
        for inst, col in (("ES", "drift_es_pct"), ("NQ", "drift_nq_pct")):
            v = before(days[inst], J)
            if v is not None and pos[inst][v] >= 20:
                d0 = days[inst][pos[inst][v] - 20]
                out[col] = f"{(closes[inst][v] / closes[inst][d0] - 1) * 100:+.2f}"
                out[col + "_base"] = f"{d0}>{v}"
            else:
                out[col], out[col + "_base"] = "", ""
        tv = before(tdays, J)
        if tv is not None and tpos[tv] >= 20:
            t0 = tdays[tpos[tv] - 20]
            out["drift_tnx_bp"] = f"{(tnx[tv] - tnx[t0]) * 100:+.0f}"
            out["drift_tnx_base"] = f"{t0}>{tv}"
        else:
            out["drift_tnx_bp"], out["drift_tnx_base"] = "", ""
        dd = num(out["drift_tnx_bp"])
        drift = "" if dd is None else ("dovish" if dd <= -DRIFT_FLAT_BP else
                                       ("hawkish" if dd >= DRIFT_FLAT_BP else "flat"))
        out["drift"] = drift
        if sens == "inline" or not drift or drift == "flat":
            out["alignement"] = "n.d."
        elif (drift == "dovish") != (sens == "dovish"):
            out["alignement"] = "CONTRE"
        else:
            out["alignement"] = "AVEC"
        # move jour J (close J vs veille) ; J doit exister tel quel, jamais interpole
        # (ex : FOMC 18 sep 2024 sans close NT8 -> vide, pas le 24 sep)
        for inst, col in (("ES", "jday_es_pct"), ("NQ", "jday_nq_pct")):
            v = before(days[inst], J)
            if v is not None and J in pos[inst]:
                out[col] = f"{(closes[inst][J] / closes[inst][v] - 1) * 100:+.2f}"
            else:
                out[col] = ""
        if tv is not None and J in tnx:
            out["jday_tnx_bp"] = f"{(tnx[J] - tnx[tv]) * 100:+.0f}"
        else:
            out["jday_tnx_bp"] = ""
        rows.append(out)

    with open(os.path.join(REGIME, "pre_drift_20j.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"ecrit pre_drift_20j.csv : {len(rows)} lignes")

    # --- controles : les 4 cas d'etude ---
    print("controles cas d'etude (drift_es / drift_tnx / sens / alignement) :")
    for d, v, var in (("2022-07-13", "CPI", "headline"), ("2022-11-10", "CPI", "headline"),
                      ("2024-09-18", "FED", "target"), ("2025-02-12", "CPI", "headline")):
        for r in rows:
            if r["date_et"].startswith(d) and r["event_type"] == v and var in r["variant"]:
                print(f"  {d} {v}: es={r['drift_es_pct']}% tnx={r['drift_tnx_bp']}bp "
                      f"sens={r['sens']} -> {r['alignement']} | J: es={r['jday_es_pct']}% "
                      f"tnx={r['jday_tnx_bp']}bp")

    # --- rapport avec / contre ---
    def agg(sel, col):
        vals = [num(r[col]) for r in rows
                if r["alignement"] == sel and num(r[col]) is not None]
        if len(vals) < 5:
            return f"N={len(vals)} (insuffisant)"
        aversion = 0.5 if "pct" in col else 5.0  # seuil "gros move" jour J
        big = [abs(v) for v in vals]
        return (f"N={len(vals)} |J| moy={mean(big):+.2f} med={median(big):+.2f} "
                f"part gros moves(>{aversion:g})={sum(1 for v in big if v > aversion) / len(vals):.0%}")

    lines = ["# Derive pre-news 20j : surprise avec / contre la derive",
             "",
             "Base : releases avec surprise 2022-2026. Drift = tnx veille vs tnx-20j (bande plate +/-15 bp).",
             "Sens hawkish/dovish via seuils CPI/PCE 0.1, UNEMP 0.1 (inverse), NFP 30K, FED 0.1.",
             "Move jour J = close J vs veille (RTH capte news 8h30 et FOMC 14h00).",
             "",
             "## Amplitude jour J par alignement",
             ""]
    for col, lbl in (("jday_es_pct", "ES jour J (%)"), ("jday_nq_pct", "NQ jour J (%)"),
                     ("jday_tnx_bp", "10Y jour J (bp, amplitude)")):
        lines.append(f"### {lbl}")
        for sel in ("CONTRE", "AVEC", "n.d."):
            lines.append(f"- {sel} : {agg(sel, col)}")
        lines.append("")
    lines += ["## Nombre de cas par couple (drift x sens)",
              ""]
    seen = {}
    for r in rows:
        seen[(r["drift"] or "?", r["sens"])] = seen.get((r["drift"] or "?", r["sens"]), 0) + 1
    for k in sorted(seen):
        lines.append(f"- drift {k[0]} x surprise {k[1]} : {seen[k]}")
    lines.append("")
    rep = os.path.join(REGIME, "pre_drift_report.md")
    with open(rep, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"ecrit {rep}")


if __name__ == "__main__":
    main()
