"""Automated text audit of the compiled release PDF.

Extracts the text of every page and fails on the exact defects earlier builds produced, plus the
internal release language that must not reach a reader. Complements, and does not replace, the
page-by-page visual inspection in PDF_QA.md.

Needs a PDF text extractor, which is a QA-only dependency and is not required to build the paper:

    uv run --no-project --with pypdfium2 --python 3.12 python scripts/release_pdf_audit.py
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pypdfium2 as pdfium

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "papers" / "falsification_first_alpha_discovery" / "release" / "paper.pdf"

# Patterns that must NOT appear. Each pins a defect found in a compiled build.
MUST_NOT = {
    "stray backslash before asterisk (RC2 math defect)": re.escape("N" + chr(92)),
    "bare sum subscript, sigma lost (RC2 math defect)": r"(?<!∑)_e\s+I_e",
    "internal release label RC1": r"Release candidate RC1",
    "internal release label RC2": r"Release candidate RC2",
    "internal release label RC3": r"Release candidate RC3",
    "bibliography pointer instead of a bibliography": r"See references\.bib in this directory",
    "unresolved cross-reference": r"\?\?",
    "internal referee acceptance in the paper": r"Referee #4|Referee #2",
    "internal commit hash in the front matter": r"commit c597ba6",
    # Author metadata the author explicitly excluded. The email pattern is generic on purpose: the
    # address itself is never written into source, here or anywhere else in the public package.
    "unresolved author placeholder": r"AUTHOR_METADATA_REQUIRED",
    "any email address": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "employer affiliation (not authorised)": r"Ita[uú]|FIAP",
    "ORCID claim (none exists)": r"ORCID|orcid\.org",
}

# Patterns that MUST appear.
#
# Note on math extraction: text extracted from a PDF reflects the font's character mapping, not the
# source. Correctly typeset mathematics in Computer Modern extracts with substitutions - `\sum`
# comes out as "P", and `^{*}` comes out as U+2217 ASTERISK OPERATOR rather than ASCII "*". The
# patterns below accept those forms deliberately, because rejecting them would flag correct output;
# the glyphs themselves were confirmed by visual inspection and are recorded in PDF_QA.md.
MUST = {
    "set membership in the procedure": re.escape("∈"),
    "summation in the procedure (U+2211, or 'P' as CM extracts it)":
        r"∑|P\s*\n?\s*e\s*\n?\s*I_?e",
    "implied confirmatory sample (ASCII * or U+2217)":
        r"N[*∗⋆]?\s*=\s*10",
    "CEX arrow survives": re.escape("CEX↔DEX"),
    "References heading": r"^\s*References\s*$",
    "a rendered bibliography entry": r"Rubin, D",
    # The authorised byline, exactly. A looser author-shaped pattern would pass a PDF carrying
    # the wrong name, which is the one metadata error that cannot be corrected after publication.
    "authorised author byline": r"Ricardo H\. Ramos Silva",
    "authorised affiliation": r"Independent Researcher",
    "a rendered bibliography author": r"[A-Z][a-z]+,\s[A-Z]\.",
}

FROZEN = {
    "62 candidate events": r"\b62\b",
    "floor 20": r"\b20\b",
    "quantiles 0 0 1 2 57": r"57",
    "52 of 62": r"52 of 62",
    "range 0 to 27": r"0 to 27",
    "median 7": r"median of 7|median 7",
    "3 of 25": r"3 of 25",
    "N_min 40": r"\b40\b",
    "no price read": r"never\s+enter|no price column|price columns loaded",
    "PRE-REGISTERED NULL": r"PRE-REGISTERED NULL",
    "DESIGN INFEASIBLE": r"DESIGN INFEASIBLE UNDER THIS",
    "OPEN": r"\bOPEN\b",
    "IMPLEMENTATION REJECT": r"IMPLEMENTATION\s*REJECT",
    "Figure 4 wording": r"recorded range, not a con.?\s*fidence",
}


def main() -> None:
    doc = pdfium.PdfDocument(str(PDF))
    pages = [doc[i].get_textpage().get_text_range() for i in range(len(doc))]
    text = "\n".join(pages).replace("�", "")   # drop soft-hyphen extraction artefacts
    joined = " ".join(text.split())

    print(f"PDF text audit - {len(doc)} pages, {len(text):,} characters")
    bad = 0

    print("\n[must not appear]")
    for name, pat in MUST_NOT.items():
        hits = len(re.findall(pat, text))
        flag = "FAIL" if hits else "ok  "
        if hits:
            bad += 1
        print(f"  {flag} {hits:>3}  {name}")

    print("\n[must appear]")
    for name, pat in MUST.items():
        hits = len(re.findall(pat, text, re.M))
        flag = "ok  " if hits else "FAIL"
        if not hits:
            bad += 1
        print(f"  {flag} {hits:>3}  {name}")

    print("\n[frozen science, as printed]")
    for name, pat in FROZEN.items():
        hits = len(re.findall(pat, joined, re.S))
        flag = "ok  " if hits else "FAIL"
        if not hits:
            bad += 1
        print(f"  {flag} {hits:>3}  {name}")

    print(f"\nRESULT: {'PASS' if bad == 0 else 'FAIL'} ({bad} issue(s))")
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
