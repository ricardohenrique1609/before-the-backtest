"""H20.0 — lineage of every inherited artefact candidate. Read-only on the parent repository.

For each candidate path outside Contextual Alpha this records SHA-256, size, row count and schema
(parquet), whether git tracks it, and the last commit that touched it. Nothing outside
Contextual Alpha is opened for writing. Column VALUES are never read here, so outcome columns that
exist in some H18 tables are seen only as names.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_lineage.py"

Writes Contextual Alpha/manifests/H20_0_INHERITED_LINEAGE.csv
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path

import pyarrow.parquet as pq

CA = Path(__file__).resolve().parents[1]
ROOT = CA.parent
OUT = CA / "manifests" / "H20_0_INHERITED_LINEAGE.csv"

CANDIDATES = [
    "H18_0_DATA_AUDIT.md",
    "H18_0_GATE.json",
    "data/raw/h18_0/announcements_binance.parquet",
    "data/raw/h18_0/announcements_bybit.parquet",
    "data/raw/h18_0/announcements_okx.parquet",
    "H18_0B_DATA_AUDIT.md",
    "H18_0B_GATE.json",
    "H18_0B_ANNOUNCEMENT_UNIVERSE.parquet",
    "H18_1_DATA_AUDIT.md",
    "H18_1_ASSET_LIFECYCLE.parquet",
    "H18_1_ASSET_PAIR_STATE.parquet",
    "H18_1_PAIR_EVENTS.parquet",
    "H18_1B_DATA_AUDIT.md",
    "H18_1B_GATE.json",
    "H18_1B_FULL_DELIST_ANNOUNCEMENTS.parquet",
    "H18_1B_FULL_DELIST_EVENTS.parquet",
    "data/raw/h18_1b/catalog_titles.parquet",
    "data/raw/h18_1b/catalog_scan.csv",
    "data/raw/h18_1b/rebrand_notices.parquet",
    "data/raw/h18_1b/asset_pair_state_extended.parquet",
    "data/alpha_sprint/h18_1b_discover.json",
    "data/alpha_sprint/h18_1b_rebrand.json",
    "data/raw/h18_2/symbol_windows.parquet",
    "data/raw/h18_2/spot_symbols.parquet",
    "data/raw/h18_2/monitoring_tag_events.parquet",
    "data/raw/h18_2/asset_weeks.parquet",
    "H18_2_RISK_SET_AUDIT.md",
    "H18_3_PIT_AUDIT.md",
    "H18_3_PREREG.md",
    "H18_3_PRE_HOLDOUT_FREEZE.json",
    "data/raw/h18_3/asset_daily.parquet",
    "data/raw/h18_3/landmarks_pit.parquet",
    "data/raw/h18_3/pair_removals_pit.parquet",
    "data/raw/h18_3/quote_retirement_notices.parquet",
    "data/raw/h18_3/features.parquet",
    "H19_0_DATA_AUDIT.md",
    "H19_0_DERIVATIVE_SECURITY_MASTER.parquet",
    "H19_0_DERIVATIVE_NOTICES.parquet",
    "data/raw/h19_2/perp_windows.parquet",
    "scripts/h18_1b_discover.py",
    "scripts/h18_1b_rebrand.py",
    "scripts/h18_2_universe.py",
    "scripts/h18_3_classes_pit.py",
    "src/qie/time.py",
    "RESEARCH_GOVERNANCE_V2.md",
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip()


def main() -> int:
    rows = []
    head = git("rev-parse", "HEAD")
    for rel in CANDIDATES:
        p = ROOT / rel
        row = {"path": rel, "exists": p.exists(), "repo_head": head}
        if p.exists():
            row["sha256"] = sha256(p)
            row["bytes"] = p.stat().st_size
            tracked = bool(git("ls-files", "--", rel))
            row["git_tracked"] = tracked
            row["last_commit"] = git("log", "-1", "--format=%h %cs %s", "--", rel) if tracked else ""
            if p.suffix == ".parquet":
                md = pq.read_metadata(p)
                row["rows"] = md.num_rows
                row["columns"] = ";".join(n for n in pq.read_schema(p).names if not n.startswith("__index"))
        rows.append(row)
    fields = ["path", "exists", "sha256", "bytes", "rows", "git_tracked", "last_commit", "repo_head", "columns"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    print(f"{len(rows)} candidates, {sum(r['exists'] for r in rows)} exist -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
