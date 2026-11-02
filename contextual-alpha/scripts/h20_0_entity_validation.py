"""H20.0 — untuned validation of entity-resolution parser v2 (H20_0_EXECUTION_DEVIATION.md, D1).

Parser v2 was written after v1's output on the frozen sample had been seen, so its score on that
sample is tuned. This script draws an independent validation sample with the SAME rule as the freeze
(plan section 3) but seed 20261019, and scores v1 and v2 on it. The frozen sample is untouched.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_entity_validation.py"

Writes data/interim/entity_resolution_validation.parquet and evidence/H20_0_VALIDATION_SAMPLE.json.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from h20_0_entities import run
from h20_common import EVIDENCE, INTERIM, RAW, iso, now_utc

SEED = 20261019


def qstart(y: int, q: int) -> datetime:
    return datetime(y, 3 * (q - 1) + 1, 1, tzinfo=UTC)


def draw() -> list[dict]:
    W = pd.read_parquet(RAW / "inherited" / "symbol_windows_whitelist.parquet")
    W = W[W["window_known"].fillna(False)].copy()
    W["first_candle"] = pd.to_datetime(W["first_candle"], utc=True)
    W["last_candle"] = pd.to_datetime(W["last_candle"], utc=True)
    D = pd.read_parquet(RAW / "inherited" / "asset_daily_usd_volume.parquet")
    D["date"] = pd.to_datetime(D["date"], utc=True)
    rng = np.random.default_rng(SEED)
    stamps = []
    y, q = 2018, 1
    while (y, q) <= (2026, 3):
        s = qstart(y, q)
        e = qstart(y + 1, 1) if q == 4 else qstart(y, q + 1)
        stamps.append((f"{y}-Q{q}", s + timedelta(minutes=int(rng.integers(0, int((e - s).total_seconds() // 60))))))
        y, q = (y + 1, 1) if q == 4 else (y, q + 1)
    sample = []
    for k, (quarter, t) in enumerate(stamps):
        live = W[(W["first_candle"] <= t - timedelta(days=30)) & (W["last_candle"] >= t)]
        universe = sorted(live["base_asset"].dropna().unique())
        dv = D[(D["date"] >= t - timedelta(days=30)) & (D["date"] < t) & D["base_asset"].isin(universe)]
        has = dv.groupby("base_asset")["usd_volume"].median().dropna().sort_index()
        terc = pd.qcut(has.rank(method="first"), 3, labels=["T1_LOW", "T2_MID", "T3_HIGH"])
        assets = []
        for lab in ["T1_LOW", "T2_MID", "T3_HIGH"]:
            pool = sorted(terc[terc == lab].index)
            assets.append({"asset_ticker": pool[int(rng.integers(0, len(pool)))], "liquidity_tercile": lab})
        sample.append({"sample_id": f"V{k + 1:02d}", "quarter": quarter, "t_utc": iso(t), "assets": assets})
    return sample


def main() -> int:
    sample = draw()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "H20_0_VALIDATION_SAMPLE.json").write_text(
        json.dumps({"seed": SEED, "created_utc": iso(now_utc()), "rule": "identical to plan section 3",
                    "purpose": "untuned score of entity parser v2", "sample": sample}, indent=1)
    )
    W = pd.read_parquet(RAW / "inherited" / "symbol_windows_whitelist.parquet")
    W = W[W["window_known"].fillna(False)].copy()
    for c in ("first_candle", "last_candle"):
        W[c] = pd.to_datetime(W[c], utc=True)
    U = pd.read_parquet(INTERIM / "binance_catalog.parquet")
    U["published_utc"] = pd.to_datetime(U["published_utc"], utc=True)
    return run(sample, INTERIM / "entity_resolution_validation.parquet", W, U)


if __name__ == "__main__":
    raise SystemExit(main())
