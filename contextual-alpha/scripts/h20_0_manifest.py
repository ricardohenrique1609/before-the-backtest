"""H20.0 — CONTEXT_EVIDENCE_MANIFEST.csv: every H20 artefact with hash, size, rows, producing script and
evidence label (NEW H20 EVIDENCE vs INHERITED EVIDENCE vs DESIGN). Run last.

Also publishes registries/CONTEXT_SOURCE_REGISTRY.csv at the project root, where the brief asks for it.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_manifest.py"
"""

from __future__ import annotations

import csv
import platform
import shutil
import subprocess
import sys

import pandas as pd

from h20_common import CA, ROOT, iso, now_utc, sha256_file, to_lf

PRODUCER = {
    "H20_0_SAMPLE_FREEZE.json": "h20_0_sample_freeze.py",
    "H20_0_GATE.json": "h20_0_audit.py + h20_0_sealed_survivorship.py",
    "evidence/H20_0_SEALED_SURVIVORSHIP.json": "h20_0_sealed_survivorship.py",
    "evidence/H20_0_ENTITY_GOLD_VALIDATION.csv": "hand check (researcher) of h20_0_entity_validation.py output",
    "evidence/H20_0_VALIDATION_SAMPLE.json": "h20_0_entity_validation.py",
    "manifests/H20_0_INHERITED_LINEAGE.csv": "h20_0_lineage.py",
    "manifests/H20_0_PRE_SEAL_HASHES.json": "h20_0_audit.py",
    "data/derived/context_documents.parquet": "h20_0_audit.py",
}
INTERIM_PRODUCER = {
    "binance": "h20_0_collect_binance.py", "fed": "h20_0_collect_official.py", "fr": "h20_0_collect_official.py",
    "sec": "h20_0_collect_official.py", "cftc": "h20_0_collect_official.py", "alfred": "h20_0_collect_official.py",
    "gdelt": "h20_0_collect_gdelt.py", "wiki": "h20_0_collect_wiki.py", "entity": "h20_0_entities.py / h20_0_entity_validation.py",
    "archive": "h20_0_archive_refetch.py", "refetch": "h20_0_archive_refetch.py",
}


def rows_of(p) -> str:
    try:
        if p.suffix == ".parquet":
            return str(len(pd.read_parquet(p)))
        if p.suffix == ".csv":
            return str(sum(1 for _ in p.open(encoding="utf-8")) - 1)
    except Exception:  # noqa: BLE001
        return ""
    return ""


def main() -> int:
    shutil.copyfile(CA / "registries" / "CONTEXT_SOURCE_REGISTRY.csv", CA / "CONTEXT_SOURCE_REGISTRY.csv")
    to_lf([p for p in CA.rglob("*") if p.relative_to(CA).parts[:1] not in (("data",), ("docs",)) and "__pycache__" not in p.parts])
    files = []
    for pat in ("*.md", "*.json", "*.csv", "*.sha256", "evidence/*", "manifests/*", "registries/*", "scripts/*.py",
                "tests/*.py", "data/interim/*", "data/derived/*", "data/raw/inherited/*"):
        files += [p for p in CA.glob(pat) if p.is_file()]
    out = []
    for p in sorted(set(files)):
        rel = str(p.relative_to(CA)).replace("\\", "/")
        if rel == "CONTEXT_EVIDENCE_MANIFEST.csv":
            continue
        if rel.startswith("data/raw/inherited/"):
            label, stage, prod = "INHERITED EVIDENCE (snapshot copy)", "5-sample", "h20_0_sample_freeze.py"
        elif rel.startswith(("scripts/", "tests/")):
            label, stage, prod = "CODE", "all", ""
        elif rel.endswith(".md") or rel.startswith("registries/") or rel == "CONTEXT_SOURCE_REGISTRY.csv":
            label, stage, prod = "DESIGN / REPORT", "3-4-9", "authored"
        elif rel.startswith("manifests/H20_0_INHERITED"):
            label, stage, prod = "INHERITED EVIDENCE (lineage)", "1-3", PRODUCER[rel]
        else:
            label = "NEW H20 EVIDENCE"
            key = p.name.split("_")[0]
            stage = "6-7-collect" if rel.startswith("data/interim/") else "8-9-audit"
            prod = PRODUCER.get(rel) or INTERIM_PRODUCER.get(key, "h20_0_audit.py")
        out.append({"path": rel, "sha256": sha256_file(p), "bytes": p.stat().st_size, "rows": rows_of(p),
                    "evidence_label": label, "stage": stage, "produced_by": prod,
                    "git_tracked_by_repo_rules": not rel.startswith("data/")})
    with (CA / "CONTEXT_EVIDENCE_MANIFEST.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    (CA / "manifests" / "H20_0_ENVIRONMENT.txt").write_text(
        f"generated_utc={iso(now_utc())}\nrepo_head={head}\npython={sys.version.split()[0]}\npandas={pd.__version__}\n"
        f"platform={platform.platform()}\nraw_data=Contextual Alpha/data/raw (gitignored by repo rule 'data/')\n",
        encoding="utf-8")
    to_lf([CA / "CONTEXT_EVIDENCE_MANIFEST.csv", CA / "manifests" / "H20_0_ENVIRONMENT.txt"])
    print(f"{len(out)} files in manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
