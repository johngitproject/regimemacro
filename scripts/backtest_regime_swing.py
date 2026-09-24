"""Backtest strategie REGIME SWING (ES+NQ, daily RTH close) + walk-forward.

Couche 1 (biais de fond, rebalance sur changement de config) :
  R/down long 1.0 | R/flat long 0.75 | R/up FLAT | N/* long 0.5 | A/down FLAT
  A/flat short 0.5 | A/up short 1.0   (NQ : taille / 1.4, vol-adjust recherche)
Couche 2 (tactique events) :
  - blackout : pas de NOUVELLE entree les 2 seances avant un CPI/FOMC (calendrier
    connu d'avance ; positions gardees)
  - renfort +0.5 (cap |pos| 1.5) sur surprise ALIGNEE (dovish<->long, hawkish<->short),
    expire J+20
  - sortie d'urgence : surprise CONTRE >= seuil -> cloture au close SUIVANT (J+1),
    re-entree seulement sur nouvelle config favorable
Sorties (au close t) : flip/neutralisation, fin de boost, stop temporel 60 seances
par lot, stop technique -3 % par lot.
Kill-switch : stance A + tendance ES 60j positive 40 seances d'affilee -> FLAT force.
Lots : {inst, dir, size, entry, px_in, exp}. Executions au close RTH.

Couts (hypotheses documentees) : par transaction et par contrat, 1 tick spread+slip
+ $2.50 commission -> ES $15.00 (tick $12.50), NQ $7.50 (tick $5.00).

Walk-forward : IS 2022-23 / OOS 2024-25 puis inverse. Benchmarks : buy&hold ES 1 contrat,
config-seule (couche 1 sans events). Sensibilites : seuil mom 30/70 bp, sans jours bridges.
Metriques : CAGR (notionnel $100k), Sharpe daily annualise, maxDD, winrate/PF trades,
exposition %. Critere passage reel : PF OOS > 1.3 ET maxDD < 50 % du buy&hold.

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/backtest_regime_swing.py [--index FICHIER] [--mom-thr BP]
"""
import argparse
import csv
import math
import os
from datetime import date
from statistics import mean, stdev

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
SRC = os.path.join(REGIME, "sources")

PT = {"ES": 50.0, "NQ": 20.0}          # $ par point
COST = {"ES": 15.0, "NQ": 7.5}         # $ par transaction et par contrat
SIZE_NQ = 1.0 / 1.4
SEUIL = {"CPI": 0.1, "PCE": 0.1, "NFP": 30.0, "UNEMP": 0.1, "FED": 0.1}
BASE_POS = {"R/down": 1.0, "R/flat": 0.75, "R/up": 0.0, "N/down": 0.5, "N/up": 0.5,
            "N/flat": 0.5, "A/down": 0.0, "A/flat": -0.5, "A/up": -1.0}
BOOST, BOOST_EXP, TSTOP = 0.5, 20, 60
TECHSTOP = -0.03
KILL_WIN = 40
NOTIONAL = 100000.0


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(x):
    try:
        return float(x) if x not in (None, "") else None
    except ValueError:
        return None


def ymd(s):
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def side(label):
    if label in ("restrictif", "nettement restrictif"):
        return "R"
    if label in ("accommodant", "nettement accommodant"):
        return "A"
    return "N" if label == "neutre" else ""


def load_inputs(index_file):
    idx = {(r["inst"], r["date"]): float(r["rth_close"])
           for r in load_csv(os.path.join(REGIME, index_file))}
    days = {i: sorted(d for (j, d) in idx if j == i) for i in ("ES", "NQ")}
    stance = sorted(load_csv(os.path.join(REGIME, "fed_stance.csv")),
                    key=lambda r: (r["date_et"], r["variant"]))
    ev_by_day = {}
    for r in stance:
        ev_by_day.setdefault(r["date_et"][:10], []).append(r)
    px = {r["date"]: float(r["tnx"]) for r in load_csv(os.path.join(SRC, "market_pricing_daily.csv"))
          if r.get("tnx")}
    tdays = sorted(px)
    cal = [r for r in load_csv(os.path.join(REGIME, "calendar_macro_2022_2026.csv"))
           if r["status"] == "released"]
    blackout, surprises = set(), {}
    for r in cal:
        d = r["date_et"][:10]
        if r["event_type"] in ("CPI", "FED"):
            blackout.add(d)
        s = num(r["surprise"])
        if s is None:
            continue
        sev = SEUIL[r["event_type"]]
        if r["event_type"] == "UNEMP":
            sens = 1 if s <= -sev else (-1 if s >= sev else 0)  # chomage - = hawkish
        else:
            sens = 1 if s >= sev else (-1 if s <= -sev else 0)  # +1 = hawkish
        if sens and abs(s) / sev >= 0.5:
            surprises.setdefault(d, []).append((sens, abs(s) / sev))
    return idx, days, ev_by_day, px, tdays, blackout, surprises


def run(index_file="index_daily.csv", mom_thr=50.0, layer2=True, vol_target=0.0,
        emerg_mag=1.0, reblock_max=None):
    idx, days, ev_by_day, px, tdays, blackout, surprises = load_inputs(index_file)
    ev_days = sorted(ev_by_day)
    sess = sorted(set(days["ES"]) & set(days["NQ"]))
    spos = {d: i for i, d in enumerate(sess)}
    all_days = sorted(set(days["ES"]) | set(days["NQ"]))
    # vol realisee 20 seances par instrument (pour vol targeting)
    vol20 = {}
    for inst in ("ES", "NQ"):
        dd = days[inst]
        for k in range(21, len(dd)):
            rets = [math.log(idx[(inst, dd[j])] / idx[(inst, dd[j - 1])])
                    for j in range(k - 20, k + 1)]
            m = sum(rets) / len(rets)
            var = sum((r - m) ** 2 for r in rets) / len(rets)
            vol20[(inst, dd[k])] = math.sqrt(var) if var > 0 else 0.0

    def stance_of(day):
        ref = next((d for d in reversed(ev_days) if d <= day), None)
        return ev_by_day[ref][-1] if ref else None

    def momday(day):
        past = [d for d in tdays if d <= day]
        if len(past) <= 60:
            return "", None
        m = (px[past[-1]] - px[past[-61]]) * 100
        return ("up" if m > mom_thr else ("down" if m < -mom_thr else "flat")), round(m)

    cfg, momv = {}, {}
    for t in all_days:
        s = stance_of(t)
        sd = side(s["stance_label"]) if s else ""
        md, mv = momday(t)
        cfg[t] = f"{sd}/{md}" if sd and md else ""
        momv[t] = mv
    tr60 = {}
    for t in all_days:
        if t in spos and spos[t] >= 60 and (("ES", t) in idx):
            c0 = idx[("ES", t)]
            c1 = idx[("ES", sess[spos[t] - 60])]
            tr60[t] = c0 / c1 - 1
    blk = set()
    for b in blackout:
        if b in spos:
            for k in (1, 2):
                if spos[b] - k >= 0:
                    blk.add(sess[spos[b] - k])

    lots, closed = [], []
    eq, eq_days, daily = [0.0], [], []
    prev_latent, reblock_day, kill_days = 0.0, None, 0
    c_emerg, c_boost, c_black, c_reblock = 0, 0, 0, 0

    for t in all_days:
        i = spos.get(t)
        s = stance_of(t)
        sd = side(s["stance_label"]) if s else ""
        if sd == "A" and i is not None:
            win = [tr60.get(sess[j], -1) for j in range(max(0, i - KILL_WIN + 1), i + 1)]
            kill = len(win) == KILL_WIN and all(v > 0 for v in win)
        else:
            kill = False
        if kill:
            kill_days += 1
        tgt = 0.0 if kill else BASE_POS.get(cfg[t], 0.0)
        px_t = {inst: idx.get((inst, t)) for inst in ("ES", "NQ")}
        day_pnl, open_fees = 0.0, 0.0

        def close_lot(lot, c):
            pnl = lot["dir"] * (c - lot["px_in"]) * PT[lot["inst"]] * lot["size"] \
                - COST[lot["inst"]] * lot["size"]
            closed.append({"day": t, "inst": lot["inst"], "dir": lot["dir"], "pnl": pnl})
            return pnl

        # (a) sorties d'urgence programmees (marquees un jour avant, executees au close t)
        rest = []
        for lot in lots:
            if lot.pop("force_exit", False) and px_t[lot["inst"]] is not None:
                day_pnl += close_lot(lot, px_t[lot["inst"]])
                reblock_day = t
                c_emerg += 1
            else:
                rest.append(lot)
        lots = rest
        # (b) sorties standard au close t
        rest = []
        for lot in lots:
            c = px_t[lot["inst"]]
            if c is None:
                rest.append(lot)
                continue
            ret = lot["dir"] * (c / lot["px_in"] - 1)
            out = tgt == 0.0 or ((tgt > 0) != (lot["dir"] > 0))
            out = out or (lot["exp"] != -1 and t >= lot["exp"])
            out = out or (i is not None and i - spos.get(lot["entry"], i) >= TSTOP)
            out = out or ret <= TECHSTOP
            if out:
                day_pnl += close_lot(lot, c)
            else:
                rest.append(lot)
        lots = rest
        # (c) marquage urgence : surprise du jour J contre les lots, |mag| >= emerg_mag
        #     (execution J+1)
        if layer2 and t in surprises:
            for lot in lots:
                for sens, mag in surprises[t]:
                    if mag >= emerg_mag and (sens > 0) != (lot["dir"] > 0):
                        lot["force_exit"] = True
        # (d) entrees au close t
        reblocked = False
        if reblock_day is not None:
            if cfg.get(t) != cfg.get(reblock_day):
                reblock_day = None  # nouvelle config : leve le blocage
            elif reblock_max is None:
                reblocked = True
                c_reblock += 1
            elif i is not None and i - spos.get(reblock_day, i) < reblock_max:
                reblocked = True
                c_reblock += 1
            else:
                reblock_day = None  # borne atteinte : leve le blocage
        blocked = (layer2 and t in blk) or reblocked
        if layer2 and t in blk:
            c_black += 1
        if not blocked and i is not None:
            boost = 0.0
            if layer2 and t in surprises and tgt != 0.0:
                for sens, mag in surprises[t]:
                    if mag >= 1.0 and ((sens > 0 and tgt < 0) or (sens < 0 and tgt > 0)):
                        boost = 0.5 * (1 if tgt > 0 else -1)
            for inst, unit in (("ES", 1.0), ("NQ", SIZE_NQ)):
                want = tgt * unit + (boost * unit if boost else 0.0)
                if vol_target > 0:  # vol targeting : deleverage seul, jamais de levier
                    v = vol20.get((inst, t), 0.0)
                    if v > 0:
                        want *= min(1.0, vol_target / v)
                cap = 1.5 * unit
                want = max(-cap, min(cap, want))
                cur = sum(x["dir"] * x["size"] for x in lots if x["inst"] == inst)
                delta = want - cur
                if abs(delta) > 1e-9 and px_t[inst] is not None and \
                   (cur == 0 or (delta > 0) == (cur > 0)):
                    exp = sess[min(len(sess) - 1, i + BOOST_EXP)] \
                        if boost and (delta > 0) == (boost > 0) else -1
                    if boost and (delta > 0) == (boost > 0):
                        c_boost += 1
                    lots.append({"inst": inst, "dir": 1 if delta > 0 else -1,
                                 "size": abs(delta), "entry": t,
                                 "px_in": px_t[inst], "exp": exp})
                    open_fees += COST[inst] * abs(delta)
        latent = sum(x["dir"] * ((px_t[x["inst"]] or x["px_in"]) - x["px_in"])
                     * PT[x["inst"]] * x["size"] for x in lots)
        step = day_pnl - open_fees + (latent - prev_latent)
        prev_latent = latent
        eq.append(eq[-1] + step)
        eq_days.append(t)
        daily.append(step)
    return {"equity": eq[1:], "days": eq_days, "daily": daily, "closed": closed,
            "kill_days": kill_days, "diag": {"emerg": c_emerg, "boost": c_boost,
                                             "black": c_black, "reblock": c_reblock}}


def perf(eq, days, closed):
    rets = [b - a for a, b in zip(eq, eq[1:])] if len(eq) > 1 else []
    yrs = (ymd(days[-1]) - ymd(days[0])).days / 365.25 if len(days) > 1 else 0
    tot = eq[-1] - eq[0] if eq else 0.0
    cagr = (1 + tot / NOTIONAL) ** (1 / yrs) - 1 if yrs > 0 and tot > -NOTIONAL else -1.0
    sd = stdev(rets) if len(rets) > 1 else 0.0
    sharpe = (mean(rets) / sd * math.sqrt(252)) if sd else 0.0
    peak, dd = (eq[0], 0.0) if eq else (0.0, 0.0)
    for v in eq:
        peak = max(peak, v)
        dd = min(dd, v - peak)
    pnls = [c["pnl"] for c in closed]
    wins = [x for x in pnls if x > 0]
    gl = -sum(x for x in pnls if x < 0)
    expo = (sum(1 for r in rets if r != 0) / len(rets)) if rets else 0
    return {"tot": tot, "cagr": cagr, "sharpe": sharpe, "maxdd": dd, "expo": expo,
            "ntr": len(pnls), "wr": (len(wins) / len(pnls)) if pnls else 0,
            "pf": ((sum(wins) / gl) if gl else float("inf")) if pnls else 0,
            "exp": (mean(pnls)) if pnls else 0}


def fmt(m):
    pf = "inf" if m["pf"] == float("inf") else f"{m['pf']:.2f}"
    return (f"tot={m['tot']:+.0f}$ CAGR={m['cagr']:+.1%} Sharpe={m['sharpe']:+.2f} "
            f"maxDD={m['maxdd']:+.0f}$ expo={m['expo']:.0%} | "
            f"trades={m['ntr']} WR={m['wr']:.0%} PF={pf} exp={m['exp']:+.2f}$")


def slice_it(res, y0, y1):
    idx = [k for k, d in enumerate(res["days"]) if y0 <= d[:4] <= y1]
    if not idx:
        return None
    # reconstruit : equity de la tranche = cumul des daily de la tranche
    cum, out = 0.0, [0.0]
    for k in idx:
        cum += res["daily"][k]
        out.append(cum)
    days = [res["days"][k] for k in idx]
    closed = [c for c in res["closed"] if y0 <= c["day"][:4] <= y1]
    return perf(out, days, closed)


def buyhold(index_file):
    idx = {(r["inst"], r["date"]): float(r["rth_close"])
           for r in load_csv(os.path.join(REGIME, index_file)) if r["inst"] == "ES"}
    days = sorted(d for (i, d) in idx)
    eq, prev = [0.0], None
    for k, d in enumerate(days):
        if k == 0:
            eq.append(-COST["ES"])  # entree
        else:
            eq.append(eq[-1] + (idx[("ES", d)] - idx[("ES", days[k - 1])]) * PT["ES"])
    eq[-1] -= COST["ES"]  # sortie
    closed = [{"day": days[-1], "inst": "ES", "dir": 1, "pnl": eq[-1]}]
    return {"equity": eq[1:], "days": days, "closed": closed}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Backtest REGIME SWING + walk-forward.")
    ap.add_argument("--index", default="index_daily.csv")
    ap.add_argument("--mom-thr", type=float, default=50.0)
    a = ap.parse_args(argv)
    print(f"index={a.index} mom_thr={a.mom_thr} "
          f"(couts ES ${COST['ES']}/NQ ${COST['NQ']} par transaction/contrat, notionnel ${NOTIONAL:.0f})")
    full = run(a.index, a.mom_thr, layer2=True)
    base = run(a.index, a.mom_thr, layer2=False)
    bh = buyhold(a.index)
    print(f"FULL   : {fmt(perf(full['equity'], full['days'], full['closed']))} kill={full['kill_days']}j diag={full['diag']}")
    print(f"CONFIG : {fmt(perf(base['equity'], base['days'], base['closed']))} kill={base['kill_days']}j")
    print(f"B&H ES : {fmt(perf(bh['equity'], bh['days'], bh['closed']))}")
    # v2 : CONFIG + vol targeting + urgences restreintes (|mag|>=2, reblocage borne 5j)
    v2 = run(a.index, a.mom_thr, layer2=True, vol_target=0.01, emerg_mag=2.0, reblock_max=5)
    print(f"V2     : {fmt(perf(v2['equity'], v2['days'], v2['closed']))} kill={v2['kill_days']}j diag={v2['diag']}")
    for tag, y0, y1 in (("IS 22-23", "2022", "2023"), ("OOS 24-25", "2024", "2025")):
        m = slice_it(v2, y0, y1)
        print(f"  {tag} V2: {fmt(m) if m else 'n/a'}")
    for vt in (0.0075, 0.015):
        s = run(a.index, a.mom_thr, layer2=True, vol_target=vt, emerg_mag=2.0, reblock_max=5)
        print(f"V2 vol{vt:g} : {fmt(perf(s['equity'], s['days'], s['closed']))}")
    s = run(a.index, a.mom_thr, layer2=True, vol_target=0.01, emerg_mag=3.0, reblock_max=5)
    print(f"V2 mag3 : {fmt(perf(s['equity'], s['days'], s['closed']))} diag={s['diag']}")
    for tag, y0, y1 in (("IS 22-23", "2022", "2023"), ("OOS 24-25", "2024", "2025"),
                        ("IS 24-25", "2024", "2025"), ("OOS 22-23", "2022", "2023")):
        m = slice_it(full, y0, y1)
        print(f"  {tag} FULL: {fmt(m) if m else 'n/a'}")
    for tag, y0, y1 in (("IS 22-23", "2022", "2023"), ("OOS 24-25", "2024", "2025")):
        m = slice_it(base, y0, y1)
        print(f"  {tag} CONFIG: {fmt(m) if m else 'n/a'}")
    for y in ("2022", "2023", "2024", "2025"):
        mf = slice_it(full, y, y)
        mc = slice_it(base, y, y)
        print(f"  {y} FULL: {fmt(mf) if mf else 'n/a'}")
        print(f"  {y} CONFIG: {fmt(mc) if mc else 'n/a'}")
    for thr in (30.0, 70.0):
        s = run(a.index, thr, layer2=True)
        print(f"SENSI mom{thr:g} : {fmt(perf(s['equity'], s['days'], s['closed']))}")
    print("criteres passage reel : PF OOS > 1.3 ET maxDD < 50% du B&H (lire lignes OOS/B&H)")


if __name__ == "__main__":
    main()
