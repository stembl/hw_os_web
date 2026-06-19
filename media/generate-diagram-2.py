#!/usr/bin/env python3
"""Generate diagram-2-dri-decision-flow.svg.

Goals (from methodology):
  A (40%) Show five duties as sequential, numbered steps.
  B (40%) Show escalation branch when criteria not met — the unique content.
  C (20%) Show two terminal outcomes: decision closed vs. escalated.

Usage
-----
  python generate-diagram-2.py                    # light theme
  python generate-diagram-2.py --theme dark
  python generate-diagram-2.py --theme bw
  python generate-diagram-2.py --no-background
  python generate-diagram-2.py --all
"""

import argparse
import math
import os

# ── Content ───────────────────────────────────────────────────────────────────

TITLE    = "DRI Decision Flow"
SUBTITLE = "Five duties — with escalation when criteria are not met"

# Two-element tuples: (line1, line2_or_None)
DUTIES = [
    ("1. Frame the decision question",    None),
    ("2. Collect required inputs",         None),
    ("3. Propose a decision by date",      None),
    ("4. Record outcome and rationale",    None),
    ("5. Push updates into",               "   dependent artifacts"),
]

DIAMOND_LABEL = "Criteria met?"
ESC_LABEL     = "Escalate to lead"
CLOSED_LABEL  = "Decision closed"

# ── Themes ────────────────────────────────────────────────────────────────────

THEMES = {
    "light": {
        "bg":           "#FFFFFF",
        "title":        "#162447",
        "subtitle":     "#4D6A8A",
        "duty_fill":    "#1F4287",
        "duty_text":    "#FFFFFF",
        "diamond_fill": "#2E6BB0",
        "diamond_text": "#FFFFFF",
        "esc_fill":     "#4A5568",
        "esc_text":     "#FFFFFF",
        "closed_fill":  "#162447",
        "closed_text":  "#FFFFFF",
        "arrow":        "#2E6BB0",
        "yes_no":       "#2E4A6E",
    },
    "dark": {
        "bg":           "#0D1520",
        "title":        "#D8E8F5",
        "subtitle":     "#7A9AB8",
        "duty_fill":    "#162447",
        "duty_text":    "#D8E8F5",
        "diamond_fill": "#1F4287",
        "diamond_text": "#D8E8F5",
        "esc_fill":     "#2D3748",
        "esc_text":     "#D8E8F5",
        "closed_fill":  "#0A1628",
        "closed_text":  "#D8E8F5",
        "arrow":        "#4D91CC",
        "yes_no":       "#7A9AB8",
    },
    "bw": {
        "bg":           "#FFFFFF",
        "title":        "#111111",
        "subtitle":     "#444444",
        "duty_fill":    "#222222",
        "duty_text":    "#FFFFFF",
        "diamond_fill": "#555555",
        "diamond_text": "#FFFFFF",
        "esc_fill":     "#555555",
        "esc_text":     "#FFFFFF",
        "closed_fill":  "#111111",
        "closed_text":  "#FFFFFF",
        "arrow":        "#333333",
        "yes_no":       "#333333",
    },
}

# ── Layout ────────────────────────────────────────────────────────────────────

WIDTH     = 680
BOX_W     = 300
BOX_H     = 60
BOX_CX    = 255          # centre x of the main column
BOX_LEFT  = BOX_CX - BOX_W // 2
ARROW_GAP = 26           # vertical gap between elements (room for arrow)

DIA_HW    = 68           # diamond half-width
DIA_HH    = 32           # diamond half-height

ESC_X     = BOX_LEFT + BOX_W + 30   # left edge of escalation box
ESC_W     = 180
ESC_H     = BOX_H
ESC_CX    = ESC_X + ESC_W // 2

PAD_TOP   = 22
TITLE_Y   = PAD_TOP + 18          # = 40  title baseline
SUBTITLE_Y = TITLE_Y + 24         # = 64  subtitle baseline
FIRST_Y   = SUBTITLE_Y + 22       # = 86  top of first duty box

FONT = "'Helvetica Neue', 'Arial', sans-serif"

# Compute y positions for each element.
def layout():
    y = FIRST_Y
    positions = []
    for i, (line1, line2) in enumerate(DUTIES):
        positions.append(("box", y, i))
        y += BOX_H
        if i < 2:                    # arrow to next duty box
            positions.append(("arrow_down", y, y + ARROW_GAP))
            y += ARROW_GAP
        elif i == 2:                 # arrow to diamond
            positions.append(("arrow_down", y, y + ARROW_GAP))
            y += ARROW_GAP
            # diamond
            positions.append(("diamond", y))
            y += DIA_HH * 2
            # YES arrow down
            positions.append(("arrow_yes", y, y + ARROW_GAP))
            y += ARROW_GAP
        elif i == 3:                 # arrow between box 4 and box 5
            positions.append(("arrow_down", y, y + ARROW_GAP))
            y += ARROW_GAP
    # closed indicator
    y += ARROW_GAP
    positions.append(("closed", y))
    y += BOX_H
    return positions, y + PAD_TOP


# ── SVG helpers ───────────────────────────────────────────────────────────────

def arrow_down(out, cx, y1, y2, color):
    AH = 7
    shaft_y2 = y2 - AH
    out.append(f'  <line x1="{cx}" y1="{y1}" x2="{cx}" y2="{shaft_y2}"'
               f' stroke="{color}" stroke-width="1.5"/>')
    out.append(f'  <polygon points="{cx},{y2} {cx-AH*.55:.1f},{y2-AH}'
               f' {cx+AH*.55:.1f},{y2-AH}" fill="{color}"/>')


def arrow_right(out, x1, x2, cy, color, dashed=False):
    AH = 7
    shaft_x2 = x2 - AH
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    out.append(f'  <line x1="{x1}" y1="{cy}" x2="{shaft_x2}" y2="{cy}"'
               f' stroke="{color}" stroke-width="1.5"{dash}/>')
    out.append(f'  <polygon points="{x2},{cy} {x2-AH},{cy-AH*.55:.1f}'
               f' {x2-AH},{cy+AH*.55:.1f}" fill="{color}"/>')


def box_rect(out, x, y, w, h, fill):
    out.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}"'
               f' fill="{fill}" rx="4"/>')


def centred_text(out, cx, cy, text, size, weight, color, dy_extra=0):
    out.append(f'  <text x="{cx}" y="{cy + dy_extra}"'
               f' font-family="{FONT}" font-size="{size}" font-weight="{weight}"'
               f' fill="{color}" text-anchor="middle"'
               f' dominant-baseline="central">{text}</text>')


# ── SVG builder ───────────────────────────────────────────────────────────────

def generate_svg(theme_name="light", transparent_bg=False):
    t = THEMES[theme_name]
    positions, height = layout()

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg"')
    out.append(f'     viewBox="0 0 {WIDTH} {height}"')
    out.append(f'     width="{WIDTH}" height="{height}"')
    out.append( '     role="img"')
    out.append(f'     aria-label="{TITLE} — {SUBTITLE}">')

    if not transparent_bg:
        out.append(f'  <rect width="{WIDTH}" height="{height}" fill="{t["bg"]}"/>')

    # Title and subtitle
    out.append(f'  <text x="{BOX_LEFT}" y="{TITLE_Y}"'
               f' font-family="{FONT}" font-size="22" font-weight="700"'
               f' fill="{t["title"]}">{TITLE}</text>')
    out.append(f'  <text x="{BOX_LEFT}" y="{SUBTITLE_Y}"'
               f' font-family="{FONT}" font-size="14" font-weight="400"'
               f' fill="{t["subtitle"]}">{SUBTITLE}</text>')

    dia_cy = None

    for item in positions:
        kind = item[0]

        if kind == "box":
            _, y, duty_idx = item
            line1, line2 = DUTIES[duty_idx]
            box_rect(out, BOX_LEFT, y, BOX_W, BOX_H, t["duty_fill"])
            if line2:
                centred_text(out, BOX_CX, y + BOX_H // 2, line1,
                             13, "700", t["duty_text"], dy_extra=-8)
                centred_text(out, BOX_CX, y + BOX_H // 2, line2,
                             13, "400", t["duty_text"], dy_extra=10)
            else:
                centred_text(out, BOX_CX, y + BOX_H // 2, line1,
                             14, "700", t["duty_text"])

        elif kind == "arrow_down":
            _, y1, y2 = item
            arrow_down(out, BOX_CX, y1, y2, t["arrow"])

        elif kind == "diamond":
            _, y = item
            dia_cy = y + DIA_HH
            pts = (f"{BOX_CX},{y} {BOX_CX+DIA_HW},{dia_cy} "
                   f"{BOX_CX},{y+DIA_HH*2} {BOX_CX-DIA_HW},{dia_cy}")
            out.append(f'  <polygon points="{pts}" fill="{t["diamond_fill"]}" stroke="none"/>')
            centred_text(out, BOX_CX, dia_cy, DIAMOND_LABEL,
                         13, "700", t["diamond_text"])
            # NO label + horizontal arrow to escalation box
            no_y = dia_cy
            # Arrow from diamond right vertex to ESC box
            arrow_right(out, BOX_CX + DIA_HW, ESC_X, no_y, t["arrow"])
            # NO label above arrow
            mid_no_x = (BOX_CX + DIA_HW + ESC_X) // 2
            out.append(f'  <text x="{mid_no_x}" y="{no_y - 6}"'
                       f' font-family="{FONT}" font-size="11" font-weight="700"'
                       f' fill="{t["yes_no"]}" text-anchor="middle">NO</text>')
            # Escalation box
            esc_y = no_y - ESC_H // 2
            box_rect(out, ESC_X, esc_y, ESC_W, ESC_H, t["esc_fill"])
            centred_text(out, ESC_CX, no_y, ESC_LABEL, 13, "700", t["esc_text"])

        elif kind == "arrow_yes":
            _, y1, y2 = item
            arrow_down(out, BOX_CX, y1, y2, t["arrow"])
            # YES label
            out.append(f'  <text x="{BOX_CX + 8}" y="{(y1+y2)//2}"'
                       f' font-family="{FONT}" font-size="11" font-weight="700"'
                       f' fill="{t["yes_no"]}" dominant-baseline="central">YES</text>')

        elif kind == "closed":
            _, y = item
            box_rect(out, BOX_LEFT, y, BOX_W, BOX_H, t["closed_fill"])
            centred_text(out, BOX_CX, y + BOX_H // 2, CLOSED_LABEL,
                         14, "700", t["closed_text"])
            # Final arrow into closed box
            arrow_down(out, BOX_CX, y - ARROW_GAP, y, t["arrow"])

    out.append('</svg>')
    return '\n'.join(out)


# ── CLI ───────────────────────────────────────────────────────────────────────

VARIANTS = [
    ("light", False, "diagram-2-dri-decision-flow.svg"),
    ("dark",  False, "diagram-2-dri-decision-flow-dark.svg"),
    ("bw",    False, "diagram-2-dri-decision-flow-bw.svg"),
    ("light", True,  "diagram-2-dri-decision-flow-nobg.svg"),
]


def write_svg(path, svg):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  written: {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate DRI Decision Flow diagram.")
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
        out = args.output or os.path.join(base, "diagram-2-dri-decision-flow.svg")
        write_svg(out, generate_svg(args.theme, getattr(args, "no_background")))


if __name__ == "__main__":
    main()
