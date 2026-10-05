"""Hand-authored neofetch-style card -> info-card.svg   (STATIC=1 for a frozen frame)
Edit the CONTENT list below, re-run, commit the SVG."""
import os
from xml.sax.saxutils import escape

STATIC = os.environ.get("STATIC") == "1"
W, H = 490, 370
BG, BAR, FG, KEY, MUTED, GREEN = "#0d1117", "#161b22", "#e6edf3", "#58a6ff", "#7d8590", "#39d353"

TITLE = "Mohamed Amine Bouhassoune"
HOST = "amine@ensa-agadir"
CONTENT = [                      # (key, value)  keep values under ~44 chars
    ("Role",     "IT & AI Engineering student @ ENSA Agadir"),
    ("Now",      "CS:APP · OSTEP · NeetCode 150 (21/150)"),
    ("Systems",  "C · pointers · memory layout · linking"),
    ("Stack",    "C, C++, Python, JavaScript, HTML/CSS"),
    ("Learning", "Linux, SQL → ML · LLMOps · DevOps · Cloud"),
    ("Built",    "Telegram price bot · lumi-ai · PDFMate"),
    ("Seeking",  "Summer 2027 internship · SWE / AI / systems"),
    ("LinkedIn", "in/aminebouhassoune"),
    ("Email",    "aminemestro@gmail.com"),
]
PALETTE = ["#ff7b72", "#ffa657", "#f2cc60", "#39d353", "#58a6ff", "#bc8cff", "#e6edf3", "#7d8590"]

def line(delay, inner):
    if STATIC:
        return f"<g>{inner}</g>"
    return f'<g class="l" style="animation-delay:{delay:.2f}s">{inner}</g>'

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Info card for Mohamed Amine Bouhassoune">',
       "<style>",
       "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;font-size:13px}",
       ".l{animation:in .5s ease-out backwards}",
       "@keyframes in{from{opacity:0;transform:translateX(-10px)}}",
       ".b{animation:blink 1.1s steps(1) infinite}",
       "@keyframes blink{50%{opacity:0}}",
       "</style>",
       f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
       f'<rect width="{W}" height="26" rx="10" fill="{BAR}"/><rect y="14" width="{W}" height="12" fill="{BAR}"/>',
       '<circle cx="18" cy="13" r="5" fill="#ff5f56"/><circle cx="36" cy="13" r="5" fill="#ffbd2e"/><circle cx="54" cy="13" r="5" fill="#27c93f"/>',
       f'<text x="{W/2}" y="17" text-anchor="middle" font-size="11" fill="{MUTED}" style="font-size:11px">{HOST}: ~</text>']

out.append(line(0.3, f'<text x="22" y="56" fill="{GREEN}" style="font-size:16px;font-weight:bold">{escape(TITLE)}</text>'))
out.append(line(0.5, f'<text x="22" y="76" fill="{MUTED}">{"─" * 40}</text>'))
y = 102
for i, (k, v) in enumerate(CONTENT):
    out.append(line(0.7 + i * 0.22,
        f'<text x="22" y="{y}" fill="{KEY}" style="font-weight:bold">{escape(k)}</text>'
        f'<text x="100" y="{y}" fill="{MUTED}">:</text>'
        f'<text x="116" y="{y}" fill="{FG}">{escape(v)}</text>'))
    y += 26
pal = "".join(f'<rect x="{22 + j*22}" y="{y-10}" width="18" height="12" rx="2" fill="{c}"/>' for j, c in enumerate(PALETTE))
out.append(line(0.7 + len(CONTENT) * 0.22, pal))
out.append(line(0.9 + len(CONTENT) * 0.22,
    f'<text x="22" y="{y+26}" fill="{GREEN}">amine@github</text><text x="124" y="{y+26}" fill="{MUTED}">~ $</text>'
    f'<rect class="{"" if STATIC else "b"}" x="156" y="{y+14}" width="8" height="15" fill="{FG}"/>'))
out.append("</svg>")
open("info-card.svg", "w").write("\n".join(out))
print("info-card.svg", len("\n".join(out)) // 1024, "KB")
