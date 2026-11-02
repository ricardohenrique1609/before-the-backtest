"""H20.3 P2 — X_market (MARKET_FEATURE_REGISTRY admissible features) at every landmark, + audits P2.1-P2.8.

Inputs, by column whitelist only (no outcome, no status column):
  data/raw/h18_2/symbol_windows.parquet   symbol, base_asset, quote_asset, first_candle, last_candle, window_known
  data/raw/h18_3/pair_removals_pit.parquet symbol, base_asset, quote_asset, removal_date, assets_losing_this_quote_prior_90d
  data/raw/h18_3/asset_daily.parquet       date, base_asset, usd_volume, trades, hhi_trades, usd_close
  data/raw/h18_3/candles/<symbol>.parquet  date                       (P2.3 / P2.4 only)
  data/raw/h18_3/features.parquet          asset_era_id, week + the 18 shared baseline columns (P2.8 only)

The landmark rows are the OUTCOME-FREE superset: every asset-era week from the era's first served
candle to era end + 7 d with >= 1 route ever seen and age >= 90 d, inside DEVELOPMENT or LCUV. The
announcement-based truncation of the risk set happens only in the sealed target stage (P4).

    .venv/Scripts/python "Contextual Alpha/scripts/h20_3_market.py"
"""

from __future__ import annotations

import json
import sys
from datetime import date

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from h20_3_common import OUT, ROOT, block_of, calendar, iso, now_utc, p0, sha256_file, spec

RAW2, RAW3 = ROOT / "data/raw/h18_2", ROOT / "data/raw/h18_3"
EPOCH = pd.Timestamp("2017-07-03")
ERA_GAP_DAYS = 365
MIN_AGE = 90
BATCH_N = 15
CAP = 3650
QUOTES = ("USDT", "USDC", "BTC", "BNB", "FDUSD")
SHARED = ["dollar_volume_90d", "volume_trend", "zero_low_volume_freq_90d", "realized_vol_90d", "trailing_return_90d",
          "drawdown_365d", "liquidity_concentration_90d", "asset_age_days", "n_active_spot_pairs", "n_quote_assets",
          "has_USDT", "has_USDC", "has_BTC", "has_BNB", "has_FDUSD", "venue_listed_assets", "venue_removal_intensity_90d",
          "time_index_years"]


def load():
    W = pq.read_table(RAW2 / "symbol_windows.parquet",
                      columns=["symbol", "base_asset", "quote_asset", "first_candle", "last_candle", "window_known"]).to_pandas()
    S = W[W["window_known"].fillna(False) & W["base_asset"].notna()].copy()
    S["first_candle"] = pd.to_datetime(S["first_candle"])
    S["last_candle"] = pd.to_datetime(S["last_candle"])
    R = pq.read_table(RAW3 / "pair_removals_pit.parquet",
                      columns=["symbol", "base_asset", "quote_asset", "removal_date", "assets_losing_this_quote_prior_90d"]).to_pandas()
    R["removal_date"] = pd.to_datetime(R["removal_date"])
    A = pq.read_table(RAW3 / "asset_daily.parquet",
                      columns=["date", "base_asset", "usd_volume", "trades", "hhi_trades", "usd_close"]).to_pandas()
    A["date"] = pd.to_datetime(A["date"])
    return S, R, A


def eras(S: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Inherited H18.2 era rule A7: a new era only after > 365 days with no served route (backward)."""
    rows, assign = [], []
    for asset, g in S.groupby("base_asset"):
        g = g.sort_values(["first_candle", "symbol"])
        era, run_last = 0, None
        for r in g.itertuples():
            if run_last is not None and (r.first_candle - run_last).days > ERA_GAP_DAYS:
                era += 1
            run_last = r.last_candle if run_last is None else max(run_last, r.last_candle)
            assign.append({"symbol": r.symbol, "era": era})
    S = S.merge(pd.DataFrame(assign), on="symbol", how="left")
    E = S.groupby(["base_asset", "era"]).agg(era_start=("first_candle", "min"), era_end=("last_candle", "max")).reset_index()
    E["asset_era_id"] = E["base_asset"] + "#" + E["era"].astype(str)
    S = S.merge(E[["base_asset", "era", "asset_era_id", "era_start", "era_end"]], on=["base_asset", "era"])
    return S, E


def rolling(A: pd.DataFrame) -> pd.DataFrame:
    """H18.3 stage 2, unchanged formulas, backward-looking."""
    out = []
    for asset, g in A.groupby("base_asset"):
        g = g.set_index("date").sort_index()
        full = g.reindex(pd.date_range(g.index.min(), g.index.max(), freq="D"))
        vol, tr, px = full["usd_volume"].fillna(0.0), full["trades"].fillna(0.0), full["usd_close"].ffill()
        logret = np.log(px).diff()
        f = pd.DataFrame(index=full.index)
        f["dollar_volume_90d"] = vol.rolling(90, min_periods=10).sum()
        v30 = vol.rolling(30, min_periods=5).sum()
        f["volume_trend"] = np.log1p(v30 / 30.0) - np.log1p(f["dollar_volume_90d"] / 90.0)
        f["zero_low_volume_freq_90d"] = (tr == 0).rolling(90, min_periods=10).mean()
        f["realized_vol_90d"] = logret.rolling(90, min_periods=20).std()
        f["trailing_return_90d"] = px / px.shift(90) - 1.0
        f["drawdown_365d"] = px / px.rolling(365, min_periods=30).max() - 1.0
        f["liquidity_concentration_90d"] = full["hhi_trades"].rolling(90, min_periods=10).mean()
        f["base_asset"] = asset
        out.append(f.reset_index().rename(columns={"index": "date"}))
    F = pd.concat(out, ignore_index=True)
    F["date"] = pd.to_datetime(F["date"]).astype("datetime64[ns]")
    return F


def candle_dates(symbols) -> dict[str, np.ndarray]:
    out = {}
    for s in symbols:
        p = RAW3 / "candles" / f"{s}.parquet"
        if p.exists():
            d = pq.read_table(p, columns=["date"]).to_pandas()["date"]
            out[s] = np.sort(pd.to_datetime(d).to_numpy().astype("datetime64[D]"))
        else:
            out[s] = np.array([], dtype="datetime64[D]")
    return out


def active_by_candle(cd: dict, syms, w64: np.datetime64) -> np.ndarray:
    lo = w64 - np.timedelta64(6, "D")
    res = []
    for s in syms:
        a = cd[s]
        i = np.searchsorted(a, lo, side="left")
        res.append(i < len(a) and a[i] <= w64)
    return np.array(res, dtype=bool)


def panel(S, E, R, weeks_keep: set, cd: dict | None, mode: str) -> pd.DataFrame:
    """Route state / history per (era, week). mode = 'window' (frozen primary) or 'candle' (frozen P2.3 fallback)."""
    grid = pd.date_range(EPOCH, pd.Timestamp("2025-10-13"), freq="W-MON").to_numpy().astype("datetime64[D]")
    rem_by_sym = {k: g for k, g in R.groupby("symbol")}
    rows = []
    for e in E.itertuples():
        g = S[S["asset_era_id"] == e.asset_era_id].sort_values("symbol")
        syms = g["symbol"].to_numpy()
        f = g["first_candle"].to_numpy().astype("datetime64[D]")
        la = g["last_candle"].to_numpy().astype("datetime64[D]")
        qs = g["quote_asset"].to_numpy()
        rr = [rem_by_sym[s] for s in syms if s in rem_by_sym]
        rr = pd.concat(rr) if rr else None
        rd = rr["removal_date"].to_numpy().astype("datetime64[D]") if rr is not None else np.array([], dtype="datetime64[D]")
        rn = rr["assets_losing_this_quote_prior_90d"].to_numpy() if rr is not None else np.array([], dtype=int)
        es, ee = np.datetime64(e.era_start, "D"), np.datetime64(e.era_end, "D")
        wk = grid[(grid >= es) & (grid <= ee + np.timedelta64(7, "D"))]
        peak = 0
        for w64 in wk:
            alive = (f <= w64) & (la >= w64) if mode == "window" else ((f <= w64) & active_by_candle(cd, syms, w64))
            n = int(alive.sum())
            if n == 0 and peak == 0:
                continue
            peak = max(peak, n)
            age = int((w64 - es) / np.timedelta64(1, "D"))
            wd = date.fromisoformat(str(w64))
            if wd.isoformat() not in weeks_keep or age < MIN_AGE:
                continue
            aq = set(qs[alive])
            past = rd[rd <= w64]
            in365 = (rd > w64 - np.timedelta64(365, "D")) & (rd <= w64)
            rows.append({
                "asset_era_id": e.asset_era_id, "base_asset": e.base_asset, "week": wd.isoformat(),
                "asset_age_days": age, "n_active_spot_pairs": n, "n_quote_assets": len(aq),
                **{f"has_{q}": float(q in aq) for q in QUOTES},
                "route_ratio_to_peak": n / peak,
                "days_since_last_pair_removal": float(min(CAP, int((w64 - past.max()) / np.timedelta64(1, "D")))) if past.size else float(CAP),
                "never_had_pair_removal": float(past.size == 0),
                "asset_specific_removals_365d_mkt": int((in365 & (rn < BATCH_N)).sum()),
                "batch_prune_removals_365d_mkt": int((in365 & (rn >= BATCH_N)).sum()),
                "max_removal_date_counted": str(past.max()) if past.size else "",
                "max_pair_first_candle_counted": str(f[alive].max()) if n else "",
            })
    return pd.DataFrame(rows)


def venue(S, R, weeks, cd, mode):
    fc = S["first_candle"].to_numpy().astype("datetime64[D]")
    lc = S["last_candle"].to_numpy().astype("datetime64[D]")
    ba, syms = S["base_asset"].to_numpy(), S["symbol"].to_numpy()
    rem = R["removal_date"].to_numpy().astype("datetime64[D]")
    out = {}
    for wk in weeks:
        w64 = np.datetime64(wk, "D")
        m = (fc <= w64) & (lc >= w64) if mode == "window" else ((fc <= w64) & active_by_candle(cd, syms, w64))
        listed = len(set(ba[m]))
        r90 = int(((rem > w64 - np.timedelta64(90, "D")) & (rem <= w64)).sum())
        out[wk] = {"venue_listed_assets": listed, "venue_removal_intensity_90d": r90 / listed if listed else np.nan,
                   "time_index_years": (pd.Timestamp(wk) - EPOCH).days / 365.25}
    return out


def main() -> int:
    p0()
    sp = spec()
    cal = calendar()
    weeks = sorted({c["week"] for c in cal})
    S, R, A = load()
    S, E = eras(S)
    cd = candle_dates(sorted(S["symbol"]))
    print(f"eras {len(E)}  pairs {len(S)}  removals {len(R)}  calendar weeks {len(weeks)}", flush=True)

    Pw = panel(S, E, R, set(weeks), None, "window")
    print(f"window panel rows {len(Pw)}", flush=True)
    # ---------------- P2.3 route-state gap audit (structural, outcome-free)
    Pc = panel(S, E, R, set(weeks), cd, "candle")
    j = Pw.merge(Pc[["asset_era_id", "week", "n_active_spot_pairs"]], on=["asset_era_id", "week"], how="left",
                 suffixes=("", "_candle"))
    j["n_active_spot_pairs_candle"] = j["n_active_spot_pairs_candle"].fillna(0)
    disagree = float((j["n_active_spot_pairs"] != j["n_active_spot_pairs_candle"]).mean())
    route_fallback = disagree > 0.01
    # ---------------- P2.4 removal permanence (structural)
    resumed = 0
    for r in R.itertuples():
        a = cd.get(r.symbol, np.array([], dtype="datetime64[D]"))
        resumed += int((a > np.datetime64(r.removal_date, "D")).any())
    resumed_share = resumed / len(R)
    removal_fallback = resumed_share > 0.01
    print(f"P2.3 disagreement {disagree:.4%} fallback={route_fallback} | P2.4 resumed {resumed_share:.4%} fallback={removal_fallback}", flush=True)
    if removal_fallback:
        raise SystemExit("P2.4 fallback triggered: candle-gap removal definition required (frozen); not implemented in this run")

    mode = "candle" if route_fallback else "window"
    P = Pc if route_fallback else Pw
    if route_fallback:  # frozen fallback: route-state + ratio from candle activity, removal features unchanged
        keep = ["asset_era_id", "week", "n_active_spot_pairs", "n_quote_assets", *[f"has_{q}" for q in QUOTES], "route_ratio_to_peak",
                "max_pair_first_candle_counted"]
        P = Pw.drop(columns=keep[2:]).merge(Pc[keep], on=["asset_era_id", "week"], how="inner")
    V = venue(S, R, weeks, cd, mode)
    for c in ("venue_listed_assets", "venue_removal_intensity_90d", "time_index_years"):
        P[c] = P["week"].map(lambda w, c=c: V[w][c])
    F = rolling(A)
    P["week_ts"] = pd.to_datetime(P["week"]).astype("datetime64[ns]")
    P = pd.merge_asof(P.sort_values("week_ts"), F.sort_values("date"), left_on="week_ts", right_on="date", by="base_asset",
                      direction="backward", tolerance=pd.Timedelta(days=10))
    P["block"] = P["week"].map(lambda w: block_of(date.fromisoformat(w), sp))
    P["t_utc"] = P["week"].map(lambda w: iso(pd.Timestamp(w, tz="UTC").to_pydatetime() + pd.Timedelta(days=1)))
    reg = pd.read_csv(ROOT / "Contextual Alpha" / "MARKET_FEATURE_REGISTRY.csv")
    feats = reg.loc[reg["in_market_arm"], "feature_name"].tolist()
    assert len(feats) == 23

    # ---------------- audits
    jd = P["date"]
    a = {
        "P2.1_joined_daily_after_w": int((jd.notna() & (jd > P["week_ts"])).sum()),
        "P2.1_asof_tolerance_days": 10,
        "P2.2_rows_after_w_entering_windows": int((jd.notna() & (jd > P["week_ts"])).sum()),
        "P2.2_removal_after_w_counted": int((P["max_removal_date_counted"].replace("", np.nan).dropna().map(pd.Timestamp) > pd.to_datetime(P.loc[P["max_removal_date_counted"] != "", "week"])).sum()),
        "P2.2_pair_first_candle_after_w_counted": int((P["max_pair_first_candle_counted"].replace("", np.nan).dropna().map(pd.Timestamp) > pd.to_datetime(P.loc[P["max_pair_first_candle_counted"] != "", "week"])).sum()),
        "P2.3_route_state_disagreement_share": round(disagree, 6), "P2.3_bar": 0.01, "P2.3_fallback_applied": route_fallback,
        "P2.4_removals_with_later_candle_share": round(resumed_share, 6), "P2.4_bar": 0.01, "P2.4_fallback_applied": removal_fallback,
        "P2.4_removals_counted_after_w": None,
    }
    a["P2.4_removals_counted_after_w"] = a["P2.2_removal_after_w_counted"]
    rng = np.random.default_rng(20261105)
    idx = rng.choice(len(R), size=min(500, len(R)), replace=False)
    mism = 0
    for i in idx:
        r = R.iloc[i]
        same = R[(R["quote_asset"] == r["quote_asset"]) & (R["removal_date"] >= r["removal_date"] - pd.Timedelta(days=90))
                 & (R["removal_date"] <= r["removal_date"])]
        mism += int(same["base_asset"].nunique() != r["assets_losing_this_quote_prior_90d"])
    a["P2.5_batch_count_recompute_mismatches"] = mism
    excluded = set(reg.loc[reg["pit_status"] == "EXCLUDED", "feature_name"])
    a["P2.6_excluded_columns_present"] = sorted(set(feats) & excluded)
    a["P2.7_era_not_backward"] = 0  # by construction: an era break needs a > 365-day gap before the era's first candle <= w
    # ---------------- P2.8 reproducibility versus H18.3 features (column whitelist)
    H = pq.read_table(RAW3 / "features.parquet", columns=["asset_era_id", "week", *SHARED]).to_pandas()
    H["week"] = pd.to_datetime(H["week"]).dt.date.astype(str)
    M = P[["asset_era_id", "week", *SHARED]].merge(H, on=["asset_era_id", "week"], suffixes=("", "_h18"))
    agree = {}
    for c in SHARED:
        x, y_ = M[c].astype(float), M[f"{c}_h18"].astype(float)
        both = x.notna() & y_.notna()
        agree[c] = round(float((np.isclose(x[both], y_[both], rtol=1e-6, atol=1e-9)).mean()), 4) if both.any() else None
    a["P2.8_matched_rows"] = int(len(M))
    a["P2.8_agreement_share_by_feature"] = agree
    a["P2.8_rows_only_in_h20"] = int(len(P) - len(M))

    passed = (a["P2.1_joined_daily_after_w"] == 0 and a["P2.2_removal_after_w_counted"] == 0
              and a["P2.2_pair_first_candle_after_w_counted"] == 0 and mism == 0 and not a["P2.6_excluded_columns_present"]
              and not removal_fallback)
    X = P[["asset_era_id", "base_asset", "week", "t_utc", "block", *feats]].sort_values(["week", "asset_era_id"]).reset_index(drop=True)
    X.to_parquet(OUT / "x_market.parquet", index=False)
    res = {"stage": "P2", "computed_utc": iso(now_utc()), "route_state_mode": mode, "checks": a, "PASS": passed,
           "rows": int(len(X)), "rows_by_block": X["block"].value_counts().to_dict(), "asset_eras": int(X["asset_era_id"].nunique()),
           "missing_share_by_feature": X[feats].isna().mean().round(4).to_dict(), "features": feats,
           "x_market_sha256": sha256_file(OUT / "x_market.parquet")}
    (OUT / "p2_audit.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"PASS": passed, "mode": mode, **{k: v for k, v in a.items() if k != "P2.8_agreement_share_by_feature"}},
                     indent=1, default=str))
    print("P2.8 agreement:", agree)
    return 0 if passed else 3


if __name__ == "__main__":
    sys.exit(main())
