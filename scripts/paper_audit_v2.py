"""Audit paper V2 and verify that V1 is still byte-identical to its freeze hashes.

Reads only manuscripts and evidence files. Computes nothing economic, loads no price, touches no
experiment artefact. Exits non-zero on any failure.

Run: .venv/Scripts/python -I scripts/paper_audit_v2.py
"""

from __future__ import annotations

import collections
import hashlib
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "falsification_first_alpha_discovery"
V2 = PAPER / "v2"

V1_FROZEN = {
    "paper.md": "1853bce01e638da159733ab61fd3d4945ba51a160d3ddc156ab26fa57da95cef",
    "paper.tex": "2abad0f88b468ea542ef32d838539c7c29b8d5683a907f96cb56b2328d0d97e7",
    "CLAIM_EVIDENCE_MATRIX.csv": "a1b97453ada9f3397f317f6b3e15d720ff5791c60896e37fea0539d8e98cb781",
    "PAPER_QA.md": "357c25b9490e109d08af8092f1b0079ab91529b1b21cf26e60d206eaef8fe9be",
    "REPRODUCIBILITY_APPENDIX.md":
        "6ea8edaa0a94f9c989f206229ac386b47c548cbd61938a08ef70e291c72adcff",
}

TRIVIAL = set("0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 31 32".split()) | {
    str(y) for y in range(2009, 2031)}

FLAGGED = ["prove", "proved", "proves", "proven", "obvious", "obviously", "clearly", "always",
           "never", "guaranteed", "caused", "causes", "insider", "profitab", "alpha",
           "demonstrat", "feasible for small capital"]

# Verdict labels that must appear verbatim and must not be altered from V1.
EXPECTED_STATUS = {
    "H18.3": "`PRE-REGISTERED NULL`",
    "H19.0": "`PARTIAL PASS`",
    "H19.2": "`BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL`",
    "H14 parent": "`OPEN`",
    "H13": "IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED",
}

# Statements the referee required V2 to carry.
REQUIRED = {
    "retrospective case selection disclosed":
        r"selected retrospectively for methodological[\s>]*informativeness",
    "hypothesis vs case selection distinguished":
        r"different processes",
    "governance split 2A present": r"2A\. Rules in force at the start",
    "governance split 2B present": r"2B\. Rules added after a specific failure",
    "governance trajectory headline": r"became progressively more falsification-first",
    "NULL means failed criteria": r"pre-registered support criteria[\s>*]*were not met",
    "absence of effect not demonstrated": r"[Aa]bsence of effect is not demonstrated",
    "coarse liquidity screen wording": r"coarse volume-based liquidity screen",
    "execution ingredients listed": r"order book, the spread, market impact",
    "common support claim bounded":
        r"not[\s>*]*claim that covariate adjustment cannot establish common support",
    "alternatives acknowledged and not executed": r"not executed",
    "no-price guarantee subsection": r"Structural outcome blinding",
    "threshold table present": r"ENGINEERING JUDGEMENT",
    "threshold sensitivity unmeasured": r"[Tt]hreshold sensitivity remains unmeasured",
    "pre-specification caveat": r"does not make an[\s>]*arbitrary threshold theoretically correct",
    "full denominator table": r"All families, H1 to H19\.2",
    "terminal state counts": r"Terminal-state distribution",
    "denominator cuts against thesis": r"is not supported by\s*\n?this registry",
    "H8 archival reported": r"did not clear the return hurdle",
    "leakage claim narrowed": r"not\*\* a new leakage category",
    "framework falsifiability": r"What would falsify this framework",
    "independent check named": r"cheapest independent check",
    "dependence channels named": r"batch announcements",
    "principles conditional marked": r"`CONDITIONAL`",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def v1_integrity() -> int:
    bad = 0
    for name, want in V1_FROZEN.items():
        got = sha(PAPER / name)
        if got != want:
            print(f"              *** V1 HASH CHANGED: {name}\n                  want {want}\n"
                  f"                  got  {got}")
            bad += 1
    print(f"[v1 freeze]   files {len(V1_FROZEN)} | changed {bad}")
    return bad


def body(md: Path) -> str:
    """Manuscript body with the apparatus stripped.

    Removed before extracting numeric claims, because none of these is a claim about the world:
    headings, section cross-references, inline code spans (commit hashes, field names, file names)
    and the V1 hash prefix in the version note.
    """
    text = md.read_text(encoding="utf-8").split("## Figures and tables")[0]
    text = re.sub(r"^#{2,4} [\d.]+\.?.*$", "", text, flags=re.M)
    text = re.sub(r"§\s?[\d.]+", "", text)
    text = re.sub(r"`[^`]*`", " ", text)                      # commit hashes, fields, filenames
    text = re.sub(r"[Ss]ections?\s+[\d.]+(\s*(and|to|-)\s*[\d.]+)?", " ", text)
    text = re.sub(r"H\d+(\.\d+)?[a-z]?(\s*[-–]\s*\d+(\.\d+)?)?", " ", text)
    return text


def claim_audit() -> int:
    text = body(V2 / "paper_v2.md")
    matrix = (V2 / "CLAIM_EVIDENCE_MATRIX_V2.csv").read_text(encoding="utf-8").replace(",", "")
    counts = collections.Counter(
        n.replace(",", "") for n in re.findall(r"(?<![A-Za-z0-9._/-])(\d[\d,]*\.?\d*)", text))
    missing = [n for n in counts if n not in TRIVIAL and n not in matrix
               and n.rstrip("0").rstrip(".") not in matrix]
    print(f"[claim]       distinct numeric tokens {len(counts)} | unsupported {len(missing)}")
    for n in sorted(missing):
        m = re.search(r".{0,70}" + re.escape(n) + r".{0,40}", text, re.S)
        print(f"              UNSUPPORTED {n} :: {' '.join(m.group(0).split()) if m else ''}")
    return len(missing)


def status_audit() -> int:
    md = (V2 / "paper_v2.md").read_text(encoding="utf-8")
    bad = 0
    for fam, label in EXPECTED_STATUS.items():
        if label not in md:
            print(f"              MISSING VERDICT LABEL for {fam}: {label}")
            bad += 1
    for m in re.finditer(r"H19[.\-]?2|H19-P3A", md):
        w = " ".join(md[max(0, m.start() - 170):m.end() + 170].split())
        if re.search(r"\bnull\b|\brejected\b", w, re.I) and "it is not a null" not in w:
            print(f"              H19.2 NEAR NULL/REJECTED: {w[:200]}")
            bad += 1
    print(f"[status]      labels {len(EXPECTED_STATUS)} | failures {bad}")
    return bad


def required_audit() -> int:
    md = (V2 / "paper_v2.md").read_text(encoding="utf-8")
    bad = 0
    for name, pat in REQUIRED.items():
        if not re.search(pat, md, re.S):
            print(f"              MISSING: {name}")
            bad += 1
    print(f"[must-fix]    checks {len(REQUIRED)} | failures {bad}")
    return bad


def language_audit() -> int:
    md = (V2 / "paper_v2.md").read_text(encoding="utf-8")
    counts = {w: len(re.findall(rf"\b{w}[a-z]*\b", md, re.I)) for w in FLAGGED}
    print("[language]    " + ", ".join(f"{w}={c}" for w, c in counts.items() if c))
    banned = counts["feasible for small capital"]
    if banned:
        print(f"              *** V1 wording survives {banned} time(s)")
    return banned


def literature_audit() -> int:
    bib = (V2 / "references_v2.bib").read_text(encoding="utf-8")
    entries = [e for e in re.split(r"\n(?=@)", bib) if e.strip().startswith("@")]
    no_access = [e for e in entries if "note" not in e or not re.search(
        r"[Aa]ccess|full|[Rr]etrieved|read|level|not recorded", e)]
    print(f"[literature]  entries {len(entries)} | without an access statement {len(no_access)}")
    for e in no_access:
        print("              NO ACCESS LEVEL: " + re.search(r"@\w+\{([^,]+)", e).group(1))
    return len(no_access)


def main() -> None:
    print("PAPER V2 AUDIT - no economic computation, no price load, no experiment artefact touched")
    v1bad = v1_integrity()
    if v1bad:
        print("\nSTOP: V1 is no longer byte-identical to its freeze. Nothing else was checked.")
        sys.exit(2)
    bad = claim_audit() + status_audit() + required_audit() + language_audit() + literature_audit()
    print(f"\nRESULT: {'PASS' if bad == 0 else 'FAIL'} ({bad} issue(s))")
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
