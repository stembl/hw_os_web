#!/usr/bin/env python3
"""Generate diagram-3-requirements-lifecycle-arc.svg.

Goals (from methodology):
  A (40%) Show four states as a cycle — Bless→Evidence→Revise repeats.
  B (30%) Show transition triggers between states.
  C (30%) Show "Frozen but Wrong" dead-end — the broken loop path.

Usage
-----
  python generate-diagram-3.py                    # light theme
  python generate-diagram-3.py --theme dark
  python generate-diagram-3.py --theme bw
  python generate-diagram-3.py --no-background
  python generate-diagram-3.py --all
"""

import argparse
import os

# ── Content ───────────────────────────────────────────────────────────────────

TITLE    = "Requirements Lifecycle Arc"
SUBTITLE = "Four states in a controlled cycle \u2014 \u201cFrozen but Wrong\u201d when the loop breaks"

STATES = ["Hypothesis", "Bless", "Evidence", "Revise"]

# Short labels in the 40px gaps (centred above each arrow)
TRANSITIONS = ["Sign-off", "Data attached", "Threshold"]

LOOP_LABEL = "Revision complete"
FBW_NAME   = "Frozen but Wrong"
FBW_DESC   = "Revision blocked \u2014 stays wrong"
FBW_BREAK  = "Loop broken"        # label on dashed arrow

# ── Themes ────────────────────────────────────────────────────────────────────

THEMES = {
    "light": {
        "bg":         "#FFFFFF",
        "title":      "#162447",
        "subtitle":   "#4D6A8A",
        "state_fill": "#1F4287",
        "state_text": "#FFFFFF",
        "fbw_fill":   "#7B2020",
        "fbw_text":   "#FFFFFF",
        "fbw_muted":  "#F0AEAE",
        "arrow":      "#2E6BB0",
        "loop_arrow": "#4D91CC",
        "fbw_arrow":  "#C05050",
        "trigger":    "#2E4A6E",
        "loop_label": "#2E6BB0",
        "fbw_label":  "#C05050",
    },
    "dark": {
        "bg":         "#0D1520",
        "title":      "#D8E8F5",
        "subtitle":   "#7A9AB8",
        "state_fill": "#162447",
        "state_text": "#D8E8F5",
        "fbw_fill":   "#5C1A1A",
        "fbw_text":   "#F5D0D0",
        "fbw_muted":  "#F0AEAE",
        "arrow":      "#4D91CC",
        "loop_arrow": "#6AAAD8",
        "fbw_arrow":  "#E08080",
        "trigger":    "#7A9AB8",
        "loop_label": "#4D91CC",
        "fbw_label":  "#E08080",
    },
    "bw": {
        "bg":         "#FFFFFF",
        "title":      "#111111",
        "subtitle":   "#444444",
        "state_fill": "#222222",
        "state_text": "#FFFFFF",
        "fbw_fill":   "#444444",
        "fbw_text":   "#FFFFFF",
        "fbw_muted":  "#CCCCCC",
        "arrow":      "#333333",
        "loop_arrow": "#555555",
        "fbw_arrow":  "#555555",
        "trigger":    "#444444",
        "loop_label": "#555555",
        "fbw_label":  "#555555",
    },
}

# ── Layout (all values in viewBox px) ────────────────────────────────────────
#
# Horizontal row of 4 state boxes. 40px gaps between boxes give room
# for transition arrows + short labels above them.
#
# Overlap analysis (verified before coding):
#   - Transition labels: placed at y=LABEL_Y which is ABOVE state row top.
#   - FBW dashed arrow: starts at STATE_BOT (not STATE_CY), no box conflict.
#   - Loop-back right arm: goes to x=LOOP_ARM_X which is right of FBW right edge.
#   - Loop-back horizontal: runs at LOOP_Y which is below FBW bottom.

WIDTH      = 740
PAD_H      = 20          # horizontal padding each side
PAD_TOP    = 22
PAD_BOT    = 22

TITLE_Y    = PAD_TOP + 18    # = 40
SUBTITLE_Y = TITLE_Y + 24   # = 64

# Transition labels sit above the state row
LABEL_Y    = SUBTITLE_Y + 20  # = 84  (label baselines)

# State boxes start 18px below labels
STATE_W    = 130
STATE_H    = 64
STATE_GAP  = 40             # gap between boxes — holds arrow + short label
STATES_Y   = LABEL_Y + 18  # = 102

# Derived state geometry
STATE_CY   = STATES_Y + STATE_H // 2   # = 134  vertical centre
STATE_BOT  = STATES_Y + STATE_H         # = 166

TOTAL_ROW_W = 4 * STATE_W + 3 * STATE_GAP   # = 520 + 120 = 640
ROW_LEFT    = (WIDTH - TOTAL_ROW_W) // 2    # = 20

def state_left(i):  return ROW_LEFT + i * (STATE_W + STATE_GAP)
def state_cx(i):    return state_left(i) + STATE_W // 2
def gap_cx(i):      return state_left(i) + STATE_W + STATE_GAP // 2  # centre of gap i→i+1

# FBW dead-end: hangs below the E→R gap
E_RIGHT        = state_left(2) + STATE_W     # = 20 + 2*170 + 130 = 490
R_LEFT         = state_left(3)               # = 20 + 3*170 = 530
FBW_BRANCH_X   = (E_RIGHT + R_LEFT) // 2    # = 510  midpoint of E→R gap
FBW_W          = 220
FBW_H          = 64
FBW_X          = FBW_BRANCH_X - FBW_W // 2  # = 400
FBW_BOT_X      = FBW_X + FBW_W              # = 620
FBW_Y          = STATE_BOT + 34             # = 200  (34px gap → room for arrow)
FBW_BOT        = FBW_Y + FBW_H             # = 264
FBW_CX         = FBW_BRANCH_X              # = 510
FBW_CY         = FBW_Y + FBW_H // 2       # = 232

# Loop-back: R → Bless (U-shape below FBW)
#   Right arm goes to LOOP_ARM_X which must be:
#     (a) > R box right edge (= ROW_LEFT + 4*STATE_W + 3*STATE_GAP = 660)
#     (b) > FBW right edge (= 620)
#     (c) within SVG width (680)
R_RIGHT     = state_left(3) + STATE_W     # = 660  right edge of Revise
LOOP_ARM_X  = R_RIGHT + 14               # = 704  clears both Revise (690) and FBW right (650)
R_CX        = state_cx(3)                 # = 595  (used for FBW branch calc only)
B_CX        = state_cx(1)                 # = 255
LOOP_Y      = FBW_BOT + 28               # = 292  below FBW bottom (264)

# Total SVG height
HEIGHT = LOOP_Y + 30 + PAD_BOT            # = 364

FONT = "'Helvetica Neue', 'Arial', sans-serif"


# ── SVG helpers ───────────────────────────────────────────────────────────────

def arrow_right(out, x1, x2, cy, color, dashed=False):
    AH = 7
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    out.append(f'  <line x1="{x1}" y1="{cy}" x2="{x2 - AH}" y2="{cy}"'
               f' stroke="{color}" stroke-width="1.5"{dash}/>')
    out.append(f'  <polygon points="{x2},{cy} {x2-AH},{cy-AH*.55:.1f}'
               f' {x2-AH},{cy+AH*.55:.1f}" fill="{color}"/>')


def arrow_down(out, cx, y1, y2, color, dashed=False):
    AH = 7
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    out.append(f'  <line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2 - AH}"'
               f' stroke="{color}" stroke-width="1.5"{dash}/>')
    out.append(f'  <polygon points="{cx},{y2} {cx-AH*.55:.1f},{y2-AH}'
               f' {cx+AH*.55:.1f},{y2-AH}" fill="{color}"/>')


def arrow_up(out, cx, y_from, y_to, color):
    """Upward arrow: line from y_from down to y_to (y_to < y_from)."""
    AH = 7
    out.append(f'  <line x1="{cx}" y1="{y_from}" x2="{cx}" y2="{y_to + AH}"'
               f' stroke="{color}" stroke-width="1.5"/>')
    out.append(f'  <polygon points="{cx},{y_to} {cx-AH*.55:.1f},{y_to+AH}'
               f' {cx+AH*.55:.1f},{y_to+AH}" fill="{color}"/>')


def plain_line(out, x1, y1, x2, y2, color):
    out.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"'
               f' stroke="{color}" stroke-width="1.5"/>')


def centred(out, cx, cy, text, size, weight, color):
    out.append(f'  <text x="{cx}" y="{cy}" font-family="{FONT}"'
               f' font-size="{size}" font-weight="{weight}" fill="{color}"'
               f' text-anchor="middle" dominant-baseline="central">{text}</text>')


# ── SVG builder ───────────────────────────────────────────────────────────────

def generate_svg(theme_name="light", transparent_bg=False):
    t = THEMES[theme_name]
    out = []

    out.append(f'<svg xmlns="http://www.w3.org/2000/svg"')
    out.append(f'     viewBox="0 0 {WIDTH} {HEIGHT}"')
    out.append(f'     width="{WIDTH}" height="{HEIGHT}"')
    out.append( '     role="img"')
    out.append(f'     aria-label="{TITLE}">')

    if not transparent_bg:
        out.append(f'  <rect width="{WIDTH}" height="{HEIGHT}" fill="{t["bg"]}"/>')

    # Title + subtitle
    out.append(f'  <text x="{ROW_LEFT}" y="{TITLE_Y}" font-family="{FONT}"'
               f' font-size="22" font-weight="700" fill="{t["title"]}">{TITLE}</text>')
    out.append(f'  <text x="{ROW_LEFT}" y="{SUBTITLE_Y}" font-family="{FONT}"'
               f' font-size="14" font-weight="400" fill="{t["subtitle"]}">{SUBTITLE}</text>')

    # ── Transition labels (above state row, centred over each gap) ──
    for i, label in enumerate(TRANSITIONS):
        cx = gap_cx(i)
        out.append(f'  <text x="{cx}" y="{LABEL_Y}" font-family="{FONT}"'
                   f' font-size="10" font-weight="400" fill="{t["trigger"]}"'
                   f' text-anchor="middle" dominant-baseline="central">{label}</text>')

    # ── State boxes ──
    for i, name in enumerate(STATES):
        x = state_left(i)
        out.append(f'  <rect x="{x}" y="{STATES_Y}" width="{STATE_W}"'
                   f' height="{STATE_H}" fill="{t["state_fill"]}" rx="4"/>')
        centred(out, state_cx(i), STATE_CY, name, 16, "700", t["state_text"])

    # ── Entry arrow into Hypothesis ──
    entry_x = ROW_LEFT - 20
    arrow_right(out, entry_x, ROW_LEFT, STATE_CY, t["arrow"])

    # ── Forward transition arrows (through gaps) ──
    for i in range(3):
        x1 = state_left(i) + STATE_W   # right edge of state i
        x2 = state_left(i + 1)         # left edge of state i+1
        arrow_right(out, x1, x2, STATE_CY, t["arrow"])

    # ── FBW dead-end: dashed arrow from STATE_BOT down to FBW box ──
    arrow_down(out, FBW_BRANCH_X, STATE_BOT, FBW_Y, t["fbw_arrow"], dashed=True)
    # "Loop broken" label — right of dashed arrow
    out.append(f'  <text x="{FBW_BRANCH_X + 8}" y="{(STATE_BOT + FBW_Y) // 2}"'
               f' font-family="{FONT}" font-size="10" font-weight="400"'
               f' fill="{t["fbw_label"]}" dominant-baseline="central">{FBW_BREAK}</text>')

    # FBW box (dashed border)
    out.append(f'  <rect x="{FBW_X}" y="{FBW_Y}" width="{FBW_W}" height="{FBW_H}"'
               f' fill="{t["fbw_fill"]}" rx="4"'
               f' stroke="{t["fbw_arrow"]}" stroke-width="1.5" stroke-dasharray="6,4"/>')
    centred(out, FBW_CX, FBW_Y + 22, FBW_NAME, 14, "700", t["fbw_text"])
    centred(out, FBW_CX, FBW_Y + 44, FBW_DESC, 10, "400", t["fbw_muted"])

    # ── Loop-back: R → Bless (U-shape with right arm outside Revise box) ──
    # Path: R right edge → jog to LOOP_ARM_X → down to LOOP_Y
    #       → left to B_CX → up to B bottom (arrowhead)
    plain_line(out, R_RIGHT, STATE_BOT, LOOP_ARM_X, STATE_BOT, t["loop_arrow"])
    plain_line(out, LOOP_ARM_X, STATE_BOT, LOOP_ARM_X, LOOP_Y, t["loop_arrow"])
    plain_line(out, LOOP_ARM_X, LOOP_Y, B_CX, LOOP_Y, t["loop_arrow"])
    arrow_up(out, B_CX, LOOP_Y, STATE_BOT, t["loop_arrow"])

    # Loop label centred on the long horizontal segment
    loop_label_cx = (LOOP_ARM_X + B_CX) // 2
    out.append(f'  <text x="{loop_label_cx}" y="{LOOP_Y - 10}"'
               f' font-family="{FONT}" font-size="10" font-weight="400"'
               f' fill="{t["loop_label"]}" text-anchor="middle"'
               f' dominant-baseline="central">{LOOP_LABEL}</text>')

    out.append('</svg>')
    return '\n'.join(out)


# ── CLI ───────────────────────────────────────────────────────────────────────

VARIANTS = [
    ("light", False, "diagram-3-requirements-lifecycle-arc.svg"),
    ("dark",  False, "diagram-3-requirements-lifecycle-arc-dark.svg"),
    ("bw",    False, "diagram-3-requirements-lifecycle-arc-bw.svg"),
    ("light", True,  "diagram-3-requirements-lifecycle-arc-nobg.svg"),
]


def write_svg(path, svg):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  written: {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate Requirements Lifecycle Arc diagram.")
    parser.add_argument("--theme", choices=list(THEMES.keys()), default="light")
    parser.add_argument("--no-background", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    base = os.path.dirname(os.path.abspath(__file__))

    if args.all:
        print("Generating all variants:")
        for theme, nobg, fname in VARIANTS:
            write_svg(os.path.join(base, fname), generate_svg(theme, nobg))
    else:
        out = args.output or os.path.join(base, "diagram-3-requirements-lifecycle-arc.svg")
        write_svg(out, generate_svg(args.theme, getattr(args, "no_background")))


if __name__ == "__main__":
    main()
