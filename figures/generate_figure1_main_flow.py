#!/usr/bin/env python3
"""Generate "Figure 1. Main Flow" for the new IA (Criterion C) as SVG + PNG.

Laid out by hand from the node/connection tables in ../figure1_main_flow_spec.md.
The shape helpers are reused from the old IA's flowchart generator so the visual
style (fonts, line weights, symbols) matches the old Figure 1 exactly.

Run:  python3 generate_figure1_main_flow.py
Writes figure1_main_flow.svg and figure1_main_flow.png next to this script.
"""
import math
import os
import shutil
import subprocess
import textwrap

FONT_SIZE = 13
LINE_H = 17          # line height for wrapped label text
CHAR_W = 7.3         # generous per-character width estimate (13px Helvetica)
STROKE = 1.5
PAD_X = 14           # horizontal text padding inside rectangles
PAD_Y = 10           # vertical text padding
SKEW = 14            # horizontal lean of input/output parallelograms
BAR = 8              # inset of the double bars on predefined-process boxes
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def measure(text, wrapw):
    lines = textwrap.wrap(text, wrapw)
    tw = max(len(l) for l in lines) * CHAR_W
    th = len(lines) * LINE_H
    return lines, tw, th


# ---------------------------------------------------------------- anchors ---
def top(n):    return (n["cx"], n["cy"] - n["h"] / 2)
def bottom(n): return (n["cx"], n["cy"] + n["h"] / 2)
def left(n):   return (n["cx"] - n["w"] / 2, n["cy"])
def right(n):  return (n["cx"] + n["w"] / 2, n["cy"])


def io_left_at(n, y):
    """x of a parallelogram's slanted left edge at height y (leans right)."""
    t, b = n["cy"] - n["h"] / 2, n["cy"] + n["h"] / 2
    return n["cx"] - n["w"] / 2 + SKEW * (b - y) / (b - t)


def io_right_at(n, y):
    t, b = n["cy"] - n["h"] / 2, n["cy"] + n["h"] / 2
    return n["cx"] + n["w"] / 2 - SKEW * (y - t) / (b - t)


# ------------------------------------------------------------------ chart ---
class Chart:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.shapes, self.texts, self.flow, self.labels = [], [], [], []

    def _label_text(self, cx, cy, lines):
        n = len(lines)
        for i, ln in enumerate(lines):
            y = cy + (i - (n - 1) / 2) * LINE_H
            self.texts.append(
                f'<text x="{cx:.1f}" y="{y:.1f}" text-anchor="middle" '
                f'dominant-baseline="central">{esc(ln)}</text>')

    def _node(self, cx, cy, w, h):
        return {"cx": cx, "cy": cy, "w": w, "h": h}

    def terminator(self, text, cx, cy, wrapw=24):
        lines, tw, th = measure(text, wrapw)
        w, h = tw + 2 * PAD_X + 16, th + 2 * PAD_Y
        self.shapes.append(
            f'<rect x="{cx - w/2:.1f}" y="{cy - h/2:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" rx="{h/2:.1f}"/>')
        self._label_text(cx, cy, lines)
        return self._node(cx, cy, w, h)

    def process(self, text, cx, cy, wrapw=24):
        lines, tw, th = measure(text, wrapw)
        w, h = tw + 2 * PAD_X, th + 2 * PAD_Y
        self.shapes.append(
            f'<rect x="{cx - w/2:.1f}" y="{cy - h/2:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}"/>')
        self._label_text(cx, cy, lines)
        return self._node(cx, cy, w, h)

    def predefined(self, text, cx, cy, wrapw=16):
        lines, tw, th = measure(text, wrapw)
        w, h = tw + 2 * (PAD_X + BAR + 4), th + 2 * PAD_Y
        x0, y0 = cx - w / 2, cy - h / 2
        self.shapes.append(
            f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}"/>')
        for bx in (x0 + BAR, x0 + w - BAR):
            self.shapes.append(
                f'<line x1="{bx:.1f}" y1="{y0:.1f}" x2="{bx:.1f}" y2="{y0 + h:.1f}"/>')
        self._label_text(cx, cy, lines)
        return self._node(cx, cy, w, h)

    def io(self, text, cx, cy, wrapw=24):
        lines, tw, th = measure(text, wrapw)
        w, h = tw + 2 * PAD_X + 2 * SKEW, th + 2 * PAD_Y
        x0, x1 = cx - w / 2, cx + w / 2
        t, b = cy - h / 2, cy + h / 2
        pts = f"{x0 + SKEW:.1f},{t:.1f} {x1:.1f},{t:.1f} {x1 - SKEW:.1f},{b:.1f} {x0:.1f},{b:.1f}"
        self.shapes.append(f'<polygon points="{pts}"/>')
        self._label_text(cx, cy, lines)
        return self._node(cx, cy, w, h)

    def decision(self, text, cx, cy, wrapw=18):
        lines, tw, th = measure(text, wrapw)
        W, H = tw + 70, th + 44
        while tw / W + th / H > 0.88:
            W += 12
            H += 6
        pts = (f"{cx:.1f},{cy - H/2:.1f} {cx + W/2:.1f},{cy:.1f} "
               f"{cx:.1f},{cy + H/2:.1f} {cx - W/2:.1f},{cy:.1f}")
        self.shapes.append(f'<polygon points="{pts}"/>')
        self._label_text(cx, cy, lines)
        return self._node(cx, cy, W, H)

    # -------- flowlines --------
    def arrow(self, pts, label=None, lx=0, ly=0, anchor="middle"):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.flow.append(f'<polyline points="{d}" marker-end="url(#ah)"/>')
        if label:
            self.branch_label(label, lx, ly, anchor)

    def line(self, pts):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.flow.append(f'<polyline points="{d}"/>')

    def branch_label(self, text, lx, ly, anchor="middle"):
        self.labels.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
            f'dominant-baseline="central" paint-order="stroke" stroke="#fff" '
            f'stroke-width="4">{esc(text)}</text>')

    def svg(self):
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" font-family="Helvetica, Arial, sans-serif" '
            f'font-size="{FONT_SIZE}">'
            '<defs><marker id="ah" markerWidth="11" markerHeight="9" refX="9.5" refY="4.5" '
            'orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M0,0 L10,4.5 L0,9 z" fill="#000" stroke="none"/></marker></defs>'
            f'<rect width="{self.w}" height="{self.h}" fill="#fff"/>'
            f'<g fill="none" stroke="#000" stroke-width="{STROKE}">{"".join(self.flow)}</g>'
            f'<g fill="#fff" stroke="#000" stroke-width="{STROKE}">{"".join(self.shapes)}</g>'
            f'<g fill="#000">{"".join(self.texts)}{"".join(self.labels)}</g>'
            '</svg>')


def spine(c, a, b):
    """Straight arrow from bottom of node a to top of node b."""
    c.arrow([bottom(a), top(b)])


# ================================================================ figure 1 ==
def build_main():
    c = Chart(1010, 760)
    cx = 505

    # vertical spine: N1..N5 top-down, centered
    start = c.terminator("Start", cx, 100)                                # N1
    p_load = c.process("Load catalogue from local storage", cx, 170)      # N2
    menu = c.io("Display main menu", cx, 248)                             # N3
    sel = c.io("User selects an option", cx, 320)                         # N4
    d_opt = c.decision("Which option?", cx, 420)                          # N5

    spine(c, start, p_load)
    spine(c, p_load, menu)
    spine(c, menu, sel)
    spine(c, sel, d_opt)

    # N6-N9 in one horizontal row below the diamond, left to right
    cols = {"catalogue": 150, "import": 330, "search": 680, "export": 880}
    box_cy = 520
    b_cat = c.predefined("Catalogue sub-process (pricing module)",
                         cols["catalogue"], box_cy)                       # N6
    b_imp = c.predefined("Import sub-process", cols["import"], box_cy)    # N7
    b_sea = c.predefined("Search sub-process", cols["search"], box_cy)    # N8
    b_exp = c.predefined("Export sub-process", cols["export"], box_cy)    # N9

    # five-way dispatch: labeled drops off left/right split lines + Exit
    y_split = d_opt["cy"]
    c.line([left(d_opt), (cols["catalogue"], y_split)])
    c.line([right(d_opt), (cols["export"], y_split)])
    for key, box in (("catalogue", b_cat), ("import", b_imp),
                     ("search", b_sea), ("export", b_exp)):
        c.arrow([(cols[key], y_split), top(box)])
    c.branch_label("Catalogue", cols["catalogue"] + 8, 455, "start")
    c.branch_label("Import", cols["import"] + 8, 455, "start")
    c.branch_label("Search", cols["search"] - 8, 455, "end")
    c.branch_label("Export", cols["export"] - 8, 455, "end")

    # N10: automatic save, placed left of the menu node; N10 -> N3
    p_save = c.process("Save catalogue automatically", 170, menu["cy"], wrapw=16)
    c.arrow([right(p_save), (io_left_at(menu, menu["cy"]), menu["cy"])])

    save_x0 = p_save["cx"] - p_save["w"] / 2
    save_y0 = p_save["cy"] - p_save["h"] / 2

    # returns from N6/N7 merge left into N10's left edge (nested rails)
    c.arrow([bottom(b_cat), (b_cat["cx"], 585), (40, 585),
             (40, p_save["cy"] + 9), (save_x0, p_save["cy"] + 9)])
    c.arrow([bottom(b_imp), (b_imp["cx"], 612), (20, 612),
             (20, p_save["cy"] - 9), (save_x0, p_save["cy"] - 9)])

    # returns from N8/N9 merge right and route around the outside (over the
    # top of the chart) into N10's top edge
    c.arrow([bottom(b_exp), (b_exp["cx"], 585), (952, 585),
             (952, 34), (195, 34), (195, save_y0)])
    c.arrow([bottom(b_sea), (b_sea["cx"], 612), (976, 612),
             (976, 20), (145, 20), (145, save_y0)])

    # Exit branch: straight down the center, between N7 and N8, no save
    end = c.terminator("End", cx, 700)                                    # N11
    c.arrow([bottom(d_opt), top(end)], "Exit", cx + 10, 470, "start")
    return c


if __name__ == "__main__":
    chart = build_main()
    svg_path = os.path.join(OUT_DIR, "figure1_main_flow.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(chart.svg())
    print(f"figure1_main_flow.svg  ({chart.w}x{chart.h})")

    if shutil.which("rsvg-convert"):
        png_path = os.path.join(OUT_DIR, "figure1_main_flow.png")
        subprocess.run(["rsvg-convert", "-z", "2", "-o", png_path, svg_path],
                       check=True)
        print("figure1_main_flow.png")
    else:
        print("rsvg-convert not found - PNG skipped")
