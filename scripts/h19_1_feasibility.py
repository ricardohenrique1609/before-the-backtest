"""H19.1 — data feasibility for H19-P3A. Coverage, synchronization and control windows only.

ZERO RETURN. Nothing here computes a return, a log return, a basis move, a funding change, a
z-score against an outcome or any direction of price - not for one event (§39). The script reads
only: which minutes exist, which minutes carry trades, and which archive dates are present.

To make that guarantee checkable rather than asserted, the only kline columns ever loaded are the
open time, the volume and the trade count. The price columns are never read into memory.

    .venv/Scripts/python scripts/h19_1_feasibility.py [--workers 8]

Writes data/raw/h19_1/coverage.parquet, sync.parquet and data/alpha_sprint/h19_1_feasibility.json.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import pandas as pd

import os

# Fair-access policies at SEC EDGAR and at the venue archives ask automated clients to identify
# themselves with a real contact address. There is deliberately no default: a placeholder would be
# a false identification.
CONTACT = os.environ.get("QIE_CONTACT_EMAIL")
if not CONTACT:
    raise RuntimeError(
        "Set QIE_CONTACT_EMAIL to a real contact address before using SEC retrieval."
    )


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "h19_1"
RAW2 = ROOT / "data" / "raw" / "h18_2"
RAW3 = ROOT / "data" / "raw" / "h18_3"
OUT = ROOT / "data" / "alpha_sprint"
UA = {"User-Agent": f"Mozilla/5.0 (compatible; QIE research; {CONTACT})"}
BUCKET = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
VISION = "https://data.binance.vision"

PRE_DAYS = 30                 # §9 coverage window T0-30d -> T0+1d
CONTROL_LO, CONTROL_HI = 180, 14   # §19 control pool T0-180d .. T0-14d
SPOT_PREF = ["USDT", "USDC", "FDUSD", "BUSD", "TUSD", "BTC", "ETH", "BNB"]

_lock = threading.Lock()
_last = [0.0]


def throttle(gap: float = 0.1) -> None:
    with _lock:
        d = time.monotonic() - _last[0]
        if d < gap:
            time.sleep(gap - d)
        _last[0] = time.monotonic()


def get(c: httpx.Client, url: str, params: dict | None = None, tries: int = 4):
    delay = 0.9
    for _ in range(tries):
        throttle()
        try:
            r = c.get(url, params=params, follow_redirects=True)
        except Exception:  # noqa: BLE001
            time.sleep(delay)
            delay *= 1.8
            continue
        if r.status_code in (200, 404):
            return r
        time.sleep(delay)
        delay *= 1.8
    return None


def listed_dates(c: httpx.Client, prefix: str) -> set[str]:
    """All YYYY-MM-DD dates present under an archive prefix."""
    out: set[str] = set()
    marker = None
    while True:
        p = {"prefix": prefix}
        if marker:
            p["marker"] = marker
        r = get(c, BUCKET, p)
        if r is None or r.status_code != 200:
            break
        out |= {m.group(1) for m in re.finditer(r"-(\d{4}-\d{2}-\d{2})\.zip", r.text)}
        keys = re.findall(r"<Key>([^<]+)</Key>", r.text)
        t = re.search(r"<IsTruncated>(true|false)</IsTruncated>", r.text)
        # S3 only returns NextMarker when a delimiter is set. Without one, a truncated listing must
        # be continued from the LAST KEY returned - relying on NextMarker here silently stopped
        # after the first 1,000 keys, which are the OLDEST dates, so recent events read as
        # uncovered while old ones read as fully covered.
        if not (t and t.group(1) == "true") or not keys:
            break
        marker = keys[-1]
    return out


def listed_months(c: httpx.Client, prefix: str) -> set[str]:
    r = get(c, BUCKET, {"prefix": prefix})
    if r is None or r.status_code != 200:
        return set()
    return {m.group(1) for m in re.finditer(r"-(\d{4}-\d{2})\.zip", r.text)}


def minute_frame(c: httpx.Client, url: str) -> pd.DataFrame | None:
    """Open time, volume and trade count ONLY. Price columns are never loaded (§39)."""
    r = get(c, url)
    if r is None or r.status_code != 200:
        return None
    try:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        with z.open(z.namelist()[0]) as f:
            d = pd.read_csv(f, header=None, usecols=[0, 5, 8], names=["open_ms", "volume", "trades"])
    except Exception:  # noqa: BLE001
        return None
    d = d[pd.to_numeric(d["open_ms"], errors="coerce").notna()]
    if not len(d):
        return None
    for col in d.columns:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    # Binance switched these archives to MICROSECOND open times from 2025; reading them as
    # milliseconds puts every row in the year 57000 and the window filter then returns nothing.
    # This is a fact already recorded in the project's own notes from H18.3 and it has to be
    # detected per file rather than assumed.
    unit = "us" if float(d["open_ms"].iloc[0]) > 1e14 else "ms"
    d["ts"] = pd.to_datetime(d["open_ms"], unit=unit)
    return d.dropna(subset=["ts"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)

    X = pd.read_parquet(ROOT / "H19_0_EVENT_DERIVATIVE_CROSSWALK.parquet")
    clean = X[X["public_information_state"] == "CLEAN_SPOT_INFORMATION_EVENT"].copy()
    clean["T0"] = pd.to_datetime(clean["spot_delisting_announcement_time"])
    print(f"clean events from H19.0: {len(clean)}")

    # spot route choice: the preferred quote among routes alive at T0 (§10 needs one spot series)
    SW = pd.read_parquet(RAW2 / "symbol_windows.parquet")
    SW["first_candle"] = pd.to_datetime(SW["first_candle"])
    SW["last_candle"] = pd.to_datetime(SW["last_candle"])
    SW = SW[SW["window_known"] & SW["base_asset"].notna()]
    pref = {q: i for i, q in enumerate(SPOT_PREF)}

    def spot_symbol(asset: str, t0: pd.Timestamp) -> str | None:
        g = SW[(SW["base_asset"] == asset) & (SW["first_candle"] <= t0) & (SW["last_candle"] >= t0)]
        if not len(g):
            return None
        g = g.assign(p=g["quote_asset"].map(pref).fillna(99)).sort_values("p")
        return str(g.iloc[0]["symbol"])

    clean["spot_symbol"] = [spot_symbol(r.asset_id, pd.Timestamp(r.T0)) for r in clean.itertuples()]
    print(f"clean events with a spot route alive at T0: {int(clean['spot_symbol'].notna().sum())}")

    # lifecycle facts for the wind-down contamination audit (§20) - factual timestamps only
    R = pd.read_parquet(RAW3 / "pair_removals_pit.parquet").reset_index()
    R["removal_date"] = pd.to_datetime(R["removal_date"])
    # H18.1b subgroup (§21) and Monitoring Tag presence (§22), both factual
    CW = pd.read_parquet(ROOT / "H18_1B_H18_1_CROSSWALK.parquet")[["full_delisting_event_id", "winddown_state"]]
    MT = pd.read_parquet(RAW2 / "monitoring_tag_events.parquet")
    MT = MT[MT["action"] == "TAG_ADDED"]
    MT["published"] = pd.to_datetime(MT["published"])
    first_tag = MT.groupby("asset")["published"].min()

    rows = []
    sync_rows = []
    rlock = threading.Lock()
    done = [0]

    def work(r) -> None:
        t0 = pd.Timestamp(r.T0)
        perp = r.derivative_symbol
        spot = r.spot_symbol
        win_days = pd.date_range((t0 - pd.Timedelta(days=PRE_DAYS)).normalize(), (t0 + pd.Timedelta(days=1)).normalize(), freq="D")
        want = {d.strftime("%Y-%m-%d") for d in win_days}
        ctl_days = pd.date_range((t0 - pd.Timedelta(days=CONTROL_LO)).normalize(), (t0 - pd.Timedelta(days=CONTROL_HI)).normalize(), freq="D")
        want_ctl = {d.strftime("%Y-%m-%d") for d in ctl_days}

        rec = {"full_delisting_event_id": r.full_delisting_event_id, "asset": r.asset_id, "T0": t0,
               "perp_symbol": perp, "spot_symbol": spot}
        with httpx.Client(headers=UA, timeout=90, follow_redirects=True) as c:
            surfaces = {
                "perp_klines": f"data/futures/um/daily/klines/{perp}/1m/",
                "perp_markPrice": f"data/futures/um/daily/markPriceKlines/{perp}/1m/",
                "perp_indexPrice": f"data/futures/um/daily/indexPriceKlines/{perp}/1m/",
                "perp_premiumIndex": f"data/futures/um/daily/premiumIndexKlines/{perp}/1m/",
                "perp_metrics_oi": f"data/futures/um/daily/metrics/{perp}/",
            }
            if isinstance(spot, str):
                surfaces["spot_klines"] = f"data/spot/daily/klines/{spot}/1m/"
            for name, pre in surfaces.items():
                have = listed_dates(c, pre)
                rec[f"{name}_cov"] = round(len(have & want) / len(want), 4)
                rec[f"{name}_ctl_cov"] = round(len(have & want_ctl) / len(want_ctl), 4)
            fm = listed_months(c, f"data/futures/um/monthly/fundingRate/{perp}/")
            need_m = {d.strftime("%Y-%m") for d in win_days}
            rec["funding_cov"] = round(len(fm & need_m) / len(need_m), 4) if need_m else 0.0

            # §10 synchronization inside the PRIMARY window only: T0-24h .. T0-1h
            lo, hi = t0 - pd.Timedelta(hours=24), t0 - pd.Timedelta(hours=1)
            pmin, smin = set(), set()
            ptr, str_ = 0, 0
            for k in (1, 0):
                day = (t0.normalize() - pd.Timedelta(days=k)).strftime("%Y-%m-%d")
                dp = minute_frame(c, f"{VISION}/data/futures/um/daily/klines/{perp}/1m/{perp}-1m-{day}.zip")
                if dp is not None:
                    sel = dp[(dp["ts"] >= lo) & (dp["ts"] < hi)]
                    pmin |= set(sel["ts"])
                    ptr += int((sel["trades"].fillna(0) > 0).sum())
                if isinstance(spot, str):
                    ds = minute_frame(c, f"{VISION}/data/spot/daily/klines/{spot}/1m/{spot}-1m-{day}.zip")
                    if ds is not None:
                        sel = ds[(ds["ts"] >= lo) & (ds["ts"] < hi)]
                        smin |= set(sel["ts"])
                        str_ += int((sel["trades"].fillna(0) > 0).sum())
        total_min = int((hi - lo).total_seconds() // 60)
        both = pmin & smin
        rec |= {
            "primary_window_minutes": total_min,
            "perp_minutes_present": len(pmin),
            "spot_minutes_present": len(smin),
            "synchronized_minutes": len(both),
            "sync_fraction": round(len(both) / total_min, 4) if total_min else 0.0,
            "perp_minutes_with_trades": ptr,
            "spot_minutes_with_trades": str_,
            "perp_zero_trade_share": round(1 - ptr / len(pmin), 4) if pmin else None,
            "spot_zero_trade_share": round(1 - str_ / len(smin), 4) if smin else None,
        }

        # §20 wind-down contamination of the control pool, from factual removal dates only
        rr = R[R["base_asset"] == r.asset_id]
        prior = rr.loc[rr["removal_date"] < t0, "removal_date"]
        first_rem = prior.min() if len(prior) else pd.NaT
        rec["first_prior_pair_removal"] = first_rem
        rec["control_pool_overlaps_winddown"] = bool(
            pd.notna(first_rem) and first_rem <= (t0 - pd.Timedelta(days=CONTROL_HI))
        )
        rec["days_first_removal_to_T0"] = int((t0 - first_rem).days) if pd.notna(first_rem) else None
        tg = first_tag.get(r.asset_id)
        rec["monitoring_tag_before_T0"] = bool(tg is not None and pd.notna(tg) and pd.Timestamp(tg) < t0)
        rec["public_warning_state"] = "PUBLIC_WARNING_ALREADY_PRESENT" if rec["monitoring_tag_before_T0"] else "NO_KNOWN_PUBLIC_WARNING"

        with rlock:
            rows.append(rec)
            done[0] += 1
            if done[0] % 10 == 0:
                print(f"  {done[0]}/{len(clean)} events probed", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, list(clean.itertuples())))

    C = pd.DataFrame(rows).sort_values("T0")
    C = C.merge(CW, on="full_delisting_event_id", how="left")
    C.to_parquet(RAW / "coverage.parquet")
    pd.DataFrame(sync_rows).to_parquet(RAW / "sync.parquet") if sync_rows else None

    def m(col):
        return round(float(C[col].mean()), 4) if col in C else None

    usable = C[(C["spot_klines_cov"].fillna(0) >= 0.95) & (C["perp_klines_cov"] >= 0.95) & (C["sync_fraction"] >= 0.95)]
    C["usable_primary"] = C["full_delisting_event_id"].isin(usable["full_delisting_event_id"])
    C.to_parquet(RAW / "coverage.parquet")

    by_year = C.assign(y=C["T0"].dt.year).groupby("y").agg(
        events=("asset", "size"), usable=("usable_primary", "sum"),
        sync=("sync_fraction", "mean")).round(4)

    # §11 current vs terminated perp differential
    M = pd.read_parquet(ROOT / "H19_0_DERIVATIVE_SECURITY_MASTER.parquet")
    M["last_trading_time"] = pd.to_datetime(M["last_trading_time"])
    termset = set(M.loc[M["last_trading_time"] < pd.Timestamp("2026-09-01"), "symbol"])
    C["perp_terminated"] = C["perp_symbol"].isin(termset)
    diff = {
        "terminated_n": int(C["perp_terminated"].sum()),
        "current_n": int((~C["perp_terminated"]).sum()),
        "terminated_perp_cov": round(float(C.loc[C["perp_terminated"], "perp_klines_cov"].mean()), 4) if C["perp_terminated"].any() else None,
        "current_perp_cov": round(float(C.loc[~C["perp_terminated"], "perp_klines_cov"].mean()), 4),
        "terminated_sync": round(float(C.loc[C["perp_terminated"], "sync_fraction"].mean()), 4) if C["perp_terminated"].any() else None,
        "current_sync": round(float(C.loc[~C["perp_terminated"], "sync_fraction"].mean()), 4),
    }
    diff["coverage_gap_pp"] = (round(abs((diff["terminated_perp_cov"] or 0) - diff["current_perp_cov"]) * 100, 2)
                               if diff["terminated_perp_cov"] is not None else None)

    summary = {
        "zero_return_guarantee": "only open time, volume and trade count were ever loaded; price columns were never read (§39)",
        "clean_events": int(len(C)),
        "events_with_spot_route_at_T0": int(C["spot_symbol"].notna().sum()),
        "coverage_T0_minus_30d_to_T0_plus_1d": {
            "spot_1m": m("spot_klines_cov"), "perp_1m": m("perp_klines_cov"),
            "mark_price_1m": m("perp_markPrice_cov"), "index_price_1m": m("perp_indexPrice_cov"),
            "premium_index_1m": m("perp_premiumIndex_cov"), "open_interest_metrics": m("perp_metrics_oi_cov"),
            "funding_monthly": m("funding_cov"),
        },
        "bars": {"spot_1m": 0.95, "perp_1m": 0.95, "mark_index": 0.90, "funding": 0.90, "sync": 0.95},
        "share_of_events_meeting_each_bar": {
            "spot_1m_ge_95": round(float((C["spot_klines_cov"].fillna(0) >= 0.95).mean()), 4),
            "perp_1m_ge_95": round(float((C["perp_klines_cov"] >= 0.95).mean()), 4),
            "mark_ge_90": round(float((C["perp_markPrice_cov"] >= 0.90).mean()), 4),
            "index_ge_90": round(float((C["perp_indexPrice_cov"] >= 0.90).mean()), 4),
            "funding_ge_90": round(float((C["funding_cov"] >= 0.90).mean()), 4),
            "oi_ge_90": round(float((C["perp_metrics_oi_cov"] >= 0.90).mean()), 4),
            "sync_ge_95": round(float((C["sync_fraction"] >= 0.95).mean()), 4),
        },
        "synchronization_primary_window": {
            "window": "T0-24h .. T0-1h (1,380 minutes)",
            "mean_sync_fraction": m("sync_fraction"),
            "median_sync_fraction": round(float(C["sync_fraction"].median()), 4),
            "events_at_or_above_95pct": int((C["sync_fraction"] >= 0.95).sum()),
        },
        "zero_trade_contamination_primary_window": {
            "perp_mean_zero_trade_share": m("perp_zero_trade_share"),
            "spot_mean_zero_trade_share": m("spot_zero_trade_share"),
            "perp_events_above_50pct_zero_trade": int((C["perp_zero_trade_share"] > 0.5).sum()),
        },
        "control_window_availability_T0_minus_180d_to_minus_14d": {
            "spot_1m": m("spot_klines_ctl_cov"), "perp_1m": m("perp_klines_ctl_cov"),
            "events_with_perp_ctl_cov_ge_80": int((C["perp_klines_ctl_cov"] >= 0.80).sum()),
            "events_with_spot_ctl_cov_ge_80": int((C["spot_klines_ctl_cov"].fillna(0) >= 0.80).sum()),
        },
        "winddown_contamination": {
            "control_pool_overlaps_a_known_winddown": int(C["control_pool_overlaps_winddown"].sum()),
            "share": round(float(C["control_pool_overlaps_winddown"].mean()), 4),
            "median_days_first_removal_to_T0": float(C["days_first_removal_to_T0"].median()) if C["days_first_removal_to_T0"].notna().any() else None,
        },
        "public_warning_state": C["public_warning_state"].value_counts().astype(int).to_dict(),
        "winddown_subgroup": C["winddown_state"].value_counts().astype(int).to_dict(),
        "usable_primary_n": int(C["usable_primary"].sum()),
        "by_year": by_year.to_dict(orient="index"),
        "current_vs_terminated_perp": diff,
        "note": "No return, basis move, funding change or price direction computed anywhere (§39).",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "h19_1_feasibility.json").write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")
    print()
    print(json.dumps(summary, indent=1, default=str)[:3400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
