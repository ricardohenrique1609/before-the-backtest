# PAPER QA — V1

Quality report for *Falsification-First Alpha Discovery*, version 1, 2026-10-11. Four audits were
run against the finished manuscript: claim, language, status and internal consistency.

---

## 1. Unsupported numerical claims: **0**

**Target met.** Every numeric token in the manuscript body resolves to a row of
`CLAIM_EVIDENCE_MATRIX.csv`, excluding section numbers, calendar years and small integers used as
counts within a sentence.

| | |
|---|---|
| distinct numeric tokens in the body | 252 |
| unsupported after audit | **0** |
| matrix rows | **126** |
| status `VERIFIED` (artefact field read in this session) | 110 |
| status `ARTEFACT_CITED` (recorded in a committed document, not re-derived) | 16 |

The audit is reproducible: it strips section headings and cross-references, extracts every numeric
token from the body, and tests each against the matrix in both comma-stripped and
trailing-zero-stripped form.

**Numbers added to the matrix during the audit (17 new rows plus 2 extended):** the H15 sampling
figures, the H16.1 parsed-document count, the H17.0 identity and label-free survivorship fields, the
H18.1b era-defect correction, the H18.2 risk-set-entry differential, four H18.3 fields, the H19.0
rounded share, two external-literature figures, and the abstract's rounded forms. Two existing rows
were extended to carry both the fractional and the percentage form of the same value.

**Numbers removed from the manuscript because no artefact supports them:** the H15 split into
initial filings and amendments (see §4 below), the H15 cover-page count, and the H17.0 "symbol
printed in the filing in 98.9%" figure, which conflated two different gate fields. In each case the
number was deleted rather than weakened.

---

## 2. Language audit

Every occurrence of the flagged vocabulary was reviewed individually.

| term | occurrences | verdict |
|---|---|---|
| prove / proved / proves | **1** (`proven`) | **justified.** It appears in a denial: "not 184 events *proven* to have had no notice". The sentence exists to prevent a coverage limit being read as evidence of absence. |
| obvious, obviously, clearly | 0 | — |
| always | 0 | — |
| never | 13 | **justified.** All are statements of fact about what this program did or did not do ("raw data is never edited", "bot protections were never circumvented", "the OHLC columns never entered memory"), or about what the paper itself does not claim. The one rhetorical use — a claim that a professional desk "would never notice" a capacity constraint — was **softened to "would rarely encounter"** during this audit. |
| guaranteed | 0 | — |
| caused / causes | 0 | — |
| insider | 3 | **justified.** One is the name of the SEC data product ("insider transaction records"); one reports what the equity literature found, attributed to that literature; one is the explicit disclaimer that this paper does **not** transfer the term to the events it studies. |
| profitable | 1 | **justified.** It appears only in the H19.0 disclaimer: "Nothing here implies that shorting delistings is or is not profitable." |
| alpha | 4 | **justified.** The title, the abstract's "apparent alpha", an explicit denial ("neither is a claim about alpha"), and one occurrence of the literal word as the token that a filter bug matched. |
| demonstrate / demonstrated | 4 | **justified.** Each refers to a measurement reported in this paper, not to a general claim about markets. |

**Hindsight language.** No instance found in which a defect's discovery is narrated as though it had
been anticipated. The silent-failure classes are reported with the plausible output they produced
first, and the detection second.

**Overclaim.** One instance found and softened (above). The four case-study conclusions were checked
against their verdicts and none overstates: H13 rejects an implementation and records the economic
question as unresolved; H18.3 is explicitly not described as a near miss; H19.0 states that no return
was computed; H19.2 states that no economic inference exists.

---

## 3. Result-status audit: **0 unresolved issues**

All eleven `**Verdict.**` lines were checked against the gate artefacts, and every family reference
was checked for proximity to a mislabelling term.

| family | status in the paper | correct |
|---|---|---|
| H13 | `ECONOMIC REJECT` of the implementation; economic hypothesis **unresolved** | yes |
| H14 | `OPEN` (parent); `DATA-GATE FAIL / UNTESTED` (three sub-families) | yes |
| H15 | `DATA-GATE FAIL / UNTESTED`, 5 of 22 | yes |
| H16.1 | `DATA-GATE FAIL / UNTESTED`, 2 of 23 | yes |
| H17.0 | `INFRASTRUCTURE BLOCKED`, 14 of 32 | yes |
| H18.0 / H18.0b | `INFRASTRUCTURE BLOCKED` as a gate / `PASS` 14 of 14 | yes |
| H18.1 | `PARTIAL PASS`, 11 of 12 | yes |
| H18.1b | `STRONG PASS`, 19 of 19, two named diagnostics below bar | yes |
| **H18.3** | **`PRE-REGISTERED NULL`** — tested; the data and design survived | yes |
| **H19.0** | **`PARTIAL PASS`**, 12 of 15; small-capital thesis fails the sample and liquidity gate | yes |
| **H19.2** | **`BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL`** | yes |

**H19.2 is never called `NULL` or `REJECTED`.** A proximity search for those terms within 160
characters of every `H19.2` and `H19-P3A` mention returned one match, which is a false positive: the
introduction's sentence about H18 returning a null is followed by a separate sentence about H19.2.

**H14 is never described as an economic null.** It is `OPEN`, with three gated sub-families.

---

## 4. Internal consistency audit

| check | result |
|---|---|
| H13 denominators, 52.9% versus 50.1% | **explicit.** A set-off note in §4.1 states that 52.9% belongs to the 5,604-CIK screen candidate universe and 50.1% to the 1,197-company Test A panel, and that they must not be used interchangeably. |
| H18.3 event accounting, 110 + 72 + 86 | **explicit.** A set-off note in §6.4 states that the sum of 268 is not a count of distinct delistings, explains the overlap through the 365-day horizon, and states that development and holdout share zero events. |
| H19.0 notice coverage, 184 | **explicit.** §7 states that 184 is a limit of the official surfaces reached, not 184 events proven to have had no notice, and that the ordering subgroup is not estimable rather than null. |
| H19.0 margin, `UNKNOWN` | **explicit.** §7 states that margin shortability is `UNKNOWN` rather than zero, and that the funnel is therefore a **lower bound** on shortability. |
| F3 panel b arithmetic | **corrected during this work.** The first version decomposed 84 + 119 = 203. The crosswalk records 82 shared episodes; the two that do not appear (AUD, GBP) are fiat quote assets. The panel and the manuscript now read 82 + 75 + 39 + 5 = 201. |
| Table 1 gate counts | **corrected during this work.** The build script preferred integer gate fields and rendered five families as "0 of 0"; the earlier gates store a string such as `"5/22"`. Both schemas are now read. |

### Discrepancy found and recorded, not resolved

`H15_13D_GATE.json` records 23,187 initial filings and 70,849 amendments; the hypothesis ledger
records 33,196 and 60,840. Both sum to 94,036. Resolving it requires re-deriving the classification
over the full index, which this phase forbids. The manuscript therefore **omits the split entirely**
and reports only the three figures that agree across artefacts. Recorded as `PAPER_OPEN_QUESTIONS.md`
Q12.

---

## 5. Citations

| | |
|---|---|
| entries in `references.bib` | 14 |
| full text read | 4 (Yang & Kwon 2026; Ammann et al. 2022; the dead-coins preprint; the 2019 listings study) |
| **abstract or metadata level only** | **7**, each flagged in its own `note` field |
| PDF level (preprint or working paper) | 2 |
| access level not recorded by the source review, and therefore not claimed | 1 |
| entries with no author field | 8 |

No DOI, volume, issue, year or author was invented. Where the committed literature reviews recorded
no authors or no given names, the entry carries none and its note says so. Four entries were
**corrected during this audit** by removing given names that the source reviews did not record
(Ammann et al., Aldhahi & Alsamaani, Ackerer et al., Fantazzini), and one unverified subtitle was
removed.

The three evidence classes are kept separate: `references.bib` contains academic literature only,
official venue documentation is reached through the artefact index, and internal QIE artefacts
through the claim–evidence matrix.

---

## 6. Figures and tables: **6 of 6, 5 of 5**

| planned | produced | notes |
|---|---|---|
| F1 research lifecycle | yes | structural; its only quantities are gate outcomes |
| F2 gate outcomes by family | yes | reads `criteria_passed` from each gate |
| F3 lifecycle reconstruction | yes | two panels; arithmetic corrected during this work |
| F4 rolling origin versus holdout | yes | holdout separated by a rule, differently coloured, and annotated as a different evaluation role; no line connects it to the folds |
| F5 execution funnel | yes | 201 → 75 → 64 → 63 → 32 |
| F6 common-support collapse | yes | two panels, justified in the caption; panel b plots markers, not a line, and states that it shows the 8 of 25 dates the artefact records |
| T1–T5 | yes | all five generated by `scripts/paper_build_tables.py` |

Every figure writes its plotted values to `figures/data/*.csv` with a provenance line. Both build
scripts pass `ruff`. All six figures are embedded in `paper.md` and, through the converter, in
`paper.tex` as `\includegraphics` blocks.

---

## 7. Build status

| output | status |
|---|---|
| `paper.md` | **canonical.** All edits are made here. |
| `paper.tex` | **generated** by `scripts/paper_md_to_tex.py` from `paper.md`, so the two cannot diverge. |
| PDF | **not built.** Neither `pandoc` nor a LaTeX distribution (`pdflatex`, `xelatex`, `tectonic`) is present in this environment. The PDF was declared optional and no effort was spent on toolchain installation. The `.tex` targets a standard `article` class with `geometry`, `graphicx`, `microtype`, `csquotes` and `hyperref`, and compiles tables as `tabular` blocks. |

The converter is a small, deliberately limited Markdown subset handler covering exactly the
constructs the manuscript uses. It has not been tested against a LaTeX compiler, because none is
available here; that is a known and stated limitation rather than a silent one.

---

## 8. Open questions

Twelve entries in `PAPER_OPEN_QUESTIONS.md`. **Q1 is now `RESOLVED`:** the research program accepts
`STOP` for H19-P3A, so the confirmatory design remains blocked, the control bars are not relaxed, and
no price is loaded. Q3 and Q9 are recorded as resolved reconciliations rather than open items. The
remaining items are genuine gaps: H13's unresolved economic question, derivative-notice coverage,
historical margin eligibility, H14's open status, three events whose traded reality outran their own
notices, the H10 known issue, literature access levels, and the newly recorded H15 split discrepancy.

**No open question was resolved by computation.** No new experiment was run, no return was computed,
no price was loaded, and no gate, verdict, pre-registration or historical artefact was altered during
the writing of this paper. The single edit ever made to a historical artefact — a correction note in
`H18_1B_DATA_AUDIT.md` — predates this work and is marked as a correction in the document itself.

---

## 9. Known limitations of this QA process

- The claim audit matches **numeric tokens**, so it verifies that each number has an artefact behind
  it, not that each number is used in the right sentence. The latter was checked by reading.
- The language audit uses a fixed vocabulary list. It cannot detect overclaim expressed without those
  words, and the judgement about each occurrence is the author's.
- The status audit checks labels and proximity. A sentence could in principle imply a wrong status
  without using any of the searched terms; the eleven verdict lines were therefore also read in full.
- `ARTEFACT_CITED` rows (16 of 126) were taken from committed documents and not re-derived from the
  underlying data in this session. They are marked so a reader can tell the difference.
