# Development log — Criterion D (Record of Tasks 15–17)

Working notes kept while building the catalogue program. Dates are the days the
work actually happened. Code is in this repository; this file records the
decisions, the reasons and the test results that the Criterion D write-up draws
on. Success criteria (SC1–SC8), figures and the testing table are the ones fixed
in Criteria B and C.

---

## Status

| RoT | Task | Done | Evidence |
|---|---|---|---|
| 15 | Catalogue module (Product, Catalogue, Storage) | 10 Sep 2026 | console add/edit/delete, persists across reopen |
| 16 | Pricing module (`PricingModule.compute`) | 12 Sep 2026 | console checks below (SC1, SC2) |
| 17 | Import module (`ImportModule.import_file`) | 13 Sep 2026 | test 12 on the real sheet: 50 of 50 (SC7) |
| 17b | Optional retail column + made-up test file for tests 13, 14 | pending | — |
| 18 | Search module (Figure 9) | next, target 28 Sep | — |

---

## RoT 16 — Pricing (12 Sep 2026)

**Design followed.** Figure 3 (flowchart) and Figure 8 (pseudocode), line for
line: wholesale first, ceiling to the next multiple of 5, then the manual-retail
gate, then retail. Rounding uses `math.ceil` as the CEILING abstract function.

**Rounding check.** Floating-point error could push an exact multiple of 5 a
hair above itself and make ceiling jump to the next multiple (e.g. 290 → 295).
Every whole-peso cost from 1 to 10 000 was compared against exact fraction
arithmetic: zero mismatches, so the boundary rule "an exact multiple stays put"
holds (testing table, test 2).

**Where pricing is called from.** Figure 2 calls the pricing module on create
and on cost change. Implemented as: `Catalogue` owns one `PricingModule`
(created in its constructor) and calls it inside `add()` and inside `edit()`
when the cost changed. Import therefore never calls pricing itself; it only
adds products. One pricing path, one place to change the constants.

**`edit(product, changes)` — decision.** Figure 7 originally showed
`edit(product)`, but a method that only receives the product cannot know which
field changed. Three options were considered:

- A. `edit(product, new_cost)` — handles cost only.
- B. `edit(product, changes)` with a dictionary of changed fields; pricing runs
  only if `"cost"` is a key. Chosen: it maps one-to-one onto Figure 2's
  "Enter changes → Cost changed?" and extends to other fields later.
- C. Keep `edit(product)` and move the "cost changed?" test into the UI —
  rejected, it would scatter pricing logic across modules.

Figure 7 updated to `edit(product, changes)` (13 Sep).

**SC2 second half (clearing a manual retail).** Figure 2 re-prices only on
cost change, so a cleared manual retail with an unchanged cost would never get
its formula price back. `edit` therefore also handles a `"retail"` key: a
number sets the manual retail and flag; `None` clears the flag and re-runs
pricing. Documented as a refinement of Figure 2 for test 5.

**Console checks (SC1, SC2).** Products are invented (dev harness, not in repo).

| Case | Wholesale | Retail | Manual |
|---|---|---|---|
| add, cost 275 | 400 | 460 | no |
| add, cost 275, retail given 440 | 400 | 440 | yes |
| edit cost → 200 (boundary, test 2) | 290 | 335 | no |
| manual product, edit cost → 300 (test 4) | 435 | 440 kept | yes |
| clear manual retail (test 5) | 435 | 505 restored | no |

**Slips fixed along the way** (worth a sentence in D as development
narrative): a setter was called with the wrong price (`set_retail` given the
wholesale value — would have overwritten every manual retail, SC2 failure);
assignments left on the left of setter calls creating stray public attributes;
an `else` attached to the wrong `if` in `edit`.

---

## RoT 17 — Import (13 Sep 2026)

**Library.** All the shop's lists are legacy `.xls`, so `xlrd` (reads `.xls`
only; `openpyxl` is `.xlsx` only). Cite xlrd's documentation in the sources
strand.

**Data preparation (not code).** The real workbook `HALLOWEEN.xls` (kept out of
the repo — it holds live supplier names and cost prices) has four sheets. The
target sheet, Hoja4, originally ended with a block of accessories that carried
two hand-written prices (wholesale and retail) instead of a cost, because the
owner had not had time to cost them. With the owner's permission that block
(rows 164–217) was removed from the working copy; the program covers the
costume list only. The original workbook is kept as a backup. Consequence: the
sheet has no retail column, so Figure 10's retail comparison is exercised by a
made-up test file (tests 13, 14), not by the real data.

**Row validity rules (`_is_number`).** Decided before coding:

| Cost cell | Result |
|---|---|
| text such as "OFERTA" | review |
| empty | review |
| zero or negative | review (refinement — Figure 10 did not state it) |
| number stored as text, e.g. "275" | accepted by conversion |

**Refinement: blank rows are skipped.** Hoja4 has spacer rows where every cell
is empty. Figure 10 as approved would send each to the review list as "name
missing", filling the owner's review list with about 15 useless lines per
import. Decision: a row whose cells are all empty is skipped before the name
check. Figures 4 and 10 updated (13 Sep). Alternative kept in mind: leave
Figure 10 untouched and accept the noise.

**Other implementation decisions.**
- Names and supplier strings have their internal runs of spaces collapsed
  (the sheet pads names with dozens of spaces before the size). Needed for
  readable screens and for the search similarity in RoT 18.
- Category = sheet name (the only category the file gives). Owner can rename
  later in the UI.
- Review entries carry exactly Figure 15's columns: Excel row number, name (or
  "(empty)"), cost cell, problem text ("name missing" / "cost missing or not a
  number").
- No save inside import (persistence belongs to the main loop, SC3 design).
- Import touches `Product` only through its constructor; it never calls
  pricing directly.

**Test 12 — the 50-row answer key (SC7).** Rows 85–134 of Hoja4 were
hand-classified first (answer key kept locally; it contains real cost prices).
The window was chosen because it contains every kind of row in the file: clean
costume rows, rows with a missing cost, a mid-sheet title row, blank spacer
rows and an accessories block with no costs at all.

| | Imported | Review | Skipped (blank) |
|---|---|---|---|
| Hand-classified answer key | 21 | 25 | 4 |
| Program output, same rows | 21 | 25 | 4 |

Every row matched: 50 of 50 (SC7 target: 45). Whole sheet: 101 imported, 55
review, 7 skipped. The review list correctly catches the title rows at the top
of the sheet ("CHIDO BOUTIQUE", "HALLOWEN", the header row) and the
accessories with no cost.

**Abnormal case.** A sheet with no data rows returns an empty review list and
adds nothing — no crash.

**Slips fixed along the way.** Method defined as `is_number` but called as
`_is_number`; `except ValueError or TypeError` (only catches the first — needs
a tuple); `return` placed inside the row loop so only the first product was
imported; wrong method name `add_product` for `Catalogue.add`.

---

## Figure revisions (all dated 13 Sep 2026, generator scripts carry the same note)

- **Figure 4** — "Blank row?" decision inserted after "Read next row".
- **Figure 7** — `Catalogue` shows `-pricing : PricingModule` and
  `+edit(product, changes)`; `Product` shows its getters/setters;
  `ImportModule` shows `-catalogue : Catalogue`; the "ImportModule calls
  PricingModule per row" dependency removed (pricing now runs inside
  `Catalogue.add`).
- **Figure 10** — blank-row skip added; review check split into the name and
  cost branches with their problem text; "add to catalogue" annotated as the
  step that triggers pricing. Retail comparison lines unchanged.

Rule followed throughout: when code and figure disagree, one of them is
changed and the change is dated — never silent drift.

---

## Open items

1. **RoT 17b.** Read an optional retail column (only present in the made-up
   test file), compare it with the formula retail and flag manual when they
   differ — the last block of Figure 10. Build the test file for tests 13 and
   14 (a row whose retail equals the formula → automatic; a row with retail 240
   where the formula gives 220 → manual, asterisk shown).
2. **RoT 18, Search** — Figure 9: linear scan, `difflib.SequenceMatcher`
   ratio ≥ 0.70 as a named constant, sort descending before the 4-result cap.

## Notes for the write-up

- Word budget for D is about 1 000 words; the TAR (technique / alternative /
  reason) candidates above are: ceiling-to-5 rounding; where pricing is called
  from; `edit(product, changes)`; blank-row refinement; manual-retail inference
  by comparison (once 17b exists).
- Evidence available: console outputs in the two tables above, the test 12
  totals, and the dated figure revisions.
