"""data/contributions.json -> contrib-heatmap.svg (diagonal drop-in wave, plays once, then freezes)."""
import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "contributions.json").read_text())
STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BOX, GAP = 11, 3
STEP = BOX + GAP
LEFT, TOP = 34, 44
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DOW = {1: "Mon", 3: "Wed", 5: "Fri"}

days = data["days"]
first = dt.date.fromisoformat(days[0]["date"])
offset = (first.weekday() + 1) % 7  # Sunday-first rows
cells = []
for i, d in enumerate(days):
    idx = i + offset
    cells.append((idx // 7, idx % 7, d))
weeks = cells[-1][0] + 1

W = LEFT + weeks * STEP + 16
H = TOP + 7 * STEP + 52
out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="10" fill="#8b949e">',
    "<style>",
    ".c{opacity:1}" if STATIC else ".c{opacity:0;transform-box:fill-box;transform-origin:center}",
    # each cell drops in from just above, growing as it lands
    ".a{animation:drop .5s cubic-bezier(.2,.7,.2,1) forwards}"
    "@keyframes drop{from{opacity:0;transform:translateY(-9px) scale(.4)}to{opacity:1;transform:none}}",
    # reduced motion: show the finished graph at once
    "@media (prefers-reduced-motion:reduce){.c{opacity:1}.a{animation:none}}",
    "</style>",
    '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
    f'<text x="{LEFT}" y="18" fill="#c9d1d9" font-size="12">$ ./contributions.sh --user {data["username"]}</text>',
]
labels = []  # (week, month); the first column is often only the tail of a month
for w, d, day in cells:
    if d == 0:
        m = dt.date.fromisoformat(day["date"]).month
        if not labels or m != labels[-1][1]:
            if labels and w - labels[-1][0] < 3:  # too close: the later month wins
                labels.pop()
            labels.append((w, m))
for w, m in labels:
    out.append(f'<text x="{LEFT + w * STEP}" y="{TOP - 6}">{MONTHS[m - 1]}</text>')
for r, label in DOW.items():
    out.append(f'<text x="4" y="{TOP + r * STEP + 9}">{label}</text>')
for w, d, day in cells:
    delay = "" if STATIC else f' style="animation-delay:{(w + d) * 0.014:.3f}s"'
    cls = "c" if STATIC else "c a"
    tip = f'{day["count"]} on {day["date"]}'
    out.append(
        f'<rect class="{cls}"{delay} x="{LEFT + w * STEP}" y="{TOP + d * STEP}" width="{BOX}" height="{BOX}" '
        f'rx="2" fill="{PALETTE[min(day["level"], 4)]}"><title>{tip}</title></rect>'
    )
fy = TOP + 7 * STEP + 22
out.append(
    f'<text x="{LEFT}" y="{fy}" fill="#c9d1d9">{data["total"]} contributions in the last year'
    f' · current streak {data["current_streak"]}d · longest {data["longest_streak"]}d</text>'
)
lx = W - 16 - (5 * STEP + 62)
out.append(f'<text x="{lx}" y="{fy}">less</text>')
for i, c in enumerate(PALETTE):
    out.append(f'<rect x="{lx + 28 + i * STEP}" y="{fy - 9}" width="{BOX}" height="{BOX}" rx="2" fill="{c}"/>')
out.append(f'<text x="{lx + 28 + 5 * STEP + 4}" y="{fy}">more</text>')
out.append("</svg>")
(ROOT / "contrib-heatmap.svg").write_text("\n".join(out))
print("wrote contrib-heatmap.svg", weeks, "weeks")
