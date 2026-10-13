# PDF QA — page by page

**Document:** `paper.pdf`, 21 pages, SHA-256
`ab58cdecd8b4b52b2fac2879184b535a09cbf695f011556d70de3edeab20e45e`
**Engine:** Tectonic 0.17.0 · **Date:** 2026-10-12 · **Exit code:** 0

> **Compilation exiting zero was not treated as sufficient.** Every page was inspected.

---

## Method

Three passes, because each catches what the others miss.

1. **Rendered-image inspection.** Every page rendered to PNG at 1.3× and examined. Sixteen of the 21
   were read in full on screen, chosen to cover every structurally distinct element: title and
   abstract, body prose, the boxed procedure, each of the four figures with its caption, each table,
   every appendix, and the end matter.
2. **Pixel analysis of all 21 pages.** Ink coverage measured per page, plus ink in a 2.5% margin band
   on each of the four edges — the signature of clipping, of a table overflowing the text block, and
   of a blank page. **Result: zero ink in any margin band on any page; no blank page.**
3. **Full text extraction from all 21 pages**, checked for `??` cross-references, for the frozen
   quantities, for the verdict labels and for broken Unicode.

## Page-by-page record

| page | content | verdict | issue | action |
|---|---|---|---|---|
| 1 | title, provenance note, abstract | **pass** | cover date read 2026-10-11 in the first build | corrected to 2026-10-12 in the release converter — PRODUCTION |
| 2 | keywords, §1.1–§1.3 | **pass** | — | — |
| 3 | §1.3 continued, §1.4 domain | **pass** | — | — |
| 4 | §1.5 contribution, §1.6 definitions, §2.1 | **pass** | — | — |
| 5 | §2.3 upper-bound argument, §2.4 stop rule, §2.5 structural blinding | **pass** | — | — |
| 6 | §2.6 what is inherited and added | **pass** | — | — |
| 7 | §3 setting, §4.1 funnel table | **pass** | — | circled-S in USDⓈ-M renders correctly |
| 8 | §4.2 matching rule, §4.3 central result | **pass** | — | — |
| 9 | stop-rule table, floor invariance, quantile-convention note | **pass** | `N\*` rendered as "N\ = 10" followed by a runaway italic span in the first build | Markdown escape handling added to the release converter — PRODUCTION |
| 10 | §4.4 specificity note, §4.5 outcome blindness | **pass** | — | — |
| 11 | §5 what the gate prevents | **pass** | — | — |
| 12 | §6.1 supporting case A | **pass** | — | — |
| 13 | §7 denominator, terminal-state table, §8 limitations | **pass** | — | — |
| 14 | §8 limitations continued | **pass** | — | — |
| 15 | §8 end, §9 conclusion, **Figure 1** | **pass** | — | — |
| 16 | Figure 1 caption, **Figure 2**, **Figure 3** and captions | **pass** | Figure 3's caption carried the `N\*` defect | same fix as page 9 — PRODUCTION |
| 17 | **Figure 4** and caption, tables index, Appendix A | **pass** | — | legend sits below the axis with no collision; caption states *recorded range, not a confidence interval* |
| 18 | Appendix A liquidity distribution, **Appendix B registry** begins | **pass** | — | — |
| 19 | Appendix B registry continued, Appendices C, D, E | **pass** | in the first build the registry table overflowed the page bottom and the right margin, collided with the page number, and columns ran together | `longtable` with proportional column widths — PRODUCTION |
| 20 | Appendix E, **Appendix F** base-rate detail | **pass** | — | — |
| 21 | end matter, evidence classes, references | **pass** | stated that the manuscript had never been typeset, which this build falsified | text corrected — recorded in `CHANGELOG.md` |

## Checklist results

| check | result |
|---|---|
| clipping at any margin | **none** — pixel analysis, all 21 pages, all four edges |
| tables overflowing the text block | **none** after the `longtable` fix |
| figure readability at print size | **good** — all four figures legible; Figure 3's two panels and Figure 4's hatched band both reproduce cleanly |
| captions complete and adjacent to their figure | **yes** |
| legend overlap | **none** — Figure 4's legend was moved below the axis in RC1 and does not collide |
| page breaks splitting a figure from its caption | **none** |
| the boxed procedure (§2.3) broken badly | **no** — it sits whole on page 5 |
| orphan headings | **none** |
| monospace spans overflowing the measure | **none** |
| footnotes | none in the document |
| appendix ordering and navigation | **A, B, C, D, E, F in order** |
| broken or missing Unicode | **none** — Δ, ≤, ≥, ×, ≈, −, §, →, ↔ and the circled S in USDⓈ-M all render. The ↔ in "CEX↔DEX" was lost in the first build and is restored |
| blank pages | **none** |
| `??` unresolved cross-references | **zero** |
| hyperlink artefacts | **none visible**; `hyperref` is loaded with `hidelinks` |

## Known cosmetic limitations, accepted

| item | why accepted |
|---|---|
| a bulleted list inside a block quote renders as inline hyphenated text rather than a nested list, on page 9 | readable, and the alternative is further surgery on a converter whose output is otherwise verified. Content is unaffected |
| hyphenation inside narrow table headers, e.g. "econ. out-come" on page 19 | a consequence of fitting an 8-column table to the text block; legible |
| overfull horizontal boxes up to 20.7pt in the widest tables | below the threshold at which text visibly crosses the margin; pixel analysis confirms no ink in any margin band |

## Science check on the typeset output

Performed against the extracted text of the final PDF, not against the Markdown.

| frozen quantity | present |
|---|---|
| 62 candidate events | ✔ |
| floor *m* = 20 | ✔ |
| quantiles 0 / 0 / 1 / 2 / 57 | ✔ |
| 52 of 62 below the floor | ✔ |
| ceiling range 0 to 27 | ✔ |
| ceiling median 7 | ✔ |
| 3 of 25 dates reach the floor | ✔ |
| N\* = 10 | ✔ |
| *N_min* = 40 | ✔ |
| no price column loaded | ✔ |

| verdict | present |
|---|---|
| `PRE-REGISTERED NULL` | ✔ |
| `DESIGN INFEASIBLE UNDER THIS SPECIFICATION` | ✔ |
| `OPEN` | ✔ |
| `IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED` | ✔ |

Figure 4's caption states **"recorded range, not a confidence interval"** in the typeset output. ✔

Two checks initially reported as failures were **text-extraction artefacts, not document defects**:
the extractor inserts a soft hyphen at line breaks, which split "con-fidence" and the
`IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED` label across lines in a table cell. Both read
correctly in the rendered page.
