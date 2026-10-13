"""Release candidate build: Figure 4 layout fix and paper.tex generation.

Production only. The plotted values are byte-identical to those V4 used; only the legend placement
changes, per referee V4's layout note. Nothing is recomputed, no price is loaded, and no V1-V4 file
is touched.

Run: .venv/Scripts/python -I scripts/release_build.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "falsification_first_alpha_discovery"
REL = PAPER / "release"
FIG = REL / "figures"

_spec = importlib.util.spec_from_file_location("v1fig", ROOT / "scripts" / "paper_build_figures.py")
v1fig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1fig)
INK, MUTED, NEUTRAL, FAIL_C = v1fig.INK, v1fig.MUTED, v1fig.NEUTRAL, v1fig.FAIL_C


def f4_legend_fix() -> None:
    """Same values as V4; legend moved clear of the hatched band and the top marker."""
    txt = (ROOT / "H19_2_PREFREEZE_FEASIBILITY.md").read_text(encoding="utf-8", errors="replace")
    rows = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in v1fig.CEILING_RE.finditer(txt)]
    dates = [r[0] for r in rows]
    warned = [r[2] for r in rows]

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    fig.subplots_adjust(bottom=0.40, top=0.86)

    ax.axhspan(0, 27, facecolor="none", edgecolor=MUTED, hatch="///", linewidth=0.8, zorder=0,
               label="recorded range 0-27 (NOT a confidence interval)")
    ax.axhline(7, color=NEUTRAL, linestyle="-", linewidth=1.2,
               label="median across all 25 dates = 7")
    ax.axhline(20, color=INK, linestyle="--", linewidth=1.0, label="pre-registered floor m = 20")
    ax.plot(dates, warned, marker="o", markersize=5.5, color=FAIL_C, linestyle="none",
            label="8 of 25 dates with individually persisted values")
    for d, t in zip(dates, warned, strict=True):
        ax.annotate(str(t), (d, t), textcoords="offset points", xytext=(0, 6), ha="center",
                    fontsize=6.9, color=INK)

    ax.set_xticks(dates)
    ax.set_xticklabels([d[:7] for d in dates], rotation=60, fontsize=6.8)
    ax.set_ylim(0, 31)
    ax.set_ylabel("warned assets eligible as controls")
    # Legend below the axis, clear of the hatched band and of the marker at 27.
    ax.legend(fontsize=6.9, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.30),
              ncol=1, handletextpad=0.8)
    ax.set_title("Full-pool ceiling: recorded range, not a confidence interval\n"
                 "17 dates are not individually persisted and are not plotted or interpolated",
                 fontsize=8.6, loc="left")
    fig.savefig(FIG / "f4_full_pool_ceiling.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "f4_full_pool_ceiling.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote f4_full_pool_ceiling (values identical to V4; legend moved below the axis)")


_meta_spec = importlib.util.spec_from_file_location(
    "release_metadata", ROOT / "scripts" / "release_metadata.py")
meta = importlib.util.module_from_spec(_meta_spec)
_meta_spec.loader.exec_module(meta)

# The release metadata - title, byline, cover date, keywords - lives in one module so that the
# author's name has a single canonical representation everywhere it is printed or recorded.
RELEASE_DATE = meta.RELEASE_DATE
TITLE = meta.TITLE
SUBJECT = meta.SUBJECT
KEYWORDS = meta.KEYWORDS
AUTHOR = meta.AUTHOR
AFFILIATION = meta.AFFILIATION


def latex() -> None:
    """Generate release/paper.tex with the release converter.

    The release converter is separate from scripts/paper_md_to_tex.py so that regenerating the
    frozen V1-V4 .tex files stays byte-exact. It owns inline mathematics, list continuation, lists
    inside block quotes, page-breaking long tables and Unicode mapping - typesetting only.
    """
    spec = importlib.util.spec_from_file_location(
        "release_md2tex", ROOT / "scripts" / "release_md_to_tex.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    tex = m.convert((REL / "paper.md").read_text(encoding="utf-8"),
                    date=RELEASE_DATE, title=TITLE, author=meta.pdf_author(),
                    affiliation=AFFILIATION, keywords=KEYWORDS, subject=SUBJECT)
    (REL / "paper.tex").write_text(tex, encoding="utf-8")
    print(f"wrote paper.tex ({(REL / 'paper.tex').stat().st_size:,} bytes)")
    meta.check_author_metadata()
    print(f"  author: {AUTHOR}" + (f" ({AFFILIATION})" if AFFILIATION else ""))


def main() -> None:
    f4_legend_fix()
    latex()
    print("figures 1-3 and all tables carried unchanged from V4")


if __name__ == "__main__":
    main()
