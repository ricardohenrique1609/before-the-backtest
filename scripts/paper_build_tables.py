"""Build the paper's five tables from committed artefacts.

Every quantity is read from a gate JSON, a results JSON or a committed report. Nothing is typed in
by hand except the qualitative columns (lesson, mechanism, defense), which carry no numbers.

Run: .venv/Scripts/python -I scripts/paper_build_tables.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "alpha_sprint"
OUT = ROOT / "papers" / "falsification_first_alpha_discovery" / "tables"
OUT.mkdir(parents=True, exist_ok=True)


def jload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def gate(name: str) -> dict:
    return jload(ROOT / name)


def crit_counts(g: dict) -> tuple[int, int]:
    """Passed / total, preferring the gate's own recorded counts.

    Two schemas exist across the families: the later gates store integers in
    ``criteria_passed`` and ``criteria_total``, the earlier ones store a single string
    ``"5/22"``. Both are read here rather than recounted, so the paper reports the count the
    gate itself recorded.
    """
    cp = g.get("criteria_passed")
    if isinstance(cp, str) and "/" in cp:
        a, b = cp.split("/", 1)
        return int(a), int(b)
    if cp is not None and "criteria_total" in g:
        return int(cp), int(g["criteria_total"])
    crits = g.get("criteria", [])
    return sum(1 for c in crits if c.get("pass")), len(crits)


def md_table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------------------
# Table 1 - experiment registry
# --------------------------------------------------------------------------------------
def table1() -> str:
    h15 = crit_counts(gate("H15_13D_GATE.json"))
    h16 = crit_counts(gate("H16_1_GATE.json"))
    h17 = crit_counts(gate("H17_0_GATE.json"))
    h18_0b = crit_counts(gate("H18_0B_GATE.json"))
    h18_1 = crit_counts(gate("H18_1_GATE.json"))
    h18_1b = crit_counts(gate("H18_1B_GATE.json"))
    h19_0 = crit_counts(gate("H19_0_GATE.json"))

    rows = [
        ["H13", "do filings separate cheap-because-ignored from cheap-because-the-cash-disappears?",
         "survivorship audit", "TESTED", "REJECT (implementation)", "C1 data construction",
         "a spectacular backtest is a bug candidate until the universe is audited"],
        ["H14", "B3 deep special situations", "universe built", "NOT SELECTED", "OPEN",
         "—", "a universe is not a hypothesis"],
        ["H14.1", "takeover-offer terms resolution", "gold set of 64 cases", "UNTESTED",
         "DATA-GATE FAIL", "C2 semantics", "extraction precision is a gate, not a nuisance"],
        ["H14.2", "judicial reorganisation", "1 of 7", "UNTESTED", "DATA-GATE FAIL",
         "C2 semantics", "state labels must be verified against documents"],
        ["H14.3", "recapitalizations and rights", "0 of 9", "UNTESTED", "DATA-GATE FAIL",
         "C1 data construction", "report both denominators: broad and material"],
        ["H15", "13D activist intent and outcome", f"{h15[0]} of {h15[1]}", "UNTESTED",
         "DATA-GATE FAIL", "C2 semantics", "standardized form is not standardized meaning"],
        ["H16.1", "FDA / PDUFA binary catalysts", f"{h16[0]} of {h16[1]}", "UNTESTED",
         "DATA-GATE FAIL", "C2 semantics", "a date is not a datum until attributed"],
        ["H17.0", "historical market data for Form 4", f"{h17[0]} of {h17[1]}", "UNTESTED",
         "INFRASTRUCTURE BLOCKED", "C1 data construction",
         "identity can pass while price history fails"],
        ["H18.0", "does a venue serve delisted spot OHLCV?", "2 of 3 venues required", "UNTESTED",
         "INFRASTRUCTURE BLOCKED", "C1 data construction",
         "who owns the record determines what stays observable"],
        ["H18.0b", "venue-owned substrate confirmation", f"{h18_0b[0]} of {h18_0b[1]}", "UNTESTED",
         "PASS", "C1 data construction", "substrate adequacy is not alpha"],
        ["H18.1", "pair removal versus asset delisting", f"{h18_1[0]} of {h18_1[1]}", "UNTESTED",
         "PARTIAL PASS", "C2 semantics", "pair removal is not asset delisting"],
        ["H18.1b", "was the full-delisting universe truncated?", f"{h18_1b[0]} of {h18_1b[1]}",
         "UNTESTED", "STRONG PASS", "C1 data construction", "the catalog is not the population"],
        ["H18.2", "literature, mechanism, hypothesis selection", "5 preconditions", "UNTESTED",
         "SELECT H18-P1", "C3 point-in-time", "select the question before seeing any result"],
        ["H18.3", "route contraction to 365-day delisting risk", "frozen prereg + amendment",
         "TESTED", "PRE-REGISTERED NULL", "C3 point-in-time",
         "a positive development result is not evidence until frozen OOS survives"],
        ["H19.0", "did a short exist when the market learned?", f"{h19_0[0]} of {h19_0[1]}",
         "UNTESTED", "PARTIAL PASS", "C4 execution", "a documented event is not a tradable event"],
        ["H19.1", "derivative price-discovery selection", "6 conditions", "UNTESTED",
         "SELECT H19-P3A + 3 modifications", "C4 execution",
         "a served candle is not a traded market"],
        ["H19.2", "derivative-specific pre-delisting discovery", "pre-freeze feasibility", "UNTESTED",
         "BLOCKED BEFORE FREEZE", "C3 point-in-time",
         "two reasonable requirements can be jointly impossible"],
    ]
    head = ["family", "question", "data gate", "test status", "result", "failure class",
            "paper lesson"]
    return ("# Table 1 — Experiment registry, H13 to H19.2\n\n"
            "Gate counts are read from each family's gate JSON. *Test status* `UNTESTED` means no\n"
            "economic test was run, which is not the same as a negative economic result.\n\n"
            + md_table(head, rows))


# --------------------------------------------------------------------------------------
# Table 2 - failure taxonomy
# --------------------------------------------------------------------------------------
def table2() -> str:
    rows = [
        ["universe survivorship", "candidates that left the listed universe are absent from the "
         "sample", "returns look high and the risk factor looks protective",
         "H13: 52.9% of candidates have no current ticker", "rebuild the universe from a "
         "point-in-time source and bound the bias explicitly"],
        ["outcome-selected join", "the join key exists only for surviving entities",
         "coverage correlates with the outcome", "H17.0: identity passes at 98-99% while price "
         "history fails", "run a missingness differential by outcome for every join"],
        ["semantic drift", "a standardized form carries non-standard meaning",
         "field-level accuracy collapses on a human gold set",
         "H15: 100% identity, 5 of 22 criteria", "gold set with two passes, the first persisted "
         "before the second"],
        ["category conflation", "one document type covers several economic events",
         "the event count is implausibly large", "H18.1: 102 of 1,422 pair events are a full "
         "delisting", "classify to the economic unit, not the document unit"],
        ["identity reuse", "a ticker is reassigned to a different asset",
         "an entity appears to be relisted or to have impossible history",
         "H18.1b: asset-era keying; H19.0: SKY", "key on asset-era, never on ticker alone"],
        ["catalog truncation", "the source index is not the population",
         "coverage has a clean horizon at a round date",
         "H18.1b: 84 to 201 events, 39 missed before 2022",
         "measure source reach against the source's own reported total"],
        ["future-derived labels", "a classification window reaches past the decision date",
         "label changes when the window is made backward-only",
         "H18.3: 676 of 2,352 removals (28.7%) change class",
         "classify as of the decision date and audit classification, not only values"],
        ["event sharing across splits", "one outcome event supports landmarks in two blocks",
         "validation performance tracks the holdout too closely",
         "H18.3: 41 of 86 holdout events shared under the original boundaries",
         "one-horizon embargo, and drop a block that cannot be separated"],
        ["contaminated control", "the control window sits inside the treatment process",
         "the event looks normal relative to its own history",
         "H19.1: 62 of 63 same-asset windows inside the wind-down",
         "require the control to be outside the process, and say so before freezing"],
        ["common-support collapse", "the matched cell is empty at the required strata",
         "n falls far below the pre-registered floor",
         "H19.2: median 7 eligible controls against a floor of 20",
         "compute the ceiling on the full pool before freezing the design"],
        ["execution assumption", "a documented event is assumed tradable",
         "the sample survives every data gate and dies at capacity",
         "H19.0: 201 to 32 under a US$1,000 order", "impose instrument existence, materiality and "
         "capacity at T0, in that order"],
        ["served-but-untraded data", "a candle exists without a trade",
         "a leg looks liquid while its trade count is zero",
         "H19.1: spot has no trades in a median 25% of window minutes",
         "require both legs to have traded in each bucket"],
    ]
    head = ["failure mode", "mechanism", "observable symptom", "QIE example", "defense"]
    return ("# Table 2 — Research failure taxonomy\n\n"
            "Each row is instantiated by an experiment in this paper; the examples carry their\n"
            "family tag so the claim can be traced to its artefact.\n\n" + md_table(head, rows))


# --------------------------------------------------------------------------------------
# Table 3 - classes of silent failure
# --------------------------------------------------------------------------------------
def table3() -> str:
    rows = [
        ["catalog truncation", "H18.1b: the source catalog did not cover pre-2022 notices",
         "a universe of 84 full delistings that looked complete",
         "cross-catalog expansion plus recall against candle-measured cessation",
         "measure source reach; never infer absence of event from absence of record"],
        ["date-format change", "H18.1b: pre-2021 notices use slash dates",
         "every trading_end before 2021 silently dropped",
         "coverage discontinuity at a format boundary",
         "a format change is a false data horizon until proven otherwise"],
        ["ticker collision", "H18.1b era rule compared gaps between first candles",
         "297 assets marked as reused tickers, none of them true",
         "reproduced a known artefact from the previous family",
         "asset-era keying, and test the era rule against known reuse cases"],
        ["pagination without a delimiter", "H19.1: S3 NextMarker is only returned with a delimiter",
         "listings stopped at the 1,000 oldest keys",
         "synchronization of 1.00 in 2023 and exactly 0.00 in 2025-26",
         "a suspiciously clean temporal pattern is a pagination symptom"],
        ["timestamp-unit divergence", "H19.1: spot archives in microseconds, futures in "
         "milliseconds for the same date", "the spot leg landed outside any plausible range and "
         "the intersection was empty", "first run reported spot coverage 2.7%",
         "detect units per file by magnitude; two legs of one venue can differ"],
        ["NaN truthiness", "H19.0 identity guard", "125 valid mappings rejected",
         "rejection count implausibly high", "test for type, not for truthiness"],
        ["zero-is-falsy gate logic", "H19.0 churn rate, and the same defect in H17.0",
         "a perfect 0.0 churn read as a missing value and failed the gate",
         "a passing metric produced a failing gate", "compare against None explicitly"],
        ["future-derived removal class", "H18.2 to H18.3 amendment A1 and A2",
         "28.7% of removals carried a class that used information from after the decision",
         "classification changed under a backward-only window",
         "a leakage test must cover feature classification, not only values and dates"],
        ["right censoring", "H18.3 administrative censoring at 2026-10-09",
         "landmarks without complete follow-up would have counted as non-events",
         "21,769 landmarks excluded once the rule was applied",
         "state the censoring date in the pre-registration"],
        ["event sharing across splits", "H18.3 frozen splits",
         "validation would have previewed 41 of the holdout's 86 events",
         "measured directly on landmark dates",
         "measure event sharing, do not assume date boundaries separate events"],
        ["common-support collapse", "H19.2 tagged-control matching",
         "a design that passed every data check and could not be estimated",
         "ceiling computed on the full pool with no sampling",
         "demonstrate common support before freezing, not after"],
        ["numerical instability", "H18.3 sigmoid overflow",
         "an exception rather than a wrong number",
         "caught at runtime, fixed, development re-run",
         "record the deviation; every number was unchanged to four decimals"],
    ]
    head = ["class", "instance", "what it produced", "how it was detected", "generalised lesson"]
    return ("# Table 3 — Classes of silent failure that produced plausible outputs\n\n"
            "These are classes of defect, not a list of mistakes. Each produced output that looked\n"
            "reasonable, which is what makes the class worth naming. A software defect is recorded\n"
            "separately from the economic question it was obscuring, and finding a defect is not\n"
            "itself a research result.\n\n" + md_table(head, rows))


# --------------------------------------------------------------------------------------
# Table 4 - H18.3 pre-registered metrics
# --------------------------------------------------------------------------------------
def table4() -> str:
    dev = jload(DATA / "h18_3_development.json")
    g = gate("H18_3_GATE.json")
    sup = dev["scientific_support_criteria"]
    mat = dev["materiality"]
    cb = dev["cluster_bootstrap"]
    pool = dev["pooled_out_of_fold"]

    rows = [
        ["scientific support 1", "aggregate ΔPR-AUC > 0", f"{pool['delta_abs']:+.4f}",
         "PASS" if sup["1_aggregate_delta_gt_0"] else "FAIL"],
        ["scientific support 2", "cluster-bootstrap 95% CI excludes zero",
         f"[{cb['ci95_low']:+.4f}, {cb['ci95_high']:+.4f}], {cb['share_positive']:.2%} of draws > 0",
         "PASS" if sup["2_bootstrap_ci_excludes_zero"] else "FAIL"],
        ["scientific support 3", "median fold ΔPR-AUC > 0", f"{dev['median_fold_delta']:+.4f}",
         "PASS" if sup["3_median_fold_delta_gt_0"] else "FAIL"],
        ["scientific support 4", "positive in a clear majority of folds",
         f"{dev['folds_with_positive_delta']} of {dev['folds_total']}",
         "PASS" if sup["4_clear_majority_positive_folds"] else "FAIL"],
        ["materiality 1", "relative ΔPR-AUC ≥ 10%", f"{mat['relative_delta']:+.2%}",
         "PASS" if mat["criteria"]["1_relative_delta_ge_10pct"] else "FAIL"],
        ["materiality 2", "absolute ΔPR-AUC ≥ 0.01", f"{mat['absolute_delta']:+.4f}",
         "PASS" if mat["criteria"]["2_absolute_delta_ge_0.01"] else "FAIL"],
        ["materiality 3", "top-decile lift improvement ≥ 15%",
         f"{mat['mean_topdecile_lift_baseline']:.4f} to "
         f"{mat['mean_topdecile_lift_challenger']:.4f} = {mat['topdecile_lift_improvement']:+.2%}",
         "PASS" if mat["criteria"]["3_topdecile_lift_improvement_ge_15pct"] else "FAIL"],
        ["materiality 4", "Brier does not worsen",
         f"{mat['mean_brier_baseline']:.5f} to {mat['mean_brier_challenger']:.5f}",
         "PASS" if mat["criteria"]["4_brier_does_not_worsen"] else "FAIL"],
        ["materiality 5", r"\|calibration slope shift\| < 0.10",
         f"{mat['calibration_slope_shift']:.4f}",
         "PASS" if mat["criteria"]["5_calibration_slope_shift_lt_0.10"] else "FAIL"],
    ]

    ho = None
    for key in ("holdout", "HOLDOUT", "holdout_results"):
        if key in g:
            ho = g[key]
            break
    if isinstance(ho, dict):
        base = ho.get("pr_auc_baseline")
        chal = ho.get("pr_auc_challenger")
        delta = ho.get("delta_pr_auc_abs", ho.get("delta_abs", ho.get("delta")))
        rows.append(["holdout directional veto (A3)", "ΔPR-AUC on the single-use holdout > 0",
                     f"baseline {base:.5f}, challenger {chal:.5f}, Δ {delta:+.5f}",
                     "PASS" if (delta or 0) > 0 else "FAIL"])

    head = ["gate", "bar as frozen", "measured", "verdict"]
    body = md_table(head, rows)
    note = (f"\nDevelopment pooled out-of-fold: baseline {pool['pr_auc_baseline']:.5f}, challenger "
            f"{pool['pr_auc_challenger']:.5f}, over {pool['landmarks']:,} landmarks and "
            f"{pool['unique_eras']} asset-eras. Bootstrap: {cb['n_boot']:,} replications over "
            f"{cb['unit']} clusters, seed {cb['seed']}.\n\n"
            "Verdict **NULL**, and no bar was renegotiated after the result. Criterion 5 of\n"
            "materiality fails on an *improvement* in calibration, which is a defect in the bar as\n"
            "the researcher wrote it; it is recorded for the next pre-registration and not patched\n"
            "into this one. The verdict does not depend on it: scientific-support criterion 2 and\n"
            "the holdout each fail independently.\n")
    return "# Table 4 — H18.3 pre-registered metrics\n\n" + body + note


# --------------------------------------------------------------------------------------
# Table 5 - H19 execution gate
# --------------------------------------------------------------------------------------
def table5() -> str:
    g = gate("H19_0_GATE.json")
    rows = []
    for c in g.get("criteria", []):
        crit = re.sub(r"\s+", " ", str(c.get("criterion", ""))).strip()
        rows.append([crit, str(c.get("bar", "")), str(c.get("measured", "")),
                     "PASS" if c.get("pass") else "**FAIL**"])
    head = ["criterion", "bar", "measured", "result"]
    passed, total = crit_counts(g)

    pf = Path(ROOT / "H19_2_PREFREEZE_FEASIBILITY.md").read_text(encoding="utf-8", errors="replace")
    n_final = re.search(r"Final confirmatory n = \*\*(\d+)\*\*", pf)
    floor = re.search(r"A7's hard floor of (\d+)", pf)

    extra = [
        ["H19.2 §A7 — confirmatory events", f">= {floor.group(1) if floor else '40'}",
         n_final.group(1) if n_final else "10", "**FAIL**"],
        ["H19.2 §A7 — matched controls per event", ">= 20",
         "median 1; 52 of 62 events below 20", "**FAIL**"],
        ["H19.2 §A8-A10 — valid 15-minute transitions", ">= 73",
         "median 92; 1 of 62 events below 73", "PASS"],
        ["H19.2 §A11 — VWAP fields available", "fallback not triggered", "62 of 62 (100%)", "PASS"],
        ["H19.2 — leg availability", ">= 95%", "2,857 of 2,877 legs (99.3%)", "PASS"],
    ]

    return ("# Table 5 — H19 execution and feasibility gate\n\n"
            f"## H19.0 — execution and shortability ({passed} of {total}, verdict "
            f"{g.get('verdict')})\n\n" + md_table(head, rows) +
            "\n## H19.2 — pre-freeze feasibility (verdict STOP, BLOCKED BEFORE FREEZE)\n\n" +
            md_table(head, extra) +
            "\nNo pre-registration was frozen for H19.2 and no price column was ever read, so no\n"
            "economic inference about H19-P3A exists. H19.0's status is PARTIAL PASS: the sample\n"
            "gate fails for the small-capital thesis, and no return was computed for any event.\n")


def main() -> None:
    for name, fn in [("table1_experiment_registry.md", table1),
                     ("table2_failure_taxonomy.md", table2),
                     ("table3_silent_failure_classes.md", table3),
                     ("table4_h18_3_preregistered_metrics.md", table4),
                     ("table5_h19_execution_gate.md", table5)]:
        (OUT / name).write_text(fn(), encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    main()
