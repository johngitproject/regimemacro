"""Étape 4 — Assemblage final : calendrier + FRED (veille) + réactions NQ.

Règle market_implied : dernière obs FRED strictement avant le jour de
publication (pas de lookahead ; la valeur FRED du jour J n'est de toute
façon pas connue à 8h30 ET).

Sortie : donnees/regime/regime_dataset_2025.csv
Colonnes brief : date, event_type, consensus, actual, market_implied,
surprise, reaction_nq, reaction_rate (+ extras documentés).
"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")

cal = pd.read_csv(os.path.join(REGIME, "calendar_cpi_2025.csv"), parse_dates=["date_et"])
fred = pd.read_csv(os.path.join(REGIME, "fred_T5YIE_T10YIE.csv"), parse_dates=["date"])
reac = pd.read_csv(os.path.join(REGIME, "nq_reactions_2025.csv"))

cal["day"] = cal["date_et"].dt.normalize()
rows = []
for _, ev in cal.iterrows():
    past = fred[fred["date"] < ev["day"]]
    if past.empty:
        raise SystemExit(f"Pas de donnée FRED avant {ev['day']}")
    f = past.iloc[-1]
    r = reac[reac["date"] == ev["date_et"].strftime("%Y-%m-%d %H:%M")]
    if r.empty:
        raise SystemExit(f"Pas de réaction NQ pour {ev['date_et']}")
    r = r.iloc[0]
    rows.append({
        "date": ev["date_et"].strftime("%Y-%m-%d %H:%M"),
        "event_type": ev["event_type"],
        "consensus": ev["consensus_mom"],
        "actual": ev["actual_mom"],
        "market_implied": round(float(f["T5YIE"]), 3),          # proxy principal : T5YIE veille
        "market_implied_T10YIE": round(float(f["T10YIE"]), 3),
        "fred_ref_date": f["date"].strftime("%Y-%m-%d"),
        "surprise": round(float(ev["actual_mom"]) - float(f["T5YIE"]), 3),
        "surprise_T10YIE": round(float(ev["actual_mom"]) - float(f["T10YIE"]), 3),
        "surprise_consensus": round(float(ev["actual_mom"]) - float(ev["consensus_mom"]), 3),
        "reaction_nq": float(r["reaction_nq_pts"]),
        "reaction_nq_pct": float(r["reaction_nq_pct"]),
        "reaction_rate": float("nan"),   # pas de ZT/2Y sur le sample 1
        "flag_ambigu": "NA_no_ZT",
    })

out = pd.DataFrame(rows)
p = os.path.join(REGIME, "regime_dataset_2025.csv")
out.to_csv(p, index=False)
print(f"écrit {p} : {len(out)} lignes")
print(out[["date", "consensus", "actual", "market_implied", "surprise",
           "reaction_nq", "reaction_rate"]].to_string(index=False))
