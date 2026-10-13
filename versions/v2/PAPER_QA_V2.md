# PAPER QA — V2

Quality report for *Falsification-First Alpha Discovery*, **V2**, 2026-10-11. Run after both revision
passes (MUST FIX, then SHOULD FIX and OPTIONAL).

**Audit command:** `.venv/Scripts/python -I scripts/paper_audit_v2.py`

```
[v1 freeze]   files 5 | changed 0
[claim]       distinct numeric tokens 192 | unsupported 0
[status]      labels 5 | failures 0
[must-fix]    checks 24 | failures 0
[language]    prove=6, proves=3, proven=3, never=15, insider=2, profitab=2, alpha=1, demonstrat=5
[literature]  entries 22 | without an access statement 0
RESULT: PASS (0 issues)
```

---

## 1. Claims

| | |
|---|---|
| distinct numeric tokens in the V2 body | 192 |
| **unsupported** | **0** |
| `CLAIM_EVIDENCE_MATRIX_V2.csv` rows | **150** (126 carried from V1, 24 new) |
| `INTERNAL_EMPIRICAL` | 134 |
| `EXTERNAL_LITERATURE` | 13 |
| `OFFICIAL_VENUE` | 3 |

Evidence categories are never blended within a claim: each row carries exactly one. Numbers taken
from published work are tagged `EXTERNAL_LITERATURE` and carry the bibliography key they came from,
so a reader can tell a measurement of this program from a measurement of someone else's.

The audit strips section cross-references, inline code spans (commit hashes, field names, file
names) and the V1 hash prefix before extracting tokens, because none of those is a claim about the
world. That stripping rule is in the committed script and is auditable.

## 2. Status — all verdicts unchanged

| family | V1 | V2 | changed? |
|---|---|---|---|
| H18.3 | `PRE-REGISTERED NULL` | `PRE-REGISTERED NULL` | **no** — interpretation bounded only |
| H19.0 | `PARTIAL PASS` | `PARTIAL PASS` | **no** — description of the 32 changed |
| H19.2 | `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL` | same | **no** |
| H14 parent | `OPEN` | `OPEN` | **no** |
| H13 | implementation rejected, economics unresolved | `IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED` | label only; the V1 text already said this |

The status audit also searches every mention of H19.2 and H19-P3A within 170 characters for "null"
or "rejected": **no violation**.

## 3. V1 integrity

**All five frozen hashes still match.** The audit checks this first and aborts with exit status 2
without running anything else if one has moved.

| file | SHA-256 | state |
|---|---|---|
| `paper.md` | `1853bce01e638da159733ab61fd3d4945ba51a160d3ddc156ab26fa57da95cef` | unchanged |
| `paper.tex` | `2abad0f88b468ea542ef32d838539c7c29b8d5683a907f96cb56b2328d0d97e7` | unchanged |
| `CLAIM_EVIDENCE_MATRIX.csv` | `a1b97453ada9f3397f317f6b3e15d720ff5791c60896e37fea0539d8e98cb781` | unchanged |
| `PAPER_QA.md` | `357c25b9490e109d08af8092f1b0079ab91529b1b21cf26e60d206eaef8fe9be` | unchanged |
| `REPRODUCIBILITY_APPENDIX.md` | `6ea8edaa0a94f9c989f206229ac386b47c548cbd61938a08ef70e291c72adcff` | unchanged |

V2 writes only inside `papers/falsification_first_alpha_discovery/v2/`.

## 4. Novelty — every claim mapped against prior work

| V2 novelty claim | prior work it is positioned against | what remains ours |
|---|---|---|
| Venue-side archive asymmetry (§5.1) | Shumway 1997; Shumway & Warther 1999 (vendor-side bias and a correction); Ammann et al. 2022 (crypto attrition, attributed to aggregators) | the measurement from the **venue** side: a 0.0 pp retrieval differential making a risk set *constructible* without paid data. Bounded to one venue measured against two that failed the same probe. |
| Validated universe with a measured recall denominator (§5.3) | event-study practice generally | recall measured against a denominator built from **market data** (assets whose candles stopped being served), not from the document source being validated |
| Pre-freeze full-pool common-support ceiling (§8.2) | Petersen et al. 2012 (positivity diagnostics, structural vs practical violations) | the **pre-freeze, full-pool, outcome-blind** application. Positivity theory is explicitly **not** claimed. |
| Structural outcome blinding (§8.3) | blinding generally | blinding that is **auditable from data-access code** (`usecols`), not declared in prose. Blinding itself is explicitly not claimed. |
| Classification-level leakage (§10) | Kapoor & Narayanan 2023, category "features which are not legitimate" | **narrowed in V2** to a detection procedure plus a measured rate (676 of 2,352, 28.7%). The manuscript states in bold that this is **not** a new leakage category. |
| Cost-of-enforcement framing (§1.2) | Bailey & López de Prado 2014; Hou, Xue & Zhang 2020; Menkveld et al. 2024 | what enforcement destroyed, including studies made impossible before they began — which the cited literature, auditing work that already exists, does not report |

No novelty claim in V2 stands without an explicit statement of what the prior literature already
owns.

## 5. Case selection

**Disclosed, in the required words**, in §4.1:

> The four detailed case studies were selected retrospectively for methodological informativeness.
> Hypothesis selection within families and case selection for this manuscript are different
> processes.

§4.2 reports all 31 registry entries; §4.3 the terminal-state distribution; §4.4 states the three
facts that cut against the thesis, including that nine entries were rejected on a completed economic
test and that the single promoted family was later archived for falling below a revised return
hurdle. Figure 1 plots the denominator.

## 6. Governance timeline

§2A lists 7 rules in force at the start, each with its evidence. §2B lists 14 rules added later, each
with the family, the triggering failure, the commit and its date. The headline is explicit: *the
program became progressively more falsification-first as failures accumulated*, and the manuscript
states that any reading in which the full protocol governed the whole program is wrong.

Commit dates are read from the git history (`C-GOV-03`), not asserted.

## 7. Thresholds

§9 classifies **19** thresholds as `THEORETICAL`, `CONVENTIONAL` or `ENGINEERING JUDGEMENT`, with the
conclusion each drives. None is `THEORETICAL`; two are `CONVENTIONAL`; the rest are engineering
judgement, and one (90-day risk-set entry) is marked as having a post-hoc origin.

Three headline conclusions are identified as threshold-determined. The required caveat is present:
*pre-specification protects against outcome-driven threshold movement; it does not make an arbitrary
threshold theoretically correct.* §9.1 adds the four-level hierarchy of bars and states that level-3
discipline is weaker than levels 1 and 2.

**Threshold sensitivity remains unmeasured**, stated in §9 and §12, and deferred as F1.

## 8. H18.3 — bounded interpretation

Present in the abstract, §6.3 and §13. The set-off note states: the pre-registered support criteria
were not met; development was positive in 8 of 8 folds; the interval [−0.0074, +0.0628] is consistent
with a positive effect roughly twice the point estimate; the holdout reverses sign; the base rate
moves from 5.822% to 11.792%; the honest description is a small, unstable, possibly regime-sensitive
effect; **absence of effect is not demonstrated at this sample size**.

The verdict label is unchanged, and the manuscript states that the defective calibration bar did not
determine it.

## 9. H19.0 — screen, not feasibility

"feasible for small capital" appears **zero** times. The replacement wording is "passes a coarse
volume-based liquidity screen", used in the text, in Figure 4's title and in its caption. §7 lists
the eight missing ingredients — order book, spread, market impact, taker and maker fees, funding
cost, latency, intraday volume distribution, fill probability — and states that the result is
instrument availability plus coarse screening, **not** execution feasibility and **not**
profitability.

The count of 32 is unchanged.

## 10. H19.2 — bounded exact-matching claim

The general claim is gone. §8.2's note states the bounded version — exact matching on a rare binary
warning state can leave an insufficient comparison set, and the ceiling can be measured on the full
eligible population before a design is frozen — and explicitly says the manuscript does **not** claim
that covariate adjustment cannot establish common support in general.

Five alternatives are named and marked **not executed**: propensity weighting with overlap
diagnostics, overlap weights, trimming, coarsened matching, estimand redefinition. The manuscript
observes that with 52 of 62 event assets warned and a full-pool median of 7, the violation sits
closer to the structural than the practical end of the distinction in Petersen et al. 2012.

The no-price guarantee has its own subsection (§8.3) with the `usecols` evidence and the consequence
that a future redesign would be a new design rather than an outcome-driven rescue.

## 11. Future work — nothing from Bucket 3 was executed

| deferred item | state |
|---|---|
| F1 threshold sensitivity | **not run** |
| F2 two-way cluster / block bootstrap | **not run** |
| F3 weighted or trimmed H19-P3A redesign | **not run**; no price loaded |
| F4 independent reconstruction of the 201-event universe | **not run**; named in §12 with an acceptance criterion |
| F5 order-book execution analysis | **not run** |
| F6 second-venue replication | **not run** |

No script that loads market data was executed during either revision pass. The only computation
performed was counting registry rows, copying committed figures, re-rendering figures from committed
JSON, converting Markdown to LaTeX, and hashing.

## 12. Contents

| | V1 | V2 |
|---|---|---|
| body word count | 9,394 | **10,786** |
| total word count | 9,753 | 11,643 |
| figures | 6 | **6** (1 dropped, 1 new, 1 moved to an appendix) |
| tables | 5 | 5, plus two authored tables in §4.2 and §9 |
| references | 14 | **22** |
| claim rows | 126 | **150** |
| sections | 12 | 13 |

## 13. Known limitations of this QA process

- The claim audit matches numeric tokens. It verifies that each number has an artefact behind it, not
  that each number is used in the right sentence; the latter was checked by reading.
- The must-fix audit matches required statements by regular expression. A statement could be present
  and still be poorly placed; placement was checked by reading.
- The language audit uses a fixed vocabulary. It cannot detect overclaim expressed without those
  words.
- `ARTEFACT_CITED` rows (now 16 of 150 carried plus the external-literature rows) were taken from
  committed documents or published work and not re-derived in this session. They are marked.
- The V2 manuscript has **never been compiled**: no LaTeX distribution and no `pandoc` exist in this
  environment. `paper_v2.tex` is generated from `paper_v2.md` by a committed converter and is
  syntactically unverified.
- **No public repository or DOI exists.** For a paper whose contribution includes an artefact trail,
  this remains a blocking item before any external release.
