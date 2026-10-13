"""Per-page geometry QA of the compiled release PDF: margin ink, blank pages, page renders.

This complements scripts/release_pdf_audit.py, which audits the extracted *text*. Text extraction
cannot see a table running off the page or a legend colliding with a page number, so every page is
also rasterised and checked for ink inside a margin band. The check is mechanical and detects ink in
the band and blank pages; it cannot judge typographic quality, which is why selected pages are also
written out for inspection by eye.

QA-only dependencies, deliberately not project dependencies - building the paper needs neither:

    uv run --no-project --with pypdfium2 --with pillow --python 3.12 python -I \
        scripts/release_pdf_pages.py [--render 1,2,21 --out DIR]

Exit code is non-zero if any page has margin ink or is blank.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import pypdfium2 as pdfium

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "papers" / "falsification_first_alpha_discovery" / "release" / "paper.pdf"

# Fraction of each edge treated as the forbidden band. The document's smallest margin is the
# geometry package default, well outside this band, so ink here means something overflowed.
BAND = 0.025
# A pixel counts as ink below this luminance; anti-aliasing of a glyph edge lands far below it.
INK_LEVEL = 200
# Pages with fewer dark pixels than this are treated as blank. A single stray mark is not a page.
BLANK_MAX_INK = 40
SCALE = 2.0   # ~144 dpi: enough to resolve a hairline rule without large rasters


def analyse(render: list[int], out: Path | None) -> int:
    doc = pdfium.PdfDocument(str(PDF))
    n = len(doc)
    print(f"{PDF.name}: {n} pages, {PDF.stat().st_size:,} bytes")
    print(f"margin band {BAND:.1%} of each edge | ink threshold {INK_LEVEL} | scale {SCALE}x\n")

    margin_pages: list[int] = []
    blank_pages: list[int] = []

    for i in range(n):
        img = doc[i].render(scale=SCALE).to_pil().convert("L")
        w, h = img.size
        bw, bh = max(1, int(w * BAND)), max(1, int(h * BAND))
        px = img.load()

        total_ink = 0
        band_ink = 0
        for y in range(h):
            in_band_row = y < bh or y >= h - bh
            for x in range(w):
                if px[x, y] < INK_LEVEL:
                    total_ink += 1
                    if in_band_row or x < bw or x >= w - bw:
                        band_ink += 1

        page = i + 1
        if band_ink:
            margin_pages.append(page)
        if total_ink < BLANK_MAX_INK:
            blank_pages.append(page)
        flag = "MARGIN" if band_ink else ("BLANK" if total_ink < BLANK_MAX_INK else "ok    ")
        print(f"  {flag} page {page:>3}  ink {total_ink:>8,}  band {band_ink:>6,}")

        if page in render and out is not None:
            out.mkdir(parents=True, exist_ok=True)
            doc[i].render(scale=SCALE).to_pil().save(out / f"page_{page:02d}.png")

    print(f"\npages with margin ink: {len(margin_pages)} of {n}"
          + (f" -> {margin_pages}" if margin_pages else ""))
    print(f"blank pages:           {len(blank_pages)} of {n}"
          + (f" -> {blank_pages}" if blank_pages else ""))
    if render and out is not None:
        print(f"rendered {len(render)} page(s) to {out}")

    issues = len(margin_pages) + len(blank_pages)
    print(f"\nRESULT: {'PASS' if issues == 0 else 'FAIL'} ({issues} issue(s))")
    return issues


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--render", default="", help="comma-separated 1-based page numbers to rasterise")
    ap.add_argument("--out", default="", help="directory for the rendered pages")
    a = ap.parse_args()
    pages = [int(x) for x in a.render.split(",") if x.strip()]
    out = Path(a.out) if a.out else None
    if pages and out is None:
        ap.error("--render needs --out")
    sys.exit(1 if analyse(pages, out) else 0)


if __name__ == "__main__":
    main()
