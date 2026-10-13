# PAPER REVISION PLAN — V2

Derived from `REFEREE_REPORT_V1.md` and `AUTHOR_RESPONSE_V1.md`. V1 is frozen at commit `52a980a`
with hashes in `PAPER_V1_FREEZE.md`; nothing here edits V1.

**Nothing in this plan is executed yet.** Items in bucket 3 are explicitly not to be run while alpha
discovery is paused.

---

## Bucket 1 — V2, NO NEW EXPERIMENT REQUIRED

Editorial, framing, literature and clarification. All of it can be written from the manuscript, the
committed artefacts and published literature.

| # | revision | source | severity | effort | impact | new exp. |
|---|---|---|---|---|---|---|
| **R1** | Split §2 into **2a: rules in force from the start** and **2b: rules added at a named family after a named failure**, with the commit that introduced each. Restate the title claim as a trajectory the program travelled, not a starting condition. | MC4 | **critical** | medium | **high** | no |
| **R2** | Rebuild §1 and §10 against the methodology literature: Bailey & López de Prado (deflated Sharpe, trials); Hou/Xue/Zhang (replication, 64% insignificant); Menkveld et al. (*Nonstandard Errors*, JF 2024); Shumway (1997) and Shumway & Warther (1999) (delisting bias, −55% correction, Nasdaq size effect); Kapoor & Narayanan (leakage taxonomy, *Patterns* 2023); the positivity / overlap-weighting literature. | MC10 | **critical** | high | **high** | no |
| **R3** | Restate the contribution as the four measurements that survive comparison: venue-side archive asymmetry; validated universe reconstruction with a measured recall denominator; the pre-freeze full-pool common-support ceiling; the structural zero-price guarantee. Demote C1–C4 from "contributions" to organising structure, each attributed to the prior literature that established it. | MC10 | **critical** | medium | **high** | no |
| **R4** | Narrow the classification-level leakage claim from a **new category** to a **detection procedure plus a measured rate** (676 of 2,352, 28.7%), citing Kapoor & Narayanan's "features which are not legitimate" category. | MC10 | major | low | medium | no |
| **R5** | Add to the abstract and §6.5: `PRE-REGISTERED NULL` means "failed the pre-registered support criteria"; the interval is consistent with a small positive effect; the development-to-holdout reversal, with the base rate moving 5.822% → 11.792%, is instability rather than demonstrated absence. Adjust §12. **Verdict unchanged.** | MC6 | **critical** | low | **high** | no |
| **R6** | Add a dependence paragraph to §6.4: batch announcements, calendar/policy regime, cross-sectional contemporaneity; state that the reported interval is likely **too narrow**; name two-way clustering and a block bootstrap as the unperformed remedies. | MC7 | major | low | medium | no |
| **R7** | Replace "feasible for small capital" with "passes a coarse volume-based liquidity screen" everywhere, including Figure 5's final bar. Add a sentence listing what an execution analysis would require and this one lacks. Count of 32 unchanged. | MC8 | **critical** | low | **high** | no |
| **R8** | Narrow §8's closing principle to exact matching on a rare binary covariate; add two sentences on weighting and trimming and on why a 134-asset tagged universe is closer to a structural than a practical positivity violation. Promote the zero-price guarantee to its own subsection. | MC9 | **critical** | low | **high** | no |
| **R9** | Narrow "the decisive question was almost never which model was fitted" in §1 and §12 to the families reported, noting that twelve further families are summarised but not analysed. | MC14 | major | low | **high** | no |
| **R10** | Add §9.1 "What would falsify this framework": state that it is a governance protocol, name the four observables (defect-detection stage, post-freeze reversal rate, artefact reproducibility, avoided false promotions), report the two this program can report, declare the others unmeasured. | MC11 | major | medium | medium | no |
| **R11** | Expand §11's single-researcher sentence into a subsection; state what two-pass gold sets do and do not control for; name the cheapest independent check (second-party reconstruction of the 201-event universe compared on asset, announcement date and stated trading end) with its acceptance criterion. | MC15 | major | low | medium | no |
| **R12** | Mark each principle in §9 `GENERAL` or `CONDITIONAL (free data / no order book)`; expand venue concentration in §11 from a sentence to a paragraph. | MC5 | major | low | medium | no |
| **R13** | Restructure to a methodological paper with empirical cases as evidence: compress governance to one section, move implementation-defect material to an appendix. | MC12, MC1 | major | high | **high** | no |
| **R14** | Subtitle: "Manufacture Trading Strategies" → "Create and Destroy Apparent Trading Opportunities". | minor 1 | minor | low | medium | no |
| **R15** | Rewrite the abstract to lead with the four measurements. | minor 3 | major | low | **high** | no |
| **R16** | Define "point-in-time" and "common support" formally at first use. | minor 11 | minor | low | low | no |
| **R17** | Descriptive family names in the body, codes retained in parentheses on first use and in the registry. | minor 4 | minor | medium | low | no |
| **R18** | Move internal artefact references from prose to footnotes/appendix. | minor 5 | minor | low | low | no |
| **R19** | Drop Figure 1, merging its content into Figure 2. Make all captions self-contained with units and sample sizes. | minor 6, 8 | minor | low | low | no |
| **R20** | Move Figure 6b to an appendix with its 8-of-25 limitation restated. **Do not regenerate the series.** | minor 7 | minor | low | low | no |
| **R21** | Relabel `ECONOMIC REJECT` → `IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED` in the taxonomy and use it consistently. | minor 13 | minor | low | low | no |
| **R22** | Narrow §10 to implications for research under comparable constraints. | minor 14 | minor | low | low | no |
| **R23** | Add a sentence to §5.3 stating that discovering one's own defect carries no information about markets. | MC1 | minor | low | medium | no |
| **R24** | State in §2/§3 the sequence argument explicitly: a bar chosen by judgement and held is weaker than a bar derived from theory and stronger than a bar chosen after the result. | MC3 | major | low | medium | no |

---

## Bucket 2 — V2, USES EXISTING ARTEFACTS ONLY

Reorganises values already committed. No economic recomputation, no new fit, no price load.

| # | revision | source artefact | severity | effort | impact | new exp. |
|---|---|---|---|---|---|---|
| **R25** | **Full-denominator appendix table: every family H1 → H19.2 with verdict, failure class and commit.** Plus an explicit statement in §1 that the four cases were selected retrospectively to illustrate a thesis formed after the families ran. | `docs/alpha_sprint/HYPOTHESIS_LEDGER.md`, git log | **critical** | medium | **high** | no |
| **R26** | Terminal-state counts across all families (how many reached each of the six labels), so the denominator is visible without importing H8's performance. | same | **critical** | low | **high** | no |
| **R27** | Threshold-classification table: every gate threshold marked `THEORETICAL`, `CONVENTIONAL` or `ENGINEERING JUDGEMENT`, with the conclusion it drives, plus an explicit statement that three conclusions are threshold-determined and their sensitivity is unmeasured. | `H18_3_PREREG.md`, `H19_2_PREFREEZE_FEASIBILITY.md` (`frozen_bars`), `H19_0_GATE.json` (`criteria[].bar`), `PREREGISTRATION_H13.md` | **critical** | medium | **high** | no |
| **R28** | Table 3 reduced to the five classes with cross-family recurrence or distributional cause; the rest to an appendix labelled "implementation defects, not claimed as contributions". Cite `scripts/h19_0_gate.py:307` as the in-code record that the gate-metric truthiness defect recurred. | `H18_1B_DATA_AUDIT.md`, gate scripts | major | medium | medium | no |
| **R29** | Paragraph in §6.1 showing, from hashes and commit order, that the pre-registration specified reporting obligations and the verdict vocabulary for **both** outcomes before the holdout was opened (`522bafb`, `203390b` precede `4aa4180`). | `H18_3_PREREG.md`, `.sha256` files, git log | major | low | **high** | no |
| **R30** | Count of defects caught at a gate before any economic result was produced, by stage, for §9.1's framework observables. | `HYPOTHESIS_LEDGER.md`, gate JSONs | major | medium | medium | no |
| **R31** | Extend the H8 paragraph to state what it does and does not establish, without importing performance. | `docs/DECISIONS.md` | minor | low | medium | no |

---

## Bucket 3 — FUTURE WORK, NEW EXPERIMENT REQUIRED (not executed)

| # | work | source | why it is a new experiment |
|---|---|---|---|
| **F1** | Threshold sensitivity: re-run gates and fits across a grid of the twelve thresholds and report which verdicts change. | MC3 | New fits and new gate evaluations. |
| **F2** | Two-way cluster bootstrap (asset-era × announcement date) and a temporal block bootstrap for H18.3. | MC7 | New resampling over fitted predictions. |
| **F3** | Weighted / trimmed / coarsened-match redesign of H19-P3A, with overlap diagnostics reported rather than a hard control count. | MC9 | A new design; would require reading price. **Because no price has ever been read, this would be a new study, not a rescue after seeing an outcome.** |
| **F4** | Independent second-party reconstruction of the 201-event universe from the venue archive. | MC15 | Requires a second researcher. |
| **F5** | Order-book or trade-level execution analysis for the H19.0 sample: spread, impact, fees, funding, latency, intraday volume distribution around T0. | MC8 | Requires data the program does not have. |
| **F6** | Replication of the venue-archive asymmetry on a second venue. | MC5 | New data collection. |

---

## Prioritisation

### MUST FIX BEFORE EXTERNAL RELEASE

These are the five conditions the referee named for outright rejection, plus the two items that make
the paper citable.

| | revision | why |
|---|---|---|
| 1 | **R25, R26** — full denominator and terminal-state counts | case selection conditioned on outcome, in a paper about selection effects, is not survivable |
| 2 | **R1** — split ex ante from ex post governance | a correctness issue: the paper's own evidence contradicts its framing |
| 3 | **R2, R3, R15** — novelty positioning and abstract | the contribution as stated is owned by literatures the paper does not cite |
| 4 | **R5** — `NULL` interpretation in the abstract and conclusion | the label is doing work the sample size cannot support |
| 5 | **R7, R8** — "coarse liquidity screen" and the narrowed common-support principle | both current claims exceed the evidence |
| 6 | **R27** — threshold classification and threshold-determined conclusions | three headline conclusions are threshold-driven and the paper does not say so |
| 7 | public repository with a DOI; compile `paper.tex` | minors 12 and 15; a reproducibility paper that cannot be fetched or compiled is not one |

### SHOULD FIX

R4, R6, R9, R10, R11, R12, R13, R24, R28, R29, R30.

### OPTIONAL

R14, R16, R17, R18, R19, R20, R21, R22, R23, R31.

---

## What this plan does not do

- It does not change any verdict. H18.3 remains `PRE-REGISTERED NULL`, H19.0 `PARTIAL PASS`, H19.2
  `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL`, H14 `OPEN`, and H13's economic question unresolved.
- It does not change any number. Every revision in buckets 1 and 2 changes framing, attribution,
  structure or wording, or adds a table built from values already committed.
- It does not resolve an open question by computation.
- It does not run anything in bucket 3.

Any V2 that changes a V1 claim must say so explicitly and must be traceable against the hashes in
`PAPER_V1_FREEZE.md`.
