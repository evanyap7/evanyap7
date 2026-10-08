"""Terminal-style footer -> now.svg: types `cat now.txt`, fades in the output, then blinks a prompt. STATIC=1 freezes it."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"

PROMPT = "evan@github ~ $ "
CMD = "cat now.txt"
ROWS = [
    ("building", "ESG decarbonisation audit agent @ Univers"),
    ("shipping", "Telegram AI assistant · WebGL / Three.js interfaces"),
    ("training", "HYROX · powerlifting"),
    ("ask me", "AI agents · WebGL · SUTD · coffee"),
]

W, PAD = 860, 24
FONT, CW, LH = 14, 8.4, 24  # monospace advance ~0.6em
H = PAD + LH * (len(ROWS) + 3) + 8
TYPE_START, TYPE_STEP = 0.5, 0.09
type_end = TYPE_START + TYPE_STEP * len(CMD)

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FONT}">',
    "<style>",
    ".o{opacity:1}" if STATIC else ".o{opacity:0;animation:in .4s ease-out forwards}",
    "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}",
    ".p{fill:#39d353;font-weight:bold}.c{fill:#c9d1d9}.k{fill:#58a6ff;font-weight:bold}.v{fill:#c9d1d9}",
    "</style>",
    '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
]

y0 = PAD + LH
x_cmd = PAD + len(PROMPT) * CW
# typed command: a clip rect revealing one character per step
steps = ";".join(f"{i * CW:.1f}" for i in range(len(CMD) + 1))
times = ";".join(f"{i / len(CMD):.3f}" for i in range(len(CMD) + 1))
if STATIC:
    out.append(f'<clipPath id="t"><rect x="{x_cmd}" y="{y0 - FONT - 2}" width="{len(CMD) * CW:.1f}" height="{LH}"/></clipPath>')
else:
    out.append(
        f'<clipPath id="t"><rect x="{x_cmd}" y="{y0 - FONT - 2}" width="0" height="{LH}">'
        f'<animate attributeName="width" values="{steps}" keyTimes="{times}" calcMode="discrete" '
        f'begin="{TYPE_START}s" dur="{TYPE_STEP * len(CMD):.2f}s" fill="freeze"/></rect></clipPath>'
    )
out.append(f'<text x="{PAD}" y="{y0}" class="p">{escape(PROMPT)}</text>')
out.append(f'<text x="{x_cmd}" y="{y0}" class="c" clip-path="url(#t)">{escape(CMD)}</text>')

for i, (k, v) in enumerate(ROWS):
    y = y0 + LH * (i + 1) + 6
    delay = "" if STATIC else f' style="animation-delay:{type_end + 0.25 + i * 0.18:.2f}s"'
    out.append(
        f'<text class="o" x="{PAD}" y="{y}"{delay}><tspan class="k">{escape(k)}</tspan>'
        f'<tspan class="v" x="{PAD + 11 * CW:.1f}">{escape(v)}</tspan></text>'
    )

# new prompt + blinking block cursor
y_last = y0 + LH * (len(ROWS) + 1) + 12
last_delay = type_end + 0.25 + len(ROWS) * 0.18
delay = "" if STATIC else f' style="animation-delay:{last_delay:.2f}s"'
out.append(f'<text class="o p" x="{PAD}" y="{y_last}"{delay}>{escape(PROMPT)}</text>')
cx = PAD + len(PROMPT) * CW
if STATIC:
    cursor_attrs, blink = "", ""
else:
    cursor_attrs = ' opacity="0"'
    blink = (
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" '
        f'begin="{last_delay:.2f}s" repeatCount="indefinite"/>'
    )
out.append(
    f'<rect x="{cx:.1f}" y="{y_last - FONT + 1}" width="{CW:.1f}" height="{FONT + 2}" fill="#39d353"{cursor_attrs}>{blink}</rect>'
)
out.append("</svg>")
(ROOT / "now.svg").write_text("\n".join(out))
print("wrote now.svg", W, "x", H)
