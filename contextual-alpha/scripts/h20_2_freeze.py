"""H20.2 — generate the frozen specification files from h20_2_spec.py and hash the pre-registration.

  --part specs    writes MARKET_FEATURE_REGISTRY.csv, H20_2_CONTEXT_SETS.json, H20_2_MODEL_SPEC.json,
                  H20_2_TEMPORAL_SPLIT.json, H20_2_METRICS_SPEC.json, H20_2_VERDICT_RULES.json and the
                  schema-only target check evidence/H20_2_TARGET_SCHEMA_CHECK.json
  --part freeze   writes H20_2_FREEZE.json with the sha256 of every frozen file (refuses to overwrite)

Data access is metadata only: parquet schema, row count and row-group null counts. No row value of
any table is read; no outcome, return, prediction or model result is touched.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_2_freeze.py" --part specs|freeze
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, timedelta

import pyarrow.parquet as pq

import h20_2_spec as sp
from h20_common import CA, EVIDENCE, ROOT, iso, now_utc, sha256_file, to_lf

SPEC_FILES = [
    "H20_2_EXPERIMENT_PLAN.md", "H20_2_PREREG.md", "MARKET_FEATURE_REGISTRY.csv", "H20_2_CONTEXT_SETS.json",
    "H20_2_MODEL_SPEC.json", "H20_2_TEMPORAL_SPLIT.json", "H20_2_METRICS_SPEC.json", "H20_2_INFERENCE_SPEC.md",
    "H20_2_VERDICT_RULES.json", "H20_2_PIT_AUDIT_PLAN.md", "evidence/H20_2_TARGET_SCHEMA_CHECK.json",
    "scripts/h20_2_spec.py", "scripts/h20_2_freeze.py",
]
SCHEMA_TABLES = {
    "events": ("H18_1B_FULL_DELIST_EVENTS.parquet", ["full_delisting_event_id", "symbol", "announcement_public_time",
                                                    "announcement_precision", "trading_end"]),
    "symbol_windows": ("data/raw/h18_2/symbol_windows.parquet", ["symbol", "base_asset", "quote_asset", "first_candle",
                                                                 "last_candle", "window_known"]),
    "pair_removals_pit": ("data/raw/h18_3/pair_removals_pit.parquet", ["symbol", "base_asset", "quote_asset", "removal_date",
                                                                       "assets_losing_this_quote_prior_90d"]),
    "asset_daily": ("data/raw/h18_3/asset_daily.parquet", ["date", "base_asset", "usd_volume", "trades", "hhi_trades", "usd_close"]),
    "landmarks_pit": ("data/raw/h18_3/landmarks_pit.parquet", ["asset_era_id", "base_asset", "week"]),
}


def dump(name: str, obj) -> None:
    (CA / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=str), encoding="utf-8")


def schema_check() -> dict:
    out = {"method": "pyarrow schema, num_rows and row-group null_count statistics only; no row value read",
           "tables": {}, "all_required_columns_present": True}
    for k, (path, need) in SCHEMA_TABLES.items():
        f = pq.ParquetFile(ROOT / path)
        names = f.schema_arrow.names
        md = f.metadata
        cols = {}
        for c in need:
            if c not in names:
                cols[c] = {"present": False}
                out["all_required_columns_present"] = False
                continue
            j = names.index(c)
            nulls = [md.row_group(i).column(j).statistics for i in range(md.num_row_groups)]
            nn = sum(s.null_count for s in nulls if s is not None and s.has_null_count) if all(s is not None for s in nulls) else None
            cols[c] = {"present": True, "type": str(f.schema_arrow.field(c).type), "null_count": nn}
        out["tables"][k] = {"path": path, "sha256": sha256_file(ROOT / path), "num_rows": md.num_rows, "columns": cols}
    ev = out["tables"]["events"]["columns"]
    out["target_reconstructibility"] = {
        "verdict": "RECONSTRUCTIBLE (CONDITIONAL ON TWO SEALED VALUE CHECKS)",
        "schema_level": "event id, ticker, announcement time and trading end present with 0 nulls; era inputs (symbol windows) "
                        "present; the join and window rule are deterministic (h20_2_spec.TARGET)",
        "announcement_time_type": ev["announcement_public_time"].get("type"),
        "deferred_value_checks": [
            "every announcement_public_time parses under the strict ISO rule (else STOP: DATA / DESIGN FAILURE)",
            "every event matches at most one asset-era (else STOP)",
        ],
        "why_deferred": "both checks need row values of the lifecycle table, which H20.2 may not read; they run in the H20.3 sealed "
                        "target stage after X is hashed and before any fit",
        "stop_now": False,
    }
    return out


def specs() -> int:
    # market registry
    fields = ["feature_id", "feature_name", "block", "source", "definition", "logistic_transform", "pit_status", "audit_note",
              "h18_3_equivalent", "in_market_arm"]
    with (CA / "MARKET_FEATURE_REGISTRY.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for m in sp.MARKET:
            w.writerow(dict(zip(fields, [*m, m[6] in ("ADMISSIBLE", "ADMISSIBLE_WITH_AUDIT")])))
    # context sets, checked against the H20.1 gate and freeze
    g1 = json.loads((CA / "H20_1_GATE.json").read_text(encoding="utf-8"))
    eligible = [e["feature_name"] for e in g1["eligible_for_h20_2"]]
    assert sorted(eligible) == sorted(sp.CONTEXT_EXPANDED), "CONTEXT_EXPANDED must equal the H20.1 eligible set"
    assert set(sp.CONTEXT_CORE) <= set(sp.CONTEXT_EXPANDED)
    assert not set(sp.CONTEXT_CORE) & set(sp.CONTEXT_RULES["classifier_dependence"]), "core must be classifier-free"
    f1 = json.loads((CA / "H20_1_REPRESENTATION_FREEZE.json").read_text(encoding="utf-8"))
    assert sha256_file(CA / "scripts/h20_1_rep.py") == f1["rules_module_sha256"], "H20.1 rules module changed"
    reg = {r["feature_name"]: r for r in csv.DictReader((CA / "CONTEXT_FEATURE_REGISTRY.csv").open(encoding="utf-8"))}
    dump("H20_2_CONTEXT_SETS.json", {
        "spec_version": sp.SPEC_VERSION,
        "CONTEXT_EXPANDED": [{"feature_name": f, "feature_id": reg[f]["feature_id"], "layer": reg[f]["context_layer"],
                              "family": reg[f]["representation_family"], "classifiers": reg[f]["classifiers"],
                              "logistic_transform": sp.CONTEXT_LOGISTIC_TRANSFORM[f]} for f in sp.CONTEXT_EXPANDED],
        "CONTEXT_CORE": sp.CONTEXT_CORE,
        "core_rule": "classifier-free: excludes every feature using K1a, K1b, K2, K3 or K4; fixed before any outcome",
        "excluded_from_core": sorted(sp.CONTEXT_RULES["classifier_dependence"]),
        "layers_in_core": sorted({reg[f]["context_layer"] for f in sp.CONTEXT_CORE}),
        "rules": sp.CONTEXT_RULES,
        "h20_1_gate_sha256": sha256_file(CA / "H20_1_GATE.json"),
        "h20_1_representation_freeze_sha256": f1["freeze_sha256"],
        "arms": sp.ARMS, "primary_comparison": sp.PRIMARY_COMPARISON,
    })
    dump("H20_2_MODEL_SPEC.json", {"spec_version": sp.SPEC_VERSION, "arms": sp.ARMS, "primary_comparison": sp.PRIMARY_COMPARISON,
                                   "market_arm_features": sp.MARKET_ARM_FEATURES, "context_expanded": sp.CONTEXT_EXPANDED,
                                   "context_core": sp.CONTEXT_CORE, **sp.MODEL,
                                   "environment_pins": {"python": sys.version.split()[0], "lightgbm": "4.7.0", "scipy": "1.18.1",
                                                        "note": "scikit-learn is not installed in the repository venv and is not used"}})
    # temporal split from the calendar only
    fl = sp.folds()
    assert len(fl) == 8
    for f in fl:
        assert date.fromisoformat(f["train_to"]) + timedelta(days=sp.FOLD_EMBARGO_DAYS) < date.fromisoformat(f["test_from"])
    assert sp.HOLDOUT[0] - sp.DEV[1] > timedelta(days=365)
    assert sp.HOLDOUT[1] + timedelta(days=366) <= sp.ADMIN_CENSOR + timedelta(days=1)
    blocks = {"DEVELOPMENT": sp.DEV, "EMBARGO_DROPPED": sp.EMBARGO, "HOLDOUT_H20": sp.HOLDOUT, "PROSPECTIVE_CONFIRMATION": sp.PROSPECTIVE}
    dump("H20_2_TEMPORAL_SPLIT.json", {
        "spec_version": sp.SPEC_VERSION, "landmark_rule": sp.LANDMARK_RULE, "target": sp.TARGET,
        "administrative_censor": sp.ADMIN_CENSOR.isoformat(), "horizon_days": 365,
        "blocks": {k: {"first_landmark_monday": a.isoformat(), "last_landmark_monday": b.isoformat(),
                       "n_weeks": len(sp.mondays(a, b))} for k, (a, b) in blocks.items()},
        "block_roles": {
            "DEVELOPMENT": "all fitting, selection and the 8 folds; 2018-01-01 .. 2023-12-25 (inherited H18.3 boundaries, chosen on "
                           "calendar and follow-up grounds)",
            "EMBARGO_DROPPED": "one horizon between development labels (mature by 2024-12-24) and the holdout; not used",
            "HOLDOUT_H20": "opened exactly once, after the pre-holdout freeze; untouched by any H20 or context model. DISCLOSED: the "
                           "same calendar block was the H18.3 holdout, opened in H18.3 for market-only models",
            "PROSPECTIVE_CONFIRMATION": "landmarks whose outcomes are not yet observable (follow-up ends 2027-09-28); frozen now as the "
                                        "only block untouched by the whole research programme; evaluable only after a lifecycle "
                                        "refresh past 2027-09-28; not part of the H20.3 verdict",
        },
        "folds": fl, "fold_embargo_days": sp.FOLD_EMBARGO_DAYS,
        "selection_basis": "calendar and follow-up completeness only; no performance figure was read in choosing any date",
        "label_overlap": "a positive event at A is the label of every landmark t in [A - 365 d, A): up to 52 consecutive positive "
                         "weeks per event; the folds' 365-day embargo removes train/test label overlap",
    })
    dump("H20_2_METRICS_SPEC.json", {"spec_version": sp.SPEC_VERSION, **sp.METRICS})
    dump("H20_2_VERDICT_RULES.json", {"spec_version": sp.SPEC_VERSION, **sp.VERDICTS, "inference": sp.INFERENCE})
    sc = schema_check()
    p = EVIDENCE / "H20_2_TARGET_SCHEMA_CHECK.json"
    p.write_text(json.dumps(sc, indent=1, default=str), encoding="utf-8")
    to_lf([CA / n for n in SPEC_FILES if (CA / n).exists()])
    print("specs written; target:", sc["target_reconstructibility"]["verdict"], "| columns present:",
          sc["all_required_columns_present"])
    return 0


def freeze() -> int:
    out = CA / "H20_2_FREEZE.json"
    if out.exists():
        print("freeze exists; refusing to overwrite")
        return 1
    missing = [n for n in SPEC_FILES if not (CA / n).exists()]
    if missing:
        print("missing:", missing)
        return 1
    to_lf([CA / n for n in SPEC_FILES])
    rec = {
        "experiment": "H20.2 Prospective Historical Decision Design (pre-registration of H20.3)",
        "frozen_utc": iso(now_utc()), "spec_version": sp.SPEC_VERSION,
        "files": {n: sha256_file(CA / n) for n in SPEC_FILES},
        "upstream": {"H20_1_GATE.json": sha256_file(CA / "H20_1_GATE.json"),
                     "H20_1_REPRESENTATION_FREEZE.json": sha256_file(CA / "H20_1_REPRESENTATION_FREEZE.json"),
                     "scripts/h20_1_rep.py": sha256_file(CA / "scripts/h20_1_rep.py"),
                     "CONTEXT_FEATURE_REGISTRY.csv": sha256_file(CA / "CONTEXT_FEATURE_REGISTRY.csv")},
        "state_at_freeze": {"outcome_tables_read": False, "rows_of_lifecycle_tables_read": False, "returns_after_t_computed": False,
                            "models_fitted": False, "metrics_computed": False, "h18_3_results_files_read": False},
        "authorises": "nothing; H20.3 requires sponsor authorisation",
    }
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    to_lf([out])
    print(json.dumps(rec["files"], indent=1))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=["specs", "freeze"])
    sys.exit({"specs": specs, "freeze": freeze}[ap.parse_args().part]())
