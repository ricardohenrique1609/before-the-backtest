"""Audit paper V3, and verify that V1 and V2 are still byte-identical to their freezes.

Reads only manuscripts and evidence files. Computes nothing economic, loads no price, touches no
experiment artefact. Exits 2 if a frozen hash moved, 1 on any other failure.

Run: .venv/Scripts/python -I scripts/paper_audit_v3.py
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
V3 = PAPER / "v3"

FROZEN = {
    "paper.md": "1853bce01e638da159733ab61fd3d4945ba51a160d3ddc156ab26fa57da95cef",
    "paper.tex": "2abad0f88b468ea542ef32d838539c7c29b8d5683a907f96cb56b2328d0d97e7",
    "CLAIM_EVIDENCE_MATRIX.csv": "a1b97453ada9f3397f317f6b3e15d720ff5791c60896e37fea0539d8e98cb781",
    "PAPER_QA.md": "357c25b9490e109d08af8092f1b0079ab91529b1b21cf26e60d206eaef8fe9be",
    "REPRODUCIBILITY_APPENDIX.md":
        "6ea8edaa0a94f9c989f206229ac386b47c548cbd61938a08ef70e291c72adcff",
    "v2/paper_v2.md": "b2c3ddaed36fd7371a16cf9f5b75c39272dbd38edc10a482d114c9a187bfd157",
    "v2/paper_v2.tex": "ad18523888093b1cc54956babea531581edcac1000243fc6b42ec2eb0b7a9cbd",
    "v2/CLAIM_EVIDENCE_MATRIX_V2.csv":
        "47d22e1e1abd7669f4cd68c852ac41751461caba2ad395df3a7463a275afbd7f",
    "v2/references_v2.bib": "543d467791d55fe734334fd107f91ab143bb00d02b1ac1a3b36b47418e9b298c",
    "v2/PAPER_QA_V2.md": "7bf5cae957da8f2108dd59057d23e81a8d88a5e7de5f8e321885c89da5958273",
}

TRIVIAL = set("0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 31 32 40".split()) | {
    str(y) for y in range(2009, 2031)}

# Broad phrases that must not survive the V3 narrowing, or must be bounded where they appear.
BROAD = ["alpha discovery", "manufacture", "usually", "typical", "most quant", "improves returns",
         "framework proves", "feasible for small capital", "almost never"]

VERDICTS = {
    "H18.3": "`PRE-REGISTERED NULL`",
    "H19.2": "DESIGN INFEASIBLE UNDER THIS SPECIFICATION",
    "H14 parent": "`OPEN`",
    "H13": "IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED",
}

REQUIRED = {
    "single contribution in abstract": r"pre-freeze common-support ceiling",
    "single contribution in intro": r"The \*\*contribution\*\* is the pre-freeze common-support",
    "single contribution in conclusion":
        r"Identification feasibility is itself a pre-analysis empirical object",
    "novelty bounded, no 'first'": r"We are not aware of prior work that operationalises",
    "Rubin credited": r"Rubin \(2008\)",
    "design-stage principle disclaimed": r"the principle is Rubin's|is Rubin's\.",
    "positivity not claimed": r"We do \*\*not\*\* claim",
    "domain stated": r"### 1\.4 Domain",
    "procedure box": r"PROCEDURE — PRE-FREEZE COMMON-SUPPORT AUDIT",
    "stop status not a null": r"not a null result, not a rejected hypothesis",
    "structural blinding": r"outcome-blind design failure",
    "usecols evidence": r"usecols=\[0, 5, 7, 8\]",
    "registry 31 entries": r"registry contains \*\*31 entries\*\*",
    "nine economic rejects": r"economic reject, with an economic quantity computed \| \*\*9\*\*",
    "denominator does not support broad thesis":
        r"denominator does not support a broad thesis",
    "retrospective selection": r"selected retrospectively for methodological",
    "liquidity distribution reported": r"≤ 0.10%",
    "liquidity screen not feasibility": r"This is a screen, not an execution analysis",
    "base-rate paragraph": r"On the base-rate shift",
    "estimand not invalidated": r"does not invalidate the definition of the\s+estimand",
    "threshold sensitivity unmeasured": r"[Tt]hreshold sensitivity is unmeasured",
    "protocol self-critique in limitations":
        r"The protocol itself is not empirically validated",
    "four principles only": r"\*\*P4\.\*\* Failure at a pre-outcome design gate",
    "independent check named": r"cheapest independent check",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def frozen_integrity() -> int:
    bad = 0
    for name, want in FROZEN.items():
        got = sha(PAPER / name)
        if got != want:
            print(f"              *** FROZEN HASH CHANGED: {name}")
            bad += 1
    print(f"[freezes]     V1+V2 files {len(FROZEN)} | changed {bad}")
    return bad


def body() -> str:
    text = (V3 / "paper_v3.md").read_text(encoding="utf-8").split("## Figures")[0]
    text = re.sub(r"^#{2,4} [\d.]+\.?.*$", "", text, flags=re.M)
    text = re.sub(r"§\s?[\d.]+", "", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"[Ss]ections?\s+[\d.]+(\s*(and|to|-)\s*[\d.]+)?", " ", text)
    return re.sub(r"\bH\d+(\.\d+)?[a-z]?(\s*[-–]\s*\d+(\.\d+)?)?", " ", text)


def claim_audit() -> int:
    text = body()
    matrix = (V3 / "CLAIM_EVIDENCE_MATRIX_V3.csv").read_text(encoding="utf-8").replace(",", "")
    counts = collections.Counter(
        n.replace(",", "") for n in re.findall(r"(?<![A-Za-z0-9._/-])(\d[\d,]*\.?\d*)", text))
    missing = [n for n in counts if n not in TRIVIAL and n not in matrix
               and n.rstrip("0").rstrip(".") not in matrix]
    print(f"[claim]       distinct numeric tokens {len(counts)} | unsupported {len(missing)}")
    for n in sorted(missing):
        m = re.search(r".{0,70}" + re.escape(n) + r".{0,40}", text, re.S)
        print(f"              UNSUPPORTED {n} :: {' '.join(m.group(0).split()) if m else ''}")
    return len(missing)


def required_audit() -> int:
    md = (V3 / "paper_v3.md").read_text(encoding="utf-8")
    bad = 0
    for name, pat in REQUIRED.items():
        if not re.search(pat, md, re.S):
            print(f"              MISSING: {name}")
            bad += 1
    print(f"[required]    checks {len(REQUIRED)} | failures {bad}")
    return bad


def verdict_audit() -> int:
    md = (V3 / "paper_v3.md").read_text(encoding="utf-8")
    bad = 0
    for fam, label in VERDICTS.items():
        if label not in md:
            print(f"              MISSING VERDICT for {fam}: {label}")
            bad += 1
    print(f"[verdicts]    labels {len(VERDICTS)} | failures {bad}")
    return bad


def breadth_audit() -> int:
    md = (V3 / "paper_v3.md").read_text(encoding="utf-8").lower()
    hits = {p: md.count(p) for p in BROAD if md.count(p)}
    print("[breadth]     " + (", ".join(f"{k}={v}" for k, v in hits.items()) or "none found"))
    # 'usually' and 'typical' are allowed only in a negated/bounded construction; flag for review.
    banned = sum(md.count(p) for p in ("feasible for small capital", "alpha discovery",
                                       "framework proves", "improves returns"))
    if banned:
        print(f"              *** banned broad phrasing present {banned} time(s)")
    return banned


def wordcount() -> int:
    md = (V3 / "paper_v3.md").read_text(encoding="utf-8")
    b = len(md.split("## Figures")[0].split())
    print(f"[length]      body {b:,} words | total {len(md.split()):,} words")
    return 0


def main() -> None:
    print("PAPER V3 AUDIT - no economic computation, no price load, no experiment artefact touched")
    if frozen_integrity():
        print("\nSTOP: a frozen V1/V2 file changed. Nothing else was checked.")
        sys.exit(2)
    bad = (claim_audit() + required_audit() + verdict_audit() + breadth_audit() + wordcount())
    print(f"\nRESULT: {'PASS' if bad == 0 else 'FAIL'} ({bad} issue(s))")
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
