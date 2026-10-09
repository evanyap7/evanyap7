"""Scrape the public contributions page (no token needed) -> data/contributions.json."""
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER = sys.argv[1] if len(sys.argv) > 1 else "evanyap7"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

URL = f"https://github.com/users/{USER}/contributions"


def fetch_cells(attempts=5):
    """GET the page, retrying on throttling / error pages until contribution cells show up."""
    for i in range(1, attempts + 1):
        try:
            r = requests.get(
                URL,
                headers={"User-Agent": "Mozilla/5.0 (compatible; profile-readme-refresh)"},
                timeout=30,
            )
            soup = BeautifulSoup(r.text, "html.parser")
            if r.ok and soup.select("td.ContributionCalendar-day"):
                return soup
            print(f"attempt {i}: HTTP {r.status_code}, no cells; body starts: {r.text[:200]!r}")
        except requests.RequestException as e:
            print(f"attempt {i}: {e}")
        if i < attempts:
            time.sleep(10 * i)
    sys.exit(f"no contribution cells after {attempts} attempts; see log above")


soup = fetch_cells()

# tooltips carry the exact counts: "3 contributions on October 7th." / "No contributions on ..."
counts = {}
for tip in soup.find_all("tool-tip"):
    m = re.match(r"(\d+|No) contributions? on", tip.get_text(strip=True))
    if m:
        counts[tip.get("for")] = 0 if m.group(1) == "No" else int(m.group(1))

days = []
for td in soup.select("td.ContributionCalendar-day"):
    date = td.get("data-date")
    if not date:
        continue
    days.append(
        {"date": date, "level": int(td.get("data-level", 0)), "count": counts.get(td.get("id"), 0)}
    )
days.sort(key=lambda d: d["date"])
if not days:
    sys.exit("no contribution cells found; GitHub markup may have changed")

today = dt.date.today().isoformat()
active = [d["level"] > 0 or d["count"] > 0 for d in days if d["date"] <= today]

longest = run = 0
for a in active:
    run = run + 1 if a else 0
    longest = max(longest, run)

if active and not active[-1]:  # today may simply not have a contribution yet
    active = active[:-1]
current = 0
for a in reversed(active):
    if not a:
        break
    current += 1

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(
    json.dumps(
        {
            "username": USER,
            "generated": today,
            "total": sum(d["count"] for d in days),
            "current_streak": current,
            "longest_streak": longest,
            "days": days,
        },
        indent=1,
    )
)
print(f"wrote {OUT}: {len(days)} days, {sum(d['count'] for d in days)} contributions")
