"""Build every paper table and figure deterministically from frozen Contextual Alpha outputs.

Reads only committed / frozen artefacts (H20.0 gate, H20.1 gate and registries, H20.2 A02 specs,
H20.3 results) plus the frozen H20.3 primary out-of-fold predictions. Nothing is refit, rescored or
re-tuned. The only recomputation is the H20.3 two-way bootstrap distribution for Figure 5, regenerated
with the frozen seed and procedure from the frozen predictions; the script refuses to write the figure
unless the recomputed 95% interval equals the frozen one.

    .venv/Scripts/python "Contextual Alpha/paper/scripts/build_paper_assets.py"

Writes paper/tables/*.csv|*.md, paper/figures/*.png|*.pdf and paper/PAPER_DATA_MANIFEST.json.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

PAPER = Path(__file__).resolve().parents[1]
CA = PAPER.parent
sys.path.insert(0, str(CA / "scripts"))
TAB, FIG = PAPER / "tables", PAPER / "figures"

# validated two-series palette (dataviz reference instance, light mode): M0 blue, M2 orange; neutral ink
C_M0, C_M2 = "#2a78d6", "#eb6834"
INK, INK2, GRID, MUTED = "#0b0b0b", "#52514e", "#e4e3df", "#a3a29c"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
    "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "legend.frameon": False,
})
INPUTS: dict[str, Path] = {}


def load(name: str) -> dict:
    p = CA / name
    INPUTS[name] = p
    return json.loads(p.read_text(encoding="utf-8"))


def csv_in(name: str) -> pd.DataFrame:
    p = CA / name
    INPUTS[name] = p
    return pd.read_csv(p)


MINUS = "\u2212"


def cell(v, dec: int | None = None, signed: bool = False) -> str:
    """Markdown cell: fixed decimals where given, and a true minus sign, as in the manuscript text."""
    if isinstance(v, float) and np.isnan(v):
        return ""
    if dec is not None and isinstance(v, (int, float, np.floating)) and not isinstance(v, bool):
        s = f"{v:+.{dec}f}" if signed else f"{v:.{dec}f}"
    else:
        s = str(v)
    return MINUS + s[1:] if s.startswith("-") else s


def save_table(df: pd.DataFrame, stem: str, caption: str, fmt: dict | None = None) -> None:
    """CSV keeps raw values; the Markdown copy prints fixed decimals per column (fmt: col -> (dec, signed))."""
    df.to_csv(TAB / f"{stem}.csv", index=False, lineterminator="\n")
    cols = list(df.columns)
    fmt = fmt or {}
    md = [f"**{caption}**", "", "| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for r in df.itertuples(index=False):
        md.append("| " + " | ".join(cell(v, *fmt.get(c, (None, False))) for c, v in zip(cols, r)) + " |")
    (TAB / f"{stem}.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")


def savefig(fig, stem: str) -> None:
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"{stem}.{ext}", metadata={"CreationDate": None} if ext == "pdf" else None)
    plt.close(fig)


def f4(x: float) -> str:
    return f"{x:+.4f}" if x < 0 or x > 0 else "0.0000"


# ============================================================= tables
def tables() -> dict:
    g0, g1 = load("H20_0_GATE.json"), load("H20_1_GATE.json")
    t1 = []
    names = {"C1": "Macro", "C2": "Political / regulatory", "C3": "Crypto-systemic", "C4": "Exchange-specific", "C5": "Asset-specific"}
    for k, v in g0["layers"].items():
        c = v["criteria"]
        g7 = c.get("G7_entity", {}).get("value")
        t1.append({"layer": f"{k} {names[k]}", "G4 version share": round(c["G4_version"]["value"], 3),
                   "G7 entity resolution": round(g7, 3) if g7 is not None else "n/a",
                   "failed criteria": ", ".join(v["failed"]) or "none",
                   "severe biases": "; ".join(v["severe_bias"]) or "none",
                   "H20.0 status": "DATA-GATE FAIL / UNTESTED" if v["layer_verdict"] == "FAIL" else "CONDITIONAL (reconstructible)"})
    save_table(pd.DataFrame(t1), "table1_context_layers", "Table 1. Context layers and H20.0 data-gate status")

    elig = csv_in("evidence/H20_1_FEATURE_ELIGIBILITY.csv")
    t2 = []
    for fam, v in g1["families"].items():
        t2.append({"family": fam, "H20.1 verdict": v["verdict"], "built": len(v["features_built"]), "eligible": len(v["eligible"]),
                   "ineligible (criterion)": "; ".join(f"{k}: {r}" for k, r in v["ineligible"].items()) or "none"})
    save_table(pd.DataFrame(t2), "table2_representation_families", "Table 2. Representation families and H20.1 eligibility")
    save_table(elig[["feature_id", "feature_name", "layer", "family", "eligible_h20_2", "failed_criteria"]],
               "tableA1_feature_eligibility", "Table A1. H20.1 feature-level eligibility")

    sp = load("H20_2_TEMPORAL_SPLIT_A02.json")
    ta = load("H20_3_TARGET_AUDIT.json")
    eu = ta["effective_units"]
    t3 = [
        {"block": "DEVELOPMENT", "landmark Mondays": f"{sp['blocks']['DEVELOPMENT']['first_landmark_monday']} to {sp['blocks']['DEVELOPMENT']['last_landmark_monday']}",
         "landmark rows": eu["DEVELOPMENT"]["rows"], "asset-eras": eu["DEVELOPMENT"]["asset_eras"], "weeks": eu["DEVELOPMENT"]["weeks"],
         "unique events": eu["DEVELOPMENT"]["unique_positive_events"], "positive landmark rate": f"{100*eu['DEVELOPMENT']['base_rate']:.2f}%"},
        {"block": "EMBARGO (dropped)", "landmark Mondays": f"{sp['blocks']['EMBARGO_DROPPED']['first_landmark_monday']} to {sp['blocks']['EMBARGO_DROPPED']['last_landmark_monday']}",
         "landmark rows": "not built", "asset-eras": "", "weeks": sp["blocks"]["EMBARGO_DROPPED"]["n_weeks"], "unique events": "", "positive landmark rate": ""},
        {"block": "LCUV", "landmark Mondays": f"{sp['blocks']['LOCKED_CONTEXT_UNSEEN_VALIDATION']['first_landmark_monday']} to {sp['blocks']['LOCKED_CONTEXT_UNSEEN_VALIDATION']['last_landmark_monday']}",
         "landmark rows": eu["LOCKED_CONTEXT_UNSEEN_VALIDATION"]["rows"], "asset-eras": eu["LOCKED_CONTEXT_UNSEEN_VALIDATION"]["asset_eras"],
         "weeks": eu["LOCKED_CONTEXT_UNSEEN_VALIDATION"]["weeks"], "unique events": eu["LOCKED_CONTEXT_UNSEEN_VALIDATION"]["unique_positive_events"],
         "positive landmark rate": f"{100*eu['LOCKED_CONTEXT_UNSEEN_VALIDATION']['base_rate']:.2f}%"},
        {"block": "PROSPECTIVE_CONFIRMATION (unopened)", "landmark Mondays": f"{sp['blocks']['PROSPECTIVE_CONFIRMATION']['first_landmark_monday']} to {sp['blocks']['PROSPECTIVE_CONFIRMATION']['last_landmark_monday']}",
         "landmark rows": "not built", "asset-eras": "", "weeks": sp["blocks"]["PROSPECTIVE_CONFIRMATION"]["n_weeks"], "unique events": "", "positive landmark rate": ""},
    ]
    save_table(pd.DataFrame(t3), "table3_design_effective_units", "Table 3. Temporal design and effective sample size")

    dev, lc, bs = load("H20_3_DEVELOPMENT_RESULTS.json"), load("H20_3_LCUV_RESULTS.json"), load("H20_3_BOOTSTRAP_RESULTS.json")
    lab = {"M0": "M0 market", "M2": "M2 market + context", "M1": "M1 context only", "M2_core": "M2_core market + CONTEXT_CORE",
           "M1_core": "M1_core CONTEXT_CORE only"}
    role = {"M0": "primary", "M2": "primary", "M1": "secondary", "M2_core": "robustness", "M1_core": "robustness"}

    def arm_rows(res: dict) -> pd.DataFrame:
        rows = []
        for a in ("M0", "M2", "M1", "M2_core", "M1_core"):
            m = res[a]
            rows.append({"arm": lab[a], "role": role[a], "PR-AUC": round(m["pr_auc"], 4), "ROC-AUC": round(m["roc_auc"], 3),
                         "Brier": round(m["brier"], 4), "top-decile lift (within-week)": round(m["top_decile_lift_xsec"], 2),
                         "within-week PR-AUC": round(m["within_week_pr_auc"], 3), "calibration slope": round(m["calibration"]["slope"], 2)})
        return pd.DataFrame(rows)

    arm_fmt = {"PR-AUC": (4, False), "ROC-AUC": (3, False), "Brier": (4, False), "top-decile lift (within-week)": (2, False),
               "within-week PR-AUC": (3, False), "calibration slope": (2, False)}

    save_table(arm_rows(dev["pooled_oof"]), "table4_development_results",
               "Table 4. Development pooled out-of-fold results (L2 logistic, \u03bb = 10)", arm_fmt)
    folds = pd.DataFrame([{"fold": f["fold"], "test era": f["era"], "test events": f["units_test"]["unique_positive_events"],
                           "test rows": f["units_test"]["rows"], "PR-AUC M0": round(f["arms"]["M0"]["pr_auc"], 4),
                           "PR-AUC M2": round(f["arms"]["M2"]["pr_auc"], 4), "\u0394 (M2 \u2212 M0)": round(f["delta_M2_M0"], 4),
                           "\u0394 (M2_core \u2212 M0)": round(f["delta_M2core_M0"], 4)} for f in dev["folds"]])
    save_table(folds, "tableA2_fold_results", "Table A2. Fold-level development results (primary model)",
               {"PR-AUC M0": (4, False), "PR-AUC M2": (4, False), "\u0394 (M2 \u2212 M0)": (4, True),
                "\u0394 (M2_core \u2212 M0)": (4, True)})
    save_table(arm_rows(lc["metrics"]), "table5_lcuv_results",
               "Table 5. LOCKED_CONTEXT_UNSEEN_VALIDATION (2025) results, scored once (L2 logistic, \u03bb = 10)", arm_fmt)

    vd = load("H20_3_VERDICT.json")
    desc = {"S1": "development pooled-OOF \u0394 > 0", "S2": "\u2265 5 of 8 folds with \u0394 > 0",
            "S3": "two-way bootstrap 95% CI lower bound > 0", "S4": "LCUV \u0394 > 0",
            "S5": "no severe calibration deterioration on LCUV (Brier ratio \u2264 1.05; slope excess \u2264 0.20)",
            "S6": "PIT audit passes",
            "S7": "\u0394 > 0 in \u2265 2 of 3 era blocks (2022 folds, 2023 folds, LCUV) and leave-one-fold-out \u0394 > 0"}
    c = vd["criteria"]
    val = {"S1": f4(c["S1"]["value"]), "S2": f"{c['S2']['value']} of 8", "S3": f"[{c['S3']['value'][0]:+.4f}, {c['S3']['value'][1]:+.4f}]",
           "S4": f4(c["S4"]["value"]), "S5": f"Brier ratio {c['S5']['value']['brier_ratio']:.3f}; slope excess {c['S5']['value']['slope_excess']:+.3f}",
           "S6": "all stages PASS", "S7": f"{c['S7']['value']['positive_era_blocks']} of 3 era blocks positive; min leave-one-fold-out \u0394 {c['S7']['value']['lofo_min_delta']:+.4f}"}
    val = {k: v.replace("-0", MINUS + "0") for k, v in val.items()}
    t6 = pd.DataFrame([{"criterion": k, "condition": desc[k], "observed": val[k], "result": "PASS" if c[k]["PASS"] else "FAIL"} for k in desc])
    t6.loc[len(t6)] = {"criterion": "verdict", "condition": "closed list, applied mechanically", "observed": vd["verdict"], "result": ""}
    save_table(t6, "table6_verdict", "Table 6. Pre-registered criteria S1\u2013S7 and the mechanical verdict")

    ex = load("H20_3_EXPLORATORY_RESULTS.json")
    fold_mean = lambda key: float(np.mean([f[key] for f in dev["folds"]]))  # noqa: E731
    lsl, lgd, lgs = ex["logistic_selected_lambda"], ex["lightgbm_default"], ex["lightgbm_selected"]

    def lgb_cfg(c: dict) -> str:
        return f"{c['num_leaves']} leaves, {c['n_estimators']} trees"

    def lgb_sel_mean(arm: str) -> float:
        sel = lgs[arm]["config"]
        return next(x["mean"] for x in lgs[arm]["mean_fold_pr_auc_by_config"] if x["config"] == sel)

    def lam_mean(arm: str) -> float:
        return lsl[arm]["mean_fold_pr_auc_by_lambda"][str(lsl[arm]["selected"])]

    ci_core = bs["robustness_M2core_vs_M0"]["two_way"]["ci95"]
    t7 = [
        {"analysis": "primary: logistic, \u03bb = 10 (A02)", "status": "primary",
         "development \u0394, pooled OOF": dev["delta_pr_auc_M2_M0"], "development \u0394, mean of folds": fold_mean("delta_M2_M0"),
         "LCUV \u0394": lc["delta_pr_auc_M2_M0"], "note": "verdict: PRE-REGISTERED NULL"},
        {"analysis": "CONTEXT_CORE (classifier-free), \u03bb = 10", "status": "robustness",
         "development \u0394, pooled OOF": dev["delta_pr_auc_M2core_M0"], "development \u0394, mean of folds": fold_mean("delta_M2core_M0"),
         "LCUV \u0394": lc["delta_pr_auc_M2core_M0"],
         "note": f"two-way CI [{cell(ci_core[0], 3, True)}, {cell(ci_core[1], 3, True)}]; {dev['positive_folds_M2core_M0']} of 8 folds positive"},
        {"analysis": "logistic, fold-selected \u03bb (the v1 primary rule)", "status": "exploratory",
         "development \u0394, pooled OOF": lsl["delta_dev_M2_M0"],
         "development \u0394, mean of folds": lam_mean("M2") - lam_mean("M0"),
         "LCUV \u0394": lsl["delta_lcuv_M2_M0"],
         "note": f"\u03bb = {lsl['M0']['selected']:g} selected for both M0 and M2; verdict under the v1 rule: PRE-REGISTERED NULL (S4 fails)"},
        {"analysis": "LightGBM, a-priori configuration", "status": "exploratory",
         "development \u0394, pooled OOF": lgd["delta_dev_M2_M0"],
         "development \u0394, mean of folds": lgd["M2"]["mean_fold_pr_auc"] - lgd["M0"]["mean_fold_pr_auc"],
         "LCUV \u0394": lgd["delta_lcuv_M2_M0"],
         "note": f"{lgb_cfg(lgd['M0']['config'])} for every arm; M0 pooled PR-AUC {lgd['M0']['dev_pooled_oof_pr_auc']:.3f}"},
        {"analysis": "LightGBM, fold-selected", "status": "exploratory",
         "development \u0394, pooled OOF": lgs["delta_dev_M2_M0"],
         "development \u0394, mean of folds": lgb_sel_mean("M2") - lgb_sel_mean("M0"),
         "LCUV \u0394": lgs["delta_lcuv_M2_M0"],
         "note": f"selected: M0 {lgb_cfg(lgs['M0']['config'])}; M2 {lgb_cfg(lgs['M2']['config'])}"},
    ]
    dfmt = {"development \u0394, pooled OOF": (4, True), "development \u0394, mean of folds": (4, True), "LCUV \u0394": (4, True)}
    save_table(pd.DataFrame(t7), "table7_robustness_exploratory",
               "Table 7. Primary, robustness and exploratory results (only the primary determines the verdict)", dfmt)

    grid = lsl["M0"]["mean_fold_pr_auc_by_lambda"]
    pooled = {10.0: dev["delta_pr_auc_M2_M0"], float(lsl["M0"]["selected"]): lsl["delta_dev_M2_M0"]}
    t8 = [{"\u03bb": f"{float(k):g}" + (" (primary)" if float(k) == 10.0 else ""),
           "M0 PR-AUC, mean of folds": grid[k], "M2 PR-AUC, mean of folds": lsl["M2"]["mean_fold_pr_auc_by_lambda"][k],
           "\u0394, mean of folds": lsl["M2"]["mean_fold_pr_auc_by_lambda"][k] - grid[k],
           "\u0394, pooled OOF": pooled.get(float(k), float("nan"))} for k in grid]
    save_table(pd.DataFrame(t8), "table8_penalty_path",
               "Table 8. Development \u0394 along the frozen \u03bb grid (logistic; read from the frozen exploratory run, no refit; "
               "pooled values exist only for \u03bb = 10 and the selected \u03bb)",
               {"M0 PR-AUC, mean of folds": (4, False), "M2 PR-AUC, mean of folds": (4, False), "\u0394, mean of folds": (4, True),
                "\u0394, pooled OOF": (4, True)})
    return {"dev": dev, "lc": lc, "bs": bs, "vd": vd, "g0": g0, "g1": g1, "sp": sp, "ta": ta, "ex": ex, "elig": elig}


# ============================================================= figures
def fig_funnel(d: dict) -> None:
    g1 = d["g1"]
    n_built = sum(len(v["features_built"]) for v in g1["families"].values())
    n_elig = len(g1["eligible_for_h20_2"])
    stages = [
        ("Candidate context", "5 layers\nC1 macro, C2 political/regulatory,\nC3 crypto-systemic, C4 exchange, C5 asset", None),
        ("H20.0 PIT data gate", "3 layers reconstructible (conditional)\nC1, C2 (US-only), C3 (metadata only)", "C4, C5: DATA-GATE FAIL / UNTESTED"),
        ("H20.1 representation gate", f"{n_built} features built -> {n_elig} eligible\nR4 PASS, R1/R2 PARTIAL PASS", "R3 text (LLM, embeddings, TF-IDF): not PIT-safe\nGDELT (4), CFTC, redundant, degenerate: ineligible"),
        ("H20.2 pre-registration", "18 context features (CONTEXT_EXPANDED)\n10 classifier-free (CONTEXT_CORE)\n23 market features; lambda = 10 frozen", None),
        ("H20.3 predictive test", "M2 vs M0, outcomes opened once\nverdict: PRE-REGISTERED NULL", None),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.set_axis_off()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(stages) * 1.0)
    for i, (title, body, drop) in enumerate(stages):
        y = len(stages) - 1 - i
        w = 5.6 - 0.45 * i
        x0 = 0.2 + (5.6 - w) / 2
        ax.add_patch(FancyBboxPatch((x0, y + 0.06), w, 0.86, boxstyle="round,pad=0.02,rounding_size=0.06", fc="#f1f0ec", ec=INK2, lw=0.8))
        ax.text(x0 + w / 2, y + 0.80, title, ha="center", va="center", fontsize=9, fontweight="bold", color=INK)
        ax.text(x0 + w / 2, y + 0.66, body, ha="center", va="top", fontsize=7.2, color=INK2, linespacing=1.3)
        if drop:
            ax.annotate("", xy=(6.25, y + 0.5), xytext=(x0 + w + 0.05, y + 0.5), arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.9))
            ax.text(6.35, y + 0.5, drop, ha="left", va="center", fontsize=7.0, color=INK2, linespacing=1.25)
    savefig(fig, "figure1_research_funnel")


def fig_timeline(d: dict) -> None:
    b = d["sp"]["blocks"]
    rows = [("DEVELOPMENT\n(8 rolling-origin folds)", "DEVELOPMENT", "#c9c8c2"), ("EMBARGO\n(dropped)", "EMBARGO_DROPPED", "#ecebe6"),
            ("LCUV\n(scored once)", "LOCKED_CONTEXT_UNSEEN_VALIDATION", "#8f8e88"),
            ("PROSPECTIVE_CONFIRMATION\n(unopened)", "PROSPECTIVE_CONFIRMATION", "#ffffff")]
    fig, ax = plt.subplots(figsize=(7.2, 1.9))
    ypos = {"DEVELOPMENT": 0.30, "EMBARGO_DROPPED": 0.30, "LOCKED_CONTEXT_UNSEEN_VALIDATION": 0.95, "PROSPECTIVE_CONFIRMATION": 0.30}
    for i, (lab, k, fc) in enumerate(rows):
        a, z = pd.Timestamp(b[k]["first_landmark_monday"]), pd.Timestamp(b[k]["last_landmark_monday"])
        ax.barh(0, (z - a).days + 7, left=a, height=0.5, color=fc, edgecolor=INK2, lw=0.8, hatch="////" if "PROSPECTIVE" in k else None)
        mid = a + (z - a) / 2
        if k == "PROSPECTIVE_CONFIRMATION":
            mid = a
        text = " ".join(lab.split("\n")) if k == "LOCKED_CONTEXT_UNSEEN_VALIDATION" else lab
        ax.text(mid, ypos[k], text, ha="left" if k == "PROSPECTIVE_CONFIRMATION" else "center", va="bottom", fontsize=7, color=INK)
        if k == "LOCKED_CONTEXT_UNSEEN_VALIDATION":
            ax.plot([mid, mid], [0.25, 0.92], color=MUTED, lw=0.7)
    for f in d["sp"]["folds"]:
        a, z = pd.Timestamp(f["test_from"]), pd.Timestamp(f["test_to"])
        ax.barh(-0.55, (z - a).days, left=a, height=0.22, color=C_M0, edgecolor="#fcfcfb", lw=0.8)
    ax.text(pd.Timestamp("2021-12-20"), -0.55, "fold test windows", ha="right", va="center", fontsize=7, color=INK2)
    ax.set_yticks([])
    ax.set_ylim(-0.85, 1.35)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("landmark week (decision time t = landmark Monday + 1 day, 00:00 UTC)")
    savefig(fig, "figure3_timeline")


def fig_primary(d: dict) -> None:
    dev, lc = d["dev"], d["lc"]
    vals = {"Development\n(pooled OOF, 8 folds)": (dev["pooled_oof"]["M0"]["pr_auc"], dev["pooled_oof"]["M2"]["pr_auc"]),
            "LCUV 2025\n(scored once)": (lc["metrics"]["M0"]["pr_auc"], lc["metrics"]["M2"]["pr_auc"])}
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    x = np.arange(len(vals))
    w = 0.34
    for j, (lab, col) in enumerate((("M0 market", C_M0), ("M2 market + context", C_M2))):
        v = [vv[j] for vv in vals.values()]
        bars = ax.bar(x + (j - 0.5) * (w + 0.02), v, width=w, color=col, label=lab)
        for bx, vv in zip(bars, v):
            ax.text(bx.get_x() + bx.get_width() / 2, vv + 0.006, f"{vv:.4f}", ha="center", va="bottom", fontsize=7, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(list(vals))
    ax.set_ylabel("PR-AUC")
    ax.set_ylim(0, 0.40)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", fontsize=7.5)
    for i, (m0, m2) in enumerate(vals.values()):
        ax.text(i, max(m0, m2) + 0.035, f"Delta = {m2 - m0:+.4f}", ha="center", fontsize=7.5, color=INK2)
    savefig(fig, "figure4_primary_pr_auc")


def fig_folds(d: dict) -> None:
    f = d["dev"]["folds"]
    fig, ax = plt.subplots(figsize=(5.4, 2.8))
    x = [r["fold"] for r in f]
    y = [r["delta_M2_M0"] for r in f]
    ax.bar(x, y, width=0.6, color=C_M2)
    ax.axhline(0, color=INK, lw=0.8)
    for xi, yi, r in zip(x, y, f):
        ax.text(xi, yi + (0.0006 if yi >= 0 else -0.0006), f"{yi:+.4f}", ha="center", va="bottom" if yi >= 0 else "top", fontsize=6.5, color=INK)
        ax.text(xi, -0.0175, f"{r['units_test']['unique_positive_events']} ev", ha="center", fontsize=6.3, color=INK2)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r['fold']}\n{r['era']}" for r in f], fontsize=7)
    ax.set_ylabel("Delta PR-AUC (M2 - M0)")
    ax.set_ylim(-0.019, 0.011)
    ax.grid(axis="x", visible=False)
    ax.set_xlabel(f"development fold (test quarter); positive folds: {d['dev']['positive_folds_M2_M0']} of 8")
    savefig(fig, "figure5_fold_delta")


def fig_bootstrap(d: dict) -> None:
    import h20_3_model as hm

    p = CA / "data/derived/h20_3/oof_predictions_primary.parquet"
    src = p if p.exists() else CA / "evidence/H20_3_OOF_PREDICTIONS_PRIMARY.csv"
    INPUTS[str(src.relative_to(CA)).replace("\\", "/")] = src
    O = pd.read_parquet(src) if src.suffix == ".parquet" else pd.read_csv(src)
    rng = np.random.default_rng(hm.SEED_BOOT)
    y = O["y"].to_numpy(float)
    _, ei = np.unique(O["asset_era_id"].to_numpy(), return_inverse=True)
    _, bi = np.unique(O["fold"].to_numpy(), return_inverse=True)
    ne, nb = ei.max() + 1, bi.max() + 1
    out = []
    while len(out) < hm.B:
        m = np.bincount(rng.integers(0, ne, ne), minlength=ne)
        n = np.bincount(rng.integers(0, nb, nb), minlength=nb)
        w = m[ei] * n[bi]
        if (w * y).sum() <= 0:
            continue
        out.append(hm.ap(y, O["p_M2"].to_numpy(), w) - hm.ap(y, O["p_M0"].to_numpy(), w))
    dd = np.array(out)
    ci = [float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))]
    frozen = d["bs"]["primary_M2_vs_M0"]["two_way"]["ci95"]
    if not np.allclose(ci, frozen, atol=1e-12):
        raise SystemExit(f"recomputed CI {ci} != frozen {frozen}; refusing to draw Figure 5")
    fig, ax = plt.subplots(figsize=(5.4, 2.8))
    ax.hist(dd, bins=60, color=MUTED, edgecolor="#fcfcfb", lw=0.4)
    for v in ci:
        ax.axvline(v, color=INK2, lw=0.9, ls="--")
    ax.axvline(0, color=INK, lw=0.8)
    pt = d["dev"]["delta_pr_auc_M2_M0"]
    ax.axvline(pt, color=C_M2, lw=1.6)
    ax.text(pt, ax.get_ylim()[1] * 0.97, f"point {pt:+.4f} ", color=INK, fontsize=7, va="top", ha="right")
    ax.text(ci[0], ax.get_ylim()[1] * 0.80, f"2.5% {ci[0]:+.4f} ", color=INK2, fontsize=7, ha="right", va="top")
    ax.text(ci[1], ax.get_ylim()[1] * 0.80, f" 97.5% {ci[1]:+.4f}", color=INK2, fontsize=7, ha="left", va="top")
    ax.set_xticks(np.arange(-0.10, 0.101, 0.05))
    ax.set_xlabel("bootstrap Delta PR-AUC (M2 - M0), development pooled OOF")
    ax.set_ylabel("replicates")
    ax.grid(axis="x", visible=False)
    savefig(fig, "figure6_bootstrap_delta")
    d["bootstrap_recomputed_ci"] = ci


def fig_survival(d: dict) -> None:
    e = d["elig"]
    reason = []
    for r in e.itertuples():
        fc = str(r.failed_criteria) if isinstance(r.failed_criteria, str) else ""
        reason.append("eligible" if r.eligible_h20_2 else ("semantic defect" if "semantic" in fc else ("redundant" if "REDUNDANT" in fc else
                      ("coverage" if "coverage" in fc else "other"))))
    e = e.assign(status=reason)
    tab = e.groupby(["layer", "status"]).size().unstack(fill_value=0)
    order = [c for c in ("eligible", "semantic defect", "coverage", "redundant", "other") if c in tab.columns]
    cols = {"eligible": C_M0, "semantic defect": "#8f8e88", "coverage": "#c9c8c2", "redundant": "#ecebe6", "other": "#ffffff"}
    fig, ax = plt.subplots(figsize=(5.4, 2.6))
    left = np.zeros(len(tab))
    for c in order:
        v = tab[c].to_numpy()
        ax.barh(tab.index, v, left=left, color=cols[c], edgecolor="#fcfcfb" if c == "eligible" else INK2, lw=0.6, label=c, height=0.55)
        for yi, (l0, vv) in enumerate(zip(left, v)):
            if vv:
                ax.text(l0 + vv / 2, yi, str(vv), ha="center", va="center", fontsize=7, color="#ffffff" if c == "eligible" else INK)
        left += v
    ax.invert_yaxis()
    ax.set_xlabel("H20.1 features built (25), by outcome of the representation gate")
    ax.grid(axis="y", visible=False)
    ax.legend(ncol=4, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.32))
    savefig(fig, "figure2_feature_survival")


def main() -> int:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    d = tables()
    fig_funnel(d)
    fig_timeline(d)
    fig_primary(d)
    fig_folds(d)
    fig_bootstrap(d)
    fig_survival(d)
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
    man = {"generator": "paper/scripts/build_paper_assets.py", "generator_sha256": sha(__file__),
           "inputs": {k: sha(v) for k, v in sorted(INPUTS.items())},
           "outputs": {str(p.relative_to(PAPER)).replace("\\", "/"): sha(p) for p in sorted(list(TAB.glob("*")) + list(FIG.glob("*.png")))},
           "bootstrap_recomputed_ci_equals_frozen": d["bootstrap_recomputed_ci"],
           "note": "figures in PDF are regenerated alongside PNG; PNG hashes are recorded (PDF embeds renderer metadata)",
           "frozen_commits": {"H20.0": "a14c347", "H20.1": "e21c264", "H20.2+A02": "9932e20", "H20.3": "180def4"}}
    (PAPER / "PAPER_DATA_MANIFEST.json").write_text(json.dumps(man, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({"tables": len(list(TAB.glob('*.csv'))), "figures": len(list(FIG.glob('*.png'))), "ci": d["bootstrap_recomputed_ci"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
