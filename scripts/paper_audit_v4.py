"""Audit paper V4, and verify that V1, V2 and V3 are still byte-identical to their freezes.

Reads only manuscripts and evidence files. Computes nothing economic, loads no price, touches no
experiment artefact. Exits 2 if a frozen hash moved, 1 on any other failure.

Run: .venv/Scripts/python -I scripts/paper_audit_v4.py
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
V4 = PAPER / "v4"

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
    "v3/paper_v3.md": "5f5468eb80e44fba50b8fb240e526b346f536f76d4ee900b6149ad1cb28cc547",
    "v3/paper_v3.tex": "668387d707d579506424c5fa9c8c1bf4880b88cc81a8dd8577dddd17197b69a6",
    "v3/CLAIM_EVIDENCE_MATRIX_V3.csv":
        "39eb3cfb7c0c3713d62e5037576c4033a9858436d96022247c134616745a85b0",
    "v3/references_v3.bib": "dd98e55260855990a6e105a0ed125e3ed5a169bb02ca3cdccac345d73815c11f",
    "v3/PAPER_QA_V3.md": "b37436d944fa05520e952812c6999ec96034a36eb3b3bdc3964fcf8d5a016470",
    "v3/REFEREE_REPORT_V3.md": "373ee752ba7ea156eb5c6e7222fa1e4296796f42863ffe16df0571ddfb67295e",
}

TRIVIAL = set("0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 31 32 40".split()) | {
    str(y) for y in range(2009, 2031)}

BANNED = ["alpha discovery", "feasible for small capital", "framework proves", "improves returns",
          "first pre-freeze", "unprecedented", "pre-model failure is usually",
          "typically fails upstream"]

NOVELTY_WORDS = ["novel", "novelty", "first", "new method", "new principle", "unique",
                 "unprecedented", "contribution"]

VERDICTS = {
    "H18.3": "`PRE-REGISTERED NULL`",
    "H19.2": "DESIGN INFEASIBLE UNDER THIS SPECIFICATION",
    "H14 parent": "`OPEN`",
    "H13": "IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED",
}

# The five mandatory referee-V3 changes, plus the optional sixth, each checked verbatim.
REQUIRED = {
    "R1 N_min extension": r"any admissible confirmatory minimum[\s*]*\*?N_min\*?\s*>\s*15",
    "R1 bound is not a sensitivity analysis": r"it is not a[\s*>]*sensitivity analysis",
    "R1 what the bound excludes": r"establishes \*\*nothing\*\*",
    "R2 detection not specificity": r"evidence here concerns detection, not specificity",
    "R2 no feasible-case control": r"no case reported in this paper",
    "R2 registry is not a control": r"reading their outcomes as negative",
    "R2 echoed in limitations": r"One demonstration; specificity unmeasured",
    "R3 matching rule ranked largest": r"largest remaining unmeasured design\s*>?\s*sensitivity is the matching rule",
    "R3 specification not question": r"does \*\*not\*\*[\s>]*establish that this question cannot be identified",
    "R4 figure 4 not an interval": r"recorded range, not a confidence\s*\n?interval",
    "R4 figure 4 counts": r"8 of the 25 announcement dates have[\s*]*\n?\*?\*?individually persisted values",
    "R5 appendix A.2 removed": r"^(?!.*Derivative notice coverage).*$",
    "R6 base-rate compressed in body": r"The detail is in Appendix F",
    "R6 base-rate detail in appendix": r"## Appendix F — The base-rate shift",
    # carried invariants
    "single contribution in abstract": r"pre-freeze common-support ceiling",
    "Rubin credited": r"Rubin \(2008\)",
    "design-stage principle disclaimed": r"is Rubin's",
    "novelty bounded, no 'first'": r"We are not aware of prior work that operationalises",
    "novelty fallback preserved": r"the contribution reduces to the §4 demonstration|contribution of this paper reduces to the empirical demonstration",
    "registry 31 entries": r"registry contains \*\*31 entries\*\*",
    "nine economic rejects": r"economic reject, with an economic quantity computed \| \*\*9\*\*",
    "promotion archived": r"did not clear the return hurdle|subsequently archived",
    "procedure not prevalence": r"a claim about a \*\*procedure\*\*, not about a prevalence",
    "retrospective selection": r"selected retrospectively for methodological",
    "stop status not a null": r"not a null result, not a rejected hypothesis",
    "usecols evidence": r"usecols=\[0, 5, 7, 8\]",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def frozen_integrity() -> int:
    bad = 0
    for name, want in FROZEN.items():
        if sha(PAPER / name) != want:
            print(f"              *** FROZEN HASH CHANGED: {name}")
            bad += 1
    print(f"[freezes]     V1+V2+V3 files {len(FROZEN)} | changed {bad}")
    return bad


def body() -> str:
    text = (V4 / "paper_v4.md").read_text(encoding="utf-8").split("## Figures")[0]
    text = re.sub(r"^#{2,4} [\d.]+\.?.*$", "", text, flags=re.M)
    text = re.sub(r"§\s?[\d.]+", "", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"[Ss]ections?\s+[\d.]+(\s*(and|to|-)\s*[\d.]+)?", " ", text)
    return re.sub(r"\bH\d+(\.\d+)?[a-z]?(\s*[-–]\s*\d+(\.\d+)?)?", " ", text)


def claim_audit() -> int:
    text = body()
    matrix = (V4 / "CLAIM_EVIDENCE_MATRIX_V4.csv").read_text(encoding="utf-8").replace(",", "")
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
    md = (V4 / "paper_v4.md").read_text(encoding="utf-8")
    bad = 0
    for name, pat in REQUIRED.items():
        if name == "R5 appendix A.2 removed":
            if "Derivative notice coverage" in md:
                print("              MISSING: R5 appendix A.2 removed (still present)")
                bad += 1
            continue
        if not re.search(pat, md, re.S):
            print(f"              MISSING: {name}")
            bad += 1
    print(f"[required]    checks {len(REQUIRED)} | failures {bad}")
    return bad


def verdict_audit() -> int:
    md = (V4 / "paper_v4.md").read_text(encoding="utf-8")
    bad = 0
    for fam, label in VERDICTS.items():
        if label not in md:
            print(f"              MISSING VERDICT for {fam}: {label}")
            bad += 1
    print(f"[verdicts]    labels {len(VERDICTS)} | failures {bad}")
    return bad


def novelty_audit() -> int:
    md = (V4 / "paper_v4.md").read_text(encoding="utf-8").lower()
    counts = {w: md.count(w) for w in NOVELTY_WORDS if md.count(w)}
    print("[novelty]     " + ", ".join(f"{w}={c}" for w, c in counts.items()))
    banned = sum(md.count(p) for p in BANNED)
    if banned:
        for p in BANNED:
            if md.count(p):
                print(f"              *** BANNED PHRASE: '{p}' x{md.count(p)}")
    return banned


def wordcount() -> int:
    md = (V4 / "paper_v4.md").read_text(encoding="utf-8")
    b = len(md.split("## Figures")[0].split())
    ok = 6800 <= b <= 7400
    print(f"[length]      body {b:,} words | target 6,800-7,400 | {'in range' if ok else 'OUT OF RANGE'}")
    return 0 if ok else 1


def main() -> None:
    print("PAPER V4 AUDIT - no economic computation, no price load, no experiment artefact touched")
    if frozen_integrity():
        print("\nSTOP: a frozen V1/V2/V3 file changed. Nothing else was checked.")
        sys.exit(2)
    bad = (claim_audit() + required_audit() + verdict_audit() + novelty_audit() + wordcount())
    print(f"\nRESULT: {'PASS' if bad == 0 else 'FAIL'} ({bad} issue(s))")
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
