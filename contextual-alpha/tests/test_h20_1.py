"""H20.1 structural tests: time rules, freezes, outcome blindness, no model-time leakage, missing != zero.

    .venv/Scripts/python -m pytest "Contextual Alpha/tests" -q
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

CA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CA / "scripts"))

import h20_1_rep as rep  # noqa: E402

H20_1_SCRIPTS = sorted((CA / "scripts").glob("h20_1_*.py"))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------- time rules
def test_day_end_rule_is_next_et_midnight():
    assert rep.day_end_et(date(2020, 1, 15)) == datetime(2020, 1, 16, 5, 0, tzinfo=UTC)  # EST
    assert rep.day_end_et(date(2020, 7, 15)) == datetime(2020, 7, 16, 4, 0, tzinfo=UTC)  # EDT


def test_alfred_asof_never_admits_a_same_et_day_vintage():
    t = datetime(2020, 5, 10, 3, 0, tzinfo=UTC)  # 2020-05-09 23:00 ET
    assert rep.alfred_asof(t) == date(2020, 5, 8)
    assert rep.day_end_et(rep.alfred_asof(t)) <= t


@pytest.mark.parametrize("w", [rep.W7, rep.W30])
def test_window_is_left_open_right_closed(w):
    t = datetime(2022, 3, 1, 12, 0, tzinfo=UTC)
    assert rep.in_window(t, t, w)
    assert not rep.in_window(t + timedelta(minutes=1), t, w)
    assert not rep.in_window(t - w, t, w)
    assert rep.in_window(t - w + timedelta(minutes=1), t, w)


def test_gdelt_slices_are_published_by_t():
    t = datetime(2021, 6, 3, 0, 7, tzinfo=UTC)
    s = rep.gdelt_slices(t)
    assert len(s) == 7 and len({x.date() for x in s}) == 7
    assert all(x + rep.GDELT_PUBLISH_LAG <= t and x.minute % 15 == 0 for x in s)


def test_wiki_days_end_on_t():
    t = datetime(2024, 2, 29, 23, 59, tzinfo=UTC)
    d = rep.wiki_days(t)
    assert d[-1] == date(2024, 2, 29) and d[0] == date(2024, 2, 23) and len(d) == 7


def test_cftc_walked_spans_exclude_blocked_years():
    assert rep.cftc_walked(datetime(2019, 5, 1, tzinfo=UTC), datetime(2019, 5, 31, tzinfo=UTC))
    assert not rep.cftc_walked(datetime(2022, 5, 1, tzinfo=UTC), datetime(2022, 5, 31, tzinfo=UTC))
    assert not rep.cftc_walked(datetime(2018, 12, 20, tzinfo=UTC), datetime(2019, 1, 10, tzinfo=UTC))


# ---------------------------------------------------------------- dictionaries
def test_dictionaries_behave_as_written():
    assert rep.K_CRYPTO.search("SEC Charges Bitcoin Mining Company")
    assert not rep.K_CRYPTO.search("Federal Reserve issues FOMC statement")
    assert rep.K_FOMC_TITLE.search("Federal Reserve issues FOMC statement")
    assert not rep.K_FOMC_TITLE.search("Minutes of the Federal Open Market Committee")
    assert rep.K_SEC_ENFORCEMENT.search("SEC Charges Adviser With Fraud")
    assert not rep.K_SEC_ENFORCEMENT.search("SEC Names New Chief Accountant")


def test_no_named_entities_beyond_the_inherited_one():
    names = {"ftx", "terra", "luna", "celsius", "tether", "ust", "coinbase", "ripple", "xrp", "mt. gox"}
    for terms in rep.LEXICON.values():
        assert not names & {t.lower() for t in terms}


# ---------------------------------------------------------------- freezes
def test_representation_freeze_matches_files():
    f = json.loads((CA / "H20_1_REPRESENTATION_FREEZE.json").read_text(encoding="utf-8"))
    assert f["plan_sha256"] == sha(CA / "H20_1_REPRESENTATION_PLAN.md")
    assert f["registry_sha256"] == sha(CA / "CONTEXT_FEATURE_REGISTRY.csv")
    assert f["rules_module_sha256"] == sha(CA / "scripts" / "h20_1_rep.py")
    assert f["n_features"] == len(rep.FEATURES)


def test_sample_freeze_is_reproducible_and_calendar_only():
    j = json.loads((CA / "H20_1_SAMPLE_FREEZE.json").read_text(encoding="utf-8"))
    assert (CA / "H20_1_SAMPLE_FREEZE.json.sha256").read_text().split()[0] == sha(CA / "H20_1_SAMPLE_FREEZE.json")
    rng = np.random.default_rng(j["rng"]["seed"])
    y, m = 2018, 1
    for s in j["sample"]:
        a = datetime(y, m, 1, tzinfo=UTC)
        b = datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=UTC)
        t = a + timedelta(minutes=int(rng.integers(0, int((b - a).total_seconds() // 60))))
        assert s["t_utc"] == t.isoformat().replace("+00:00", "Z") and s["month"] == f"{y}-{m:02d}"
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    assert len(j["sample"]) == 105
    assert j["representation_freeze_sha256"] == json.loads(
        (CA / "H20_1_REPRESENTATION_FREEZE.json").read_text(encoding="utf-8"))["freeze_sha256"]


# ---------------------------------------------------------------- outcome blindness, model-time leakage
FORBIDDEN = [
    "H18_0B_ANNOUNCEMENT_UNIVERSE", "H18_1_PAIR_EVENTS", "H18_1_ASSET_LIFECYCLE", "H18_1B_FULL_DELIST",
    "H18_1B_H18_1_CROSSWALK", "asset_weeks", "landmarks", "features.parquet", "oof_predictions",
    "H19_0_DERIVATIVE", "pair_removals", "is_live_now", "ever_delisted", "y_365", "days_to_delist",
    "usd_close", "trailing_return", "symbol_windows", "asset_daily", "binance_cms", "binance_catalog",
    "binance_detail", "entity_resolution", "wiki_assets",  # C4 / C5 inputs
]


def literals(p: Path) -> list[str]:
    tree = ast.parse(p.read_text(encoding="utf-8"))
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                docs.add(id(first.value))
    return [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs]


@pytest.mark.parametrize("p", H20_1_SCRIPTS, ids=lambda p: p.name)
def test_h20_1_scripts_read_no_outcome_or_asset_input(p):
    for s in literals(p):
        for bad in FORBIDDEN:
            assert bad.lower() not in s.lower(), f"{p.name}: {bad!r} in {s[:80]!r}"


@pytest.mark.parametrize("p", H20_1_SCRIPTS, ids=lambda p: p.name)
def test_no_model_based_transform_is_imported(p):
    tree = ast.parse(p.read_text(encoding="utf-8"))
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module.split(".")[0])
    assert not mods & {"openai", "anthropic", "transformers", "sentence_transformers", "sklearn", "gensim",
                       "torch", "tensorflow", "spacy", "nltk"}


# ---------------------------------------------------------------- built outputs (skipped before a build)
BUILD = CA / "data" / "derived" / "h20_1" / "features_long.csv"


@pytest.mark.skipif(not BUILD.exists(), reason="features not built")
def test_missing_is_never_zero():
    import pandas as pd

    V = pd.read_csv(BUILD, dtype=str, keep_default_na=False)
    miss = V[V["status"] == "MISSING"]
    assert (miss["value"] == "").all() and (miss["missing_reason"] != "").all()
    assert (V.loc[V["status"] == "ZERO", "value"].astype(float) == 0).all()
    assert (V.loc[V["status"] == "VALUE", "value"] != "").all()


@pytest.mark.skipif(not BUILD.exists(), reason="features not built")
def test_no_provenance_record_after_t():
    import pandas as pd

    P = pd.read_csv(BUILD.parent / "provenance.csv", dtype=str, keep_default_na=False)
    P = P[P["public_availability_time"] != ""]
    assert (pd.to_datetime(P["public_availability_time"], utc=True) <= pd.to_datetime(P["t_utc"], utc=True)).all()
