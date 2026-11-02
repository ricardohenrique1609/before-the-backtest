# H20.3 — Execution Deviations

Departures from the frozen H20.2 specification (v1 superseded by A02) and from the H20.3 execution
plumbing. None changes a frozen rule, set, threshold or criterion, and none was decided by looking at
an outcome or a model result.

## D1 — Context collection split across parallel processes (P1, before the X seal)

The ALFRED vintage server answered at about 6.5 s per request, so the single collector would have
taken about 2 hours. Two additional processes ran the unchanged H20.1 `alfred()` routine over two
slices of the landmark calendar (2021-06 … 2023-06 and 2023-07 … 2025-10), writing only the
write-once raw cache. Their own tables went to scratch folders and are not used. A fourth process
ran the unchanged `wiki()` routine. The main collector was stopped after it finished ALFRED, so
Wikipedia was collected once. Every interim table used by the build is a single, complete parse of
the raw cache. Total load on the ALFRED host stayed below one request per second.

## D2 — The frozen route-state fallback fired (P2.3; a frozen rule, recorded for visibility)

Window-based and candle-based `n_active_spot_pairs` disagreed on 4.554% of landmarks, above the
frozen 1% bar. As pre-registered, M09–M16 and M19 were built from candle activity (a pair is active
iff it has a daily candle in `[w − 6 d, w]`) for all landmarks and every arm. The trigger is a
structural disagreement rate computed before any outcome was read. The removal-permanence trigger
(P2.4) did not fire (0.000% of removals show a later candle).

## D3 — Four ALFRED fetch failures retried (P1, before the X seal)

The first pass left 4 of 1,065 vintages not OK: UNRATE 2020-10-11 and DFF 2021-01-10 (HTTP error),
CPIAUCSL 2021-04-25 and DFF 2023-04-16 (404). The unchanged `alfred()` routine was re-run. It
re-parsed every cached vintage and requested only the missing ones, and all four were then received
(1,065 / 1,065 OK). This is a transport retry, as in H20.1 D2/D5. The missing-value rule is unchanged.

## D4 — LightGBM through its native API; exploratory stage re-run once after a crash

The first exploratory run crashed at the LightGBM step, because `lightgbm.LGBMClassifier` is a
scikit-learn wrapper and scikit-learn is not installed (as disclosed in the spec). The script now
calls `lightgbm.train` with the frozen parameters mapped one-to-one:

| spec name | native name |
|---|---|
| `min_child_samples=200` | `min_data_in_leaf` |
| `subsample=0.8` | `bagging_fraction` |
| `bagging_freq=1` | `bagging_freq` |
| `colsample_bytree=0.8` | `feature_fraction` |
| `reg_lambda=1.0` | `lambda_l2` |
| `n_estimators` | `num_boost_round` |

`learning_rate`, `num_leaves`, `max_bin`, `deterministic`, `force_row_wise`, single thread and
seed 20261104 are unchanged.

The crashed run had completed the selected-λ logistic step but wrote no file. The whole exploratory
stage was re-run once. This affects only EXPLORATORY outputs, which cannot determine the verdict.
The primary LCUV scoring ran exactly once (lock file) and is untouched.

Because of this edit, the current sha256 of `scripts/h20_3_model.py` differs from the hash recorded
in `H20_3_PRE_LCUV_FREEZE.json → code`. This was verified to be confined to the exploratory
function. Reversing the five replacements reproduces exactly the frozen hash, and every changed diff
hunk lies inside `explore()` (from line 349). `fit_l2`, `prep_fit`, `design`, `predict`, the metrics,
the bootstrap, `dev()` and `lcuv()` are byte-identical to the frozen version.

## D5 — Test scope for the outcome-opening stage

`tests/test_h20_0.py::test_no_collection_or_audit_script_reads_an_outcome_table` scans every script
for lifecycle path names. H20.3 is the authorised outcome-opening stage, so `h20_3_*` scripts are
exempted from that scan. Their isolation is tested instead by `tests/test_h20_3.py`:
- X sealed before y, and the y hash holds;
- the pre-LCUV freeze precedes a single LCUV run;
- the arms equal the frozen sets;
- the verdict recomputes from the criteria.

## Interpretation notes (no deviation)

- **S7 era blocks.** "2022 folds" and "2023 folds" are the pooled out-of-fold predictions of folds
  1–4 and 5–8 respectively, and "2025" is the LCUV block. Each block's Δ is the PR-AUC difference on
  its pooled rows.
- **Convergence** of a primary fit means `scipy.optimize.minimize(..., method="L-BFGS-B").success`.
  Every fold fit and every final fit of every arm converged at the first attempt.
