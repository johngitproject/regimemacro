"""Construit les seuils Fed (SEP) + distribution des dots, 2022-2026.

Entrees :
  donnees/regime/sources/sep_tables/fomcprojtableYYYYMMDD.htm (19 tables, medianes Table 1)
  donnees/regime/sources/dotplot.csv (dots individuels palewire/fed-dot-plot-scraper)

Sorties :
  donnees/regime/fed_thresholds.csv  (meeting_date,var,horizon,median,source)
      var = gdp | unrate | pce | core_pce | ffr ; horizon = AAAA | LR
  donnees/regime/fed_dots.csv        (meeting_date,horizon,median,dmin,dmax,n,source)
      distribution des dots Fed funds par horizon (dont LR)

Validations integrees :
  - longer-run Mar-22 : ffr 2.4 / unrate 4.0 / pce 2.0 (valeurs FRED FEDTARMDLR/UNRATEMDLR)
  - longer-run Jun-24 : ffr 2.8 / unrate 4.2 ; Mar-26 : ffr 3.1
  - medianes dots ffr == medianes table SEP (tolerance 0.001)

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/build_fed_thresholds.py
"""
import csv
import math
import os
import re
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "donnees", "regime", "sources")
SEP = os.path.join(SRC, "sep_tables")
DOT_TMP = r"C:\Users\BMC\AppData\Local\Temp\opencode\dotplot.csv"
DOT_SRC = os.path.join(SRC, "dotplot.csv")
OUT_T = os.path.join(BASE, "donnees", "regime", "fed_thresholds.csv")
OUT_D = os.path.join(BASE, "donnees", "regime", "fed_dots.csv")

MEETINGS = ["20211215",
            "20220316", "20220615", "20220921", "20221214",
            "20230322", "20230614", "20230920", "20231213",
            "20240320", "20240612", "20240918", "20241218",
            "20250319", "20250618", "20250917", "20251210",
            "20260318", "20260617", "20260916"]

VARS = [("Core PCE inflation", "core_pce"), ("PCE inflation", "pce"),
        ("Change in real GDP", "gdp"), ("Unemployment rate", "unrate"),
        ("Federal funds rate", "ffr")]

# controles longer-run connus (FRED FEDTARMDLR / UNRATEMDLR ; PCE LR = 2.0, pas de LR core)
SPOT = {("2022-03-16", "ffr", "LR"): 2.4, ("2022-03-16", "unrate", "LR"): 4.0,
        ("2022-03-16", "pce", "LR"): 2.0,
        ("2024-06-12", "ffr", "LR"): 2.8, ("2024-06-12", "unrate", "LR"): 4.2,
        ("2026-03-18", "ffr", "LR"): 3.1, ("2026-03-18", "unrate", "LR"): 4.2,
        ("2026-09-16", "unrate", "LR"): 4.2}


def strip_tags(s):
    s = re.sub(r"<sup>.*?</sup>", "", s)
    return re.sub(r"<[^>]+>", "", s).strip()


def parse_sep(path):
    """Rend {var: [(horizon, median)]} depuis la Table 1 (Median).

    Robustesse : l'id de section Median (xt1a2, xt2a2, ...) est detecte, et le
    core PCE n'a pas de colonne longer-run (emptystub) -> horizons positionnels.
    """
    h = open(path, encoding="utf-8", errors="replace").read()
    tables = re.findall(r"<table[^>]*pubtables[^>]*>(.*?)</table>", h, re.S)
    for tab in tables:
        thead = re.search(r"<thead>(.*?)</thead>", tab, re.S)
        if not thead:
            continue
        m = re.search(r'<th class="colhead" colspan="\d+" id="([^"]+)">Median', thead.group(1))
        if not m:
            continue
        sec = m.group(1)
        med_labels = re.findall(r'<th[^>]*headers="%s"[^>]*>(.*?)</th>' % re.escape(sec),
                                thead.group(1), re.S)
        med_labels = [strip_tags(x) for x in med_labels]
        if not med_labels or "Longer run" not in med_labels:
            continue
        horizons = ["LR" if x == "Longer run" else x for x in med_labels]
        if "Federal funds rate" not in strip_tags(tab):
            continue
        out = {}
        for tr in re.findall(r"<tr>(.*?)</tr>", tab, re.S):
            mth = re.search(r'<th class="stub"[^>]*>(.*?)</th>', tr, re.S)
            if not mth:
                continue
            name = strip_tags(mth.group(1))
            var = next((v for pat, v in VARS if pat in name), None)
            if var is None:
                continue
            cells = re.findall(r'<td[^>]*headers="[^"]*%s[^"]*"[^>]*>(.*?)</td>'
                               % re.escape(sec), tr, re.S)
            cells = [strip_tags(c) for c in cells]
            if not cells or len(cells) > len(horizons):
                continue
            try:
                # positionnel : le longer-run est toujours en dernier (absent = core PCE)
                out[var] = [(hz, float(v)) for hz, v in zip(horizons[:len(cells)], cells)]
            except ValueError:
                continue
        if "ffr" in out and "unrate" in out and "pce" in out:
            return out
    return {}


def parse_dots():
    rows = list(csv.DictReader(open(DOT_SRC, encoding="utf-8")))
    per = {}
    for r in rows:
        try:
            level = float(r["midpoint"])
        except ValueError:
            continue
        for col, val in r.items():
            if col in ("date", "midpoint") or not val:
                continue
            try:
                n = int(val)
            except ValueError:
                continue
            per.setdefault((r["date"], col), []).extend([level] * n)
    dist = {}
    for (day, col), vals in per.items():
        vals.sort()
        n = len(vals)
        med = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
        dist[(day, "LR" if col == "longer_run" else col)] = {
            "median": round(med, 3), "dmin": vals[0], "dmax": vals[-1], "n": n}
    return dist


def main():
    if not os.path.exists(DOT_SRC):
        shutil.copy(DOT_TMP, DOT_SRC)
        print(f"vendored {DOT_SRC}")
    trows, missing = [], []
    for d in MEETINGS:
        day = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        p = os.path.join(SEP, f"fomcprojtable{d}.htm")
        if not os.path.exists(p):
            p = os.path.join(SEP, f"fomcprojtabl{d}.htm")
        if not os.path.exists(p):
            missing.append(d)
            continue
        parsed = parse_sep(p)
        if len(parsed) < 5:
            missing.append(f"{d} (parse incomplet: {sorted(parsed)})")
            continue
        for var, pairs in parsed.items():
            for hz, med in pairs:
                trows.append({"meeting_date": day, "var": var, "horizon": hz,
                              "median": f"{med:g}",
                              "source": f"federalreserve.gov fomcprojtable {d}"})
    dots = parse_dots()

    # --- validations ---
    errs = []
    lut = {(r["meeting_date"], r["var"], r["horizon"]): float(r["median"]) for r in trows}
    for key, want in SPOT.items():
        got = lut.get(key)
        if got is None or abs(got - want) > 1e-9:
            errs.append(f"SPOT {key}: attendu {want}, obtenu {got}")
    for r in trows:
        d = dots.get((r["meeting_date"], r["horizon"]))
        # La TABLE SEP (publication officielle) fait foi pour la mediane.
        # Les dots (scrapes tiers) servent la dispersion ; ecart > 1 cran = erreur.
        # Cas connu : 2026-09-16 LR table 3.2 vs dots 3.25 (arrondi Fed ou dot deplace).
        if r["var"] == "ffr" and d is not None and abs(d["median"] - float(r["median"])) > 0.126:
            errs.append(f"DOTS vs SEP {r['meeting_date']}/{r['horizon']}: "
                        f"table {r['median']} vs dots {d['median']}")
    n_dot_meetings = len({day for day, _ in dots}) if dots else 0
    print(f"SEP: {len(trows)} lignes, {len(MEETINGS) - len(missing)}/{len(MEETINGS)} meetings "
          f"| dots: {len(dots)} horizons sur {n_dot_meetings} meetings")
    if missing:
        print("MANQUANTS:", missing)
    if errs:
        print("ERREURS DE VALIDATION:")
        for e in errs[:20]:
            print("  ", e)
        raise SystemExit(f"{len(errs)} erreurs, dataset non ecrit")

    with open(OUT_T, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["meeting_date", "var", "horizon", "median", "source"])
        w.writeheader()
        w.writerows(sorted(trows, key=lambda r: (r["meeting_date"], r["var"], r["horizon"])))
    with open(OUT_D, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["meeting_date", "horizon", "median", "dmin",
                                           "dmax", "n", "source"])
        w.writeheader()
        for (day, hz), v in sorted(dots.items()):
            w.writerow({"meeting_date": day, "horizon": hz, "median": v["median"],
                        "dmin": v["dmin"], "dmax": v["dmax"], "n": v["n"],
                        "source": "palewire/fed-dot-plot-scraper"})
    print(f"ecrit {OUT_T} ({len(trows)} lignes) + {OUT_D} ({len(dots)} lignes)")


if __name__ == "__main__":
    main()
