"""H20.3 shared plumbing: effective specification (v1 superseded by A02), P0 freeze verification,
landmark calendar, sealed-stage guards. Nothing here reads an outcome.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from h20_common import CA, DERIVED, INTERIM, ROOT, iso, now_utc, sha256_file, to_lf

OUT = DERIVED / "h20_3"
INT3 = INTERIM / "h20_3"
LCUV = "LOCKED_CONTEXT_UNSEEN_VALIDATION"
CAL = OUT / "landmark_calendar.json"


def load(name: str) -> dict:
    return json.loads((CA / name).read_text(encoding="utf-8"))


def spec() -> dict:
    """Effective specification: A02 files where they exist, else v1."""
    return {
        "model": load("H20_2_MODEL_SPEC_A02.json"),
        "split": load("H20_2_TEMPORAL_SPLIT_A02.json"),
        "metrics": load("H20_2_METRICS_SPEC_A02.json"),
        "verdict": load("H20_2_VERDICT_RULES_A02.json"),
        "context": load("H20_2_CONTEXT_SETS.json"),
    }


def p0() -> dict:
    """Verify every H20.1, H20.2 and A02 hash. Raises on any mismatch (DATA / DESIGN FAILURE)."""
    bad = []
    v1 = load("H20_2_FREEZE.json")
    a2 = load("H20_2_FREEZE_A02.json")
    f1 = load("H20_1_REPRESENTATION_FREEZE.json")
    for n, h in {**v1["files"], **v1["upstream"]}.items():
        if sha256_file(CA / n) != h:
            bad.append(n)
    for n, h in a2["files"].items():
        if sha256_file(CA / n) != h:
            bad.append(n)
    if a2["v1_freeze"]["sha256"] != sha256_file(CA / "H20_2_FREEZE.json"):
        bad.append("H20_2_FREEZE.json (chain)")
    for k, n in (("plan_sha256", "H20_1_REPRESENTATION_PLAN.md"), ("rules_module_sha256", "scripts/h20_1_rep.py"),
                 ("registry_sha256", "CONTEXT_FEATURE_REGISTRY.csv")):
        if f1[k] != sha256_file(CA / n):
            bad.append(n)
    if bad:
        raise SystemExit(f"P0 FAILED - DATA / DESIGN FAILURE: hash mismatch {bad}")
    return {"verified_utc": iso(now_utc()), "v1_files": len(v1["files"]) + len(v1["upstream"]), "a02_files": len(a2["files"]),
            "h20_1_files": 3, "mismatches": 0}


def mondays(a: date, b: date) -> list[date]:
    d, out = a + timedelta(days=(7 - a.weekday()) % 7), []
    while d <= b:
        out.append(d)
        d += timedelta(days=7)
    return out


def block_of(w: date, sp: dict) -> str | None:
    for k, v in sp["split"]["blocks"].items():
        if date.fromisoformat(v["first_landmark_monday"]) <= w <= date.fromisoformat(v["last_landmark_monday"]):
            return k
    return None


def decision_time(w: date) -> datetime:
    return datetime(w.year, w.month, w.day, tzinfo=UTC) + timedelta(days=1)


def calendar() -> list[dict]:
    """Landmark Mondays of DEVELOPMENT and LCUV (the blocks H20.3 scores). EMBARGO and PROSPECTIVE are not built."""
    sp = spec()
    out = []
    for k in ("DEVELOPMENT", LCUV):
        b = sp["split"]["blocks"][k]
        for w in mondays(date.fromisoformat(b["first_landmark_monday"]), date.fromisoformat(b["last_landmark_monday"])):
            out.append({"sample_id": f"W{w.isoformat()}", "week": w.isoformat(), "t_utc": iso(decision_time(w)), "block": k})
    return out


def write_calendar() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    CAL.write_text(json.dumps({"sample": calendar()}, indent=1), encoding="utf-8")
    to_lf([CAL])
    return CAL


def write_json(name: str, obj) -> Path:
    p = CA / name
    p.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")
    to_lf([p])
    return p


__all__ = ["CA", "ROOT", "OUT", "INT3", "LCUV", "CAL", "spec", "p0", "calendar", "write_calendar", "decision_time",
           "block_of", "write_json", "sha256_file", "iso", "now_utc", "to_lf", "INTERIM"]
