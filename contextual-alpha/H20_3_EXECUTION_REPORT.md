# H20.3 — Incremental Context Information Test: Execution Report

**Mechanical verdict: PRE-REGISTERED NULL.**

PIT-valid C1–C3 public context did **not** add incremental out-of-time predictive information about
Binance full-asset delisting beyond the 23-feature market baseline, under the frozen primary
specification: L2 logistic at λ = 10, ΔPR-AUC = PR-AUC(M2) − PR-AUC(M0).

- The development Δ is −0.0095.
- Only 2 of 8 folds are positive.
- The two-way cluster-bootstrap 95% CI is [−0.062, +0.040].
- On the locked, context-unseen 2025 block Δ is −0.024.

No incremental context signal is claimed.

Executed exactly as frozen in H20.2, with the v1 specification superseded by Addendum 02.
- **H20.2 commit:** `9932e20`.
- **Execution:** 2026-10-19.

Every number below is in the `H20_3_*.json` files. Predictions are in `evidence/H20_3_*_PREDICTIONS_PRIMARY.csv`.

---

## 1. PIT audit — PASS (`H20_3_PIT_AUDIT.json`)

| stage | result |
|---|---|
| P0 freezes | every H20.1, H20.2 and A02 hash verified at the start of every stage (0 mismatches) |
| P1 context (353 decision times × 18 features) | 0 records after `t`; 0 vintages after `asof(t)`; 0 revisions after `t`; 0 windows ending after `t`; provenance 100%; two independent rebuilds byte-identical; 0 missing-encoding violations; only the 18 frozen features; context coverage 100% |
| P2 market | 0 daily rows after `w`; 0 removals or pair first-candles after `w` counted; batch-count recompute 0 / 500 mismatches; 0 excluded columns. **Route-state trigger fired** (window vs candle disagreement 4.554% > 1%), so the frozen candle-based fallback was applied to M09–M16, M19. Removal-permanence trigger did not fire (0.000%) |
| P3 X seal | `H20_3_X_SEAL.json`, 2026-10-19 19:35:18 UTC, before the lifecycle table was opened |
| P4 target | see §2 |
| P5–P6 | preprocessing fitted on training rows only; every fold's training landmarks ≤ test start − 366 d; same λ, folds, preprocessing and seeds for all arms; pre-LCUV freeze (19:41:47 UTC) before the single LCUV scoring; LCUV primary scored once (lock file) |

P2.8 reproducibility versus H18.3:
- the 8 market and liquidity features agree on 100% of matched rows;
- route-state and venue features differ only because of the candle-based fallback and H20's
  decision-time rule.

## 2. Target audit — PASS (`H20_3_TARGET_AUDIT.json`)

`y = 1` iff `t < A ≤ t + 365 d`, where `A` is the validated announcement time
(`announcement_public_time`, never `trading_end`) and `t` is the end of the landmark Monday.

- **Strict ISO parse:** 0 failures; 0 date-only values.
- **Era matching:** 0 events match more than one era. Four of 201 events attach to no era: IDRT and
  VAI (no candles, known) and SKY and USDS. The rebuilt `y` agrees 100% (0 differing rows, 93,394
  matched) with H18's inherited `y_365`, so those two were unattached there as well.
- **Risk set:** 259 already-announced landmarks removed; 0 such landmarks remain; follow-up complete
  for every landmark.
- **Sample floors** met: the minimum fold has 20 test events (bar 5), and the LCUV block has 86 (bar 20).

## 3. Sample and effective units

| set | landmark rows | asset-eras | weeks | positive rows | **unique events** | base rate |
|---|---|---|---|---|---|---|
| DEVELOPMENT | 78,227 | 522 | 313 | 4,555 | **110** | 5.82% |
| development OOF (8 folds) | 37,772 | — | 104 | — | 20–35 per fold | — |
| LCUV 2025 | 15,167 | 443 | 40 | 1,789 | **86** | 11.80% |

The context arms rest on **104 development test weeks and 40 LCUV weeks**. Positive landmark weeks
are not independent events.

## 4. Primary results (L2 logistic, λ = 10)

### Development, pooled out-of-fold

| arm | PR-AUC | ROC-AUC | Brier | top-decile lift (within-week) | within-week PR-AUC | calib. slope |
|---|---|---|---|---|---|---|
| **M0** market | **0.2300** | 0.767 | 0.0512 | 4.51 | 0.247 | 0.67 |
| **M2** market + context | **0.2205** | 0.750 | 0.0521 | 4.60 | 0.244 | 0.52 |
| M1 context only | 0.0674 | 0.540 | 0.0592 | 0.64 | 0.059 | 0.17 |
| M2_core | 0.2303 | 0.759 | 0.0522 | 4.61 | 0.245 | 0.58 |
| M1_core | 0.0675 | 0.541 | 0.0573 | 0.64 | 0.059 | 0.20 |

**ΔPR-AUC (M2 − M0) = −0.0095** (relative −4.1%).

| fold | test window | events | Δ |
|---|---|---|---|
| 1 | 2022-Q1 | 31 | −0.0119 |
| 2 | 2022-Q2 | 27 | −0.0101 |
| 3 | 2022-Q3 | 27 | −0.0022 |
| 4 | 2022-Q4 | 24 | −0.0115 |
| 5 | 2023-Q1 | 22 | −0.0061 |
| 6 | 2023-Q2 | 20 | +0.0009 |
| 7 | 2023-Q3 | 27 | +0.0074 |
| 8 | 2023-Q4 | 35 | −0.0106 |

**Positive folds: 2 of 8.**

**Bootstrap (2,000 replicates, seed 20261103, no refits, 0 redraws).** 95% CIs for Δ:
- two-way asset-era × fold-block: **[−0.0621, +0.0405]**;
- asset-era only: [−0.0653, +0.0388];
- block only: [−0.0224, +0.0054].

**Era robustness.**
- Δ by era block: 2022 = −0.0073, 2023 = +0.0080, 2025 LCUV = −0.0240, so 1 of 3 eras is positive.
- Leave-one-fold-out pooled Δ is negative in every case (minimum −0.0143).

### LCUV block (2025, scored once)

| arm | PR-AUC | ROC-AUC | Brier | lift | within-week PR-AUC | slope |
|---|---|---|---|---|---|---|
| **M0** | **0.3270** | 0.809 | 0.0929 | 3.21 | 0.350 | 1.05 |
| **M2** | **0.3029** | 0.806 | 0.0960 | 3.12 | 0.330 | 0.99 |
| M2_core | 0.3112 | 0.808 | 0.0972 | 3.10 | 0.337 | 1.01 |
| M1 / M1_core | 0.119 / 0.121 | 0.51 | — | 0.87 | 0.118 | — |

**LCUV ΔPR-AUC = −0.0240** (relative −7.4%). The informational asset-era × month interval is
[−0.061, +0.001].

**S5 values:** Brier(M2)/Brier(M0) = **1.033** (bar ≤ 1.05); slope excess
|0.994 − 1| − |1.050 − 1| = **−0.044** (bar ≤ 0.20).

## 5. Criteria and mechanical verdict (`H20_3_VERDICT.json`)

| | criterion | value | result |
|---|---|---|---|
| S1 | development Δ > 0 | −0.0095 | **FAIL** |
| S2 | ≥ 5 of 8 folds positive | 2 | **FAIL** |
| S3 | two-way CI lower bound > 0 | −0.0621 | **FAIL** |
| S4 | LCUV Δ > 0 | −0.0240 | **FAIL** |
| S5 | no severe calibration deterioration | 1.033 ≤ 1.05; −0.044 ≤ 0.20 | PASS |
| S6 | PIT audit | all stages PASS | PASS |
| S7 | ≥ 2 of 3 eras positive, and leave-one-fold-out Δ > 0 | 1 of 3; min −0.0143 | **FAIL** |

No DATA / DESIGN FAILURE condition holds. Not every criterion holds. NEGATIVE INCREMENTAL RESULT
needs the development CI upper bound below 0, and it is +0.0405. So the verdict is **PRE-REGISTERED
NULL**.

## 6. Annotations (cannot change the verdict)

**Materiality:** SMALL.

**CONTEXT_CORE robustness** (classifier-free context, M2_core vs M0):
- development Δ +0.0003, 3 of 8 folds positive, two-way CI [−0.042, +0.045];
- LCUV Δ −0.0158.
- The null does not depend on the agent-audited classifiers.

**Exploratory** (`H20_3_EXPLORATORY_RESULTS.json`, labelled EXPLORATORY). The selection-tuned
models show positive development Δ but negative LCUV Δ:

| model | dev Δ | LCUV Δ |
|---|---|---|
| logistic, fold-selected λ (= 1000 for M0, M2 and M2_core) | +0.027 | −0.017 |
| LightGBM, a-priori default | +0.029 | −0.008 |
| LightGBM, fold-selected | +0.027 | −0.003 |

The selected configurations were chosen on the same folds that score them, which is the optimism
A02 removed from the primary, and none survives on the LCUV block. These results do not support
reopening the verdict. Under the frozen rules they cannot.

**Context-only arms** (M1, M1_core) are near the base rate. Development ROC-AUC is about 0.54 and
LCUV about 0.51. Common-to-all-assets context ranks weeks, not assets, and here it barely ranks weeks.

## 7. Claim scope and limitations

**Allowed claim.** In the locked retrospective / context-unseen evaluation, the frozen PIT-valid C1–C3
context set did not add incremental predictive information beyond the market baseline. This is a
pre-registered null.

**Not claimed.** No absence of any context effect in general. The test has low effective power: 104
and 40 test weeks, 110 and 86 events. No trading, profitability, alpha, tradability, shorting or
P&L claim of any kind is made.

**Scope.**
- C2 is US-only.
- C3 is only generic English-Wikipedia crypto attention.
- C4, C5, GDELT and every text-model representation are excluded.
- Eight context features rest on agent-audited classifiers; the classifier-free core gives the same
  null.

**The 2025 block** was the H18.3 holdout for market-only models. It is described as LOCKED /
CONTEXT-UNSEEN, never as an untouched holdout or external confirmation. **PROSPECTIVE_CONFIRMATION
remains unopened.**

**Implementation notes** (`H20_3_EXECUTION_DEVIATIONS.md`):
- parallelised context collection;
- the frozen route-state fallback (a frozen trigger, not a choice);
- ALFRED transport retries;
- LightGBM through its native API, with exploratory code changes verified not to touch the primary
  code;
- the test-scope exemption for H20.3 scripts.

**STOP.** H20.4 is not begun. The pre-registration is not modified.
