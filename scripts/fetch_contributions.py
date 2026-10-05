"""Scrape the public contribution calendar (no token needed) -> data/contributions.json"""
import json, os, re, sys
from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GITHUB_USER") or (sys.argv[1] if len(sys.argv) > 1 else "Amineimmo")
URL = f"https://github.com/users/{USER}/contributions"

def fetch_days():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 profile-readme-bot"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tips = {}
    for t in soup.find_all("tool-tip"):
        m = re.match(r"\s*(No|\d[\d,]*) contribution", t.get_text())
        if m:
            tips[t.get("for")] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))
    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        days.append({"date": d, "level": int(td.get("data-level", 0)), "count": tips.get(td.get("id"), 0)})
    days.sort(key=lambda x: x["date"])
    return days

def stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    # current streak: today may still be empty, so allow starting from yesterday
    cur, i = 0, len(days) - 1
    if i >= 0 and days[i]["count"] == 0:
        i -= 1
    while i >= 0 and days[i]["count"] > 0:
        cur += 1
        i -= 1
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
    return {"total": total, "current_streak": cur, "longest_streak": longest,
            "best_day": best, "months": months}

if __name__ == "__main__":
    days = fetch_days()
    if not days:
        sys.exit("No days parsed - GitHub HTML may have changed")
    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w") as f:
        json.dump({"user": USER, "days": days, "stats": stats(days)}, f, indent=1)
    print(f"{USER}: {len(days)} days, {stats(days)['total']} contributions")
