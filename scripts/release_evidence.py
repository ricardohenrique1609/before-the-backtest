"""RC2 Part B: copy the cited derived evidence artefacts into the release package.

Copies ONLY derived summary artefacts that the claim-evidence matrix cites and that are not already
tracked by git. No raw corpus, no market-data archive, no downloaded source document may enter
release/evidence/ - the script refuses anything above a size ceiling or with a non-JSON extension.

The repository's global `data/` ignore rule is left in place; the copies live inside the release
package, which is tracked.

Run: .venv/Scripts/python -I scripts/release_evidence.py
"""

from __future__ import annotations

import csv
import hashlib
import io
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
REL = ROOT / "papers" / "falsification_first_alpha_discovery" / "release"
EV = REL / "evidence"
EV.mkdir(parents=True, exist_ok=True)

# Guardrails: a derived summary artefact is small and is JSON. Anything else is a corpus.
MAX_BYTES = 200_000
ALLOWED_SUFFIX = {".json"}

# The nine cited derived artefacts, with the family that produced each and the commit that
# introduced it. Roles are stated so a reader knows what each supports.
ARTEFACTS = [
    ("data/alpha_sprint/h13_results.json", "H13", "9e73558",
     "survivorship audit and bias bounds for the micro-cap screen"),
    ("data/alpha_sprint/h18_1b_discover_incomplete.json", "H18.1b", "27c3283",
     "refusal record of the catalog coverage guard"),
    ("data/alpha_sprint/h18_2_audit.json", "H18.2", "45d575d",
     "risk-set entry diagnostics, including the baseline coverage differential"),
    ("data/alpha_sprint/h18_2_universe.json", "H18.2", "45d575d",
     "instrument universe reconstructed from the venue archive"),
    ("data/alpha_sprint/h18_3_development.json", "H18.3", "4aa4180",
     "development-block results, pooled metrics and cluster bootstrap"),
    ("data/alpha_sprint/h18_3_eligibility.json", "H18.3", "522bafb",
     "frozen splits, censoring and event-sharing check"),
    ("data/alpha_sprint/h18_3_falsification.json", "H18.3", "4aa4180",
     "falsification suite, including placebo variants"),
    ("data/alpha_sprint/h18_3_pit_audit.json", "H18.3", "203390b",
     "point-in-time classification audit"),
    ("data/alpha_sprint/h19_2_prefreeze.json", "H19.2", "42f35df",
     "the support audit: quantiles, exclusions and the stop rule"),
]


def tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, cwd=ROOT).stdout
    return set(out.split())


def main() -> None:
    known = tracked()
    rows = []
    total = 0
    for orig, family, commit, role in ARTEFACTS:
        src = ROOT / orig
        if not src.exists():
            raise SystemExit(f"MISSING SOURCE ARTEFACT: {orig}")
        if src.suffix not in ALLOWED_SUFFIX:
            raise SystemExit(f"REFUSED (not a derived summary): {orig}")
        size = src.stat().st_size
        if size > MAX_BYTES:
            raise SystemExit(f"REFUSED (too large for a derived summary, {size} bytes): {orig}")
        if orig in known:
            print(f"  skip (already tracked): {orig}")
            continue
        dst = EV / src.name
        shutil.copyfile(src, dst)
        digest = hashlib.sha256(dst.read_bytes()).hexdigest()
        assert digest == hashlib.sha256(src.read_bytes()).hexdigest(), "copy mismatch"
        rows.append({
            "release_path": f"evidence/{src.name}",
            "original_path": orig,
            "family": family,
            "source_commit": commit,
            "bytes": size,
            "sha256": digest,
            "evidence_role": role,
            "raw_or_derived": "derived",
        })
        total += size
        print(f"  copied {size:>7,} bytes  {orig}")

    with (REL / "EVIDENCE_MANIFEST.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["release_path", "original_path", "family",
                                           "source_commit", "bytes", "sha256", "evidence_role",
                                           "raw_or_derived"])
        w.writeheader()
        w.writerows(rows)

    assert all(r["raw_or_derived"] == "derived" for r in rows), "a non-derived row would be a bug"
    print(f"\n{len(rows)} derived artefacts, {total:,} bytes, written to release/evidence/")
    print("EVIDENCE_MANIFEST.csv written; every row is 'derived'")


if __name__ == "__main__":
    main()
