"""Telecharge les tables SEP (medanes) depuis federalreserve.gov.

19 meetings SEP 2022-2026 : https://www.federalreserve.gov/monetarypolicy/fomcprojtableYYYYMMDD.htm
Sortie : donnees/regime/sources/sep_tables/fomcprojtableYYYYMMDD.htm

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/fetch_sep_tables.py
"""
import os
import time
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "donnees", "regime", "sources", "sep_tables")

# meetings avec SEP ( quarto : mars / juin / sept / dec )
SEP_DATES = [
    "20211215",
    "20220316", "20220615", "20220921", "20221214",
    "20230322", "20230614", "20230920", "20231213",
    "20240320", "20240612", "20240918", "20241218",
    "20250319", "20250618", "20250917", "20251210",
    "20260318", "20260617", "20260916",
]
# le prefixe varie selon les vintages (table vs tabl)
VARIANTS = ["fomcprojtable{d}.htm", "fomcprojtabl{d}.htm"]


def fetch(url, tries=5):
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise  # pas de retry sur 404 : essayer la variante suivante
            last = e
            print(f"  essai {a + 1} echec: HTTP {e.code}")
            time.sleep(4 * (a + 1))
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  essai {a + 1} echec: {type(e).__name__}")
            time.sleep(4 * (a + 1))
    raise RuntimeError(f"echec {url}: {last}")


def main():
    os.makedirs(OUT, exist_ok=True)
    for d in SEP_DATES:
        dest = os.path.join(OUT, f"fomcprojtable{d}.htm")
        if os.path.exists(dest) and os.path.getsize(dest) > 50000:
            print(f"{d}: deja la ({os.path.getsize(dest)} o)")
            continue
        data, used = None, None
        for var in VARIANTS:
            url = f"https://www.federalreserve.gov/monetarypolicy/{var.format(d=d)}"
            print(f"{d}: {url}")
            try:
                data = fetch(url)
                used = var.format(d=d)
                break
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    raise
                print("  404 -> variante suivante")
        if data is None:
            print(f"  MANQUANT: {d} (inspecter a la main)")
            continue
        with open(dest, "wb") as fh:
            fh.write(data)
        print(f"  -> {len(data)} o ({used})")
        time.sleep(2)
    print("OK")


if __name__ == "__main__":
    main()
