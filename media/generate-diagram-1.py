#!/usr/bin/env python3
"""Generate diagram-1-hardware-os-stack.svg.

Usage
-----
  python generate-diagram-1.py                    # light theme, with background
  python generate-diagram-1.py --theme dark       # dark theme
  python generate-diagram-1.py --theme bw         # black-and-white for print
  python generate-diagram-1.py --no-background    # transparent background
  python generate-diagram-1.py --all              # write all four variants
  python generate-diagram-1.py --output foo.svg   # custom output path
"""

import argparse
import os

# ── Layer data ────────────────────────────────────────────────────────────────
# Index 0 = Layer 1 (foundation). Order here is bottom → top.

LAYERS = [
    {
        "num": 1,
        "name": "Program Truth",
        "keywords": "Requirements · Limits · Ownership · Evidence",
        "chapters": "1, 2, 4, 5, 9, 10",
    },
    {
        "num": 2,
        "name": "Decision Discipline",
        "keywords": "DRI · Gates · Risk rows · Escalation triggers",
        "chapters": "3, 4, 6, 7, 11, 14",
    },
    {
        "num": 3,
        "name": "Execution Evidence",
        "keywords": "Supplier data · Factory · Test · Fleet",
        "chapters": "12, 13, 16, 17",
    },
    {
        "num": 4,
        "name": "Forecast You Can Defend",
        "keywords": "Schedule · Cross-tier contracts · One-page truth",
        "chapters": "6, 8, 15",
    },
    {
        "num": 5,
        "name": "Installation and Durability",
        "keywords": "Rollout · Cadence · Failure recovery",
        "chapters": "18, 19, 20",
    },
]

# ── Themes ────────────────────────────────────────────────────────────────────
# bars: list of 5 dicts, index 0 = Layer 1. Each dict:
#   fill   bar background
#   text   primary text (name, number)
#   muted  keywords
#   ch     chapter numbers

THEMES = {
    "light": {
        "bg": "#FFFFFF",
        "arrow": "#4D91CC",
        "title": "#162447",
        "subtitle": "#4D6A8A",
        "bars": [
            {"fill": "#162447", "text": "#FFFFFF", "muted": "#8BAAC8", "ch": "#A8C8E8"},
            {"fill": "#1F4287", "text": "#FFFFFF", "muted": "#90B8DC", "ch": "#B8D4EE"},
            {"fill": "#2E6BB0", "text": "#FFFFFF", "muted": "#A8D0EE", "ch": "#C8E4FA"},
            {"fill": "#4D91CC", "text": "#162447", "muted": "#1A3460", "ch": "#162447"},
            {"fill": "#85BAE0", "text": "#162447", "muted": "#2A4A6E", "ch": "#162447"},
        ],
    },
    "dark": {
        "bg": "#0D1520",
        "arrow": "#6AAAD8",
        "title": "#D8E8F5",
        "subtitle": "#7A9AB8",
        "bars": [
            {"fill": "#0A1628", "text": "#D8E8F5", "muted": "#4A6A8A", "ch": "#6A8AAA"},
            {"fill": "#162447", "text": "#D8E8F5", "muted": "#5A7A9A", "ch": "#7A9AB8"},
            {"fill": "#1F4287", "text": "#D8E8F5", "muted": "#7A9AB8", "ch": "#9AB8D4"},
            {"fill": "#2E6BB0", "text": "#FFFFFF", "muted": "#A0C8E8", "ch": "#C0E0FA"},
            {"fill": "#4D91CC", "text": "#162447", "muted": "#1A3460", "ch": "#162447"},  # dark-text flip: CR 4.5
        ],
    },
    "bw": {
        "bg": "#FFFFFF",
        "arrow": "#555555",
        "title": "#111111",
        "subtitle": "#555555",
        "bars": [
            {"fill": "#111111", "text": "#FFFFFF", "muted": "#888888", "ch": "#AAAAAA"},
            {"fill": "#333333", "text": "#FFFFFF", "muted": "#999999", "ch": "#BBBBBB"},
            {"fill": "#555555", "text": "#FFFFFF", "muted": "#BBBBBB", "ch": "#CCCCCC"},
            {"fill": "#878787", "text": "#111111", "muted": "#222222", "ch": "#111111"},
            {"fill": "#BBBBBB", "text": "#111111", "muted": "#444444", "ch": "#222222"},
        ],
    },
}

# ── Layout constants (viewBox units) ─────────────────────────────────────────

WIDTH      = 680
PAD_TOP    = 22
PAD_BOT    = 20
ARROW_W    = 32   # left margin for the "builds on" arrow
NUM_ZONE_W = 54   # width of the layer-number column
SEP_X      = ARROW_W + NUM_ZONE_W          # x of the thin vertical separator
CONTENT_X  = SEP_X + 18                    # x where name + keywords start
CH_X       = WIDTH - 18                    # right edge for chapter numbers

# Title block above the bars
TITLE_Y    = PAD_TOP + 18    # title text baseline (cap top = PAD_TOP)
SUBTITLE_Y = TITLE_Y + 26    # subtitle baseline (8px gap + 18px cap)
BARS_TOP   = SUBTITLE_Y + 20 # y of first bar (gap after subtitle)

# Bar dimensions
BAR_H   = 78
BAR_GAP = 5

# Vertical offsets inside each bar.
# Name (18px, cap≈13px) + 10px gap + keywords (15px, cap≈11px) → block ≈ 34px.
_BLOCK_PAD = (BAR_H - 34) // 2   # ≈ 22px top/bottom breathing room
NAME_DY    = _BLOCK_PAD + 13     # name baseline from bar top       (≈ 35px)
KW_DY      = NAME_DY + 10 + 11  # keywords baseline from bar top   (≈ 56px)
NUM_DY     = BAR_H // 2          # number y centre (dominant-baseline:central)

HEIGHT = BARS_TOP + 5 * BAR_H + 4 * BAR_GAP + PAD_BOT

FONT = "'Helvetica Neue', 'Arial', sans-serif"


# ── SVG builder ───────────────────────────────────────────────────────────────

def generate_svg(theme_name: str = "light", transparent_bg: bool = False) -> str:
    t = THEMES[theme_name]
    out: list[str] = []

    def w(s: str) -> None:
        out.append(s)

    w(f'<svg xmlns="http://www.w3.org/2000/svg"')
    w(f'     viewBox="0 0 {WIDTH} {HEIGHT}"')
    w(f'     width="{WIDTH}" height="{HEIGHT}"')
    w( '     role="img"')
    w( '     aria-label="Hardware OS Stack — five layers from Program Truth'
       ' at the foundation to Installation and Durability at the top">')

    if not transparent_bg:
        w(f'  <rect width="{WIDTH}" height="{HEIGHT}" fill="{t["bg"]}"/>')

    # Title and subtitle
    w(f'  <text x="{ARROW_W}" y="{TITLE_Y}"'
      f' font-family="{FONT}" font-size="22" font-weight="700"'
      f' fill="{t["title"]}">Hardware OS Stack</text>')
    w(f'  <text x="{ARROW_W}" y="{SUBTITLE_Y}"'
      f' font-family="{FONT}" font-size="14" font-weight="400"'
      f' fill="{t["subtitle"]}">Five operating layers — each built on those below</text>')

    # Draw layers from the top of the image (Layer 5) to the bottom (Layer 1).
    for pos, layer in enumerate(reversed(LAYERS)):
        c = t["bars"][layer["num"] - 1]
        y = BARS_TOP + pos * (BAR_H + BAR_GAP)
        cx_num = ARROW_W + NUM_ZONE_W // 2

        # Bar background
        w(f'  <rect x="{ARROW_W}" y="{y}" width="{WIDTH - ARROW_W}" height="{BAR_H}"'
          f' fill="{c["fill"]}" rx="3"/>')

        # Layer number — vertically centered, bold
        w(f'  <text x="{cx_num}" y="{y + NUM_DY}"'
          f' font-family="{FONT}" font-size="22" font-weight="700"'
          f' fill="{c["text"]}" text-anchor="middle"'
          f' dominant-baseline="central">{layer["num"]}</text>')

        # Thin vertical separator
        w(f'  <line x1="{SEP_X}" y1="{y + 10}" x2="{SEP_X}" y2="{y + BAR_H - 10}"'
          f' stroke="{c["text"]}" stroke-opacity="0.20" stroke-width="1"/>')

        # Layer name (first line)
        w(f'  <text x="{CONTENT_X}" y="{y + NAME_DY}"'
          f' font-family="{FONT}" font-size="18" font-weight="700"'
          f' fill="{c["text"]}">{layer["name"]}</text>')

        # Chapter numbers — right-aligned, same baseline as name
        w(f'  <text x="{CH_X}" y="{y + NAME_DY}"'
          f' font-family="{FONT}" font-size="13" font-weight="400"'
          f' fill="{c["ch"]}" text-anchor="end">Ch. {layer["chapters"]}</text>')

        # Keywords (second line)
        w(f'  <text x="{CONTENT_X}" y="{y + KW_DY}"'
          f' font-family="{FONT}" font-size="15" font-weight="400"'
          f' fill="{c["muted"]}">{layer["keywords"]}</text>')

    # "builds on" upward arrow — spans the full bar section only
    ax    = ARROW_W // 2
    a_top = BARS_TOP + 4
    a_bot = BARS_TOP + 5 * BAR_H + 4 * BAR_GAP - 4
    ac    = t["arrow"]

    w(f'  <polygon points="{ax},{a_top} {ax - 5},{a_top + 10} {ax + 5},{a_top + 10}"'
      f' fill="{ac}" fill-opacity="0.55"/>')
    w(f'  <line x1="{ax}" y1="{a_top + 10}" x2="{ax}" y2="{a_bot}"'
      f' stroke="{ac}" stroke-opacity="0.55" stroke-width="1.5"/>')

    w('</svg>')
    return '\n'.join(out)


# ── CLI ───────────────────────────────────────────────────────────────────────

DEFAULT_OUT = os.path.join(os.path.dirname(__file__), "diagram-1-hardware-os-stack.svg")

VARIANTS = [
    ("light", False, "diagram-1-hardware-os-stack.svg"),
    ("dark",  False, "diagram-1-hardware-os-stack-dark.svg"),
    ("bw",    False, "diagram-1-hardware-os-stack-bw.svg"),
    ("light", True,  "diagram-1-hardware-os-stack-nobg.svg"),
]


def write_svg(path: str, svg: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  written: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Hardware OS Stack diagram (diagram-1) as SVG."
    )
    parser.add_argument(
        "--theme", choices=list(THEMES.keys()), default="light",
        help="Colour theme (default: light)",
    )
    parser.add_argument(
        "--no-background", action="store_true",
        help="Omit background rectangle (transparent)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Write all four variants (light, dark, bw, nobg) to the script directory",
    )
    parser.add_argument(
        "--output", default=None,
        help=f"Output file path (default: {DEFAULT_OUT})",
    )
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    if args.all:
        print("Generating all variants:")
        for theme, nobg, filename in VARIANTS:
            write_svg(os.path.join(base_dir, filename), generate_svg(theme, nobg))
    else:
        out_path = args.output or DEFAULT_OUT
        write_svg(out_path, generate_svg(args.theme, getattr(args, "no_background")))


if __name__ == "__main__":
    main()
