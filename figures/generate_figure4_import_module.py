#!/usr/bin/env python3
"""Generate "Figure 4. Import module" for the new IA (Criterion C).

Laid out by hand from the node/connection tables in
../figure4_import_module_spec.md.  Shape helpers are imported from the
Figure 1 and Figure 3 generators so all figures share the same visual style.

Run:  python3 generate_figure4_import_module.py
Writes figure4_import_module.svg and .png next to this script.
"""
import os
import shutil
import subprocess

from generate_figure1_main_flow import (Chart, top, bottom, left, right,
                                        spine, CHAR_W, LINE_H, PAD_X, PAD_Y,
                                        BAR)
from generate_figure3_pricing_module import process2

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def predefined2(c, title, subtitle, cx, cy):
    """Predefined-process box with an exact two-line "title / subtitle" label."""
    lines = [title, subtitle]
    tw = max(len(l) for l in lines) * CHAR_W
    th = len(lines) * LINE_H
    w, h = tw + 2 * (PAD_X + BAR + 4), th + 2 * PAD_Y
    x0, y0 = cx - w / 2, cy - h / 2
    c.shapes.append(
        f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}"/>')
    for bx in (x0 + BAR, x0 + w - BAR):
        c.shapes.append(
            f'<line x1="{bx:.1f}" y1="{y0:.1f}" x2="{bx:.1f}" y2="{y0 + h:.1f}"/>')
    c._label_text(cx, cy, lines)
    return c._node(cx, cy, w, h)


def build_import():
    c = Chart(800, 960)
    cx = 430

    # vertical spine
    t_start = c.terminator("Import module", cx, 40)                      # N1
    in_file = c.io("Select Excel file", cx, 110)                         # N2
    p_read = c.process("Read next row", cx, 185)                         # N3
    d_valid = c.decision("Fields valid?", cx, 270)                       # N4
    p_create = c.process("Create register", cx, 355)                     # N6
    b_price = predefined2(c, "Pricing module",
                          "computes Pw and Pr", cx, 440)                 # N7
    d_retail = c.decision("Retail price in row?", cx, 535)               # N8
    d_match = c.decision("Row retail = formula?", cx, 635)               # N9
    d_more = c.decision("More rows?", cx, 760)                           # N11
    out_list = c.io("Display review list", cx, 845)                      # N12
    t_ret = c.terminator("Return", cx, 915)                              # N13

    # side nodes
    p_review = c.process("Add to review list", 650, 270)                 # N5
    p_manual = process2(c, "Set manual retail",
                        "keeps row value", 140, 635)                     # N10

    spine(c, t_start, in_file)
    spine(c, in_file, p_read)
    spine(c, p_read, d_valid)

    # N4: no -> review list (right), yes -> create register (spine)
    c.arrow([right(d_valid), left(p_review)],
            "no", (right(d_valid)[0] + left(p_review)[0]) / 2, 258)
    c.arrow([bottom(d_valid), top(p_create)], "yes", cx + 8, 320, "start")

    spine(c, p_create, b_price)
    spine(c, b_price, d_retail)

    # N8: yes -> compare retail (spine), no -> bypass right into spine above N11
    c.arrow([bottom(d_retail), top(d_match)], "yes", cx + 8, 585, "start")
    c.line([right(d_retail), (590, d_retail["cy"]), (590, 700), (cx, 700)])
    c.branch_label("no", right(d_retail)[0] + 14, d_retail["cy"] - 12, "start")

    # N9: no -> set manual retail (left), yes -> spine down to N11
    c.arrow([left(d_match), right(p_manual)],
            "no", (left(d_match)[0] + right(p_manual)[0]) / 2, 623)
    c.arrow([bottom(d_match), top(d_more)], "yes", cx + 8, 690, "start")

    # N10 exit merges back into the spine above N11
    c.line([bottom(p_manual), (p_manual["cx"], 712), (cx, 712)])

    # N5 exit routes down the right side into N11's right vertex
    c.line([bottom(p_review), (p_review["cx"], d_more["cy"])])
    c.arrow([(p_review["cx"], d_more["cy"]), right(d_more)])

    # N11: yes -> loop around the far left back into N3, no -> review list
    c.arrow([left(d_more), (30, d_more["cy"]), (30, p_read["cy"]),
             left(p_read)], "yes", left(d_more)[0] - 12, d_more["cy"] - 12,
            "end")
    c.arrow([bottom(d_more), top(out_list)], "no", cx + 8, 808, "start")

    spine(c, out_list, t_ret)
    return c


if __name__ == "__main__":
    chart = build_import()
    svg_path = os.path.join(OUT_DIR, "figure4_import_module.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(chart.svg())
    print(f"figure4_import_module.svg  ({chart.w}x{chart.h})")

    if shutil.which("rsvg-convert"):
        png_path = os.path.join(OUT_DIR, "figure4_import_module.png")
        subprocess.run(["rsvg-convert", "-z", "2", "-o", png_path, svg_path],
                       check=True)
        print("figure4_import_module.png")
    else:
        print("rsvg-convert not found - PNG skipped")
