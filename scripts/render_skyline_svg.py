"""data/contributions.json -> contrib-skyline.svg (every day a 3D block that rises in a wave, then freezes)."""
import datetime as dt
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "contributions.json").read_text())
STATIC = os.environ.get("STATIC") == "1"

# front face by GitHub level; the top is lighter and the side darker, so each block reads as solid
FRONT = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
TOP = ["#1c2128", "#17653d", "#0f8a45", "#3dbb59", "#6ee786"]
SIDE = ["#10141a", "#093020", "#004d24", "#1a7a2e", "#28a043"]

W_BOX, DX, DY = 9, 4, 4      # block width, and how far its top and side lean back
PITCH = W_BOX + DX           # one week to the next
RX, RY = 5, 5                # how far each day of the week sits back and up
LEFT, HEAD = 34, 26
H_MAX = 70                   # the tallest block, in px
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

days = data["days"]
first = dt.date.fromisoformat(days[0]["date"])
offset = (first.weekday() + 1) % 7  # Sunday-first rows
cells = [((i + offset) // 7, (i + offset) % 7, d) for i, d in enumerate(days)]
weeks = cells[-1][0] + 1
peak = max(d["count"] for d in days) or 1
best = max(cells, key=lambda c: c[2]["count"])

W = LEFT + weeks * PITCH + 6 * RX + 24
BASE = HEAD + H_MAX + 6 * RY + 30   # y of the front row's floor
H = BASE + 46


def origin(w, d):
    """Bottom-left corner of a day's block; later days of the week sit further back."""
    return LEFT + w * PITCH + d * RX, BASE - d * RY


def height(count):
    # square root, so one very busy day does not flatten every other block
    return 0 if count == 0 else 3 + math.sqrt(count / peak) * (H_MAX - 3)


def poly(points, fill):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="{fill}"/>'


out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="10" fill="#8b949e">',
    "<style>",
    ".b{transform-box:fill-box;transform-origin:50% 100%}" if STATIC else
    ".b{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0);animation:rise .6s cubic-bezier(.2,.8,.2,1) forwards}"
    "@keyframes rise{to{transform:scaleY(1)}}"
    ".m{opacity:0;animation:show .5s ease-out 1.3s forwards}@keyframes show{to{opacity:1}}",
    # reduced motion: show the finished skyline at once
    "@media (prefers-reduced-motion:reduce){.b{animation:none;transform:none}.m{animation:none;opacity:1}}",
    "</style>",
    '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
    f'<text x="{LEFT}" y="18" fill="#c9d1d9" font-size="12">$ ./skyline.sh --user {data["username"]}</text>',
]

# the floor first: one flat tile per day, back rows before front rows
for w, d, day in sorted(cells, key=lambda c: -c[1]):
    x, y = origin(w, d)
    out.append(poly([(x, y), (x + W_BOX, y), (x + W_BOX + DX, y - DY), (x + DX, y - DY)], FRONT[0] if day["count"] == 0 else "#10141a"))

# then the blocks, back to front so nearer ones cover the ones behind
for w, d, day in sorted(cells, key=lambda c: -c[1]):
    if day["count"] == 0:
        continue
    x, y = origin(w, d)
    h = height(day["count"])
    lv = min(day["level"], 4)
    delay = "" if STATIC else f' style="animation-delay:{w * 0.014 + (6 - d) * 0.004:.3f}s"'
    out.append(
        f'<g class="b"{delay}><title>{day["count"]} on {day["date"]}</title>'
        f'<rect x="{x}" y="{y - h:.1f}" width="{W_BOX}" height="{h:.1f}" fill="{FRONT[lv]}"/>'
        + poly([(x, y - h), (x + W_BOX, y - h), (x + W_BOX + DX, y - h - DY), (x + DX, y - h - DY)], TOP[lv])
        + poly([(x + W_BOX, y - h), (x + W_BOX + DX, y - h - DY), (x + W_BOX + DX, y - DY), (x + W_BOX, y)], SIDE[lv])
        + "</g>"
    )

# month names along the front edge; the first column is often only the tail of a month
labels = []
for w, d, day in cells:
    if d == 0:
        m = dt.date.fromisoformat(day["date"]).month
        if not labels or m != labels[-1][1]:
            if labels and w - labels[-1][0] < 3:
                labels.pop()
            labels.append((w, m))
for w, m in labels:
    out.append(f'<text x="{LEFT + w * PITCH}" y="{BASE + 16}">{MONTHS[m - 1]}</text>')

# the busiest day gets a leader line and a label, shown once the skyline has risen
bw, bd, bday = best
bx, by = origin(bw, bd)
top = by - height(bday["count"]) - DY
label = f'busiest day: {bday["count"]} on {bday["date"]}'
anchor = "end" if bx > W * 0.6 else "start"
tx = bx + W_BOX / 2 + (-6 if anchor == "end" else 6)
out.append(
    f'<g class="m"><line x1="{bx + W_BOX / 2 + DX / 2:.1f}" y1="{top:.1f}" x2="{bx + W_BOX / 2 + DX / 2:.1f}" y2="{HEAD - 4}" stroke="#39d353" stroke-width="1"/>'
    f'<text x="{tx:.1f}" y="{HEAD + 4}" text-anchor="{anchor}" fill="#c9d1d9">{label}</text></g>'
)

fy = BASE + 36
out.append(
    f'<text x="{LEFT}" y="{fy}" fill="#c9d1d9">{data["total"]} contributions in the last year'
    f' · current streak {data["current_streak"]}d · longest {data["longest_streak"]}d</text>'
)
out.append("</svg>")
(ROOT / "contrib-skyline.svg").write_text("\n".join(out))
print("wrote contrib-skyline.svg", weeks, "weeks, busiest day", bday["count"])
