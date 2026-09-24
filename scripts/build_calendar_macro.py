"""Construit donnees/regime/calendar_macro_2022_2026.csv depuis les snapshots vendored.

Entrees :
  donnees/regime/sources/fred-us-macro-history.json       (niveaux FRED : YoY/levels)
  donnees/regime/sources/investing-us-macro-consensus.json (previous/forecast/actual)
  donnees/regime/sources/bls_cpi_sa_2021_2026.json         (index CPI SA headline+core)
  donnees/regime/calendar_cpi_2025.csv                     (forecast MoM CPI headline 2025)

Sortie :
  donnees/regime/calendar_macro_2022_2026.csv
  colonnes : date_et,event_type,variant,ref_period,status,previous,forecast,
             actual,surprise,ecart_attendu,direction_attendue,unit,
             source_forecast,source_actual,note

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/build_calendar_macro.py

Regles :
  - fenetre released : 2022-01-01 -> 2026-01-31 (l'upcoming posterieur est conserve,
    actual vide, pour les requetes "prochain chiffre").
  - forecast manquant = vide (jamais 0) ; actual snapshot fait foi.
  - ref_period par regle de decalage publication (CPI/NFP/UNEMP: M-1 ; PCE: M-1 si
    jour>=25 sinon M-2 ; FED: mois du meeting), verifiee par valeur FRED.
  - CPI MoM = SA via BLS (pas de NSA) ; PCE MoM = SA via BEA/FRED.
  - dedup des occurrences multiples le meme jour (ex: PCE 2026-01-22 double).
Details : donnees/regime/sources/SOURCES.md
"""
import csv
import json
import os
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "donnees", "regime", "sources")
OUT = os.path.join(BASE, "donnees", "regime", "calendar_macro_2022_2026.csv")
CAL_CPI_MOM = os.path.join(BASE, "donnees", "regime", "calendar_cpi_2025.csv")

WIN_START = "2022-01-01T00:00:00Z"
SCOPE_END_ET = "2026-01-31 23:59"  # released au-dela = hors scope (garde : upcoming)

# seriesId -> (event_type, variant, unit)
SERIES = {
    "CPIAUCNS": ("CPI", "headline_yoy", "%"),
    "CPILFENS": ("CPI", "core_yoy", "%"),
    "PCEPI": ("PCE", "headline_yoy", "%"),
    "PCEPILFE": ("PCE", "core_yoy", "%"),
    "PAYEMS": ("NFP", "change_K", "K"),
    "UNRATE": ("UNEMP", "rate", "%"),
    "DFEDTARU": ("FED", "target_upper", "%"),
}
YOY_SERIES = {"CPIAUCNS", "CPILFENS", "PCEPI", "PCEPILFE"}
SRC_CONS = "Investing.com (snapshot)"
SRC_FRED = "FRED/Investing (open-data match)"
TOL = {"%": 0.25, "K": 25.0}  # verification ref par valeur (history revisee)


# ---------- heures : UTC -> America/New_York (DST US) ----------
def _nth_weekday(year, month, weekday, n):
    from datetime import date
    if n > 0:
        d = date(year, month, 1)
        return d + timedelta(days=(weekday - d.weekday()) % 7 + (n - 1) * 7)
    d = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)
    return (d - timedelta(days=1)) - timedelta(days=((d - timedelta(days=1)).weekday() - weekday) % 7)


def utc_to_et(iso_z):
    dt = datetime.strptime(iso_z, "%Y-%m-%dT%H:%M:%SZ")
    dst_start = datetime.combine(_nth_weekday(dt.year, 3, 6, 2), datetime.min.time()) + timedelta(hours=2)
    dst_end = datetime.combine(_nth_weekday(dt.year, 11, 6, 1), datetime.min.time()) + timedelta(hours=2)
    return dt - timedelta(hours=4 if dst_start <= dt < dst_end else 5)


# ---------- helpers ----------
def rnd(x, unit):
    if x is None:
        return ""
    return f"{round(x, 1 if unit == 'K' else 2):g}"


def direction(ecart):
    if ecart is None or ecart == "":
        return "inconnue"
    v = float(ecart)
    return "hausse" if v > 0 else ("baisse" if v < 0 else "stable")


def sub_months(ym, n):
    y, m = int(ym[:4]), int(ym[5:7])
    m -= n
    while m < 1:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}"


# ---------- chargement ----------
def load_history():
    with open(os.path.join(SRC, "fred-us-macro-history.json"), encoding="utf-8") as fh:
        raw = json.load(fh)
    hist = {}
    for s in raw["series"]:
        obs = sorted(((o["date"], o["value"]) for o in s["observations"]
                      if o["value"] is not None), key=lambda t: t[0])
        hist[s["id"]] = {"obs": obs, "by_date": {d: v for d, v in obs}}
    return hist


def load_consensus():
    with open(os.path.join(SRC, "investing-us-macro-consensus.json"), encoding="utf-8") as fh:
        raw = json.load(fh)
    return {s["seriesId"]: [o for o in s["occurrences"] if o["occurrenceTime"] >= WIN_START]
            for s in raw["series"]}


def load_cpi_mom_calendar():
    """Rend les lignes MoM temps reel du calendrier CPI 2025 existant.

    previous = chaine avec le print precedent du meme calendrier
    (vide pour la 1ere ligne : pas de fabrication du print hors calendrier).
    """
    rows = []
    if not os.path.exists(CAL_CPI_MOM):
        return rows
    with open(CAL_CPI_MOM, newline="", encoding="utf-8") as fh:
        cal = sorted(list(csv.DictReader(fh)), key=lambda r: r["date_et"])
    prev_actual = ""
    for row in cal:
        try:
            fc, ac = float(row["consensus_mom"]), float(row["actual_mom"])
        except (ValueError, KeyError):
            continue
        surprise = ac - fc
        ecart = fc - float(prev_actual) if prev_actual != "" else None
        rows.append({
            "date_et": row["date_et"], "event_type": "CPI", "variant": "headline_mom",
            "ref_period": row.get("ref_month", ""), "status": "released",
            "previous": prev_actual, "forecast": f"{fc:g}", "actual": f"{ac:g}",
            "surprise": rnd(surprise, "%"),
            "ecart_attendu": rnd(ecart, "%"),
            "direction_attendue": direction(rnd(ecart, "%")),
            "unit": "%", "source_forecast": f"calendar_cpi_2025.csv ({row.get('consensus_source', '')})",
            "source_actual": f"BLS temps reel ({row.get('actual_source', '')})",
            "note": "",
        })
        prev_actual = f"{ac:g}"
    return rows


# ---------- valeur marche attendue au ref (verification) ----------
def expected_at_ref(sid, hist, ref_ym, rel_day):
    by_date = hist[sid]["by_date"]
    if sid in YOY_SERIES:
        a, b = by_date.get(ref_ym + "-01"), by_date.get(sub_months(ref_ym, 12) + "-01")
        return (a / b - 1.0) * 100.0 if (a and b) else None
    if sid == "PAYEMS":
        a, b = by_date.get(ref_ym + "-01"), by_date.get(sub_months(ref_ym, 1) + "-01")
        return (a - b) if (a is not None and b is not None) else None
    if sid == "UNRATE":
        return by_date.get(ref_ym + "-01")
    if sid == "DFEDTARU":  # serie quotidienne : valeur veille du meeting
        ds = [d for d, _ in hist[sid]["obs"] if d <= rel_day]
        return by_date[ds[-1]] if ds else None
    return None


# Mois de reference du snapshot (noms chinois) -> 'MM'. DFEDTARU = '' (pas de ref).
ZH_MONTH = {"一月": "01", "二月": "02", "三月": "03", "四月": "04", "五月": "05",
            "六月": "06", "七月": "07", "八月": "08", "九月": "09", "十月": "10",
            "十一月": "11", "十二月": "12"}


def ref_rule(sid, et):
    """Repli si referencePeriod absent : M-1 (FED : mois du meeting)."""
    ym = et[:7]
    if sid == "DFEDTARU":
        return ym
    return sub_months(ym, 1)


def ref_from_occ(sid, occ, et):
    """(ref_ym, note). Source : referencePeriod du snapshot ; repli = regle de decalage."""
    if sid == "DFEDTARU":
        return et[:7], ""
    zh = (occ.get("referencePeriod") or "").strip()
    mm = ZH_MONTH.get(zh)
    if mm is None:
        return ref_rule(sid, et), "ref_regle_sans_referencePeriod"
    rel_y, rel_m = int(et[:4]), int(et[5:7])
    ref_y = rel_y if int(mm) <= rel_m else rel_y - 1
    # garde-fous : CPI/NFP/UNEMP = M-1 strict ; PCE = M-1 ou M-2
    if sid in ("CPIAUCNS", "CPILFENS", "PAYEMS", "UNRATE"):
        exp = sub_months(et[:7], 1)
        got = f"{ref_y:04d}-{mm}"
        if got != exp:
            return got, f"ref_inattendue(attendu_{exp})"
        return got, ""
    if sid in ("PCEPI", "PCEPILFE"):
        got = f"{ref_y:04d}-{mm}"
        if got not in (sub_months(et[:7], 1), sub_months(et[:7], 2), sub_months(et[:7], 3)):
            return got, "ref_pce_eloignee_a_verifier"
        return got, ""
    return f"{ref_y:04d}-{mm}", ""


def dedupe(occ_list):
    """Regroupe par (jour ET, referencePeriod) : deux releases le meme jour avec
    des refs differentes (ex: rattrapage PCE oct+nov 2025 le 2026-01-22) sont
    conservees. Ne fusionne que les vrais doublons, en gardant l'occurrence
    avec forecast, sinon actual, sinon la 1ere."""
    groups = {}
    for o in occ_list:
        key = (utc_to_et(o["occurrenceTime"]).strftime("%Y-%m-%d"),
               (o.get("referencePeriod") or "").strip())
        groups.setdefault(key, []).append(o)
    out = []
    for day, grp in sorted(groups.items()):
        if len(grp) == 1:
            out.append((grp[0], ""))
            continue
        grp.sort(key=lambda o: (o.get("forecast") is None, o.get("actual") is None,
                                o["occurrenceTime"]))
        best = grp[0]
        vals = {(g.get("forecast"), g.get("actual"), g.get("previous")) for g in grp}
        note = "" if len(vals) == 1 else "occurrences_multiples_valeurs_divergentes"
        out.append((best, note))
    return out


def main():
    hist = load_history()
    cons = load_consensus()
    rows = []
    n_dedup = 0

    for sid, (ev, variant, unit) in SERIES.items():
        for occ, dup_note in dedupe(cons.get(sid, [])):
            et = utc_to_et(occ["occurrenceTime"]).strftime("%Y-%m-%d %H:%M")
            prev, fc, ac = occ.get("previous"), occ.get("forecast"), occ.get("actual")
            status = "released" if ac is not None else "upcoming"
            if status == "released" and et > SCOPE_END_ET:
                continue  # hors scope demande (jan 2022 -> jan 2026)
            note = dup_note
            if dup_note:
                n_dedup += 1
            if ac is None:
                # upcoming : ref connue seulement pour FED (mois du meeting schedule)
                ref = et[:7] if sid == "DFEDTARU" else ""
                note = (note + ";" if note else "") + "upcoming_sans_actual"
            else:
                ref, ref_note = ref_from_occ(sid, occ, et)
                if ref_note:
                    note = (note + ";" if note else "") + ref_note
                # Verification : series stables (CPI NSA, UNRATE) par valeur ;
                # FED : valeur veille == previous.
                # (PCE/NFP : historique revise, pas de controle par valeur.)
                if sid in ("CPIAUCNS", "CPILFENS", "UNRATE") and "ref_inattendue" not in ref_note:
                    exp = expected_at_ref(sid, hist, ref, occ["occurrenceTime"][:10])
                    if exp is not None and abs(exp - ac) > TOL[unit]:
                        note = (note + ";" if note else "") + f"ref_a_verifier(exp={exp:.2f})"
                elif sid == "DFEDTARU" and prev is not None:
                    pre = expected_at_ref(sid, hist, ref, occ["occurrenceTime"][:10])
                    if pre is not None and abs(pre - prev) > 0.01:
                        note = (note + ";" if note else "") + f"veille_vs_previous(pre={pre})"
            if occ.get("previousRevisedFrom") not in (None, ""):
                note = (note + ";" if note else "") + f"prev_rev_from={occ['previousRevisedFrom']}"
            surprise = (ac - fc) if (ac is not None and fc is not None) else None
            ecart = (fc - prev) if (fc is not None and prev is not None) else None
            rows.append({
                "date_et": et, "event_type": ev, "variant": variant,
                "ref_period": ref, "status": status,
                "previous": "" if prev is None else f"{prev:g}",
                "forecast": "" if fc is None else f"{fc:g}",
                "actual": "" if ac is None else f"{ac:g}",
                "surprise": rnd(surprise, unit),
                "ecart_attendu": rnd(ecart, unit),
                "direction_attendue": direction(rnd(ecart, unit)),
                "unit": unit, "source_forecast": SRC_CONS, "source_actual": SRC_FRED,
                "note": note,
            })

    # ---- couche MoM temps reel : calendrier CPI 2025 existant uniquement ----
    # (aucun MoM recalcule : les series SA/BEA revisees ne reproduisent pas les
    # prints temps reel, cf. SOURCES.md)
    rows.extend(load_cpi_mom_calendar())

    rows.sort(key=lambda r: (r["date_et"], r["event_type"], r["variant"]))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["date_et", "event_type", "variant", "ref_period",
                                           "status", "previous", "forecast", "actual",
                                           "surprise", "ecart_attendu", "direction_attendue",
                                           "unit", "source_forecast", "source_actual", "note"])
        w.writeheader()
        w.writerows(rows)

    # ---- rapport ----
    from collections import Counter
    print(f"ecrit {OUT} : {len(rows)} lignes (dedup fusions: {n_dedup})")
    print(Counter((r["event_type"], r["variant"], r["status"]) for r in rows))
    print("released sans forecast :",
          sum(1 for r in rows if r["status"] == "released" and not r["forecast"]))
    for r in rows:
        if r["status"] == "released" and not r["forecast"] and r["variant"].endswith(("_yoy", "_K", "rate", "upper")):
            print("  ", r["date_et"], r["event_type"], r["variant"], "ref=" + r["ref_period"])
    verify = [r for r in rows if "ref_a_verifier" in r["note"] or "veille_vs_previous" in r["note"]]
    print(f"flags verification : {len(verify)}")
    for r in verify[:20]:
        print("  ", r["date_et"], r["event_type"], r["variant"], r["ref_period"],
              f"A={r['actual']}", r["note"])

    mom_rows = sorted([x for x in rows if x["variant"] == "headline_mom"],
                      key=lambda x: x["date_et"])
    print(f"CPI MoM temps reel integres : {len(mom_rows)} (attendu 10)")
    for r in mom_rows:
        print(f"  {r['date_et']} ref={r['ref_period']} P={r['previous']} F={r['forecast']} "
              f"A={r['actual']} surprise={r['surprise']} dir={r['direction_attendue']}")

    print("couverture ref_period (released YoY/levels) :")
    for ev in ("CPI", "PCE", "NFP", "UNEMP", "FED"):
        refs = sorted({r["ref_period"] for r in rows
                       if r["event_type"] == ev and r["status"] == "released"
                       and r["ref_period"] and not r["variant"].endswith("_mom")})
        print(f"  {ev}: {len(refs)} refs, {refs[0] if refs else '?'} -> {refs[-1] if refs else '?'}")


if __name__ == "__main__":
    main()
