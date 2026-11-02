# H20.2 — Inference Specification

Frozen before any outcome is read. Machine-readable copy: `H20_2_VERDICT_RULES.json → inference`.

## 1. Why rows are not independent

| source of dependence | consequence | handled by |
|---|---|---|
| one asset-era contributes up to ~400 weekly landmarks | rows of one asset are serially dependent | asset-era clusters |
| one delisting at time *A* is the label of every landmark in `[A − 365 d, A)` | up to 52 consecutive positive weeks per event | asset-era clusters; positive weeks never called events |
| context is **identical for all assets at the same t** | a context effect is a week-level effect; its information content is bounded by the number of distinct weeks, not rows | calendar-time blocks |
| common venue regimes (delisting waves) | cross-asset correlation within a period | calendar-time blocks |

**Effective units reported with every result:** landmark rows, unique asset-eras, unique positive
events and distinct weeks. Inherited H18.3 sample accounting (not recomputed in H20.2) gives the
scale:
- DEVELOPMENT: about 110 unique events and 522 asset-eras.
- Folds: 20–35 events each, over 13 weeks.
- HOLDOUT: about 86 events.

For context the binding unit is the week. The development test period holds **104** distinct
weeks (8 folds × 13), and the holdout **40**.

## 2. Primary interval (criterion S3)

**Pigeonhole two-way cluster bootstrap** (Owen 2007) on the pooled out-of-fold development
predictions of M0 and M2 (the same rows for both):

1. Resample the unique asset-eras with replacement → multiplicity `m_i`.
2. Independently resample the 8 fold test windows (13-week calendar blocks) with replacement →
   multiplicity `n_b`.
3. Row weight `w = m_i × n_b`. Recompute weighted PR-AUC for M2 and M0 on the same weights;
   `Δ* = PR-AUC*(M2) − PR-AUC*(M0)`.
4. 2,000 replicates, `numpy.random.default_rng(20261103)`. 95% percentile interval of `Δ*`.

The models are **not refit** inside the bootstrap. The interval describes sampling uncertainty of
the evaluation set given fixed out-of-fold predictions. The two-way scheme is conservative relative
to either one-way scheme, and both one-way intervals (asset-era only; block only) are reported
beside it. A replicate with no positive row is redrawn and the redraw count is reported.

S3 passes only if the **lower bound > 0**.

## 3. Holdout

Point estimate of Δ (criterion S4: `> 0`). A pigeonhole interval with asset-eras × calendar months
(10 blocks) is **reported for information only**. As in H18.3 amendment A3, the holdout is a
directional confirmation, not a second significance test.

## 4. Folds and eras

- Per-fold Δ for S2 (≥ 5 of 8 positive).
- Era blocks for S7: 2022 (folds 1–4), 2023 (folds 5–8), 2025 holdout.
- Leave-one-fold-out pooled Δ for S7.

## 5. What is never done

- No unclustered standard error, row-level test or significance claim from repeated landmarks.
- No interval on relative improvement alone.
- No multiple-comparison shopping. The single primary comparison is M2 vs M0 under L2 logistic.
  The secondary arms, the LightGBM class and the a-priori-default sensitivity are reported with the
  same intervals, labelled secondary, and cannot produce a verdict.
