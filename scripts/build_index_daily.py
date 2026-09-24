"""Serie continue daily ES/NQ 2022-2025 depuis exports NT8 1-min (templates 24h).

Regles :
  - filtre RTH 08:30-15:00 CT (timestamps = fin de barre : premiere 083100, derniere 150000).
  - rth_close = close de la barre 150000 (repli : derniere barre <= 150000).
  - eth_close = close de la derniere barre du jour (reference).
  - rollover : un seul contrat actif par jour, bascule a J-8 calendaires avant echeance
    (nouveau contrat actif des echeance-8j), sans ajustement de prix.
  - echeances : 2022: 18/03, 17/06, 16/09, 16/12 ; 2023: 17/03, 16/06, 15/09, 15/12 ;
    2024: 15/03, 21/06, 20/09, 20/12 ; 2025: 21/03, 20/06, 19/09, 19/12.

Sortie : donnees/regime/index_daily.csv (date, inst, contract, rth_close, eth_close)

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/build_index_daily.py
"""
import csv
import os
from datetime import date, timedelta
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKET = os.path.join(BASE, "donnees", "market")
OUT = os.path.join(BASE, "donnees", "regime", "index_daily.csv")

EXPIRIES = ["2022-03-18", "2022-06-17", "2022-09-16", "2022-12-16",
            "2023-03-17", "2023-06-16", "2023-09-15", "2023-12-15",
            "2024-03-15", "2024-06-21", "2024-09-20", "2024-12-20",
            "2025-03-21", "2025-06-20", "2025-09-19", "2025-12-19"]
LETTER = {"03": "H", "06": "M", "09": "U", "12": "Z"}


def ymd(s):
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def contract_for(inst, day):
    """(fichier, date_switch) : contrat actif pour day (roll a J-8)."""
    for exp in EXPIRIES:
        switch = ymd(exp) - timedelta(days=8)
        if ymd(day) < switch:
            return f"{inst} {exp[5:7]}-{exp[2:4]}.Last.txt"
    return f"{inst} 12-25.Last.txt"


def parse_file(path):
    """Rend {jjjjmmaa: (rth_close, eth_close)}. Ignore samedi/dimanche :
    les exports contiennent parfois des barres parasites le week-end
    (ex : 120 barres le dimanche 2023-09-17, RTH inexistant en realite)."""
    days = {}
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ts, o, h, l, c, v = line.split(";")
                d, t = ts.split(" ")
                if date(int(d[:4]), int(d[4:6]), int(d[6:8])).weekday() >= 5:
                    continue
                close = float(c)
            except ValueError:
                continue
            rec = days.setdefault(d, [None, None])
            if "083000" < t <= "150000":
                rec[0] = close  # ecrase : garde la derniere <= 15h00
            rec[1] = close      # derniere barre du jour (fichier trie)
    return days


def main():
    cache = {}
    rows = []
    for inst in ("ES", "NQ"):
        # toutes les dates presentes dans les fichiers concernes
        wanted = {}
        for exp in EXPIRIES:
            switch = ymd(exp) - timedelta(days=8)
            prev = None
            for e2 in EXPIRIES:
                if ymd(e2) < ymd(exp):
                    prev = e2
            start = (ymd(prev) - timedelta(days=8)) if prev else date(2021, 1, 1)
            fname = f"{inst} {exp[5:7]}-{exp[2:4]}.Last.txt"
            wanted[fname] = (start, switch)
        for fname, (start, end) in wanted.items():
            p = os.path.join(MARKET, fname)
            if not os.path.exists(p):
                print(f"MANQUANT: {fname}")
                continue
            if fname not in cache:
                cache[fname] = parse_file(p)
                print(f"charge {fname}: {len(cache[fname])} jours")
            for d, (rth, eth) in cache[fname].items():
                day = f"{d[:4]}-{d[4:6]}-{d[6:]}"
                if not (start <= ymd(day) < end):
                    continue
                if contract_for(inst, day) != fname:
                    continue
                if rth is None:
                    print(f"ATTENTION {inst} {day}: pas de barre RTH dans {fname}")
                    continue
                rows.append({"date": day, "inst": inst,
                             "contract": fname.replace(".Last.txt", ""),
                             "rth_close": f"{rth:g}", "eth_close": f"{eth:g}" if eth else ""})
    rows.sort(key=lambda r: (r["date"], r["inst"]))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "inst", "contract", "rth_close", "eth_close"])
        w.writeheader()
        w.writerows(rows)
    for inst in ("ES", "NQ"):
        sub = [r["date"] for r in rows if r["inst"] == inst]
        print(f"{inst}: {len(sub)} jours, {sub[0]} -> {sub[-1]}")
        # trous > 4 jours calendaires (week-ends longs / feries OK jusqu'a 4)
        gaps = [(a, b, (ymd(b) - ymd(a)).days)
                for a, b in zip(sub, sub[1:]) if (ymd(b) - ymd(a)).days > 4]
        print(f"  trous >4j: {gaps[:10]}")
    print(f"ecrit {OUT} : {len(rows)} lignes")


if __name__ == "__main__":
    main()
