# PAPER V2 — FREEZE RECORD

> **V2 is frozen after the second hostile referee report.** V1 remains frozen and byte-identical.
> Any V3 change must be traceable against both hash sets below and may not silently overwrite a V1
> or V2 claim or interpretation.

**V2 is not external-release ready**, and this record says so explicitly. See §7.

---

## 1. Identity

| | |
|---|---|
| version | **V2** |
| frozen | 2026-10-11 |
| revision basis | `REFEREE_REPORT_V1.md` (MAJOR REVISION), `AUTHOR_RESPONSE_V1.md`, `PAPER_REVISION_PLAN_V2.md` |
| directory | `papers/falsification_first_alpha_discovery/v2/` |
| V1 freeze commit | `52a980a` |

## 2. V1 hashes — re-verified, all unchanged

| file | SHA-256 | state at V2 freeze |
|---|---|---|
| `paper.md` | `1853bce01e638da159733ab61fd3d4945ba51a160d3ddc156ab26fa57da95cef` | **unchanged** |
| `paper.tex` | `2abad0f88b468ea542ef32d838539c7c29b8d5683a907f96cb56b2328d0d97e7` | **unchanged** |
| `CLAIM_EVIDENCE_MATRIX.csv` | `a1b97453ada9f3397f317f6b3e15d720ff5791c60896e37fea0539d8e98cb781` | **unchanged** |
| `PAPER_QA.md` | `357c25b9490e109d08af8092f1b0079ab91529b1b21cf26e60d206eaef8fe9be` | **unchanged** |
| `REPRODUCIBILITY_APPENDIX.md` | `6ea8edaa0a94f9c989f206229ac386b47c548cbd61938a08ef70e291c72adcff` | **unchanged** |

Verified by `scripts/paper_audit_v2.py`, which checks V1 integrity first and aborts without running
anything else if a hash has moved.

## 3. V2 hashes

| file | SHA-256 | bytes |
|---|---|---|
| `paper_v2.md` | `b2c3ddaed36fd7371a16cf9f5b75c39272dbd38edc10a482d114c9a187bfd157` | 74,976 |
| `paper_v2.tex` | `ad18523888093b1cc54956babea531581edcac1000243fc6b42ec2eb0b7a9cbd` | 81,881 |
| `CLAIM_EVIDENCE_MATRIX_V2.csv` | `47d22e1e1abd7669f4cd68c852ac41751461caba2ad395df3a7463a275afbd7f` | 40,569 |
| `references_v2.bib` | `543d467791d55fe734334fd107f91ab143bb00d02b1ac1a3b36b47418e9b298c` | 15,695 |
| `PAPER_QA_V2.md` | `7bf5cae957da8f2108dd59057d23e81a8d88a5e7de5f8e321885c89da5958273` | 10,986 |
| `V2_MUST_FIX_AUDIT.md` | `424ec1d5d9fa0fd071bbe44afc38bcaa6efb3c8b249d68f64018a6e4ba46382c` | 8,294 |

## 4. Exact changes from V1

### Claims narrowed (V2 claims less)

| # | V1 | V2 | referee |
|---|---|---|---|
| 1 | four contribution classes presented as contributions | organising structure only; four **procedures** are the contribution, each with the prior literature that owns the surrounding claim | MC10, R3 |
| 2 | "covariate adjustment cannot manufacture common support" | exact matching on a rare binary warning state can leave an insufficient comparison set, and the ceiling can be measured before a design is frozen; five alternatives named as unexecuted | MC9, R8 |
| 3 | "feasible for small capital" | "passes a coarse volume-based liquidity screen"; appears **zero** times in V2; eight missing execution ingredients listed | MC8, R7 |
| 4 | "the decisive question was almost never which model was fitted" | bounded to the four retrospectively selected cases, with the registry showing nine economic rejections that contradict the general form | MC14, R9 |
| 5 | classification-level leakage implied as a new category | a detection procedure applied to a known leakage class, plus a measured rate (676 of 2,352, 28.7%) | MC10, R4 |
| 6 | `NULL` used without interpretive bounds | `PRE-REGISTERED NULL` defined as "failed the pre-registered support criteria", with the interval consistent with a modest positive effect and absence not demonstrated | MC6, R5 |
| 7 | ten principles at equal confidence | each marked `GENERAL` or `CONDITIONAL` with the condition stated | MC5, R12 |
| 8 | subtitle "Manufacture Trading Strategies" | "Create and Destroy Apparent Trading Opportunities" | minor 1, R14 |

### Material added

| # | addition | referee |
|---|---|---|
| 9 | §4.2 full registry denominator, 31 entries, H1 to H19.2 | MC2, MC13, R25 |
| 10 | §4.3 terminal-state distribution; Figure 1 | R26 |
| 11 | §4.1 retrospective case-selection disclosure, in the required words | MC2 |
| 12 | §4.4 the three facts that cut against the thesis, including nine economic rejections and the archival of the one promoted family | MC13, Part F |
| 13 | §2A / §2B governance split: 7 rules at the start, 14 added later with family, failure, commit and date | MC4, R1 |
| 14 | §1.1 prior-literature opening; 8 new references with access levels | MC10, R2 |
| 15 | §9 threshold classification, 19 thresholds, plus the pre-specification caveat and the unmeasured-sensitivity statement | MC3, R27 |
| 16 | §9.1 four-level hierarchy of bars | R24 |
| 17 | §6.1 both-outcomes reporting paragraph with commit order | R29 |
| 18 | §11.1 "What would falsify this framework", with six protocol observables, three of them `UNMEASURED` | MC11, R10 |
| 19 | §11.1 defect-detection staging table | R30 |
| 20 | §12 single-researcher subsection and the named cheapest independent check | MC15, R11 |
| 21 | §12 dependence paragraph: batch announcements, policy waves, cross-sectional shocks; interval likely too narrow | MC7, R6 |
| 22 | §1.4 formal definitions of point-in-time and common support | minor 11, R16 |
| 23 | §8.3 structural outcome blinding as its own subsection | MC9 |
| 24 | Appendix B: implementation defects, explicitly not claimed as contributions | MC1, R28 |

### Verdicts — unchanged

| family | state | changed? |
|---|---|---|
| H18.3 | `PRE-REGISTERED NULL` | **no** |
| H19.0 | `PARTIAL PASS` | **no** |
| H19.2 | `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL` | **no** |
| H14 parent | `OPEN` | **no** |
| H13 | `IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED` | label only; V1 text already said this |

**No number produced by an experiment changed.** Every quantitative difference between V1 and V2 is
either a new count of registry rows, a newly cited published figure, or a value carried from a
committed artefact that V1 did not quote.

## 5. Contents at freeze

| | V1 | V2 |
|---|---|---|
| body word count | 9,394 | **10,786** |
| total word count | 9,753 | 11,643 |
| sections | 12 | 13 |
| figures | 6 | **6** (V1 F1 dropped; registry denominator added; ceiling panel moved to an appendix figure) |
| tables | 5 generated | 5 generated + 2 authored (§4.2, §9) |
| references | 14 | **22** |
| claim–evidence rows | 126 | **150** (126 carried, 24 new) |
| evidence categories | implicit | explicit: 134 `INTERNAL_EMPIRICAL`, 13 `EXTERNAL_LITERATURE`, 3 `OFFICIAL_VENUE` |

## 6. QA status

```
[v1 freeze]   files 5 | changed 0
[claim]       distinct numeric tokens 192 | unsupported 0
[status]      labels 5 | failures 0
[must-fix]    checks 24 | failures 0
[language]    prove=6, proves=3, proven=3, never=15, insider=2, profitab=2, alpha=1, demonstrat=5
[literature]  entries 22 | without an access statement 0
RESULT: PASS (0 issues)
```

**No Bucket-3 work was executed.** No experiment, no backtest, no sensitivity analysis, no bootstrap,
no redesign, no price load for H19.2, no order-book study, no independent reconstruction. No gate,
verdict, pre-registration or historical artefact was altered.

## 7. Referee V2 recommendation and unresolved concerns

**`REFEREE_REPORT_V2.md`: MAJOR REVISION.**

All five of the referee's V1 rejection conditions are resolved. The remaining objections:

| # | concern | fixable without a new experiment? |
|---|---|---|
| 1 | **No single clear contribution.** Four procedures at equal weight; the referee's view is that one (the pre-freeze common-support ceiling) is the contribution and the other three are evidence for it. | **yes** — restructure and retitle |
| 2 | **The thesis is wider than the registry supports.** The denominator shows the economic test was decisive more often than the data layer; the claim should be narrowed to the domain of institutional event data from public documents and venue archives. | **yes** |
| 3 | **The 1%-rule endpoint is arbitrary**; report the whole liquidity distribution instead, which the manuscript already contains. | **yes** |
| 4 | **The landmark estimand under a changing base rate** is unaddressed. | **yes** — one paragraph |
| 5 | **§2A's evidence standard is weaker than §2B's**, and §2A is the half that supports the author. | **yes** |
| 6 | **§11.1 undercuts the paper mid-document**; it belongs in the limitations. | **yes** |
| 7 | **Three conclusions remain threshold-determined with unmeasured sensitivity.** | no — requires new computation (F1) |
| 8 | **One-way clustering disclosed, not remedied.** | no — requires new computation (F2) |
| 9 | **No independent verification of any result.** | no — requires a second party (F4) |
| 10 | **No public repository, no DOI, never compiled.** | yes, but requires external action |

### Release status

> **V2 is NOT external-release ready.** The author's own rule is that no external release occurs
> while a referee recommends Reject or Major Revision for a reason fixable without a new experiment.
> Concern 1 is exactly such a reason, and concerns 2 through 6 are as well. A V3 addressing
> concerns 1–6 — none of which requires running anything — would satisfy that rule; the referee
> states he would move to Minor Revision on seeing it.

Nothing has been submitted, uploaded, posted or assigned a DOI.

## 8. Reproduction

```bash
.venv/Scripts/python -I scripts/paper_build_tables.py    # V1 tables (unchanged)
.venv/Scripts/python -I scripts/paper_build_figures.py   # V1 figures (unchanged)
.venv/Scripts/python -I scripts/paper_build_v2.py        # V2 figures, tables, paper_v2.tex
.venv/Scripts/python -I scripts/paper_audit_v2.py        # V1 integrity + four V2 audits
```

All four read only committed artefacts. `paper_v2.tex` is generated from `paper_v2.md`, so the two
cannot diverge; neither has ever been compiled, because no LaTeX distribution exists in this
environment.
