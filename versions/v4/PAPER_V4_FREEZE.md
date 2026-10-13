# PAPER V4 — FREEZE RECORD

> **V4 is frozen as reviewed.** V1, V2 and V3 remain frozen and byte-identical. The two proof-stage
> items in `REFEREE_REPORT_V4.md` are **not applied here**: the referee reviewed this text, and
> amending a reviewed version in place is the practice this research programme exists to avoid. They
> open the production phase, recorded in `../SCIENTIFIC_FREEZE.md`.

**Referee #4: ACCEPT.** The scientific content is frozen; see `../SCIENTIFIC_FREEZE.md`.
**V4 is not external-release ready** — three production blockers remain (§7).

---

## 1. Identity

| | |
|---|---|
| title | Before the Backtest: Pre-Freeze Common-Support Ceilings for Event-Driven Strategy Research |
| version | **V4** (acceptance revision) |
| frozen | 2026-10-12 |
| revision basis | `../v3/REFEREE_REPORT_V3.md` — MINOR REVISION, six editorial items |
| directory | `papers/falsification_first_alpha_discovery/v4/` |

## 2. Prior freeze hashes — all re-verified, all unchanged

Sixteen files, checked by `scripts/paper_audit_v4.py`, which verifies them first and aborts with exit
status 2 without running anything else if one has moved.

| version | files | changed |
|---|---|---|
| V1 (`52a980a`) | `paper.md`, `paper.tex`, `CLAIM_EVIDENCE_MATRIX.csv`, `PAPER_QA.md`, `REPRODUCIBILITY_APPENDIX.md` | **0** |
| V2 | `paper_v2.md`, `paper_v2.tex`, `CLAIM_EVIDENCE_MATRIX_V2.csv`, `references_v2.bib`, `PAPER_QA_V2.md` | **0** |
| V3 (`c219704`) | `paper_v3.md`, `paper_v3.tex`, `CLAIM_EVIDENCE_MATRIX_V3.csv`, `references_v3.bib`, `PAPER_QA_V3.md`, `REFEREE_REPORT_V3.md` | **0** |

Canonical manuscript hashes: V1 `1853bce0…`, V2 `b2c3ddae…`, V3 `5f5468eb…`.

## 3. V4 hashes

| file | SHA-256 | bytes |
|---|---|---|
| `paper_v4.md` | `def1442cb27b048e16b5b79d3ab64f1b26f99bab9ff3a8d79bda46370009e38e` | 60,644 |
| `paper_v4.tex` | `0660c11b65d62c3a4f3537e9461387d7417a8248c093151c84fcc772c199d2fb` | 65,838 |
| `CLAIM_EVIDENCE_MATRIX_V4.csv` | `8e05e3a7cbcba7328afc78887533586853c0b96ed4f6c906a1ce45c272b7f281` | 46,594 |
| `references_v4.bib` | `dd98e55260855990a6e105a0ed125e3ed5a169bb02ca3cdccac345d73815c11f` | 18,931 |
| `PAPER_QA_V4.md` | `fcc90182cae9da77b5453ea8b30d7944d50ff9067ab329a2e2ca22245c6bb8a1` | 10,601 |
| `REFEREE_REPORT_V4.md` | `1a0efa7ece57b36d601f32825c0f75a784ade9c353545588ec9d6e56f168a2c7` | 9,757 |

`references_v4.bib` is byte-identical to `references_v3.bib`: no citation changed, because no claim
changed.

## 4. Exact V3 → V4 edits

Six edits, all editorial, each traceable to a numbered referee request. **No result, verdict, claim
or number changed.**

| # | referee item | edit | location |
|---|---|---|---|
| 1 | R1 | `N*` ≤ 15 for any *m* ≥ 3 therefore infeasible for any *N_min* > 15, plus a scope note stating that it is arithmetic on committed quantities, **not** a sensitivity analysis, and enumerating the eight things it does not establish | §4.4 |
| 2 | R2 | set-off note: the procedure is demonstrated once, on one specification that returned infeasible; evidence concerns detection, not specificity; no feasible-case control is reported; the registry cannot supply one | §4.4 |
| 3 | R2 | echo in Limitations — "One demonstration; specificity unmeasured" | §8 |
| 4 | R3 | explicit ranking: after the floor-invariance bound, the **matching rule** is the largest unmeasured design sensitivity, with its four components; set-off note preserving specification-versus-question | §8 |
| 5 | R4 | Figure 4 re-rendered: hatched unfilled band, legend and title both stating "NOT a confidence interval"; caption carries all six required facts; figure-data provenance restated. **Same committed values as V3; presentation only** | Figure 4 |
| 6 | R5 | Appendix A.2 (derivative-notice coverage) **removed**; Appendix A retitled "The liquidity screen, reported as a distribution" | Appendix A |
| 7 | R6 (optional) | base-rate discussion compressed to one sentence in the body; full detail relocated to a new **Appendix F**, which also states that no post-hoc decomposition was attempted | §6.3, Appendix F |
| 8 | housekeeping | version header; figure and table paths `v3_` → `v4_`; appendices reordered so E precedes F | throughout |

### Unchanged

The contribution statement, the novelty positioning, the Rubin concession, all twelve frozen
quantities of the demonstration, every verdict label and its interpretation, the scope paragraph, the
31-entry registry with its nine economic rejections and archived promotion, and the four body
principles.

## 5. Contents

| | V1 | V2 | V3 | V4 |
|---|---|---|---|---|
| body words | 9,394 | 10,786 | 7,026 | **7,394** (target 6,800–7,400) |
| total words | 9,753 | 11,643 | 8,860 | 9,431 |
| figures | 6 | 6 | 4 | **4** |
| body tables | 5 | 5 + 2 | 3 | **3** |
| appendix tables | — | — | 6 | **6** |
| references | 14 | 22 | 25 | **25** |
| claim rows | 126 | 150 | 161 | **165** |

The four new claim rows are the *N_min* bound (status `ARITHMETIC DERIVATION FROM COMMITTED VALUES`),
the specificity disclosure, the matching-rule ranking and Figure 4's composition.

## 6. QA

```
[freezes]     V1+V2+V3 files 16 | changed 0
[claim]       distinct numeric tokens 85 | unsupported 0
[required]    checks 26 | failures 0
[verdicts]    labels 4 | failures 0
[novelty]     novel=1, novelty=1, first=4, unique=1, contribution=8
[length]      body 7,394 words | target 6,800-7,400 | in range
RESULT: PASS (0 issues)
```

Every novelty-word occurrence was reviewed individually (`PAPER_QA_V4.md` §4): no priority claim; all
four uses of "first" are ordinal or gold-set terminology; "unique" appears once, in "attributed
uniquely to a changing effect".

**Zero experiments.** No threshold sensitivity, no alternative matching, no weighting, no trimming,
no H19.2 price, no bootstrap, no return, no model, no event reconstruction, no order-book work, no
independent replication. No gate, verdict, pre-registration or historical artefact was altered.

## 7. Referee recommendation and status

**`REFEREE_REPORT_V4.md`: ACCEPT**, subject to two proof-stage items and the production requirements.

All six V3 requests were answered, none partially. The referee verified the *N_min* arithmetic
independently and found it correct, raising one precision clause about the quantile convention — "a
proof correction, not a revision". He records that the sentence refusing the registry as a negative
control closes the escape route he was watching for.

| status | state |
|---|---|
| **scientific content** | **ACCEPTED and FROZEN** — see `../SCIENTIFIC_FREEZE.md` |
| proof-stage items | 2, open: name the quantile convention; reposition Figure 4's legend |
| production blockers | 3, open: never compiled; no public repository or DOI; Figure 4 legend overlap |
| future-work science | 6, named and not performed: matching-rule frontier, threshold sensitivity, independent reconstruction, weighted redesign, specificity evidence, second-venue replication |
| release | **not authorised.** Nothing submitted, uploaded, posted or assigned a DOI |

## 8. Reproduction

```bash
.venv/Scripts/python -I scripts/paper_build_v4.py   # Figure 4 (same values, revised presentation) + paper_v4.tex
.venv/Scripts/python -I scripts/paper_audit_v4.py   # V1+V2+V3 integrity, then the V4 audits
```

Figures 1–3 and all nine tables are carried unchanged from V3. Both scripts read only committed
artefacts.
