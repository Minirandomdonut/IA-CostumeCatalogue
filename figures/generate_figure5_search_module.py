#!/usr/bin/env python3
"""Generate "Figure 5. Search module" for the new IA (Criterion C).

Laid out by hand from the node/connection tables in
../figure5_search_module_spec.md.  Shape helpers are imported from the
Figure 1 and Figure 3 generators so all figures share the same visual style.

Run:  python3 generate_figure5_search_module.py
Writes figure5_search_module.svg and .png next to this script.
"""
import os
import shutil
import subprocess

from generate_figure1_main_flow import (Chart, top, bottom, left, right,
                                        spine, io_left_at, io_right_at,
                                        CHAR_W, LINE_H, PAD_X, PAD_Y, SKEW)
from generate_figure3_pricing_module import process2

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def io2(c, title, subtitle, cx, cy):
    """Input/output parallelogram with an exact two-line label."""
    lines = [title, subtitle]
    tw = max(len(l) for l in lines) * CHAR_W
    th = len(lines) * LINE_H
    w, h = tw + 2 * PAD_X + 2 * SKEW, th + 2 * PAD_Y
    x0, x1 = cx - w / 2, cx + w / 2
    t, b = cy - h / 2, cy + h / 2
    pts = f"{x0 + SKEW:.1f},{t:.1f} {x1:.1f},{t:.1f} {x1 - SKEW:.1f},{b:.1f} {x0:.1f},{b:.1f}"
    c.shapes.append(f'<polygon points="{pts}"/>')
    c._label_text(cx, cy, lines)
    return c._node(cx, cy, w, h)


def build_search():
    c = Chart(760, 900)
    cx = 380

    # vertical spine
    t_start = c.terminator("Search module", cx, 40)                      # N1
    in_query = c.io("Enter search query", cx, 110)                       # N2
    p_read = c.process("Read next product", cx, 185)                     # N3
    p_sim = process2(c, "Compute similarity",
                     "query vs product name", cx, 262)                   # N4
    d_score = c.decision("Score ≥ 0.70?", cx, 352)                  # N5
    d_more = c.decision("More products?", cx, 475)                       # N7
    p_sort = c.process("Sort matches by score", cx, 560)                 # N8
    out_res = io2(c, "Display top 4 results",
                  "name, prices, photo", cx, 645)                        # N9
    d_open = c.decision("Open a result?", cx, 740)                       # N10
    t_ret = c.terminator("Return", cx, 840)                              # N12

    # side nodes
    p_add = c.process("Add to matches", 600, 352)                        # N6
    out_view = io2(c, "Display product view",
                   "details and photo", 620, 740)                       # N11

    spine(c, t_start, in_query)
    spine(c, in_query, p_read)
    spine(c, p_read, p_sim)
    spine(c, p_sim, d_score)

    # N5: yes -> add to matches (right), no -> straight down to N7
    c.arrow([right(d_score), left(p_add)],
            "yes", (right(d_score)[0] + left(p_add)[0]) / 2, 340)
    c.arrow([bottom(d_score), top(d_more)], "no", cx + 8, 400, "start")
    # N6 merges back into the spine above N7
    c.line([bottom(p_add), (p_add["cx"], 420), (cx, 420)])

    # N7: yes -> loop around the far left back into N3, no -> sort
    c.arrow([left(d_more), (30, d_more["cy"]), (30, p_read["cy"]),
             left(p_read)], "yes", left(d_more)[0] - 12, d_more["cy"] - 12,
            "end")
    c.arrow([bottom(d_more), top(p_sort)], "no", cx + 8, 525, "start")

    spine(c, p_sort, out_res)
    spine(c, out_res, d_open)

    # N10: yes -> product view (right), no -> Return
    c.arrow([right(d_open), (io_left_at(out_view, d_open["cy"]), d_open["cy"])],
            "yes", (right(d_open)[0] + io_left_at(out_view, d_open["cy"])) / 2,
            728)
    c.arrow([bottom(d_open), top(t_ret)], "no", cx + 8, 790, "start")

    # N11 loops up into N9's right edge (closing the view -> results list)
    c.arrow([top(out_view), (out_view["cx"], out_res["cy"]),
             (io_right_at(out_res, out_res["cy"]), out_res["cy"])])
    return c


if __name__ == "__main__":
    chart = build_search()
    svg_path = os.path.join(OUT_DIR, "figure5_search_module.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(chart.svg())
    print(f"figure5_search_module.svg  ({chart.w}x{chart.h})")

    if shutil.which("rsvg-convert"):
        png_path = os.path.join(OUT_DIR, "figure5_search_module.png")
        subprocess.run(["rsvg-convert", "-z", "2", "-o", png_path, svg_path],
                       check=True)
        print("figure5_search_module.png")
    else:
        print("rsvg-convert not found - PNG skipped")
