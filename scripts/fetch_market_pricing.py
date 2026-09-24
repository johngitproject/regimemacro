"""Pricing marche quotidien 2021-12 -> 2026-02 : futures Fed funds + taux + EFFR.

Sources gratuites sans cle :
  - Yahoo Finance chart v8 : ZQ=F (fed funds futures, continu front), ^IRX (T-bill 3M),
    ^FVX (5 ans), ^TNX (10 ans). Closes ajustes dividendes/splits sans objet (taux/futures).
  - NY Fed Markets API : EFFR (taux effectif), search.json sans cle.

Limites documentees : ZQ=F continu roule chaque mois (petit bruit de roll) ; Yahoo peut
reviser/ajuster l'historique ; trous week-ends/feries combles en forward-fill cote build.

Sortie : donnees/regime/sources/market_pricing_daily.csv
  (date, zq, irx, fvx, tnx, effr)

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/fetch_market_pricing.py
"""
import csv
import json
import os
import time
import urllib.request
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "donnees", "regime", "sources", "market_pricing_daily.csv")

START = datetime(2021, 12, 1)
END = datetime(2026, 2, 5)
SYMBOLS = {"zq": "ZQ%3DF", "irx": "%5EIRX", "fvx": "%5EFVX", "tnx": "%5ETNX"}


def get(url, tries=6, timeout=90):
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  essai {a + 1} echec: {type(e).__name__}")
            time.sleep(5 * (a + 1))
    raise RuntimeError(f"echec {url}: {last}")


def yahoo(sym):
    p1 = int(START.timestamp())
    p2 = int((END + timedelta(days=1)).timestamp())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
           f"?period1={p1}&period2={p2}&interval=1d&events=div%7Csplit")
    d = json.loads(get(url))
    r = d["chart"]["result"][0]
    ts, q = r["timestamp"], r["indicators"]["quote"][0]
    out = {}
    for t, c in zip(ts, q["close"]):
        if c is None:
            continue
        out[datetime.fromtimestamp(t, tz=None).strftime("%Y-%m-%d")] = round(float(c), 3)
    name = r["meta"].get("longName", sym)
    print(f"{sym}: {name}, {len(out)} closes")
    return out


def effr():
    # l'API NY Fed limite la fenetre : boucle annuelle puis fusion
    out = {}
    for y in range(2021, 2027):
        url = ("https://markets.newyorkfed.org/api/rates/unsecured/effr/search.json"
               f"?startDate=01/01/{y}&endDate=12/31/{y}")
        d = json.loads(get(url, timeout=120))
        for r in d.get("refRates", []):
            out[r["effectiveDate"]] = round(float(r["percentRate"]), 3)
        time.sleep(1)
    print(f"EFFR: {len(out)} obs")
    return out


def main():
    data = {}
    for key, sym in SYMBOLS.items():
        try:
            for day, val in yahoo(sym).items():
                data.setdefault(day, {})[key] = val
        except RuntimeError as e:
            print(f"ATTENTION {key}: {e}")
        time.sleep(2)
    try:
        for day, val in effr().items():
            data.setdefault(day, {})["effr"] = val
    except RuntimeError as e:
        print(f"ATTENTION effr: {e}")
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "zq", "irx", "fvx", "tnx", "effr"])
        w.writeheader()
        for day in sorted(data):
            row = {"date": day}
            row.update(data[day])
            w.writerow(row)
    cov = {k: sum(1 for d in data.values() if k in d) for k in ("zq", "irx", "fvx", "tnx", "effr")}
    print(f"ecrit {OUT} : {len(data)} jours, couverture {cov}")


if __name__ == "__main__":
    main()
