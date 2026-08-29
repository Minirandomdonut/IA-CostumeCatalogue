#!/usr/bin/env python3
"""Generate "Figures 8-10. Pseudocode" for the new IA (Criterion C).

Code blocks are rendered EXACTLY as given in ../figures8-10_pseudocode_spec.md.
The renderer is carried over from the old IA's pseudocode-figure generator, so
the monospace style (box, fonts, spacing, caption band) matches the document.

Run:  python3 "generate_figures8-10_pseudocode.py"
Writes figure8/9/10_pseudocode_*.svg and .png next to this script.
"""
import os
import shutil
import subprocess

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

CHAR_W = 16.8333          # monospace advance at 28 px (Menlo / DejaVu Sans Mono)
PAD_W = 100.83            # total horizontal padding around the code block
LINE_H = 40
PAD_H = 150               # box padding above/below plus the caption band
CODE_X = 40
CODE_Y0 = 71              # baseline of the first code line
CODE_FONT = 28
CAP_X = 20
CAP_FONT = 23.5
CAP_UP = 49               # caption baseline sits this far above the bottom edge
BORDER = 3

MONO = "Menlo, 'DejaVu Sans Mono', 'Bitstream Vera Sans Mono', monospace"
SANS = "Verdana, 'DejaVu Sans', 'Bitstream Vera Sans', sans-serif"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def figure(code, caption):
    """Render one pseudocode figure. `code` is the block exactly as it should appear.

    The FUNCTION header and the END FUNCTION footer are bold, the body is
    regular — the convention the document's figures use.
    """
    lines = code.split("\n")
    width = round(CHAR_W * max(len(l) for l in lines) + PAD_W)
    height = LINE_H * len(lines) + PAD_H

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<rect x="{21.5}" y="{31.5}" width="{width - 62}" height="{height - 122}" '
        f'fill="#fff" stroke="#000" stroke-width="{BORDER}"/>',
        f'<g font-family="{MONO}" font-size="{CODE_FONT}" fill="#000">',
    ]
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        bold = ' font-weight="bold"' if line.startswith(("FUNCTION", "END FUNCTION")) else ""
        y = CODE_Y0 + i * LINE_H
        # Browsers strip leading whitespace inside <text>, so the indent is applied as an
        # x offset of whole character cells instead of as literal spaces.
        indent = len(line) - len(line.lstrip(" "))
        x = round(CODE_X + indent * CHAR_W, 2)
        parts.append(f'<text x="{x}" y="{y}"{bold}>{esc(line.lstrip(" "))}</text>')
    parts.append("</g>")
    parts.append(
        f'<text x="{CAP_X}" y="{height - CAP_UP}" font-family="{SANS}" '
        f'font-size="{CAP_FONT}" fill="#000">{esc(caption)}</text>'
    )
    parts.append("</svg>")
    return "".join(parts), width, height


PRICING = """FUNCTION COMPUTE_PRICES(PRODUCT)
    PW = PRODUCT.COST * 1.25 * 1.16
    PW = CEILING(PW / 5) * 5
    IF NOT PRODUCT.MANUAL_RETAIL THEN
        PR = PW * 1.15
        PR = CEILING(PR / 5) * 5
        PRODUCT.RETAIL = PR
    END IF
    PRODUCT.WHOLESALE = PW
END FUNCTION"""

SEARCH = """FUNCTION SEARCH(CATALOGUE, QUERY)
    MATCHES = empty list
    FOR EACH PRODUCT IN CATALOGUE.PRODUCTS
        SCORE = SIMILARITY(QUERY, PRODUCT.NAME)
        IF SCORE >= 0.70 THEN
            APPEND (PRODUCT, SCORE) TO MATCHES
        END IF
    END FOR
    SORT MATCHES BY SCORE IN DESCENDING ORDER
    RETURN FIRST 4 ELEMENTS OF MATCHES, OR ALL IF FEWER
END FUNCTION"""

IMPORT = """FUNCTION IMPORT_FILE(CATALOGUE, PATH, SHEET)
    REVIEW_LIST = empty list
    FOR EACH ROW IN SHEET
        // an empty cost is not a number, so this also catches missing costs
        IF ROW.NAME = EMPTY OR NOT IS_NUMBER(ROW.COST) THEN
            APPEND ROW TO REVIEW_LIST
        ELSE
            PRODUCT = NEW PRODUCT(ROW.NAME, ROW.COST, ...)
            CALL COMPUTE_PRICES(PRODUCT)
            IF ROW.RETAIL <> EMPTY THEN
                IF ROW.RETAIL <> PRODUCT.RETAIL THEN
                    PRODUCT.RETAIL = ROW.RETAIL
                    PRODUCT.MANUAL_RETAIL = TRUE
                END IF
            END IF
            ADD PRODUCT TO CATALOGUE
        END IF
    END FOR
    RETURN REVIEW_LIST
END FUNCTION"""

FIGURES = {
    "figure8_pseudocode_pricing": (PRICING, "Figure 8. Pseudocode — Pricing"),
    "figure9_pseudocode_search": (SEARCH, "Figure 9. Pseudocode — Search"),
    "figure10_pseudocode_import": (IMPORT, "Figure 10. Pseudocode — Import"),
}


if __name__ == "__main__":
    for name, (code, caption) in FIGURES.items():
        svg, w, h = figure(code, caption)
        svg_path = os.path.join(OUT_DIR, name + ".svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"{name}.svg  ({w}x{h})")
        if shutil.which("rsvg-convert"):
            subprocess.run(["rsvg-convert", "-o",
                            os.path.join(OUT_DIR, name + ".png"), svg_path],
                           check=True)
            print(f"{name}.png")
