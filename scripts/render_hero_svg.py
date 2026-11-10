"""-> hero.svg: terminal card that types out a rotating tagline, with a pulsing status dot.

Pure CSS animation inside an <img>-embedded SVG (GitHub strips JS). STATIC=1 renders the first line, no motion.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"

PHRASES = [
    "builds AI agents and measures whether they work",
    "ships production LLM systems, with evals",
    "open to AI and software engineering internships",
]
W, H = 860, 150
X0, Y = 36, 84
CH = 10.0  # forced glyph advance (textLength), so clip widths are exact in any monospace font
SLOT = 5.0  # seconds per phrase
TYPE = 2.2  # seconds spent typing
CYCLE = SLOT * len(PHRASES)


def pct(t):
    return f"{t / CYCLE * 100:.3f}%"


css = [
    ".bg{fill:#0d1117}.dim{fill:#8b949e}.fg{fill:#c9d1d9}.g{fill:#39d353}.ph{fill:#e6edf3}",
    "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}",
]
body = []
if STATIC:
    full = len(PHRASES[0]) * CH
    body.append(
        f'<text class="ph" x="{X0}" y="{Y}" font-size="17" textLength="{full}" '
        f'lengthAdjust="spacingAndGlyphs">{PHRASES[0]}</text>'
    )
else:
    css.append(
        ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2s ease-out infinite}"
        "@keyframes pulse{0%{transform:scale(1);opacity:.7}100%{transform:scale(3.2);opacity:0}}"
    )
    for i, text in enumerate(PHRASES):
        n = len(text)
        full = n * CH
        a, t, b = i * SLOT, i * SLOT + TYPE, (i + 1) * SLOT
        # width steps up while typing, holds, then snaps shut; the cursor rides the same timeline
        kf = f"0%,{pct(a)}{{width:0}}" if a > 0 else ""
        kf += f"{pct(a)}{{width:0;animation-timing-function:steps({n},end)}}"
        kf += f"{pct(t)},{pct(b - 0.05)}{{width:{full}px}}"
        kf += f"{pct(b)},100%{{width:0}}"
        ck = f"{pct(a)}{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
        ck += f"{pct(t)},{pct(b - 0.05)}{{transform:translateX({full}px)}}"
        ck += f"{pct(b)},100%{{transform:translateX(0)}}"
        vis = f"0%,{pct(max(a - 0.05, 0))}{{opacity:0}}" if a > 0 else ""
        vis += f"{pct(a)},{pct(b - 0.05)}{{opacity:1}}{pct(b)},100%{{opacity:0}}"
        css.append(
            f"@keyframes w{i}{{{kf}}}@keyframes c{i}{{{ck}}}@keyframes v{i}{{{vis}}}"
            f".w{i}{{animation:w{i} {CYCLE}s linear infinite}}"
            f".c{i}{{animation:c{i} {CYCLE}s linear infinite}}"
            f".v{i}{{animation:v{i} {CYCLE}s linear infinite}}"
        )
        body.append(
            f'<clipPath id="k{i}"><rect class="w{i}" x="{X0}" y="{Y - 22}" width="0" height="30"/></clipPath>'
            f'<g class="v{i}"><text class="ph" x="{X0}" y="{Y}" font-size="17" textLength="{full}" '
            f'lengthAdjust="spacingAndGlyphs" clip-path="url(#k{i})">{text}</text>'
            f'<rect class="g c{i}" x="{X0 + 1}" y="{Y - 16}" width="9" height="20"/></g>'
        )
    # reduced motion: freeze on the first line, fully typed
    css.append(
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}"
        f".v1,.v2{{opacity:0}}.v0{{opacity:1}}clipPath rect{{width:{len(PHRASES[0]) * CH}px}}}}"
    )

status_x = W - 36 - 188
sx, sy = status_x + 6, 22
dot = f'<circle class="g" cx="{sx}" cy="{sy}" r="4"/>'
if not STATIC:
    dot = f'<circle class="g pulse" cx="{sx}" cy="{sy}" r="4"/>' + dot
out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
    'aria-label="Evan Yap: builds AI agents and measures whether they work">',
    "<style>" + "".join(css) + "</style>",
    f'<rect class="bg" width="{W}" height="{H}" rx="10"/>',
    '<circle cx="24" cy="20" r="5" fill="#ff5f56"/><circle cx="42" cy="20" r="5" fill="#ffbd2e"/>'
    '<circle cx="60" cy="20" r="5" fill="#27c93f"/>',
    f'<text class="dim" x="{X0}" y="58" font-size="13">evan@sutd ~ $ whoami</text>',
    *body,
    f'<text class="dim" x="{X0}" y="124" font-size="12">'
    "Singapore · SUTD BEng + MSc Tech Entrepreneurship · Univers AI intern</text>",
    dot,
    f'<text class="fg" x="{status_x + 18}" y="26" font-size="12">open to internships</text>',
    "</svg>",
]
(ROOT / "hero.svg").write_text("\n".join(out))
print("wrote hero.svg")
