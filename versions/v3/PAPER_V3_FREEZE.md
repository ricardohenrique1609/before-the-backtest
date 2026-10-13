# PAPER V3 — FREEZE RECORD

> **V3 is frozen as reviewed.** V1 and V2 remain frozen and byte-identical. The six editorial
> revisions required by `REFEREE_REPORT_V3.md` are **not applied here**: the referee reviewed this
> text, and silently amending a reviewed version is the practice this research program exists to
> avoid. They are the scope of V4 (§8).

**V3 is not external-release ready.** See §7.

---

## 1. Identity

| | |
|---|---|
| title | **Before the Backtest: Pre-Freeze Common-Support Ceilings for Event-Driven Strategy Research** |
| version | **V3** |
| frozen | 2026-10-11 |
| revision basis | `REFEREE_REPORT_V2.md` (MAJOR REVISION — no single clear contribution) |
| directory | `papers/falsification_first_alpha_discovery/v3/` |

### Title selection

Five candidates were considered and scored on accuracy, academic fit, one-contribution clarity and
journal fit.

| # | candidate | assessment |
|---|---|---|
| 1 | **Before the Backtest: Pre-Freeze Common-Support Audits for Event-Driven Strategy Research** | **selected, with "Audits" → "Ceilings"**: names the object, the timing and the domain; "ceiling" is the quantity the paper actually computes, and is more specific than "audit" |
| 2 | Can This Study Be Identified? Pre-Freeze Feasibility Gates for Event-Driven Trading Research | accurate, but the question form reads as a practitioner piece and "trading research" is broader than the domain |
| 3 | Before Opening the Outcome: Common-Support Feasibility in Systematic Event Studies | good academic fit; loses the pre-registration/freeze element that distinguishes the procedure from Rubin's |
| 4 | Pre-Freeze Design Feasibility in Event-Driven Quantitative Research | accurate but flat; "design feasibility" is vaguer than the measured object |
| 5 | The Study That Should Not Be Run: Outcome-Blind Common-Support Audits Before Backtesting | sensational; rejected on that ground |

## 2. Frozen hashes — V1 and V2, re-verified

All ten unchanged, checked by `scripts/paper_audit_v3.py`, which verifies them first and aborts with
exit status 2 without running anything else if one has moved.

| version | file | SHA-256 | state |
|---|---|---|---|
| V1 | `paper.md` | `1853bce01e638da159733ab61fd3d4945ba51a160d3ddc156ab26fa57da95cef` | unchanged |
| V1 | `paper.tex` | `2abad0f88b468ea542ef32d838539c7c29b8d5683a907f96cb56b2328d0d97e7` | unchanged |
| V1 | `CLAIM_EVIDENCE_MATRIX.csv` | `a1b97453ada9f3397f317f6b3e15d720ff5791c60896e37fea0539d8e98cb781` | unchanged |
| V1 | `PAPER_QA.md` | `357c25b9490e109d08af8092f1b0079ab91529b1b21cf26e60d206eaef8fe9be` | unchanged |
| V1 | `REPRODUCIBILITY_APPENDIX.md` | `6ea8edaa0a94f9c989f206229ac386b47c548cbd61938a08ef70e291c72adcff` | unchanged |
| V2 | `paper_v2.md` | `b2c3ddaed36fd7371a16cf9f5b75c39272dbd38edc10a482d114c9a187bfd157` | unchanged |
| V2 | `paper_v2.tex` | `ad18523888093b1cc54956babea531581edcac1000243fc6b42ec2eb0b7a9cbd` | unchanged |
| V2 | `CLAIM_EVIDENCE_MATRIX_V2.csv` | `47d22e1e1abd7669f4cd68c852ac41751461caba2ad395df3a7463a275afbd7f` | unchanged |
| V2 | `references_v2.bib` | `543d467791d55fe734334fd107f91ab143bb00d02b1ac1a3b36b47418e9b298c` | unchanged |
| V2 | `PAPER_QA_V2.md` | `7bf5cae957da8f2108dd59057d23e81a8d88a5e7de5f8e321885c89da5958273` | unchanged |

## 3. V3 hashes

| file | SHA-256 | bytes |
|---|---|---|
| `paper_v3.md` | `5f5468eb80e44fba50b8fb240e526b346f536f76d4ee900b6149ad1cb28cc547` | 56,873 |
| `paper_v3.tex` | `668387d707d579506424c5fa9c8c1bf4880b88cc81a8dd8577dddd17197b69a6` | 61,802 |
| `CLAIM_EVIDENCE_MATRIX_V3.csv` | `39eb3cfb7c0c3713d62e5037576c4033a9858436d96022247c134616745a85b0` | 44,458 |
| `references_v3.bib` | `dd98e55260855990a6e105a0ed125e3ed5a169bb02ca3cdccac345d73815c11f` | 18,931 |
| `PAPER_QA_V3.md` | `b37436d944fa05520e952812c6999ec96034a36eb3b3bdc3964fcf8d5a016470` | 8,598 |
| `REFEREE_REPORT_V3.md` | `373ee752ba7ea156eb5c6e7222fa1e4296796f42863ffe16df0571ddfb67295e` | 13,588 |

## 4. The central contribution

> **Pre-freeze common-support ceiling.** Given a proposed event set, a complete point-in-time
> candidate-control universe, an intended matching rule, a minimum support per event *m* and a
> minimum admissible confirmatory sample *N_min*: compute the attainable support
> `S_e = |{c ∈ C(t_e) : M(e, c, t_e) = 1}|` on the **complete** eligible pool at each event time,
> form `N* = Σ 1[S_e ≥ m]`, and if `N* < N_min`, stop **before** the pre-registration is frozen and
> **before** any outcome column is opened. The status is
> `DESIGN INFEASIBLE UNDER THIS SPECIFICATION` — not a null, not a rejection, hypothesis untested.

**Novelty, as stated in the manuscript:** the design-stage principle is Rubin's (2008); outcome-free
two-stage design is codified (Li 2023); design-stage overlap diagnostics exist as tooling
(`PSweight`); positivity and its remedies are established (Petersen et al. 2012). The manuscript
claims only the combination — full-population, point-in-time, pre-freeze, outcome-blind, with a
pre-registered numeric stop rule, for matched event studies in systematic strategy research — and
states that if that combination exists elsewhere, the contribution reduces to the §4 demonstration.

## 5. Exact V2 → V3 changes

### Removed

| # | removed from V2 | reason |
|---|---|---|
| 1 | the broad thesis that apparent alphas are manufactured by data errors | the registry does not support it; §7 says so |
| 2 | the claim that pre-model failure is typically decisive | same |
| 3 | four co-equal contributions | referee V2 §9: no single clear contribution |
| 4 | six of the ten principles from the body | → Appendix E |
| 5 | the result taxonomy, defect taxonomy and threshold inventory from the body | → Appendices C and D |
| 6 | V2 Figures 1 (registry denominator) and the V1 lifecycle/fold figures from the main set | four figures retained; the fold figure's content is in §6.3 |
| 7 | the 32 operating point as a headline | → Appendix A.1, demoted to one point on a reported distribution |
| 8 | the title "Falsification-First Alpha Discovery…" | too broad for the narrowed claim |

### Added

| # | added in V3 | source |
|---|---|---|
| 9 | §2 as the methodological core, with the boxed procedure in §2.3 | the single contribution |
| 10 | §2.6, itemising what is inherited (Rubin, Li, `PSweight`, Petersen) and what is added | referee V2 §2 |
| 11 | three new references: Rubin (2008), Li (2023), `PSweight` | novelty check round 3 |
| 12 | §2.3's upper-bound argument: why a full-pool ceiling differs from a sample diagnostic | — |
| 13 | §4.4 **floor invariance**: from the reported p75 of 2, at most 15 of 62 events clear any floor ≥ 3, so no defensible *m* yields 40 | derived from committed quantiles; **no recomputation** |
| 14 | §4.2's argument that the warning stratum is load-bearing (52 of 62 assets warned) | — |
| 15 | §3's statement of where the setting is favourable and where it is a fair test | — |
| 16 | §5's verification-asymmetry argument and the cost of the stop | referee V2 §6 |
| 17 | §6.3's base-rate / estimand paragraph | referee V2 §5 |
| 18 | §7's "a claim about a procedure, not a prevalence" | referee V2 §3 |
| 19 | §8's endogenous-ceiling limitation (134 warned assets is a venue policy) | — |
| 20 | Appendix A.1: the liquidity **distribution**, 2 / 21 / 32 events at ≤0.10% / ≤0.50% / ≤1.00% | referee V2 §6 |

### Unchanged

**No verdict changed. No number produced by an experiment was recomputed.**

| family | label |
|---|---|
| H18.3 | `PRE-REGISTERED NULL`, with the bounded interpretation |
| H19.2 | `DESIGN INFEASIBLE UNDER THIS SPECIFICATION` — the V2 `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL` state restated in the procedure's vocabulary; substance identical |
| H19.0 | capacity screen, 32 demoted to one operating point |
| H14 parent | `OPEN` |
| H13 | `IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED` |

## 6. Contents

| | V1 | V2 | V3 |
|---|---|---|---|
| body words | 9,394 | 10,786 | **7,026** (target 7,000–8,500) |
| total words | 9,753 | 11,643 | 8,860 |
| sections | 12 | 13 | **9** + 5 appendices |
| figures | 6 | 6 | **4** |
| body tables | 5 | 5 + 2 | **3** |
| appendix tables | — | — | **6** |
| references | 14 | 22 | **25** |
| claim rows | 126 | 150 | **161** (126 V1, 24 V2, 11 new) |
| principles in the body | 10 | 10 | **4** |

QA: `[freezes] 10 files, 0 changed` · `[claim] 87 tokens, 0 unsupported` · `[required] 24 checks, 0
failures` · `[verdicts] 4 labels, 0 failures` · **PASS**.

## 7. Referee V3 recommendation and release status

**`REFEREE_REPORT_V3.md`: MINOR REVISION.**

The V2 referee's conditional statement — Minor Revision on a restructure around one contribution with
the thesis narrowed — was tested and honoured. Both conditions are met: one contribution stated in
the abstract, §1.5 and §9; the thesis narrowed to the domain §7 supports.

The referee credits the floor-invariance result as substantially mitigating the threshold objection,
and credits the author for citing Rubin (2008) against their own novelty claim, noting that had the
referee found it first the report would have been a novelty rejection.

**Release blockers, unchanged:**

| blocker | status |
|---|---|
| no independent verification of any result | **open**; the cheapest check is named in §8 and not performed |
| no public repository or DOI | **open** |
| manuscript never compiled | **open**; no LaTeX distribution in this environment |
| threshold sensitivity to the **matching rule** unmeasured | **open**; the floor and *N_min* are now bounded, the matching rule is not |

**Nothing has been submitted, uploaded, posted or assigned a DOI.** Release is a separate explicit
task.

## 8. V4 scope — the six revisions the referee requires

Applied in V4, not here, so that `REFEREE_REPORT_V3.md` continues to describe the text it reviewed.
**None requires running anything.**

1. Extend the floor-invariance bound to *N_min* in §4.4: with N\* ≤ 15 for any floor ≥ 3, the design
   fails for any *N_min* above 15.
2. State in §4 that the procedure is demonstrated once, on a case that returned infeasible, with no
   reported instance in which it returned feasible — evidence about detection, not specificity.
3. Name the **matching rule**, not the floor, as the largest unmeasured sensitivity in §8.
4. Caption Figure 4's band as a recorded range, not an interval.
5. Cite Appendix A.2 from the body or remove it.
6. Optionally move the base-rate paragraph from §6.3 to the appendix.

## 9. Reproduction

```bash
.venv/Scripts/python -I scripts/paper_build_v3.py   # 4 figures, 3 body tables, 4 carried appendix tables, paper_v3.tex
.venv/Scripts/python -I scripts/paper_audit_v3.py   # V1+V2 integrity, then the V3 audits
```

Both read only committed artefacts. **No experiment was run at any point in producing V3**: no
threshold sensitivity, no bootstrap, no alternative matching, no price load, no order-book study, no
independent reconstruction, no new return. No gate, verdict, pre-registration or historical artefact
was altered.
