# H20.2 — Pre-Registration Addendum 02 (pre-outcome methodological amendment)

**Written 2026-10-19, before any outcome was opened.** No `y` has been loaded, no model fitted, no
metric computed. The v1 pre-registration (`H20_2_PREREG.md`), its specification files and
`H20_2_FREEZE.json` are **not modified**; their hashes stand. This addendum and its superseding
files are hashed in `H20_2_FREEZE_A02.json`, which records the v1 freeze hash and re-verifies every
v1 file.

**Effective H20.3 specification:** where an A02 file exists, it supersedes its v1 counterpart. All
other v1 files apply unchanged, read through the terminology map in §2.

| v1 | superseded by |
|---|---|
| `H20_2_MODEL_SPEC.json` | `H20_2_MODEL_SPEC_A02.json` |
| `H20_2_TEMPORAL_SPLIT.json` | `H20_2_TEMPORAL_SPLIT_A02.json` (terminology and claim scope; dates identical) |
| `H20_2_METRICS_SPEC.json` | `H20_2_METRICS_SPEC_A02.json` (fixed λ; terminology; definitions identical) |
| `H20_2_VERDICT_RULES.json` | `H20_2_VERDICT_RULES_A02.json` |
| `H20_2_INFERENCE_SPEC.md` | `H20_2_INFERENCE_SPEC_A02.md` |
| `H20_2_PREREG.md` §4, §5, §6, §8.1, §8.4 | this addendum |

---

## A02.1 — The primary logistic model uses one frozen a-priori λ

**Defect fixed.** In v1, λ for the primary L2 logistic was selected per arm by mean PR-AUC on the
same 8 outer folds whose out-of-fold predictions then produce the confirmatory ΔPR-AUC (S1, S2, S7)
and its bootstrap interval (S3). Selection and confirmation would share data.

**Rule.**
- The primary class uses **λ = 10**, identical for M0, M1, M2, M1_core and M2_core.
- There is no selection of any kind for the primary class.
- The development OOF predictions, the bootstrap, the final development refit, the LCUV scores and
  every verdict criterion use λ = 10.

**Provenance.** λ = 10 is the a-priori default already frozen in v1
(`H20_2_MODEL_SPEC.json → sensitivity_reported: "a-priori defaults (lambda = 10 …)"`). It was
written and hashed before any outcome was read. H18.3 froze only a grid (`scripts/h18_3_fit.py →
LAMBDA_GRID`), not a default, so nothing is inherited from H18.

**Rationale (engineering choice, disclosed).** The objective is Σ log-loss + ½ λ ‖β‖² on
standardised features, with about 60–78 k training landmarks. At that scale λ = 10 is weak
shrinkage. It keeps near-collinear and rare columns estimable (missing indicators, flags, the
calendar trend) without materially biasing well-identified coefficients; it equals C = 0.1 in
scikit-learn's parameterisation. It was not chosen by reading any outcome or any H18 or H20 result.

**The grid {0.1, 1, 10, 100, 1000} and the LightGBM configurations become SECONDARY / EXPLORATORY.**
- Per-arm selection on the folds is still run and reported, labelled exploratory.
- It can never determine, upgrade or downgrade the verdict.
- Exploratory configurations are scored on the LCUV block only after the primary LCUV scores are
  written and hashed.

## A02.2 — The 2025 block is the LOCKED_CONTEXT_UNSEEN_VALIDATION block

`HOLDOUT_H20` is renamed **`LOCKED_CONTEXT_UNSEEN_VALIDATION`** (LCUV). Its dates are unchanged
(2025-01-06 … 2025-10-06), and it is still opened exactly once, after the pre-LCUV freeze.

- No H20 or context model has seen it.
- Every H20.2 rule is frozen before H20 scoring.
- **It is not an untouched holdout.** The research programme observed market-only model behaviour in
  this calendar period (it was the H18.3 holdout).

**PROSPECTIVE_CONFIRMATION** (landmarks 2025-10-13 … 2026-09-28) remains the only
programme-untouched block. It cannot be scored until its 365-day outcomes mature after 2027-09-28.
The H20.3 primary models are hashed so it can be scored unchanged then; its scoring rule is to be
frozen before that.

**Claim scope (binding).** If S1–S7 pass, the strongest allowed statement is:

> *incremental context signal supported in the locked retrospective / context-unseen evaluation*,
> with **prospective confirmation pending**.

The terms "untouched holdout", "out-of-sample external confirmation" and "(fully) prospective
confirmation" may not be used for the LCUV result.

**Terminology map.** Every use of "holdout" in the v1 files, including "pre-holdout freeze",
"holdout scored once" and "2025 holdout", means the LCUV block. This covers
`H20_2_PIT_AUDIT_PLAN.md` P4.4, P5.4 and P6.1 and `H20_2_EXPERIMENT_PLAN.md`; their rules are
unchanged.

## A02.3 — S5 as an explicit numeric rule

v1 stated S5 numerically but only as prose. A02 freezes it machine-readably
(`H20_2_VERDICT_RULES_A02.json → conditions_for_support.S5`), computed on the LCUV predictions of
M0 and M2 at λ = 10:

| quantity | expression | pass if |
|---|---|---|
| Brier ratio | Brier(M2) / Brier(M0) | ≤ **1.05** |
| slope excess | \|slope(M2) − 1\| − \|slope(M0) − 1\| | ≤ **0.20** |

- **Brier:** mean (p − y)².
- **Slope:** b1 of an unpenalised logistic regression y ~ b0 + b1·logit(p), with p clipped to
  [1e-6, 1 − 1e-6], fitted with the frozen numpy/scipy routine.
- Severe deterioration (S5 fails) means either inequality is violated.
- If a slope does not converge, or Brier(M0) = 0, S5 is **not passed**.
- The bars 1.05 and 0.20 are v1's. Only the formalisation and the not-computable case are new.

## Not changed

The target, context features and sets, market features, temporal dates, PIT rules and audit plan,
outcome definition, primary metric (ΔPR-AUC), verdict list, C4/C5 exclusions and H20.1
representations are all unchanged. The amendment generator verifies every v1 file against
`H20_2_FREEZE.json` before writing.
