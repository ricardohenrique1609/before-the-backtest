"""Build the V3 figure and table set, and generate paper_v3.tex from paper_v3.md.

V3 carries four main figures, three body tables and four appendix tables. Everything is read from
committed artefacts; nothing economic is computed and no price column is loaded.

Run: .venv/Scripts/python -I scripts/paper_build_v3.py
"""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, FancyBboxPatch

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "falsification_first_alpha_discovery"
V3 = PAPER / "v3"
FIG = V3 / "figures"
FIGDATA = FIG / "data"
TAB = V3 / "tables"
for d in (FIG, FIGDATA, TAB):
    d.mkdir(parents=True, exist_ok=True)

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


def figdata(stem: str, header: list[str], rows: list[list], provenance: str) -> None:
    lines = [f"# provenance: {provenance}", ",".join(header)]
    lines += [",".join(str(x) for x in r) for r in rows]
    (FIGDATA / f"{stem}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


def jload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


# ======================================================================================
# Figure 1 - the procedure (schematic, no quantities)
# ======================================================================================
def f1_procedure() -> None:
    steps = [
        ("1. point-in-time eligible population", "C(t_e), rebuilt at each event time"),
        ("2. intended matching rule", "M(e, c, t) written in full, strata fixed"),
        ("3. attainable support, full pool", "S_e = |{c : M(e, c, t_e) = 1}|"),
        ("4. support indicator", "I_e = 1[S_e >= m]"),
        ("5. implied confirmatory sample", "N* = sum of I_e"),
        ("6. stop rule", "N* < N_min  ->  DESIGN INFEASIBLE"),
    ]
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(steps) + 1.4)
    ax.axis("off")

    ax.text(0.3, len(steps) + 1.0, "BEFORE the pre-registration freeze, and BEFORE outcome access",
            fontsize=8.5, style="italic", color=INK)
    for i, (title, detail) in enumerate(steps):
        y = len(steps) - i - 0.3
        last = i == len(steps) - 1
        box = FancyBboxPatch((0.3, y - 0.3), 5.6, 0.6,
                             boxstyle="round,pad=0.02,rounding_size=0.08",
                             linewidth=1.0 if last else 0.8,
                             edgecolor=FAIL_C if last else INK,
                             facecolor="white" if i % 2 else LIGHT)
        ax.add_patch(box)
        ax.text(0.5, y, title, va="center", ha="left", fontsize=8.6,
                color=FAIL_C if last else INK, weight="bold" if last else "normal")
        ax.text(6.1, y, detail, va="center", ha="left", fontsize=7.4, color=MUTED, family="monospace")
        if not last:
            ax.add_patch(FancyArrow(3.1, y - 0.32, 0, -0.33, width=0.004, head_width=0.1,
                                    head_length=0.1, length_includes_head=True, color=MUTED,
                                    linewidth=0))
    ax.text(0.3, 0.18, "Status on stop: DESIGN INFEASIBLE UNDER THIS SPECIFICATION  "
                       "-  not a null, not a rejection, hypothesis untested",
            fontsize=7.8, color=FAIL_C)
    save(fig, "v3_f1_procedure")


# ======================================================================================
# Figure 2 - event funnel to the candidate design (does not headline the 32)
# ======================================================================================
def f2_funnel() -> None:
    g = jload(ROOT / "H19_0_GATE.json")
    steps = [
        ("validated full-delisting events", g["input_events"], "event population"),
        ("Tier-1 USD-M perpetual live at t_e", g["tier1_usdm_at_T0"], "instrument existence at t_e"),
        ("materially shortable at t_e", g["shortable_at_T0"], "trades after t_e, not a served candle"),
        ("clean public-information events", g["clean_events"], "no prior derivative notice"),
        ("candidates for the matched design", 62, "one asset is coin-margined"),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ys = list(range(len(steps)))[::-1]
    bars = ax.barh(ys, [s[1] for s in steps], color=[NEUTRAL] * 4 + [PASS_C],
                   edgecolor=INK, linewidth=0.5, height=0.6)
    for y, s, bar in zip(ys, steps, bars, strict=True):
        ax.text(bar.get_width() + 3, y, str(s[1]), va="center", fontsize=8.5, color=INK)
        ax.text(bar.get_width() + 15, y, s[2], va="center", fontsize=6.9, color=MUTED)
    ax.set_yticks(ys)
    ax.set_yticklabels([s[0] for s in steps], fontsize=7.4)
    ax.set_xlim(0, 215)
    ax.set_xlabel("events (n = 201 validated)")
    ax.set_title("Point-in-time eligibility, evaluated at each event", fontsize=9.5, loc="left")
    figdata("v3_f2_event_funnel", ["stage", "events"],
            [[s[0].replace(",", ";"), s[1]] for s in steps],
            "H19_0_GATE.json: input_events, tier1_usdm_at_T0, shortable_at_T0, clean_events; "
            "62 from H19_2_PREFREEZE_FEASIBILITY.md section 1")
    save(fig, "v3_f2_event_funnel")


# ======================================================================================
# Figure 3 - MAIN FIGURE: attainable support vs the floor, and the implied sample
# ======================================================================================
def f3_support() -> None:
    pf = jload(ROOT / "data" / "alpha_sprint" / "h19_2_prefreeze.json")
    cpe = pf["2_controls_per_event"]
    floor = pf["frozen_bars"]["MIN_CONTROLS"]
    qs = ["p10", "p25", "median", "p75", "p90"]
    vals = [cpe[q] for q in qs]

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.4, 3.3), width_ratios=[1.35, 1])

    bars = axa.bar(qs, vals, color=[FAIL_C if v < floor else PASS_C for v in vals],
                   edgecolor=INK, linewidth=0.5, width=0.6)
    for bar, v in zip(bars, vals, strict=True):
        axa.text(bar.get_x() + bar.get_width() / 2, v + 1.6, f"{v:g}", ha="center", fontsize=8,
                 color=INK)
    axa.axhline(floor, color=INK, linestyle="--", linewidth=1.0)
    axa.text(4.42, floor + 1.8, f"pre-registered floor m = {floor}", ha="right", fontsize=7.4,
             color=INK)
    axa.set_ylim(0, 66)
    axa.set_ylabel("attainable matched controls per event")
    axa.set_title(f"a. {pf['3_events_with_fewer_than_20_controls']} of 62 events below the floor",
                  fontsize=8.8, loc="left")

    n_star = pf["1_final_candidate_n"]
    n_min = 40
    axb.bar(["N*", "N_min"], [n_star, n_min], color=[FAIL_C, MUTED], edgecolor=INK, linewidth=0.5,
            width=0.5)
    for x, v in zip([0, 1], [n_star, n_min], strict=True):
        axb.text(x, v + 1.2, str(v), ha="center", fontsize=9, color=INK)
    axb.set_ylim(0, 48)
    axb.set_ylabel("events")
    axb.set_xticks([0, 1])
    axb.set_xticklabels(["N* attainable", "N_min required"], fontsize=7.6)
    axb.set_title("b. the stop rule: N* < N_min", fontsize=8.8, loc="left")

    figdata("v3_f3_support_audit", ["key", "value"],
            [[q, cpe[q]] for q in qs] +
            [["events_below_floor", pf["3_events_with_fewer_than_20_controls"]],
             ["candidate_events", 62], ["floor_m", floor],
             ["N_star", n_star], ["N_min", n_min]],
            "data/alpha_sprint/h19_2_prefreeze.json; N_min from H19_2_PREFREEZE_FEASIBILITY.md")
    fig.tight_layout()
    save(fig, "v3_f3_support_audit")


# ======================================================================================
# Figure 4 - full-pool ceiling, recorded dates only, with range and median annotated
# ======================================================================================
def f4_ceiling() -> None:
    txt = (ROOT / "H19_2_PREFREEZE_FEASIBILITY.md").read_text(encoding="utf-8", errors="replace")
    rows = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in v1fig.CEILING_RE.finditer(txt)]
    dates = [r[0] for r in rows]
    warned = [r[2] for r in rows]
    pools = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    ax.axhspan(0, 27, color=LIGHT, alpha=0.55, zorder=0)
    ax.axhline(7, color=NEUTRAL, linestyle="-", linewidth=1.1,
               label="median across all 25 dates = 7")
    ax.axhline(20, color=INK, linestyle="--", linewidth=1.0, label="pre-registered floor m = 20")
    ax.plot(dates, warned, marker="o", markersize=5, color=FAIL_C, linestyle="none",
            label="recorded dates (8 of 25)")
    for d, t in zip(dates, warned, strict=True):
        ax.annotate(str(t), (d, t), textcoords="offset points", xytext=(0, 6), ha="center",
                    fontsize=6.9, color=INK)
    ax.set_xticks(dates)
    ax.set_xticklabels([d[:7] for d in dates], rotation=60, fontsize=6.8)
    ax.set_ylim(0, 34)
    ax.set_ylabel("warned assets eligible as controls")
    ax.legend(fontsize=6.9, frameon=False, loc="upper left")
    ax.set_title("Full-pool ceiling: shaded band is the recorded range 0 to 27\n"
                 "markers only - the full 25-date series was not persisted",
                 fontsize=8.6, loc="left")
    figdata("v3_f4_full_pool_ceiling", ["date", "eligible_pool", "warned_in_pool"],
            [[d, p, t] for d, p, t in zip(dates, pools, warned, strict=True)] +
            [["median_all_25_dates", "", 7], ["recorded_range_min", "", 0],
             ["recorded_range_max", "", 27], ["dates_reaching_floor", "", "3 of 25"]],
            "H19_2_PREFREEZE_FEASIBILITY.md Check 3; 8 of 25 dates are recorded there, the "
            "remaining 17 were summarised to a median and not persisted")
    save(fig, "v3_f4_full_pool_ceiling")


# ======================================================================================
# Tables
# ======================================================================================
def md_table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def tables() -> None:
    pf = jload(ROOT / "data" / "alpha_sprint" / "h19_2_prefreeze.json")
    g19 = jload(ROOT / "H19_0_GATE.json")

    # T1 - the procedure
    t1 = ("# Table 1 — The pre-freeze common-support audit\n\n"
          "Inputs, computation and stop rule. The audit runs before the pre-registration is frozen "
          "and before any outcome column is opened.\n\n" + md_table(
              ["element", "symbol", "definition", "fixed when?"],
              [["event set", "E", "proposed treated events", "before the audit"],
               ["PIT control universe", "C(t_e)", "entities admissible at t_e using only "
                "information available by t_e", "recomputed per event"],
               ["matching rule", "M(e, c, t)", "exact strata written in full", "before the audit"],
               ["minimum controls", "m", "support required per event", "before the audit"],
               ["minimum events", "N_min", "confirmatory sample required", "before the audit"],
               ["attainable support", "S_e", "count of c in C(t_e) with M(e, c, t_e) = 1, over the "
                "COMPLETE pool", "computed"],
               ["support indicator", "I_e", "1 if S_e >= m", "computed"],
               ["implied sample", "N*", "sum of I_e over events", "computed"],
               ["stop rule", "—", "if N* < N_min, stop before outcome access",
                "pre-registered"],
               ["status on stop", "—", "DESIGN INFEASIBLE UNDER THIS SPECIFICATION — not a null, "
                "not a rejection, hypothesis untested", "—"]]))
    (TAB / "v3_table1_procedure.md").write_text(t1, encoding="utf-8")

    # T2 - the support audit
    cpe = pf["2_controls_per_event"]
    t2 = ("# Table 2 — The support audit, with every quantity and its artefact\n\n"
          "All values read from committed artefacts. No price column was loaded at any point "
          "(`usecols=[0, 5, 7, 8]`).\n\n" + md_table(
              ["quantity", "value", "artefact field"],
              [["candidate events", "62", "H19_2_PREFREEZE_FEASIBILITY.md §1"],
               ["minimum controls per event, m", str(pf["frozen_bars"]["MIN_CONTROLS"]),
                "h19_2_prefreeze.json frozen_bars.MIN_CONTROLS"],
               ["minimum confirmatory events, N_min", "40", "H19_2_PREFREEZE_FEASIBILITY.md §A7"],
               ["attainable support p10 / p25 / median / p75 / p90",
                f"{cpe['p10']:g} / {cpe['p25']:g} / {cpe['median']:g} / {cpe['p75']:g} / "
                f"{cpe['p90']:g}", "h19_2_prefreeze.json 2_controls_per_event"],
               ["events below the floor", str(pf["3_events_with_fewer_than_20_controls"]),
                "h19_2_prefreeze.json 3_events_with_fewer_than_20_controls"],
               ["implied confirmatory sample, N*", str(pf["1_final_candidate_n"]),
                "h19_2_prefreeze.json 1_final_candidate_n"],
               ["warned universe, ever", "134 assets across 28 notices",
                "H19_2_PREFREEZE_FEASIBILITY.md Check 3"],
               ["full-pool ceiling per date", "0 to 27, median 7; 3 of 25 dates reach 20",
                "H19_2_PREFREEZE_FEASIBILITY.md Check 3"],
               ["eligible pool per date", "min 177, median 327, max 380",
                "h19_2_prefreeze.json metadata_eligible_pool_per_date"],
               ["leg availability (not binding)", "2,857 of 2,877 = 99.3%",
                "H19_2_PREFREEZE_FEASIBILITY.md Check 1"],
               ["transition filter (never binds)", "0 events",
                "H19_2_PREFREEZE_FEASIBILITY.md Check 2"],
               ["implied development / holdout", "9 / 1",
                "h19_2_prefreeze.json 7_development_holdout_after_exclusions"],
               ["decision", "N* = 10 < 40 → STOP before freeze",
                "h19_2_prefreeze.json hard_sample_rule_A7"],
               ["price columns read", "none; OHLC never entered memory",
                "scripts/h19_2_prefreeze.py; h19_2_prefreeze.json no_price_field_loaded"]]))
    (TAB / "v3_table2_support_audit.md").write_text(t2, encoding="utf-8")

    # T3 - bounded supporting results
    sm = g19["small_order_1k_share_of_median_hourly"]
    n = g19["clean_events"]
    t3 = ("# Table 3 — Bounded supporting results\n\n"
          "Each row states what the result establishes and, explicitly, what it does not.\n\n"
          + md_table(
              ["result", "value", "establishes", "does NOT establish"],
              [["venue archive symmetry", "0.0 pp retrieval differential, active vs delisted",
                "a PIT control universe is constructible from venue-owned history",
                "that survivorship bias is new, or that other venues behave this way"],
               ["validated event population", "201 events; recall 0.9801 vs candle-measured "
                "cessation; 4 true false negatives",
                "the event population is validated against an independent denominator",
                "that a larger event count is itself a result"],
               ["pair removal is not asset delisting", "102 of 1,422 pair events = 7.2%",
                "the economic unit must be classified, not assumed from the document type",
                "anything about returns"],
               ["classification-level PIT", "676 of 2,352 labels = 28.7% change class under a "
                "strictly backward window",
                "a detection procedure, and the rate it measured, for a known leakage class",
                "a new leakage category"],
               ["liquidity screen distribution",
                f"<=0.10%: {sm['<=0.10%']:.2%} ({round(sm['<=0.10%'] * n)}); "
                f"<=0.50%: {sm['<=0.50%']:.2%} ({round(sm['<=0.50%'] * n)}); "
                f"<=1.00%: {sm['<=1.00%']:.2%} ({round(sm['<=1.00%'] * n)}) of {n} clean events",
                "instrument availability and coarse liquidity at labelled operating points",
                "execution feasibility or profitability; no order book, spread, impact, fee, "
                "funding, latency or fill estimate exists"],
               ["out-of-sample falsification still required",
                "8 of 8 development folds positive; bootstrap CI [-0.0074, +0.0628]; holdout "
                "delta -0.00753",
                "that passing feasibility does not substitute for frozen OOS evaluation",
                "that no effect exists; absence is not demonstrated at this sample size"]]))
    (TAB / "v3_table3_supporting.md").write_text(t3, encoding="utf-8")
    print("wrote 3 body tables")

    # Appendix tables carried from the V1 generators
    src = PAPER / "tables"
    mapping = {
        "table2_failure_taxonomy.md": "v3_appendix_failure_taxonomy.md",
        "table3_silent_failure_classes.md": "v3_appendix_defects.md",
        "table5_h19_execution_gate.md": "v3_appendix_execution_gate.md",
        "table4_h18_3_preregistered_metrics.md": "v3_appendix_h18_3_metrics.md",
    }
    for a, b in mapping.items():
        shutil.copyfile(src / a, TAB / b)
    print("carried", len(mapping), "appendix tables")


def latex() -> None:
    spec = importlib.util.spec_from_file_location("md2tex", ROOT / "scripts" / "paper_md_to_tex.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    (V3 / "paper_v3.tex").write_text(
        m.convert((V3 / "paper_v3.md").read_text(encoding="utf-8")), encoding="utf-8")
    print(f"wrote paper_v3.tex ({(V3 / 'paper_v3.tex').stat().st_size:,} bytes)")


def main() -> None:
    f1_procedure()
    f2_funnel()
    f3_support()
    f4_ceiling()
    tables()
    latex()


if __name__ == "__main__":
    main()
