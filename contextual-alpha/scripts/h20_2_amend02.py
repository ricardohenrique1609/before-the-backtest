"""H20.2 Addendum 02 — pre-outcome methodological amendment, generated additively.

The v1 frozen files and H20_2_FREEZE.json are not modified. This script derives superseding A02
specification files from the v1 module h20_2_spec.py and freezes them in H20_2_FREEZE_A02.json, which
records the v1 freeze hash so provenance is chained. Effective specification for H20.3 = an A02 file
where one exists, otherwise the v1 file, under the A02 terminology map.

Changes (and nothing else):
  A02.1  primary L2 logistic uses ONE frozen a-priori lambda (= 10, inherited from v1's frozen
         a-priori default), identical for every arm; the lambda grid becomes secondary/exploratory
  A02.2  HOLDOUT_H20 is renamed LOCKED_CONTEXT_UNSEEN_VALIDATION; dates unchanged; claim scope bounded
  A02.3  S5 written as an explicit machine-readable numeric rule

No data file, outcome, return, prediction or model result is read.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_2_amend02.py"
"""

from __future__ import annotations

import copy
import json
import sys

import h20_2_spec as sp
from h20_common import CA, iso, now_utc, sha256_file, to_lf

A02 = "h20_2_v1+A02"
LCUV = "LOCKED_CONTEXT_UNSEEN_VALIDATION"
PRIMARY_LAMBDA = 10.0
TERMS = {
    "HOLDOUT_H20": LCUV,
    "holdout (any v1 use, incl. 'pre-holdout freeze', 'holdout scored once', '2025 holdout')":
        f"{LCUV} ('pre-LCUV freeze', 'LCUV scored once', '2025 LCUV block')",
}
CLAIM = {
    "if_supported": "incremental context signal supported in the locked retrospective / context-unseen evaluation",
    "always_append": "prospective confirmation pending (PROSPECTIVE_CONFIRMATION block, not scorable before its 365-day "
                     "outcomes mature after 2027-09-28)",
    "never_say": ["untouched holdout", "out-of-sample external confirmation", "prospective confirmation", "fully prospective"],
    "why": "no H20 or context model has seen the 2025 block and the H20.2 rules are frozen before H20 scoring, but the research "
           "programme previously observed market-model behaviour in that calendar period (H18.3 holdout)",
}
S5 = {
    "id": "S5",
    "name": "no severe calibration deterioration on the LCUV block (primary class, fixed lambda)",
    "computed_on": f"{LCUV} predictions of M0 and M2 (the same rows)",
    "definitions": {
        "brier": "mean((p - y)^2)",
        "calibration_slope": "coefficient b1 of an unpenalised logistic regression y ~ b0 + b1 * logit(p), with p clipped to "
                             "[1e-6, 1 - 1e-6], fitted by the frozen numpy/scipy routine (L-BFGS-B, gtol 1e-8, maxiter 5000)",
    },
    "rule": {
        "all_of": [
            {"quantity": "brier_ratio", "expr": "Brier(M2) / Brier(M0)", "op": "<=", "value": 1.05},
            {"quantity": "slope_excess", "expr": "abs(slope(M2) - 1) - abs(slope(M0) - 1)", "op": "<=", "value": 0.20},
        ]
    },
    "severe_deterioration": "S5 fails (severe deterioration) if either inequality is violated",
    "not_computable": "if a calibration slope does not converge or Brier(M0) == 0, S5 is NOT passed (an unmeasured criterion is "
                      "not a satisfied one)",
    "unchanged_from_v1": "the two numeric bars (1.05 and 0.20) are v1's; A02 only makes the rule machine-readable and fixes the "
                         "computation and the not-computable case",
}


def model_spec() -> dict:
    m = json.loads((CA / "H20_2_MODEL_SPEC.json").read_text(encoding="utf-8"))
    m["spec_version"] = A02
    pc = m["primary_class"]
    grid = pc.pop("hyperparameter_grid")
    pc["lambda_primary"] = PRIMARY_LAMBDA
    pc["lambda_rule"] = ("one frozen a-priori lambda = 10, identical for M0, M1, M2, M1_core, M2_core; no selection of any kind "
                         "for the primary class; the confirmatory development OOF predictions, the bootstrap interval, the "
                         "LCUV fit and every verdict criterion use lambda = 10")
    pc["lambda_provenance"] = ("inherited from the v1 frozen specification (H20_2_MODEL_SPEC.json, field sensitivity_reported: "
                               "'a-priori defaults (lambda = 10 ...)'), written and hashed in H20_2_FREEZE.json before any "
                               "outcome was read; H18.3 froze only a grid, no default, so nothing is inherited from H18")
    pc["lambda_rationale"] = ("engineering choice, disclosed as such: with the objective sum(log-loss) + 0.5*lambda*||beta||^2 on "
                              "standardised features and ~60-78k training landmarks, lambda = 10 is weak shrinkage that keeps "
                              "near-collinear and rare columns (missing indicators, flags, the calendar trend) estimable without "
                              "materially biasing well-identified coefficients; it corresponds to C = 0.1 in the "
                              "scikit-learn parameterisation. It was not chosen by reading any outcome or any H18 or H20 result")
    pc["exploratory_lambda_grid"] = {**grid, "role": "SECONDARY / EXPLORATORY only: per-arm selection by mean fold PR-AUC is "
                                     "reported, labelled exploratory, and cannot determine or modify the verdict"}
    sc = m["secondary_class"]
    sc["role"] = "SECONDARY / EXPLORATORY: reported at its a-priori default (num_leaves 7, 200 trees) and at the configuration "\
                 "selected on the folds; neither can determine the verdict"
    m["selection"] = ("primary class: none (lambda fixed). Secondary / exploratory only: for each arm and class, the configuration "
                      "with the highest mean PR-AUC over the 8 development folds; ties broken by the stronger regularisation")
    m["final_fit"] = (f"primary: lambda = 10 refit on all DEVELOPMENT landmarks; the {LCUV} block is scored once with that fit. "
                      "Exploratory configurations are refit and scored only after the primary LCUV scores are written and hashed")
    m.pop("sensitivity_reported", None)
    m["equal_budget_rule"] = ("every arm gets the same fixed primary lambda, the same exploratory grids (5 lambdas; 4 tree configs), "
                              "the same folds, preprocessing rules and seeds; no arm may receive an extra search, feature "
                              "selection or early stopping")
    m["amendment"] = "A02.1"
    return m


def temporal_split() -> dict:
    t = json.loads((CA / "H20_2_TEMPORAL_SPLIT.json").read_text(encoding="utf-8"))
    t["spec_version"] = A02
    t["blocks"][LCUV] = t["blocks"].pop("HOLDOUT_H20")
    t["block_roles"].pop("HOLDOUT_H20")
    t["block_roles"][LCUV] = ("2025-01-06 .. 2025-10-06 (dates unchanged). Locked: opened exactly once, after the pre-LCUV freeze; "
                              "no H20 or context model has seen it and every H20.2 rule is frozen before H20 scoring. NOT an "
                              "untouched holdout: the research programme observed market-only model behaviour in this calendar "
                              "period (H18.3 holdout)")
    t["block_roles"]["PROSPECTIVE_CONFIRMATION"] += ("; the only programme-untouched block. The H20.3 primary models are hashed so "
                                                     "it can be scored unchanged once its outcomes mature; its scoring rule is to "
                                                     "be frozen before then")
    t["claim_scope"] = CLAIM
    t["terminology_map"] = TERMS
    t["amendment"] = "A02.2 (terminology and claim scope only; no date changed)"
    return t


def metrics_spec() -> dict:
    m = json.loads((CA / "H20_2_METRICS_SPEC.json").read_text(encoding="utf-8"))
    m["spec_version"] = A02
    m["primary"]["primary_quantity"] = ("Delta PR-AUC = PR-AUC(M2) - PR-AUC(M0), primary class at lambda = 10, on the pooled "
                                        f"out-of-fold development predictions (8 folds) and, separately, on the {LCUV} block")
    m["secondary"]["PER_ERA"] = f"Delta PR-AUC for 2022 folds (1-4), 2023 folds (5-8) and the 2025 {LCUV} block"
    m["amendment"] = "A02.1 / A02.2 (fixed lambda; terminology); metric definitions unchanged"
    return m


def verdict_rules() -> dict:
    v = json.loads((CA / "H20_2_VERDICT_RULES.json").read_text(encoding="utf-8"))
    v["spec_version"] = A02
    v["evaluated_on"] = "primary comparison only (M2 vs M0, L2 logistic at the fixed lambda = 10); exploratory configurations never"
    c = v["conditions_for_support"]
    c["S1"] = "development pooled-OOF Delta PR-AUC > 0 (lambda = 10)"
    c["S3"] = ("two-way cluster (pigeonhole) bootstrap 95% percentile CI for the development pooled-OOF Delta (lambda = 10) has "
               "lower bound > 0")
    c["S4"] = f"{LCUV} Delta PR-AUC > 0 (directional confirmation; its CI is reported, not required)"
    c["S5"] = S5
    c["S7"] = (f"not driven by one era: Delta > 0 in at least 2 of the 3 era blocks {{2022 folds, 2023 folds, 2025 {LCUV}}} AND "
               "the development pooled-OOF Delta stays > 0 when each fold is left out in turn")
    v["rules_in_order"] = [
        "DATA / DESIGN FAILURE if: S6 fails; or the sealed target checks fail (unparsable announcement time, an event matching > 1 "
        f"era); or any development fold has < 5 unique positive events or the {LCUV} block has < 20; or > 20% of landmark weeks "
        f"lack every context source; or a model fails to converge twice; or the {LCUV} block has to be opened more than once",
        "INCREMENTAL CONTEXT SIGNAL SUPPORTED if S1-S7 all hold",
        f"NEGATIVE INCREMENTAL RESULT if the development bootstrap CI upper bound < 0 AND {LCUV} Delta < 0",
        f"PRE-REGISTERED NULL otherwise (including any CI straddling zero, any fold-majority failure, any {LCUV} veto)",
    ]
    v["annotations_not_verdicts"]["materiality"] = (f"MATERIAL if absolute Delta >= 0.01 AND relative Delta >= 10% on both "
                                                    f"development and {LCUV}, else SMALL (never converts one verdict into another)")
    v["annotations_not_verdicts"]["exploratory_tuning"] = ("selected-lambda and selected-tree results are reported as exploratory; "
                                                          "they never determine, upgrade or downgrade the verdict")
    v["claim_scope"] = CLAIM
    v["inference"]["blocks"] = {"development": "the 8 fold test windows (13 weeks each)", LCUV: "calendar months (10)"}
    v["inference"]["predictions"] = "primary class at lambda = 10 (no selection inside or outside the bootstrap)"
    v["terminology_map"] = TERMS
    v["amendment"] = "A02.1 / A02.2 / A02.3"
    return v


FILES = {"H20_2_MODEL_SPEC_A02.json": model_spec, "H20_2_TEMPORAL_SPLIT_A02.json": temporal_split,
         "H20_2_METRICS_SPEC_A02.json": metrics_spec, "H20_2_VERDICT_RULES_A02.json": verdict_rules}
FROZEN_DOCS = ["H20_2_PREREG_ADDENDUM_02.md", "H20_2_INFERENCE_SPEC_A02.md", "scripts/h20_2_amend02.py"]


def main() -> int:
    out = CA / "H20_2_FREEZE_A02.json"
    if out.exists():
        print("A02 freeze exists; refusing to overwrite")
        return 1
    v1 = json.loads((CA / "H20_2_FREEZE.json").read_text(encoding="utf-8"))
    for name, h in v1["files"].items():  # the v1 freeze must still hold exactly
        assert sha256_file(CA / name) == h, f"v1 file changed: {name}"
    for name, fn in FILES.items():
        (CA / name).write_text(json.dumps(copy.deepcopy(fn()), indent=1, ensure_ascii=False), encoding="utf-8")
    missing = [d for d in FROZEN_DOCS if not (CA / d).exists()]
    if missing:
        print("missing:", missing)
        return 1
    names = list(FILES) + FROZEN_DOCS
    to_lf([CA / n for n in names])
    rec = {
        "experiment": "H20.2 Addendum 02 (pre-outcome methodological amendment)",
        "frozen_utc": iso(now_utc()), "spec_version": A02,
        "supersedes": {"H20_2_MODEL_SPEC.json": "H20_2_MODEL_SPEC_A02.json",
                       "H20_2_TEMPORAL_SPLIT.json": "H20_2_TEMPORAL_SPLIT_A02.json",
                       "H20_2_METRICS_SPEC.json": "H20_2_METRICS_SPEC_A02.json",
                       "H20_2_VERDICT_RULES.json": "H20_2_VERDICT_RULES_A02.json",
                       "H20_2_INFERENCE_SPEC.md": "H20_2_INFERENCE_SPEC_A02.md",
                       "H20_2_PREREG.md (sections 4-6, 8)": "H20_2_PREREG_ADDENDUM_02.md"},
        "terminology_map": TERMS,
        "files": {n: sha256_file(CA / n) for n in names},
        "v1_freeze": {"file": "H20_2_FREEZE.json", "sha256": sha256_file(CA / "H20_2_FREEZE.json"),
                      "files_verified_unchanged": len(v1["files"])},
        "addendum_01": {"file": "H20_2_PREREG_ADDENDUM_01.md", "sha256": sha256_file(CA / "H20_2_PREREG_ADDENDUM_01.md")},
        "unchanged": ["target", "context features and sets", "market features", "temporal dates", "PIT rules and audit plan",
                      "outcome definition", "primary metric", "C4/C5 exclusions", "H20.1 representations"],
        "state_at_freeze": {"outcome_tables_read": False, "rows_of_lifecycle_tables_read": False, "returns_after_t_computed": False,
                            "models_fitted": False, "metrics_computed": False, "h18_3_results_files_read": False},
        "authorises": "nothing; H20.3 requires sponsor authorisation",
    }
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    to_lf([out])
    print(json.dumps(rec["files"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
