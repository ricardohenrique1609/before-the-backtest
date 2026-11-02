# H20.2 — Inference Specification (A02; supersedes `H20_2_INFERENCE_SPEC.md`)

Frozen before any outcome is read. Changes from v1:
- the primary predictions come from the **fixed λ = 10** primary model (A02.1);
- the 2025 block is the **LOCKED_CONTEXT_UNSEEN_VALIDATION (LCUV)** block (A02.2).

Everything else is unchanged. Machine-readable copy: `H20_2_VERDICT_RULES_A02.json → inference`.

## 1. Why rows are not independent

| source of dependence | consequence | handled by |
|---|---|---|
| one asset-era contributes many weekly landmarks | rows of one asset are serially dependent | asset-era clusters |
| one delisting at time *A* is the label of every landmark in `[A − 365 d, A)` | up to 52 consecutive positive weeks per event | asset-era clusters; positive weeks never called events |
| context is **identical for all assets at the same t** | a context effect is a week-level effect; its information is bounded by the number of distinct weeks | calendar-time blocks |
| common venue regimes (delisting waves) | cross-asset correlation within a period | calendar-time blocks |

**Effective units reported with every result:** landmark rows, unique asset-eras, unique positive
events and distinct weeks. Inherited H18.3 sample accounting (not recomputed) gives the scale:
- development: about 110 unique events and 522 asset-eras;
- folds: 20–35 events each, over 13 weeks;
- LCUV block: about 86 events.

The binding unit for context is the week. The development test period holds **104** weeks, and
the LCUV block **40**.

## 2. Primary interval (criterion S3)

**Pigeonhole two-way cluster bootstrap** (Owen 2007) on the pooled out-of-fold development
predictions of M0 and M2 from the **λ = 10** primary model (the same rows for both). No
hyperparameter is selected anywhere in this path.

1. Resample the unique asset-eras with replacement → multiplicity `m_i`.
2. Independently resample the 8 fold test windows (13-week calendar blocks) with replacement →
   multiplicity `n_b`.
3. Row weight `w = m_i × n_b`. Recompute weighted PR-AUC for M2 and M0 on the same weights;
   `Δ* = PR-AUC*(M2) − PR-AUC*(M0)`.
4. 2,000 replicates, `numpy.random.default_rng(20261103)`. 95% percentile interval of `Δ*`.

The models are not refit inside the bootstrap. Both one-way intervals (asset-era only; block only)
are reported beside the two-way interval. A replicate with no positive row is redrawn and the
redraw count is reported.

S3 passes only if the **lower bound > 0**.

## 3. LCUV block

Point estimate of Δ at λ = 10 (S4: `> 0`). A pigeonhole interval with asset-eras × calendar months
(10 blocks) is **reported for information only**. The LCUV block is directional confirmation in a
locked, context-unseen retrospective period. It is not an untouched holdout and not prospective
confirmation (A02.2 claim scope).

## 4. Folds and eras

- Per-fold Δ at λ = 10 for S2 (≥ 5 of 8 positive).
- Era blocks for S7: 2022 (folds 1–4), 2023 (folds 5–8), 2025 LCUV.
- Leave-one-fold-out pooled Δ for S7.

## 5. Exploratory

The selected-λ logistic and both LightGBM variants (a-priori default and fold-selected) are
reported with the same intervals and labelled **exploratory**. Their intervals for fold-selected
configurations carry the selection optimism v1 had, and are never used for a verdict.

## 6. What is never done

- No unclustered standard error, row-level test or significance from repeated landmarks.
- No interval on relative improvement alone.
- No substitution of an exploratory configuration for the primary.
- No multiple-comparison shopping.
