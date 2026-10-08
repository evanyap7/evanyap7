"""Remove background, boost local contrast, composite on white -> assets/source-prepped.png.

Local-only: needs the packages in requirements-local.txt.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets" / "photo.jpg"
OUT = ROOT / "assets" / "source-prepped.png"

img = Image.open(SRC).convert("RGB")
cut = remove(img)  # RGBA, background transparent
alpha = np.array(cut.split()[-1])

# crop to head + shoulders: top of subject down to ~52% of subject height
ys, xs = np.where(alpha > 128)
top, bottom = ys.min(), ys.max()
left, right = xs.min(), xs.max()
bottom = int(top + (bottom - top) * 0.52)
# center horizontally on the head (top 35% of the crop), half-width = 0.42 * crop height
head = xs[ys < top + (bottom - top) * 0.35]
cx = int((head.min() + head.max()) / 2)
half = int((bottom - top) * 0.42)
pad = int((bottom - top) * 0.03)
box = (max(cx - half, 0), max(top - pad, 0), min(cx + half, img.width), bottom)
cut = cut.crop(box)

rgba = np.array(cut)
gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)

a = rgba[:, :, 3:4].astype(np.float32) / 255.0
out = (gray[:, :, None] * a + 255 * (1 - a)).astype(np.uint8)
Image.fromarray(out[:, :, 0]).save(OUT)
Image.fromarray(rgba[:, :, 3]).save(ROOT / "assets" / "source-mask.png")
print("wrote", OUT, out.shape)
