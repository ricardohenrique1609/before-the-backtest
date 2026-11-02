# H20.2 — PIT Audit Plan for H20.3

Every check below must read **0 violations** (or meet its stated bar) before any model is fitted in
H20.3. A failure is criterion S6 of `H20_2_VERDICT_RULES.json` and makes the verdict
**DATA / DESIGN FAILURE**. No check may be weakened after it has been run.

## 0. Order of operations (outcome isolation)

```
P0  verify freezes (H20_2_FREEZE.json, H20.1 rules module) -> build landmark calendar from the split
P1  context features at every landmark t (H20.1 rules, unchanged) -> PIT + provenance audit
P2  market features at every landmark t                           -> PIT audit
P3  X = market + context, hashed                                  -> manifests/H20_3_X_SEAL.json
P4  SEALED target stage: read the lifecycle table, build y, run the two value checks -> y hashed
P5  development fits, folds, selection                            -> pre-holdout freeze hashed
P6  holdout scored once
```

Scripts before P4 may not open `H18_1B_FULL_DELIST_EVENTS.parquet` or any column named
`event_*`, `y_*`, `days_to_delist_*`, `ever_delisted`, `is_live_now`, `any_live`. A test scans
them. The target script (P4) is the only reader of the lifecycle table, and it refuses to run unless
`H20_3_X_SEAL.json` exists and matches the X files.

## 1. Context (P1)

| # | check | bar |
|---|---|---|
| P1.1 | `scripts/h20_1_rep.py` sha256 equals `H20_1_REPRESENTATION_FREEZE.json` | equal |
| P1.2 | every provenance record has `public_availability_time ≤ t` | 0 violations |
| P1.3 | every ALFRED vintage date ≤ `asof(t)`; every Wikipedia revision ≤ `t` | 0 |
| P1.4 | windows end at `t` (no post-`t` join) | 0 |
| P1.5 | provenance completeness (H20.1 plan §9 rules) | 100% |
| P1.6 | deterministic: two builds, identical sha256 | identical |
| P1.7 | missing values are `NaN` with a reason, never 0 | 0 |
| P1.8 | context values identical for all assets at the same `t` | 0 differences |
| P1.9 | only the 18 frozen features are produced; no GDELT / CFTC / C4 / C5 input is read | 0 |

## 2. Market (P2)

Decision time `t = w + 1 d 00:00 UTC` (end of the landmark Monday).

| # | check | bar |
|---|---|---|
| P2.1 | every daily row joined into X has `date ≤ w` (i.e. `< t`); as-of tolerance 10 days | 0 violations |
| P2.2 | no candle, conversion rate or price dated after `w` enters any window | 0 |
| P2.3 | **route-state gap audit.** Recompute `n_active_spot_pairs` from candles: a pair is active iff it has a daily candle in `[w − 6 d, w]`. Compare with the window-based value at every landmark | disagreement ≤ 1% of landmarks. Above 1%, the **frozen fallback** applies: M09–M16 and M19 are rebuilt from the candle-based definition for all landmarks and every arm. This is not an outcome-driven choice: the switch depends only on this structural disagreement rate |
| P2.4 | **removal permanence.** Every removal counted at `t` has `removal_date ≤ w`. The share of counted removals whose symbol shows any candle after its `removal_date` (a resumed pair) is reported | 0 removals after `w`; resumption share reported, ≤ 1% or the removal-based features use the candle-gap definition (≥ 30 days without a candle), frozen fallback |
| P2.5 | notice-free classes: for 500 sampled removals (seed 20261105) recompute the backward `[d − 90 d, d]` same-quote asset count from scratch | 0 mismatches |
| P2.6 | no excluded column (`MARKET_FEATURE_REGISTRY.csv`, status `EXCLUDED`) is present in X | 0 |
| P2.7 | asset-era of every landmark is backward-determined (era break needs a > 365-day gap entirely before `w`) | 0 |
| P2.8 | reproducibility versus H18.3: for the 18 baseline features shared with `data/raw/h18_3/features.parquet` (read **by column whitelist only**: `asset_era_id, week` + those 18 columns), report agreement | reported; differences explained by the H20 decision-time rule |

## 3. Target (P4, sealed)

| # | check | bar |
|---|---|---|
| P4.1 | every `announcement_public_time` parses under the strict rule (`H20_2_TEMPORAL_SPLIT.json → target`) | 0 failures, else STOP |
| P4.2 | every event matches at most one asset-era | 0 multi-matches, else STOP |
| P4.3 | landmarks with announcement ≤ `t` are excluded from the risk set | 0 remaining |
| P4.4 | `t + 365 d ≤ 2026-10-09` for every landmark in DEVELOPMENT and HOLDOUT | 0 |
| P4.5 | agreement with the inherited `y_365` column (read after y is hashed) | reported only; differences must be explained by the decision-time rule |

## 4. Modelling (P5–P6)

| # | check | bar |
|---|---|---|
| P5.1 | imputation medians, winsorisation bounds and scaling statistics come from the training rows of each fit only | 0 |
| P5.2 | every fold's training landmarks satisfy `w ≤ test_from − 366 d` | 0 |
| P5.3 | identical grid, folds, seeds and preprocessing for M0, M1, M2, M1_core, M2_core | identical |
| P5.4 | the pre-holdout freeze (selected configurations, development results, code hashes) is written **before** any holdout row is scored | timestamp order verified |
| P6.1 | holdout scored once; a second scoring run is a DATA / DESIGN FAILURE | 1 run |
