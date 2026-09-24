"""Codage (draft) du forward guidance des 33 statements FOMC 2022-2026.

Methode : extraction du corps (paragraphes <p> entre le debut et "Voting for"),
citation des phrases de guidance, score par grille de marqueurs + action.
TOUT est statut draft_a_valider : la validation humaine ligne par ligne est
obligatoire avant usage (citation source fournie pour chaque ligne).

Grille (marqueur -> poids ; compte une fois par statement) :
  hawkish : ongoing increases +2 | additional policy firming +2 | further firming +2
            highly attentive to inflation risks +1 | cumulative tightening +1
            lags with which monetary policy +1 | prepared to tighten +2
  dovish  : reduce the target range +2 | gained greater confidence +2
            extent and timing of additional adjustments +1 | roughly in balance +1
            patient +1 | prepared to ease +2 | slow the pace +1
  action  : hike +2 | cut -2 | hold 0
  stance  : score >= 2 hawkish | <= -2 dovish | sinon neutral

Sorties :
  donnees/regime/fomc_guidance.csv (date_et,decision_bps,action,stance_draft,score,
      score_detail,quote,dissents,source_url,statut)
  donnees/regime/sources/fomc_statements/YYYYMMDD_body.txt (corps nettoye, relecture)

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/code_guidance.py
"""
import csv
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
STMT = os.path.join(REGIME, "sources", "fomc_statements")
OUT = os.path.join(REGIME, "fomc_guidance.csv")
CAL = os.path.join(REGIME, "calendar_macro_2022_2026.csv")

HAWKISH = {"ongoing increases": 2, "additional policy firming": 2, "further firming": 2,
           "highly attentive to inflation risks": 1, "cumulative tightening": 1,
           "lags with which monetary policy": 1, "prepared to tighten": 2}
DOVISH = {"reduce the target range": 2, "gained greater confidence": 2,
          "extent and timing of additional adjustments": 1, "roughly in balance": 1,
          "patient": 1, "prepared to ease": 2, "slow the pace": 1,
          "additional accommodation": 2}
QUOTE_HITS = ["anticipates", "ongoing increases", "policy firming", "additional adjustments",
              "will continue to monitor", "prepared to adjust", "firming", "highly attentive",
              "greater confidence", "extent and timing", "patient", "slow the pace"]


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("\u2011", "-").replace("\u2013", "-").replace("\u2019", "'")
    return re.sub(r"\s+", " ", s).strip()


def extract(day):
    h = open(os.path.join(STMT, f"{day}_statement.htm"), encoding="utf-8", errors="replace").read()
    paras = [clean(p) for p in re.findall(r"<p>(.*?)</p>", h, re.S)]
    paras = [p for p in paras if len(p) > 80 and "media inquiries" not in p
             and "email-protection" not in p]
    body, votes = [], []
    in_votes = False
    for p in paras:
        if "Voting for the monetary policy action" in p:
            in_votes = True
        (votes if in_votes else body).append(p)
    return body, votes


def sentences(body):
    out = []
    for p in body:
        out.extend([s.strip() for s in re.split(r"\.\s+", p) if len(s.strip()) > 40])
    return out


def main():
    cal = {}
    with open(CAL, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["event_type"] == "FED" and r["variant"] == "target_upper" and r["status"] == "released":
                prev = float(r["previous"]) if r["previous"] else None
                act = float(r["actual"]) if r["actual"] else None
                dec = None if (prev is None or act is None) else round((act - prev) * 100)
                cal[r["date_et"][:10].replace("-", "")] = (r["date_et"], dec)
    rows = []
    for day in sorted(cal):
        date_et, dec = cal[day]
        url = f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{day}a.htm"
        body, votes = extract(day)
        with open(os.path.join(STMT, f"{day}_body.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n\n".join(body) + "\n\n--- VOTES ---\n" + "\n\n".join(votes) + "\n")
        low = " ".join(body).lower()
        hits = []
        for k, w in HAWKISH.items():
            if k in low:
                hits.append(f"H[{k}]+{w}")
        for k, w in DOVISH.items():
            if k in low:
                hits.append(f"D[{k}]{w:+d}")
        score = sum(HAWKISH[k] for k in HAWKISH if k in low) \
            - sum(-DOVISH[k] for k in DOVISH if k in low)
        action = "hold" if dec == 0 else ("hike" if dec and dec > 0 else ("cut" if dec else "?"))
        score += {"hike": 2, "cut": -2}.get(action, 0)
        hits.append(f"action[{action}]{ {'hike': '+2', 'cut': '-2'}.get(action, '+0')}")
        stance = "hawkish" if score >= 2 else ("dovish" if score <= -2 else "neutral")
        cited = [s.rstrip(".") + "." for s in sentences(body)
                 if any(q in s.lower() for q in QUOTE_HITS)][:2]
        quote = " ".join(cited)
        diss = "unanime"
        for v in votes:
            m = re.search(r"Voting against.*", v)
            if m:
                d = m.group(0).strip()
                diss = d if len(d) <= 320 else d[:320].rsplit(" ", 1)[0] + "…"
        rows.append({"date_et": date_et, "decision_bps": "" if dec is None else f"{dec:+.0f}",
                     "action": action, "stance_draft": stance, "score": score,
                     "score_detail": "; ".join(hits), "quote": quote, "dissents": diss,
                     "source_url": url, "statut": "draft_a_valider"})
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["date_et", "decision_bps", "action", "stance_draft",
                                           "score", "score_detail", "quote", "dissents",
                                           "source_url", "statut"])
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(f"ecrit {OUT} : {len(rows)} lignes {Counter(r['stance_draft'] for r in rows)}")
    for r in rows:
        print(f"  {r['date_et'][:10]} {r['action']:4s} {r['stance_draft']:8s} (score {r['score']:+d})")


if __name__ == "__main__":
    main()
