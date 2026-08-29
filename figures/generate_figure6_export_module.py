#!/usr/bin/env python3
"""Generate "Figure 6. Export module" for the new IA (Criterion C).

Laid out by hand from the node/connection tables in
../figure6_export_module_spec.md.  Shape helpers are imported from the
Figure 1 and Figure 3 generators so all figures share the same visual style.

Run:  python3 generate_figure6_export_module.py
Writes figure6_export_module.svg and .png next to this script.
"""
import os
import shutil
import subprocess

from generate_figure1_main_flow import (Chart, top, bottom, right, spine,
                                        io_left_at)
from generate_figure3_pricing_module import process2

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def build_export():
    c = Chart(640, 730)
    cx = 300

    # vertical spine
    t_start = c.terminator("Export module", cx, 40)                      # N1
    in_cat = c.io("Select category", cx, 110)                            # N2
    p_coll = c.process("Collect category products", cx, 182)             # N3
    d_any = c.decision("Any products?", cx, 270)                         # N4
    p_fmt = process2(c, "Format price list",
                     "name, Pw and Pr", cx, 360)                         # N6
    in_loc = c.io("Choose save location", cx, 440)                       # N7
    p_pdf = c.process("Write PDF file", cx, 515)                         # N8
    out_ok = c.io("Show confirmation", cx, 590)                          # N9
    t_ret = c.terminator("Return", cx, 680)                              # N10

    # side node: empty-category message, right of N4
    out_empty = c.io("Show empty message", 520, 270)                     # N5

    spine(c, t_start, in_cat)
    spine(c, in_cat, p_coll)
    spine(c, p_coll, d_any)

    # N4: no -> empty message (right), yes -> format (spine)
    empty_left = io_left_at(out_empty, d_any["cy"])
    c.arrow([right(d_any), (empty_left, d_any["cy"])],
            "no", (right(d_any)[0] + empty_left) / 2, 258)
    c.arrow([bottom(d_any), top(p_fmt)], "yes", cx + 8, 320, "start")

    spine(c, p_fmt, in_loc)
    spine(c, in_loc, p_pdf)
    spine(c, p_pdf, out_ok)
    spine(c, out_ok, t_ret)

    # N5 exit routes down the right side, merging into the spine above N10
    c.line([bottom(out_empty), (out_empty["cx"], 640), (cx, 640)])
    return c


if __name__ == "__main__":
    chart = build_export()
    svg_path = os.path.join(OUT_DIR, "figure6_export_module.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(chart.svg())
    print(f"figure6_export_module.svg  ({chart.w}x{chart.h})")

    if shutil.which("rsvg-convert"):
        png_path = os.path.join(OUT_DIR, "figure6_export_module.png")
        subprocess.run(["rsvg-convert", "-z", "2", "-o", png_path, svg_path],
                       check=True)
        print("figure6_export_module.png")
    else:
        print("rsvg-convert not found - PNG skipped")
