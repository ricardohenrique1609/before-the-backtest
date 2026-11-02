"""H20.2 structural tests: freeze integrity, frozen sets, calendar, outcome isolation of the design scripts.

    .venv/Scripts/python -m pytest "Contextual Alpha/tests" -q
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

CA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CA / "scripts"))

import h20_2_spec as sp  # noqa: E402

FREEZE = CA / "H20_2_FREEZE.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.mark.skipif(not FREEZE.exists(), reason="not frozen yet")
def test_every_frozen_file_matches_its_hash():
    f = json.loads(FREEZE.read_text(encoding="utf-8"))
    for name, h in f["files"].items():
        assert sha(CA / name) == h, name
    for name, h in f["upstream"].items():
        assert sha(CA / name) == h, name
    assert not any(f["state_at_freeze"].values())


def test_context_expanded_is_exactly_the_h20_1_eligible_set():
    g = json.loads((CA / "H20_1_GATE.json").read_text(encoding="utf-8"))
    assert sorted(e["feature_name"] for e in g["eligible_for_h20_2"]) == sorted(sp.CONTEXT_EXPANDED)
    assert len(sp.CONTEXT_EXPANDED) == 18


def test_context_core_is_classifier_free():
    reg = {r["feature_name"]: r for r in csv.DictReader((CA / "CONTEXT_FEATURE_REGISTRY.csv").open(encoding="utf-8"))}
    for f in sp.CONTEXT_CORE:
        assert reg[f]["classifiers"] in ("", None), f
    for f in set(sp.CONTEXT_EXPANDED) - set(sp.CONTEXT_CORE):
        assert reg[f]["classifiers"], f
    assert not any(f.startswith("c3_gdelt") for f in sp.CONTEXT_EXPANDED)


def test_market_arm_has_no_excluded_status_or_outcome_column():
    arm = set(sp.MARKET_ARM_FEATURES)
    banned = {"is_live_now", "any_live", "era_end", "n_pairs_ever", "y_365", "ever_delisted", "days_to_delist_announcement",
              "event_delist_announced_within_365d", "days_since_last_signal_removal", "asset_specific_removals_365d",
              "batch_prune_removals_365d", "quote_retirement_removals_365d", "never_had_signal_removal"}
    assert not arm & banned
    assert len(arm) == 23
    assert not arm & set(sp.CONTEXT_EXPANDED)


def test_fold_calendar_has_a_full_horizon_embargo_and_stays_in_development():
    fl = sp.folds()
    assert len(fl) == 8
    for f in fl:
        tr, te0, te1 = (date.fromisoformat(f[k]) for k in ("train_to", "test_from", "test_to"))
        # label of the last training landmark ends at train_to + 1 d + 365 d, before the test window
        assert tr + timedelta(days=366) <= te0  # label end <= test_from 00:00 < first test t
        assert te1 <= sp.DEV[1] + timedelta(days=6)
    assert sp.DEV[1] + timedelta(days=1 + 365) < sp.HOLDOUT[0]
    assert sp.HOLDOUT[1] + timedelta(days=1 + 365) <= sp.ADMIN_CENSOR


def test_same_grid_for_every_arm():
    m = sp.MODEL
    assert "equal_budget_rule" in m and len(m["primary_class"]["hyperparameter_grid"]["lambda"]) == 5
    assert set(sp.ARMS) == {"M0", "M1", "M2", "M1_core", "M2_core"}


def test_verdict_list_is_closed():
    assert sp.VERDICTS["closed_list"] == ["INCREMENTAL CONTEXT SIGNAL SUPPORTED", "PRE-REGISTERED NULL",
                                          "NEGATIVE INCREMENTAL RESULT", "DATA / DESIGN FAILURE"]
    assert set(sp.VERDICTS["conditions_for_support"]) == {f"S{i}" for i in range(1, 8)}


READ_CALLS = {"read_parquet", "read_table", "to_pandas", "read_csv", "iter_batches", "read_row_group", "read"}


@pytest.mark.parametrize("p", sorted((CA / "scripts").glob("h20_2_*.py")), ids=lambda p: p.name)
def test_design_scripts_read_no_rows(p):
    """H20.2 may touch data files through parquet metadata only (schema, num_rows, null counts)."""
    tree = ast.parse(p.read_text(encoding="utf-8"))
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in READ_CALLS:
            # json / text reads of frozen specs are allowed; table reads are not
            src = ast.unparse(n)
            assert "pq." not in src and "pd." not in src and "ParquetFile" not in src, f"{p.name}: {src}"


# ---------------------------------------------------------------- Addendum 02
FREEZE_A02 = CA / "H20_2_FREEZE_A02.json"
LCUV = "LOCKED_CONTEXT_UNSEEN_VALIDATION"


@pytest.mark.skipif(not FREEZE_A02.exists(), reason="A02 not frozen yet")
def test_a02_freeze_matches_and_chains_to_v1():
    a = json.loads(FREEZE_A02.read_text(encoding="utf-8"))
    for name, h in a["files"].items():
        assert sha(CA / name) == h, name
    assert a["v1_freeze"]["sha256"] == sha(FREEZE)
    assert a["addendum_01"]["sha256"] == sha(CA / "H20_2_PREREG_ADDENDUM_01.md")
    assert not any(a["state_at_freeze"].values())


@pytest.mark.skipif(not FREEZE_A02.exists(), reason="A02 not frozen yet")
def test_a02_primary_lambda_is_single_and_fixed():
    m = json.loads((CA / "H20_2_MODEL_SPEC_A02.json").read_text(encoding="utf-8"))
    pc = m["primary_class"]
    assert pc["lambda_primary"] == 10.0 and "hyperparameter_grid" not in pc
    assert "EXPLORATORY" in pc["exploratory_lambda_grid"]["role"]
    v1 = json.loads((CA / "H20_2_MODEL_SPEC.json").read_text(encoding="utf-8"))
    assert "lambda = 10" in v1["sensitivity_reported"]  # provenance: frozen in v1 before any outcome
    assert m["arms"] == v1["arms"] and m["market_arm_features"] == v1["market_arm_features"]
    assert m["context_expanded"] == v1["context_expanded"] and m["context_core"] == v1["context_core"]


@pytest.mark.skipif(not FREEZE_A02.exists(), reason="A02 not frozen yet")
def test_a02_block_renamed_with_identical_dates_and_bounded_claim():
    t1 = json.loads((CA / "H20_2_TEMPORAL_SPLIT.json").read_text(encoding="utf-8"))
    t2 = json.loads((CA / "H20_2_TEMPORAL_SPLIT_A02.json").read_text(encoding="utf-8"))
    assert "HOLDOUT_H20" not in t2["blocks"] and t2["blocks"][LCUV] == t1["blocks"]["HOLDOUT_H20"]
    for k in ("DEVELOPMENT", "EMBARGO_DROPPED", "PROSPECTIVE_CONFIRMATION"):
        assert t2["blocks"][k] == t1["blocks"][k]
    assert t2["folds"] == t1["folds"] and t2["target"] == t1["target"] and t2["landmark_rule"] == t1["landmark_rule"]
    assert "prospective confirmation pending" in t2["claim_scope"]["always_append"]


@pytest.mark.skipif(not FREEZE_A02.exists(), reason="A02 not frozen yet")
def test_a02_s5_is_numeric_and_verdicts_unchanged():
    v1 = json.loads((CA / "H20_2_VERDICT_RULES.json").read_text(encoding="utf-8"))
    v2 = json.loads((CA / "H20_2_VERDICT_RULES_A02.json").read_text(encoding="utf-8"))
    rule = v2["conditions_for_support"]["S5"]["rule"]["all_of"]
    assert [(r["quantity"], r["op"], r["value"]) for r in rule] == [("brier_ratio", "<=", 1.05), ("slope_excess", "<=", 0.20)]
    assert v2["closed_list"] == v1["closed_list"]
    assert set(v2["conditions_for_support"]) == set(v1["conditions_for_support"])
    for k in ("S2", "S6"):
        assert v2["conditions_for_support"][k] == v1["conditions_for_support"][k]
    m1 = json.loads((CA / "H20_2_METRICS_SPEC.json").read_text(encoding="utf-8"))
    m2 = json.loads((CA / "H20_2_METRICS_SPEC_A02.json").read_text(encoding="utf-8"))
    assert m2["primary"]["name"] == m1["primary"]["name"] == "PR_AUC"
    assert m2["primary"]["definition"] == m1["primary"]["definition"]
