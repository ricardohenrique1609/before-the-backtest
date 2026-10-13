# PAPER QA — V4

Quality report for *Before the Backtest: Pre-Freeze Common-Support Ceilings for Event-Driven
Strategy Research*, **V4** (acceptance revision), 2026-10-12.

**Audit command:** `.venv/Scripts/python -I scripts/paper_audit_v4.py`

```
[freezes]     V1+V2+V3 files 16 | changed 0
[claim]       distinct numeric tokens 85 | unsupported 0
[required]    checks 26 | failures 0
[verdicts]    labels 4 | failures 0
[novelty]     novel=1, novelty=1, first=4, unique=1, contribution=8
[length]      body 7,394 words | target 6,800-7,400 | in range
RESULT: PASS (0 issues)
```

---

## 1. Frozen integrity

**All sixteen frozen files are byte-identical.** The audit checks them first and exits with status 2
without running anything else if one has moved.

| version | files checked | changed |
|---|---|---|
| V1 (`52a980a`) | 5 | **0** |
| V2 | 5 | **0** |
| V3 (`c219704`) | 6 | **0** |

V4 writes only inside `papers/falsification_first_alpha_discovery/v4/`.

## 2. The five mandatory referee-V3 changes

Each is checked verbatim by the audit, which tests 26 required statements and finds all present.

### R1 — floor invariance extended to *N_min* ✔

§4.4 now states: *"Because `N* ≤ 15` for every support floor m ≥ 3, the infeasibility verdict also
holds for any admissible confirmatory minimum **N_min > 15**, not only for the pre-registered 40."*

A set-off note states what the bound does and does not establish: it is arithmetic on committed
quantities, **it is not a sensitivity analysis**, nothing was recomputed, and it establishes nothing
about *N_min* ≤ 15, the matching rule, the liquidity-band definition, matching exactness, the
covariate set, weighting, trimming or estimand redefinition.

Matrix row `C-V4-01` carries status **`ARITHMETIC DERIVATION FROM COMMITTED VALUES`** — a distinct
status from `VERIFIED` and `ARTEFACT_CITED`, so a reader can see at a glance that no computation
produced it.

### R2 — detection, not specificity ✔

Two placements, as required.

**Immediately after the central demonstration (§4.4):** a set-off note stating that the procedure is
demonstrated once, on one specification, which returned infeasible; that this is evidence the gate
can detect one infeasible design; and that it does **not** estimate specificity, false-positive rate,
or the rate at which the gate would allow a sound study to proceed. It states explicitly that there
is no case in which the audit returned feasible, the study proceeded, and the design was later shown
to be well identified.

**In Limitations (§8):** "One demonstration; specificity unmeasured."

**H8 is not used as a negative control**, and the note says in terms that reading the registry's
outcomes as negative controls "would be an inference the design does not support" — the registry's
families were not evaluated by this procedure.

### R3 — matching rule named as the largest unmeasured sensitivity ✔

§8 now ranks explicitly: the floor-invariance bound settles *m* (for *m* ≥ 3) and *N_min* (for
*N_min* > 15); **after that bound, the largest remaining unmeasured design sensitivity is the
matching rule itself** — exact warning-state match, liquidity-band definition, matching exactness,
covariate set. A set-off note preserves the distinction: the paper establishes `DESIGN INFEASIBLE
UNDER THIS SPECIFICATION`, **not** that the question cannot be identified.

### R4 — Figure 4 ✔

The figure was re-rendered with the **same committed values**; only the presentation changed. The
band is now **hatched and unfilled**, labelled in the legend as "recorded range 0-27 (NOT a
confidence interval)", and the title repeats it. No statistical-interval vocabulary appears in the
figure or caption.

The caption states all six required facts: 8 of 25 dates have individually persisted values; all 25
contribute to the persisted median; the recorded range is 0–27; the median is 7; only 3 of 25 dates
reach 20; and the 17 remaining dates are not plotted, not interpolated and not implied by the
shading. The figure-data CSV carries the same statement in its provenance line.

**No data were reconstructed.**

### R5 — Appendix A.2 resolved ✔

**Removed**, per the referee's stated preference. The derivative-notice coverage material is not
referenced anywhere in the body — V3's central argument does not depend on announcement ordering —
so removal breaks no sentence. Appendix A is retitled "The liquidity screen, reported as a
distribution" and now contains exactly that.

The audit asserts the absence of the removed heading rather than the presence of a replacement.

### R6 (optional) — base-rate paragraph relocated ✔

The body sentence in Supporting Case C is now the single sentence the referee drafted. The full
discussion — base rates 5.822% and 11.792%, calibration, class balance, the PR-AUC lower bound, and
transportability — moves to **Appendix F**, which also states that the design does not decompose the
three explanations and that no post-hoc decomposition was attempted, because that would be an
analysis chosen with knowledge of the outcome.

Supporting Case C stays supporting.

## 3. Claims

| | |
|---|---|
| distinct numeric tokens in the V4 body | 85 |
| **unsupported** | **0** |
| `CLAIM_EVIDENCE_MATRIX_V4.csv` rows | **165** (126 V1, 24 V2, 11 V3, **4 new**) |
| status `VERIFIED` | 133 |
| status `ARTEFACT_CITED` | 31 |
| status `ARITHMETIC DERIVATION FROM COMMITTED VALUES` | **1** |

The four new rows are the *N_min* bound, the specificity disclosure, the matching-rule ranking and
Figure 4's composition. None is a measurement; three are statements the manuscript now makes, and
one is the arithmetic derivation.

## 4. Novelty language

Every flagged occurrence reviewed:

| word | count | occurrences |
|---|---|---|
| novelty | 1 | the set-off note "**Novelty, bounded.**" — the cautious formulation itself |
| novel | 1 | inside that same note's wording |
| first | 4 | all ordinal or descriptive: "First, eligibility is time-varying"; "On the first, the domain changed"; "first-pass fields" and "the first pass persisted" (gold-set terminology). **No priority claim.** |
| unique | 1 | "cannot be attributed uniquely to a changing effect" — a statement about attribution, not about the contribution |
| contribution | 8 | all referring to this paper's single contribution or to what prior work contributed |

The required formulation is intact: *"We are not aware of prior work that operationalises
common-support feasibility in this exact pre-freeze, full-population, outcome-blind form…"* and the
fallback is preserved: if the combination has been formalised elsewhere, the contribution reduces to
the empirical demonstration.

**"first pre-freeze support audit" and equivalents: zero occurrences.** Banned broad phrasing —
"alpha discovery", "feasible for small capital", "framework proves", "improves returns",
"unprecedented", "pre-model failure is usually", "typically fails upstream" — **zero occurrences**.

## 5. Rubin concession preserved

§1.2 opens on it, §2.6 itemises it, and the audit asserts all three of: "Rubin (2008)" present, "is
Rubin's" present, and the "We do **not** claim" list present. The concession reads unchanged from
V3: design-before-outcome is Rubin's; rejecting a dataset for lack of overlap is Rubin's; positivity
is established; design-stage overlap diagnostics exist; outcome-free design is codified.

No source found during this editorial pass weakens the remaining combination claim further. No
additional literature search was performed for V4, since no new claim was introduced.

## 6. Registry denominator preserved

Unchanged from V3 and checked by the audit: 31 entries, 9 economic rejects, 1 promotion, the
promotion later archived, retrospective case selection disclosed, and the line that makes the
narrowing coherent — *"a claim about a **procedure**, not about a prevalence."*

No broad claim was reintroduced.

## 7. Verdicts — unchanged

| family | label |
|---|---|
| H18.3 | `PRE-REGISTERED NULL`; not evidence of no effect |
| H19.2 | `DESIGN INFEASIBLE UNDER THIS SPECIFICATION`; substantively the V2 `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL` state; not null, not reject, no price read |
| H19.0 | capacity and liquidity screen only; not execution feasibility, not profitability |
| H13 | implementation rejected; economics unresolved |
| H14 | `OPEN` |

The central empirical result is unchanged in every component: 62 candidates, floor 20, support
p10 0 / p25 0 / median 1 / p75 2 / p90 57, 52 of 62 below the floor, ceiling range 0–27, median 7,
3 of 25 dates reaching 20, N\* = 10, *N_min* = 40, no price column loaded, no pre-registration
frozen, hypothesis untested.

## 8. Experiments

**Zero.** The only programs run were `paper_build_v4.py` (re-renders one figure from the same
committed values and regenerates the LaTeX) and `paper_audit_v4.py` (reads manuscripts, hashes
files). No threshold sensitivity, no alternative matching, no weighting, no trimming, no H19.2
price, no bootstrap, no return, no model, no event reconstruction, no order-book work, no independent
replication.

No gate, verdict, pre-registration or historical artefact was altered.

## 9. Length

| | V1 | V2 | V3 | V4 |
|---|---|---|---|---|
| body words | 9,394 | 10,786 | 7,026 | **7,394** |
| total words | 9,753 | 11,643 | 8,860 | 9,431 |
| figures | 6 | 6 | 4 | **4** |
| body tables | 5 | 5 + 2 | 3 | **3** |
| appendix tables | — | — | 6 | **6** |
| references | 14 | 22 | 25 | **25** |
| claim rows | 126 | 150 | 161 | **165** |

Body grew by 368 words against the 6,800–7,400 target and sits at its upper end. The growth is the
two mandated set-off notes (R1's scope note and R2's specificity note) and R3's explicit ranking;
it was offset by removing Appendix A.2 from the body's appendix set and by compressing the base-rate
paragraph to one sentence. **In range, and no section was padded.**

## 10. Known limitations of this QA process

- The claim audit matches numeric tokens, not their placement.
- The required-statement audit matches by regular expression; presence is not the same as good
  placement, which was checked by reading.
- The novelty audit uses a fixed word list and cannot detect a priority claim phrased without those
  words.
- **The manuscript has never been compiled.** `paper_v4.tex` is generated from `paper_v4.md` by a
  committed converter and is syntactically unverified.
- **No public repository, no DOI, no independent verification.** All three remain release blockers
  and none is addressed by V4.
