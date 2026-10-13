"""Release-candidate audit: cross-references, LaTeX static validation, bibliography, claims,
scientific-freeze integrity, and the release manifest.

Production only. Reads committed artefacts and the release package. Computes nothing economic,
loads no price, and does not touch V1-V4.

Run: .venv/Scripts/python -I scripts/release_audit.py
"""

from __future__ import annotations

import collections
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "falsification_first_alpha_discovery"
REL = PAPER / "release"

_meta_spec = importlib.util.spec_from_file_location(
    "release_metadata", ROOT / "scripts" / "release_metadata.py")
meta = importlib.util.module_from_spec(_meta_spec)
_meta_spec.loader.exec_module(meta)

# Scientific freeze: the quantities that may not change after acceptance.
FROZEN_QUANTITIES = {
    "candidate events": r"\b62\b",
    "support floor": r"floor \*m\* = 20|m = 20|MIN_CONTROLS",
    "support quantiles": r"p10 0, p25 0, median 1, p75 2, p90 57|\| 0 \| 0 \| \*\*1\*\* \| 2 \| 57 \|",
    "events below floor": r"52 of 62",
    "ceiling range": r"0 to 27|0 and 27",
    "ceiling median": r"median of \*\*7\*\*|median \*\*7\*\*|median of 7",
    "dates reaching floor": r"3 of 25",
    "N star": r"N\\?\* = 10|confirmatory \*\*n of 10\*\*|\*\*10\*\*",
    "N min": r"N_min\* = 40|required 40|minimum of 40",
    "no price loaded": r"never\s+entered memory|no price column",
}

VERDICTS = {
    "H18.3": "`PRE-REGISTERED NULL`",
    "H19.2": "DESIGN INFEASIBLE UNDER THIS SPECIFICATION",
    "H14": "`OPEN`",
    "H13": "IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED",
}

TRIVIAL = set("0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 31 32 40".split()) | {
    str(y) for y in range(2009, 2031)}

# Payload files hashed into the manifest. RELEASE_MANIFEST.json is deliberately absent: a file
# cannot contain its own hash, so it is excluded from its own hash set and counted separately.
MANIFEST_FILES = [
    "paper.md", "paper.tex", "paper.pdf", "references.bib", "CLAIM_EVIDENCE_MATRIX.csv",
    "EVIDENCE_MANIFEST.csv", "REPRODUCIBILITY_APPENDIX.md", "ARTIFACT_INDEX.md", "README.md",
    "BUILD.md", "CHANGELOG.md", "RELEASE_PROVENANCE.md", "RELEASE_QA.md", "RELEASE_QA_RC2.md",
    "DATA_RELEASE_POLICY.md", "PUBLIC_REPO_AUDIT.md", "RELEASE_BLOCKERS.md", "PDF_QA.md",
    "PUBLIC_RELEASE_PLAN.md", "FUTURE_RESEARCH.md", "LICENSE_DECISION.md",
    "LICENSE", "LICENSE-manuscript", "LICENSE-evidence",
    "requirements.txt", "CITATION.cff", "zenodo.json",
]
MANIFEST_DIRS = ["figures", "tables", "evidence", "scripts"]
MANIFEST_EXCLUDED = ["RELEASE_MANIFEST.json"]

fails = 0


def fail(msg: str) -> None:
    global fails
    fails += 1
    print(f"              {msg}")


# ---------------------------------------------------------------------------- freeze
def scientific_freeze() -> None:
    md = (REL / "paper.md").read_text(encoding="utf-8")
    missing = [k for k, pat in FROZEN_QUANTITIES.items() if not re.search(pat, md, re.S)]
    for k in missing:
        fail(f"FROZEN QUANTITY ABSENT: {k}")
    bad_v = [f for f, label in VERDICTS.items() if label not in md]
    for f in bad_v:
        fail(f"VERDICT ABSENT: {f}")
    print(f"[freeze]      quantities {len(FROZEN_QUANTITIES)} missing {len(missing)} | "
          f"verdicts {len(VERDICTS)} missing {len(bad_v)}")


# ---------------------------------------------------------------------------- claims
def claims() -> None:
    md = (REL / "paper.md").read_text(encoding="utf-8").split("## Figures")[0]
    md = re.sub(r"^#{2,4} [\d.]+\.?.*$", "", md, flags=re.M)
    md = re.sub(r"\u00a7\s?[\d.]+", "", md)
    md = re.sub(r"`[^`]*`", " ", md)
    md = re.sub(r"[Ss]ections?\s+[\d.]+(\s*(and|to|-)\s*[\d.]+)?", " ", md)
    md = re.sub(r"\bH\d+(\.\d+)?[a-z]?(\s*[-\u2013]\s*\d+(\.\d+)?)?", " ", md)
    matrix = (REL / "CLAIM_EVIDENCE_MATRIX.csv").read_text(encoding="utf-8").replace(",", "")
    counts = collections.Counter(
        n.replace(",", "") for n in re.findall(r"(?<![A-Za-z0-9._/-])(\d[\d,]*\.?\d*)", md))
    missing = [n for n in counts if n not in TRIVIAL and n not in matrix
               and n.rstrip("0").rstrip(".") not in matrix]
    for n in sorted(missing):
        fail(f"UNSUPPORTED NUMERIC CLAIM: {n}")
    print(f"[claims]      tokens {len(counts)} | unsupported {len(missing)}")


# ---------------------------------------------------------------------------- xrefs
def crossrefs() -> None:
    md = (REL / "paper.md").read_text(encoding="utf-8")
    # Section references must exist as headings.
    headings = set(re.findall(r"^#{2,4} (?:Appendix )?([A-Z]|\d+(?:\.\d+)?)", md, re.M))
    refs = set(re.findall(r"\u00a7(\d+(?:\.\d+)?)", md))
    for r in sorted(refs):
        top = r.split(".")[0]
        if r not in headings and top not in headings:
            fail(f"SECTION REFERENCE WITH NO HEADING: \u00a7{r}")
    app_refs = set(re.findall(r"Appendix ([A-F])\b", md))
    app_heads = set(re.findall(r"^## Appendix ([A-F]) ", md, re.M))
    for a in sorted(app_refs - app_heads):
        fail(f"APPENDIX REFERENCE WITH NO HEADING: Appendix {a}")
    # Removed appendix must not be referenced.
    if re.search(r"Appendix A\.2|Derivative notice coverage", md):
        fail("REFERENCE TO REMOVED APPENDIX A.2")
    # Local file references must exist.
    bad_files = []
    for m in re.findall(r"`((?:figures|tables)/[A-Za-z0-9_./-]+)`", md):
        if not (REL / m).exists():
            bad_files.append(m)
    for m in re.findall(r"!\[\]\(([^)]+)\)", md):
        if not (REL / m).exists():
            bad_files.append(m)
    for b in sorted(set(bad_files)):
        fail(f"FILE REFERENCE MISSING: {b}")
    # Stale current-version references.
    for stale in re.findall(r"`[^`]*_[vV][123][^`]*`", md):
        if "paper_v1" in stale or "paper_v2" in stale or "paper_v3" in stale:
            continue  # deliberate historical provenance
        fail(f"STALE VERSION REFERENCE: {stale}")
    print(f"[xrefs]       section refs {len(refs)} | appendix refs {len(app_refs)} | "
          f"file refs checked")


# ---------------------------------------------------------------------------- latex
def latex_static() -> None:
    tex = (REL / "paper.tex").read_text(encoding="utf-8")
    begins = re.findall(r"\\begin\{(\w+\*?)\}", tex)
    ends = re.findall(r"\\end\{(\w+\*?)\}", tex)
    cb, ce = collections.Counter(begins), collections.Counter(ends)
    for env in set(cb) | set(ce):
        if cb[env] != ce[env]:
            fail(f"UNBALANCED LATEX ENVIRONMENT: {env} begin={cb[env]} end={ce[env]}")
    if tex.count("{") != tex.count("}"):
        fail(f"UNBALANCED BRACES: {{={tex.count('{')} }}={tex.count('}')}")
    if "\\documentclass" not in tex or "\\end{document}" not in tex:
        fail("LATEX SKELETON INCOMPLETE")
    # Every includegraphics target must exist.
    for g in re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]+)\}", tex):
        if not (REL / g).exists():
            fail(f"INCLUDEGRAPHICS TARGET MISSING: {g}")
    # Unescaped specials outside math/verbatim are the common build killer.
    # Strip what is legitimately present before looking for stray specials: escaped specials,
    # texttt spans, LaTeX comment lines, and tabular bodies where & is the column separator.
    stripped = re.sub(r"\\[%&#_$]", "", tex)
    stripped = re.sub(r"\\texttt\{[^}]*\}", "", stripped)
    stripped = re.sub(r"^%%.*$", "", stripped, flags=re.M)
    for env in ("tabular", "longtable"):
        stripped = re.sub(r"\\begin\{" + env + r"\}.*?\\end\{" + env + r"\}", "", stripped,
                          flags=re.S)
    for ch in ("%", "&", "#"):
        bad = [m.start() for m in re.finditer(re.escape(ch), stripped)]
        if bad:
            fail(f"POSSIBLE UNESCAPED '{ch}' x{len(bad)} (first at char {bad[0]})")
    pkgs = re.findall(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}", tex)
    print(f"[latex]       environments balanced | packages: {', '.join(pkgs)}")


# ---------------------------------------------------------------------------- bibtex
def bibtex() -> None:
    bib = (REL / "references.bib").read_text(encoding="utf-8")
    entries = re.findall(r"@(\w+)\{([^,]+),", bib)
    keys = [k.strip() for _, k in entries]
    dupes = [k for k, c in collections.Counter(keys).items() if c > 1]
    for d in dupes:
        fail(f"DUPLICATE BIBTEX KEY: {d}")
    if bib.count("{") != bib.count("}"):
        fail("UNBALANCED BRACES IN BIBTEX")
    no_title = [k for _, k in entries if not re.search(
        r"@\w+\{" + re.escape(k) + r",[^@]*?title\s*=", bib, re.S)]
    for k in no_title:
        fail(f"BIBTEX ENTRY WITHOUT TITLE: {k}")
    no_note = [k for _, k in entries if not re.search(
        r"@\w+\{" + re.escape(k) + r",[^@]*?note\s*=", bib, re.S)]
    for k in no_note:
        fail(f"BIBTEX ENTRY WITHOUT ACCESS-LEVEL NOTE: {k}")
    print(f"[bibtex]      entries {len(entries)} | duplicate keys {len(dupes)} | "
          f"missing notes {len(no_note)}")


# ---------------------------------------------------------------------------- manifest
def manifest() -> None:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    entries = {}
    for name in MANIFEST_FILES:
        f = REL / name
        if f.exists():
            entries[name] = {"sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                             "bytes": f.stat().st_size}
    for sub in MANIFEST_DIRS:
        d = REL / sub
        if not d.exists():
            continue
        for f in sorted(d.rglob("*")):
            if f.is_file():
                rel = f.relative_to(REL).as_posix()
                entries[rel] = {"sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                                "bytes": f.stat().st_size}
    pdf = REL / "paper.pdf"
    package_total = len(entries) + len(MANIFEST_EXCLUDED)
    doc = {
        "release": meta.RELEASE_VERSION,
        "title": meta.TITLE,
        "author": {
            "name": meta.AUTHOR,
            "affiliation": meta.AFFILIATION,
            "orcid": meta.ORCID,
            "correspondence": meta.CORRESPONDENCE,
            "note": ("Authorised by the author for publication. No employer or university "
                     "affiliation is stated and no institutional endorsement is implied; no ORCID "
                     "and no correspondence address were provided, and neither is invented."),
        },
        "release_date": meta.RELEASE_DATE_ISO,
        "counts": {
            "package_files_total": package_total,
            "payload_files_hashed": len(entries),
            "manifest_excluded_from_its_own_hash_set": MANIFEST_EXCLUDED,
            "note": ("package_files_total = payload_files_hashed + the manifest itself. "
                     "RELEASE_MANIFEST.json is not hashed here because a file cannot contain "
                     "its own hash."),
        },
        "built_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_commit": commit,
        "scientific_source": {
            "version": "V4",
            "file": "v4/paper_v4.md",
            "sha256": hashlib.sha256((PAPER / "v4" / "paper_v4.md").read_bytes()).hexdigest(),
            "accepted_by": "REFEREE_REPORT_V4.md (ACCEPT)",
        },
        "scientific_freeze_sha256":
            hashlib.sha256((PAPER / "SCIENTIFIC_FREEZE.md").read_bytes()).hexdigest(),
        "environment": {
            "python": sys.version.split()[0],
            "latex_engine": meta.LATEX_ENGINE if pdf.exists() else None,
            "pdf_built": pdf.exists(),
        },
        "files": entries,
    }
    (REL / "RELEASE_MANIFEST.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"[manifest]    package {package_total} files = {len(entries)} payload hashed "
          f"+ 1 manifest (excluded from its own hash set) | pdf_built={pdf.exists()}")


def main() -> None:
    print("RELEASE AUDIT - production only; no experiment, no price, no V1-V4 file touched")
    scientific_freeze()
    claims()
    crossrefs()
    latex_static()
    bibtex()
    manifest()
    print(f"\nRESULT: {'PASS' if fails == 0 else 'FAIL'} ({fails} issue(s))")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    main()
