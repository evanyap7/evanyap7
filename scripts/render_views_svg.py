"""data/contributions.json -> contrib-pulse.svg, contrib-ring.svg, contrib-streak.svg, contrib-terminal.svg.

Each plays once when the README loads, then freezes on the finished frame.
"""
import datetime as dt
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "contributions.json").read_text())

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
USER = data["username"]
W = 860

days = [d for d in data["days"] if d["date"] <= data["generated"]]
first = dt.date.fromisoformat(days[0]["date"])
offset = (first.weekday() + 1) % 7  # Sunday-first rows
cells = [((i + offset) // 7, (i + offset) % 7, d) for i, d in enumerate(days)]
weeks = cells[-1][0] + 1


def svg(w, h, style, body, header):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="{FONT}" font-size="10" fill="#8b949e">'
        f"<style>{style}</style>"
        '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>'
        + header
        + "".join(body)
        + "</svg>"
    )


def prompt(cmd, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="34" y="26" fill="#c9d1d9" font-size="12">$ {cmd}</text>'


def write(name, text):
    (ROOT / name).write_text(text)
    print("wrote", name)


def month_label(date):
    return MONTHS[dt.date.fromisoformat(date).month - 1]


def pulse():
    """Weekly totals as one line that draws itself, with a dot riding the tip."""
    totals = [0] * weeks
    for w, _, d in cells:
        totals[w] += d["count"]
    peak = max(totals) or 1
    x0, x1, y0, y1 = 40, W - 40, 60, 190
    pts = [(x0 + w / (weeks - 1) * (x1 - x0), y1 - t / peak * (y1 - y0)) for w, t in enumerate(totals)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{line} L{x1},{y1} L{x0},{y1} Z"
    bw = max(range(weeks), key=totals.__getitem__)
    bx, by = pts[bw]
    labels = []
    for w, d, day in cells:
        if d == 0 and dt.date.fromisoformat(day["date"]).day <= 7:
            x = x0 + w / (weeks - 1) * (x1 - x0)
            labels.append(f'<text x="{x:.1f}" y="{y1 + 18}" text-anchor="middle">{month_label(day["date"])}</text>')
    style = (
        ".l{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 3s cubic-bezier(.4,0,.2,1) forwards}"
        "@keyframes draw{to{stroke-dashoffset:0}}"
        ".f,.p{opacity:0;animation:show .8s ease-out 2.6s forwards}@keyframes show{to{opacity:1}}"
        "@media (prefers-reduced-motion:reduce){.l{animation:none;stroke-dashoffset:0}"
        ".f,.p{animation:none;opacity:1}.d{display:none}}"
    )
    body = [
        '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#39d353" stop-opacity=".35"/>'
        '<stop offset="1" stop-color="#39d353" stop-opacity="0"/></linearGradient></defs>',
        f'<path class="f" d="{area}" fill="url(#g)"/>',
        f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#21262d"/>',
        f'<path class="l" pathLength="1" d="{line}" fill="none" stroke="#39d353" stroke-width="2" '
        'stroke-linejoin="round" stroke-linecap="round"/>',
        f'<circle class="d" r="4" fill="#39d353"><animateMotion dur="3s" fill="freeze" '
        f'calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1" path="{line}"/></circle>',
        f'<g class="p"><circle cx="{bx:.1f}" cy="{by:.1f}" r="4" fill="#0d1117" stroke="#39d353" stroke-width="2"/>'
        f'<text x="{bx:.1f}" y="{by - 12:.1f}" text-anchor="middle" fill="#c9d1d9">'
        f"busiest week · {totals[bw]}</text></g>",
        *labels,
        f'<text x="{x1}" y="26" text-anchor="end">{data["total"]} contributions · {weeks} weeks</text>',
    ]
    write("contrib-pulse.svg", svg(W, y1 + 36, style, body, prompt(f"./pulse.sh --user {USER} --by week")))


def ring():
    """Weekdays as concentric rings, weeks as spokes, revealed by a sweeping hand."""
    cx, cy, r0, th, step = 190, 190, 52, 11, 14
    sweep = 2.6
    da = 360 / weeks

    def pt(r, a):
        a = math.radians(a)
        return cx + r * math.sin(a), cy - r * math.cos(a)

    def sector(r_in, r_out, a0, a1):
        (x1, y1), (x2, y2) = pt(r_out, a0), pt(r_out, a1)
        (x3, y3), (x4, y4) = pt(r_in, a1), pt(r_in, a0)
        return (f"M{x1:.1f},{y1:.1f}A{r_out},{r_out} 0 0 1 {x2:.1f},{y2:.1f}"
                f"L{x3:.1f},{y3:.1f}A{r_in},{r_in} 0 0 0 {x4:.1f},{y4:.1f}Z")

    body = []
    for w, d, day in cells:
        a0 = w * da
        r_in = r0 + d * step
        body.append(
            f'<path class="c" style="animation-delay:{a0 / 360 * sweep:.3f}s" '
            f'd="{sector(r_in, r_in + th, a0, a0 + da - 0.6)}" fill="{PALETTE[min(day["level"], 4)]}">'
            f'<title>{day["count"]} on {day["date"]}</title></path>'
        )
    outer = r0 + 7 * step
    busiest = max(days, key=lambda d: d["count"])
    stats = [
        (str(data["total"]), "contributions"),
        (f'{data["current_streak"]}d', "current streak"),
        (f'{data["longest_streak"]}d', "longest streak"),
        (str(busiest["count"]), f'busiest day · {busiest["date"]}'),
    ]
    for i, (big, small) in enumerate(stats):
        y = 96 + i * 52
        body.append(f'<text x="430" y="{y}" fill="#c9d1d9" font-size="26">{big}</text>')
        body.append(f'<text x="430" y="{y + 18}">{small}</text>')
    body.append(f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" fill="#c9d1d9" font-size="12">{USER}</text>')
    hx, hy = pt(outer + 6, 0)
    body.append(f'<line class="h" x1="{cx}" y1="{cy}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="#39d353" stroke-width="1.5"/>')
    style = (
        ".c{opacity:0;animation:in .4s ease-out forwards}@keyframes in{to{opacity:1}}"
        f".h{{transform-origin:{cx}px {cy}px;opacity:0;animation:spin {sweep}s linear forwards}}"
        "@keyframes spin{0%{transform:rotate(0);opacity:1}99%{opacity:1}100%{transform:rotate(360deg);opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.c{animation:none;opacity:1}.h{display:none}}"
    )
    write("contrib-ring.svg", svg(W, 2 * cy + 4, style, body,
                                  prompt(f"./ring.sh --user {USER} --rings weekday --spokes week")))


def streak():
    """The last 12 weeks, with the current streak traced day by day and the day off before it marked."""
    cur = data["current_streak"]
    recent = days[-84:]
    end = max((i for i, d in enumerate(recent) if d["count"] > 0 or d["level"] > 0), default=len(recent) - 1)
    start = end - cur + 1
    size, gap, left, top = 26, 6, 80, 56
    off = (dt.date.fromisoformat(recent[0]["date"]).weekday() + 1) % 7
    pos = {i: (left + ((i + off) // 7) * (size + gap), top + ((i + off) % 7) * (size + gap))
           for i in range(len(recent))}
    ncols = (len(recent) + off - 1) // 7 + 1
    h = top + 7 * (size + gap) + 34
    body = []
    for i, d in enumerate(recent):
        x, y = pos[i]
        body.append(
            f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="5" fill="{PALETTE[min(d["level"], 4)]}">'
            f'<title>{d["count"]} on {d["date"]}</title></rect>'
        )
    step_t = 0.13
    total_t = step_t * cur
    centers = [(pos[i][0] + size / 2, pos[i][1] + size / 2) for i in range(start, end + 1)]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in centers)
    for k, i in enumerate(range(start, end + 1)):
        x, y = pos[i]
        body.append(
            f'<rect class="t" style="animation-delay:{k * step_t:.2f}s" x="{x - 1}" y="{y - 1}" '
            f'width="{size + 2}" height="{size + 2}" rx="6" fill="none" stroke="#39d353" stroke-width="2"/>'
        )
    body.append(
        f'<circle class="d" r="5" fill="#fff"><animateMotion dur="{total_t:.2f}s" fill="freeze" '
        f'path="{path}" calcMode="linear"/></circle>'
    )
    if start > 0:
        x, y = pos[start - 1]
        body.append(
            f'<g class="m" style="animation-delay:{total_t:.2f}s">'
            f'<rect x="{x - 3}" y="{y - 3}" width="{size + 6}" height="{size + 6}" rx="8" fill="none" '
            'stroke="#f85149" stroke-width="1.5" stroke-dasharray="4 3"/>'
            f'<text x="{x + size / 2}" y="{top - 10}" text-anchor="middle" fill="#f85149">last day off</text></g>'
        )
    ex, _ = pos[end]
    body.append(
        f'<text class="m" style="animation-delay:{total_t:.2f}s" x="{ex + size / 2}" y="{h - 12}" '
        f'text-anchor="middle" fill="#39d353">day {cur}</text>'
    )
    px = left + ncols * (size + gap) + 40
    body += [
        f'<text x="{px}" y="{top + 28}" fill="#c9d1d9" font-size="38">{cur}</text>',
        f'<text x="{px}" y="{top + 48}">days in a row</text>',
        f'<text x="{px}" y="{top + 100}" fill="#c9d1d9" font-size="38">{data["longest_streak"]}</text>',
        f'<text x="{px}" y="{top + 120}">longest this year</text>',
    ]
    for r, label in {1: "Mon", 3: "Wed", 5: "Fri"}.items():
        body.append(f'<text x="34" y="{top + r * (size + gap) + 17}">{label}</text>')
    style = (
        ".t{opacity:0;animation:trail 1.6s ease-out forwards}"
        "@keyframes trail{0%{opacity:0}10%{opacity:1}100%{opacity:.35}}"
        ".m{opacity:0;animation:show .5s ease-out forwards}@keyframes show{to{opacity:1}}"
        "@media (prefers-reduced-motion:reduce){.t{animation:none;opacity:.35}.m{animation:none;opacity:1}.d{display:none}}"
    )
    write("contrib-streak.svg", svg(W, h, style, body, prompt(f"./streak.sh --user {USER}")))


def terminal():
    """A typed command, then every day scrambles through noise and settles on . : + # @ by level."""
    glyphs = [".", ":", "+", "#", "@"]
    colors = ["#3b434d", "#0e6b3a", "#1f9d4d", "#39d353", "#7ee787"]
    junk = "░▒%&$*=?/\\<>"
    cw, ch, left, top = 14, 17, 34, 62
    cmd = f"./contributions.sh --user {USER} --ascii"
    type_t = len(cmd) * 0.045
    body = ['<defs><clipPath id="k"><rect class="k" x="0" y="0" height="40"/></clipPath></defs>']
    for w, d, day in cells:
        x, y = left + w * cw, top + d * ch
        delay = type_t + 0.2 + (w + d) * 0.012
        lvl = min(day["level"], 4)
        for n, j in enumerate((junk[(w * 7 + d * 3) % len(junk)], junk[(w * 5 + d * 11 + 4) % len(junk)])):
            body.append(f'<text class="j" style="animation-delay:{delay + n * .14:.3f}s" x="{x}" y="{y}" fill="#6e7681">{html.escape(j)}</text>')
        body.append(
            f'<text class="g" style="animation-delay:{delay + .28:.3f}s" x="{x}" y="{y}" fill="{colors[lvl]}">'
            f'{glyphs[lvl]}<title>{day["count"]} on {day["date"]}</title></text>'
        )
    fy = top + 7 * ch + 22
    legend = " ".join(f'<tspan fill="{c}">{g}</tspan>' for g, c in zip(glyphs, colors))
    body.append(f'<text x="34" y="{fy}">{legend}  none → busiest · {data["total"]} contributions, {weeks} weeks</text>')
    style = (
        f".k{{width:0;animation:type {type_t:.2f}s steps({len(cmd)}) forwards}}"
        f"@keyframes type{{to{{width:{len(cmd) * 7.8 + 50:.0f}px}}}}"
        ".ty{clip-path:url(#k)}"
        ".j{opacity:0;animation:blip .14s steps(1) forwards}@keyframes blip{0%{opacity:1}100%{opacity:0}}"
        ".g{opacity:0;animation:show .01s forwards}@keyframes show{to{opacity:1}}"
        "@media (prefers-reduced-motion:reduce){.g{animation:none;opacity:1}.j{display:none}.ty{clip-path:none}.k{animation:none}}"
    )
    write("contrib-terminal.svg", svg(W, fy + 20, style, body, prompt(cmd, "ty")))


pulse()
ring()
streak()
terminal()
