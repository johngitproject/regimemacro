"""Étape 3-4 (partiel) — Réactions NQ 1-min aux CPI 2025 depuis exports NinjaTrader 8.

Entrées :
  donnees/regime/calendar_cpi_2025.csv   (date_et, event_type, ref_month, consensus_mom, actual_mom, ...)
  donnees/market/NQ *.Last.txt           (format NT8 Minute/Last, heure Chicago, `aaaammjj HHmmss;O;H;L;C;V`)

Rollover (cf. donnees/market/LISEZMOI.md) : un seul contrat actif par jour,
bascule à l'open RTH de J-8 calendaires avant échéance.
Échéances 2025 : H5 ven 21/03, M5 ven 20/06, U5 ven 19/09, Z5 ven 19/12.
  -> H5 actif jusqu'au 2025-03-12 inclus, M5 jusqu'au 2025-06-11,
     U5 jusqu'au 2025-09-11, Z5 ensuite.
Cas limite documenté : CPI du 2025-09-11 = jour de roll U5->Z5, mais 7h30 CT
(avant l'open RTH 8h30 CT) reste sur U5.

Fenêtre de réaction : CPI 8h30 ET = 7h30 CT (mur Chicago, CST comme CDT).
  pre  = close de la barre 1-min 07:30 CT (barre 07:29-07:30)
  post = close de la barre 1-min 08:00 CT (T+30min)
  reaction_pts = post - pre ; reaction_pct = reaction_pts / pre * 100

Sortie : donnees/regime/nq_reactions_2025.csv
"""
import csv
import os
import sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKET = os.path.join(BASE, "donnees", "market")
REGIME = os.path.join(BASE, "donnees", "regime")
CAL = os.path.join(REGIME, "calendar_cpi_2025.csv")
OUT = os.path.join(REGIME, "nq_reactions_2025.csv")

# (fichier NT8, date active début, date active fin) — contrat front
CONTRACTS = [
    ("NQ 03-25.Last.txt", date(2025, 1, 1), date(2025, 3, 12)),
    ("NQ 06-25.Last.txt", date(2025, 3, 13), date(2025, 6, 11)),
    ("NQ 09-25.Last.txt", date(2025, 6, 12), date(2025, 9, 11)),
    ("NQ 12-25.Last.txt", date(2025, 9, 12), date(2025, 12, 31)),
]
FALLBACK = "NQ 03-25-LAST2.txt"  # même H5, autre template de session


def load_nt8(path):
    """Retourne dict {(date_str, hhmmss): close}."""
    bars = {}
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ts, o, h, l, c, v = line.split(";")
                d, t = ts.split(" ")
                bars[(d, t)] = float(c)
            except ValueError:
                continue
    return bars


def main():
    # 1. calendrier
    with open(CAL, newline="", encoding="utf-8") as fh:
        events = list(csv.DictReader(fh))

    # 2. barres par contrat
    data = {}
    for fname, d0, d1 in CONTRACTS:
        p = os.path.join(MARKET, fname)
        if not os.path.exists(p):
            print(f"MANQUANT: {fname}", file=sys.stderr)
            continue
        data[(d0, d1)] = load_nt8(p)
        print(f"chargé {fname}: {len(data[(d0, d1)])} barres")
    fb = {}
    pfb = os.path.join(MARKET, FALLBACK)
    if os.path.exists(pfb):
        fb = load_nt8(pfb)
        print(f"chargé {FALLBACK} (fallback): {len(fb)} barres")

    # 3. réactions
    rows = []
    missing = []
    for ev in events:
        day = ev["date_et"][:10]  # YYYY-MM-DD
        dkey = day.replace("-", "")
        y, m, d = int(day[:4]), int(day[5:7]), int(day[8:10])
        evdate = date(y, m, d)
        bars = None
        for (d0, d1), b in data.items():
            if d0 <= evdate <= d1:
                bars = b
                break
        pre = post = None
        src = ""
        if bars is not None:
            pre = bars.get((dkey, "073000"))
            post = bars.get((dkey, "080000"))
            src = "front"
        if (pre is None or post is None) and fb:
            pre = fb.get((dkey, "073000"), pre)
            post = post if post is not None else fb.get((dkey, "080000"))
            if pre is not None and post is not None:
                src = "fallback-LAST2"
        if pre is None or post is None:
            missing.append(day)
            print(f"ATTENTION {day}: barre 07:30 ou 08:00 CT introuvable")
            continue
        rpts = post - pre
        rpct = rpts / pre * 100.0
        rows.append({
            "date": ev["date_et"],
            "event_type": ev["event_type"],
            "contract": src,
            "pre_close": f"{pre:.2f}",
            "post_close": f"{post:.2f}",
            "reaction_nq_pts": f"{rpts:.2f}",
            "reaction_nq_pct": f"{rpct:.4f}",
        })
        print(f"{day}: pre={pre:.2f} post={post:.2f} react={rpts:+.2f}pts ({rpct:+.4f}%) [{src}]")

    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "event_type", "contract",
                                           "pre_close", "post_close",
                                           "reaction_nq_pts", "reaction_nq_pct"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nécrit {OUT} : {len(rows)} lignes, {len(missing)} manquantes {missing}")
    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
