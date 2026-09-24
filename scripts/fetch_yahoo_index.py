"""Closes daily continus ES/NQ depuis Yahoo Finance (v8, sans cle).

But : combler les semaines de rollover manquantes des exports NT8 + la queue
dec-2025 -> 2026 (forwards 20/60j). Symboles continus front-month : ES=F, NQ=F.

Point critique : attribution des dates en heure CHICAGO (futures quasi-24h ;
un timestamp UTC minuit +/- quelques heures peut basculer de jour calendaire).
Regle DST US : 2e dimanche de mars -> 1er dimanche de novembre.

Sortie : donnees/regime/sources/yahoo_index_daily.csv (date, inst, close)

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/fetch_yahoo_index.py
"""
import csv
import json
import os
import time
import urllib.request
from datetime import datetime, timedelta, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "donnees", "regime", "sources", "yahoo_index_daily.csv")

START = datetime(2021, 12, 1)
END = datetime(2026, 7, 5)
SYMBOLS = {"ES": "ES%3DF", "NQ": "NQ%3DF"}


def _nth_weekday(year, month, weekday, n):
    from datetime import date
    if n > 0:
        d = date(year, month, 1)
        return d + timedelta(days=(weekday - d.weekday()) % 7 + (n - 1) * 7)
    d = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)
    d -= timedelta(days=1)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def ts_to_chicago(ts):
    """Epoch UTC -> date de seance. Les barres daily Yahoo sont horodatees a
    minuit heure de New York (05:00Z l'hiver, 04:00Z l'ete) ; cette date ET est
    la date de seance (le RTH 15h00 CT du meme jour calendaire en fait partie).
    Regle DST US : 2e dimanche de mars -> 1er dimanche de novembre."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)
    dst_start = datetime.combine(_nth_weekday(dt.year, 3, 6, 2), datetime.min.time())
    dst_end = datetime.combine(_nth_weekday(dt.year, 11, 6, 1), datetime.min.time())
    off = 4 if dst_start <= dt < dst_end else 5
    return (dt - timedelta(hours=off)).strftime("%Y-%m-%d")


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


def fetch(sym):
    p1 = int(START.timestamp())
    p2 = int((END + timedelta(days=1)).timestamp())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
           f"?period1={p1}&period2={p2}&interval=1d&events=div%7Csplit")
    d = json.loads(get(url))
    r = d["chart"]["result"][0]
    out = {}
    for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
        if c is None:
            continue
        day = ts_to_chicago(t)
        out[day] = round(float(c), 2)  # 1 barre/jour ; doublon eventuel ecrase
    print(f"{sym}: {r['meta'].get('longName', sym)}, {len(out)} closes")
    return out


def main():
    rows = []
    for inst, sym in SYMBOLS.items():
        try:
            data = fetch(sym)
        except RuntimeError as e:
            print(f"ATTENTION {inst}: {e}")
            continue
        rows.extend({"date": d, "inst": inst, "close": c} for d, c in sorted(data.items()))
        time.sleep(2)
    rows.sort(key=lambda r: (r["date"], r["inst"]))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "inst", "close"])
        w.writeheader()
        w.writerows(rows)
    es = [r["date"] for r in rows if r["inst"] == "ES"]
    print(f"ecrit {OUT} : {len(rows)} lignes, ES {es[0]} -> {es[-1]}")


if __name__ == "__main__":
    main()
