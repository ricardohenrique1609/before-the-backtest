"""Build the paper's six figures from committed artefacts only.

No economic quantity is recomputed here. Every number plotted is read from a gate JSON, a results
JSON, or - where a value exists only in a committed report - from a small provenance-carrying CSV
written next to the figures. Nothing in this script loads price data.

Run: .venv/Scripts/python -I scripts/paper_build_figures.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, FancyBboxPatch

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "alpha_sprint"
PAPER = ROOT / "papers" / "falsification_first_alpha_discovery"
FIG = PAPER / "figures"
FIGDATA = FIG / "data"
FIG.mkdir(parents=True, exist_ok=True)
FIGDATA.mkdir(parents=True, exist_ok=True)

INK = "#1a1a1a"
MUTED = "#6e6e6e"
PASS_C = "#2f6f4f"
FAIL_C = "#8c2f2f"
NEUTRAL = "#4a6fa5"
LIGHT = "#d9dde3"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def jload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def crit_counts(g: dict) -> tuple[int, int]:
    cp = g.get("criteria_passed")
    if isinstance(cp, str) and "/" in cp:
        a, b = cp.split("/", 1)
        return int(a), int(b)
    if cp is not None and "criteria_total" in g:
        return int(cp), int(g["criteria_total"])
    crits = g.get("criteria", [])
    return sum(1 for c in crits if c.get("pass")), len(crits)


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIG / f"{stem}.png")
    fig.savefig(FIG / f"{stem}.pdf")
    plt.close(fig)
    print("wrote", stem)


def write_figdata(stem: str, header: list[str], rows: list[list], provenance: str) -> None:
    lines = [f"# provenance: {provenance}", ",".join(header)]
    for r in rows:
        lines.append(",".join(str(x) for x in r))
    (FIGDATA / f"{stem}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ======================================================================================
# F1 - research lifecycle / falsification funnel
# ======================================================================================
def f1() -> None:
    stages = [
        ("idea", "H1-H12 cycles"),
        ("data gate", "H14.1, H14.2, H14.3 stop"),
        ("semantic gate", "H15, H16.1 stop"),
        ("substrate gate", "H17.0, H18.0 stop"),
        ("PIT gate", "H18.3 design amended"),
        ("identification", "H19.2 stops before freeze"),
        ("pre-registration", "H18.3 frozen and hashed"),
        ("frozen OOS", "H18.3 NULL"),
        ("execution", "H19.0 partial: 201 to 32"),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(stages) + 0.6)
    ax.axis("off")

    for i, (stage, died) in enumerate(stages):
        y = len(stages) - i - 0.5
        width = 6.4 - i * 0.52
        box = FancyBboxPatch((0.25, y - 0.3), width, 0.6,
                             boxstyle="round,pad=0.02,rounding_size=0.08",
                             linewidth=0.8, edgecolor=INK,
                             facecolor=LIGHT if i % 2 == 0 else "white")
        ax.add_patch(box)
        ax.text(0.45, y, stage, va="center", ha="left", fontsize=9, color=INK)
        ax.text(0.35 + width + 0.15, y, died, va="center", ha="left", fontsize=7.5, color=MUTED)
        if i < len(stages) - 1:
            ax.add_patch(FancyArrow(0.25 + width / 2, y - 0.32, 0, -0.34, width=0.004,
                                    head_width=0.11, head_length=0.1, length_includes_head=True,
                                    color=MUTED, linewidth=0))

    ax.text(0.25, len(stages) + 0.25, "stage a hypothesis must survive",
            fontsize=8, style="italic", color=MUTED)
    ax.text(6.9, len(stages) + 0.25, "what the stage did to a family",
            fontsize=8, style="italic", color=MUTED)
    save(fig, "f1_research_lifecycle")


# ======================================================================================
# F2 - where each family stopped, with its gate count
# ======================================================================================
def f2() -> None:
    gates = {
        "H15": ("H15_13D_GATE.json", "semantic"),
        "H16.1": ("H16_1_GATE.json", "semantic"),
        "H17.0": ("H17_0_GATE.json", "substrate"),
        "H18.0": ("H18_0_GATE.json", "substrate"),
        "H18.0b": ("H18_0B_GATE.json", "substrate"),
        "H18.1": ("H18_1_GATE.json", "semantic"),
        "H18.1b": ("H18_1B_GATE.json", "construction"),
        "H19.0": ("H19_0_GATE.json", "execution"),
    }
    rows, labels = [], []
    for fam, (fname, _) in gates.items():
        g = jload(ROOT / fname)
        if fam == "H18.0":
            p, t = 4, 9  # the Binance column of the three-venue probe, as the gate records it
            label = "4 of 9 (Binance), 2 of 3 venues required"
        else:
            p, t = crit_counts(g)
            label = f"{p} of {t}"
        rows.append((fam, p, t))
        labels.append(label)

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    fams = [r[0] for r in rows]
    shares = [r[1] / r[2] for r in rows]
    colors = [PASS_C if s == 1.0 else (NEUTRAL if s >= 0.9 else FAIL_C) for s in shares]
    bars = ax.barh(fams[::-1], [s * 100 for s in shares][::-1], color=colors[::-1],
                   height=0.6, edgecolor="none")
    for bar, lab in zip(bars, labels[::-1], strict=True):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2, lab,
                va="center", fontsize=7.5, color=MUTED)
    ax.set_xlim(0, 125)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("share of the family's own gate criteria that passed (%)")
    ax.axvline(100, color=INK, linewidth=0.6, linestyle=":")
    ax.set_title("Gate outcomes as each family recorded them", fontsize=9.5, loc="left")
    write_figdata("f2_gate_outcomes", ["family", "criteria_passed", "criteria_total"],
                  [[f, p, t] for f, p, t in rows],
                  "each family's gate JSON, field criteria_passed; H18.0 is the Binance column of "
                  "the three-venue probe")
    save(fig, "f2_gate_outcomes")


# ======================================================================================
# F3 - H18 lifecycle reconstruction
# ======================================================================================
def f3() -> None:
    g1 = jload(ROOT / "H18_1_GATE.json")
    g1b = jload(ROOT / "H18_1B_GATE.json")
    cats = g1["pair_event_categories"]
    uni = g1b["universe"]

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.4, 3.4), width_ratios=[1.25, 1])

    order = ["MINOR_PAIR_REMOVAL", "QUOTE_MIGRATION", "ASSET_FULL_SPOT_DELISTING",
             "FIAT_PAIR_REMOVAL", "PARTIAL_ASSET_DELISTING", "UNKNOWN"]
    vals = [cats[k] for k in order]
    cols = [LIGHT] * len(order)
    cols[order.index("ASSET_FULL_SPOT_DELISTING")] = NEUTRAL
    bars = axa.barh([k.replace("_", " ").lower() for k in order][::-1], vals[::-1],
                    color=cols[::-1], edgecolor=INK, linewidth=0.5, height=0.62)
    for bar, v in zip(bars, vals[::-1], strict=True):
        axa.text(bar.get_width() + 12, bar.get_y() + bar.get_height() / 2, f"{v:,}",
                 va="center", fontsize=7.5, color=MUTED)
    axa.set_xlim(0, 820)
    axa.set_xlabel("pair-removal events")
    axa.set_title(f"a. {cats['ASSET_FULL_SPOT_DELISTING']} of "
                  f"{g1['universe']['pair_events']:,} pair events are a full delisting",
                  fontsize=9, loc="left")

    # The decomposition is 82 + 119 = 201, not 84 + 119: two of H18.1's 84 episodes (AUD, GBP)
    # are fiat quote assets that H18.1b does not class as full delistings. Both numbers come from
    # the gate: crosswalk.BOTH and recall.against_h18_1_classifier.
    both = uni["crosswalk"]["BOTH"]
    steps = [(f"H18.1 episodes\nalso in H18.1b\n({both} of "
              f"{g1['asset_episode_categories']['ASSET_FULL_SPOT_DELISTING']})", both, NEUTRAL),
             ("+ different\ncatalog", uni["miss_reasons"]["DIFFERENT_CATEGORY"], MUTED),
             ("+ pre-2022\ncatalog", uni["miss_reasons"]["PRE_2022_CATALOG"], MUTED),
             ("+ pair\nuniverse", uni["miss_reasons"]["PAIR_UNIVERSE"], MUTED),
             ("H18.1b validated\nuniverse", uni["full_delisting_events"], PASS_C)]
    xs = range(len(steps))
    axb.bar([x for x in xs], [s[1] for s in steps], color=[s[2] for s in steps],
            edgecolor=INK, linewidth=0.5, width=0.62)
    for x, s in zip(xs, steps, strict=True):
        axb.text(x, s[1] + 4, str(s[1]), ha="center", fontsize=7.5, color=INK)
    axb.set_xticks(list(xs))
    axb.set_xticklabels([s[0] for s in steps], fontsize=6.0)
    axb.set_ylim(0, 225)
    axb.set_ylabel("asset-level events")
    axb.set_title(f"b. {uni['h18_1_held']} to {uni['full_delisting_events']} after catalog "
                  "expansion", fontsize=9, loc="left")

    write_figdata("f3_lifecycle_reconstruction", ["step", "value"],
                  [[k, cats[k]] for k in order] +
                  [["h18_1_held", uni["h18_1_held"]],
                   ["crosswalk_BOTH", uni["crosswalk"]["BOTH"]],
                   ["miss_DIFFERENT_CATEGORY", uni["miss_reasons"]["DIFFERENT_CATEGORY"]],
                   ["miss_PRE_2022_CATALOG", uni["miss_reasons"]["PRE_2022_CATALOG"]],
                   ["miss_PAIR_UNIVERSE", uni["miss_reasons"]["PAIR_UNIVERSE"]],
                   ["full_delisting_events", uni["full_delisting_events"]]],
                  "H18_1_GATE.json pair_event_categories / asset_episode_categories; "
                  "H18_1B_GATE.json universe")
    fig.tight_layout()
    save(fig, "f3_lifecycle_reconstruction")


# ======================================================================================
# F4 - H18.3 rolling-origin folds versus the single-use holdout
# ======================================================================================
FOLD_TABLE_RE = re.compile(
    r"^\|\s*(\d)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|[^|]*\|[^|]*\|[^|]*\|\s*\*\*([+-][\d.]+)\*\*",
    re.M)


def read_folds() -> list[tuple[int, str, int, float]]:
    txt = (ROOT / "H18_3_DEVELOPMENT_REPORT.md").read_text(encoding="utf-8", errors="replace")
    out = []
    for m in FOLD_TABLE_RE.finditer(txt):
        out.append((int(m.group(1)), m.group(2).strip(), int(m.group(3)), float(m.group(4))))
    if len(out) != 8:
        raise SystemExit(f"expected 8 folds in the development report, parsed {len(out)}")
    return out


def f4() -> None:
    folds = read_folds()
    dev = jload(DATA / "h18_3_development.json")
    g = jload(ROOT / "H18_3_GATE.json")
    ho = g["holdout"]
    cb = dev["cluster_bootstrap"]
    pool = dev["pooled_out_of_fold"]

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    xs = list(range(1, 9))
    deltas = [f[3] for f in folds]
    ax.bar(xs, deltas, color=NEUTRAL, edgecolor=INK, linewidth=0.5, width=0.62,
           label="development: rolling-origin test fold")
    for x, d in zip(xs, deltas, strict=True):
        ax.text(x, d + 0.0025, f"{d:+.4f}", ha="center", fontsize=6.6, color=INK)

    ax.axvline(9.0, color=INK, linewidth=0.8)
    hx = 10.0
    ax.bar([hx], [ho["delta_pr_auc_abs"]], color=FAIL_C, edgecolor=INK, linewidth=0.5, width=0.62,
           label="holdout: single-use, opened once")
    ax.text(hx, ho["delta_pr_auc_abs"] - 0.0045, f"{ho['delta_pr_auc_abs']:+.5f}",
            ha="center", va="top", fontsize=6.8, color=INK)

    ax.axhspan(cb["ci95_low"], cb["ci95_high"], xmin=0, xmax=0.78, color=NEUTRAL, alpha=0.10,
               zorder=0)
    ax.axhline(pool["delta_abs"], xmin=0, xmax=0.78, color=NEUTRAL, linestyle="--", linewidth=0.9,
               label=f"pooled out-of-fold {pool['delta_abs']:+.4f}, "
                     f"bootstrap 95% CI [{cb['ci95_low']:+.4f}, {cb['ci95_high']:+.4f}]")
    ax.axhline(0, color=INK, linewidth=0.8)

    ax.set_xticks(xs + [hx])
    ax.set_xticklabels([f"fold {i}" for i in xs] + ["HOLDOUT\n2025"], fontsize=7)
    ax.set_ylabel("Δ PR-AUC  (challenger − baseline)")
    ax.set_title("Eight positive development folds, and the frozen holdout that reversed the sign",
                 fontsize=9.5, loc="left")
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_ylim(-0.022, 0.108)
    ax.text(9.15, 0.074, "a different evaluation role,\nnot a ninth fold", fontsize=6.8,
            color=MUTED, va="top")

    write_figdata("f4_h18_3_folds_vs_holdout",
                  ["block", "fold", "test_window", "test_events", "delta_pr_auc"],
                  [["DEVELOPMENT", f[0], f[1].replace(",", " "), f[2], f[3]] for f in folds] +
                  [["HOLDOUT", "", "2025-01-06..2025-10-06", ho["unique_events"],
                    ho["delta_pr_auc_abs"]]],
                  "H18_3_DEVELOPMENT_REPORT.md section 3 table (folds); H18_3_GATE.json holdout "
                  "block; h18_3_development.json pooled_out_of_fold and cluster_bootstrap")
    save(fig, "f4_h18_3_folds_vs_holdout")


# ======================================================================================
# F5 - H19.0 execution funnel
# ======================================================================================
def f5() -> None:
    g = jload(ROOT / "H19_0_GATE.json")
    n_small = round(g["clean_events"] * g["small_order_1k_share_of_median_hourly"]["<=1.00%"])
    steps = [
        ("documented full-delisting events", g["input_events"],
         "H18.1b validated universe"),
        ("Tier-1 USD-M perpetual live at T0", g["tier1_usdm_at_T0"],
         "instrument existence at T0, not today"),
        ("materially shortable at T0", g["shortable_at_T0"],
         "trades after T0, not merely a served candle"),
        ("clean public-information event", g["clean_events"],
         "no prior derivative notice"),
        ("US$1,000 order ≤1% of median hourly notional", n_small,
         "capacity for small capital"),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ys = list(range(len(steps)))[::-1]
    vals = [s[1] for s in steps]
    cols = [NEUTRAL] * 4 + [FAIL_C]
    bars = ax.barh(ys, vals, color=cols, edgecolor=INK, linewidth=0.5, height=0.6)
    for y, s, bar in zip(ys, steps, bars, strict=True):
        ax.text(bar.get_width() + 3, y, f"{s[1]}", va="center", fontsize=8.5, color=INK)
        ax.text(bar.get_width() + 14, y, s[2], va="center", fontsize=7, color=MUTED)
    ax.set_yticks(ys)
    ax.set_yticklabels([s[0] for s in steps], fontsize=7.6)
    ax.set_xlim(0, 215)
    ax.set_xlabel("events")
    ax.set_title("A documented event is not a tradable event (H19.0, PARTIAL PASS)",
                 fontsize=9.5, loc="left")
    write_figdata("f5_execution_funnel", ["stage", "events"],
                  [[s[0].replace(",", " "), s[1]] for s in steps],
                  "H19_0_GATE.json input_events, tier1_usdm_at_T0, shortable_at_T0, clean_events, "
                  "and clean_events x small_order_1k_share_of_median_hourly['<=1.00%']")
    save(fig, "f5_execution_funnel")


# ======================================================================================
# F6 - H19.2 common-support collapse
# Two panels are used because the collapse and its cause are distinct measurements: panel a is
# the realised per-event control count, panel b is the ceiling computed on the full pool.
# ======================================================================================
CEILING_RE = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d+)\s*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|",
                        re.M)


def f6() -> None:
    pf = jload(DATA / "h19_2_prefreeze.json")
    txt = (ROOT / "H19_2_PREFREEZE_FEASIBILITY.md").read_text(encoding="utf-8", errors="replace")
    ceiling = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in CEILING_RE.finditer(txt)]
    if not ceiling:
        raise SystemExit("could not parse the Check 3 ceiling table")

    cpe = pf["2_controls_per_event"]
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.4, 3.3), width_ratios=[1, 1.15])

    qs = ["p10", "p25", "median", "p75", "p90"]
    vals = [cpe[q] for q in qs]
    bars = axa.bar(qs, vals, color=[FAIL_C if v < 20 else PASS_C for v in vals],
                   edgecolor=INK, linewidth=0.5, width=0.6)
    for bar, v in zip(bars, vals, strict=True):
        axa.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f"{v:g}", ha="center", fontsize=7.5,
                 color=INK)
    axa.axhline(pf["frozen_bars"]["MIN_CONTROLS"], color=INK, linestyle="--", linewidth=0.9)
    axa.text(4.4, pf["frozen_bars"]["MIN_CONTROLS"] + 1.5, "frozen floor: 20", ha="right",
             fontsize=7, color=INK)
    axa.set_ylim(0, 66)
    axa.set_ylabel("matched controls available")
    axa.set_title(f"a. {pf['3_events_with_fewer_than_20_controls']} of 62 events below the floor; "
                  f"confirmatory n = {pf['1_final_candidate_n']}", fontsize=8.6, loc="left")

    dates = [c[0] for c in ceiling]
    tagged = [c[2] for c in ceiling]
    pools = [c[1] for c in ceiling]
    # markers only: these are 8 of the 25 announcement dates, so a connecting line would imply a
    # continuous series the artefact does not record.
    axb.plot(dates, tagged, marker="o", markersize=4.5, color=FAIL_C, linestyle="none",
             label="tagged assets eligible in the full pool")
    axb.axhline(20, color=INK, linestyle="--", linewidth=0.9, label="frozen floor: 20 controls")
    for d, t in zip(dates, tagged, strict=True):
        axb.annotate(str(t), (d, t), textcoords="offset points", xytext=(0, 5), ha="center",
                     fontsize=6.6, color=INK)
    axb.set_xticks(dates)
    axb.set_xticklabels([d[:7] for d in dates], rotation=60, fontsize=6.4)
    axb.set_ylim(0, 34)
    axb.set_ylabel("assets")
    axb.legend(fontsize=6.8, frameon=False, loc="upper left")
    axb.set_title("b. the ceiling, computed on the full pool\n(8 dates reported of 25; median "
                  "across all 25 = 7)", fontsize=8.6, loc="left")

    write_figdata("f6_common_support", ["panel", "key", "value"],
                  [["a", q, cpe[q]] for q in qs] +
                  [["a", "events_below_20", pf["3_events_with_fewer_than_20_controls"]],
                   ["a", "confirmatory_n", pf["1_final_candidate_n"]],
                   ["a", "frozen_floor", pf["frozen_bars"]["MIN_CONTROLS"]]] +
                  [["b", f"{d}_eligible_pool", p] for d, p in zip(dates, pools, strict=True)] +
                  [["b", f"{d}_tagged_in_pool", t] for d, t in zip(dates, tagged, strict=True)],
                  "h19_2_prefreeze.json 2_controls_per_event / 3_events_with_fewer_than_20_controls "
                  "/ 1_final_candidate_n / frozen_bars; H19_2_PREFREEZE_FEASIBILITY.md Check 3 "
                  "table (the 8 dates it reports of 25)")
    fig.tight_layout()
    save(fig, "f6_common_support")


def main() -> None:
    f1()
    f2()
    f3()
    f4()
    f5()
    f6()


if __name__ == "__main__":
    main()
