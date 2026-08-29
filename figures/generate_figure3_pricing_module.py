#!/usr/bin/env python3
"""Generate "Figure 3. Pricing module" for the new IA (Criterion C).

Laid out by hand from the node/connection tables in
../figure3_pricing_module_spec.md.  Shape helpers are imported from the
Figure 1 generator so all three figures share the same visual style.

Run:  python3 generate_figure3_pricing_module.py
Writes figure3_pricing_module.svg and .png next to this script.
"""
import os
import shutil
import subprocess

from generate_figure1_main_flow import (Chart, top, bottom, right, spine,
                                        CHAR_W, LINE_H, PAD_X, PAD_Y)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def process2(c, title, subtitle, cx, cy):
    """Process box with an exact two-line "title / subtitle" label."""
    lines = [title, subtitle]
    tw = max(len(l) for l in lines) * CHAR_W
    th = len(lines) * LINE_H
    w, h = tw + 2 * PAD_X, th + 2 * PAD_Y
    c.shapes.append(
        f'<rect x="{cx - w/2:.1f}" y="{cy - h/2:.1f}" width="{w:.1f}" '
        f'height="{h:.1f}"/>')
    c._label_text(cx, cy, lines)
    return c._node(cx, cy, w, h)


def build_pricing():
    c = Chart(420, 620)
    cx = 200

    t_start = c.terminator("Pricing module", cx, 40)                     # N1
    p_pw = process2(c, "Compute wholesale",
                    "Pw = cost × 1.25 × 1.16", cx, 115)        # N2
    p_rw = process2(c, "Round wholesale",
                    "to next multiple of 5", cx, 195)                    # N3
    d_man = c.decision("Manual retail set?", cx, 285)                    # N4
    p_pr = process2(c, "Compute retail", "Pr = 1.15 × Pw", cx, 370) # N5
    p_rr = process2(c, "Round retail",
                    "to next multiple of 5", cx, 450)                    # N6
    t_ret = c.terminator("Return", cx, 555)                              # N7

    spine(c, t_start, p_pw)
    spine(c, p_pw, p_rw)
    spine(c, p_rw, d_man)
    c.arrow([bottom(d_man), top(p_pr)], "no", cx + 8, 330, "start")
    spine(c, p_pr, p_rr)
    spine(c, p_rr, t_ret)

    # yes branch: around the right of N5/N6, rejoining the spine above N7
    c.line([right(d_man), (360, d_man["cy"]), (360, 510), (cx, 510)])
    c.branch_label("yes", right(d_man)[0] + 14, d_man["cy"] - 12, "start")
    return c


if __name__ == "__main__":
    chart = build_pricing()
    svg_path = os.path.join(OUT_DIR, "figure3_pricing_module.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(chart.svg())
    print(f"figure3_pricing_module.svg  ({chart.w}x{chart.h})")

    if shutil.which("rsvg-convert"):
        png_path = os.path.join(OUT_DIR, "figure3_pricing_module.png")
        subprocess.run(["rsvg-convert", "-z", "2", "-o", png_path, svg_path],
                       check=True)
        print("figure3_pricing_module.png")
    else:
        print("rsvg-convert not found - PNG skipped")
