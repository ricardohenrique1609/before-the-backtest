"""H20.3 execution-integrity tests: seal order, single LCUV run, frozen lambda, closed verdict recomputed.

    .venv/Scripts/python -m pytest "Contextual Alpha/tests" -q
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

CA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CA / "scripts"))
OUT = CA / "data" / "derived" / "h20_3"
V = CA / "H20_3_VERDICT.json"
pytestmark = pytest.mark.skipif(not V.exists(), reason="H20.3 not executed")


def j(n):
    return json.loads((CA / n).read_text(encoding="utf-8"))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_x_sealed_before_y_and_y_hash_holds():
    xs, ys = j("H20_3_X_SEAL.json"), j("H20_3_Y_SEAL.json")
    assert xs["sealed_utc"] < ys["sealed_utc"] and xs["outcome_read_before_seal"] is False
    assert ys["x_seal_sha256"] == sha(CA / "H20_3_X_SEAL.json")
    if (OUT / "y.parquet").exists():
        assert sha(OUT / "y.parquet") == ys["y_parquet_sha256"]


def test_pre_lcuv_freeze_precedes_single_lcuv_run():
    fz, lc = j("H20_3_PRE_LCUV_FREEZE.json"), j("H20_3_LCUV_RESULTS.json")
    assert fz["frozen_utc"] < lc["scored_utc"] and fz["lcuv_rows_scored_before_freeze"] == 0
    assert lc["scoring_runs"] == 1 and fz["lambda"] == 10.0 == lc["primary_lambda"]
    assert sha(CA / "H20_3_DEVELOPMENT_RESULTS.json") == fz["development_results_sha256"]
    assert sha(CA / "H20_3_BOOTSTRAP_RESULTS.json") == fz["bootstrap_results_sha256"]


def test_only_development_and_lcuv_blocks_were_built():
    xs = j("H20_3_X_SEAL.json")
    assert set(xs["rows_by_block"]) == {"DEVELOPMENT", "LOCKED_CONTEXT_UNSEEN_VALIDATION"}


def test_arms_match_the_frozen_sets():
    xs, cs = j("H20_3_X_SEAL.json"), j("H20_2_CONTEXT_SETS.json")
    exp = [e["feature_name"] for e in cs["CONTEXT_EXPANDED"]]
    assert xs["arms"]["M1"]["features"] == exp and xs["arms"]["M1_core"]["features"] == cs["CONTEXT_CORE"]
    assert xs["arms"]["M0"]["n_features"] == 23 and xs["arms"]["M2"]["features"] == xs["arms"]["M0"]["features"] + exp


def test_verdict_is_closed_and_recomputes_from_criteria():
    v, rules = j("H20_3_VERDICT.json"), j("H20_2_VERDICT_RULES_A02.json")
    assert v["verdict"] in rules["closed_list"]
    c = v["criteria"]
    if v["design_failures"]:
        assert v["verdict"] == "DATA / DESIGN FAILURE"
    elif all(x["PASS"] for x in c.values()):
        assert v["verdict"] == "INCREMENTAL CONTEXT SIGNAL SUPPORTED"
    elif c["S3"]["value"][1] < 0 and c["S4"]["value"] < 0:
        assert v["verdict"] == "NEGATIVE INCREMENTAL RESULT"
    else:
        assert v["verdict"] == "PRE-REGISTERED NULL"
    if v["verdict"] != "INCREMENTAL CONTEXT SIGNAL SUPPORTED":
        assert v["claim"] == "no incremental context signal is claimed"


def test_exploratory_is_labelled_and_separate():
    e = j("H20_3_EXPLORATORY_RESULTS.json")
    assert e["label"].startswith("EXPLORATORY")
