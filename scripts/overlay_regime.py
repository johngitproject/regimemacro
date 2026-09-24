# Overlay regime H10/H9/H14 sur trades.csv ssrn-v2 (FRED quotidien, stdlib uniquement).
# Methode anti-lookahead : toute valeur FRED rattachee a un trade est STRICTEMENT
# anterieure au jour du trade (dernier obs < date trade = cloture veille connue).
#   H10 : RISK-OFF = spread 10Y-2Y < 0 ET SPX < SMA200 (variante : pas de longs ce jour-la).
#   H9  : quintiles VIX veille (2025) + moyenne 21 obs ; variante taille 0.5x si VIX Q4-Q5
#         (couts supposes proportionnels = convention fractionnaire declaree).
#   H14 : spread HY OAS : widening = hausse sur 5 obs (~1 sem) -> RISK-OFF-credit ;
#         variante : breakouts longs OFF si widening (fades gardes).
# Sorties : donnees/backtest/ssrn-v2/regime_trades.csv + regime.md
import csv, os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(BASE, "donnees", "regime")
TRADES = os.path.join(BASE, "donnees", "backtest", "ssrn-v2", "trades.csv")
OUTD = os.path.join(BASE, "donnees", "backtest", "ssrn-v2")
NET = "net_NT-Lifetime_$"
BREAKOUTS = ("H1-ORB", "H1F-ORBf", "H2-MOM", "H2-MOM150", "H7-VWAPx")


def load(fname, col):
    d = {}
    with open(os.path.join(REG, fname), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            v = r[col].strip()
            if v != "":
                d[r["observation_date"]] = float(v)
    return d


def asof(d, series, strict=True):
    # dernier obs < d (strict, anti-lookahead) ou <= d.
    best = None
    for dt in series:
        if (dt < d if strict else dt <= d) and (best is None or dt > best):
            best = dt
    return best


def main():
    d10 = load("fred_DGS10_2025.csv", "DGS10")
    d2 = load("fred_DGS2_2025.csv", "DGS2")
    vix = load("fred_VIXCLS_2025.csv", "VIXCLS")
    hy = load("fred_HY_OAS_2025.csv", "HY_OAS")
    spx = load("fred_SP500_2024_2025.csv", "SP500")
    spx_days = sorted(spx)
    # SMA200 par date (200 obs, strictement anterieures pour l'usage final via asof).
    sma = {}
    for i, dt in enumerate(spx_days):
        if i + 1 >= 200:
            sma[dt] = sum(spx[x] for x in spx_days[i - 199:i + 1]) / 200.0
    # quintiles VIX sur 2025 (declare : historique court).
    vv = sorted(vix.values())
    q = [vv[int(len(vv) * p)] for p in (0.2, 0.4, 0.6, 0.8)]
    vix_days = sorted(vix)

    def vix_q(x):
        for i, t in enumerate(q):
            if x <= t:
                return i + 1
        return 5

    def vix21(dt):
        prior = [x for x in vix_days if x < dt][-21:]
        return sum(vix[x] for x in prior) / len(prior) if prior else None

    def hy_chg5(dt):
        prior = [x for x in sorted(hy) if x < dt][-5:]
        if len(prior) < 5:
            return None
        return hy[prior[-1]] - hy[prior[0]]

    trades = list(csv.DictReader(open(TRADES, encoding="utf-8")))
    rows = []
    nodata = 0
    for x in trades:
        d = x["date"]
        a = asof(d, d10)
        b = asof(d, d2)
        v = asof(d, vix)
        s = asof(d, spx)
        if not (a and b and v and s) or s not in sma:
            nodata += 1
            continue
        spread = d10[a] - d2[b]
        ro_rates = 1 if (spread < 0 and spx[s] < sma[s]) else 0
        below = 1 if spx[s] < sma[s] else 0
        vx = vix[v]
        chg = hy_chg5(d)
        ro_cred = 1 if (chg is not None and chg > 0) else 0
        rows.append({"date": d, "market": x["market"], "hyp": x["hyp"], "dir": x["dir"],
                     "net": float(x[NET]), "spread": round(spread, 2),
                     "riskoff_rates": ro_rates, "spx_below_sma": below, "vix": vx, "vix_q": vix_q(vx),
                     "vix21": round(vix21(d), 2) if vix21(d) else "",
                     "hy_chg5": round(chg, 2) if chg is not None else "",
                     "riskoff_credit": ro_cred})
    with open(os.path.join(OUTD, "regime_trades.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    L = ["# Overlay regime H10/H9/H14 -- trades ssrn-v2 x FRED (2025)",
         "",
         "_Usage perso. FRED sans cle (fredgraph.csv, 13/09/2026) : DGS10/DGS2/VIXCLS/HY-OAS 2025, "
         "SP500 2024-2025 (SMA200). BAA/AAA abandonnes (mensuels). "
         "Rattachement strictement anterieur au jour du trade (cloture veille, anti-lookahead). "
         f"Trades rattaches : {len(rows)}/{len(trades)} ({nodata} sans historique). "
         "Seuils VIX calibres sur 2025 seul (declare). Decision sur Lifetime $/contrat._", ""]
    L.append("## H10 -- RISK-OFF taux (spread<0 ET SPX<SMA200)")
    ro_days = sorted(set(r["date"] for r in rows if r["riskoff_rates"]))
    L.append(f"- jours RISK-OFF : {len(ro_days)}")
    # marginales (jambes separees, informatif : la conjonction stricte n'existe pas en 2025)
    for m in ("NQ", "ES"):
        sub = [r for r in rows if r["market"] == m]
        inv = [r for r in sub if r["spread"] < 0]
        bel = [r for r in sub if r["spx_below_sma"]]
        L.append(f"- {m}: jours spread<0 -> {len(set(r['date'] for r in inv))}j, "
                 f"trades N={len(inv)}" +
                 (f" exp={sum(r['net'] for r in inv) / len(inv):.2f}$" if inv else "") +
                 f" | jours SPX<SMA200 -> {len(set(r['date'] for r in bel))}j, "
                 f"trades N={len(bel)}" +
                 (f" exp={sum(r['net'] for r in bel) / len(bel):.2f}$" if bel else ""))
    for m in ("NQ", "ES"):
        sub = [r for r in rows if r["market"] == m]
        on = [r for r in sub if r["riskoff_rates"]]
        off = [r for r in sub if not r["riskoff_rates"]]
        e = lambda s: sum(r["net"] for r in s) / max(1, len(s))
        L.append(f"- {m}: ON N={len(on)} exp={e(on):.2f}$ | OFF N={len(off)} exp={e(off):.2f}$")
        for h in sorted(set(r["hyp"] for r in sub)):
            so = [r for r in on if r["hyp"] == h]
            if so:
                el = sum(r["net"] for r in so if r["dir"] == "1") / max(1, len([r for r in so if r["dir"] == "1"]))
                es = sum(r["net"] for r in so if r["dir"] == "-1") / max(1, len([r for r in so if r["dir"] == "-1"]))
                L.append(f"  - {h} en RISK-OFF: N={len(so)} longs={el:.2f}$ shorts={es:.2f}$")
        # variante : pas de longs en RISK-OFF
        base = sum(r["net"] for r in sub)
        var = sum(r["net"] for r in sub if not (r["riskoff_rates"] and r["dir"] == "1"))
        dropped = sum(1 for r in sub if r["riskoff_rates"] and r["dir"] == "1")
        L.append(f"  - variante sans-longs-OFF: {base:+.0f}$ -> {var:+.0f}$ ({dropped} longs retires)")
    L.append("")
    L.append("## H9 -- VIX veille (quintiles 2025) + sizing 0.5x si Q4-Q5")
    L.append(f"- seuils Q: {[round(t, 2) for t in q]}")
    for m in ("NQ", "ES"):
        sub = [r for r in rows if r["market"] == m]
        line = []
        for qi in (1, 2, 3, 4, 5):
            s = [r for r in sub if r["vix_q"] == qi]
            e = sum(r["net"] for r in s) / max(1, len(s))
            line.append(f"Q{qi}:N={len(s)}:{e:+.0f}$")
        L.append(f"- {m}: " + " | ".join(line))
        base = sum(r["net"] for r in sub)
        var = sum(r["net"] * (0.5 if r["vix_q"] >= 4 else 1.0) for r in sub)
        L.append(f"  - variante 0.5x en Q4-Q5 (couts proportionnels, convention declaree): "
                 f"{base:+.0f}$ -> {var:+.0f}$")
    L.append("")
    L.append("## H14 -- Credit HY widening 5 obs (proxy pente)")
    for m in ("NQ", "ES"):
        sub = [r for r in rows if r["market"] == m]
        w = [r for r in sub if r["riskoff_credit"]]
        n = [r for r in sub if not r["riskoff_credit"]]
        e = lambda s: sum(r["net"] for r in s) / max(1, len(s))
        L.append(f"- {m}: widening N={len(w)} exp={e(w):.2f}$ | ok N={len(n)} exp={e(n):.2f}$")
        bl = [r for r in w if r["hyp"] in BREAKOUTS and r["dir"] == "1"]
        if bl:
            L.append(f"  - breakouts longs en widening: N={len(bl)} exp={e(bl):.2f}$")
        base = sum(r["net"] for r in sub)
        var = sum(r["net"] for r in sub if not (r["riskoff_credit"] and r["hyp"] in BREAKOUTS and r["dir"] == "1"))
        dropped = sum(1 for r in sub if r["riskoff_credit"] and r["hyp"] in BREAKOUTS and r["dir"] == "1")
        L.append(f"  - variante sans-breaklongs-widening: {base:+.0f}$ -> {var:+.0f}$ ({dropped} retires)")
    with open(os.path.join(OUTD, "regime.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"REGIME trades={len(rows)}/{len(trades)}")
    print(f"RISK-OFF jours={len(ro_days)}")


if __name__ == "__main__":
    main()
