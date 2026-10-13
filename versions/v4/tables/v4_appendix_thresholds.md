# Appendix C table — Threshold inventory

Authored, not generated: the classification maps artefact values onto a taxonomy defined in this
paper. Every *value* is read from a committed artefact (`H18_3_PREREG.md`,
`H19_2_PREFREEZE_FEASIBILITY.md` `frozen_bars`, `H19_0_GATE.json` `criteria[].bar`,
`docs/alpha_sprint/PREREGISTRATION_H13.md`, the filing-family gate JSONs); every *class* is a
judgement stated here.

Classes: **THEORETICAL** — derived from a theorem or an explicit model of the decision.
**CONVENTIONAL** — borrowed from an established convention in a literature. **ENGINEERING
JUDGEMENT** — researcher-chosen practical bar.

| experiment | threshold | value | purpose | class | rationale recorded? | conclusion affected | sensitivity measured? |
|---|---|---|---|---|---|---|---|
| H13 | burn-tertile spread | ≥ +20 pp | predictive strength | ENGINEERING JUDGEMENT | no | `IMPLEMENTATION REJECT` (measured +11.14 pp) | no |
| H13 | filter improvement over raw screen | ≥ +10 pp | materiality | ENGINEERING JUDGEMENT | no | contributes to the same verdict (measured +1.9 pp) | no |
| H13 | dilution spread | ≥ +10 pp | secondary mechanism | ENGINEERING JUDGEMENT | no | contributes (measured +7 pp) | no |
| H15 / H16.1 / H17.0 | field accuracy bars | 95% to 99% | extraction validity | CONVENTIONAL | gold-standard practice in information extraction | the `DATA-GATE FAIL` verdicts | no |
| H17.0 | yearly price-coverage floor | ≥ 85% | usable history | ENGINEERING JUDGEMENT | no | `INFRASTRUCTURE BLOCKED` (1 of 17 years) | no |
| H18.1b | catalog coverage guard | ≥ 99% of the source's own reported total | harvest completeness | ENGINEERING JUDGEMENT | the source's total is objective; the 99% is not | guard fired at 0.9887 and refused to write | no |
| H18.2 / H18.3 | risk-set entry | 90 days after first candle | remove a listing-age artefact | ENGINEERING JUDGEMENT, **post-hoc origin** | chosen after a 6.22 pp coverage differential was observed; reduced it to 0.09 pp against a 5.0 pp bar | eligibility of early landmarks | no |
| H18.3 | bootstrap confidence | 95%, one-sided 95% | scientific support | CONVENTIONAL | standard interval convention | **`PRE-REGISTERED NULL`** (measured 93.45%) | no |
| H18.3 | relative ΔPR-AUC | ≥ 10% | materiality | ENGINEERING JUDGEMENT | no | passed (13.46%) | no |
| H18.3 | top-decile lift improvement | ≥ 15% | materiality | ENGINEERING JUDGEMENT | no | passed (20.0%) | no |
| H18.3 | \|calibration slope shift\| | < 0.10 | materiality | ENGINEERING JUDGEMENT, **defective as written** | no; penalises improvement as well as deterioration | materiality `FAIL` (0.1948, on an improvement) | no |
| H18.3 | outcome horizon | 365 days | estimand | ENGINEERING JUDGEMENT, fixed ex ante on lifecycle and actionability | stated in the pre-registration | defines the estimand | no |
| H19.0 | Tier-1 event count | ≥ 80 | sample adequacy | ENGINEERING JUDGEMENT | no | `PARTIAL PASS` (measured 75) | no |
| H19.0 | single-year concentration | ≤ 40% | sample balance | ENGINEERING JUDGEMENT | no | `PARTIAL PASS` (measured 46.0%) | no |
| H19.0 | small-order liquidity screen | US$1,000 ≤ 1% of median hourly notional, in ≥ 90% of events | capacity | ENGINEERING JUDGEMENT | no | the 32 operating point (measured 50.79%) | no |
| **H19.2** | **matched controls per event, m** | **≥ 20** | **comparison adequacy** | **ENGINEERING JUDGEMENT** | **no** | **`DESIGN INFEASIBLE`** (median attainable 1) | **no** |
| **H19.2** | **confirmatory events, N_min** | **≥ 40** | **power** | **ENGINEERING JUDGEMENT** | **no** | **the stop** (N\* = 10) | **no** |
| H19.2 | valid transitions per event | ≥ 73 | grid adequacy | ENGINEERING JUDGEMENT | approximately 80% of the 91 possible | 1 of 62 events excluded; never binding | no |
| H19.2 | leg availability | ≥ 95% | data adequacy | CONVENTIONAL | common coverage convention | not binding (99.3%) | no |

**Summary.** 19 thresholds: **0 THEORETICAL**, **2 CONVENTIONAL**, **17 ENGINEERING JUDGEMENT**, of
which one has a post-hoc origin and one is defective as written.

**Three conclusions in this research program are threshold-determined:** the infeasibility verdict
(from *m* = 20 and *N_min* = 40), the 32 operating point in the liquidity screen (from the 1% rule),
and a materiality criterion in the pre-registered test (from a calibration bar that penalises
improvement).

> **Pre-specification protects against outcome-driven threshold movement; it does not make an
> arbitrary threshold theoretically correct.**

**A hierarchy of bars.** (1) derived from a model — none here; (2) borrowed from an established
convention — two; (3) engineering judgement fixed before the measurement and not moved — the rest;
(4) chosen or adjusted after seeing the result — none, by construction. Level-3 discipline protects
the sequence, not the value. The correct reading of "do not move the bar" is that it kept level-3
bars from becoming level-4 bars; it is not a claim that the bars were right.

**Threshold sensitivity is unmeasured.** Quantifying it requires re-running the gates and fits
across a grid of alternative bars, which was not done.
