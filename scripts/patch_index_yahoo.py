"""Bouche les trous NT8 avec les closes Yahoo (jamais de niveaux inventes).

Methode (choisie apres diagnostic : closes Yahoo ~= closes fin de journee NT8,
mediane 0.09 %, mais != closes RTH 15h00 — derive d'apres-midi/soiree reelle) :
  - fenetres interieures (trous > 4 j calendaires) : niveaux interieurs = closes
    Yahoo bruts, ancres NT8 aux deux bouts. QC = SAUT de base Yahoo/NT8 entre les
    ancres (un roll divergent au milieu fausse la shape) : > 2 % = fenetre NON
    bouchee ; > 0.5 % = qa=roll_suspect (conserve, borne par les ancres).
  - queue (apres le dernier close NT8, cap 2026-04-30) : retours Yahoo vers l'avant
    sans ancre aval (derive possible ~1 %, documentee).
  - QC par fenetre : |residu| > 2 % -> qa=roll_suspect ; |ret Yahoo| > 8 % un jour
    -> qa=spike. Aucun jour echoue n'est invente : tout jour patche est trace
    source=yahoo_bridge + qa. Snapshot pre-patch conserve (index_daily_nt8_only.csv).

Entrees : index_daily.csv (colonne source ajoutee : nt8|yahoo_bridge),
          sources/yahoo_index_daily.csv
Sorties : index_daily.csv reecrit, index_daily_nt8_only.csv (snapshot),
          rapport QC affiche (correlation des retours, residus par fenetre).

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/patch_index_yahoo.py
"""
import csv
import math
import os
import shutil
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
SRC = os.path.join(REGIME, "sources")
IDX = os.path.join(REGIME, "index_daily.csv")
SNAP = os.path.join(REGIME, "index_daily_nt8_only.csv")
TAIL_CAP = "2026-04-30"


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def ymd(s):
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def main():
    if not os.path.exists(SNAP):
        shutil.copy(IDX, SNAP)
    idx = load_csv(IDX)
    # idempotence : on repart toujours des seuls closes NT8
    idx = [r for r in idx if r.get("source", "nt8") == "nt8"]
    y = {(r["inst"], r["date"]): float(r["close"])
         for r in load_csv(os.path.join(SRC, "yahoo_index_daily.csv"))}

    # correlation des retours journaliers sur chevauchements (diagnostic)
    print("correlation retours Yahoo vs NT8 (chevauchements) :")
    for inst in ("ES", "NQ"):
        com = sorted({r["date"] for r in idx if r["inst"] == inst}
                     & {d for (i, d) in y if i == inst})
        n = {r["date"]: (float(r["rth_close"]), float(r["eth_close"] or 0) or None)
             for r in idx if r["inst"] == inst}
        for tag, k in (("RTH", 0), ("ETH", 1)):
            ry, rn = [], []
            for i in range(1, len(com)):
                a0, a1 = y.get((inst, com[i - 1])), y.get((inst, com[i]))
                b0, b1 = n[com[i - 1]][k], n[com[i]][k]
                if None in (a0, a1, b0, b1) or 0 in (a0, a1, b0, b1):
                    continue
                ry.append(math.log(a1 / a0))
                rn.append(math.log(b1 / b0))
            my, mn = sum(ry) / len(ry), sum(rn) / len(rn)
            cov = sum((a - my) * (b - mn) for a, b in zip(ry, rn)) / len(ry)
            sy = (sum((a - my) ** 2 for a in ry) / len(ry)) ** 0.5
            sn = (sum((b - mn) ** 2 for b in rn) / len(rn)) ** 0.5
            print(f"  {inst} vs {tag}: {cov / sy / sn:.4f} ({len(com)} j)")

    base = {(r["inst"], r["date"]): r for r in idx}
    patched = []
    for inst in ("ES", "NQ"):
        days = sorted(r["date"] for r in idx if r["inst"] == inst)
        contract = {r["date"]: r["contract"] for r in idx if r["inst"] == inst}
        nclose = {r["date"]: float(r["rth_close"]) for r in idx if r["inst"] == inst}
        # 1) fenetres interieures : QC = saut de base Yahoo/NT8 entre les ancres
        #    (un roll divergent au milieu fausse la shape). Ancre Yahoo = barre dispo
        #    la plus proche a +/-5 j calendaires (trous Yahoo : Juneteenth...).
        #    > 2 % = fenetre NON bouchee ; > 0.5 % = qa=roll_suspect (conservee, bornee).
        for a, b in zip(days, days[1:]):
            if (ymd(b) - ymd(a)).days <= 4:
                continue
            yd_all = sorted(d for (i, d) in y if i == inst)
            ya = next((d for d in reversed(yd_all) if d <= a and (ymd(a) - ymd(d)).days <= 5), None)
            yb = next((d for d in yd_all if d >= b and (ymd(d) - ymd(b)).days <= 5), None)
            if ya is None or yb is None:
                print(f"  pont {inst} {a} -> {b} : Yahoo manquant aux ancres, ignore")
                continue
            jump = abs(y[(inst, yb)] / nclose[b] - y[(inst, ya)] / nclose[a])
            if jump > 0.02:
                print(f"  pont {inst} {a} -> {b} : saut de base {jump * 100:.2f}% > 2 %, NON bouche")
                continue
            yd = sorted(d for d in
                        ([k[1] for k in y if k[0] == inst and a < k[1] < b] + [a, b]))
            # niveaux interieurs = closes Yahoo bruts ; les marches aux ancres absorbent
            # la base (petite en general, cf. controle d'alignement). Le QC porte sur le
            # SAUT de base entre les ancres (= roll divergent au milieu) :
            spike = any(abs(math.log(y[(inst, d1)] / y[(inst, d0)])) > 0.08
                        for d0, d1 in zip(yd, yd[1:]) if d0 != a and d1 != b)
            qa = "roll_suspect" if jump > 0.005 else ("spike" if spike else "ok")
            for d1 in yd[1:-1]:
                patched.append({"date": d1, "inst": inst, "contract": contract[a] + "+",
                                "rth_close": f"{y[(inst, d1)]:g}",
                                "eth_close": f"{y[(inst, d1)]:g}",
                                "source": "yahoo_bridge", "qa": qa,
                                "qa_resid_pct": f"{jump * 100:+.2f}"})
            print(f"  pont {inst} {a} -> {b} : {len(yd) - 2} j, saut de base {jump * 100:+.2f}% [{qa}]")
        # 2) queue vers l'avant (cap TAIL_CAP)
        last = days[-1]
        yd = sorted(d for (i, d) in y if i == inst and last < d <= TAIL_CAP)
        lv = math.log(nclose[last])
        prev = nclose[last]
        for d in yd:
            r = math.log(y[(inst, d)] / prev)
            prev = y[(inst, d)]
            lv += r
            qa = "spike_tail" if abs(r) > 0.08 else "tail_no_anchor"
            patched.append({"date": d, "inst": inst, "contract": contract[last] + "+",
                            "rth_close": f"{math.exp(lv):g}", "eth_close": f"{math.exp(lv):g}",
                            "source": "yahoo_bridge", "qa": qa,
                            "qa_resid_pct": ""})
        print(f"  queue {inst} {last} -> {yd[-1] if yd else last} : {len(yd)} j [tail_no_anchor]")

    for r in idx:
        r.setdefault("source", "nt8")
        r.setdefault("qa", "")
        r.setdefault("qa_resid_pct", "")
    allrows = sorted(idx + patched, key=lambda r: (r["date"], r["inst"]))
    # dedup de securite (ne jamais ecraser un close NT8)
    seen, out = set(), []
    for r in sorted(allrows, key=lambda r: (r["date"], r["inst"], 0 if r["source"] == "nt8" else 1)):
        if (r["date"], r["inst"]) in seen:
            print(f"  DOUBLON ignore (NT8 prioritaire) : {r['date']} {r['inst']} {r['source']}")
            continue
        seen.add((r["date"], r["inst"]))
        out.append(r)
    with open(IDX, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "inst", "contract", "rth_close",
                                           "eth_close", "source", "qa", "qa_resid_pct"])
        w.writeheader()
        w.writerows(out)
    n_bridge = sum(1 for r in out if r["source"] == "yahoo_bridge")
    print(f"ecrit {IDX} : {len(out)} lignes dont {n_bridge} yahoo_bridge "
          f"({sum(1 for r in out if r.get('qa') == 'roll_suspect')} roll_suspect)")


if __name__ == "__main__":
    main()
