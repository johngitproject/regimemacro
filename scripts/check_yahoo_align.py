"""Controle d'alignement NT8 <-> Yahoo avant tout patch.

Compare, sur tous les jours communs 2022-2025 :
  - yahoo close vs rth_close (15h00 CT) et vs eth_close (derniere barre)
  - distribution des ecarts (mediane, p95, max), par annee
  - jours aberrants (|ecart| > 1 %) : decalage de date ? roll divergent ?
  - ecarts autour des rollovers (contrat Yahoo vs regle J-8)

But : valider que le close Yahoo peut boucher les trous (bruit d'entree ~ ?).
Ne modifie rien, diagnostic seul.

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/check_yahoo_align.py
"""
import csv
import os
from statistics import median

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
SRC = os.path.join(REGIME, "sources")


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def pct(a, b):
    return (a / b - 1) * 100 if b else None


def main():
    idx = {(r["inst"], r["date"]): (float(r["rth_close"]), float(r["eth_close"] or 0) or None)
           for r in load_csv(os.path.join(REGIME, "index_daily.csv"))}
    y = {(r["inst"], r["date"]): float(r["close"])
         for r in load_csv(os.path.join(SRC, "yahoo_index_daily.csv"))}
    common = sorted(set(idx) & set(y))
    print(f"jours communs : {len(common)}")
    for inst in ("ES", "NQ"):
        dr, de = [], []
        for k in common:
            if k[0] != inst:
                continue
            rth, eth = idx[k]
            dr.append(abs(pct(y[k], rth)))
            if eth:
                de.append(abs(pct(y[k], eth)))
        dr.sort(), de.sort()
        q = lambda v, p: v[min(len(v) - 1, int(len(v) * p))]
        print(f"{inst} vs RTH: n={len(dr)} med={median(dr):.3f}% p95={q(dr, .95):.3f}% max={dr[-1]:.2f}%")
        print(f"{inst} vs ETH: n={len(de)} med={median(de):.3f}% p95={q(de, .95):.3f}% max={de[-1]:.2f}%")
    print("jours |ecart vs RTH| > 1 % :")
    n = 0
    for k in common:
        rth = idx[k][0]
        d = abs(pct(y[k], rth))
        if d > 1.0:
            print(f"  {k[0]} {k[1]} : NT8_RTH={rth:g} Y={y[k]:g} ({d:+.2f}%)")
            n += 1
            if n > 25:
                print("  ... (tronque)")
                break
    if n == 0:
        print("  aucun")
    # rollovers : ecart moyen la semaine avant/apres chaque switch J-8
    print("ecart median par annee (vs RTH) :")
    for inst in ("ES", "NQ"):
        by_y = {}
        for k in common:
            if k[0] == inst:
                by_y.setdefault(k[1][:4], []).append(abs(pct(y[k], idx[k][0])))
        print(f"  {inst}: " + ", ".join(f"{y0}={median(v):.3f}%" for y0, v in sorted(by_y.items())))


if __name__ == "__main__":
    main()
