"""Jointure stance Fed x ES/NQ : le regime suit-il les grandes tendances ?

Pour chaque jour trade (close RTH), stance as-of (dernier event <= jour),
momentum 10Y 20/60 seances (tnx, seuil +/-50 bp) et rendements forward 5/20/60
seances sur rth_close. Stats par (stance x momentum) et par stance seule.

Sorties :
  donnees/regime/stance_index_fwd.csv (lignes jour : date, inst, close, stance_label,
      real_gap_bps, mom20_bp, mom60_bp, config, fwd5/20/60_pct)
  donnees/regime/stance_index_report.md (tableaux + lecture)

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/join_stance_index.py
"""
import csv
import math
import os
from statistics import mean, median, stdev

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
SRC = os.path.join(REGIME, "sources")

HORIZONS = (5, 20, 60)
SEUIL_MOM = 50.0  # 50 bp sur mom60 (mom en bp : (tnx[t]-tnx[t-60])*100)


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(x):
    try:
        return float(x) if x not in (None, "") else None
    except ValueError:
        return None


def side(label):
    if label in ("restrictif", "nettement restrictif"):
        return "R"
    if label in ("accommodant", "nettement accommodant"):
        return "A"
    if label == "neutre":
        return "N"
    return ""


def momdir(m):
    if m is None:
        return ""
    if m > SEUIL_MOM:
        return "up"
    if m < -SEUIL_MOM:
        return "down"
    return "flat"


def main():
    idx = load_csv(os.path.join(REGIME, "index_daily.csv"))
    stance = sorted(load_csv(os.path.join(REGIME, "fed_stance.csv")),
                    key=lambda r: (r["date_et"], r["variant"]))
    px = load_csv(os.path.join(SRC, "market_pricing_daily.csv"))
    tnx_days = sorted(d["date"] for d in px if d.get("tnx"))
    tnx = {d["date"]: float(d["tnx"]) for d in px if d.get("tnx")}
    pos_tnx = {d: i for i, d in enumerate(tnx_days)}

    closes = {}
    for r in idx:
        closes.setdefault(r["inst"], {})[r["date"]] = float(r["rth_close"])
    days = {inst: sorted(v) for inst, v in closes.items()}
    pos = {inst: {d: i for i, d in enumerate(dd)} for inst, dd in days.items()}

    # stance du jour = dernier event <= jour (ligne du dernier event du jour)
    ev_by_day = {}
    for r in stance:
        ev_by_day.setdefault(r["date_et"][:10], []).append(r)
    ev_days = sorted(ev_by_day)

    def stance_of(day):
        best = None
        for d in ev_days:
            if d <= day:
                best = d
            else:
                break
        if best is None:
            return None
        return ev_by_day[best][-1]

    rows = []
    for inst in ("ES", "NQ"):
        for t in days[inst]:
            s = stance_of(t)
            if s is None or not s["stance_label"]:
                continue
            i = pos_tnx.get(t)
            m20 = m60 = None
            if i is not None:
                if i - 20 >= 0:
                    m20 = round((tnx[t] - tnx[tnx_days[i - 20]]) * 100)
                if i - 60 >= 0:
                    m60 = round((tnx[t] - tnx[tnx_days[i - 60]]) * 100)
            fw = {}
            for h in HORIZONS:
                j = pos[inst][t] + h
                fw[h] = round((closes[inst][days[inst][j]] / closes[inst][t] - 1) * 100, 3) \
                    if j < len(days[inst]) else None
            rows.append({"date": t, "inst": inst, "close": f"{closes[inst][t]:g}",
                         "stance_label": s["stance_label"], "side": side(s["stance_label"]),
                         "real_gap_bps": s["real_gap_bps"],
                         "mom20_bp": "" if m20 is None else m20,
                         "mom60_bp": "" if m60 is None else m60,
                         "momdir": momdir(m60),
                         "config": f"{side(s['stance_label'])}/{momdir(m60)}",
                         "fwd5_pct": "" if fw[5] is None else fw[5],
                         "fwd20_pct": "" if fw[20] is None else fw[20],
                         "fwd60_pct": "" if fw[60] is None else fw[60]})
    rows = [r for r in rows if r["side"] and r["momdir"]]
    with open(os.path.join(REGIME, "stance_index_fwd.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"ecrit stance_index_fwd.csv : {len(rows)} lignes")

    # ---------- stats ----------
    def stats(vals):
        vals = [v for v in vals if v is not None]
        n = len(vals)
        if n < 5:
            return f"N={n} (insuffisant)"
        sd = stdev(vals) if n > 1 else 0.0
        t = mean(vals) / sd * math.sqrt(n) if sd else 0.0
        hr = sum(1 for v in vals if v > 0) / n
        return (f"N={n} moy={mean(vals):+.2f}% med={median(vals):+.2f}% "
                f"hit={hr:.0%} sd={sd:.2f} t={t:+.1f}")

    lines = ["# Stance x ES/NQ — le regime suit-il les tendances ?",
             "", f"Base : {len(rows)} jours (2022-2025, rollovers J-8, trous 6j/roll absorbes par offsets en seances).",
             "Forwards 5/20/60 seances sur close RTH. Momentum 10Y : tnx[t]-tnx[t-60] en bp, seuil +/-50.",
             "Stats : t indicatif (forwards chevauchants -> autocorrelation), lire d'abord N, mediane, hit rate.",
             ""]
    for inst in ("ES", "NQ"):
        sub = [r for r in rows if r["inst"] == inst]
        lines += [f"## {inst} ({len(sub)} j)", ""]
        for h in HORIZONS:
            lines.append(f"### forward {h}j")
            base = [num(r[f"fwd{h}_pct"]) for r in sub]
            lines.append(f"- tous jours : {stats(base)}")
            for s in ("R", "A", "N"):
                v = [num(r[f"fwd{h}_pct"]) for r in sub if r["side"] == s]
                lines.append(f"- stance {s} : {stats(v)}")
            lines.append("- par config (stance/mom60) :")
            for c in sorted({r["config"] for r in sub}):
                v = [num(r[f"fwd{h}_pct"]) for r in sub if r["config"] == c]
                lines.append(f"  - {c} : {stats(v)}")
            lines.append("")
    rep = os.path.join(REGIME, "stance_index_report.md")
    lines += ["## Lecture (ne pas lire les labels au premier degre)",
              "",
              "- Les labels sont des MARQUEURS D'EPOQUE, pas des signaux directionnels : A = 2022",
              "  (bear, Fed en retard sur la courbe), R = 2023-2025 (plateau restrictif + bull).",
              "  'Restrictif -> acheter' serait une lecture naive et dangereuse hors-echantillon.",
              "- Ce que le regime fait bien : SEPARER les grandes tendances. A vs R ont des",
              "  distributions forward opposees sur les deux indices et les trois horizons.",
              "- Meilleure config : R/down (restrictif + 10Y en baisse >50bp/60j = desinflation,",
              "  la politique mord, pivot anticipe) : ES60 +7.20% hit 99, NQ60 +8.84% hit 95.",
              "  C'est la config 'soft landing' (fin 2023, ete 2024).",
              "- Pire config court terme : A/up (retard + 10Y qui flambe) : NQ20 -2.36% hit 40.",
              "  Pire config 60j : A/flat (bear qui saigne) : ES med -2.76% hit 30, NQ med -5.52% hit 26.",
              "  A/down n'est jamais observe (10Y 60j jamais < -50bp en stance A sur 2022-25).",
              "- R/up (restrictif + 10Y qui monte = tension late-cycle) reste positif mais faible :",
              "  ES60 +2.02% hit 56 vs +7.20% en R/down. Le 10Y discrimine DANS le regime.",
              "- Limites : un seul cycle (pas de vrai easing-cycle haussier observe), forwards",
              "  chevauchants (quelques episodes independants : T4-2023, S2-2024), drift haussier",
              "  2023-25 qui gonfle la baseline. Usage recommande : FILTRE de conviction/taille,",
              "  pas signal autonome. Anticipation = transitions R/up -> R/down (pivot price),",
              "  a tester en walk-forward.",
              ""]
    with open(rep, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\necrit {rep}")


if __name__ == "__main__":
    main()
