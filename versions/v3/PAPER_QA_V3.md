# PAPER QA — V3

Quality report for *Before the Backtest: Pre-Freeze Common-Support Ceilings for Event-Driven
Strategy Research*, **V3**, 2026-10-11.

**Audit command:** `.venv/Scripts/python -I scripts/paper_audit_v3.py`

```
[freezes]     V1+V2 files 10 | changed 0
[claim]       distinct numeric tokens 85 | unsupported 0
[required]    checks 24 | failures 0
[verdicts]    labels 4 | failures 0
[breadth]     usually=2, typical=2
[length]      body 6,822 words | total 8,656 words
RESULT: PASS (0 issues)
```

---

## 1. Version integrity

**All ten frozen files are byte-identical.** The audit checks them first and exits with status 2
without running anything else if one has moved.

| version | files checked | changed |
|---|---|---|
| V1 (`52a980a`) | 5 | **0** |
| V2 | 5 | **0** |

V3 writes only inside `papers/falsification_first_alpha_discovery/v3/`.

## 2. Single contribution

Verified mechanically in three places and by reading:

| location | statement |
|---|---|
| abstract | "We describe and apply a narrower variant: a **pre-freeze common-support ceiling**…" |
| §1.5 | "The **contribution** is the pre-freeze common-support ceiling of §2…" |
| §9 | "Identification feasibility is itself a pre-analysis empirical object, and it can be measured before outcome access." |

The four co-equal contributions of V2 are gone. V2's procedures 1, 2 and 4 are now **supporting
cases** (§6.1) or a **supporting method** (§2.5), explicitly subordinate. The ten principles are cut
to four in the body, with the remaining six in Appendix E.

## 3. Domain

§1.4 states the domain explicitly: event-driven systematic research; event populations from public
institutional documents and venue archives; free or public historical data; matched or controlled
event designs; time-varying eligibility. It states what the claims are **not** about.

The breadth audit found four occurrences of `usually` / `typical`, each reviewed:

| line | text | verdict |
|---|---|---|
| §2.3 | "the realised count is at most `S_e` and typically below it" | technical, about sampling |
| §3 | "the data quality was unusually good" | descriptive |
| §7 | "**not** the typical binding constraint across the whole program" | **negation** |
| §7 | "We do **not** argue that upstream feasibility is usually the binding constraint" | **negation** |

Banned broad phrasing — "alpha discovery", "feasible for small capital", "framework proves",
"improves returns" — appears **zero** times.

## 4. Registry and denominator

Preserved and visible. §7 reports 31 entries, the terminal-state distribution including **9 economic
rejects** and **1 promotion**, the fact that the promoted family was later archived, and the required
retrospective-selection statement. Appendix B carries the full entry-by-entry table. §7 states
plainly that the denominator does **not** support a broad thesis and that the paper does not advance
one; it then narrows to a domain-level statement and names the two competing explanations it cannot
separate.

## 5. Verdicts — unchanged

| family | V3 label | changed from V1/V2? |
|---|---|---|
| H18.3 | `PRE-REGISTERED NULL`, with the bounded interpretation | **no** |
| H19.2 | `DESIGN INFEASIBLE UNDER THIS SPECIFICATION` | **no** — this is the V2 `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL` state restated in the procedure's own vocabulary; the substance is identical and §2.4 states it is not a null, not a rejection, hypothesis untested |
| H14 parent | `OPEN` | **no** |
| H13 | `IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED` | **no** |
| H19.0 | capacity screen; distribution reported | **no** — the 32 is demoted to one operating point |

## 6. H19.0 liquidity

Reported as a **distribution** in Appendix A.1: 3.17% of the 63 clean events at ≤0.10% (2 events),
33.33% at ≤0.50% (21), 50.79% at ≤1.00% (32). The text states that the distribution is the result
and the 1% operating point is an engineering judgement. The 32 is retained and demoted; it does not
appear in the abstract, in §4, or in any figure title.

The section states that this is a screen, not an execution analysis, and lists the eight missing
ingredients.

## 7. H19.2 — the central result, and its blindness

§4.3 and §4.4 carry it: 62 candidates, floor 20, realised support p10 0 / p25 0 / median 1 / p75 2 /
p90 57, 52 of 62 below the floor, full-pool ceiling 0–27 with a median of 7, 3 of 25 dates reaching
20, N\* = 10 against N_min = 40.

Outcome-blindness is established at §2.5 and §4.5 with the loader evidence. §2.4 states that the
status is a statement about the design, not about the world, and that filing an infeasible design as
a null would accumulate a literature of absences that were never measured.

## 8. Novelty — bounded against prior work

The audit requires, and finds, all of: the cautious formulation ("We are not aware of prior work
that operationalises…"), credit to Rubin (2008), an explicit disclaimer that the design-stage
rejection principle is Rubin's, and an explicit "We do **not** claim" list.

| claim | prior work cited | what V3 claims |
|---|---|---|
| design stage without outcome data; reject a dataset for lack of overlap | **Rubin (2008)** | nothing — explicitly credited |
| outcome-free two-stage design, codified | Li (2023) | nothing |
| design-stage overlap diagnostics run before outcome use | `PSweight` design module | nothing |
| positivity, structural vs practical violations, remedies | Petersen et al. (2012) | nothing |
| the **combination**: full-population, point-in-time, pre-freeze, outcome-blind, with a pre-registered numeric stop rule, for matched event studies in systematic strategy research | — | "we are not aware of prior work that operationalises… in this exact form", with an explicit fallback that if it exists, the contribution reduces to the §4 demonstration |

The word "first" appears nowhere as a priority claim. §2.6 separates inherited components from the
added combination, item by item.

## 9. Claims

| | |
|---|---|
| distinct numeric tokens in the V3 body | 85 |
| **unsupported** | **0** |
| `CLAIM_EVIDENCE_MATRIX_V3.csv` rows | **160** (126 from V1, 24 from V2, 10 new) |
| `INTERNAL_EMPIRICAL` | 141 |
| `EXTERNAL_LITERATURE` | 16 |
| `OFFICIAL_VENUE` | 3 |

The token count fell from 192 (V2) to 85 because the registry detail, threshold inventory and defect
material moved to appendices, which the audit excludes from the body scan. Those appendix numbers
remain in the matrix.

## 10. No new experiment

**Zero.** No script that loads market data was run. The programs executed were
`paper_build_v3.py` (reads committed JSON and copies committed figures and tables) and
`paper_audit_v3.py` (reads manuscripts and hashes files). Nothing in Bucket 3 of the V2 revision plan
was executed: no threshold sensitivity, no two-way or block bootstrap, no alternative H19.2 matching,
no price load, no order-book study, no independent reconstruction, no new return.

No gate, verdict, pre-registration or historical artefact was altered.

## 11. Length and structure

| | V1 | V2 | V3 |
|---|---|---|---|
| body words | 9,394 | 10,786 | **6,822** |
| total words | 9,753 | 11,643 | 8,656 |
| figures | 6 | 6 | **4** |
| body tables | 5 | 5 + 2 authored | **3** |
| appendix tables | — | — | 6 |
| references | 14 | 22 | **25** |
| principles in the body | 10 | 10 | **4** |
| taxonomies in the body | 3 | 3 | **0** (all in appendices) |

**The body is 6,822 words against a 7,000–8,500 target.** This is a deliberate shortfall rather than
a padding opportunity: the material that would close the gap is the registry detail, the threshold
inventory and the defect taxonomy, all of which were moved to appendices precisely because the
referee judged them to be competing with the contribution. Total length including appendices is
8,656 words, inside the range.

## 12. Known limitations of this QA process

- The claim audit matches numeric tokens, not their placement; placement was checked by reading.
- The required-statement audit matches by regular expression; a statement can be present and badly
  placed.
- The breadth audit uses a fixed phrase list and cannot detect an unbounded generalisation phrased
  without those words.
- **The manuscript has never been compiled.** No LaTeX distribution and no `pandoc` are available
  here; `paper_v3.tex` is generated from `paper_v3.md` by a committed converter and is syntactically
  unverified.
- **No public repository or DOI**, and **no independent verification of any result**. Both remain
  release blockers.
