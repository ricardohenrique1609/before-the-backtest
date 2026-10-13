# V2 MUST-FIX AUDIT

Run after the first V2 pass, which applied only the items marked **MUST FIX BEFORE EXTERNAL
RELEASE** in `PAPER_REVISION_PLAN_V2.md`. SHOULD FIX and OPTIONAL items were not yet applied when
this audit ran.

**Audit command:** `.venv/Scripts/python -I scripts/paper_audit_v2.py`

```
[v1 freeze]   files 5 | changed 0
[claim]       distinct numeric tokens 186 | unsupported 0
[status]      labels 5 | failures 0
[must-fix]    checks 24 | failures 0
[language]    prove=6, proves=3, proven=3, never=14, insider=2, profitab=2, alpha=1, demonstrat=5
[literature]  entries 22 | without an access statement 0
RESULT: PASS (0 issues)
```

---

## 1. Are all MUST FIX items complete?

| plan item | revision | state | where in V2 |
|---|---|---|---|
| **R25** | full experiment denominator, H1 → H19.2 | **done** | §4.2, 31 entries with stage, terminal state, failure class, whether an economic outcome was computed, whether pre-registered, whether a holdout was used, and a commit or artefact reference |
| **R26** | terminal-state counts, plus the retrospective-selection statement | **done** | §4.3 (distribution over 31 entries) and §4.1 (the required sentence, verbatim) |
| **R1** | governance split into ex ante and ex post | **done** | §2A (7 rules in force at the start) and §2B (14 rules with family, triggering failure, commit and date); headline restated as a trajectory |
| **R2** | literature positioning rebuilt | **done** | §1.1 now opens on the prior literature; `references_v2.bib` adds Bailey & López de Prado, Hou/Xue/Zhang, Menkveld et al., Shumway, Shumway & Warther, Kapoor & Narayanan, Petersen et al. and a registered-reports entry |
| **R3** | contribution restated | **done** | §1.3 states four procedures and their measurements; C1–C4 no longer appear as contributions |
| **R15** | abstract rewritten | **done** | abstract leads with what is already known, then the gap, then the four procedures, then the two bounded results |
| **R5** | H18.3 null interpretation | **done** | §6.3 set-off note: failed criteria, interval consistent with a positive effect, sign reversal, base-rate shift, absence not demonstrated; abstract and §13 carry it |
| **R7** | H19.0 execution wording | **done** | "coarse volume-based liquidity screen" throughout; the eight missing execution ingredients listed; "feasible for small capital" appears **zero** times |
| **R8** | H19.2 common-support claim bounded | **done** | §8.2 set-off note narrows the claim and lists five unexecuted alternatives; §8.3 promotes the no-price guarantee to its own subsection |
| **R27** | threshold classification table | **done** | §9, 19 thresholds classified `THEORETICAL` / `CONVENTIONAL` / `ENGINEERING JUDGEMENT`, with the conclusion each drives; the pre-specification caveat and the unmeasured-sensitivity statement are both present |

**All ten MUST FIX items are complete.** The audit's `[must-fix]` block tests 24 required statements
mechanically and all 24 are present.

## 2. Unsupported numerical claims

**Zero**, over 186 distinct numeric tokens in the V2 body.

Three were added to the matrix during this audit rather than removed from the text: the 95–99% field
accuracy range, Ammann et al.'s 39.5% attrition rate (tagged `EXTERNAL_LITERATURE`), and the
sub-family identifiers the registry uses. One wording change was made because the token was a range
rather than a claim: `0.95–0.99` became `95% to 99%`.

`CLAIM_EVIDENCE_MATRIX_V2.csv` now has **150 rows** — 126 carried from V1 and 24 new — with an
`evidence_category` column: 135 `INTERNAL_EMPIRICAL`, 12 `EXTERNAL_LITERATURE`, 3 `OFFICIAL_VENUE`.
The categories are never blended in a single claim.

## 3. Did any V1 hash change?

**No.** All five frozen files are byte-identical to `PAPER_V1_FREEZE.md`:

| file | SHA-256 | state |
|---|---|---|
| `paper.md` | `1853bce0…` | unchanged |
| `paper.tex` | `2abad0f8…` | unchanged |
| `CLAIM_EVIDENCE_MATRIX.csv` | `a1b97453…` | unchanged |
| `PAPER_QA.md` | `357c25b9…` | unchanged |
| `REPRODUCIBILITY_APPENDIX.md` | `6ea8edaa…` | unchanged |

V2 lives in `papers/falsification_first_alpha_discovery/v2/` and writes nothing outside it. The audit
checks V1 integrity **first** and exits with status 2 without running anything else if a hash has
moved.

## 4. Did any verdict change?

**No.** The five non-negotiable states are present verbatim and unchanged:

| family | state in V2 | changed from V1? |
|---|---|---|
| H18.3 | `PRE-REGISTERED NULL` | no — only the **interpretation** is bounded |
| H19.0 | `PARTIAL PASS` | no — only the **description** of the 32 changed |
| H19.2 | `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL` | no |
| H14 parent | `OPEN` | no |
| H13 | implementation rejected; economic question unresolved | relabelled to `IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED`, which is the V1 taxonomy's own wording made into the label |

The status audit additionally searches every mention of H19.2 and H19-P3A for the words "null" or
"rejected" within 170 characters and found no violation.

## 5. Was any new experiment run?

**No.** No script that loads market data was executed. The three programs run during this pass —
`paper_build_tables.py`, `paper_build_figures.py` and `paper_audit_v2.py` — read committed gate
JSONs, results JSONs and manuscripts. The only new computation of any kind is counting registry rows
and SHA-256 hashing.

## 6. Was any new economic quantity computed?

**No.** No return, P&L, Sharpe, edge, abnormal return, PR-AUC, interval or any other economic or
statistical estimate was produced. Every quantitative statement in V2 is either carried from a
committed artefact or is a count of registry entries. No price column was loaded for H19.2 or for
anything else.

Bucket 3 of the revision plan — threshold sensitivity, two-way clustering, a weighted H19-P3A
redesign, independent replication, order-book analysis, second-venue replication — remains
**DEFERRED and unexecuted**.

## 7. Which referee rejection conditions are now addressed?

The referee named five conditions for outright rejection.

| # | condition | state after MUST FIX |
|---|---|---|
| 1 | author declines to report the full experiment denominator | **addressed.** §4.2 reports all 31 entries; §4.3 the distribution; §4.1 states that case selection was retrospective |
| 2 | governance presented as ex ante | **addressed.** §2A/§2B split with commits and dates; the headline is the trajectory |
| 3 | novelty positioning not rebuilt | **addressed.** §1.1 opens on the prior literature and §1.3 restates the contribution as four procedures; whether the referee finds the remaining novelty sufficient is for the second report |
| 4 | `NULL` carrying the weight of "no effect" | **addressed.** §6.3, the abstract and §13 all state that it means failed pre-registered criteria and that absence is not demonstrated |
| 5 | "feasible for small capital" and the general common-support claim surviving | **addressed.** The first phrase appears zero times; the second is replaced by a bounded claim with five unexecuted alternatives named |

**Remaining, and not addressed by this pass:** everything in SHOULD FIX and OPTIONAL — the
dependence limitation (R6), the narrowed model claim (R9), framework falsifiability (R10), the
single-researcher expansion (R11), general-versus-conditional principles (R12), the structural
restructure (R13), the bar hierarchy (R24), the compressed defect table (R28), both-outcomes
reporting (R29), and gate-detection staging (R30).

> **Note on scope.** Several SHOULD FIX items were in fact written into the first V2 draft because
> the manuscript was rebuilt rather than patched — §11.1 (R10), §12's independent-check paragraph
> (R11), §11's `GENERAL`/`CONDITIONAL` marks (R12), §10's narrowed leakage claim (R4), §12's
> dependence paragraph (R6) and Appendix B (R28) are already present. They are nonetheless re-checked
> in the second pass rather than assumed complete, and `PAPER_QA_V2.md` records their final state.

## 8. Verdict

**PASS.** V1 is intact, no verdict moved, no experiment ran, no economic quantity was computed, and
all ten MUST FIX items are in place with zero unsupported numerical claims. The second pass may
proceed.
