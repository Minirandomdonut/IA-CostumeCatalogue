# Costume Catalogue

## Internal Assessment (IB Computer Science)

**Institution:** Tecnológico de Monterrey, Campus Ciudad de México (CCM)
**Program:** International Baccalaureate (IB) Diploma Programme
**Subject:** Computer Science
**Assessment Type:** Internal Assessment (IA)
**First assessment:** May 2027

---

## Project Overview

<!-- VICTOR — WRITE THIS YOURSELF (3–5 sentences, your own words).
     Say what the program is and who it is for. Points you can draw on:
       - a desktop catalogue program for a costume and regional-dress shop in Mexico City
       - the shop's stock currently lives in unstructured Excel sheets (~1,900 products)
       - the program stores products, prices them automatically, imports the old sheets,
         searches them, and exports category price lists
     Do not copy these bullets across — rewrite them as your own sentences. -->

---

## Problem Statement

<!-- VICTOR — WRITE THIS YOURSELF (one short paragraph + the bullet list below).
     Explain the problem in the client's terms: what goes wrong today, and why a
     spreadsheet is not enough. Things you found in the real data:
       - prices are recalculated by hand, so they drift and go stale
       - the same product appears on several sheets at different prices
       - rows are inconsistent: "OFERTA" written where a price should be, blank-name
         size-variant rows, title rows sitting in the middle of a sheet
       - nothing links a product to a photo
       - finding one product means scrolling, and a misspelling finds nothing -->

The program addresses this by providing:

* Automatic price calculation from a single cost figure.
* Persistent storage that survives closing the program.
* Bulk import of the existing Excel sheets, with doubtful rows flagged for review.
* Search that tolerates misspellings.
* Formatted PDF price lists per category.
* A graphical interface the shop owner can use unaided.

---

## Features

### Catalogue

* Add, edit and delete products.
* Each product holds name, category, supplier, cost, wholesale price, retail price and a photo.
* Every change is saved automatically; nothing is saved on exit.

### Pricing

* Wholesale price `Pw = cost × 1.25 × 1.16`.
* Retail price `Pr = 1.15 × Pw`.
* Both prices rounded **up** to the next multiple of 5 (an exact multiple stays put: 250 → 250).
* A retail price set by hand is kept; clearing it restores the formula.
* Prices are recalculated only when a product is created or its cost changes.

### Import

* Reads the shop's existing Excel workbooks, one sheet per run.
* A row is marked doubtful when the name is missing, or the cost is missing or not a number.
* The wholesale column already in the file is ignored — prices are always recomputed.
* Doubtful rows are collected and shown once, at the end, for manual correction.

### Search

* Fuzzy matching with `difflib`, at a similarity threshold of 0.70.
* Results sorted by similarity, then capped at the four best matches.
* Read-only: searching never modifies the catalogue.
* Results show the product photo, wholesale price and retail price.

### Export

* Filter by category, then export a formatted PDF price list.
* The list shows product name, wholesale price and retail price.
* Guards against exporting an empty category, and against cancelling the file dialog.

### Interface

* Six Tkinter screens: main menu, catalogue browser, product view, search, import review, export.
* One reusable product form serves add, edit, search-view and import-fix.

---

## Technologies Used

* Python 3
* Tkinter (GUI)
* `json` (persistent storage)
* `math.ceil` (price rounding)
* `difflib.SequenceMatcher` (fuzzy search)
* `openpyxl` / `xlrd` (Excel import, including legacy `.xls`)
* PDF generation library (export module)

---

## Educational Objectives

This project applies the following Computer Science concepts:

* Object-Oriented Programming — `Product`, `Catalogue`, `Storage`, and one class per module.
* Separation of concerns — the pricing constants and the save/load logic each exist in exactly one place.
* Algorithm design and justification — a deliberate linear scan for search, with its cost argued rather than hidden.
* File handling and data persistence.
* Handling messy real-world input, including partial and malformed records.
* Event-driven GUI programming.
* Systematic testing against defined success criteria — normal, boundary and abnormal cases.

---

## Development

The modules were built in dependency order, fixed during Criterion B:

```
Catalogue  →  Pricing  →  Import  →  Search
                                  →  Export
                                          →  UI
```

Development follows the IA Record of Tasks. The commit history of this repository
tracks that sequence:

| Record of Tasks | Module | Target date |
|---|---|---|
| 15 | Catalogue — `Product`, `Catalogue`, `Storage` | 10 Sep 2026 |
| 16 | Pricing | 14 Sep 2026 |
| 17 | Import | 24 Sep 2026 |
| 18 | Search | 28 Sep 2026 |
| 19 | Export | 30 Sep 2026 |
| 20 | User interface | 7 Oct 2026 |
| 21 | Testing — 15 planned tests | 15 Oct 2026 |
| 22 | Client test — owner unaided, timed | 16 Oct 2026 |

The design documents this code implements — flowcharts, class diagram, pseudocode and
wireframes — are in `figures/`, together with the Python scripts that generated them.

---

## Installation

Requires Python 3.

```bash
git clone https://github.com/Minirandomdonut/IA-CostumeCatalogue.git
cd IA-CostumeCatalogue
```

The catalogue file holding the real shop data is not part of this repository. To try the
program with sample data instead:

```bash
cp sample_catalogue.json catalogue.json
```

---

## Future Improvements

* Photo management directly inside the product form.
* Undo for deletions.
* Detection of duplicate products across imported sheets.
* Price history, so past cost changes can be reviewed.
* Multi-user access for shop staff.
* Backup of the catalogue file.

---

## Academic Integrity Statement

<!-- VICTOR — WRITE THIS YOURSELF. This is the section that matters most, so it has to
     be in your voice, not a template. Cover, in your own sentences:
       - this is your IB Computer Science IA at Tecnológico de Monterrey CCM
       - the code in this repository is written by you
       - why the repository exists: it is a dated record of how the program was built,
         one commit per Record of Tasks milestone
       - the design documents in figures/ were made on 28 August 2026, before this
         repository was created, so the first commits import existing work rather than
         create it — say that plainly
       - the client is a real shop; the business is anonymised in the IA, and its real
         product data (HALLOWEEN.xls) and working catalogue are deliberately excluded
         from this repository
     Then sign it. -->
