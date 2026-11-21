"""Generate contrib-heatmap.svg from a GitHub user's contribution calendar.

Usage:  GITHUB_TOKEN=... python scripts/generate_heatmap.py Amineimmo
        python scripts/generate_heatmap.py --demo      # fake data, for previewing
"""
import json, os, random, sys, urllib.request
from datetime import date, timedelta

QUERY = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
COLORS = ["#121826", "#4a2f0e", "#8f5412", "#e08a17", "#ffc15e"]  # empty -> busiest
CELL, GAP, X0, Y0 = 13, 3.5, 44, 70


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], [[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]]


def demo():
    random.seed(7)
    weeks = [[random.choice([0, 0, 0, 1, 2, 4, 7]) for _ in range(7)] for _ in range(53)]
    return sum(map(sum, weeks)), weeks


def level(n, top):
    if n == 0:
        return 0
    return min(4, 1 + int(3 * (n - 1) / max(top - 1, 1)))


def render(total, weeks):
    top = max(max(w) for w in weeks) or 1
    width = 960
    height = Y0 + 7 * (CELL + GAP) + 34
    cells = []
    for x, w in enumerate(weeks):
        for y, n in enumerate(w):
            lv = level(n, top)
            extra = f' class="c" style="animation-delay:{x * 0.07:.2f}s"' if lv else ""
            cells.append(
                f'<rect{extra} x="{X0 + x * (CELL + GAP)}" y="{Y0 + y * (CELL + GAP)}" width="{CELL}" height="{CELL}" '
                f'rx="3" fill="{COLORS[lv]}"/>'
            )
    lx = width - X0 - 34 - 5 * (CELL + 3)
    legend = "".join(
        f'<rect x="{lx + i * (CELL + 3)}" y="{height - 26}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>'
        for i, c in enumerate(COLORS)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="t">
<title id="t">{total} contributions in the last year</title>
<style>.m{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.c{{animation:wave 7s ease-in-out infinite}}
@keyframes wave{{0%,30%,100%{{opacity:.7}}13%{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<rect width="{width}" height="{height}" rx="14" fill="#080b12"/>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="13.5" fill="none" stroke="#1b2333"/>
<text x="{X0}" y="40" class="m" font-size="15" font-weight="700" fill="#ffb347">{total} contributions</text>
<text x="{X0 + 190}" y="40" class="m" font-size="13" fill="#6b7585">in the last year</text>
{chr(10).join(cells)}
<text x="{lx - 8}" y="{height - 15}" class="m" font-size="11" fill="#6b7585" text-anchor="end">less</text>
{legend}
<text x="{lx + 5 * (CELL + 3) + 2}" y="{height - 15}" class="m" font-size="11" fill="#6b7585">more</text>
</svg>
'''


if __name__ == "__main__":
    if "--demo" in sys.argv:
        total, weeks = demo()
    else:
        total, weeks = fetch(sys.argv[1], os.environ["GITHUB_TOKEN"])
    out = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")
    open(out, "w", encoding="utf-8").write(render(total, weeks))
    print(f"wrote {os.path.normpath(out)} ({total} contributions)")
