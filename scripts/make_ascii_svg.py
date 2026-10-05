"""source-prepped.png -> amine-ascii.svg  (monochrome ASCII portrait that 'types' itself in once)
STATIC=1 python scripts/make_ascii_svg.py  -> frozen frame, no animation"""
import os
import cv2
import numpy as np

STATIC = os.environ.get("STATIC") == "1"
COLS, ROWS = 130, 65                 # char cell is ~2x taller than wide -> square image
W, H, PAD = 380, 380, 10
CW, CH = (W - 2 * PAD) / COLS, (H - 2 * PAD) / ROWS
RAMP = " .'`^,:;-~=+*cs#%@"        # empty/sparse -> dense. Dense = bright on the dark panel
LIGHT = os.environ.get("THEME", "light") == "light"
FG, BG, CURSOR = ("#161b22", "#eef1f5", "#1f883d") if LIGHT else ("#e6edf3", "#0d1117", "#39d353")

img = cv2.imread("source-prepped.png", cv2.IMREAD_UNCHANGED)
g0 = cv2.resize(img[..., 0], (COLS * 4, ROWS * 4), interpolation=cv2.INTER_AREA)
g0 = cv2.addWeighted(g0, 1.8, cv2.GaussianBlur(g0, (0, 0), 6), -0.8, 0)          # unsharp: crisper eyes/brows/mouth
gray = cv2.resize(g0, (COLS, ROWS), interpolation=cv2.INTER_AREA) / 255.0
alpha = cv2.resize(img[..., 3], (COLS, ROWS), interpolation=cv2.INTER_AREA) / 255.0

if LIGHT:
    gray = 1 - gray                                   # light panel: dark pixels become dense ink
# rank-equalize tones inside the subject so the whole ramp gets used (flat-lit faces need this)
inside = alpha >= 0.5
vals = gray[inside]
order = vals.argsort().argsort() / max(1, len(vals) - 1)
dens = np.zeros_like(gray)
dens[inside] = order
dens8 = (np.where(inside, dens, np.median(dens[inside])) * 255).astype(np.uint8)
dens = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(4, 4)).apply(dens8) / 255.0   # even out lopsided lighting

rows = []
for r in range(ROWS):
    line = ""
    for c in range(COLS):
        if not inside[r, c]:
            line += " "
            continue
        d = 0.20 + 0.80 * dens[r, c] ** 1.15
        fade = max(0.0, (r - 0.80 * ROWS) / (0.20 * ROWS))
        d *= 1 - 0.95 * fade                          # neck fades out at the bottom
        line += RAMP[min(len(RAMP) - 1, int(d * (len(RAMP) - 1) + 0.5))]
    rows.append(line)

# keep a text preview for debugging
open("/tmp/ascii.txt", "w").write("\n".join(rows))

nbsp = lambda s: s.replace(" ", "&#160;").replace("&", "&amp;").replace("&amp;#160;", "&#160;")
STAG, WIPE = 0.04, 0.55
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ASCII art portrait of Amine">',
       '<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;white-space:pre}</style>',
       f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>', "<defs>"]
if not STATIC:
    for i in range(ROWS):
        d = i * STAG; T = d + WIPE; k = d / T
        out.append(f'<clipPath id="c{i}"><rect x="{PAD}" y="{PAD + i*CH:.2f}" width="{W-2*PAD}" height="{CH+0.5:.2f}">'
                   f'<animate attributeName="width" dur="{T:.2f}s" begin="0s" fill="freeze" values="0;0;{W-2*PAD}" keyTimes="0;{k:.4f};1"/></rect></clipPath>')
out.append("</defs>")
for i, line in enumerate(rows):
    if not line.strip():
        continue
    y = PAD + (i + 0.8) * CH
    lead, body = len(line) - len(line.lstrip()), line.strip()   # position by offset: no reliance on leading/trailing spaces
    clip = "" if STATIC else f' clip-path="url(#c{i})"'
    out.append(f'<text x="{PAD + lead*CW:.2f}" y="{y:.2f}" font-size="{CW/0.6:.2f}" fill="{FG}" textLength="{len(body)*CW:.2f}" lengthAdjust="spacing" xml:space="preserve"{clip}>{nbsp(body)}</text>')
if not STATIC:
    for i, line in enumerate(rows):
        if not line.strip():
            continue
        d = i * STAG; T = d + WIPE; k = d / T
        out.append(f'<rect y="{PAD + i*CH:.2f}" width="{CW*1.6:.2f}" height="{CH:.2f}" fill="{CURSOR}" opacity="0">'
                   f'<animate attributeName="x" dur="{T:.2f}s" begin="0s" fill="freeze" values="{PAD};{PAD};{W-PAD}" keyTimes="0;{k:.4f};1"/>'
                   f'<animate attributeName="opacity" dur="{T:.2f}s" begin="0s" fill="freeze" values="0;0;0.9;0.9;0" keyTimes="0;{k:.4f};{min(k+0.001,0.999):.4f};0.995;1"/></rect>')
out.append("</svg>")
open("amine-ascii.svg", "w").write("\n".join(out))
print("amine-ascii.svg", sum(len(x) for x in out) // 1024, "KB")
