# Etape 1 — Series FRED regime H10/H9/H14, SANS cle API (endpoint public fredgraph.csv).
# Lancer avec le venv du projet (pandas + urllib) :
#   .\venv\Scripts\python.exe scripts/fetch_fred_regime.py
# Sortie : donnees/regime/fred_H10_H9_H14.csv (date + 6 colonnes brutes).
# Series : DGS10, DGS2 (spread H10), VIXCLS (sizing H9), SP500 (SMA200 H10),
#          BAA, AAA (spread credit H14). Historique depuis 2024-01-01
#          (SMA200 exige 200 seances avant le 02/01/2025). Valeurs "." -> vide.
import os
import time
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "donnees", "regime", "fred_H10_H9_H14.csv")
SERIES = ("DGS10", "DGS2", "VIXCLS", "SP500", "BAA", "AAA")
START = "2024-01-01"


def fetch_chunk(sid, cosd, coed, tries=6):
    url = (f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
           f"&cosd={cosd}&coed={coed}")
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                lines = r.read().decode("utf-8").splitlines()
            data = {}
            for ln in lines[1:]:
                p = ln.split(",")
                if len(p) != 2:
                    continue
                data[p[0]] = "" if p[1].strip() == "." else p[1].strip()
            return data
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (a + 1))
    raise RuntimeError(f"echec {sid} {cosd}-{coed}: {last}")


def fetch(sid):
    # morceaux annuels (FRED coupe les gros appels), pause entre series.
    data = {}
    for cosd, coed in (("2024-01-01", "2024-12-31"), ("2025-01-01", "2026-01-31")):
        data.update(fetch_chunk(sid, cosd, coed))
        time.sleep(3)
    print(f"{sid}: {len(data)} obs")
    return data


def main():
    alld = {sid: fetch(sid) for sid in SERIES}
    dates = sorted(set().union(*[set(d) for d in alld.values()]))
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("date," + ",".join(SERIES) + "\n")
        for dt in dates:
            f.write(dt + "," + ",".join(alld[s].get(dt, "") for s in SERIES) + "\n")
    print(f"ecrit {OUT} ({len(dates)} lignes)")


if __name__ == "__main__":
    main()
