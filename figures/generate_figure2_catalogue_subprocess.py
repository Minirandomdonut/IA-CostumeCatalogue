#!/usr/bin/env python3
"""Generate "Figure 2. Catalogue subprocess" for the new IA (Criterion C).

Laid out by hand from the node/connection tables in
../figure2_catalogue_subprocess_spec.md.  All shape helpers are imported from
the Figure 1 generator so both figures share the exact same visual style.

Run:  python3 generate_figure2_catalogue_subprocess.py
Writes figure2_catalogue_subprocess.svg and .png next to this script.
"""
import os
import shutil
import subprocess

from generate_figure1_main_flow import Chart, top, bottom, left, right, spine

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def build_catalogue():
    c = Chart(940, 700)
    cx = 450

    # vertical spine: N1, N2, N3 top-down, centered
    t_start = c.terminator("Catalogue subprocess", cx, 40, wrapw=30)     # N1
    in_sel = c.io("User selects action", cx, 112)                        # N2
    d_act = c.decision("Which action?", cx, 195)                         # N3

    spine(c, t_start, in_sel)
    spine(c, in_sel, d_act)

    # three columns below the decision: Add | Edit | Delete
    col_add, col_edit, col_del = 150, cx, 750

    # Add column
    in_prod = c.io("Enter product data", col_add, 280)                   # N4
    p_create = c.process("Create register", col_add, 360)                # N5
    b_price1 = c.predefined("Pricing module", col_add, 440)              # N6
    # Edit column
    in_chg = c.io("Enter changes", col_edit, 280)                        # N7
    d_cost = c.decision("Cost changed?", col_edit, 368)                  # N8
    b_price2 = c.predefined("Pricing module", col_edit, 460)             # N9
    # Delete column
    d_conf = c.decision("Confirm delete?", col_del, 290)                 # N10
    p_del = c.process("Delete register", col_del, 390)                   # N11

    # three-way dispatch with branch labels
    c.line([left(d_act), (col_add, d_act["cy"])])
    c.arrow([(col_add, d_act["cy"]), top(in_prod)],
            "Add", col_add + 8, 232, "start")
    c.arrow([bottom(d_act), top(in_chg)], "Edit", cx + 8, 240, "start")
    c.line([right(d_act), (col_del, d_act["cy"])])
    c.arrow([(col_del, d_act["cy"]), top(d_conf)],
            "Delete", col_del - 8, 232, "end")

    # Add path: N4 -> N5 -> N6
    spine(c, in_prod, p_create)
    spine(c, p_create, b_price1)
    # Edit path: N7 -> N8 -> (yes) N9 / (no) bypass
    spine(c, in_chg, d_cost)
    c.arrow([bottom(d_cost), top(b_price2)], "yes", cx + 8, 415, "start")
    # Delete path: N10 -> (yes) N11 / (no) bypass
    c.arrow([bottom(d_conf), top(p_del)], "yes", col_del + 8, 340, "start")

    # merge bus: all five terminal paths feed N12 at bottom center
    bus_y = 560
    bypass_no_x, del_no_x = 560, 870
    c.line([bottom(b_price1), (col_add, bus_y)])                 # N6 -> N12
    c.line([bottom(b_price2), (col_edit, bus_y)])                # N9 -> N12
    c.line([right(d_cost), (bypass_no_x, d_cost["cy"]),          # N8 no ->
            (bypass_no_x, bus_y)])
    c.branch_label("no", right(d_cost)[0] + 14, d_cost["cy"] - 12, "start")
    c.line([bottom(p_del), (col_del, bus_y)])                    # N11 -> N12
    c.line([right(d_conf), (del_no_x, d_conf["cy"]),             # N10 no ->
            (del_no_x, bus_y)])
    c.branch_label("no", right(d_conf)[0] + 14, d_conf["cy"] - 12, "start")
    c.line([(col_add, bus_y), (del_no_x, bus_y)])                # the bus

    t_ret = c.terminator("Return", cx, 630)                              # N12
    c.arrow([(cx, bus_y), top(t_ret)])
    return c


if __name__ == "__main__":
    chart = build_catalogue()
    svg_path = os.path.join(OUT_DIR, "figure2_catalogue_subprocess.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(chart.svg())
    print(f"figure2_catalogue_subprocess.svg  ({chart.w}x{chart.h})")

    if shutil.which("rsvg-convert"):
        png_path = os.path.join(OUT_DIR, "figure2_catalogue_subprocess.png")
        subprocess.run(["rsvg-convert", "-z", "2", "-o", png_path, svg_path],
                       check=True)
        print("figure2_catalogue_subprocess.png")
    else:
        print("rsvg-convert not found - PNG skipped")
