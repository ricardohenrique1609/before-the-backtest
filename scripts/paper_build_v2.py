"""Build the V2 figure and table set, and generate paper_v2.tex from paper_v2.md.

V2 figure set, per the revision plan:
  V1 F1 (schematic lifecycle) is dropped; its content merges into the gate-outcome figure.
  F3 lifecycle reconstruction, F4 rolling origin vs holdout and F5 funnel are retained, with the
  funnel relabelled to "coarse liquidity screen".
  F6 keeps the realised common-support panel in the body; the 8-of-25 ceiling panel moves to an
  appendix figure of its own.
  A new figure reports the registry denominator by terminal state.

Reads only committed artefacts. Computes nothing economic and loads no price.

Run: .venv/Scripts/python -I scripts/paper_build_v2.py
"""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "falsification_first_alpha_discovery"
V2 = PAPER / "v2"
FIG = V2 / "figures"
FIGDATA = FIG / "data"
TAB = V2 / "tables"
for d in (FIG, FIGDATA, TAB):
    d.mkdir(parents=True, exist_ok=True)

# Reuse the V1 builders' style and helpers without duplicating them.
_spec = importlib.util.spec_from_file_location("v1fig", ROOT / "scripts" / "paper_build_figures.py")
v1fig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1fig)

INK, MUTED, PASS_C, FAIL_C, NEUTRAL, LIGHT = (
    v1fig.INK, v1fig.MUTED, v1fig.PASS_C, v1fig.FAIL_C, v1fig.NEUTRAL, v1fig.LIGHT)


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIG / f"{stem}.png")
    fig.savefig(FIG / f"{stem}.pdf")
    plt.close(fig)
    print("wrote", stem)


def write_figdata(stem: str, header: list[str], rows: list[list], provenance: str) -> None:
    lines = [f"# provenance: {provenance}", ",".join(header)]
    lines += [",".join(str(x) for x in r) for r in rows]
    (FIGDATA / f"{stem}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ======================================================================================
# V2-F1 - registry denominator by terminal state
# ======================================================================================
TERMINAL = [
    ("economic reject (economic quantity computed)", 9, FAIL_C),
    ("data-gate fail / untested", 5, MUTED),
    ("construction or substrate pass", 3, LIGHT),
    ("watch / research (inconclusive)", 3, LIGHT),
    ("infrastructure blocked", 2, MUTED),
    ("hypothesis selection (not a verdict)", 2, LIGHT),
    ("promoted", 1, PASS_C),
    ("implementation reject, economics unresolved", 1, FAIL_C),
    ("pre-registered null", 1, NEUTRAL),
    ("identification blocked", 1, MUTED),
    ("execution / capacity fail", 1, MUTED),
    ("open", 1, LIGHT),
    ("falsification of alternatives", 1, LIGHT),
]


def f_denominator() -> None:
    total = sum(c for _, c, _ in TERMINAL)
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    labels = [t[0] for t in TERMINAL][::-1]
    vals = [t[1] for t in TERMINAL][::-1]
    cols = [t[2] for t in TERMINAL][::-1]
    bars = ax.barh(labels, vals, color=cols, edgecolor=INK, linewidth=0.5, height=0.62)
    for bar, v in zip(bars, vals, strict=True):
        ax.text(bar.get_width() + 0.12, bar.get_y() + bar.get_height() / 2, str(v),
                va="center", fontsize=8, color=INK)
    ax.set_xlim(0, 10.5)
    ax.set_xlabel(f"registry entries (n = {total})")
    ax.tick_params(axis="y", labelsize=7.2)
    ax.set_title("The full denominator: all 31 registry entries, H1 to H19.2",
                 fontsize=9.5, loc="left")
    write_figdata("v2_f1_registry_denominator", ["terminal_state", "entries"],
                  [[t[0].replace(",", ";"), t[1]] for t in TERMINAL],
                  "docs/alpha_sprint/HYPOTHESIS_LEDGER.md, mapped to the paper taxonomy in section 4.3")
    save(fig, "v2_f1_registry_denominator")


# ======================================================================================
# V2-F5 - execution funnel, relabelled
# ======================================================================================
def f_funnel() -> None:
    g = json.loads((ROOT / "H19_0_GATE.json").read_text(encoding="utf-8", errors="replace"))
    n_small = round(g["clean_events"] * g["small_order_1k_share_of_median_hourly"]["<=1.00%"])
    steps = [
        ("documented full-delisting events", g["input_events"], "validated universe"),
        ("Tier-1 USD-M perpetual live at T0", g["tier1_usdm_at_T0"],
         "instrument existence at T0, not today"),
        ("materially shortable at T0", g["shortable_at_T0"],
         "trades after T0, not merely a served candle"),
        ("clean public-information event", g["clean_events"], "no prior derivative notice"),
        ("passes coarse volume-based liquidity screen", n_small,
         "US$1,000 order <= 1% of median hourly notional"),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ys = list(range(len(steps)))[::-1]
    bars = ax.barh(ys, [s[1] for s in steps], color=[NEUTRAL] * 4 + [FAIL_C],
                   edgecolor=INK, linewidth=0.5, height=0.6)
    for y, s, bar in zip(ys, steps, bars, strict=True):
        ax.text(bar.get_width() + 3, y, str(s[1]), va="center", fontsize=8.5, color=INK)
        ax.text(bar.get_width() + 15, y, s[2], va="center", fontsize=6.8, color=MUTED)
    ax.set_yticks(ys)
    ax.set_yticklabels([s[0] for s in steps], fontsize=7.4)
    ax.set_xlim(0, 215)
    ax.set_xlabel("events (n = 201 documented)")
    ax.set_title("Screening, not execution feasibility: 201 documented events to 32 screened",
                 fontsize=9.5, loc="left")
    write_figdata("v2_f5_screening_funnel", ["stage", "events"],
                  [[s[0].replace(",", ";"), s[1]] for s in steps],
                  "H19_0_GATE.json: input_events, tier1_usdm_at_T0, shortable_at_T0, clean_events, "
                  "clean_events x small_order_1k_share_of_median_hourly['<=1.00%']")
    save(fig, "v2_f5_screening_funnel")


# ======================================================================================
# V2-F6 - realised common support (body) and V2-A1 - full-pool ceiling (appendix)
# ======================================================================================
def f_common_support() -> None:
    pf = json.loads((ROOT / "data" / "alpha_sprint" / "h19_2_prefreeze.json")
                    .read_text(encoding="utf-8", errors="replace"))
    cpe = pf["2_controls_per_event"]
    qs = ["p10", "p25", "median", "p75", "p90"]
    vals = [cpe[q] for q in qs]
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    bars = ax.bar(qs, vals, color=[FAIL_C if v < 20 else PASS_C for v in vals],
                  edgecolor=INK, linewidth=0.5, width=0.6)
    for bar, v in zip(bars, vals, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f"{v:g}", ha="center", fontsize=8,
                color=INK)
    ax.axhline(pf["frozen_bars"]["MIN_CONTROLS"], color=INK, linestyle="--", linewidth=0.9)
    ax.text(4.42, pf["frozen_bars"]["MIN_CONTROLS"] + 1.6, "frozen floor: 20", ha="right",
            fontsize=7.4, color=INK)
    ax.set_ylim(0, 66)
    ax.set_ylabel("matched controls available per event")
    ax.set_title(f"{pf['3_events_with_fewer_than_20_controls']} of 62 candidate events fall below "
                 f"the floor;\nfinal confirmatory n = {pf['1_final_candidate_n']} (descriptive; "
                 "no outcome was read)", fontsize=8.8, loc="left")
    write_figdata("v2_f6_common_support", ["quantile", "matched_controls"],
                  [[q, cpe[q]] for q in qs] +
                  [["events_below_floor", pf["3_events_with_fewer_than_20_controls"]],
                   ["confirmatory_n", pf["1_final_candidate_n"]],
                   ["frozen_floor", pf["frozen_bars"]["MIN_CONTROLS"]]],
                  "data/alpha_sprint/h19_2_prefreeze.json")
    save(fig, "v2_f6_common_support")


def f_ceiling_appendix() -> None:
    txt = (ROOT / "H19_2_PREFREEZE_FEASIBILITY.md").read_text(encoding="utf-8", errors="replace")
    ceiling = [(m.group(1), int(m.group(2)), int(m.group(3)))
               for m in v1fig.CEILING_RE.finditer(txt)]
    dates = [c[0] for c in ceiling]
    tagged = [c[2] for c in ceiling]
    pools = [c[1] for c in ceiling]
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    ax.plot(dates, tagged, marker="o", markersize=4.5, color=FAIL_C, linestyle="none",
            label="warned assets eligible in the full pool")
    ax.axhline(20, color=INK, linestyle="--", linewidth=0.9, label="frozen floor: 20 controls")
    for d, t in zip(dates, tagged, strict=True):
        ax.annotate(str(t), (d, t), textcoords="offset points", xytext=(0, 5), ha="center",
                    fontsize=6.8, color=INK)
    ax.set_xticks(dates)
    ax.set_xticklabels([d[:7] for d in dates], rotation=60, fontsize=6.6)
    ax.set_ylim(0, 34)
    ax.set_ylabel("assets")
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title("Appendix: the full-pool ceiling for the 8 of 25 announcement dates\nthe artefact "
                 "records (median across all 25 = 7; markers, not a series)",
                 fontsize=8.6, loc="left")
    write_figdata("v2_a1_ceiling", ["date", "eligible_pool", "warned_in_pool"],
                  [[d, p, t] for d, p, t in zip(dates, pools, tagged, strict=True)],
                  "H19_2_PREFREEZE_FEASIBILITY.md Check 3 table; 8 of 25 dates are recorded there, "
                  "the remaining 17 were summarised to a median and not persisted")
    save(fig, "v2_a1_ceiling")


# ======================================================================================
# Tables: regenerate V1's five into v2/tables, plus the two new V2 tables
# ======================================================================================
def tables() -> None:
    v1tab = ROOT / "papers" / "falsification_first_alpha_discovery" / "tables"
    for src in sorted(v1tab.glob("*.md")):
        shutil.copyfile(src, TAB / src.name)
        print("copied", src.name)
    print("note: the registry denominator (section 4.2/4.3) and the threshold classification "
          "(section 9) are authored in paper_v2.md itself and are not generated files")


# ======================================================================================
# LaTeX
# ======================================================================================
def latex() -> None:
    spec = importlib.util.spec_from_file_location("md2tex", ROOT / "scripts" / "paper_md_to_tex.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    src = (V2 / "paper_v2.md").read_text(encoding="utf-8")
    (V2 / "paper_v2.tex").write_text(m.convert(src), encoding="utf-8")
    size = (V2 / "paper_v2.tex").stat().st_size
    print(f"wrote paper_v2.tex ({size:,} bytes)")


def main() -> None:
    f_denominator()
    f_funnel()
    f_common_support()
    f_ceiling_appendix()
    # lifecycle reconstruction and the rolling-origin/holdout figure are unchanged from V1
    for stem in ("f3_lifecycle_reconstruction", "f4_h18_3_folds_vs_holdout"):
        for ext in ("png", "pdf"):
            shutil.copyfile(PAPER / "figures" / f"{stem}.{ext}", FIG / f"v2_{stem}.{ext}")
        shutil.copyfile(PAPER / "figures" / "data" / f"{stem}.csv",
                        FIGDATA / f"v2_{stem}.csv")
        print("carried", stem)
    tables()
    latex()


if __name__ == "__main__":
    main()
