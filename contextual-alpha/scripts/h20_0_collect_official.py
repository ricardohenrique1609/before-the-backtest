"""H20.0 — official public sources for C1 (macro) and C2 (political / regulatory).

  fed     Federal Reserve press-release feed (one JSON, all items); time of day in US Eastern
  fr      Federal Register API, fixed crypto term list, per sample window
  sec     SEC newsroom press-release listings for the months touching each window
  cftc    CFTC press-release listings for the years touching each window
  alfred  ALFRED vintages of CPIAUCSL, UNRATE, DFF as of the day before t, and today's vintage

Every document in a window is kept; the crypto tag (governance section 3) only splits counts.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_collect_official.py" [--only fed,fr,sec,cftc,alfred]
"""

from __future__ import annotations

import argparse
import html
import io
import json
import re
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from h20_common import INTERIM, RAW, get, iso, load_freeze, save_raw

ET = ZoneInfo("America/New_York")
CRYPTO_RE = re.compile(
    r"crypto|digital asset|virtual currenc|bitcoin|stablecoin|blockchain|token|coin offering|binance|\bether\b", re.I
)
FR_TERM = 'cryptocurrency | "digital asset" | "virtual currency" | bitcoin | stablecoin'


def stamps() -> list[tuple[str, datetime]]:
    return [
        (s["sample_id"], datetime.fromisoformat(s["t_utc"].replace("Z", "+00:00")))
        for s in load_freeze()["sample"]
    ]


def day_end_utc(d, tz=ET) -> datetime:
    """T2 rule: a day-only document becomes admissible at the next local midnight."""
    return datetime(d.year, d.month, d.day, tzinfo=tz).astimezone(UTC) + timedelta(days=1)


def in_w7(avail: datetime, t: datetime) -> bool:
    return t - timedelta(days=7) < avail <= t


# ---------------------------------------------------------------- Fed
def fed() -> None:
    r = get("https://www.federalreserve.gov/json/ne-press.json", purpose="fed:feed")
    save_raw("fed", f"ne-press_{r.sha256[:12]}.json", r.content)
    items = json.loads(r.content.decode("utf-8-sig"))
    rows = []
    for x in items:
        if "d" not in x:  # trailing {'updateDate': ...} record
            continue
        has_time = " " in x["d"].strip()
        if has_time:
            local = datetime.strptime(x["d"], "%m/%d/%Y %I:%M:%S %p").replace(tzinfo=ET)
            pub, avail = local.astimezone(UTC), local.astimezone(UTC)
        else:
            d = datetime.strptime(x["d"], "%m/%d/%Y").date()
            local, pub, avail = None, None, day_end_utc(d)
        rows.append(
            {
                "source_id": "S_FED_PRESS",
                "source_document_key": x["l"],
                "title": html.unescape(x["t"]),
                "doc_type": x.get("pt"),
                "raw_date": x["d"],
                "has_time": has_time,
                "publication_time": pub,
                "public_availability_time": avail,
                "midnight_stamp": bool(local and local.hour == 0 and local.minute == 0),
                "url": "https://www.federalreserve.gov" + x["l"],
            }
        )
    D = pd.DataFrame(rows)
    D.to_parquet(INTERIM / "fed_feed.parquet", index=False)
    print("fed items", len(D), D["public_availability_time"].min(), D["public_availability_time"].max())
    print(D.assign(y=D["public_availability_time"].dt.year).groupby("y")["has_time"].mean().tail(12))
    assign(D, "public_availability_time", "fed")


# ---------------------------------------------------------------- Federal Register
def fr() -> None:
    rows = []
    for sid, t in stamps():
        lo, hi = (t - timedelta(days=8)).date(), t.date()
        page = 1
        while True:
            p = {
                "conditions[term]": FR_TERM,
                "conditions[publication_date][gte]": lo.isoformat(),
                "conditions[publication_date][lte]": hi.isoformat(),
                "per_page": 100,
                "page": page,
                "fields[]": ["document_number", "publication_date", "type", "title", "html_url", "agencies"],
            }
            r = get("https://www.federalregister.gov/api/v1/documents.json", p, purpose="fr:window")
            if r.outcome != "OK":
                rows.append({"sample_id": sid, "fetch_outcome": r.outcome})
                break
            save_raw("federal_register", f"{sid}_p{page}_{r.sha256[:12]}.json", r.content)
            j = json.loads(r.content)
            for x in j.get("results") or []:
                d = datetime.fromisoformat(x["publication_date"]).date()
                rows.append(
                    {
                        "sample_id": sid,
                        "fetch_outcome": "OK",
                        "source_id": "S_FEDREG",
                        "source_document_key": x["document_number"],
                        "title": x["title"],
                        "doc_type": x.get("type"),
                        "agencies": ";".join(a.get("name", "") or "" for a in x.get("agencies") or []),
                        "publication_date": d.isoformat(),
                        "public_availability_time": day_end_utc(d),
                        "url": x["html_url"],
                        "in_w7": in_w7(day_end_utc(d), t),
                    }
                )
            if page >= (j.get("total_pages") or 1):
                break
            page += 1
    D = pd.DataFrame(rows)
    D.to_parquet(INTERIM / "fr_windows.parquet", index=False)
    print("fr rows", len(D), D.get("in_w7", pd.Series(dtype=bool)).sum())


# ---------------------------------------------------------------- SEC
SEC_ITEM = re.compile(
    r'<time[^>]*datetime="([^"]+)"[^>]*>.*?href="(/newsroom/press-releases/[^"#?]+)"[^>]*>(.*?)</a>', re.S
)


def sec() -> None:
    months = set()
    for _, t in stamps():
        for d in (t - timedelta(days=7), t):
            months.add((d.year, d.month))
    rows = []
    for y, m in sorted(months):
        seen, page = set(), 0
        while page < 10:
            p = {"year": str(y), "month": str(m)} | ({"page": str(page)} if page else {})
            r = get("https://www.sec.gov/newsroom/press-releases", p, purpose="sec:listing")
            if r.outcome != "OK":
                rows.append({"listing": f"{y}-{m:02d}", "fetch_outcome": r.outcome})
                break
            save_raw("sec", f"list_{y}_{m:02d}_p{page}_{r.sha256[:12]}.html", r.content)
            h = r.content.decode("utf-8", "replace")
            new = 0
            for ts, href, title in SEC_ITEM.findall(h):
                if href in seen:
                    continue
                seen.add(href)
                new += 1
                rows.append(
                    {
                        "listing": f"{y}-{m:02d}",
                        "fetch_outcome": "OK",
                        "source_id": "S_SEC_PRESS",
                        "source_document_key": href.rsplit("/", 1)[-1],
                        "title": html.unescape(re.sub(r"<[^>]+>", "", title)).strip(),
                        "publication_time": pd.Timestamp(ts).tz_convert("UTC") if pd.Timestamp(ts).tzinfo else pd.Timestamp(ts, tz="UTC"),
                        "url": "https://www.sec.gov" + href,
                    }
                )
            if new == 0:
                break
            page += 1
    D = pd.DataFrame(rows).drop_duplicates(subset=["source_document_key"], keep="first")
    D.to_parquet(INTERIM / "sec_listing.parquet", index=False)
    print("sec rows", len(D))
    assign(D[D["fetch_outcome"] == "OK"], "publication_time", "sec")


# ---------------------------------------------------------------- CFTC
CFTC_ROW = re.compile(
    r'<time datetime="([^"]+)">(\d{2}/\d{2}/\d{4})</time>.*?href="(/PressRoom/PressReleases/(\d+-\d+))"[^>]*>(.*?)</a>', re.S
)


def cftc() -> None:
    need: dict[int, datetime] = {}
    for _, t in stamps():
        for d in (t - timedelta(days=7), t):
            need[d.year] = min(need.get(d.year, t), t - timedelta(days=8))
    rows = []
    for y in sorted(need):
        page, seen = 0, set()
        while page < 80:
            cached = sorted((RAW / "cftc").glob(f"list_{y}_p{page}_*.html"))
            if cached:  # raw is write-once; a page already received is parsed, not re-requested
                h = cached[0].read_bytes().decode("utf-8", "replace")
            else:
                p = {"year": str(y)} | ({"page": str(page)} if page else {})
                r = get("https://www.cftc.gov/PressRoom/PressReleases", p, purpose="cftc:listing")
                if r.outcome != "OK":
                    rows.append({"listing": str(y), "fetch_outcome": r.outcome, "status": r.status})
                    break
                save_raw("cftc", f"list_{y}_p{page}_{r.sha256[:12]}.html", r.content)
                h = r.content.decode("utf-8", "replace")
            new, oldest = 0, None
            for ts, ds, href, key, title in CFTC_ROW.findall(h):
                if key in seen:
                    continue
                seen.add(key)
                new += 1
                stamp = pd.Timestamp(ts).tz_convert("UTC")
                oldest = stamp if oldest is None else min(oldest, stamp)
                rows.append(
                    {
                        "listing": str(y),
                        "fetch_outcome": "OK",
                        "source_id": "S_CFTC_PRESS",
                        "source_document_key": key,
                        "title": html.unescape(re.sub(r"<[^>]+>", "", title)).strip(),
                        "publication_date": datetime.strptime(ds, "%m/%d/%Y").date().isoformat(),
                        "publication_time": stamp,
                        "url": "https://www.cftc.gov" + href,
                    }
                )
            if new == 0 or (oldest is not None and oldest < need[y]):
                break
            page += 1
    D = pd.DataFrame(rows)
    ok = D["fetch_outcome"] == "OK"  # keep one blocked row per year; de-duplicate documents only
    D = pd.concat([D[ok].drop_duplicates(subset=["source_document_key"]), D[~ok].drop_duplicates(subset=["listing"])])
    D.to_parquet(INTERIM / "cftc_listing.parquet", index=False)
    print("cftc rows", len(D))
    assign(D[D["fetch_outcome"] == "OK"], "publication_time", "cftc")


# ---------------------------------------------------------------- window assignment
def assign(D: pd.DataFrame, col: str, name: str) -> None:
    rows = []
    ts = pd.to_datetime(D[col], utc=True)
    for sid, t in stamps():
        m = (ts > t - timedelta(days=7)) & (ts <= t)
        for i in D.index[m]:
            rows.append({"sample_id": sid, "source_document_key": D.at[i, "source_document_key"]})
    pd.DataFrame(rows).to_parquet(INTERIM / f"{name}_w7.parquet", index=False)
    print(name, "window rows", len(rows))


# ---------------------------------------------------------------- ALFRED
SERIES = ["CPIAUCSL", "UNRATE", "DFF"]


def alfred() -> None:
    rows = []
    current = {}
    for s in SERIES:
        r = get("https://fred.stlouisfed.org/graph/fredgraph.csv", {"id": s}, purpose="alfred:current")
        save_raw("alfred", f"{s}_current_{r.sha256[:12]}.csv", r.content)
        current[s] = pd.read_csv(io.BytesIO(r.content)) if r.outcome == "OK" else None
    for sid, t in stamps():
        vint = (t - timedelta(days=1)).date().isoformat()
        for s in SERIES:
            r = get(
                "https://alfred.stlouisfed.org/graph/alfredgraph.csv",
                {"id": s, "vintage_date": vint},
                purpose="alfred:vintage",
            )
            row = {"sample_id": sid, "series": s, "vintage_date": vint, "fetch_outcome": r.outcome}
            if r.outcome == "OK":
                save_raw("alfred", f"{s}_{vint}_{r.sha256[:12]}.csv", r.content)
                v = pd.read_csv(io.BytesIO(r.content))
                v.columns = ["date", "value"]
                v["value"] = pd.to_numeric(v["value"], errors="coerce")
                v = v.dropna()
                c = current[s]
                row["vintage_last_obs"] = v["date"].max()
                row["vintage_n_obs"] = len(v)
                if c is not None:
                    c = c.copy()
                    c.columns = ["date", "value"]
                    c["value"] = pd.to_numeric(c["value"], errors="coerce")
                    j = v.merge(c, on="date", suffixes=("_vint", "_now"))
                    recent = j[j["date"] >= (pd.Timestamp(vint) - pd.Timedelta(days=400)).date().isoformat()]
                    row["recent_obs_compared"] = len(recent)
                    row["recent_obs_revised"] = int((recent["value_vint"] - recent["value_now"]).abs().gt(1e-9).sum())
            rows.append(row)
    D = pd.DataFrame(rows)
    D.to_parquet(INTERIM / "alfred_vintages.parquet", index=False)
    print(D.groupby("series")[["recent_obs_compared", "recent_obs_revised"]].sum())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="fed,fr,sec,cftc,alfred")
    a = ap.parse_args()
    INTERIM.mkdir(parents=True, exist_ok=True)
    for name in a.only.split(","):
        {"fed": fed, "fr": fr, "sec": sec, "cftc": cftc, "alfred": alfred}[name]()
    print("done", iso(datetime.now(tz=UTC)))
