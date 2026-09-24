"""Telecharge les 33 statements FOMC jan 2022 -> jan 2026 depuis federalreserve.gov.

URL : https://www.federalreserve.gov/newsevents/pressreleases/monetaryYYYYMMDDa.htm
Sorties :
  donnees/regime/sources/fomc_statements/YYYYMMDD_statement.htm (brut)
  donnees/regime/sources/fomc_statements/YYYYMMDD.txt (texte brut)
  donnees/regime/sources/fomc_statements/index.csv (date, date_et, url, decision_bps)

Les dates/decisions viennent de donnees/regime/calendar_macro_2022_2026.csv (FED released).
"""
import csv
import os
import re
import time
import urllib.request
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
OUT = os.path.join(REGIME, "sources", "fomc_statements")
CAL = os.path.join(REGIME, "calendar_macro_2022_2026.csv")


class TextPull(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "header", "footer"):
            self.skip += 1
        elif tag in ("p", "br", "h1", "h2", "li", "tr"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "header", "footer") and self.skip:
            self.skip -= 1
        elif tag in ("p", "h1", "h2", "li", "tr"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_text(raw):
    p = TextPull()
    p.feed(raw)
    txt = "".join(p.parts)
    txt = re.sub(r"\n\s*\n+", "\n\n", txt)
    return txt.strip()


def fetch(url, tries=6):
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  essai {a + 1} echec: {type(e).__name__}")
            time.sleep(4 * (a + 1))
    raise RuntimeError(f"echec {url}: {last}")


def fed_meetings():
    rows = []
    with open(CAL, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["event_type"] == "FED" and r["variant"] == "target_upper" and r["status"] == "released":
                rows.append(r)
    return sorted(rows, key=lambda r: r["date_et"])


def main():
    os.makedirs(OUT, exist_ok=True)
    meetings = fed_meetings()
    print(f"{len(meetings)} meetings FED")
    index = []
    for m in meetings:
        day = m["date_et"][:10].replace("-", "")
        url = f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{day}a.htm"
        dest = os.path.join(OUT, f"{day}_statement.htm")
        txtd = os.path.join(OUT, f"{day}.txt")
        prev, act = (float(m["previous"]) if m["previous"] else None,
                     float(m["actual"]) if m["actual"] else None)
        dec = "" if (prev is None or act is None) else f"{(act - prev) * 100:+.0f}bp"
        if os.path.exists(txtd) and os.path.getsize(txtd) > 2000:
            print(f"{day}: deja la")
        else:
            print(f"{day}: {url} [{m['date_et']}, decision {dec}]")
            data = fetch(url)
            with open(dest, "wb") as fh:
                fh.write(data)
            txt = html_to_text(data.decode("utf-8", errors="replace"))
            with open(txtd, "w", encoding="utf-8") as fh:
                fh.write(txt)
            print(f"  -> {len(data)} o brut, {len(txt)} car texte")
            time.sleep(2)
        index.append({"day": day, "date_et": m["date_et"], "url": url, "decision": dec})
    with open(os.path.join(OUT, "index.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["day", "date_et", "url", "decision"])
        w.writeheader()
        w.writerows(index)
    print("OK")


if __name__ == "__main__":
    main()
