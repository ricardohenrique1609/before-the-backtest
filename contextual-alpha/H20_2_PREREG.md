# H20.2 — Pre-Registration of H20.3

**Status: FROZEN.** The SHA-256 of this file and of every specification it cites is in
`H20_2_FREEZE.json`. Nothing here was chosen after seeing an outcome. A later change is a filed
amendment, never an edit.

**Date:** 2026-10-19 · **HEAD at start:** `e21c264` (H20.1 committed) · **Write zone:**
`Contextual Alpha/` only.

**State at freeze:**
- no `y` was read and no lifecycle-table row was opened;
- no return after `t`, no model and no metric was computed;
- no H18.3 results file was read (final report, development report, gate, rolling-origin, bootstrap,
  holdout or OOF predictions).

---

## 1. Question and hypotheses

> Does PIT-valid public context add incremental out-of-sample predictive information about Binance
> full-asset delisting beyond structured market data?

- **H-C1:** PR-AUC(M2) > PR-AUC(M0) out of time.
- **H0:** context adds no out-of-time information beyond the market baseline.

A null or negative result is a finding. No trading or profitability claim is made (that belongs to a
possible H20.4).

## 2. Unit, decision time, target

| | frozen value (`H20_2_TEMPORAL_SPLIT.json`) |
|---|---|
| unit | (asset-era, landmark week); asset-era per inherited rule A7 |
| decision time | **t = Monday w + 1 day, 00:00 UTC** (end of the landmark Monday) |
| target | **y = 1 iff the asset-era's validated full-asset delisting announcement A satisfies t < A ≤ t + 365 d** |
| event source | `H18_1B_FULL_DELIST_EVENTS.parquet` (frozen; 201 events); `announcement_public_time`, never `trading_end` |
| risk set | inherited H18.2/H18.3 exposure window and 90-day age rule, plus: a landmark whose announcement is ≤ t is excluded |
| censor | t + 365 d ≤ 2026-10-09 |

**Target reconstructibility: RECONSTRUCTIBLE, conditional on two sealed checks**
(`evidence/H20_2_TARGET_SCHEMA_CHECK.json`). From schema and metadata only:
- event id, ticker, announcement time and trading end are present with 0 nulls;
- the era inputs are present;
- the join rule is deterministic.

Two checks need row values, which H20.2 may not read. They run in the sealed H20.3 target stage,
after X is hashed. If either fails, H20.3 stops as DATA / DESIGN FAILURE before any fit:
- strict ISO parse of every announcement time (stored as a string);
- at most one era per event.

The H18 `y_365` column is not reused, because its decision-time convention differs (see the plan §2).

## 3. Features

- **X_market** — the 23 admissible columns of `MARKET_FEATURE_REGISTRY.csv` (M01–M22):
  - market and liquidity (8);
  - route state (7);
  - regime, including a calendar trend (3);
  - **notice-free** route history (5).

  The H18.3 route-history features that rest on `QUOTE_RETIREMENT`, a class taken from Binance notice
  titles (C4, from the truncated H18.1b snapshot), are **excluded** and replaced by class-free versions.
  Current listing status, whole-era quantities, outcome columns and the Monitoring Tag are excluded.
  Every exclusion is listed with its reason.
- **CONTEXT_EXPANDED** — exactly the 18 H20.1-eligible features (`H20_2_CONTEXT_SETS.json`), built
  at every landmark `t` with the unchanged H20.1 rules (`h20_1_rep_v1`).
- **CONTEXT_CORE** — the 10 classifier-free features: none depends on the agent-audited
  classifiers K1a, K1b, K2, K3 or K4. This is a robustness comparison fixed now, not a replacement.
- C3 is represented only by **generic English-Wikipedia crypto attention**
  (`c3_wiki_crypto_item_count_D7`). That is not a systemic-crypto-state measure. No GDELT, C4, C5,
  LLM or repaired feature is used.
- The semantic audit behind K1a/K1b/K2/K3/K4 was agent-produced, is not re-annotated and is not
  retuned.

## 4. Arms and models (`H20_2_MODEL_SPEC.json`)

| arm | features | role |
|---|---|---|
| M0 | X_market | **primary baseline** |
| M1 | CONTEXT_EXPANDED | secondary |
| M2 | X_market + CONTEXT_EXPANDED | **primary treatment** |
| M1_core | CONTEXT_CORE | robustness |
| M2_core | X_market + CONTEXT_CORE | robustness |

**Primary model class:** L2-penalised logistic regression (numpy/scipy), λ ∈ {0.1, 1, 10, 100, 1000}.
**Secondary class:** LightGBM 4.7.0 with 4 configurations. The grid, folds, preprocessing, missing
treatment (train medians + indicators; native NaN for trees), unweighted classes, absence of
recalibration and seeds are identical for every arm. Selection is by mean fold PR-AUC inside
DEVELOPMENT only.

## 5. Temporal design (`H20_2_TEMPORAL_SPLIT.json`)

| block | landmark Mondays | role |
|---|---|---|
| DEVELOPMENT | 2018-01-01 … 2023-12-25 (313 weeks) | fitting, selection, 8 rolling-origin folds |
| EMBARGO | 2024-01-01 … 2024-12-30 | dropped (one horizon) |
| **HOLDOUT_H20** | 2025-01-06 … 2025-10-06 (40 weeks) | opened **once**, after the pre-holdout freeze |
| PROSPECTIVE_CONFIRMATION | 2025-10-13 … 2026-09-28 (51 weeks) | outcomes not yet observable; reserved |

The 8 folds use expanding training from 2018-01-01, a 365-day embargo and 13-week test windows
through 2022–2023. They are H18.3's frozen calendar, regenerated from its rule. Dates were chosen on
calendar and follow-up grounds only.

## 6. Metrics, inference, verdicts

- **Primary:** ΔPR-AUC = PR-AUC(M2) − PR-AUC(M0), on pooled out-of-fold development predictions and
  on the holdout (`H20_2_METRICS_SPEC.json`).
- **Secondary:** ROC-AUC, Brier, cross-sectional within-week top-decile lift, calibration
  slope/intercept/ECE, within-week PR-AUC, and per-fold and per-era Δ.
- **Uncertainty:** a pigeonhole two-way cluster bootstrap over asset-eras × calendar blocks, 2,000
  replicates, seed 20261103 (`H20_2_INFERENCE_SPEC.md`).

**Verdicts (closed list, `H20_2_VERDICT_RULES.json`):** **INCREMENTAL CONTEXT SIGNAL SUPPORTED**
requires all of S1–S7:

| | condition |
|---|---|
| S1 | development Δ > 0 |
| S2 | Δ > 0 in ≥ 5 of 8 folds |
| S3 | bootstrap CI lower bound > 0 |
| S4 | holdout Δ > 0 |
| S5 | no severe calibration deterioration |
| S6 | PIT audit clean |
| S7 | not driven by one era: ≥ 2 of 3 era blocks positive, and leave-one-fold-out Δ > 0 |

The other verdicts:
- **NEGATIVE INCREMENTAL RESULT:** the development CI lies entirely below 0 and holdout Δ < 0.
- **DATA / DESIGN FAILURE:** the PIT audit or the sealed target checks fail, a sample-adequacy floor
  is not met, a fit fails to converge, or the holdout is reopened.
- **PRE-REGISTERED NULL:** everything else.

Materiality and robustness are reported as annotations: the classifier-free arm, LightGBM, and the
a-priori defaults. They never change the verdict.

## 7. PIT conditions

`H20_2_PIT_AUDIT_PLAN.md` lists the context, market, target and modelling checks. Two of them carry
**frozen structural fallbacks**: route-state gaps and removal permanence. The fallbacks are triggered
only by structural disagreement rates, never by performance.

## 8. Disclosed exposures and limits

1. **Holdout reuse.** HOLDOUT_H20 is the same calendar block H18.3 opened for market-only models. No
   context model and no H20 model has seen it, and this design read no H18.3 result. However, the
   research programme has seen market-baseline performance there. ΔPR-AUC on it is untouched; M0's
   level is not. The PROSPECTIVE_CONFIRMATION block is the only block untouched by the programme,
   and it cannot be scored until outcomes mature after 2027-09-28.
2. **Design-time knowledge.** The H18.3 pre-registration (read for its design) carries per-block
   event counts, base rates and one burned descriptive observation about `route_ratio_to_peak`. No
   choice here depends on them beyond the inherited calendar.
3. **Low effective power for context.** Context is common to all assets in a week, so its evidence
   rests on 104 development test weeks and 40 holdout weeks, with about 110 / 86 unique events. A
   null is the likely outcome under modest effects.
4. **Selection optimism.** Hyperparameters are selected on the same folds that report Δ. The
   optimism is symmetric across arms (same grid), and the a-priori-default results are reported.
5. **Agent-produced semantic audit** for 8 of the 18 context features (see CONTEXT_CORE).
6. **Scope.** C2 is US-only; C3 is English-Wikipedia attention only; C1–C3 inherit H20.0's archive
   and language conditions; route state comes from candle windows (audited); IDRT and VAI are
   unmodellable (no candles).
7. **Environment.** scikit-learn is absent from the repository venv. Models and metrics are
   implemented on numpy/scipy (as H18.3 did) plus LightGBM 4.7.0, with definitions frozen in the
   specs.

## 9. Stop rule

H20.2 ends here. **No y is loaded, no model is trained, H20.3 is not executed.** H20.3 begins only
on sponsor authorisation and then follows `H20_2_EXPERIMENT_PLAN.md` §5 in order.
