"""H20.3 P5-P6 — development folds, bootstrap, pre-LCUV freeze, single LCUV scoring, exploratory.

  --part dev        primary L2 logistic at the frozen lambda = 10 for M0, M1, M2, M1_core, M2_core on the
                    8 frozen folds; OOF predictions; metrics; pigeonhole bootstrap (seed 20261103,
                    2,000 replicates); final development refits; writes H20_3_DEVELOPMENT_RESULTS.json,
                    H20_3_BOOTSTRAP_RESULTS.json and H20_3_PRE_LCUV_FREEZE.json. Reads no LCUV row label
                    or prediction.
  --part lcuv       ONE run only (lock file): scores the LCUV block with the frozen primary fits, writes
                    and hashes H20_3_LCUV_RESULTS.json. A second run is refused (DATA / DESIGN FAILURE).
  --part explore    only after the LCUV primary results are hashed: selected-lambda logistic and
                    LightGBM (a-priori default and fold-selected), labelled EXPLORATORY.

Implementation follows H20_2_MODEL_SPEC_A02.json / H20_2_METRICS_SPEC_A02.json /
H20_2_VERDICT_RULES_A02.json exactly. No return, P&L or trading quantity is computed.
"""

from __future__ import annotations

import json
import math
import sys

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from h20_3_common import CA, LCUV, OUT, iso, now_utc, p0, sha256_file, spec, write_json

LAM = 10.0
SEED_BOOT = 20261103
SEED_LGB = 20261104
B = 2000
ARMS = ["M0", "M1", "M2", "M1_core", "M2_core"]
LOCK = OUT / "LCUV_PRIMARY_RUN.lock"


# =============================================================== data
def load_xy() -> tuple[pd.DataFrame, dict, dict]:
    seal = json.loads((CA / "H20_3_X_SEAL.json").read_text(encoding="utf-8"))
    yseal = json.loads((CA / "H20_3_Y_SEAL.json").read_text(encoding="utf-8"))
    for k, h in seal["files"].items():
        assert sha256_file(CA / k) == h, f"sealed X file changed: {k}"
    assert sha256_file(OUT / "y.parquet") == yseal["y_parquet_sha256"], "y changed"
    X = pd.read_parquet(OUT / "X.parquet")
    Y = pd.read_parquet(OUT / "y.parquet")[["asset_era_id", "week", "in_risk_set", "y"]]
    D = X.merge(Y, on=["asset_era_id", "week"], validate="one_to_one")
    D = D[D["in_risk_set"]].reset_index(drop=True)
    arms = {k: v["features"] for k, v in seal["arms"].items()}
    reg = pd.read_csv(CA / "MARKET_FEATURE_REGISTRY.csv")
    tr = dict(zip(reg["feature_name"], reg["logistic_transform"].fillna("none")))
    ctx = json.loads((CA / "H20_2_CONTEXT_SETS.json").read_text(encoding="utf-8"))
    tr.update({e["feature_name"]: e["logistic_transform"] for e in ctx["CONTEXT_EXPANDED"]})
    return D, arms, tr


# =============================================================== preprocessing (frozen order)
def prep_fit(df: pd.DataFrame, feats: list[str], tr: dict) -> dict:
    """Frozen order: transform -> winsorise at train 0.5/99.5 pct -> train-median imputation + indicator -> standardise."""
    st = {"features": feats, "params": {}}
    for f in feats:
        x = df[f].astype(float).to_numpy()
        if tr.get(f, "none") == "log1p":
            x = np.log1p(x)
        ok = np.isfinite(x)
        lo, hi = (float(np.percentile(x[ok], 0.5)), float(np.percentile(x[ok], 99.5))) if ok.any() else (np.nan, np.nan)
        xc = np.clip(x, lo, hi)
        med = float(np.median(xc[ok])) if ok.any() else 0.0
        st["params"][f] = {"lo": lo, "hi": hi, "median": med, "indicator": bool((~ok).any())}
    design(df, st, tr, fit_scale=True)
    return st


def design(df: pd.DataFrame, st: dict, tr: dict, fit_scale: bool = False) -> np.ndarray | None:
    mats, names = [], []
    for f in st["features"]:
        p = st["params"][f]
        x = df[f].astype(float).to_numpy()
        if tr.get(f, "none") == "log1p":
            x = np.log1p(x)
        x = np.clip(x, p["lo"], p["hi"])
        miss = ~np.isfinite(x)
        x = np.where(miss, p["median"], x)
        mats.append(x)
        names.append(f)
        if p["indicator"]:
            mats.append(miss.astype(float))
            names.append(f + "_missing")
    M = np.column_stack(mats) if mats else np.zeros((len(df), 0))
    if fit_scale:
        mu, sd = M.mean(axis=0), M.std(axis=0)
        keep = sd > 0
        st["dropped_sd0"] = [n for n, k in zip(names, keep) if not k]
        st["cols"] = [n for n, k in zip(names, keep) if k]
        st["mu"], st["sd"], st["keep"] = mu[keep].tolist(), sd[keep].tolist(), keep.tolist()
        return None
    keep = np.array(st["keep"], dtype=bool)
    M = (M[:, keep] - np.array(st["mu"])) / np.array(st["sd"])
    return np.column_stack([np.ones(len(df)), M])


# =============================================================== L2 logistic (frozen objective)
def sigmoid(z: np.ndarray) -> np.ndarray:
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def fit_l2(Z: np.ndarray, y: np.ndarray, lam: float) -> tuple[np.ndarray, dict]:
    """minimise sum log-loss + 0.5*lam*||beta||^2 (intercept unpenalised); L-BFGS-B gtol 1e-8, maxiter 5000, retry 20000."""

    def obj(b):
        z = Z @ b
        ll = np.sum(np.logaddexp(0.0, z) - y * z)
        g = Z.T @ (sigmoid(z) - y)
        g[1:] += lam * b[1:]
        return ll + 0.5 * lam * np.sum(b[1:] ** 2), g

    info = {}
    for it in (5000, 20000):
        r = minimize(obj, np.zeros(Z.shape[1]), jac=True, method="L-BFGS-B", options={"gtol": 1e-8, "maxiter": it})
        info = {"success": bool(r.success), "message": str(r.message), "nit": int(r.nit), "maxiter": it, "fun": float(r.fun)}
        if r.success:
            return r.x, info
    raise SystemExit(f"logistic fit failed to converge twice: {info} - DATA / DESIGN FAILURE")


def fit_arm(train: pd.DataFrame, feats: list[str], tr: dict, lam: float = LAM) -> dict:
    st = prep_fit(train, feats, tr)
    Z = design(train, st, tr)
    b, info = fit_l2(Z, train["y"].to_numpy(float), lam)
    return {"state": st, "beta": b.tolist(), "fit": info, "lambda": lam, "n_train": int(len(train))}


def predict(model: dict, df: pd.DataFrame, tr: dict) -> np.ndarray:
    return sigmoid(design(df, model["state"], tr) @ np.array(model["beta"]))


# =============================================================== metrics (frozen definitions)
def ap(y: np.ndarray, s: np.ndarray, w: np.ndarray | None = None) -> float:
    """Average precision, tied scores form one threshold; optional case weights."""
    w = np.ones_like(s, dtype=float) if w is None else w
    o = np.argsort(-s, kind="mergesort")
    s, y, w = s[o], y[o], w[o]
    tpw, allw = np.cumsum(w * y), np.cumsum(w)
    last = np.r_[np.nonzero(np.diff(s))[0], len(s) - 1]  # end index of each tie group
    tp, tot = tpw[last], allw[last]
    P = tpw[-1]
    if P <= 0:
        return float("nan")
    rec = tp / P
    prec = tp / np.maximum(tot, 1e-300)
    return float(np.sum(np.diff(np.r_[0.0, rec]) * prec))


def roc(y: np.ndarray, s: np.ndarray) -> float:
    r = pd.Series(s).rank(method="average").to_numpy()
    n1, n0 = y.sum(), len(y) - y.sum()
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)) if n1 and n0 else float("nan")


def calib(y: np.ndarray, p: np.ndarray) -> dict:
    pc = np.clip(p, 1e-6, 1 - 1e-6)
    z = np.log(pc / (1 - pc))
    Z = np.column_stack([np.ones_like(z), z])

    def obj(b):
        zz = Z @ b
        return np.sum(np.logaddexp(0.0, zz) - y * zz), Z.T @ (sigmoid(zz) - y)

    r = minimize(obj, np.array([0.0, 1.0]), jac=True, method="L-BFGS-B", options={"gtol": 1e-8, "maxiter": 5000})
    q = pd.qcut(pd.Series(p).rank(method="first"), 10, labels=False)
    tab = pd.DataFrame({"q": q, "p": p, "y": y}).groupby("q").agg(mean_p=("p", "mean"), obs=("y", "mean"), n=("y", "size"))
    ece = float((tab["n"] * (tab["mean_p"] - tab["obs"]).abs()).sum() / len(p))
    return {"slope": float(r.x[1]) if r.success else None, "intercept": float(r.x[0]) if r.success else None,
            "converged": bool(r.success), "ece": ece, "reliability": tab.reset_index().round(6).to_dict("records")}


def xsec_lift(df: pd.DataFrame, s: np.ndarray) -> float:
    d = df[["week", "y"]].assign(s=s)
    top_pos = top_n = 0
    for _, g in d.groupby("week"):
        k = math.ceil(0.1 * len(g))
        t = g.nlargest(k, "s")
        top_pos += t["y"].sum()
        top_n += k
    base = d["y"].mean()
    return float((top_pos / top_n) / base) if base > 0 else float("nan")


def within_week_ap(df: pd.DataFrame, s: np.ndarray) -> float:
    d = df[["week", "y"]].assign(s=s)
    vals = [ap(g["y"].to_numpy(float), g["s"].to_numpy()) for _, g in d.groupby("week") if 0 < g["y"].sum() < len(g)]
    return float(np.mean(vals)) if vals else float("nan")


def metrics(df: pd.DataFrame, p: np.ndarray) -> dict:
    y = df["y"].to_numpy(float)
    return {"pr_auc": ap(y, p), "roc_auc": roc(y, p), "brier": float(np.mean((p - y) ** 2)), "top_decile_lift_xsec": xsec_lift(df, p),
            "within_week_pr_auc": within_week_ap(df, p), "calibration": calib(y, p), "units": units(df)}


def units(df: pd.DataFrame) -> dict:
    return {"rows": int(len(df)), "asset_eras": int(df["asset_era_id"].nunique()), "weeks": int(df["week"].nunique()),
            "positive_rows": int(df["y"].sum()), "unique_positive_events": int(df.loc[df["y"] == 1, "asset_era_id"].nunique()),
            "base_rate": float(df["y"].mean())}


# =============================================================== bootstrap (frozen pigeonhole)
def boot(df: pd.DataFrame, pa: np.ndarray, pb: np.ndarray, block: np.ndarray, mode: str, seed: int = SEED_BOOT) -> dict:
    rng = np.random.default_rng(seed)
    y = df["y"].to_numpy(float)
    era_codes, era_idx = np.unique(df["asset_era_id"].to_numpy(), return_inverse=True)
    blk_codes, blk_idx = np.unique(block, return_inverse=True)
    ne, nb = len(era_codes), len(blk_codes)
    out, redraw = [], 0
    while len(out) < B:
        m = np.bincount(rng.integers(0, ne, ne), minlength=ne) if mode in ("two_way", "asset_era") else np.ones(ne)
        n = np.bincount(rng.integers(0, nb, nb), minlength=nb) if mode in ("two_way", "block") else np.ones(nb)
        w = m[era_idx] * n[blk_idx]
        if (w * y).sum() <= 0:
            redraw += 1
            continue
        out.append(ap(y, pb, w) - ap(y, pa, w))
    d = np.array(out)
    return {"mode": mode, "replicates": B, "seed": seed, "redraws": redraw, "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "mean": float(d.mean()), "sd": float(d.std()), "share_positive": float((d > 0).mean())}


# =============================================================== development
def dev() -> int:
    p0()
    sp = spec()
    D, arms, tr = load_xy()
    folds = sp["split"]["folds"]
    devD = D[D["block"] == "DEVELOPMENT"].reset_index(drop=True)
    oof = []
    fold_res = []
    for f in folds:
        trn = devD[(devD["week"] >= f["train_from"]) & (devD["week"] <= f["train_to"])]
        tst = devD[(devD["week"] >= f["test_from"]) & (devD["week"] <= f["test_to"])].copy()
        assert pd.to_datetime(trn["week"]).max() <= pd.Timestamp(f["test_from"]) - pd.Timedelta(days=366)  # P5.2
        row = {"fold": f["fold"], "era": f["test_era"], "units_test": units(tst), "units_train": units(trn), "arms": {}}
        for a in ARMS:
            mdl = fit_arm(trn, arms[a], tr)
            p = predict(mdl, tst, tr)
            tst[f"p_{a}"] = p
            row["arms"][a] = {"pr_auc": ap(tst["y"].to_numpy(float), p), "roc_auc": roc(tst["y"].to_numpy(float), p),
                              "brier": float(np.mean((p - tst["y"].to_numpy(float)) ** 2)), "fit": mdl["fit"],
                              "n_columns": len(mdl["state"]["cols"])}
        row["delta_M2_M0"] = row["arms"]["M2"]["pr_auc"] - row["arms"]["M0"]["pr_auc"]
        row["delta_M2core_M0"] = row["arms"]["M2_core"]["pr_auc"] - row["arms"]["M0"]["pr_auc"]
        fold_res.append(row)
        tst["fold"] = f["fold"]
        oof.append(tst[["asset_era_id", "base_asset", "week", "block", "y", "fold", *[f"p_{a}" for a in ARMS]]])
        print(f"fold {f['fold']}: M0 {row['arms']['M0']['pr_auc']:.4f} M2 {row['arms']['M2']['pr_auc']:.4f} delta {row['delta_M2_M0']:+.4f}", flush=True)
    O = pd.concat(oof, ignore_index=True)
    O.to_parquet(OUT / "oof_predictions_primary.parquet", index=False)
    pooled = {a: metrics(O, O[f"p_{a}"].to_numpy()) for a in ARMS}
    d = pooled["M2"]["pr_auc"] - pooled["M0"]["pr_auc"]
    dcore = pooled["M2_core"]["pr_auc"] - pooled["M0"]["pr_auc"]
    y = O["y"].to_numpy(float)
    era = {}
    for e in ("2022", "2023"):
        s = O[O["fold"].isin([f["fold"] for f in folds if f["test_era"] == e])]
        era[e] = {"pr_auc_M0": ap(s["y"].to_numpy(float), s["p_M0"].to_numpy()), "pr_auc_M2": ap(s["y"].to_numpy(float), s["p_M2"].to_numpy()),
                  "units": units(s)}
        era[e]["delta"] = era[e]["pr_auc_M2"] - era[e]["pr_auc_M0"]
    lofo = {}
    for f in folds:
        s = O[O["fold"] != f["fold"]]
        lofo[str(f["fold"])] = ap(s["y"].to_numpy(float), s["p_M2"].to_numpy()) - ap(s["y"].to_numpy(float), s["p_M0"].to_numpy())
    devres = {
        "stage": "P5", "computed_utc": iso(now_utc()), "model": "L2 logistic, lambda = 10 (primary; no selection)",
        "pooled_oof": pooled, "delta_pr_auc_M2_M0": d, "relative_delta": d / pooled["M0"]["pr_auc"],
        "delta_pr_auc_M2core_M0": dcore, "folds": fold_res,
        "positive_folds_M2_M0": int(sum(r["delta_M2_M0"] > 0 for r in fold_res)),
        "positive_folds_M2core_M0": int(sum(r["delta_M2core_M0"] > 0 for r in fold_res)),
        "era": era, "leave_one_fold_out_delta": lofo, "lofo_min": min(lofo.values()),
        "oof_sha256": sha256_file(OUT / "oof_predictions_primary.parquet"),
    }
    write_json("H20_3_DEVELOPMENT_RESULTS.json", devres)
    blk = O["fold"].to_numpy()
    bs = {"primary_M2_vs_M0": {m: boot(O, O["p_M0"].to_numpy(), O["p_M2"].to_numpy(), blk, m) for m in ("two_way", "asset_era", "block")},
          "robustness_M2core_vs_M0": {m: boot(O, O["p_M0"].to_numpy(), O["p_M2_core"].to_numpy(), blk, m) for m in ("two_way", "asset_era", "block")},
          "blocks": "8 fold test windows", "point_delta": d}
    write_json("H20_3_BOOTSTRAP_RESULTS.json", bs)
    print("bootstrap two-way CI", bs["primary_M2_vs_M0"]["two_way"]["ci95"], flush=True)
    # final development refits (pre-LCUV model state)
    finals = {a: fit_arm(devD, arms[a], tr) for a in ARMS}
    (OUT / "final_models_primary.json").write_text(json.dumps(finals), encoding="utf-8")
    freeze = {
        "stage": "PRE-LCUV FREEZE", "frozen_utc": iso(now_utc()), "lambda": LAM, "primary_configuration": "L2 logistic, lambda = 10, frozen preprocessing (A02)",
        "code": {s: sha256_file(CA / s) for s in ["scripts/h20_3_model.py", "scripts/h20_3_common.py", "scripts/h20_3_seal_target.py",
                                                  "scripts/h20_3_market.py", "scripts/h20_3_context.py"]},
        "x_seal_sha256": sha256_file(CA / "H20_3_X_SEAL.json"), "y_seal_sha256": sha256_file(CA / "H20_3_Y_SEAL.json"),
        "X_parquet_sha256": sha256_file(OUT / "X.parquet"), "y_parquet_sha256": sha256_file(OUT / "y.parquet"),
        "oof_predictions_sha256": sha256_file(OUT / "oof_predictions_primary.parquet"),
        "development_results_sha256": sha256_file(CA / "H20_3_DEVELOPMENT_RESULTS.json"),
        "bootstrap_results_sha256": sha256_file(CA / "H20_3_BOOTSTRAP_RESULTS.json"),
        "final_models_sha256": sha256_file(OUT / "final_models_primary.json"),
        "final_fit_convergence": {a: finals[a]["fit"] for a in ARMS},
        "pending_criteria": ["S4 (LCUV Delta > 0)", "S5 (LCUV calibration)", "S7 (needs the LCUV era block)"],
        "development_criteria_computed": {"S1_delta": d, "S2_positive_folds": devres["positive_folds_M2_M0"],
                                          "S3_ci95": bs["primary_M2_vs_M0"]["two_way"]["ci95"]},
        "lcuv_rows_scored_before_freeze": 0,
    }
    write_json("H20_3_PRE_LCUV_FREEZE.json", freeze)
    print(json.dumps({"M0": pooled["M0"]["pr_auc"], "M2": pooled["M2"]["pr_auc"], "delta": d, "pos_folds": devres["positive_folds_M2_M0"]}, indent=1))
    return 0


# =============================================================== LCUV, once
def lcuv() -> int:
    p0()
    if LOCK.exists():
        raise SystemExit("LCUV primary scoring already run once - a second run is a DATA / DESIGN FAILURE")
    fz = json.loads((CA / "H20_3_PRE_LCUV_FREEZE.json").read_text(encoding="utf-8"))
    for k, f in (("final_models_sha256", OUT / "final_models_primary.json"), ("X_parquet_sha256", OUT / "X.parquet"),
                 ("y_parquet_sha256", OUT / "y.parquet"), ("development_results_sha256", CA / "H20_3_DEVELOPMENT_RESULTS.json")):
        assert sha256_file(f) == fz[k], f"pre-LCUV frozen file changed: {f}"
    LOCK.write_text(iso(now_utc()), encoding="utf-8")
    D, arms, tr = load_xy()
    L = D[D["block"] == LCUV].reset_index(drop=True)
    finals = json.loads((OUT / "final_models_primary.json").read_text(encoding="utf-8"))
    for a in ARMS:
        L[f"p_{a}"] = predict(finals[a], L, tr)
    L[["asset_era_id", "base_asset", "week", "block", "y", *[f"p_{a}" for a in ARMS]]].to_parquet(OUT / "lcuv_predictions_primary.parquet", index=False)
    res = {a: metrics(L, L[f"p_{a}"].to_numpy()) for a in ARMS}
    d = res["M2"]["pr_auc"] - res["M0"]["pr_auc"]
    month = pd.to_datetime(L["week"]).dt.strftime("%Y-%m").to_numpy()
    info = boot(L, L["p_M0"].to_numpy(), L["p_M2"].to_numpy(), month, "two_way")
    s5 = {"brier_ratio": res["M2"]["brier"] / res["M0"]["brier"] if res["M0"]["brier"] > 0 else None,
          "slope_M0": res["M0"]["calibration"]["slope"], "slope_M2": res["M2"]["calibration"]["slope"]}
    s5["slope_excess"] = (abs(s5["slope_M2"] - 1) - abs(s5["slope_M0"] - 1)) if None not in (s5["slope_M0"], s5["slope_M2"]) else None
    out = {"stage": "P6", "scored_utc": iso(now_utc()), "block": LCUV, "primary_lambda": LAM, "metrics": res,
           "delta_pr_auc_M2_M0": d, "relative_delta": d / res["M0"]["pr_auc"],
           "delta_pr_auc_M2core_M0": res["M2_core"]["pr_auc"] - res["M0"]["pr_auc"],
           "info_interval_two_way_asset_era_x_month": info, "S5_values": s5,
           "predictions_sha256": sha256_file(OUT / "lcuv_predictions_primary.parquet"), "scoring_runs": 1}
    write_json("H20_3_LCUV_RESULTS.json", out)
    print(json.dumps({"M0": res["M0"]["pr_auc"], "M2": res["M2"]["pr_auc"], "delta": d, "S5": s5}, indent=1))
    return 0


# =============================================================== exploratory (after LCUV primary hashed)
def explore() -> int:
    import lightgbm as lgb

    p0()
    lr = json.loads((CA / "H20_3_LCUV_RESULTS.json").read_text(encoding="utf-8"))
    assert sha256_file(OUT / "lcuv_predictions_primary.parquet") == lr["predictions_sha256"]
    sp = spec()
    D, arms, tr = load_xy()
    folds = sp["split"]["folds"]
    devD = D[D["block"] == "DEVELOPMENT"].reset_index(drop=True)
    L = D[D["block"] == LCUV].reset_index(drop=True)
    grid = sp["model"]["primary_class"]["exploratory_lambda_grid"]["lambda"]
    tconf = [{"num_leaves": nl, "n_estimators": ne} for nl in (7, 15) for ne in (200, 500)]
    # native API (scikit-learn is absent): the frozen parameters, one-to-one with the sklearn-style names of the spec
    base = dict(objective="binary", learning_rate=0.03, min_data_in_leaf=200, bagging_fraction=0.8, bagging_freq=1,
                feature_fraction=0.8, lambda_l2=1.0, max_bin=255, deterministic=True, force_row_wise=True, num_threads=1,
                seed=SEED_LGB, verbose=-1)

    def lgb_fit(df, feats, conf):
        prm = {**base, "num_leaves": conf["num_leaves"]}
        return lgb.train(prm, lgb.Dataset(df[feats].astype(float).to_numpy(), label=df["y"].to_numpy()),
                         num_boost_round=conf["n_estimators"])

    def cv(fitpred):
        per, oof = [], []
        for f in folds:
            trn = devD[(devD["week"] >= f["train_from"]) & (devD["week"] <= f["train_to"])]
            tst = devD[(devD["week"] >= f["test_from"]) & (devD["week"] <= f["test_to"])]
            p = fitpred(trn, tst)
            per.append(ap(tst["y"].to_numpy(float), p))
            oof.append(pd.DataFrame({"y": tst["y"].to_numpy(), "p": p, "week": tst["week"].to_numpy(), "asset_era_id": tst["asset_era_id"].to_numpy()}))
        O = pd.concat(oof)
        return float(np.mean(per)), per, ap(O["y"].to_numpy(float), O["p"].to_numpy())

    def logit_fp(feats, lam):
        return lambda trn, tst: predict(fit_arm(trn, feats, tr, lam), tst, tr)

    def lgb_fp(feats, conf):
        def f(trn, tst):
            return lgb_fit(trn, feats, conf).predict(tst[feats].astype(float).to_numpy())
        return f

    res = {"label": "EXPLORATORY - cannot determine, upgrade or downgrade the verdict", "logistic_selected_lambda": {},
           "lightgbm_default": {}, "lightgbm_selected": {}}
    for a in ARMS:
        scores = {lam: cv(logit_fp(arms[a], lam)) for lam in grid}
        best = max(grid, key=lambda lam: (round(scores[lam][0], 12), lam))  # ties -> larger lambda
        Lp = predict(fit_arm(devD, arms[a], tr, best), L, tr)
        res["logistic_selected_lambda"][a] = {"mean_fold_pr_auc_by_lambda": {str(k): v[0] for k, v in scores.items()}, "selected": best,
                                              "dev_pooled_oof_pr_auc": scores[best][2], "lcuv_pr_auc": ap(L["y"].to_numpy(float), Lp)}
        print("logit", a, best, flush=True)
    for a in ARMS:
        dflt = {"num_leaves": 7, "n_estimators": 200}
        mean_d, per_d, pooled_d = cv(lgb_fp(arms[a], dflt))
        m = lgb_fit(devD, arms[a], dflt)
        res["lightgbm_default"][a] = {"config": dflt, "dev_pooled_oof_pr_auc": pooled_d, "mean_fold_pr_auc": mean_d,
                                      "lcuv_pr_auc": ap(L["y"].to_numpy(float), m.predict(L[arms[a]].astype(float).to_numpy()))}
        sc = [(c, cv(lgb_fp(arms[a], c))) for c in tconf]
        best = max(sc, key=lambda z: (round(z[1][0], 12), -z[0]["num_leaves"], -z[0]["n_estimators"]))
        m = lgb_fit(devD, arms[a], best[0])
        res["lightgbm_selected"][a] = {"config": best[0], "mean_fold_pr_auc_by_config": [{"config": c, "mean": v[0]} for c, v in sc],
                                       "dev_pooled_oof_pr_auc": best[1][2],
                                       "lcuv_pr_auc": ap(L["y"].to_numpy(float), m.predict(L[arms[a]].astype(float).to_numpy()))}
        print("lgb", a, flush=True)
    for k in ("logistic_selected_lambda", "lightgbm_default", "lightgbm_selected"):
        r = res[k]
        r["delta_dev_M2_M0"] = r["M2"]["dev_pooled_oof_pr_auc"] - r["M0"]["dev_pooled_oof_pr_auc"]
        r["delta_lcuv_M2_M0"] = r["M2"]["lcuv_pr_auc"] - r["M0"]["lcuv_pr_auc"]
    write_json("H20_3_EXPLORATORY_RESULTS.json", res)
    print(json.dumps({k: {"dev": res[k]["delta_dev_M2_M0"], "lcuv": res[k]["delta_lcuv_M2_M0"]} for k in
                      ("logistic_selected_lambda", "lightgbm_default", "lightgbm_selected")}, indent=1))
    return 0


if __name__ == "__main__":
    part = sys.argv[sys.argv.index("--part") + 1]
    sys.exit({"dev": dev, "lcuv": lcuv, "explore": explore}[part]())
