"""Étape 2 — Breakevens d'inflation FRED (T5YIE, T10YIE) via API fredapi.

Clé lue UNIQUEMENT depuis la variable d'environnement FRED_API_KEY
(jamais en clair dans le code). Gratuite sur https://fred.stlouisfed.org
(My Account > API Keys).

Sortie : donnees/regime/fred_T5YIE_T10YIE.csv (date, T5YIE, T10YIE, % annualisé)

Note d'unité (assumée, cf. brief) : le breakeven est une anticipation
annualisée 5Y/10Y, PAS une attente de CPI mensuel. Conservé tel quel comme
proxy de `market_implied`, avec colonnes de sensibilité sur le consensus
dans le script d'assemblage final.
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "donnees", "regime", "fred_T5YIE_T10YIE.csv")


def main():
    key = os.environ.get("FRED_API_KEY")
    if not key:
        sys.exit("ERREUR: variable d'environnement FRED_API_KEY absente.")
    try:
        from fredapi import Fred
    except ImportError:
        sys.exit("ERREUR: fredapi manquant (pip install fredapi)")
    fred = Fred(api_key=key)
    series = {}
    for sid in ("T5YIE", "T10YIE"):
        s = fred.get_series(sid, observation_start="2023-01-01")
        s = s.dropna()
        series[sid] = s
        print(f"{sid}: {len(s)} obs journalières, {s.index.min().date()} -> {s.index.max().date()}, "
              f"dernière={s.iloc[-1]:.2f}%")
    import pandas as pd
    df = pd.DataFrame(series)
    df.index.name = "date"
    df.to_csv(OUT)
    print(f"écrit {OUT}")


if __name__ == "__main__":
    main()
