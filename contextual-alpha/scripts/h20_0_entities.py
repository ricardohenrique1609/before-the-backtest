"""H20.0 — point-in-time entity resolution for the 105 asset-time units (CONTEXT_DATA_MODEL.md section 4).

For each (t, ticker):
  era        eras from the inherited symbol windows (A5 whitelist): an era breaks after > 365 days with
             no served route (A7). `era_at_t` uses only windows that had started by t. `n_eras_total`
             uses all windows and exists only to measure how often a mapping made with today's data
             would differ from the as-of-t mapping (ticker-era conflict); it is never a feature.
  name       from Binance notices published <= t whose title carries "(TICKER)" next to a listing
             verb. One distinct name -> RESOLVED; several -> AMBIGUOUS; none -> NOT_FOUND.
             No third-party or current metadata is consulted.
  type       leveraged tokens (TICKER ending UP/DOWN/BULL/BEAR whose own notice says "leveraged") are
             venue products, typed BLVT, not projects.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_entities.py"
"""

from __future__ import annotations

import re
from datetime import timedelta

import pandas as pd

from h20_common import INTERIM, RAW, load_freeze

LISTING = re.compile(r"\b(?:list|lists|listed|listing|will list|adds?|will add|launchpool|launchpad|"
                     r"introducing|open trading|will open trading|airdrop)\b", re.I)
LEAD = re.compile(r"^(?:.*?\b(?:binance\s+)?(?:will\s+)?(?:lists?|adds?|introduc\w*|launch\w*|"
                  r"open\w*\s+trading\s+for|support\w*)\s+)", re.I)
ERA_GAP = timedelta(days=365)


def eras(win: pd.DataFrame) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    out: list[list[pd.Timestamp]] = []
    for _, w in win.sort_values("first_candle").iterrows():
        if out and w["first_candle"] <= out[-1][1] + ERA_GAP:
            out[-1][1] = max(out[-1][1], w["last_candle"])
        else:
            out.append([w["first_candle"], w["last_candle"]])
    return [(a, b) for a, b in out]


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def names_for(ticker: str, titles: pd.DataFrame) -> list[str]:
    pat = re.compile(rf"([A-Za-z0-9][\w.\-&'’ ]{{0,48}}?)\s*\(\s*{re.escape(ticker)}\s*\)")
    found = []
    for title in titles["title"]:
        if not LISTING.search(title):
            continue
        for seg in pat.findall(title):
            seg = re.split(r",|\band\b|&", seg)[-1].strip()
            seg = LEAD.sub("", seg).strip()
            seg = re.sub(r"^(?:the|new)\s+", "", seg, flags=re.I).strip()
            if seg and seg.upper() != ticker and len(seg) <= 40:
                found.append(seg)
    return found


STRICT_VERB = r"(?:will\s+list|lists|will\s+add|adds|introducing|launchpool|launchpad|megadrop|hodler\s+airdrops?:?)"


def names_v2(ticker: str, titles: pd.DataFrame) -> list[tuple[pd.Timestamp, str]]:
    """Parser v2 (see H20_0_EXECUTION_DEVIATION.md): a name is the text between a listing verb and
    '(TICKER)'; a name equal to the ticker is a valid name; lists keep only the last segment."""
    pat = re.compile(rf"\b{STRICT_VERB}\s+(?:the\s+)?(.{{1,60}}?)\s*\(\s*{re.escape(ticker)}\s*\)", re.I)
    out = []
    for _, r in titles.sort_values("published_utc").iterrows():
        for seg in pat.findall(r["title"]):
            seg = re.split(r",|\band\b|&|\)", seg)[-1].strip()
            seg = re.sub(r"^(?:the|new)\s+", "", seg, flags=re.I).strip()
            if seg and len(seg) <= 40:
                out.append((r["published_utc"], seg))
    return out


def resolve(tk: str, before: pd.DataFrame, parser: str) -> dict:
    hits = before[before["title"].str.contains(rf"\(\s*{re.escape(tk)}\s*\)", regex=True)]
    if parser == "v1":
        distinct = sorted({norm(c): c for c in names_for(tk, hits)}.values(), key=str.lower)
        status = "RESOLVED" if len(distinct) == 1 else ("AMBIGUOUS" if len(distinct) > 1 else "NOT_FOUND")
        return {"name_candidates": "|".join(distinct), "name_status": status, "name_detail": status,
                "pit_name": distinct[0] if len(distinct) == 1 else None, "n_historical_names": len(distinct)}
    found = names_v2(tk, hits)
    distinct = list(dict.fromkeys(norm(n) for _, n in found))
    if found:
        latest = found[-1][1]
        return {"name_candidates": "|".join(dict.fromkeys(n for _, n in found)), "name_status": "RESOLVED",
                "name_detail": "RESOLVED_SINGLE_NAME" if len(distinct) == 1 else "RESOLVED_LATEST_OF_RENAMES",
                "pit_name": latest, "n_historical_names": len(distinct)}
    bare = before["title"].str.contains(rf"\b{STRICT_VERB}\s+{re.escape(tk)}\b", case=False, regex=True).any()
    return {"name_candidates": "", "name_status": "NOT_FOUND",
            "name_detail": "TICKER_ONLY_NOTICE" if bare else "NO_LISTING_NOTICE", "pit_name": None,
            "n_historical_names": 0}


def main() -> int:
    W = pd.read_parquet(RAW / "inherited" / "symbol_windows_whitelist.parquet")
    W = W[W["window_known"].fillna(False)].copy()
    for c in ("first_candle", "last_candle"):
        W[c] = pd.to_datetime(W[c], utc=True)
    U = pd.read_parquet(INTERIM / "binance_catalog.parquet")
    U["published_utc"] = pd.to_datetime(U["published_utc"], utc=True)
    return run(load_freeze()["sample"], INTERIM / "entity_resolution.parquet", W, U)


def run(sample: list, out, W: pd.DataFrame, U: pd.DataFrame) -> int:
    rows = []
    for s in sample:
        t = pd.Timestamp(s["t_utc"])
        before = U[U["published_utc"] <= t]
        for a in s["assets"]:
            tk = a["asset_ticker"]
            w = W[W["base_asset"] == tk]
            all_eras = eras(w)
            eras_t = eras(w[w["first_candle"] <= t])
            era_idx = len(eras_t)
            hits = before[before["title"].str.contains(rf"\(\s*{re.escape(tk)}\s*\)", regex=True)]
            blvt = bool(re.search(r"(UP|DOWN|BULL|BEAR)$", tk)) and before["title"].str.contains(
                rf"\b{re.escape(tk)}\b.*leveraged|leveraged.*\b{re.escape(tk)}\b", case=False, regex=True).any()
            blvt = blvt or (bool(re.search(r"(UP|DOWN)$", tk)) and before["title"].str.contains(
                "Leveraged Token", case=False).any() and tk[:-2] in set(W["base_asset"]))
            rows.append(
                {
                    "sample_id": s["sample_id"],
                    "t_utc": t,
                    "asset_ticker": tk,
                    "liquidity_tercile": a["liquidity_tercile"],
                    "entity_type": "BLVT" if blvt else "ASSET",
                    "entity_id": f"asset:{tk}#{era_idx}",
                    "era_at_t": era_idx,
                    "n_eras_total": len(all_eras),
                    "ticker_era_conflict": len(all_eras) > era_idx,
                    "first_route_utc": w["first_candle"].min(),
                    "asset_age_days": (t - w["first_candle"].min()).days,
                    "n_notices_with_paren_ticker_le_t": len(hits),
                }
                | {f"v1_{k}": v for k, v in resolve(tk, before, "v1").items()}
                | resolve(tk, before, "v2")
            )
    D = pd.DataFrame(rows)
    D.to_parquet(out, index=False)
    print(D["v1_name_status"].value_counts(), D["name_detail"].value_counts(), D["entity_type"].value_counts(),
          D["ticker_era_conflict"].sum())
    print(D[["sample_id", "asset_ticker", "entity_type", "v1_name_status", "name_detail", "pit_name"]].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
