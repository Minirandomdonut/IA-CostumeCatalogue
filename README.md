# Costume Catalogue

## Internal Assessment (IB Computer Science)

**Institution:** Tecnológico de Monterrey, Campus Ciudad de México (CCM)
**Program:** International Baccalaureate (IB) Diploma Programme
**Subject:** Computer Science
**Assessment Type:** Internal Assessment (IA)
**First assessment:** May 2027

---

## Project Overview

Costume Catalogue is management software developed entirely in Python as part of
the International Baccalaureate (IB) Computer Science Internal Assessment (IA).

The objective of this project is to provide a clothing business with an updated
database capable of computing price calculations, importing old Excel lists,
searching them and exporting product registers for client usage fast and efficiently.

Unlike traditional Excel lists, this interface is friendly for people inexperienced
with lists and is tolerant of misspelled words. Moreover, it allows for local management,
which means the users do not require an internet connection for it.

---

## Problem Statement

The owner of a shop business in downtown Mexico City has experienced growth in retail customers since the pandemic,
as a result, coordination with clients and providers has become increasingly messy. Prices for ~1900 products live in
inconsistently formatted and separate Excel lists, so when a supplier changes cost, cost and retail prices must be
rewritten by hand everywhere. Moreover, when clients ask about costume information, employees have to look at these lists
again and create versions for the clients, with photos. These methods are prone to human errors, which are quite common
on the lists: mixed results, wrong computations, wasted opportunity cost for the staff and slow responses for the
clients. As a matter of fact, many of these lists were outdated or had price errors. Alternatives such as better Excel
organization fail as they cannot search misspelled words, hold product exceptions or easily purge legacy data.



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
* Tkinter
* `json`
* `math.ceil`
* `difflib.SequenceMatcher`
* `openpyxl` / `xlrd`
* PDF generation library

---

## Educational Objectives

This project applies the following Computer Science concepts:

* Object-Oriented Programming (OOP)
* Problem decomposition
* Algorithmic design and justification
* File handling and data persistence.
* Handling messy real-world inputs.
* Event-driven GUI programming.
* Testing and iterative development.
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

This project was developed as part of the International Baccalaureate (IB) Computer Science Internal Assessment at Tecnológico de Monterrey, Campus Ciudad de México.
The client is a real shop, and its private information is deliberately kept out for privacy concerns.
I confirm that this work is my own work, registered as it has evolved. I have acknowledged each use of the words or ideas of another person, whether written, oral or visual.

-Mini
