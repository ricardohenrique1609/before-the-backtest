"""H20.1 freezes: the representation (registry + rules) and the evaluation sample (plan sections 7, 10).

  --part representation   writes CONTEXT_FEATURE_REGISTRY.csv from h20_1_rep.FEATURES and
                          H20_1_REPRESENTATION_FREEZE.json (sha256 of plan, rules module, registry)
  --part sample           draws one decision timestamp per calendar month 2018-01..2026-09 with
                          numpy default_rng(20261101) and writes H20_1_SAMPLE_FREEZE.json (+ .sha256)

Both refuse to overwrite an existing freeze. No context source is contacted.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_1_freeze.py" --part representation|sample
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

import h20_1_rep as rep
from h20_common import CA, iso, load_freeze, now_utc, sha256_bytes, sha256_file, to_lf

PLAN = CA / "H20_1_REPRESENTATION_PLAN.md"
REGISTRY = CA / "CONTEXT_FEATURE_REGISTRY.csv"
REP_FREEZE = CA / "H20_1_REPRESENTATION_FREEZE.json"
SAMPLE_FREEZE = CA / "H20_1_SAMPLE_FREEZE.json"
SEED = 20261101
FIRST_M, LAST_M = (2018, 1), (2026, 9)

CONDITION = {
    "C1": "H20.0 CONDITIONAL: temporal/archive bias (Fed archive capture early vs late)",
    "C2": "H20.0 CONDITIONAL: US-only; temporal/archive bias",
    "C3": "H20.0 CONDITIONAL: metadata only; GDELT language (English dictionary) and archive bias",
}
FIELDS = [
    "feature_id", "feature_name", "context_layer", "representation_family", "source_ids", "window",
    "definition", "classifiers", "zero_semantics", "missing_semantics", "pit_document_safe",
    "pit_transform_safe", "transform_version", "notes",
]


def representation() -> int:
    if REP_FREEZE.exists():
        print("representation freeze exists; refusing to overwrite")
        return 1
    rows = []
    for fid, name, layer, fam, src, win, defin, kls, zero, miss, just in rep.FEATURES:
        rows.append({
            "feature_id": fid, "feature_name": name, "context_layer": layer, "representation_family": fam,
            "source_ids": src, "window": win, "definition": defin, "classifiers": kls,
            "zero_semantics": zero, "missing_semantics": miss,
            "pit_document_safe": "BY_RULE (plan section 6); verified by audit B",
            "pit_transform_safe": just.split(":", 1)[0], "transform_version": rep.REP_VERSION,
            "notes": f"{just.split(':', 1)[1].strip()} | {CONDITION[layer]}",
        })
    with REGISTRY.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    to_lf([PLAN, REGISTRY])
    freeze = {
        "experiment": "H20.1 Context Representation Feasibility",
        "created_utc": iso(now_utc()),
        "representation_version": rep.REP_VERSION,
        "plan_file": PLAN.name, "plan_sha256": sha256_file(PLAN),
        "rules_module": "scripts/h20_1_rep.py", "rules_module_sha256": sha256_file(CA / "scripts/h20_1_rep.py"),
        "registry_file": REGISTRY.name, "registry_sha256": sha256_file(REGISTRY),
        "common_module_sha256": sha256_file(CA / "scripts/h20_common.py"),
        "freeze_script_sha256": sha256_file(CA / "scripts/h20_1_freeze.py"),
        "n_features": len(rows),
        "features_by_family": pd.Series([r["representation_family"] for r in rows]).value_counts().sort_index().to_dict(),
        "features_by_layer": pd.Series([r["context_layer"] for r in rows]).value_counts().sort_index().to_dict(),
        "r3_candidates_assessed_not_built": [{"id": c[0], "transform": c[1], "class": c[2]} for c in rep.R3_CANDIDATES],
        "frozen_before": "H20.1 evaluation sample draw and any H20.1 context collection",
        "gate_bars": {
            "pit_violations": 0, "determinism": "identical sha256 across two independent builds",
            "provenance_completeness": 1.0, "coverage_nonmissing_share": 0.90, "coverage_years": "8 of 9",
            "semantic_precision": 0.90, "semantic_negative_agreement": 0.90, "semantic_min_n": 10,
            "gdelt_undeterminable_max": 0.20, "sparse_nonzero_share_min": 0.05, "redundancy_abs_spearman": 0.95,
            "redundancy_min_pairs": 30, "drift_era_ratio": 2.0,
        },
        "outcome_inputs": "none",
    }
    body = json.dumps(freeze, indent=1, ensure_ascii=False)
    freeze["freeze_sha256"] = sha256_bytes(body.encode("utf-8"))
    REP_FREEZE.write_bytes(json.dumps(freeze, indent=1, ensure_ascii=False).encode("utf-8"))
    print(f"registry {len(rows)} features; representation freeze {freeze['freeze_sha256']}")
    return 0


def months():
    y, m = FIRST_M
    while (y, m) <= LAST_M:
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def sample() -> int:
    if SAMPLE_FREEZE.exists():
        print("sample freeze exists; refusing to overwrite")
        return 1
    if not REP_FREEZE.exists():
        print("representation must be frozen first")
        return 1
    rng = np.random.default_rng(SEED)
    h0 = [datetime.fromisoformat(s["t_utc"].replace("Z", "+00:00")) for s in load_freeze()["sample"]]
    out = []
    for k, (y, m) in enumerate(months()):
        s = datetime(y, m, 1, tzinfo=UTC)
        e = datetime(y + 1, 1, 1, tzinfo=UTC) if m == 12 else datetime(y, m + 1, 1, tzinfo=UTC)
        t = s + timedelta(minutes=int(rng.integers(0, int((e - s).total_seconds() // 60))))
        # overlap with any H20.0 W30 window, recorded and never used to drop or move t
        overlap = any(abs((t - u).total_seconds()) < rep.W30.total_seconds() for u in h0)
        out.append({"sample_id": f"E{k + 1:03d}", "month": f"{y}-{m:02d}", "t_utc": iso(t),
                    "w30_overlaps_h20_0_w30": overlap})
    freeze = {
        "experiment": "H20.1 Context Representation Feasibility",
        "created_utc": iso(now_utc()),
        "role": "evaluation sample (H20.0's 35 timestamps were the design sample)",
        "plan_sha256": sha256_file(PLAN),
        "representation_freeze_sha256": json.loads(REP_FREEZE.read_text(encoding="utf-8"))["freeze_sha256"],
        "selection_rule": "one decision timestamp per calendar month 2018-01..2026-09; uniform minute within the "
                          "month; numpy default_rng(seed) draws in month order; calendar only, nothing moved, "
                          "added or dropped; no assets",
        "rng": {"generator": "numpy.random.default_rng", "seed": SEED},
        "generation_script_sha256": sha256_file(CA / "scripts/h20_1_freeze.py"),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
                        "platform": platform.platform()},
        "n_timestamps": len(out),
        "n_overlapping_h20_0_w30": sum(o["w30_overlaps_h20_0_w30"] for o in out),
        "sample": out,
    }
    body = json.dumps(freeze, indent=1, ensure_ascii=False)
    freeze["freeze_sha256"] = sha256_bytes(body.encode("utf-8"))
    final = json.dumps(freeze, indent=1, ensure_ascii=False).encode("utf-8")
    SAMPLE_FREEZE.write_bytes(final)
    (CA / "H20_1_SAMPLE_FREEZE.json.sha256").write_text(f"{sha256_bytes(final)}  {SAMPLE_FREEZE.name}\n", encoding="utf-8")
    print(f"frozen {len(out)} timestamps; overlapping H20.0 W30: {freeze['n_overlapping_h20_0_w30']}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=["representation", "sample"])
    sys.exit({"representation": representation, "sample": sample}[ap.parse_args().part]())
