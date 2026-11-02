"""H20.1 — publish the tracked copies of the build and write the artefact manifest.

Copies data/derived/h20_1/provenance.csv to H20_1_FEATURE_PROVENANCE.csv and features_wide.csv to
evidence/H20_1_FEATURE_MATRIX.csv, refusing if either copy's sha256 differs from the deterministic
build recorded in H20_1_REPRESENTATION_METRICS.json. Then writes manifests/H20_1_MANIFEST.csv with
the sha256 of every H20.1 artefact, script, test and interim input.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_1_manifest.py"
"""

from __future__ import annotations

import csv
import json
import shutil

from h20_common import CA, DERIVED, EVIDENCE, INTERIM, MANIFESTS, sha256_file, to_lf

BUILD = DERIVED / "h20_1"


def main() -> int:
    m = json.loads((CA / "H20_1_REPRESENTATION_METRICS.json").read_text(encoding="utf-8"))
    built = m["build_outputs_sha256"]
    for src, dst in (("provenance.csv", CA / "H20_1_FEATURE_PROVENANCE.csv"),
                     ("features_wide.csv", EVIDENCE / "H20_1_FEATURE_MATRIX.csv")):
        if sha256_file(BUILD / src) != built[src]:
            print(f"{src} differs from the audited build; refusing")
            return 1
        shutil.copyfile(BUILD / src, dst)
        assert sha256_file(dst) == built[src]
    rows = []
    files = sorted(CA.glob("H20_1_*")) + [CA / "CONTEXT_FEATURE_REGISTRY.csv"] + sorted(EVIDENCE.glob("H20_1_*")) \
        + sorted((CA / "scripts").glob("h20_1_*.py")) + [CA / "scripts" / "h20_common.py", CA / "tests" / "test_h20_1.py"]
    to_lf([f for f in files if f.name != "H20_1_FEATURE_PROVENANCE.csv"])
    for p in files:
        rows.append({"path": str(p.relative_to(CA)).replace("\\", "/"), "sha256": sha256_file(p), "bytes": p.stat().st_size,
                     "tracked": True})
    for p in sorted((INTERIM / "h20_1").glob("*.parquet")) + sorted(BUILD.glob("*.csv")):
        rows.append({"path": str(p.relative_to(CA)).replace("\\", "/"), "sha256": sha256_file(p), "bytes": p.stat().st_size,
                     "tracked": False})
    out = MANIFESTS / "H20_1_MANIFEST.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["path", "sha256", "bytes", "tracked"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"manifest {len(rows)} entries -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
