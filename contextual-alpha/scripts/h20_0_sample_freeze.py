"""H20.0 step 5 — build and freeze the outcome-independent feasibility sample (plan section 3).

1. Snapshot-copies the two inherited inputs with column whitelists (inheritance A5, A8):
     symbol_windows: symbol, base_asset, quote_asset, first_candle, last_candle, window_known
     asset_daily:    date, base_asset, usd_volume
   `is_live_now`, `known_to_exchange_info`, `usd_close` and every outcome table are never read.
2. Draws one timestamp per quarter 2018-Q1..2026-Q3 (minute resolution, rng seed 20261018).
3. For each t, builds A(t) = base assets with a symbol window first_candle <= t-30d and
   last_candle >= t, splits A(t) into terciles of the trailing 30-day median USD volume (rows with
   date < t only), and draws one asset per tercile.
4. Writes H20_0_SAMPLE_FREEZE.json with its own SHA-256 (computed over the file with the
   `freeze_sha256` field absent) and a .sha256 sidecar over the final bytes.

Refuses to overwrite an existing freeze.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_sample_freeze.py"
"""

from __future__ import annotations

import json
import platform
import sys
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
import pyarrow
import pyarrow.parquet as pq

from h20_common import CA, RAW, ROOT, iso, now_utc, sha256_bytes, sha256_file

SEED = 20261018
FIRST_Q, LAST_Q = (2018, 1), (2026, 3)
LISTED_BEFORE = timedelta(days=30)
LIQ_WINDOW = timedelta(days=30)

A5 = ROOT / "data/raw/h18_2/symbol_windows.parquet"
A5_COLS = ["symbol", "base_asset", "quote_asset", "first_candle", "last_candle", "window_known"]
A8 = ROOT / "data/raw/h18_3/asset_daily.parquet"
A8_COLS = ["date", "base_asset", "usd_volume"]
INH = RAW / "inherited"
FREEZE = CA / "H20_0_SAMPLE_FREEZE.json"
PLAN = CA / "H20_0_CONTEXT_FEASIBILITY_PLAN.md"


def snapshot(src, cols, name) -> tuple[pd.DataFrame, dict]:
    INH.mkdir(parents=True, exist_ok=True)
    df = pq.read_table(src, columns=cols).to_pandas()
    out = INH / name
    if not out.exists():
        df.to_parquet(out, index=False)
    lineage = {
        "source_path": str(src.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256_file(src),
        "columns_copied": cols,
        "rows": int(len(df)),
        "snapshot_path": str(out.relative_to(CA)).replace("\\", "/"),
        "snapshot_sha256": sha256_file(out),
    }
    (INH / (name + ".lineage.json")).write_text(json.dumps(lineage, indent=1), encoding="utf-8")
    return pd.read_parquet(out), lineage


def quarters():
    y, q = FIRST_Q
    while (y, q) <= LAST_Q:
        yield y, q
        y, q = (y + 1, 1) if q == 4 else (y, q + 1)


def qstart(y: int, q: int) -> datetime:
    return datetime(y, 3 * (q - 1) + 1, 1, tzinfo=UTC)


def main() -> int:
    if FREEZE.exists():
        print("freeze exists; refusing to overwrite (plan section 3)")
        return 1
    W, lin5 = snapshot(A5, A5_COLS, "symbol_windows_whitelist.parquet")
    D, lin8 = snapshot(A8, A8_COLS, "asset_daily_usd_volume.parquet")
    W = W[W["window_known"].fillna(False)].copy()
    W["first_candle"] = pd.to_datetime(W["first_candle"], utc=True)
    W["last_candle"] = pd.to_datetime(W["last_candle"], utc=True)
    D["date"] = pd.to_datetime(D["date"], utc=True)

    rng = np.random.default_rng(SEED)
    stamps = []
    for y, q in quarters():
        s = qstart(y, q)
        e = qstart(y + 1, 1) if q == 4 else qstart(y, q + 1)
        minutes = int((e - s).total_seconds() // 60)
        t = s + timedelta(minutes=int(rng.integers(0, minutes)))
        stamps.append({"quarter": f"{y}-Q{q}", "t": t})

    sample = []
    for k, st in enumerate(stamps):
        t = st["t"]
        live = W[(W["first_candle"] <= t - LISTED_BEFORE) & (W["last_candle"] >= t)]
        universe = sorted(live["base_asset"].dropna().unique())
        dv = D[(D["date"] >= t - LIQ_WINDOW) & (D["date"] < t) & D["base_asset"].isin(universe)]
        liq = dv.groupby("base_asset")["usd_volume"].median().reindex(universe)
        has = liq.dropna().sort_index()
        terc = pd.qcut(has.rank(method="first"), 3, labels=["T1_LOW", "T2_MID", "T3_HIGH"])
        assets = []
        for lab in ["T1_LOW", "T2_MID", "T3_HIGH"]:
            pool = sorted(terc[terc == lab].index)
            a = pool[int(rng.integers(0, len(pool)))]
            assets.append(
                {
                    "asset_ticker": a,
                    "liquidity_tercile": lab,
                    "trailing_30d_median_usd_volume": float(has[a]),
                    "pool_size": len(pool),
                }
            )
        sample.append(
            {
                "sample_id": f"S{k + 1:02d}",
                "quarter": st["quarter"],
                "t_utc": iso(t),
                "universe_size": len(universe),
                "universe_without_volume": int(liq.isna().sum()),
                "assets": assets,
            }
        )

    freeze = {
        "experiment": "H20.0 Context Data Feasibility",
        "created_utc": iso(now_utc()),
        "plan_file": "H20_0_CONTEXT_FEASIBILITY_PLAN.md",
        "plan_sha256": sha256_file(PLAN),
        "selection_rule": {
            "timestamps": "one per calendar quarter 2018-Q1..2026-Q3; uniform minute within quarter; "
            "numpy default_rng(seed) draws all timestamps first, in quarter order",
            "asset_universe": "base assets with >=1 Binance spot symbol window first_candle <= t-30d and "
            "last_candle >= t (window_known only); last_candle used only as the 'trading at t' predicate",
            "asset_draw": "terciles of median daily usd_volume over [t-30d, t) (rows with date < t); one "
            "asset uniformly per tercile from the alphabetically sorted pool, tercile order LOW, MID, HIGH",
            "windows": {"W7": "(t-7d, t]", "W30": "(t-30d, t]"},
            "outcome_inputs": "none; no lifecycle, delisting, return or price column is read",
        },
        "rng": {"generator": "numpy.random.default_rng", "seed": SEED},
        "generation_script": "scripts/h20_0_sample_freeze.py",
        "generation_script_sha256": sha256_file(CA / "scripts/h20_0_sample_freeze.py"),
        "common_module_sha256": sha256_file(CA / "scripts/h20_common.py"),
        "inputs": [lin5, lin8],
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "pyarrow": pyarrow.__version__,
            "platform": platform.platform(),
        },
        "n_timestamps": len(sample),
        "n_asset_time_units": sum(len(s["assets"]) for s in sample),
        "sample": sample,
    }
    body = json.dumps(freeze, indent=1, ensure_ascii=False)
    freeze["freeze_sha256"] = sha256_bytes(body.encode("utf-8"))
    freeze["freeze_sha256_note"] = (
        "sha256 of this file serialised with indent=1 and without the two freeze_sha256 fields; "
        "H20_0_SAMPLE_FREEZE.json.sha256 holds the sha256 of the final bytes"
    )
    final = json.dumps(freeze, indent=1, ensure_ascii=False).encode("utf-8")
    FREEZE.write_bytes(final)
    (CA / "H20_0_SAMPLE_FREEZE.json.sha256").write_text(
        f"{sha256_bytes(final)}  H20_0_SAMPLE_FREEZE.json\n", encoding="utf-8"
    )
    print(f"frozen {len(sample)} timestamps, {freeze['n_asset_time_units']} asset-time units")
    print(f"freeze_sha256 {freeze['freeze_sha256']}  file sha256 {sha256_bytes(final)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
