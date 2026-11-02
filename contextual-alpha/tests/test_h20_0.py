"""H20.0 structural tests: query guard, outcome blindness, timestamp rules, freeze integrity.

    .venv/Scripts/python -m pytest "Contextual Alpha/tests" -q
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

CA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CA / "scripts"))

from h20_common import ForbiddenQueryError, check_query, content_hash  # noqa: E402

# ---------------------------------------------------------------- query guard


@pytest.mark.parametrize(
    "url,params",
    [
        ("https://en.wikipedia.org/w/api.php", {"search": "why did LUNA crash"}),
        ("https://www.federalregister.gov/api/v1/documents.json", {"conditions[term]": "exchange collapse"}),
        ("https://example.org/search", {"q": "TOKEN delisting reason"}),
        ("https://example.org/what-caused-the-hack", None),
    ],
)
def test_outcome_shaped_queries_are_refused(url, params):
    with pytest.raises(ForbiddenQueryError):
        check_query(url, params)


def test_fixed_term_queries_pass():
    check_query("https://www.federalregister.gov/api/v1/documents.json",
                {"conditions[term]": 'cryptocurrency | "digital asset" | "virtual currency" | bitcoin | stablecoin'})
    check_query("https://en.wikipedia.org/w/api.php", {"titles": "Portal:Current events/2020 January 17"})


def test_lookup_of_collected_identifier_is_not_a_query():
    url = "https://news.example.com/2022/05/exchange-hack-latest"
    check_query(url, None, lookup=url)  # an id lookup of an already-collected URL
    with pytest.raises(ForbiddenQueryError):
        check_query("http://web.archive.org/cdx/search/cdx", {"url": url, "extra": "hack"}, lookup=url)


# ---------------------------------------------------------------- outcome blindness

FORBIDDEN_PATHS = [
    "H18_0B_ANNOUNCEMENT_UNIVERSE", "H18_1_PAIR_EVENTS", "H18_1_ASSET_LIFECYCLE", "H18_1B_FULL_DELIST",
    "H18_1B_H18_1_CROSSWALK", "asset_weeks", "landmarks", "features.parquet", "oof_predictions",
    "data/raw/h18_0b/body_", "data/raw/h18_1b/body_", "H19_0_DERIVATIVE", "pair_removals",
]
FORBIDDEN_COLUMNS = ["is_live_now", "ever_delisted", "y_365", "days_to_delist", "usd_close", "trailing_return"]
SEALED = {"h20_0_sealed_survivorship.py"}


def h20_scripts():
    return [p for p in (CA / "scripts").glob("*.py")]


def code_strings(p: Path) -> list[str]:
    """String literals that the code can use: docstrings and comments are excluded, because a
    docstring saying a column is never read is not a read."""
    tree = ast.parse(p.read_text(encoding="utf-8"))
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                docs.add(id(first.value))
    return [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs]


def test_no_collection_or_audit_script_reads_an_outcome_table():
    offenders = []
    for p in h20_scripts():
        if p.name in SEALED:
            continue
        strings = " ".join(code_strings(p))
        for f in FORBIDDEN_PATHS + FORBIDDEN_COLUMNS:
            # the lineage script hashes every candidate path and records schemas (names only), by design
            if p.name == "h20_0_lineage.py" and f in FORBIDDEN_PATHS:
                continue
            # H20.2 design scripts name these paths to exclude them and to read parquet metadata only;
            # tests/test_h20_2.py::test_design_scripts_read_no_rows forbids any row read in them
            if p.name in ("h20_2_spec.py", "h20_2_freeze.py", "h20_2_amend02.py"):
                continue
            # H20.3 is the authorised outcome-opening stage: the lifecycle table is read only by the sealed
            # target stage after X is hashed; tests/test_h20_3.py verifies the seal order and hashes
            if p.name.startswith("h20_3_"):
                continue
            if f in strings:
                offenders.append((p.name, f))
    assert not offenders, offenders


def test_sealed_stage_checks_pre_seal_hashes_first():
    p = CA / "scripts" / "h20_0_sealed_survivorship.py"
    if not p.exists():
        pytest.skip("sealed stage not written yet")
    src = p.read_text(encoding="utf-8")
    assert src.index("H20_0_PRE_SEAL_HASHES") < src.index("is_live_now")


# ---------------------------------------------------------------- timestamp rules


def test_day_only_documents_become_admissible_at_next_local_midnight():
    from h20_0_collect_official import day_end_utc

    # 2020-01-17 in New York ends at 2020-01-18 05:00 UTC (EST, UTC-5)
    assert day_end_utc(date(2020, 1, 17)) == datetime(2020, 1, 18, 5, 0, tzinfo=UTC)
    # summer: EDT, UTC-4
    assert day_end_utc(date(2020, 7, 17)) == datetime(2020, 7, 18, 4, 0, tzinfo=UTC)


def test_gdelt_slice_is_published_before_t():
    from h20_0_collect_gdelt import slice_for

    t = datetime(2020, 1, 17, 15, 0, tzinfo=UTC)
    assert slice_for(t) == datetime(2020, 1, 17, 14, 45, tzinfo=UTC)
    assert slice_for(datetime(2020, 1, 17, 15, 14, tzinfo=UTC)) == datetime(2020, 1, 17, 14, 45, tzinfo=UTC)


def test_content_hash_normalises_whitespace_only():
    assert content_hash("A  b\n c") == content_hash("A b c")
    assert content_hash("A b c") != content_hash("A b d")


# ---------------------------------------------------------------- freeze integrity


def test_freeze_hash_matches_its_content():
    p = CA / "H20_0_SAMPLE_FREEZE.json"
    raw = p.read_bytes()
    side = (CA / "H20_0_SAMPLE_FREEZE.json.sha256").read_text().split()[0]
    assert hashlib.sha256(raw).hexdigest() == side
    f = json.loads(raw)
    inner = {k: v for k, v in f.items() if k not in ("freeze_sha256", "freeze_sha256_note")}
    assert hashlib.sha256(json.dumps(inner, indent=1, ensure_ascii=False).encode()).hexdigest() == f["freeze_sha256"]


def test_freeze_plan_hash_matches_plan_on_disk():
    f = json.loads((CA / "H20_0_SAMPLE_FREEZE.json").read_text(encoding="utf-8"))
    plan = (CA / "H20_0_CONTEXT_FEASIBILITY_PLAN.md").read_bytes()
    assert hashlib.sha256(plan).hexdigest() == f["plan_sha256"]


def test_freeze_shape():
    f = json.loads((CA / "H20_0_SAMPLE_FREEZE.json").read_text(encoding="utf-8"))
    assert f["n_timestamps"] == 35 and f["n_asset_time_units"] == 105
    quarters = [s["quarter"] for s in f["sample"]]
    assert quarters[0] == "2018-Q1" and quarters[-1] == "2026-Q3" and len(set(quarters)) == 35
    for s in f["sample"]:
        assert [a["liquidity_tercile"] for a in s["assets"]] == ["T1_LOW", "T2_MID", "T3_HIGH"]
        y, q = s["quarter"].split("-Q")
        t = datetime.fromisoformat(s["t_utc"].replace("Z", "+00:00"))
        assert t.year == int(y) and (t.month - 1) // 3 + 1 == int(q)


def test_nothing_written_outside_contextual_alpha():
    for p in h20_scripts():
        src = p.read_text(encoding="utf-8")
        for m in re.finditer(r"ROOT\s*/\s*\"([^\"]+)\"", src):
            target = m.group(1)
            # ROOT-relative paths are inherited read-only inputs; every write uses CA-based constants
            assert not re.search(rf"(to_parquet|write_text|write_bytes|to_csv)\([^)]*{re.escape(target)}", src), (p.name, target)
