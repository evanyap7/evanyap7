"""Hand-authored neofetch-style card -> info-card.svg. STATIC=1 freezes the animation for previews."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"

# (label, value) ; label None = blank spacer
LINES = [
    ("title", "evan@github"),
    ("rule", "-" * 38),
    ("Who", "Evan Yap · Singapore"),
    ("Uni", "SUTD · ESD + MSc Tech Entrepreneurship"),
    ("Now", "AI Business Consultant intern @ Univers"),
    ("Prev", "Founder, EvanYapFitness (2.2k followers)"),
    (None, None),
    ("hdr", "Stack"),
    ("Langs", "Python · TypeScript · JavaScript · C++ · SQL"),
    ("Web", "Next.js · React · Node · Three.js · Vercel"),
    ("AI", "Vercel AI SDK · Gemini · Groq · Zod · Pub/Sub"),
    (None, None),
    ("hdr", "Highlights"),
    ("Win", "Top 5 · Univers website revamp (live CEO pitch)"),
    ("Built", "Telegram AI assistant · 24 intents · 100% eval"),
    ("Built", "ESG audit agent · -3h research per facility"),
    ("Scholar", "SUTD Tech Entrepreneurship Programme"),
    (None, None),
    ("hdr", "Off-duty"),
    ("Train", "HYROX · powerlifting"),
    ("Play", "guitar · floorball captain · coffee"),
]

LINE_H, X_LABEL, X_VAL = 17, 16, 90
W = 500
H = 24 + len(LINES) * LINE_H + 16
out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12">',
    "<style>",
    ".l{opacity:1}" if STATIC else ".l{opacity:0;animation:in .4s ease-out forwards}",
    "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}",
    ".t{fill:#39d353;font-weight:bold}.k{fill:#58a6ff;font-weight:bold}.v{fill:#c9d1d9}.r{fill:#484f58}.h{fill:#39d353}",
    "</style>",
    '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
]
for i, (label, value) in enumerate(LINES):
    y = 28 + i * LINE_H
    delay = "" if STATIC else f' style="animation-delay:{0.4 + i * 0.12:.2f}s"'
    if label is None:
        continue
    if label == "title":
        out.append(f'<text class="l t" x="{X_LABEL}" y="{y}"{delay}>{escape(value)}</text>')
    elif label == "rule":
        out.append(f'<text class="l r" x="{X_LABEL}" y="{y}"{delay}>{value}</text>')
    elif label == "hdr":
        out.append(f'<text class="l h" x="{X_LABEL}" y="{y}"{delay}>▌{escape(value)}</text>')
    else:
        out.append(
            f'<text class="l" x="{X_LABEL}" y="{y}"{delay}><tspan class="k">{escape(label)}</tspan>'
            f'<tspan class="v" x="{X_VAL}">{escape(value)}</tspan></text>'
        )
out.append("</svg>")
(ROOT / "info-card.svg").write_text("\n".join(out))
print("wrote info-card.svg", W, "x", H)
