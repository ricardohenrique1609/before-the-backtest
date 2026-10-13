"""H19.2 pre-freeze feasibility — control pools, bucket validity, VWAP field availability.

NON-PRICE ONLY (§A25). The loader reads usecols=[0, 5, 7, 8] = open time, base volume, quote volume,
trade count. The OHLC columns (1-4) are NEVER read into memory, so no price, VWAP, return, DS,
abnormal score, basis or funding direction can be computed here even by accident.

Everything this script decides is frozen BEFORE any price is read:
  - which control assets are eligible, strictly on information available at each event's T0 (§A5);
  - how many matched controls each event has, on liquidity bucket x Monitoring-Tag status (§A6);
  - how many valid consecutive 15-minute transitions each event has (§A8-§A10);
  - whether the VWAP fields are consistently populated (§A11).

Control eligibility is strictly point-in-time. The draft's "no full delisting within +/-180d of T0"
rule is REMOVED: its forward half was look-ahead. A control delisted AFTER T0 stays a valid control
and is never removed retroactively (§A5).

    .venv/Scripts/python scripts/h19_2_prefreeze.py [--workers 10] [--cands 120]

Writes data/raw/h19_2/*.parquet and data/alpha_sprint/h19_2_prefreeze.json.
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
import numpy as np
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
RAW = ROOT / "data" / "raw" / "h19_2"
RAW2 = ROOT / "data" / "raw" / "h18_2"
RAW3 = ROOT / "data" / "raw" / "h18_3"
OUT = ROOT / "data" / "alpha_sprint"
UA = {"User-Agent": f"Mozilla/5.0 (compatible; QIE research; {CONTACT})"}
BUCKET = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
VISION = "https://data.binance.vision"

SEED = 20261010
MIN_CONTROLS = 20          # §A7, frozen
MIN_TRANSITIONS = 73       # §A10, frozen
AVAIL_BAR = 0.95           # §A5.4
SPOT_PREF = ["USDT", "USDC", "FDUSD", "BUSD", "TUSD", "BTC", "ETH", "BNB"]
PLAUSIBLE = (pd.Timestamp("2017-01-01"), pd.Timestamp("2027-01-01"))

_lock = threading.Lock()
_last = [0.0]


def throttle(gap: float = 0.09) -> None:
    with _lock:
        d = time.monotonic() - _last[0]
        if d < gap:
            time.sleep(gap - d)
        _last[0] = time.monotonic()


def get(c: httpx.Client, url: str, params: dict | None = None, tries: int = 4):
    delay = 0.8
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


def months_for(c: httpx.Client, sym: str) -> list[str]:
    out: list[str] = []
    marker = None
    pre = f"data/futures/um/monthly/klines/{sym}/1m/"
    while True:
        p = {"prefix": pre}
        if marker:
            p["marker"] = marker
        r = get(c, BUCKET, p)
        if r is None or r.status_code != 200:
            break
        out += [m.group(1) for m in re.finditer(r"-1m-(\d{4}-\d{2})\.zip", r.text)]
        keys = re.findall(r"<Key>([^<]+)</Key>", r.text)
        t = re.search(r"<IsTruncated>(true|false)</IsTruncated>", r.text)
        if not (t and t.group(1) == "true") or not keys:
            break
        marker = keys[-1]
    return sorted(set(out))


def nonprice_frame(c: httpx.Client, url: str) -> pd.DataFrame | None:
    """open time, base volume, quote volume, trade count. OHLC columns are never read (§A25)."""
    r = get(c, url)
    if r is None or r.status_code != 200:
        return None
    try:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        with z.open(z.namelist()[0]) as f:
            d = pd.read_csv(f, header=None, usecols=[0, 5, 7, 8],
                            names=["open_ms", "base_volume", "quote_volume", "trades"])
    except Exception:  # noqa: BLE001
        return None
    d = d[pd.to_numeric(d["open_ms"], errors="coerce").notna()]
    if not len(d):
        return None
    for col in d.columns:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    # §A24: detect the unit per file. Spot archives are microseconds from 2026, futures are
    # milliseconds for the same date; one unit for both empties every join silently.
    unit = "us" if float(d["open_ms"].iloc[0]) > 1e14 else "ms"
    d["ts"] = pd.to_datetime(d["open_ms"], unit=unit)
    d = d.dropna(subset=["ts"])
    if len(d) and not (PLAUSIBLE[0] <= d["ts"].min() <= PLAUSIBLE[1] and PLAUSIBLE[0] <= d["ts"].max() <= PLAUSIBLE[1]):
        raise RuntimeError(f"timestamp out of plausible range for {url}: {d['ts'].min()} .. {d['ts'].max()}")
    return d


def leg_stats(c: httpx.Client, kind: str, sym: str, t0: pd.Timestamp) -> dict | None:
    """Trade-count and volume-presence statistics for one leg over the primary window."""
    lo, hi = t0 - pd.Timedelta(hours=24), t0 - pd.Timedelta(hours=1)
    parts = []
    for k in (1, 0):
        day = (t0.normalize() - pd.Timedelta(days=k)).strftime("%Y-%m-%d")
        base = f"{VISION}/data/futures/um/daily/klines" if kind == "perp" else f"{VISION}/data/spot/daily/klines"
        d = nonprice_frame(c, f"{base}/{sym}/1m/{sym}-1m-{day}.zip")
        if d is not None:
            parts.append(d)
    if not parts:
        return None
    D = pd.concat(parts, ignore_index=True)
    W = D[(D["ts"] >= lo) & (D["ts"] < hi)].copy()
    if not len(W):
        return None
    total_min = int((hi - lo).total_seconds() // 60)
    W["bucket"] = W["ts"].dt.floor("15min")
    traded = W[W["trades"].fillna(0) > 0]
    by_bucket = traded.groupby("bucket").agg(
        trades=("trades", "sum"), base_vol=("base_volume", "sum"), quote_vol=("quote_volume", "sum"))
    # hourly notional for the liquidity bucket (§A6) - a VOLUME field, not a price
    hourly = W.assign(h=W["ts"].dt.floor("h")).groupby("h")["quote_volume"].sum()
    return {
        "minutes_present": int(len(W)),
        "availability": round(len(W) / total_min, 4),
        "minutes_with_trades": int(len(traded)),
        "valid_buckets": set(by_bucket.index),
        "buckets_with_positive_base_and_quote": int(((by_bucket["base_vol"] > 0) & (by_bucket["quote_vol"] > 0)).sum()),
        "n_valid_buckets": int(len(by_bucket)),
        "median_hourly_notional": float(hourly.median()) if len(hourly) else np.nan,
    }


def liq_bucket(v) -> str:
    if v is None or not np.isfinite(v):
        return "UNKNOWN"
    if v < 100_000:
        return "<$100k/h"
    if v < 1_000_000:
        return "$100k-$1m/h"
    if v < 10_000_000:
        return "$1m-$10m/h"
    return ">$10m/h"


def valid_transitions(ev_buckets: set, ctl_buckets: set | None = None) -> int:
    """§A9: only CONSECUTIVE valid buckets form a transition. Gaps are never bridged."""
    s = ev_buckets if ctl_buckets is None else (ev_buckets & ctl_buckets)
    if not s:
        return 0
    b = sorted(s)
    return sum(1 for i in range(1, len(b)) if (b[i] - b[i - 1]) == pd.Timedelta(minutes=15))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--cands", type=int, default=120)
    a = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)

    X = pd.read_parquet(ROOT / "H19_0_EVENT_DERIVATIVE_CROSSWALK.parquet")
    ev = X[(X["public_information_state"] == "CLEAN_SPOT_INFORMATION_EVENT") & (X["derivative_market"] == "um")].copy()
    ev["T0"] = pd.to_datetime(ev["spot_delisting_announcement_time"])
    print(f"clean USD-M candidate events: {len(ev)}  (XMR excluded: its derivative is COIN-M)")

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

    # full universe of USD-M perps, with archive windows (§A24: archive only, never the live API)
    U = pd.read_parquet(ROOT.joinpath("data/raw/h19_0/derivative_universe.parquet"))
    um = sorted(U.loc[U["market"] == "um", "symbol"])
    wcache = RAW / "perp_windows.parquet"
    if wcache.exists():
        PW = pd.read_parquet(wcache)
    else:
        print(f"resolving archive windows for {len(um)} USD-M symbols")
        rows = []
        rl = threading.Lock()
        def w(sym):
            with httpx.Client(headers=UA, timeout=90, follow_redirects=True) as c:
                ms = months_for(c, sym)
            with rl:
                rows.append({"symbol": sym, "first_month": ms[0] if ms else None,
                             "last_month": ms[-1] if ms else None, "n_months": len(ms)})
                if len(rows) % 150 == 0:
                    print(f"  {len(rows)}/{len(um)}", flush=True)
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            list(ex.map(w, um))
        PW = pd.DataFrame(rows)
        PW.to_parquet(wcache)
    PW = PW[PW["n_months"] > 0].copy()
    PW["first_ts"] = pd.to_datetime(PW["first_month"] + "-01")
    PW["last_ts"] = pd.to_datetime(PW["last_month"] + "-01") + pd.offsets.MonthEnd(0)
    PW["base_asset"] = [re.sub(r"(USDT|USDC|BUSD)$", "", re.sub(r"^(1000000|1000)", "", s)) for s in PW["symbol"]]
    PW = PW[~PW["symbol"].str.contains("SETTLED")]
    print(f"USD-M symbols with archive data: {len(PW)}")

    # PIT exclusion facts
    E201 = pd.read_parquet(ROOT / "H18_1B_FULL_DELIST_EVENTS.parquet")
    E201["ann"] = pd.to_datetime(E201["announcement_public_time"], format="mixed", errors="coerce")
    first_delist = E201.dropna(subset=["ann"]).groupby("symbol")["ann"].min()
    DN = pd.read_parquet(ROOT / "H19_0_DERIVATIVE_NOTICES.parquet")
    DN["published"] = pd.to_datetime(DN["published"])
    first_dnotice = DN.groupby("asset")["published"].min()
    MT = pd.read_parquet(RAW2 / "monitoring_tag_events.parquet")
    MT = MT[MT["action"] == "TAG_ADDED"]
    MT["published"] = pd.to_datetime(MT["published"])
    first_tag = MT.groupby("asset")["published"].min()

    def tagged_at(asset: str, t0: pd.Timestamp) -> bool:
        t = first_tag.get(asset)
        return bool(t is not None and pd.notna(t) and pd.Timestamp(t) < t0)

    # ---------------------------------------------------- metadata-only candidate pools per T0 date
    dates = sorted(ev["T0"].dt.normalize().unique())
    cand_by_date: dict = {}
    for d0 in dates:
        t0 = pd.Timestamp(d0)
        live_perp = PW[(PW["first_ts"] < t0) & (PW["last_ts"] >= t0)]
        cands = []
        for r in live_perp.itertuples():
            asset = r.base_asset
            if asset in set(ev["asset_id"]):
                continue
            fd = first_delist.get(asset)
            if fd is not None and pd.notna(fd) and pd.Timestamp(fd) <= t0:
                continue                      # §A5.5 already delisted by T0
            dn = first_dnotice.get(asset)
            if dn is not None and pd.notna(dn) and pd.Timestamp(dn) <= t0:
                continue                      # §A5.6 derivative notice already public by T0
            ss = spot_symbol(asset, t0)
            if ss is None:
                continue                      # §A5.1 needs a live spot route
            cands.append({"asset": asset, "perp": r.symbol, "spot": ss})
        cand_by_date[str(d0)[:10]] = cands
    meta_counts = {k: len(v) for k, v in cand_by_date.items()}
    print(f"metadata-eligible candidates per date: min {min(meta_counts.values())}, "
          f"median {int(np.median(list(meta_counts.values())))}, max {max(meta_counts.values())}")

    # ------------------------------------------------- evaluate a seeded sample of candidates
    rng = np.random.default_rng(SEED)
    jobs = []
    for dkey, cands in cand_by_date.items():
        idx = rng.permutation(len(cands))[: a.cands]
        for i in idx:
            jobs.append((dkey, cands[i]))
    # the events' own legs
    for r in ev.itertuples():
        jobs.append((str(pd.Timestamp(r.T0).normalize())[:10],
                     {"asset": r.asset_id, "perp": r.derivative_symbol,
                      "spot": spot_symbol(r.asset_id, pd.Timestamp(r.T0)), "is_event": True}))
    print(f"legs to evaluate (non-price): {len(jobs)}")

    res: dict = {}
    rl = threading.Lock()
    done = [0]
    t0_by_date = {str(pd.Timestamp(t).normalize())[:10]: pd.Timestamp(t) for t in ev["T0"]}

    def work(job):
        dkey, cd = job
        t0 = t0_by_date[dkey]
        with httpx.Client(headers=UA, timeout=90, follow_redirects=True) as c:
            try:
                p = leg_stats(c, "perp", cd["perp"], t0) if cd.get("perp") else None
                s = leg_stats(c, "spot", cd["spot"], t0) if cd.get("spot") else None
            except RuntimeError as e:
                with rl:
                    print(f"  STOP condition: {e}", flush=True)
                raise
        with rl:
            res[(dkey, cd["asset"])] = {"cd": cd, "perp": p, "spot": s}
            done[0] += 1
            if done[0] % 200 == 0:
                print(f"  {done[0]}/{len(jobs)} legs", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, jobs))

    # ------------------------------------------------------------------ assemble
    rows = []
    for (dkey, asset), v in res.items():
        p, s, cd = v["perp"], v["spot"], v["cd"]
        if p is None or s is None:
            rows.append({"date": dkey, "asset": asset, "is_event": bool(cd.get("is_event")),
                         "eligible": False, "reason": "NO_DATA"})
            continue
        both = p["valid_buckets"] & s["valid_buckets"]
        rows.append({
            "date": dkey, "asset": asset, "perp": cd["perp"], "spot": cd["spot"],
            "is_event": bool(cd.get("is_event")),
            "perp_avail": p["availability"], "spot_avail": s["availability"],
            "perp_valid_buckets": p["n_valid_buckets"], "spot_valid_buckets": s["n_valid_buckets"],
            "both_valid_buckets": len(both),
            "valid_transitions": valid_transitions(both),
            "vwap_fields_ok_perp": p["buckets_with_positive_base_and_quote"] == p["n_valid_buckets"],
            "vwap_fields_ok_spot": s["buckets_with_positive_base_and_quote"] == s["n_valid_buckets"],
            "median_hourly_notional": p["median_hourly_notional"],
            "liq_bucket": liq_bucket(p["median_hourly_notional"]),
            "eligible": bool(p["availability"] >= AVAIL_BAR and s["availability"] >= AVAIL_BAR),
            "reason": "OK" if (p["availability"] >= AVAIL_BAR and s["availability"] >= AVAIL_BAR) else "AVAILABILITY",
            "_both": both,
        })
    L = pd.DataFrame(rows)
    L.drop(columns=["_both"], errors="ignore").to_parquet(RAW / "leg_stats.parquet")
    bucket_map = {(r["date"], r["asset"]): r.get("_both", set()) for r in rows}

    # ----------------------------------------------------- match controls to events (§A6)
    out = []
    for r in ev.itertuples():
        dkey = str(pd.Timestamp(r.T0).normalize())[:10]
        me = L[(L["date"] == dkey) & (L["asset"] == r.asset_id) & L["is_event"]]
        if not len(me) or not bool(me.iloc[0]["eligible"]):
            out.append({"full_delisting_event_id": r.full_delisting_event_id, "asset": r.asset_id,
                        "T0": r.T0, "excluded": True, "exclusion": "EVENT_LEG_UNAVAILABLE",
                        "n_controls": 0, "event_transitions": 0})
            continue
        m = me.iloc[0]
        ev_tag = tagged_at(r.asset_id, pd.Timestamp(r.T0))
        ev_liq = liq_bucket(r.median_hourly_notional_pre24h)
        pool = L[(L["date"] == dkey) & (~L["is_event"]) & L["eligible"]].copy()
        if len(pool):
            pool["tag"] = [tagged_at(x, pd.Timestamp(r.T0)) for x in pool["asset"]]
            pool = pool[(pool["liq_bucket"] == ev_liq) & (pool["tag"] == ev_tag)]
        # a control also needs enough shared valid transitions with THIS event (§A13)
        ok = []
        evb = bucket_map.get((dkey, r.asset_id), set())
        for c2 in pool.itertuples():
            shared = valid_transitions(evb, bucket_map.get((dkey, c2.asset), set()))
            if shared >= MIN_TRANSITIONS:
                ok.append({"asset": c2.asset, "perp": c2.perp, "spot": c2.spot, "shared_transitions": shared})
        out.append({
            "full_delisting_event_id": r.full_delisting_event_id, "asset": r.asset_id, "T0": r.T0,
            "event_transitions": int(m["valid_transitions"]),
            "event_liq_bucket": ev_liq, "event_tagged": ev_tag,
            "pool_metadata": meta_counts[dkey], "pool_evaluated": int((L["date"] == dkey).sum()) - 1,
            "pool_matched": int(len(pool)), "n_controls": len(ok),
            "vwap_fields_ok": bool(m["vwap_fields_ok_perp"] and m["vwap_fields_ok_spot"]),
            "excluded": bool(int(m["valid_transitions"]) < MIN_TRANSITIONS or len(ok) < MIN_CONTROLS),
            "exclusion": ("TRANSITIONS" if int(m["valid_transitions"]) < MIN_TRANSITIONS
                          else ("CONTROLS" if len(ok) < MIN_CONTROLS else None)),
            "controls": ";".join(x["asset"] for x in ok[:60]),
        })
    S = pd.DataFrame(out)
    S["year"] = pd.to_datetime(S["T0"]).dt.year
    S.to_parquet(RAW / "event_prefreeze.parquet")

    keep = S[~S["excluded"]]
    dev = keep[keep["year"] <= 2025]
    hold = keep[keep["year"] == 2026]

    def q(s: pd.Series) -> dict:
        return {k: (round(float(s.quantile(v)), 1) if len(s) else None) for k, v in
                [("p10", .10), ("p25", .25), ("median", .50), ("p75", .75), ("p90", .90)]}

    summary = {
        "no_price_field_loaded": "usecols=[0,5,7,8] = open time, base volume, quote volume, trade count; OHLC columns 1-4 were never read",
        "frozen_bars": {"MIN_CONTROLS": MIN_CONTROLS, "MIN_TRANSITIONS": MIN_TRANSITIONS,
                        "AVAILABILITY": AVAIL_BAR, "SEED": SEED, "candidates_evaluated_per_date": a.cands},
        "1_final_candidate_n": int(len(keep)),
        "2_controls_per_event": q(S["n_controls"]),
        "3_events_with_fewer_than_20_controls": int((S["n_controls"] < MIN_CONTROLS).sum()),
        "4_valid_transition_count": q(S["event_transitions"]),
        "5_events_below_73_transitions": int((S["event_transitions"] < MIN_TRANSITIONS).sum()),
        "6_vwap_field_availability": {
            "events_with_both_legs_fully_populated": int(S["vwap_fields_ok"].sum()),
            "share": round(float(S["vwap_fields_ok"].mean()), 4),
        },
        "7_development_holdout_after_exclusions": {
            "DEVELOPMENT_2023_2025": int(len(dev)), "HOLDOUT_2026": int(len(hold)),
            "by_year": keep.groupby("year").size().astype(int).to_dict(),
        },
        "8_exclusions": S.loc[S["excluded"], "exclusion"].value_counts().astype(int).to_dict(),
        "metadata_eligible_pool_per_date": {"min": min(meta_counts.values()),
                                            "median": int(np.median(list(meta_counts.values()))),
                                            "max": max(meta_counts.values())},
        "hard_sample_rule_A7": ("confirmatory" if len(keep) >= 50 else
                                ("exploratory_underpowered" if len(keep) >= 40 else "STOP")),
        "note": "Control eligibility is strictly point-in-time; a control delisted AFTER T0 remains a valid control (§A5).",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "h19_2_prefreeze.json").write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")
    print()
    print(json.dumps(summary, indent=1, default=str)[:2800])
    return 0


if __name__ == "__main__":
    sys.exit(main())
