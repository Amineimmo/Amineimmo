"""data/contributions.json -> contrib-heatmap.svg (animated 53-week calendar, dark terminal panel)"""
import json
from datetime import date, datetime

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, FG, MUTED = "#0d1117", "#e6edf3", "#7d8590"
W, CELL, GAP, LEFT, TOP = 860, 12, 3, 40, 56
PITCH = CELL + GAP
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

data = json.load(open("data/contributions.json"))
days, st = data["days"], data["stats"]
for d in days:
    d["dt"] = datetime.strptime(d["date"], "%Y-%m-%d").date()

first = days[0]["dt"]
first_sunday = first.toordinal() - ((first.weekday() + 1) % 7)
def pos(dt):
    row = (dt.weekday() + 1) % 7              # Sunday = 0
    col = (dt.toordinal() - first_sunday) // 7
    return col, row

cols = max(pos(d["dt"])[0] for d in days) + 1
mx = max((d["count"] for d in days), default=0)
H = TOP + 7 * PITCH + 62

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="GitHub contribution heatmap: {st["total"]} contributions in the last year">',
       "<style>",
       "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}",
       ".c{animation:pop .45s ease-out backwards}",
       "@keyframes pop{from{opacity:0;transform:translateY(-8px)}}",
       ".f{animation:fade .6s ease-out 1.3s backwards}",
       "@keyframes fade{from{opacity:0}}",
       "</style>",
       f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
       f'<rect x="0" y="0" width="{W}" height="26" rx="10" fill="#161b22"/><rect x="0" y="14" width="{W}" height="12" fill="#161b22"/>',
       '<circle cx="18" cy="13" r="5" fill="#ff5f56"/><circle cx="36" cy="13" r="5" fill="#ffbd2e"/><circle cx="54" cy="13" r="5" fill="#27c93f"/>',
       f'<text x="{W/2}" y="17" text-anchor="middle" font-size="11" fill="{MUTED}">contributions — last 12 months</text>']

# month labels
last_x = -99
for d in days:
    if d["dt"].day <= 7 and d["dt"].weekday() == 6 or (d["dt"].day == 1):
        c, r = pos(d["dt"])
        x = LEFT + c * PITCH
        if r == 0 or d["dt"].day == 1:
            if x - last_x >= 36:
                out.append(f'<text x="{x}" y="{TOP-10}" font-size="10" fill="{MUTED}">{MONTHS[d["dt"].month-1]}</text>')
                last_x = x
# weekday labels
for r, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    out.append(f'<text x="8" y="{TOP + r*PITCH + 10}" font-size="9" fill="{MUTED}">{lab}</text>')

# cells
for d in days:
    c, r = pos(d["dt"])
    lvl = d["level"]
    if lvl >= 4 and mx and d["count"] >= 0.7 * mx:
        lvl = 5
    delay = (c + r) * 0.018
    tip = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} on {d["date"]}'
    out.append(f'<rect class="c" style="animation-delay:{delay:.2f}s" x="{LEFT + c*PITCH}" y="{TOP + r*PITCH}" '
               f'width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[lvl]}"><title>{tip}</title></rect>')

# footer
fy = TOP + 7 * PITCH + 28
best = st["best_day"]
out.append('<g class="f">')
out.append(f'<text x="{LEFT}" y="{fy}" font-size="13" fill="{FG}"><tspan fill="#39d353" font-weight="bold">{st["total"]:,}</tspan> contributions in the last year</text>')
out.append(f'<text x="{LEFT}" y="{fy+20}" font-size="11" fill="{MUTED}">streak: {st["current_streak"]}d  ·  longest: {st["longest_streak"]}d  ·  best day: {best["count"]} ({best["date"]})</text>')
lx = W - 40 - (6 * PITCH) - 60
out.append(f'<text x="{lx-34}" y="{fy+12}" font-size="10" fill="{MUTED}">Less</text>')
for i, col in enumerate(PALETTE):
    out.append(f'<rect x="{lx + i*PITCH}" y="{fy+2}" width="{CELL}" height="{CELL}" rx="3" fill="{col}"/>')
out.append(f'<text x="{lx + 6*PITCH + 4}" y="{fy+12}" font-size="10" fill="{MUTED}">More</text>')
out.append('</g></svg>')

open("contrib-heatmap.svg", "w").write("\n".join(out))
print("contrib-heatmap.svg", cols, "weeks", len("\n".join(out)) // 1024, "KB")
