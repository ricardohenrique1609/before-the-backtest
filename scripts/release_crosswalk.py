"""RC2 Part B: add a release-path crosswalk to the release claim-evidence matrix.

For every claim row, resolve the artefact it cites to a path inside the public release package, so a
reader can follow a claim to a file that is actually present. Rows whose artefact is a repository
file outside the package resolve to that repository path and are counted separately.

Run: .venv/Scripts/python -I scripts/release_crosswalk.py
"""

from __future__ import annotations

import collections
import csv
import io
import re
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
REL = ROOT / "papers" / "falsification_first_alpha_discovery" / "release"
MATRIX = REL / "CLAIM_EVIDENCE_MATRIX.csv"

FILE_RE = re.compile(r"[A-Za-z0-9_./-]+\.(?:json|csv|parquet|md|py|sha256|bib)")


def tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, cwd=ROOT).stdout
    return set(out.split())


def resolve(artifact: str, known: set[str], evidence: set[str]) -> tuple[str, str]:
    """Return (release_path, availability) for the first resolvable file in an artifact string."""
    for tok in FILE_RE.findall(artifact or ""):
        name = Path(tok).name
        if name in evidence:
            return f"evidence/{name}", "IN_RELEASE_PACKAGE"
        if (REL / tok).exists():
            return tok, "IN_RELEASE_PACKAGE"
        if tok in known:
            return tok, "IN_REPOSITORY"
        if (ROOT / tok).exists():
            return tok, "IN_WORKING_TREE_ONLY"
    low = (artifact or "").lower()
    if "references" in low or "bib" in low:
        return "references.bib", "IN_RELEASE_PACKAGE"
    if "git" in low or "commit" in low:
        return "(git history)", "IN_REPOSITORY"
    if "paper_v4" in low or "paper_v3" in low or "paper.md" in low:
        return "paper.md", "IN_RELEASE_PACKAGE"
    return "(narrative; no single file)", "NOT_A_FILE"


def main() -> None:
    known = tracked()
    evidence = {p.name for p in (REL / "evidence").glob("*.json")}
    rows = list(csv.DictReader(MATRIX.open(encoding="utf-8")))
    fields = list(rows[0].keys())
    for extra in ("release_path", "availability"):
        if extra not in fields:
            fields.append(extra)

    counts: collections.Counter[str] = collections.Counter()
    for r in rows:
        path, avail = resolve(r.get("artifact", ""), known, evidence)
        r["release_path"] = path
        r["availability"] = avail
        counts[avail] += 1

    with MATRIX.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    total = len(rows)
    print(f"rows {total}")
    for k, v in counts.most_common():
        print(f"  {k:<22} {v:>4}  ({v / total:.1%})")
    file_rows = total - counts["NOT_A_FILE"]
    reachable = counts["IN_RELEASE_PACKAGE"] + counts["IN_REPOSITORY"]
    print(f"\ncited-file rows reachable by a reader: {reachable} of {file_rows} "
          f"({reachable / file_rows:.1%})")
    if counts["IN_WORKING_TREE_ONLY"]:
        print("  GAP - rows citing a file that is neither in the package nor tracked:")
        for r in rows:
            if r["availability"] == "IN_WORKING_TREE_ONLY":
                print(f"    {r['claim_id']}  {r['release_path']}")


if __name__ == "__main__":
    main()
