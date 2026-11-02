"""H20.1 gate (plan sections 13-14): feature eligibility and per-family verdicts. No outcome is read.

Reads H20_1_REPRESENTATION_METRICS.json, evidence/H20_1_FEATURE_AUDIT.csv,
evidence/H20_1_SEMANTIC_AUDIT_SCORES.csv, H20_1_TRANSFORM_PIT_AUDIT.csv and the registry. Writes
H20_1_GATE.json and evidence/H20_1_FEATURE_ELIGIBILITY.csv. Bars are the frozen ones in
H20_1_REPRESENTATION_FREEZE.json; nothing here is tuned.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_1_gate.py"
"""

from __future__ import annotations

import json

import pandas as pd

from h20_common import CA, EVIDENCE, iso, now_utc, to_lf

FREEZE = json.loads((CA / "H20_1_REPRESENTATION_FREEZE.json").read_text(encoding="utf-8"))
BARS = FREEZE["gate_bars"]
CONDITION = {"C1": "temporal/archive bias", "C2": "US-only; temporal/archive bias",
             "C3": "metadata only; GDELT language and archive bias"}


def main() -> int:
    M = json.loads((CA / "H20_1_REPRESENTATION_METRICS.json").read_text(encoding="utf-8"))
    REG = pd.read_csv(CA / "CONTEXT_FEATURE_REGISTRY.csv")
    FA = pd.read_csv(EVIDENCE / "H20_1_FEATURE_AUDIT.csv").set_index("feature_id")
    TA = pd.read_csv(CA / "H20_1_TRANSFORM_PIT_AUDIT.csv")
    sp = EVIDENCE / "H20_1_SEMANTIC_AUDIT_SCORES.csv"
    SEM = pd.read_csv(sp).set_index("classifier") if sp.exists() else None

    det = bool(M["A_determinism"]["identical"])
    viol = M["B_pit_integrity"]["violations_by_feature"]
    pit_global = M["B_pit_integrity"]["total_violations"]
    prov_bad = M["provenance_completeness"]["incomplete_by_feature"]
    enc = M["E_zero_vs_missing"]["encoding_checks"]
    enc_ok = all(v == 0 for v in enc.values())
    classified = M["C_transform_pit"]["classified"] == M["C_transform_pit"]["items"]
    red_pairs = M["H_redundancy"]["redundant_pairs_rule"]

    rows, eligible = [], []
    for r in REG.itertuples():
        f = r.feature_id
        a = FA.loc[f]
        fails = []
        if r.pit_transform_safe != "PIT_SAFE":
            fails.append(f"transform {r.pit_transform_safe}")
        if int(viol.get(f, 0)) > 0:
            fails.append(f"PIT violations {viol[f]}")
        if not det:
            fails.append("non-deterministic build")
        if int(prov_bad.get(f, 0)) > 0:
            fails.append(f"provenance incomplete ({prov_bad[f]})")
        if not enc_ok:
            fails.append("missing/zero encoding")
        if not (a["nonmissing_share"] >= BARS["coverage_nonmissing_share"] and a["years_with_value"] >= 8):
            fails.append(f"coverage {a['nonmissing_share']:.3f}, {int(a['years_with_value'])} years")
        kls = [k for k in str(r.classifiers).split(";") if k and k != "nan"]
        for k in kls:
            if SEM is None or k not in SEM.index:
                fails.append(f"semantic audit {k} not measured")
            elif not bool(SEM.loc[k, "meets_bar"]):
                fails.append(f"semantic defect {k}")
        nz = a["nonzero_share_of_nonmissing"]
        sparse = (r.representation_family in ("R1", "R2") and pd.notna(nz) and nz < BARS["sparse_nonzero_share_min"]) or a["distinct_values"] <= 1
        if sparse:
            fails.append(f"SPARSE_DEGENERATE (nonzero share {nz})")
        redundant_with = None
        if not fails:
            for p in red_pairs:
                if p["feature_b"] == f and p["feature_a"] in eligible:
                    redundant_with = p["feature_a"]
                    fails.append(f"REDUNDANT with {p['feature_a']} (rho {p['spearman']})")
                    break
        ok = not fails
        if ok:
            eligible.append(f)
        constraints = [f"H20.0 CONDITIONAL ({r.context_layer}): {CONDITION[r.context_layer]}"]
        if bool(a["DRIFT"]):
            why = "publisher category set changed" if bool(a["category_set_changed"]) else f"denominator era ratio {a['denominator_era_ratio']}"
            constraints.append(f"DRIFT: era-stratified evaluation only ({why})")
        rows.append({"feature_id": f, "feature_name": r.feature_name, "layer": r.context_layer,
                     "family": r.representation_family, "eligible_h20_2": ok, "failed_criteria": "; ".join(fails),
                     "redundant_with": redundant_with or "", "constraints": "; ".join(constraints) if ok else ""})
    E = pd.DataFrame(rows)
    E.to_csv(EVIDENCE / "H20_1_FEATURE_ELIGIBILITY.csv", index=False, lineterminator="\n")

    fam = {}
    for fm in ("R1", "R2", "R3", "R4"):
        d = E[E["family"] == fm]
        fam_viol = int(sum(int(viol.get(f, 0)) for f in d["feature_id"]))
        fam_prov = int(sum(int(prov_bad.get(f, 0)) for f in d["feature_id"]))
        built_non_pit = TA[(TA["family"] == fm) & (TA["item_type"] == "FEATURE") & (TA["class"] != "PIT_SAFE")]
        family_ok = (fam_viol == 0 and classified and det and fam_prov == 0 and enc_ok and len(built_non_pit) == 0)
        n_el = int(d["eligible_h20_2"].sum())
        if not len(d):
            verdict = "DATA-GATE FAIL / UNTESTED"
        elif fam_viol > 0 or not family_ok:
            verdict = "DATA-GATE FAIL / UNTESTED"
        elif n_el == len(d):
            verdict = "PASS"
        elif n_el >= 1:
            verdict = "PARTIAL PASS"
        else:
            verdict = "DATA-GATE FAIL / UNTESTED"
        note = ""
        if fm == "R3":
            note = ("only the publisher-computed GDELT V2Tone (F22) was built; LLM, current embeddings and full-corpus "
                    "TF-IDF are NON_PIT; pre-2018 corpora/embeddings and expanding-window fits are UNRESOLVED and not built")
        fam[fm] = {"verdict": verdict, "features_built": d["feature_id"].tolist(), "eligible": d.loc[d["eligible_h20_2"], "feature_id"].tolist(),
                   "ineligible": {x.feature_id: x.failed_criteria for x in d[~d["eligible_h20_2"]].itertuples()},
                   "family_criteria": {"pit_violations": fam_viol, "transform_classification_complete": classified,
                                       "deterministic": det, "provenance_incomplete_values": fam_prov,
                                       "missing_zero_distinguishable": enc_ok, "built_features_non_pit": built_non_pit["item_id"].tolist()},
                   "note": note}
    layers = {}
    for ly in ("C1", "C2", "C3"):
        d = E[E["layer"] == ly]
        layers[ly] = {"eligible": d.loc[d["eligible_h20_2"], "feature_name"].tolist(), "n_built": int(len(d)),
                      "n_eligible": int(d["eligible_h20_2"].sum()), "inherited_condition": CONDITION[ly],
                      "status": "REPRESENTABLE (CONDITIONAL)" if d["eligible_h20_2"].any() else "NOT REPRESENTABLE"}
    verdicts = [v["verdict"] for v in fam.values()]
    overall = ("PASS" if all(v == "PASS" for v in verdicts) else
               "PARTIAL PASS" if any(v in ("PASS", "PARTIAL PASS") for v in verdicts) else "DATA-GATE FAIL / UNTESTED")
    gate = {
        "experiment": "H20.1 Context Representation Feasibility", "computed_utc": iso(now_utc()),
        "representation_freeze_sha256": FREEZE["freeze_sha256"], "verdict": overall,
        "verdict_scope": "representation substrate only; no outcome, no prediction, never an economic REJECT",
        "families": fam, "layers": layers,
        "eligible_for_h20_2": E.loc[E["eligible_h20_2"], ["feature_id", "feature_name", "family", "layer", "constraints"]].to_dict("records"),
        "global_checks": {"deterministic": det, "pit_total_violations": pit_global, "transform_classification_complete": classified,
                          "missing_zero_encoding": enc, "provenance_completeness": M["provenance_completeness"]["completeness"]},
        "out_of_scope": {"C4": "DATA-GATE FAIL / UNTESTED (H20.0); not used", "C5": "DATA-GATE FAIL / UNTESTED (H20.0); not used"},
        "outcome_tables_read": False, "returns_computed": False, "models_fitted": False,
    }
    p = CA / "H20_1_GATE.json"
    p.write_text(json.dumps(gate, indent=1, default=str), encoding="utf-8")
    to_lf([p, EVIDENCE / "H20_1_FEATURE_ELIGIBILITY.csv"])
    print(overall, {k: v["verdict"] for k, v in fam.items()})
    print(E[["feature_id", "feature_name", "eligible_h20_2", "failed_criteria"]].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
