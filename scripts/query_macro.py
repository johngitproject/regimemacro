"""Interroge donnees/regime/calendar_macro_2022_2026.csv en langage metier.

stdlib uniquement (utilisable aussi hors venv) :
  .\\venv\\Scripts\\python.exe scripts/query_macro.py <commande> [options]

Commandes :
  direction --event CPI [--variant headline_yoy] [--date AAAA-MM-JJ | --next]
      -> les economistes envisagent-ils une hausse ou une baisse ? (forecast vs previous)
  surprise  --event CPI [--variant headline_yoy] --date AAAA-MM-JJ
      -> y a-t-il eu surprise le jour de la news ? (actual vs forecast)
  trend     --event CPI [--variant headline_yoy] [--n 6] [--end AAAA-MM-JJ]
      -> evolution des prints precedents sur N releases (streak + delta)
  recap     --date AAAA-MM-JJ
      -> toutes les news du jour avec surprises
  next      [--event CPI]
      -> prochain(s) chiffre(s) attendu(s) avec consensus connu
  stance    --date AAAA-MM-JJ
      -> ou en est-on vs seuils Fed ? taux, r*/u*, gaps, Taylor, stance reelle,
         dots annee en cours, guidance en vigueur, pricing veille
  repricing --date AAAA-MM-JJ
      -> surprises du jour + reaction marche (cloture J vs veille : ZQ, T-bills,
         5Y, 10Y, en bp)
  filtre    --date AAAA-MM-JJ --sens long|short
      -> conviction/taille du setup selon le regime (matrice stance x momentum 10Y)
  news      --date AAAA-MM-JJ [--event CPI|PCE|NFP|UNEMP|FED]
      -> plan de trade : attente, drifts 20j/5j/1j, stance, scenarios hot/cool/inline,
         taille, precedents mesures

Seuils de surprise (defaut, modifiables via --seuil) :
  CPI/PCE 0.1 pt, UNEMP 0.1 pt, NFP 30 K, FED 0.1 pt.
"""
import argparse
import csv
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "donnees", "regime", "calendar_macro_2022_2026.csv")
STANCE = os.path.join(BASE, "donnees", "regime", "fed_stance.csv")
PRICING = os.path.join(BASE, "donnees", "regime", "sources", "market_pricing_daily.csv")
INDEX = os.path.join(BASE, "donnees", "regime", "index_daily.csv")
PREDRIFT = os.path.join(BASE, "donnees", "regime", "pre_drift_change.csv")

MAT = {"CPI": 0.2, "PCE": 0.2, "NFP": 20.0, "UNEMP": 0.1, "FED": 0.25}

DEFAULT_VARIANT = {"CPI": "headline_yoy", "PCE": "core_yoy", "NFP": "change_K",
                   "UNEMP": "rate", "FED": "target_upper"}
DEFAULT_SEUIL = {"CPI": 0.1, "PCE": 0.1, "NFP": 30.0, "UNEMP": 0.1, "FED": 0.1}
LABEL = {"CPI": "CPI", "PCE": "PCE", "NFP": "NFP", "UNEMP": "chomage", "FED": "taux Fed"}


def load():
    with open(DATA, newline="", encoding="utf-8") as fh:
        rows = sorted(list(csv.DictReader(fh)), key=lambda r: (r["date_et"], r["variant"]))
    return rows


def num(x):
    try:
        return float(x) if x not in (None, "") else None
    except ValueError:
        return None


def pick(rows, event, variant, date):
    c = [r for r in rows if r["event_type"] == event and r["variant"] == variant
         and r["date_et"].startswith(date)]
    # jour a doubles publications (rattrapage shutdown) : preferer la ligne avec consensus
    c.sort(key=lambda r: (r["forecast"] in (None, ""), r["date_et"]))
    return c[0] if c else None


def fmt(x, unit):
    return f"{x} {unit}" if x not in (None, "") else "n.d."


def cmd_direction(rows, a):
    variant = a.variant or DEFAULT_VARIANT[a.event]
    if a.next:
        c = [r for r in rows if r["event_type"] == a.event and r["variant"] == variant
             and r["status"] == "upcoming"]
        if not c:
            c = [r for r in rows if r["event_type"] == a.event and r["variant"] == variant
                 and r["status"] == "released"][-1:]
        r = c[0] if c else None
        where = "prochain"
    else:
        r = pick(rows, a.event, variant, a.date)
        where = f"du {a.date}"
    if r is None:
        return f"aucune donnee {a.event}/{variant} {where}."
    f, p = num(r["forecast"]), num(r["previous"])
    if f is None or p is None:
        return (f"{LABEL[a.event]} {variant} {where} ({r['date_et']}, ref {r['ref_period']}) : "
                f"pas de consensus (forecast={fmt(r['forecast'], r['unit'])}, "
                f"previous={fmt(r['previous'], r['unit'])}).")
    d = r["direction_attendue"]
    verb = {"hausse": "envisagent une HAUSSE", "baisse": "envisagent une BAISSE",
            "stable": "voient un chiffre STABLE"}.get(d, "?")
    return (f"{LABEL[a.event]} {variant} {where} ({r['date_et']}, ref {r['ref_period']}) : "
            f"les economistes {verb} - previous {p:g} {r['unit']}, "
            f"forecast {f:g} {r['unit']} (ecart attendu {r['ecart_attendu']} {r['unit']}).")


def cmd_surprise(rows, a):
    variant = a.variant or DEFAULT_VARIANT[a.event]
    r = pick(rows, a.event, variant, a.date)
    if r is None:
        return f"aucune donnee {a.event}/{variant} le {a.date}."
    if r["status"] != "released":
        return f"{LABEL[a.event]} {variant} du {a.date} : pas encore publie."
    f, ac = num(r["forecast"]), num(r["actual"])
    if f is None or ac is None:
        return (f"{LABEL[a.event]} {variant} du {a.date} (ref {r['ref_period']}) : "
                f"surprise incalculable (forecast={fmt(r['forecast'], r['unit'])}, "
                f"actual={fmt(r['actual'], r['unit'])}).")
    s = round(ac - f, 6)
    seuil = a.seuil if a.seuil is not None else DEFAULT_SEUIL[a.event]
    flag = ("SURPRISE HAUSSIERE" if s >= seuil else
            "SURPRISE BAISSIERE" if s <= -seuil else "inline (pas de surprise)")
    return (f"{LABEL[a.event]} {variant} du {a.date} (ref {r['ref_period']}) : {flag} - "
            f"forecast {f:g}, actual {ac:g} {r['unit']} "
            f"(surprise {s:+g} {r['unit']}, previous {fmt(r['previous'], r['unit'])}).")


def cmd_trend(rows, a):
    variant = a.variant or DEFAULT_VARIANT[a.event]
    hist = [r for r in rows if r["event_type"] == a.event and r["variant"] == variant
            and r["status"] == "released" and r["actual"] != ""]
    if a.end:
        hist = [r for r in hist if r["date_et"] <= a.end + " 99:99"]
    hist = hist[-a.n:]
    if not hist:
        return f"aucun historique {a.event}/{variant}."
    vals = [num(r["actual"]) for r in hist]
    moves = ["+" if b > c else ("-" if b < c else "=") for b, c in zip(vals[1:], vals[:-1])]
    streak = 0
    for m in reversed(moves):
        if m == (moves[-1] if moves else None):
            streak += 1
        else:
            break
    sens = {"+": "hausse", "-": "baisse"}.get(moves[-1], "stable") if moves else "stable"
    delta = vals[-1] - vals[0]
    lines = [f"{r['date_et'][:10]} (ref {r['ref_period']}): {r['actual']} {r['unit']}" for r in hist]
    return (f"tendance {LABEL[a.event]} {variant} sur {len(hist)} prints "
            f"(fin {hist[-1]['date_et'][:10]}) : {sens} "
            f"(streak {streak}, {vals[0]:g} -> {vals[-1]:g}, delta {delta:+g} {hist[0]['unit']})\n"
            + "\n".join("  " + ln for ln in lines))


def cmd_recap(rows, a):
    day = [r for r in rows if r["date_et"].startswith(a.date) and r["status"] == "released"]
    if not day:
        return f"aucune news le {a.date}."
    out = [f"recap {a.date} :"]
    for r in day:
        f, ac = num(r["forecast"]), num(r["actual"])
        if f is None or ac is None:
            flag = "n.d."
        else:
            s = round(ac - f, 6)
            seuil = DEFAULT_SEUIL[r["event_type"]]
            flag = (f"SURPRISE +{s:g}" if s >= seuil else
                    f"SURPRISE {s:g}" if s <= -seuil else "inline")
        out.append(f"  {r['date_et'][11:]} {r['event_type']}/{r['variant']} (ref {r['ref_period']}): "
                   f"P={fmt(r['previous'], r['unit'])} F={fmt(r['forecast'], r['unit'])} "
                   f"A={fmt(r['actual'], r['unit'])} -> {flag}")
    return "\n".join(out)


def cmd_next(rows, a):
    up = [r for r in rows if r["status"] == "upcoming"]
    if a.event:
        up = [r for r in up if r["event_type"] == a.event]
    if not up:
        return "aucun chiffre attendu (donnees jusqu'a jan 2026 + schedule dispo)."
    out = ["prochains chiffres :"]
    for r in up[:12]:
        out.append(f"  {r['date_et']} {r['event_type']}/{r['variant']}: "
                   f"previous={fmt(r['previous'], r['unit'])}, "
                   f"forecast={fmt(r['forecast'], r['unit'])}")
    return "\n".join(out)


def load_stance():
    with open(STANCE, newline="", encoding="utf-8") as fh:
        return sorted(list(csv.DictReader(fh)), key=lambda r: (r["date_et"], r["variant"]))


def load_pricing():
    with open(PRICING, newline="", encoding="utf-8") as fh:
        return {r["date"]: r for r in csv.DictReader(fh)}


def cmd_stance(srows, a):
    day = [r for r in srows if r["date_et"].startswith(a.date)]
    if not day:
        prev = sorted({r["date_et"][:10] for r in srows if r["date_et"][:10] < a.date})
        if not prev:
            return f"aucune stance avant {a.date}."
        return cmd_stance(srows, argparse.Namespace(date=prev[-1])) + \
            f"\n(note : pas d'event le {a.date}, etat au {prev[-1]})"
    r = next((x for x in day if x["event_type"] == "FED"), day[0])
    evts = ", ".join(sorted({f"{x['event_type']}/{x['variant']}" for x in day}))
    zq = num(r["zq"])
    zq_txt = f"{100 - zq:g} (impl)" if zq is not None else "n.d."
    return (
        f"stance monetaire au {a.date} ({r['date_et'][11:]} apres {evts}) :\n"
        f"  taux : target {r['target_upper']} % (r*={r['r_star']} %, u*={r['u_star']} %, SEP {r['sep_ref']})\n"
        f"  position vs seuils : core PCE {r['pce_core']} % (gap {r['pce_gap']} pt), "
        f"chomage {r['unrate']} % (gap {r['u_gap']} pt)\n"
        f"  regle Taylor : prescription {r['taylor']} % (ecart {r['taylor_gap_bps']} bp)\n"
        f"  stance reelle : {r['stance_label']} (real gap {r['real_gap_bps']} bp, "
        f"infla anticipee SEP {r['pi_exp']} % [{r['pi_exp_src']}])\n"
        f"  dots : mediane fin {r['dot_cy_year']} a {r['dot_cy']} % | "
        f"guidance en vigueur : {r['guidance_stance']} ({r['guidance_date']})\n"
        f"  pricing veille ({r['pricing_date']}) : ZQ {zq_txt}, T-bill 3M {r['irx']}, "
        f"5Y {r['fvx']}, 10Y {r['tnx']}, EFFR {r['effr']}"
    )


def cmd_repricing(srows, rows, a):
    day = [r for r in rows if r["date_et"].startswith(a.date) and r["status"] == "released"]
    if not day:
        return f"aucune news le {a.date}."
    px = load_pricing()
    closes = sorted(px)
    d0 = a.date
    before = next((d for d in reversed(closes) if d < d0), None)
    same = d0 if d0 in px else next((d for d in closes if d > d0), None)
    out = [f"repricing le {a.date} :"]
    for r in sorted(day, key=lambda x: (x["date_et"], x["variant"])):
        f, ac = num(r["forecast"]), num(r["actual"])
        if f is None or ac is None:
            flag = "n.d."
        else:
            s = round(ac - f, 6)
            seuil = DEFAULT_SEUIL[r["event_type"]]
            flag = (f"SURPRISE +{s:g}" if s >= seuil else
                    f"SURPRISE {s:g}" if s <= -seuil else "inline")
        out.append(f"  {r['date_et'][11:]} {r['event_type']}/{r['variant']} (ref {r['ref_period']}): "
                   f"A={fmt(r['actual'], r['unit'])} vs F={fmt(r['forecast'], r['unit'])} -> {flag}")
    if before and same:
        out.append(f"  marche (cloture {same} vs {before}, en bp de taux) :")
        for k, lbl, inv in (("zq", "ZQ Fed funds (implicite)", True), ("irx", "T-bill 3M", False),
                            ("fvx", "5Y", False), ("tnx", "10Y", False)):
            a0, a1 = num(px[before].get(k)), num(px[same].get(k))
            if a0 is not None and a1 is not None:
                if inv:  # ZQ cote 100 - taux : inverser le signe
                    a0, a1 = 100 - a0, 100 - a1
                mv = (a1 - a0) * 100
                out.append(f"    {lbl} : {a0:g} -> {a1:g} ({mv:+.0f} bp)")
    return "\n".join(out)


def load_index():
    idx = {}
    for r in csv.DictReader(open(INDEX, newline="", encoding="utf-8")):
        idx.setdefault(r["inst"], {})[r["date"]] = float(r["rth_close"])
    return idx


def cmd_news(srows, rows, a):
    import regime_filter
    day = [r for r in rows if r["date_et"].startswith(a.date)]
    if a.event:
        day = [r for r in day if r["event_type"] == a.event]
    if not day:
        return f"aucune news le {a.date}" + (f" pour {a.event}." if a.event else ".")
    # config du jour (biais + taille)
    cfg, detail = regime_filter.config_of(a.date)
    out = [cmd_stance(srows, a)]
    if cfg is None:
        out.append(f"config indescriptible : {detail}")
        cfg_txt, ml, ms = "?", None, None
    else:
        ml = regime_filter.LONG[cfg]
        ms = regime_filter.SHORT[cfg]
        cfg_txt = (f"config {cfg} [{regime_filter.WHY[cfg]}] -> "
                   f"long x{ml:g}" + (" VETO" if ml == 0 else "") + f" / short x{ms:g}")
    out.append(cfg_txt)
    # drifts pre-news (ancres veille)
    idx = load_index()
    days = {i: sorted(v) for i, v in idx.items()}
    tnx = {r["date"]: float(r["tnx"]) for r in
           csv.DictReader(open(PRICING, newline="", encoding="utf-8")) if r.get("tnx")}
    tdays = sorted(tnx)

    def snap(series, dmap, J, h, is_bp=False):
        past = [d for d in series if d < J]
        if len(past) <= h:
            return "n.d."
        v, d0 = dmap[past[-1]], dmap[past[-1 - h]]
        return f"{(v - d0) * 100:+.0f}bp" if is_bp else f"{(v / d0 - 1) * 100:+.2f}%"

    # precedents mesures (memes events, surprises hawkish/dovish)
    prec = {}
    if os.path.exists(PREDRIFT):
        for r in csv.DictReader(open(PREDRIFT, newline="", encoding="utf-8")):
            if r["event_type"] == (a.event or r["event_type"]) and r["sens"] in ("hawkish", "dovish"):
                prec.setdefault((r["event_type"], r["sens"]), []).append(r)

    def med(vals):
        vals = sorted(v for v in vals if v is not None)
        if not vals:
            return None
        n = len(vals)
        return vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2

    prec_done = set()
    for r in sorted(day, key=lambda x: (x["date_et"], x["variant"])):
        J = r["date_et"][:10]
        f, p = num(r["forecast"]), num(r["previous"])
        att = f"attente : previous {fmt(r['previous'], r['unit'])} -> forecast {fmt(r['forecast'], r['unit'])}"
        if f is not None and p is not None:
            ec = round(f - p, 4)
            mat = "CHANGEMENT ATTENDU" if abs(ec) >= MAT[r["event_type"]] else "pas de changement attendu (bruit)"
            att += f" (ecart {ec:+g} {r['unit']} -> {mat})"
        else:
            att += " (consensus incomplet)"
        dr = " | ".join(
            f"{lbl} " + "/".join(snap(*args) for args in
                                 ((sorted(days["ES"]), idx["ES"], J, h, False),
                                  (tdays, tnx, J, h, True)))
            for lbl, h in (("20j", 20), ("5j", 5), ("1j", 1)))
        out.append(f"\n{r['date_et'][11:]} {r['event_type']}/{r['variant']} (ref {r['ref_period']}) : {att}")
        out.append(f"  drift pre-news [ES% / 10Ybp] : {dr}  (veille={max([d for d in days['ES'] if d < J], default='?')})")
        # scenarios (sens marche : hawkish = hot, sauf UNEMP inverse)
        hot = "actual < forecast (chomage bas = hawkish)" if r["event_type"] == "UNEMP" \
            else "actual > forecast (hawkish)"
        cool = "actual > forecast (dovish)" if r["event_type"] == "UNEMP" \
            else "actual < forecast (dovish)"
        if ml is None:
            out.append(f"  si HOT ({hot}) / COOL ({cool}) : taille inconnue (config indescriptible).")
        else:
            out.append(f"  si HOT ({hot}) : short x{ms:g}" + (
                " (pleine taille, laisser courir - extension du reversal)" if ms >= 1 else
                " (taille reduite, objectifs courts, trailing serre - la stance encaisse)" if ms >= 0.5 else
                " (fade documente uniquement, contre le biais)"))
            out.append(f"  si COOL ({cool}) : long x{ml:g}" + (
                " (pleine taille, avec la tendance de fond)" if ml >= 1 else
                " (agressif modere, trailing large - relief maximal surtout 10Y haut)" if ml >= 0.5 else
                " (VETO long : pas de long meme dovish)" if ml == 0 else
                " (petite taille, prendre vite)"))
        out.append("  si INLINE : suivre le biais du regime (filtre ci-dessus).")
        for sens in ("hawkish", "dovish"):
            if r["event_type"] in prec_done:
                continue
            pp = prec.get((r["event_type"], sens), [])
            es = [num(x["jday_es"]) for x in pp]
            tn = [num(x["jday_tnx"]) for x in pp]
            me, mt = med(es), med(tn)
            out.append(f"  precedents {sens} {r['event_type']} (N={len(pp)}) : " + (
                f"ES J med {me:+.2f}%, 10Y {mt:+.0f}bp" if me is not None else "insuffisants"))
        prec_done.add(r["event_type"])
        if r["status"] == "released" and num(r["actual"]) is not None and f is not None:
            s = round(num(r["actual"]) - f, 6)
            flag = "HAUSSIERE" if (s >= DEFAULT_SEUIL[r["event_type"]] if r["event_type"] != "UNEMP"
                                   else s <= -DEFAULT_SEUIL[r["event_type"]]) else (
                "BAISSIERE" if (s <= -DEFAULT_SEUIL[r["event_type"]] if r["event_type"] != "UNEMP"
                                else s >= DEFAULT_SEUIL[r["event_type"]]) else "inline")
            out.append(f"  realise : actual {r['actual']} {r['unit']} -> surprise {flag} ({s:+g}).")
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(description="Regime macro : direction, surprise, tendance.")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("direction", "surprise", "trend"):
        s = sub.add_parser(name)
        s.add_argument("--event", required=True, choices=sorted(DEFAULT_VARIANT))
        s.add_argument("--variant", default=None)
        if name in ("direction", "surprise"):
            s.add_argument("--date", default=None)
        if name == "direction":
            s.add_argument("--next", action="store_true")
        if name == "surprise":
            s.add_argument("--seuil", type=float, default=None)
        if name == "trend":
            s.add_argument("--n", type=int, default=6)
            s.add_argument("--end", default=None)
    r = sub.add_parser("recap")
    r.add_argument("--date", required=True)
    n = sub.add_parser("next")
    n.add_argument("--event", default=None, choices=sorted(DEFAULT_VARIANT))
    for name in ("stance", "repricing"):
        s = sub.add_parser(name)
        s.add_argument("--date", required=True)
    f = sub.add_parser("filtre")
    f.add_argument("--date", required=True)
    f.add_argument("--sens", required=True, choices=("long", "short"))
    w = sub.add_parser("news")
    w.add_argument("--date", required=True)
    w.add_argument("--event", default=None, choices=sorted(DEFAULT_VARIANT))
    a = p.parse_args(argv)
    rows = load()
    if a.cmd == "direction" and not a.next and not a.date:
        p.error("direction exige --date ou --next")
    if a.cmd == "surprise" and not a.date:
        p.error("surprise exige --date")
    if a.cmd == "news":
        srows = load_stance()
        print(cmd_news(srows, rows, a))
        return
    if a.cmd == "filtre":
        import regime_filter
        print(regime_filter.filtre(a.date, a.sens))
        return
    if a.cmd in ("stance", "repricing"):
        srows = load_stance()
        if a.cmd == "stance":
            print(cmd_stance(srows, a))
        else:
            print(cmd_repricing(srows, rows, a))
        return
    fn = {"direction": cmd_direction, "surprise": cmd_surprise, "trend": cmd_trend,
          "recap": cmd_recap, "next": cmd_next}[a.cmd]
    print(fn(rows, a))


if __name__ == "__main__":
    main()
