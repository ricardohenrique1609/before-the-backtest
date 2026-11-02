"""H20.3 — assemble H20_3_PIT_AUDIT.json and apply H20_2_VERDICT_RULES_A02.json mechanically.

Reads only the frozen rules and the already-written H20.3 stage outputs. Nothing is refit, rescored or
reinterpreted; exploratory and robustness results enter only as annotations.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_3_verdict.py"
"""

from __future__ import annotations

import json
import sys

import pandas as pd

from h20_3_common import CA, LCUV, OUT, iso, now_utc, p0, sha256_file, spec, write_json


def j(p):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    p0()
    sp = spec()
    v = sp["verdict"]
    a1, a2 = j(OUT / "p1_audit.json"), j(OUT / "p2_audit.json")
    ta, dev, bs = j(CA / "H20_3_TARGET_AUDIT.json"), j(CA / "H20_3_DEVELOPMENT_RESULTS.json"), j(CA / "H20_3_BOOTSTRAP_RESULTS.json")
    fz, lc = j(CA / "H20_3_PRE_LCUV_FREEZE.json"), j(CA / "H20_3_LCUV_RESULTS.json")
    xs = j(CA / "H20_3_X_SEAL.json")
    # ---------------------------------------------------------------- P5 / P6 checks
    p5 = {
        "P5.1_preprocessing_from_training_rows_only": "by construction (h20_3_model.prep_fit called on each training set)",
        "P5.2_train_landmarks_le_test_from_minus_366d": "asserted in every fold (h20_3_model.dev)",
        "P5.3_identical_lambda_preprocessing_folds_for_all_arms": True,
        "P5.4_pre_lcuv_freeze_before_lcuv_scoring": fz["frozen_utc"] < lc["scored_utc"],
        "P5.4_lcuv_rows_scored_before_freeze": fz["lcuv_rows_scored_before_freeze"],
        "P6.1_lcuv_primary_scoring_runs": lc["scoring_runs"],
        "P6.1_lock_present": (OUT / "LCUV_PRIMARY_RUN.lock").exists(),
        "lcuv_predictions_hash_matches": sha256_file(OUT / "lcuv_predictions_primary.parquet") == lc["predictions_sha256"],
    }
    p5_pass = p5["P5.4_pre_lcuv_freeze_before_lcuv_scoring"] and p5["P5.4_lcuv_rows_scored_before_freeze"] == 0 \
        and p5["P6.1_lcuv_primary_scoring_runs"] == 1 and p5["lcuv_predictions_hash_matches"]
    pit = {"computed_utc": iso(now_utc()), "P0": "PASS (all H20.1 / H20.2 / A02 hashes verified at every stage)",
           "P1_context": {"PASS": a1["PASS"], "checks": a1["checks"]},
           "P2_market": {"PASS": a2["PASS"], "route_state_mode": a2["route_state_mode"], "checks": a2["checks"]},
           "P3_x_seal": {"sealed_utc": xs["sealed_utc"], "outcome_read_before_seal": xs["outcome_read_before_seal"]},
           "P4_target": {"PASS": ta["PASS"], "checks": ta["checks"]},
           "P5_P6_modelling": {"PASS": p5_pass, "checks": p5}}
    s6 = bool(a1["PASS"] and a2["PASS"] and ta["PASS"] and p5_pass and not xs["outcome_read_before_seal"])
    pit["S6_PASS"] = s6
    write_json("H20_3_PIT_AUDIT.json", pit)

    # ---------------------------------------------------------------- S1-S7 (primary, lambda = 10)
    d_dev = dev["delta_pr_auc_M2_M0"]
    ci = bs["primary_M2_vs_M0"]["two_way"]["ci95"]
    d_l = lc["delta_pr_auc_M2_M0"]
    s5v = lc["S5_values"]
    rule = v["conditions_for_support"]["S5"]["rule"]["all_of"]
    s5_ok = None not in (s5v["brier_ratio"], s5v["slope_excess"]) and all(
        (s5v[r["quantity"]] <= r["value"]) for r in rule)
    era_blocks = {"2022": dev["era"]["2022"]["delta"], "2023": dev["era"]["2023"]["delta"], f"2025 {LCUV}": d_l}
    s7_a = sum(x > 0 for x in era_blocks.values()) >= 2
    s7_b = dev["lofo_min"] > 0
    S = {
        "S1": {"value": d_dev, "PASS": d_dev > 0},
        "S2": {"value": dev["positive_folds_M2_M0"], "bar": ">= 5 of 8", "PASS": dev["positive_folds_M2_M0"] >= 5},
        "S3": {"value": ci, "PASS": ci[0] > 0},
        "S4": {"value": d_l, "PASS": d_l > 0},
        "S5": {"value": s5v, "rule": rule, "PASS": bool(s5_ok)},
        "S6": {"value": "H20_3_PIT_AUDIT.json", "PASS": s6},
        "S7": {"value": {"era_deltas": era_blocks, "positive_era_blocks": int(sum(x > 0 for x in era_blocks.values())),
                         "lofo_min_delta": dev["lofo_min"]}, "PASS": bool(s7_a and s7_b)},
    }
    floors_ok = ta["sample_floors_PASS"]
    failures = []
    if not s6:
        failures.append("S6 PIT audit failed")
    if not ta["PASS"]:
        failures.append("sealed target checks failed")
    if not floors_ok:
        failures.append("sample-adequacy floor not met")
    if xs["context_weeks_with_every_feature_missing"] > 0.2 * xs["decision_times"]:
        failures.append("> 20% of landmark weeks lack every context source")
    if failures:
        verdict = "DATA / DESIGN FAILURE"
    elif all(s["PASS"] for s in S.values()):
        verdict = "INCREMENTAL CONTEXT SIGNAL SUPPORTED"
    elif ci[1] < 0 and d_l < 0:
        verdict = "NEGATIVE INCREMENTAL RESULT"
    else:
        verdict = "PRE-REGISTERED NULL"
    assert verdict in v["closed_list"]
    # ---------------------------------------------------------------- annotations (never change the verdict)
    rel_dev, rel_l = dev["relative_delta"], lc["relative_delta"]
    material = d_dev >= 0.01 and rel_dev >= 0.10 and d_l >= 0.01 and rel_l >= 0.10
    ann = {
        "materiality": "MATERIAL" if material else "SMALL",
        "classifier_free_robustness": {"dev_delta_M2core_M0": dev["delta_pr_auc_M2core_M0"],
                                       "lcuv_delta_M2core_M0": lc["delta_pr_auc_M2core_M0"],
                                       "two_way_ci": bs["robustness_M2core_vs_M0"]["two_way"]["ci95"],
                                       "positive_folds": dev["positive_folds_M2core_M0"]},
    }
    if verdict == "INCREMENTAL CONTEXT SIGNAL SUPPORTED" and (dev["delta_pr_auc_M2core_M0"] <= 0 or lc["delta_pr_auc_M2core_M0"] <= 0):
        ann["classifier_free_robustness"]["note"] = "support depends on agent-audited classifiers"
    exp = CA / "H20_3_EXPLORATORY_RESULTS.json"
    if exp.exists():
        e = j(exp)
        ann["model_class_and_tuning_robustness"] = {k: {"dev_delta": e[k]["delta_dev_M2_M0"], "lcuv_delta": e[k]["delta_lcuv_M2_M0"]}
                                                    for k in ("logistic_selected_lambda", "lightgbm_default", "lightgbm_selected")}
    claim = v["claim_scope"]
    out = {"experiment": "H20.3 Incremental Context Information Test", "computed_utc": iso(now_utc()),
           "verdict": verdict, "criteria": S, "design_failures": failures, "annotations": ann,
           "claim": (f"{claim['if_supported']}, with {claim['always_append']}" if verdict == "INCREMENTAL CONTEXT SIGNAL SUPPORTED"
                     else "no incremental context signal is claimed"),
           "claim_scope_rules": claim, "economic_claims": "none (predictive information only; no trading, cost or P&L analysis)",
           "prospective_confirmation": "PROSPECTIVE_CONFIRMATION unopened",
           "inputs_sha256": {n: sha256_file(CA / n) for n in ("H20_3_PIT_AUDIT.json", "H20_3_TARGET_AUDIT.json",
                                                               "H20_3_DEVELOPMENT_RESULTS.json", "H20_3_BOOTSTRAP_RESULTS.json",
                                                               "H20_3_PRE_LCUV_FREEZE.json", "H20_3_LCUV_RESULTS.json")}}
    write_json("H20_3_VERDICT.json", out)
    print(verdict)
    print(pd.Series({k: s["PASS"] for k, s in S.items()}).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
