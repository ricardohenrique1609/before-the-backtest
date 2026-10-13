"""V4 acceptance revision: rebuild Figure 4 and regenerate paper_v4.tex.

Figures 1-3 and all tables are carried unchanged from V3; only Figure 4's presentation changes, per
referee V3 item 4: the shaded area must not read as a confidence interval. Nothing is recomputed and
no data are reconstructed - the plotted values are the same committed values as in V3.

Run: .venv/Scripts/python -I scripts/paper_build_v4.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "falsification_first_alpha_discovery"
V4 = PAPER / "v4"
FIG = V4 / "figures"
FIGDATA = FIG / "data"

_spec = importlib.util.spec_from_file_location("v1fig", ROOT / "scripts" / "paper_build_figures.py")
v1fig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1fig)
INK, MUTED, NEUTRAL, FAIL_C, LIGHT = (
    v1fig.INK, v1fig.MUTED, v1fig.NEUTRAL, v1fig.FAIL_C, v1fig.LIGHT)


def f4_ceiling() -> None:
    """Figure 4, re-presented. Same values as V3; hatched band, explicit non-interval labelling."""
    txt = (ROOT / "H19_2_PREFREEZE_FEASIBILITY.md").read_text(encoding="utf-8", errors="replace")
    rows = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in v1fig.CEILING_RE.finditer(txt)]
    dates = [r[0] for r in rows]
    warned = [r[2] for r in rows]
    pools = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(6.8, 3.5))

    # Hatched, unfilled band: a recorded range, deliberately not drawn like an interval.
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
    ax.set_ylim(0, 34)
    ax.set_ylabel("warned assets eligible as controls")
    ax.legend(fontsize=6.6, frameon=False, loc="upper left")
    ax.set_title("Full-pool ceiling: recorded range, not a confidence interval\n"
                 "17 dates are not individually persisted and are not plotted or interpolated",
                 fontsize=8.6, loc="left")
    fig.savefig(FIG / "v4_f4_full_pool_ceiling.png")
    fig.savefig(FIG / "v4_f4_full_pool_ceiling.pdf")
    plt.close(fig)

    lines = ["# provenance: H19_2_PREFREEZE_FEASIBILITY.md Check 3. 8 of 25 announcement dates have "
             "individually persisted values; all 25 contribute to the persisted median. The 17 "
             "remaining dates are NOT plotted, NOT interpolated and NOT implied by the shading. "
             "Values identical to V3; only the presentation changed.",
             "date,eligible_pool,warned_in_pool"]
    lines += [f"{d},{p},{t}" for d, p, t in zip(dates, pools, warned, strict=True)]
    lines += ["median_all_25_dates,,7", "recorded_range_min,,0", "recorded_range_max,,27",
              "dates_reaching_floor,,3 of 25"]
    (FIGDATA / "v4_f4_full_pool_ceiling.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote v4_f4_full_pool_ceiling (values unchanged from V3; presentation revised)")


def latex() -> None:
    spec = importlib.util.spec_from_file_location("md2tex", ROOT / "scripts" / "paper_md_to_tex.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    (V4 / "paper_v4.tex").write_text(
        m.convert((V4 / "paper_v4.md").read_text(encoding="utf-8")), encoding="utf-8")
    print(f"wrote paper_v4.tex ({(V4 / 'paper_v4.tex').stat().st_size:,} bytes)")


def main() -> None:
    f4_ceiling()
    latex()
    print("figures 1-3 and all tables are carried unchanged from V3")


if __name__ == "__main__":
    main()
