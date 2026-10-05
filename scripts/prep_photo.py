"""Prep a portrait for ASCII art: crop -> isolate subject (GrabCut) -> CLAHE contrast.
Usage: python scripts/prep_photo.py source-photo.png [x0 y0 size]
Writes source-prepped.png (grayscale + alpha mask)."""
import sys
import cv2
import numpy as np

src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.png"
img = cv2.imread(src)
h, w = img.shape[:2]

# square crop around head + neck (tweak these 3 numbers for your photo)
if len(sys.argv) >= 5:
    x0, y0, size = map(int, sys.argv[2:5])
else:
    size = int(w * 0.68)
    x0, y0 = int(w * 0.16), int(h * 0.02)
crop = img[y0:y0 + size, x0:x0 + size]
crop = cv2.resize(crop, (700, 700), interpolation=cv2.INTER_AREA)

# 1) isolate the subject with GrabCut (works great on a plain studio background)
mask = np.full(crop.shape[:2], cv2.GC_PR_BGD, np.uint8)
mask[:25, :] = mask[:, :25] = mask[:, -25:] = cv2.GC_BGD
mask[:, :60] = cv2.GC_BGD
cv2.ellipse(mask, (350, 330), (200, 280), 0, 0, 360, cv2.GC_PR_FGD, -1)
cv2.ellipse(mask, (350, 360), (110, 170), 0, 0, 360, cv2.GC_FGD, -1)
cv2.rectangle(mask, (305, 470), (395, 640), cv2.GC_FGD, -1)   # neck
bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
cv2.grabCut(crop, mask, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fg)
if n > 1:
    fg = np.where(lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
fg = cv2.GaussianBlur(fg, (5, 5), 0)

# 2) boost local contrast so a flat-lit face gets real highlights/shadows
gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
gray = cv2.addWeighted(cv2.createCLAHE(clipLimit=2.0, tileGridSize=(6, 6)).apply(gray), 0.65, gray, 0.35, 0)

cv2.imwrite("source-prepped.png", np.dstack([gray, gray, gray, fg]))
cv2.imwrite("/tmp/prep-preview.png", np.where(fg[..., None] > 127, np.dstack([gray] * 3), 255).astype(np.uint8))
print("wrote source-prepped.png", crop.shape[:2])
