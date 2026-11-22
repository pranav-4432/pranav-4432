#!/usr/bin/env python3
"""
Convert Pranav's portrait photo into a clean, monochrome ASCII-art SVG
that rasters in like a terminal and freezes into a crisp vector portrait.
"""
import html
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "profile.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "pranav-ascii.svg")

COLS = int(os.environ.get("COLS", 160))
ART_W_TARGET = 800
CELL_W = ART_W_TARGET / COLS
CELL_H = CELL_W * 15 / 8
ROWS = round(COLS * 8 / 15)
RAMP = " .`:-=+*cs#%@"  # bright(sparse) -> dark(dense); leading space clears bg

# Tuned contrast and brightness for Pranav's portrait
im = Image.open(SRC).convert("L")
w, h = im.size
# Focus crop around head and shoulders
crop_box = (0, 0, w, int(h * 0.95))
im = im.crop(crop_box)
im = ImageEnhance.Contrast(im).enhance(1.3)
im = ImageEnhance.Brightness(im).enhance(1.02)
im = im.resize((COLS, ROWS), Image.Resampling.LANCZOS)
px = im.load()

GAMMA = 1.15
WHITE_FLOOR = 0.88

rows_txt = []
for y in range(ROWS):
    chars = []
    for x in range(COLS):
        lum = px[x, y] / 255.0
        lum = pow(lum, GAMMA)
        if lum >= WHITE_FLOOR:
            chars.append(" ")
            continue
        idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
        idx = max(0, min(len(RAMP) - 1, idx))
        chars.append(RAMP[idx])
    rows_txt.append("".join(chars))

PAD = 20
ART_W = COLS * CELL_W
font_size = CELL_H * 0.86
lines = []
lines.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{ART_W + PAD * 2}" height="{ROWS * CELL_H + PAD * 2}" '
    f'viewBox="0 0 {ART_W + PAD * 2} {ROWS * CELL_H + PAD * 2}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
)

for ry, line in enumerate(rows_txt):
    y = PAD + ry * CELL_H + CELL_H * 0.74
    safe = html.escape(line)
    lines.append(
        f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="#111111" '
        f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>'
    )
lines.append('</svg>')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Generated {OUT} with {len(rows_txt)} rows")
