#!/usr/bin/env python3
"""Generate "Figure 7. Class diagram" for the new IA (Criterion C).

Laid out by hand from the class/relationship tables in
../figure7_class_diagram_spec.md.  The Diagram helper class is carried over
from the old IA's class-diagram generator so the visual style (fonts, stroke
weights, UML conventions) matches Figures 1-6.

Run:  python3 generate_figure7_class_diagram.py
Writes figure7_class_diagram.svg and .png next to this script.
"""
import os
import shutil
import subprocess

FONT_SIZE = 13
LINE_H = 17
CHAR_W = 7.3
STROKE = 1.5
PAD_X = 12
PAD_Y = 6

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def w_of(lines):
    return max(len(l) for l in lines) * CHAR_W + 2 * PAD_X


class Diagram:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.lines, self.shapes, self.texts = [], [], []

    # ---- text primitives -------------------------------------------------
    def text(self, x, y, s, anchor="middle", bold=False, size=FONT_SIZE, halo=False):
        style = ' font-weight="bold"' if bold else ""
        h = ' paint-order="stroke" stroke="#fff" stroke-width="4"' if halo else ""
        self.texts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}"{style}{h}>{esc(s)}</text>'
        )

    def text_block(self, left, top, lines):
        y = top + LINE_H - 4
        for l in lines:
            self.text(left, y, l, "start")
            y += LINE_H

    # ---- boxes -----------------------------------------------------------
    def class_box(self, name, attrs, methods, cx, top):
        """Three-compartment UML class: name / attributes / methods."""
        w = w_of([name] + attrs + methods)
        h1 = LINE_H + 2 * PAD_Y
        h2 = (len(attrs) * LINE_H + 2 * PAD_Y) if attrs else 14
        h3 = (len(methods) * LINE_H + 2 * PAD_Y) if methods else 14
        h = h1 + h2 + h3
        x = cx - w / 2
        self.shapes.append(
            f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="#fff" stroke="#000" stroke-width="{STROKE}"/>'
        )
        self.shapes.append(f'<line x1="{x}" y1="{top + h1}" x2="{x + w}" y2="{top + h1}" stroke="#000" stroke-width="{STROKE}"/>')
        self.shapes.append(f'<line x1="{x}" y1="{top + h1 + h2}" x2="{x + w}" y2="{top + h1 + h2}" stroke="#000" stroke-width="{STROKE}"/>')
        self.text(cx, top + h1 - PAD_Y - 3, name, "middle", bold=True)
        self.text_block(x + PAD_X, top + h1 + PAD_Y, attrs)
        self.text_block(x + PAD_X, top + h1 + h2 + PAD_Y, methods)
        return {"cx": cx, "cy": top + h / 2, "w": w, "h": h, "top": top, "bottom": top + h,
                "left": x, "right": x + w}

    # ---- connectors ------------------------------------------------------
    def polyline(self, pts, dashed=False, arrow=False):
        d = " ".join(f"{x},{y}" for x, y in pts)
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        mk = ' marker-end="url(#dep)"' if arrow else ""
        self.lines.append(
            f'<polyline points="{d}" fill="none" stroke="#000" stroke-width="{STROKE}"{dash}{mk}/>'
        )

    def comp_diamond(self, x, y, dx, dy, L=18, wd=6):
        """Filled composition diamond, tip at (x,y), axis pointing (dx,dy) into the whole."""
        bx, by = x - L * dx, y - L * dy
        mx, my = x - L / 2 * dx, y - L / 2 * dy
        px, py = -dy, dx
        pts = f"{x},{y} {mx + wd * px},{my + wd * py} {bx},{by} {mx - wd * px},{my - wd * py}"
        self.shapes.append(f'<polygon points="{pts}" fill="#000" stroke="#000"/>')

    def label(self, x, y, s, anchor="middle"):
        self.text(x, y, s, anchor, halo=True)

    # ---- assembly --------------------------------------------------------
    def svg(self):
        defs = (
            '<defs><marker id="dep" markerWidth="11" markerHeight="10" refX="9" refY="5" '
            'orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M0,0 L9,5 L0,10" fill="none" stroke="#000" stroke-width="1.5"/>'
            "</marker></defs>"
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" font-family="Helvetica, Arial, sans-serif">'
            f"{defs}"
            f'<rect width="{self.width}" height="{self.height}" fill="#fff"/>'
            f'<g>{"".join(self.lines)}</g>'
            f'<g>{"".join(self.shapes)}</g>'
            f'<g>{"".join(self.texts)}</g>'
            "</svg>"
        )


def build():
    d = Diagram(1000, 760)

    ui = d.class_box("UI", ["-screens"], ["+mainloop()"], cx=510, top=40)
    storage = d.class_box("Storage", [],
                          ["+save(catalogue)", "+load() Catalogue"],
                          cx=880, top=60)
    catalogue = d.class_box(
        "Catalogue",
        ["-products : list of Product"],
        ["+add(product)", "+edit(product)", "+delete(product)",
         "+get_category(name)"],
        cx=510, top=300)
    product = d.class_box(
        "Product",
        ["-name : str", "-category : str", "-supplier : str", "-cost : float",
         "-wholesale : float", "-retail : float", "-manual_retail : bool",
         "-photo_path : str"],
        [],
        cx=880, top=280)
    search = d.class_box("SearchModule", [], ["+search(query) list"],
                         cx=150, top=300)
    export = d.class_box("ExportModule", [], ["+export_pdf(category, path)"],
                         cx=160, top=470)
    imp = d.class_box("ImportModule", ["-review_list : list"],
                      ["+import_file(path, sheet)"], cx=510, top=600)
    pricing = d.class_box("PricingModule", [], ["+compute(product)"],
                          cx=880, top=600)

    # 1. Catalogue "1" *-- "0..*" Product : contains (composition)
    hy = 350
    d.polyline([(product["left"], hy), (catalogue["right"], hy)])
    d.comp_diamond(catalogue["right"], hy, -1, 0)
    d.label((catalogue["right"] + product["left"]) / 2 + 10, hy - 8, "contains")
    d.label(catalogue["right"] + 24, hy - 6, "1", "start")
    d.label(product["left"] - 6, hy - 6, "0..*", "end")

    # 2. Storage ..> Catalogue : saves and loads
    d.polyline([(storage["left"], 105), (700, 105), (700, 330),
                (catalogue["right"], 330)], dashed=True, arrow=True)
    d.label(709, 200, "saves and loads", "start")

    # 3. Catalogue ..> PricingModule : calls on cost change
    d.polyline([(catalogue["right"], 420), (710, 420), (710, 615),
                (pricing["left"], 615)], dashed=True, arrow=True)
    d.label(719, 520, "calls on cost change", "start")

    # 4. PricingModule ..> Product : sets Pw and Pr
    d.polyline([(pricing["cx"], pricing["top"]),
                (pricing["cx"], product["bottom"])], dashed=True, arrow=True)
    d.label(pricing["cx"] + 9, 535, "sets Pw and Pr", "start")

    # 5. ImportModule ..> Catalogue : adds products
    d.polyline([(imp["cx"], imp["top"]), (imp["cx"], catalogue["bottom"])],
               dashed=True, arrow=True)
    d.label(imp["cx"] + 9, 520, "adds products", "start")

    # 6. ImportModule ..> PricingModule : calls per row
    d.polyline([(imp["right"], 643), (pricing["left"], 643)],
               dashed=True, arrow=True)
    d.label((imp["right"] + pricing["left"]) / 2, 635, "calls per row")

    # 7. SearchModule ..> Catalogue : reads
    d.polyline([(search["right"], 336), (catalogue["left"], 336)],
               dashed=True, arrow=True)
    d.label((search["right"] + catalogue["left"]) / 2, 328, "reads")

    # 8. ExportModule ..> Catalogue : reads
    d.polyline([(export["right"], 506), (340, 506), (340, 410),
                (catalogue["left"], 410)], dashed=True, arrow=True)
    d.label(349, 460, "reads", "start")

    # 9-12. UI ..> Catalogue / SearchModule / ExportModule / ImportModule
    d.polyline([(ui["cx"], ui["bottom"]), (ui["cx"], catalogue["top"])],
               dashed=True, arrow=True)
    d.label(ui["cx"] + 9, 210, "invokes", "start")

    d.polyline([(ui["left"], 88), (search["cx"], 88),
                (search["cx"], search["top"])], dashed=True, arrow=True)
    d.label(304, 80, "invokes")

    d.polyline([(ui["left"], 70), (28, 70), (28, 506),
                (export["left"], 506)], dashed=True, arrow=True)
    d.label(243, 62, "invokes")

    d.polyline([(ui["left"], 55), (12, 55), (12, 720), (imp["cx"], 720),
                (imp["cx"], imp["bottom"])], dashed=True, arrow=True)
    d.label(261, 712, "invokes")

    return d


if __name__ == "__main__":
    diagram = build()
    svg_path = os.path.join(OUT_DIR, "figure7_class_diagram.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(diagram.svg())
    print(f"figure7_class_diagram.svg  ({diagram.width}x{diagram.height})")

    if shutil.which("rsvg-convert"):
        png_path = os.path.join(OUT_DIR, "figure7_class_diagram.png")
        subprocess.run(["rsvg-convert", "-z", "2", "-o", png_path, svg_path],
                       check=True)
        print("figure7_class_diagram.png")
    else:
        print("rsvg-convert not found - PNG skipped")
