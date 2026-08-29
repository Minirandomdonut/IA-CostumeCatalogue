#!/usr/bin/env python3
"""Generate "Figures 11-16. Wireframes" for the new IA (Criterion C).

Six low-fidelity Tkinter screen wireframes, laid out from
../figures11-16_wireframes_spec.md.  The Screen helper is adapted from the
old IA's wireframe generator (same fonts, stroke weights, grayscale style);
per the new spec there are no margin annotations or decoration.

Sample prices follow the Figure 8 formula (Pw = ceil(cost*1.25*1.16/5)*5,
Pr = ceil(Pw*1.15/5)*5); the starred retail (440*) is a manual price.

Run:  python3 "generate_figures11-16_wireframes.py"
Writes figure11..16_wireframe_*.svg and .png next to this script.
"""
import os
import shutil
import subprocess

FONT = 13
SMALL = 11
LINE_H = 17
STROKE = 1.5
GRAY = "#555"
FILL_GRAY = "#f2f2f2"
TITLEBAR_H = 30
DASH = "5 3"

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Screen:
    """One wireframe: a window rectangle with a title bar, plain grayscale."""

    def __init__(self, canvas_w, canvas_h, win_x, win_y, win_w, win_h, title):
        self.w, self.h = canvas_w, canvas_h
        self.x, self.y = win_x, win_y
        self.ww, self.wh = win_w, win_h
        self.boxes, self.texts = [], []
        self.rect(self.x, self.y, self.ww, self.wh)
        self.rect(self.x, self.y, self.ww, TITLEBAR_H, fill=FILL_GRAY)
        self.text(self.x + self.ww / 2, self.y + 20, title, "middle", bold=True)

    # ---- primitives ------------------------------------------------------
    def rect(self, x, y, w, h, fill="#fff", dashed=False, sw=STROKE):
        d = f' stroke-dasharray="{DASH}"' if dashed else ""
        self.boxes.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
            f'stroke="#000" stroke-width="{sw}"{d}/>'
        )

    def line(self, x1, y1, x2, y2, sw=STROKE):
        self.boxes.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" '
            f'stroke-width="{sw}"/>'
        )

    def text(self, x, y, s, anchor="start", size=FONT, bold=False, fill="#000"):
        b = ' font-weight="bold"' if bold else ""
        self.texts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{fill}"{b}>{esc(s)}</text>'
        )

    def heading(self, y, s):
        self.text(self.x + self.ww / 2, y, s, "middle", size=15, bold=True)

    def small(self, x, y, s, anchor="start"):
        self.text(x, y, s, anchor, size=SMALL, fill=GRAY)

    # ---- widgets ---------------------------------------------------------
    def entry(self, x, y, w, sample, cap=None, h=26):
        if cap:
            self.small(x, y - 6, cap)
        self.rect(x, y, w, h)
        self.small(x + 8, y + h / 2 + 4, sample)
        return y + h

    def readonly(self, x, y, w, sample, cap=None, h=26):
        if cap:
            self.small(x, y - 6, cap)
        self.rect(x, y, w, h, fill=FILL_GRAY, dashed=True)
        self.text(x + 8, y + h / 2 + 4, sample, size=SMALL)
        return y + h

    def button(self, x, y, w, caption, h=28, dashed=False):
        self.rect(x, y, w, h, fill="#fff" if dashed else FILL_GRAY, dashed=dashed)
        self.text(x + w / 2, y + h / 2 + 4, caption, "middle", size=SMALL)
        return y + h

    def dropdown(self, x, y, w, value, h=26):
        self.rect(x, y, w, h)
        self.small(x + 8, y + h / 2 + 4, value)
        ax, ay = x + w - 14, y + h / 2 - 2
        self.boxes.append(
            f'<polygon points="{ax - 5},{ay} {ax + 5},{ay} {ax},{ay + 6}" fill="#000"/>'
        )

    def crossed(self, x, y, w, h, label=None):
        """Photo placeholder: rectangle with crossed diagonals."""
        self.rect(x, y, w, h)
        self.line(x, y, x + w, y + h, sw=0.9)
        self.line(x + w, y, x, y + h, sw=0.9)
        if label:
            self.small(x + w / 2 - len(label) * 2.8, y + h / 2 + 4, label)

    def scrollbar(self, x, y, h, thumb_h=60):
        self.rect(x, y, 12, h, fill=FILL_GRAY)
        self.rect(x + 2, y + 14, 8, thumb_h, fill="#ccc", sw=0.9)

    def mini_button(self, x, y, caption):
        self.rect(x, y, 20, 18, fill=FILL_GRAY)
        self.text(x + 10, y + 13, caption, "middle", size=SMALL)

    def table(self, x, y, widths, headers, rows, row_h=30, header_h=24):
        w = sum(widths)
        self.rect(x, y, w, header_h, fill=FILL_GRAY)
        cx = x
        for cw, htext in zip(widths, headers):
            self.text(cx + 8, y + header_h - 8, htext, size=SMALL, bold=True)
            cx += cw
        ty = y + header_h
        for row in rows:
            self.rect(x, ty, w, row_h)
            cx = x
            for cw, cell in zip(widths, row):
                if cell is not None:
                    self.text(cx + 8, ty + row_h / 2 + 4, cell, size=SMALL)
                cx += cw
            ty += row_h
        cx = x
        for cw in widths[:-1]:
            cx += cw
            self.line(cx, y, cx, ty, sw=0.9)
        return ty


# Portrait window, same proportions as the Tkinter prototype screens.
PW, PH = 480, 594
PX, PY = 30, 30
PORTRAIT = (540, 660, PX, PY, PW, PH)
INNER_X = PX + 28
BACK_Y = PY + 548


def back_to_menu(s):
    s.button(PX + 130, BACK_Y, 220, "Back to menu")


def build_main_menu():
    s = Screen(*PORTRAIT, title="Catalogue manager")
    s.heading(PY + 100, "Main menu")
    bx, bw = PX + 130, 220
    y = PY + 160
    for cap in ["Search product", "Manage catalogue", "Import Excel list",
                "Export price list"]:
        s.button(bx, y, bw, cap, h=32)
        y += 56
    s.button(bx, y + 32, bw, "Exit", h=32, dashed=True)
    return s


def build_catalogue_browser():
    s = Screen(*PORTRAIT, title="Manage catalogue")
    s.button(INNER_X, PY + 52, 120, "+ Add product", h=26)

    tx, ty = INNER_X, PY + 100
    widths = [150, 55, 50, 55, 90]
    rows = [
        ["Catrina clasica", "250", "365", "420", None],
        ["Calabaza LED", "120", "175", "205", None],
        ["Guirnalda bruja", "199", "290", "335", None],
        ["Corona calaveras", "275", "400", "440*", None],
        ["Velas negras x12", "85", "125", "145", None],
    ]
    bottom = s.table(tx, ty, widths, ["Name", "Cost", "Pw", "Pr", "Actions"], rows)
    ax = tx + sum(widths[:-1])
    for i in range(len(rows)):
        ry = ty + 24 + i * 30 + 6
        s.mini_button(ax + 10, ry, "E")
        s.mini_button(ax + 38, ry, "D")
    s.scrollbar(tx + sum(widths), ty, bottom - ty)
    s.small(tx, bottom + 18, "* manually set retail")

    back_to_menu(s)
    return s


def build_product_view():
    s = Screen(*PORTRAIT, title="Product view / edit")
    ph_x, ph_y, ph = INNER_X, PY + 70, 140
    s.crossed(ph_x, ph_y, ph, ph, "photo")
    s.button(ph_x, ph_y + ph + 12, ph, "Choose photo...", h=26)

    fx = ph_x + ph + 26
    fw = PW - (fx - PX) - 28
    y = PY + 76
    for cap, sample in [("Name", "Corona calaveras"), ("Category", "Halloween"),
                        ("Supplier", "FantasyMex"), ("Supplier cost", "275")]:
        y = s.entry(fx, y, fw, sample, cap=cap) + 30

    div_y = PY + 330
    s.line(INNER_X, div_y, PX + PW - 28, div_y, sw=0.9)

    py_ = div_y + 34
    s.readonly(INNER_X, py_, 150, "400", cap="Wholesale (auto)")
    s.entry(INNER_X + 190, py_, 150, "440 *", cap="Retail")
    s.small(INNER_X, py_ + 48, "empty = formula price - value = manual (*)")

    s.button(INNER_X, PY + 470, 150, "Save changes")
    s.button(INNER_X + 170, PY + 470, 100, "Back")
    return s


def build_search():
    s = Screen(*PORTRAIT, title="Search product")
    qw = 280
    s.entry(INNER_X, PY + 60, qw, "catrina clasika")
    s.button(INNER_X + qw + 14, PY + 60, 100, "Search", h=26)

    ty = PY + 130
    s.small(INNER_X + 300, ty - 6, "Pw")
    s.small(INNER_X + 360, ty - 6, "Pr")
    results = [
        ("Catrina clasica", "365", "420"),
        ("Catrina charra", "450", "520"),
        ("Calavera catrina LED", "215", "250"),
        ("Catrina mini", "90", "105"),
    ]
    rw, rh = 410, 40
    for name, pw_, pr_ in results:
        s.rect(INNER_X, ty, rw, rh)
        s.crossed(INNER_X + 7, ty + 7, 26, 26)
        s.text(INNER_X + 44, ty + rh / 2 + 4, name, size=SMALL)
        s.text(INNER_X + 300 + 8, ty + rh / 2 + 4, pw_, size=SMALL)
        s.text(INNER_X + 360 + 8, ty + rh / 2 + 4, pr_, size=SMALL)
        ty += rh
    s.small(INNER_X, ty + 20, "Click a result to open the product view")

    back_to_menu(s)
    return s


def build_import_review():
    s = Screen(*PORTRAIT, title="Import Excel list")
    s.button(INNER_X, PY + 52, 110, "Choose file...", h=26)
    s.small(INNER_X + 124, PY + 52 + 17, "HALLOWEEN.xls")

    y2 = PY + 96
    s.text(INNER_X, y2 + 17, "Sheet", size=SMALL)
    s.dropdown(INNER_X + 48, y2, 110, "Hoja4")
    s.button(INNER_X + 172, y2, 90, "Import", h=26)

    s.small(INNER_X, PY + 152, "47 rows imported - 3 to review - 12 manual retails")

    tx, ty = INNER_X, PY + 176
    widths = [40, 165, 65, 140]
    rows = [
        ["2", "(oro, plata, morado...)", "OFERTA", "cost not a number"],
        ["6", "(empty)", "420", "name missing"],
        ["14", "HALLOWEEN ACC. 2020", "(empty)", "cost missing"],
    ]
    bottom = s.table(tx, ty, widths, ["Row", "Name", "Cost", "Problem"], rows)

    by = bottom + 24
    s.button(INNER_X, by, 120, "Fix selected", h=26)
    s.button(INNER_X + 136, by, 120, "Skip selected", h=26, dashed=True)

    back_to_menu(s)
    return s


def build_export():
    s = Screen(*PORTRAIT, title="Export price list")
    y = PY + 70
    s.text(INNER_X, y + 17, "Category", size=SMALL)
    s.dropdown(INNER_X + 70, y, 140, "Halloween")
    s.button(INNER_X + 224, y, 90, "Export", h=26)
    s.small(INNER_X, y + 52, "Writes a PDF with name, wholesale and retail")

    cx, cy, cw, ch = INNER_X, PY + 180, 340, 70
    s.rect(cx, cy, cw, ch, fill=FILL_GRAY)
    s.text(cx + 16, cy + 28, "Saved: precios_halloween.pdf", size=SMALL, bold=True)
    s.text(cx + 16, cy + 50, "47 products - current prices", size=SMALL)

    back_to_menu(s)
    return s


SCREENS = {
    "figure11_wireframe_main_menu": build_main_menu,
    "figure12_wireframe_catalogue_browser": build_catalogue_browser,
    "figure13_wireframe_product_view": build_product_view,
    "figure14_wireframe_search": build_search,
    "figure15_wireframe_import_review": build_import_review,
    "figure16_wireframe_export": build_export,
}


if __name__ == "__main__":
    for name, builder in SCREENS.items():
        screen = builder()
        svg_path = os.path.join(OUT_DIR, name + ".svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{screen.w}" '
                f'height="{screen.h}" viewBox="0 0 {screen.w} {screen.h}" '
                f'font-family="Helvetica, Arial, sans-serif">'
                f'<rect width="{screen.w}" height="{screen.h}" fill="#fff"/>'
                f'<g>{"".join(screen.boxes)}</g>'
                f'<g>{"".join(screen.texts)}</g>'
                "</svg>"
            )
        print(f"{name}.svg  ({screen.w}x{screen.h})")
        if shutil.which("rsvg-convert"):
            subprocess.run(["rsvg-convert", "-z", "2", "-o",
                            os.path.join(OUT_DIR, name + ".png"), svg_path],
                           check=True)
            print(f"{name}.png")
