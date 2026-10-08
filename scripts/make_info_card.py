"""Hand-authored neofetch-style card -> info-card.svg. STATIC=1 freezes the animation for previews."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"

PROMPT, CMD = "evan@github ~ $ ", "neofetch"

# ("kv", label, value) | ("hdr", title) | ("gap",) ; the "Now" row gets a pulsing status dot
LINES = [
    ("kv", "Name", "Evan Yap · Singapore"),
    ("kv", "Uni", "SUTD · ESD + MSc Tech Entrepreneurship"),
    ("kv", "Now", "AI Business Consultant intern @ Univers"),
    ("kv", "Prev", "Founder, EvanYapFitness (2.2k followers)"),
    ("gap",),
    ("hdr", "Stack"),
    ("kv", "Langs", "Python · TypeScript · JavaScript · C++ · SQL"),
    ("kv", "Web", "Next.js · React · Node · Three.js · Vercel"),
    ("kv", "AI", "Vercel AI SDK · Gemini · Groq · Zod · Pub/Sub"),
    ("gap",),
    ("hdr", "Highlights"),
    ("kv", "Won", "Top 5 · Univers website revamp (live CEO pitch)"),
    ("kv", "Agent", "ESG audit agent · -3h research per facility"),
    ("kv", "Bot", "Telegram AI assistant · 24 intents · 100% eval"),
    ("kv", "Scholar", "SUTD Tech Entrepreneurship Programme"),
    ("gap",),
    ("hdr", "Off-duty"),
    ("kv", "Train", "HYROX · powerlifting"),
    ("kv", "Play", "guitar · floorball captain · coffee"),
    ("gap",),
    ("swatch",),
]

W, LINE_H, X0, X_VAL, FONT, CW = 500, 18, 18, 96, 12, 7.2
SWATCH = ["#39d353", "#26a641", "#58a6ff", "#a371f7", "#f778ba", "#ffa657", "#e3b341", "#c9d1d9"]
H = 24 + (len(LINES) + 3) * LINE_H + 8
STEP = 0.1  # seconds per line fade-in

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FONT}">',
    "<style>",
    ".l{opacity:1}" if STATIC else ".l{opacity:0;animation:in .4s ease-out forwards}",
    "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}",
    ".p{fill:#39d353;font-weight:bold}.c{fill:#c9d1d9}.k{fill:#58a6ff;font-weight:bold}.v{fill:#c9d1d9}"
    ".h{fill:#39d353;font-weight:bold}.r{fill:#21262d}",
    "</style>",
    '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
]

# prompt line: command typed one character at a time
y = 30
x_cmd = X0 + len(PROMPT) * CW
n = len(CMD)
if STATIC:
    out.append(f'<clipPath id="t"><rect x="{x_cmd}" y="{y - FONT - 2}" width="{n * CW:.1f}" height="{LINE_H}"/></clipPath>')
else:
    vals = ";".join(f"{i * CW:.1f}" for i in range(n + 1))
    keys = ";".join(f"{i / n:.3f}" for i in range(n + 1))
    out.append(
        f'<clipPath id="t"><rect x="{x_cmd}" y="{y - FONT - 2}" width="0" height="{LINE_H}">'
        f'<animate attributeName="width" values="{vals}" keyTimes="{keys}" calcMode="discrete" '
        f'begin="0.3s" dur="{n * 0.08:.2f}s" fill="freeze"/></rect></clipPath>'
    )
out.append(f'<text class="p" x="{X0}" y="{y}">{escape(PROMPT)}</text>')
out.append(f'<text class="c" x="{x_cmd}" y="{y}" clip-path="url(#t)">{escape(CMD)}</text>')
t0 = 0.3 + n * 0.08 + 0.2

y += LINE_H + 4
for i, item in enumerate(LINES):
    delay = "" if STATIC else f' style="animation-delay:{t0 + i * STEP:.2f}s"'
    kind = item[0]
    if kind == "kv":
        label, value = item[1], item[2]
        if label == "Now":  # pulsing "live" dot
            pulse = (
                ""
                if STATIC
                else '<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/>'
            )
            out.append(f'<circle cx="{X0 - 9}" cy="{y - 4}" r="2.5" fill="#39d353">{pulse}</circle>')
        out.append(
            f'<text class="l" x="{X0}" y="{y}"{delay}><tspan class="k">{escape(label)}</tspan>'
            f'<tspan class="v" x="{X_VAL}">{escape(value)}</tspan></text>'
        )
    elif kind == "hdr":
        title = item[1]
        rule_x = X0 + (len(title) + 3) * CW
        out.append(f'<text class="l h" x="{X0}" y="{y}"{delay}>▌ {escape(title)}</text>')
        out.append(f'<rect class="l r" x="{rule_x:.1f}" y="{y - 4}" width="{W - X0 - rule_x:.1f}" height="1"{delay}/>')
    elif kind == "swatch":
        for j, c in enumerate(SWATCH):
            out.append(f'<rect class="l" x="{X0 + j * 20}" y="{y - 11}" width="16" height="12" rx="2" fill="{c}"{delay}/>')
    y += LINE_H

# trailing prompt with blinking cursor
last = t0 + len(LINES) * STEP
out.append(f'<text class="l p" x="{X0}" y="{y}"' + ("" if STATIC else f' style="animation-delay:{last:.2f}s"') + f">{escape(PROMPT)}</text>")
if STATIC:
    out.append(f'<rect x="{x_cmd}" y="{y - FONT + 1}" width="{CW}" height="{FONT + 2}" fill="#39d353"/>')
else:
    out.append(
        f'<rect x="{x_cmd}" y="{y - FONT + 1}" width="{CW}" height="{FONT + 2}" fill="#39d353" opacity="0">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" '
        f'begin="{last:.2f}s" repeatCount="indefinite"/></rect>'
    )
out.append("</svg>")
(ROOT / "info-card.svg").write_text("\n".join(out))
print("wrote info-card.svg", W, "x", H)
