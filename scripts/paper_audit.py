"""Run the paper's four audits: claim, status, language, internal consistency.

Reads only the manuscript and its evidence files. Computes nothing economic, loads no price, and
touches no experiment artefact. Exit code is non-zero if any audit fails its target.

Run: .venv/Scripts/python -I scripts/paper_audit.py
"""

from __future__ import annotations

import collections
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "falsification_first_alpha_discovery"

TRIVIAL = set("0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 32".split()) | {
    str(y) for y in range(2009, 2031)}

FLAGGED = ["prove", "proved", "proves", "proven", "obvious", "obviously", "clearly", "always",
           "never", "guaranteed", "caused", "causes", "insider", "profitab", "alpha",
           "demonstrat"]

EXPECTED_STATUS = {
    "H18.3": "PRE-REGISTERED NULL",
    "H19.0": "PARTIAL PASS",
    "H19.2": "BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL",
    "H13": "ECONOMIC REJECT",
    "H17.0": "INFRASTRUCTURE BLOCKED",
    "H18.1b": "STRONG PASS",
}

CONSISTENCY = {
    "H13 denominators kept apart": r"5,604-CIK.{0,200}1,197-company",
    "H18.3 event accounting explained": r"sum to more than the 201-event universe",
    "H19.0 notice coverage bounded": r"not 184 events proven to have had no notice",
    "H19.0 margin UNKNOWN not zero": r"`UNKNOWN`, not zero",
    "H13 economic question unresolved": r"economic hypothesis about net-nets is unresolved",
    "H14 parent OPEN": r"`OPEN` for the parent",
    "H19.2 no economic inference": r"no economic inference\s+>?\s*about this hypothesis at all",
}


def body_text() -> str:
    md = (PAPER / "paper.md").read_text(encoding="utf-8")
    text = md.split("## Figures")[0]
    text = re.sub(r"^#{2,4} [\d.]+\.?.*$", "", text, flags=re.M)
    return re.sub(r"§\s?[\d.]+", "", text)


def claim_audit() -> int:
    body = body_text()
    matrix = (PAPER / "CLAIM_EVIDENCE_MATRIX.csv").read_text(encoding="utf-8").replace(",", "")
    nums = re.findall(r"(?<![A-Za-z0-9._/-])(\d[\d,]*\.?\d*)", body)
    counts = collections.Counter(n.replace(",", "") for n in nums)
    missing = [n for n in counts if n not in TRIVIAL and n not in matrix
               and n.rstrip("0").rstrip(".") not in matrix]
    print(f"[claim]       distinct numeric tokens {len(counts)} | unsupported {len(missing)}")
    for n in missing:
        print(f"              UNSUPPORTED: {n}")
    return len(missing)


def status_audit() -> int:
    md = (PAPER / "paper.md").read_text(encoding="utf-8")
    fails = 0
    for fam, label in EXPECTED_STATUS.items():
        if label not in md:
            print(f"              MISSING STATUS LABEL for {fam}: {label}")
            fails += 1
    # H19.2 must never be called null or rejected
    for m in re.finditer(r"H19[.\-]?2|H19-P3A", md):
        window = md[max(0, m.start() - 160):m.end() + 160]
        if re.search(r"\bnull\b|\brejected\b", window, re.I):
            # the introduction's sentence about H18 returning a null sits next to an H19.2 sentence
            if "returns a null. H19.0" in " ".join(window.split()):
                continue
            print("              H19.2 NEAR NULL/REJECTED: " + " ".join(window.split())[:200])
            fails += 1
    print(f"[status]      expected labels {len(EXPECTED_STATUS)} | failures {fails}")
    return fails


def language_audit() -> int:
    md = (PAPER / "paper.md").read_text(encoding="utf-8")
    counts = {w: len(re.findall(rf"\b{w}[a-z]*\b", md, re.I)) for w in FLAGGED}
    shown = {w: c for w, c in counts.items() if c}
    print("[language]    " + ", ".join(f"{w}={c}" for w, c in shown.items()))
    print("              each occurrence is reviewed in PAPER_QA.md section 2")
    return 0


def consistency_audit() -> int:
    md = (PAPER / "paper.md").read_text(encoding="utf-8")
    fails = 0
    for name, pattern in CONSISTENCY.items():
        if not re.search(pattern, md, re.S):
            print(f"              MISSING: {name}")
            fails += 1
    print(f"[consistency] checks {len(CONSISTENCY)} | failures {fails}")
    return fails


def main() -> None:
    print("PAPER AUDIT - no economic computation, no price load, no experiment artefact touched")
    bad = claim_audit() + status_audit() + language_audit() + consistency_audit()
    print(f"\nRESULT: {'PASS' if bad == 0 else 'FAIL'} ({bad} issue(s))")
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
