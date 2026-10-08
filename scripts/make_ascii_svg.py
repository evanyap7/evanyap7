"""assets/source-prepped.png (+ mask) -> evan-ascii.svg, an ASCII portrait that types in once, row by row."""
import os
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"  # skip the typing animation for previews
COLS = 84
CHAR_W, LINE_H, FONT = 5.0, 8.2, 8.2
RAMP = " .:-=+*#%@"  # sparse -> dense, drawn light-on-dark
ROW_STAGGER, ROW_DUR = 0.05, 0.45
FG, BG = "#c9d1d9", "#0d1117"

img = Image.open(ROOT / "assets" / "source-prepped.png").convert("L")
mask = Image.open(ROOT / "assets" / "source-mask.png").convert("L")
rows = round(COLS * img.height / img.width * (CHAR_W / LINE_H))
img = img.resize((COLS, rows), Image.LANCZOS)
mask = mask.resize((COLS, rows), Image.LANCZOS)
g = np.asarray(img, dtype=np.float32) / 255.0
m = np.asarray(mask, dtype=np.float32) / 255.0

lo, hi = np.percentile(g[m > 0.5], [2, 98])
g = 0.12 + 0.88 * np.clip((g - lo) / (hi - lo), 0, 1) ** 1.6  # floor keeps dark hair/eyes visible; gamma pushes mid-tones down

lines = []
for y in range(rows):
    s = ""
    for x in range(COLS):
        if m[y, x] < 0.5:
            s += " "
        else:
            s += RAMP[min(int(g[y, x] * (len(RAMP) - 1) + 0.5), len(RAMP) - 1)]
    lines.append(s.rstrip())

pad = 10
W, H = COLS * CHAR_W + 2 * pad, rows * LINE_H + 2 * pad
out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
    f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>',
    "<defs>",
]
for i in range(rows):
    if STATIC:
        out.append(
            f'<clipPath id="c{i}"><rect x="{pad}" y="{pad + i * LINE_H:.1f}" width="{COLS * CHAR_W:.1f}" height="{LINE_H}"/></clipPath>'
        )
        continue
    out.append(
        f'<clipPath id="c{i}"><rect x="{pad}" y="{pad + i * LINE_H:.1f}" width="0" height="{LINE_H}">'
        f'<animate attributeName="width" from="0" to="{COLS * CHAR_W:.1f}" dur="{ROW_DUR}s" '
        f'begin="{0.3 + i * ROW_STAGGER:.2f}s" fill="freeze"/></rect></clipPath>'
    )
out.append("</defs>")
out.append(f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FONT}" fill="{FG}" xml:space="preserve">')
for i, line in enumerate(lines):
    if not line.strip():
        continue
    esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    lead = len(line) - len(line.lstrip())
    esc = esc.lstrip()
    out.append(
        f'<text x="{pad + lead * CHAR_W:.1f}" y="{pad + (i + 1) * LINE_H - 1.5:.1f}" '
        f'textLength="{(len(line) - lead) * CHAR_W:.1f}" lengthAdjust="spacing" clip-path="url(#c{i})">{esc}</text>'
    )
out.append("</g></svg>")
(ROOT / "evan-ascii.svg").write_text("\n".join(out))
print("wrote evan-ascii.svg", COLS, "x", rows)
