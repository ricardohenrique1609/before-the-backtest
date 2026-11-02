"""H20.0 — Binance CMS (C4, and C5 via notices naming an asset). Inheritance A1/A2: regenerated.

Stage 1  harvest every catalogue the CMS serves (48, 49, 51, 93, 128, 161), all pages, with the
         H18.1b coverage guard: a catalogue below 99% of its own reported total is marked
         INCOMPLETE (the run still writes, the audit counts it as a coverage failure).
Stage 2  diff against the inherited snapshot data/raw/h18_1b/catalog_titles.parquet (read-only):
         notices present then and gone now, and notices the snapshot never had.
Stage 3  article detail for every notice whose releaseDate falls in a sample W7 window.

No query is outcome-shaped: the catalogue is taken whole, details are id lookups.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_collect_binance.py" [--stage 1|2|3|all]
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta

import pandas as pd

from h20_common import INTERIM, RAW, ROOT, Resp, get, iso, load_freeze, save_raw, sha256_file

LIST = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"
DETAIL = "https://www.binance.com/bapi/composite/v1/public/cms/article/detail/query"
CATALOGS = [48, 49, 51, 93, 128, 161]
MIN_COVERAGE = 0.99
SNAPSHOT = ROOT / "data/raw/h18_1b/catalog_titles.parquet"
SRC = "binance_cms"


def fetch_page(cid: int, page: int):
    r = get(LIST, {"type": 1, "catalogId": cid, "pageNo": page, "pageSize": 50}, purpose=f"{SRC}:list")
    if r.outcome != "OK":
        return None, None, r
    try:
        cat = json.loads(r.content)["data"]["catalogs"][0]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return None, None, r
    save_raw(SRC, f"list_{cid}_{page:03d}_{r.sha256[:12]}.json", r.content)
    return cat.get("articles") or [], cat.get("total"), r


def stage1() -> None:
    rows, summary = [], {}
    for cid in CATALOGS:
        arts, total, _ = fetch_page(cid, 1)
        if arts is None:
            summary[cid] = {"reported_total": None, "harvested": 0, "status": "ACCESS_BLOCKED"}
            continue
        pages = (total + 49) // 50
        got = {1: arts}
        failed = []
        for p in range(2, pages + 1):
            a, _, _ = fetch_page(cid, p)
            if not a:
                failed.append(p)
            else:
                got[p] = a
        for p in list(failed):  # slow re-sweep: one bad response costs at most its own page
            a, _, _ = fetch_page(cid, p)
            if a:
                got[p] = a
                failed.remove(p)
        n = 0
        for p, arts in sorted(got.items()):
            for x in arts:
                n += 1
                rows.append(
                    {
                        "catalog_id": cid,
                        "page": p,
                        "code": str(x.get("code")),
                        "cms_id": x.get("id"),
                        "title": str(x.get("title") or ""),
                        "release_ms": x.get("releaseDate"),
                    }
                )
        cov = n / total if total else 0.0
        summary[cid] = {
            "reported_total": total,
            "harvested": n,
            "coverage": round(cov, 4),
            "failed_pages": failed,
            "status": "COMPLETE" if cov >= MIN_COVERAGE else "INCOMPLETE",
        }
        print(cid, summary[cid], flush=True)
    T = pd.DataFrame(rows)
    T["published_utc"] = pd.to_datetime(T["release_ms"], unit="ms", utc=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    T.to_parquet(INTERIM / "binance_catalog_memberships.parquet", index=False)
    U = (
        T.sort_values(["code", "catalog_id"])
        .groupby("code", as_index=False)
        .agg(
            title=("title", "first"),
            release_ms=("release_ms", "first"),
            published_utc=("published_utc", "first"),
            catalogs=("catalog_id", lambda s: ";".join(str(int(c)) for c in sorted(set(s)))),
            n_release_values=("release_ms", "nunique"),
        )
    )
    U.to_parquet(INTERIM / "binance_catalog.parquet", index=False)
    summary = {
        "harvest_utc": iso(datetime.now(tz=UTC)),
        "catalogs": summary,
        "memberships": len(T),
        "unique_articles": len(U),
    }
    (INTERIM / "binance_harvest_summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps(summary, indent=1, default=str))


def repair() -> None:
    """Re-fetch the failed pages of INCOMPLETE catalogues after a pause, merge, rebuild."""
    summ = json.loads((INTERIM / "binance_harvest_summary.json").read_text())
    M = pd.read_parquet(INTERIM / "binance_catalog_memberships.parquet")
    add = []
    for cid, s in summ["catalogs"].items():
        for p in list(s.get("failed_pages") or []):
            a, _, _ = fetch_page(int(cid), int(p))
            if not a:
                continue
            s["failed_pages"].remove(p)
            for x in a:
                add.append({"catalog_id": int(cid), "page": int(p), "code": str(x.get("code")), "cms_id": x.get("id"),
                            "title": str(x.get("title") or ""), "release_ms": x.get("releaseDate")})
        if add:
            pass
    if add:
        A = pd.DataFrame(add)
        A["published_utc"] = pd.to_datetime(A["release_ms"], unit="ms", utc=True)
        M = pd.concat([M, A], ignore_index=True).drop_duplicates(["catalog_id", "code"])
    for cid, s in summ["catalogs"].items():
        n = int((M["catalog_id"] == int(cid)).sum())
        s["harvested"] = n
        s["coverage"] = round(n / s["reported_total"], 4) if s.get("reported_total") else 0.0
        s["status"] = "COMPLETE" if s["coverage"] >= MIN_COVERAGE else "INCOMPLETE"
        s["repaired"] = True
    M.to_parquet(INTERIM / "binance_catalog_memberships.parquet", index=False)
    U = (
        M.sort_values(["code", "catalog_id"])
        .groupby("code", as_index=False)
        .agg(title=("title", "first"), release_ms=("release_ms", "first"), published_utc=("published_utc", "first"),
             catalogs=("catalog_id", lambda s: ";".join(str(int(c)) for c in sorted(set(s)))),
             n_release_values=("release_ms", "nunique"))
    )
    U.to_parquet(INTERIM / "binance_catalog.parquet", index=False)
    summ["memberships"], summ["unique_articles"] = len(M), len(U)
    summ["repair_utc"] = iso(datetime.now(tz=UTC))
    (INTERIM / "binance_harvest_summary.json").write_text(json.dumps(summ, indent=1, default=str))
    print(json.dumps(summ["catalogs"], indent=1))


def stage2() -> None:
    U = pd.read_parquet(INTERIM / "binance_catalog.parquet")
    M = pd.read_parquet(INTERIM / "binance_catalog_memberships.parquet")
    S = pd.read_parquet(SNAPSHOT)  # inherited A1, read-only
    snap_cut = pd.to_datetime(S["release_ms"].max(), unit="ms", utc=True)
    fresh = set(U["code"])
    snap = set(S["announcement_id"].astype(str))
    gone = S[~S["announcement_id"].astype(str).isin(fresh)].copy()
    old_enough = U[U["published_utc"] <= snap_cut]
    missed = old_enough[~old_enough["code"].isin(snap)].copy()
    missed["year"] = missed["published_utc"].dt.year
    # catalogue membership of what the snapshot missed
    mm = M[M["code"].isin(set(missed["code"]))]
    out = {
        "snapshot_path": str(SNAPSHOT.relative_to(ROOT)).replace("\\", "/"),
        "snapshot_rows": len(S),
        "snapshot_newest_utc": iso(snap_cut.to_pydatetime()),
        "fresh_unique_articles": len(U),
        "fresh_articles_released_by_snapshot_newest": len(old_enough),
        "snapshot_codes_absent_now": len(gone),
        "absent_now_by_catalog": gone["catalog_id"].value_counts().sort_index().to_dict(),
        "absent_now_by_year": pd.to_datetime(gone["release_ms"], unit="ms").dt.year.value_counts().sort_index().to_dict(),
        "fresh_codes_missing_from_snapshot": len(missed),
        "missing_from_snapshot_by_year": missed["year"].value_counts().sort_index().to_dict(),
        "missing_from_snapshot_by_catalog": mm["catalog_id"].value_counts().sort_index().to_dict(),
        "fresh_catalog49_oldest_utc": iso(M.loc[M["catalog_id"] == 49, "published_utc"].min().to_pydatetime()),
        "snapshot_catalog49_rows": int((S["catalog_id"] == 49).sum()),
        "fresh_catalog49_rows": int((M["catalog_id"] == 49).sum()),
    }
    gone[["catalog_id", "announcement_id", "release_ms"]].to_csv(INTERIM / "binance_snapshot_absent_now.csv", index=False)
    (INTERIM / "binance_snapshot_diff.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))


def body_text(node) -> str:
    if isinstance(node, str):
        try:
            node = json.loads(node)
        except json.JSONDecodeError:
            return node
    out: list[str] = []

    def walk(n):
        if isinstance(n, dict):
            if n.get("node") == "text":
                out.append(n.get("text", ""))
            for c in n.get("child", []) or []:
                walk(c)
        elif isinstance(n, list):
            for c in n:
                walk(c)

    walk(node)
    return " ".join(out)


def windows() -> list[tuple[str, datetime]]:
    F = load_freeze()
    return [(s["sample_id"], datetime.fromisoformat(s["t_utc"].replace("Z", "+00:00"))) for s in F["sample"]]


def stage3(tag: str = "detail") -> None:
    U = pd.read_parquet(INTERIM / "binance_catalog.parquet")
    want: dict[str, list[str]] = {}
    for sid, t in windows():
        w = U[(U["published_utc"] > t - timedelta(days=7)) & (U["published_utc"] <= t)]
        for c in w["code"]:
            want.setdefault(c, []).append(sid)
    print(f"{len(want)} articles in W7 windows", flush=True)
    out = INTERIM / f"binance_{tag}.parquet"
    prev = pd.read_parquet(out) if out.exists() else None
    if prev is not None:  # incremental: keep earlier successful fetches, refresh window membership
        done = set(prev.loc[prev["outcome"] == "OK", "code"])
        prev = prev[prev["code"].isin(done) & prev["code"].isin(want)].copy()
        prev["sample_ids"] = prev["code"].map(lambda c: ";".join(want[c]))
        want = {c: s for c, s in want.items() if c not in done}
        print(f"incremental: {len(done)} already fetched, {len(want)} to fetch", flush=True)
    rows = []
    for i, (code, sids) in enumerate(sorted(want.items())):
        cached = sorted((RAW / SRC).glob(f"{tag}_{code}_*.json")) if tag == "detail" else []
        if cached:  # raw is write-once: a body already received is parsed, not re-requested
            c = cached[0]
            r = Resp(200, "OK", c.read_bytes(), DETAIL, sha256_file(c),
                     iso(datetime.fromtimestamp(c.stat().st_mtime, tz=UTC)), {})
        else:
            r = get(DETAIL, {"articleCode": code}, purpose=f"{SRC}:{tag}", lookup=code)
        row = {"code": code, "sample_ids": ";".join(sids), "outcome": r.outcome, "status": r.status,
               "ingest_time": r.ingest_time, "raw_sha256": r.sha256, "from_cache": bool(cached)}
        if r.outcome == "OK":
            save_raw(SRC, f"{tag}_{code}_{r.sha256[:12]}.json", r.content)
            try:
                d = json.loads(r.content).get("data") or {}
            except json.JSONDecodeError:
                d = {}
            row.update(
                {
                    "title_detail": d.get("title"),
                    "publish_ms": d.get("publishDate"),
                    "version": d.get("version"),
                    "last_update_ms": d.get("lastUpdateTime"),
                    "first_catalog_id": d.get("firstCatalogId"),
                    "body_text": body_text(d.get("body") or ""),
                    "pairs": json.dumps(d.get("pairs")) if d.get("pairs") is not None else None,
                    "has_data": bool(d),
                }
            )
        rows.append(row)
        if i % 100 == 0:
            print(i, code, r.outcome, flush=True)
    D = pd.DataFrame(rows)
    if prev is not None:
        D = pd.concat([prev, D], ignore_index=True)
    D.to_parquet(out, index=False)
    print(D["outcome"].value_counts())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all")
    a = ap.parse_args()
    if a.stage in ("1", "all"):
        stage1()
    if a.stage == "repair":
        repair()
    if a.stage in ("2", "all"):
        stage2()
    if a.stage in ("3", "all"):
        stage3()
