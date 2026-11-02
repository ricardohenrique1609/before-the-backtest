"""H20.0 — archive persistence, publication-stamp validation and refetch stability (plan section 5.3, 5.5).

  archive  Wayback CDX first 200-capture for a seeded subsample of window documents from each source,
           and for crypto-tagged plus random GDELT URLs; a live GET of each GDELT URL (status only,
           no body kept) measures link rot. Capture <= t makes a document V1_ARCHIVED_AT_T; a first
           capture earlier than the publisher's stamp flags STAMP_AFTER_CAPTURE.
  refetch  re-fetches a seeded subsample per source and compares content hashes with the first fetch.

All lookups are id lookups of documents already collected (governance section 3).

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_archive_refetch.py" --part archive|refetch
"""

from __future__ import annotations

import argparse
import html
import json
import re
import time
from datetime import datetime

import numpy as np
import pandas as pd

from h20_common import INTERIM, RAW, content_hash, get, load_freeze

SEED = 20261020
PER_T = 3  # documents per sample timestamp and source for the archive subsample
CDX = "http://web.archive.org/cdx/search/cdx"


def stamps() -> dict[str, pd.Timestamp]:
    return {s["sample_id"]: pd.Timestamp(s["t_utc"]) for s in load_freeze()["sample"]}


def pick(df: pd.DataFrame, k: int, rng) -> pd.DataFrame:
    if len(df) <= k:
        return df
    return df.iloc[sorted(rng.choice(len(df), size=k, replace=False))]


def first_capture(url: str) -> dict:
    p = {"url": url, "output": "json", "fl": "timestamp,statuscode,digest", "filter": "statuscode:200", "limit": 1}
    r = get(CDX, p, purpose="archive:cdx", lookup=url, retries=2)
    if r.outcome != "OK":
        return {"cdx_outcome": r.outcome}
    try:
        rows = json.loads(r.content or b"[]")
    except json.JSONDecodeError:
        return {"cdx_outcome": "PARSE_ERROR"}
    if len(rows) < 2:
        return {"cdx_outcome": "OK", "captured": False}
    ts = pd.Timestamp(datetime.strptime(rows[1][0], "%Y%m%d%H%M%S"), tz="UTC")
    return {"cdx_outcome": "OK", "captured": True, "first_capture_utc": ts}


def candidates(rng) -> pd.DataFrame:
    T = stamps()
    out = []

    def add(src, sid, key, url, pub, alt_url=None):
        out.append({"source_id": src, "sample_id": sid, "source_document_key": key, "url": url,
                    "alt_url": alt_url, "publication_time": pub, "t_utc": T[sid]})

    B = pd.read_parquet(INTERIM / "binance_catalog.parquet")
    for sid, t in T.items():
        w = B[(pd.to_datetime(B["published_utc"], utc=True) > t - pd.Timedelta(days=7))
              & (pd.to_datetime(B["published_utc"], utc=True) <= t)].sort_values("code")
        for _, r in pick(w, PER_T, rng).iterrows():
            add("S_BINANCE_CMS", sid, r["code"], f"https://www.binance.com/en/support/announcement/{r['code']}",
                pd.Timestamp(r["published_utc"]))
    for name, src, col in (("fed", "S_FED_PRESS", "public_availability_time"), ("sec", "S_SEC_PRESS", "publication_time"),
                           ("cftc", "S_CFTC_PRESS", "publication_time")):
        f = INTERIM / f"{name}_w7.parquet"
        if not f.exists():
            continue
        W = pd.read_parquet(f)
        D = pd.read_parquet(INTERIM / ({"fed": "fed_feed", "sec": "sec_listing", "cftc": "cftc_listing"}[name] + ".parquet"))
        D = D[D["source_document_key"].notna()].drop_duplicates("source_document_key").set_index("source_document_key")
        for sid, g in W.groupby("sample_id"):
            for k in pick(g.sort_values("source_document_key"), PER_T, rng)["source_document_key"]:
                url = D.at[k, "url"]
                alt = url.replace("/newsroom/press-releases/", "/news/press-release/") if name == "sec" else None
                add(src, sid, k, url, pd.Timestamp(D.at[k, col]), alt)
    G = pd.read_parquet(INTERIM / "gdelt_records.parquet", columns=["sample_id", "gkg_id", "url", "crypto", "slice_utc", "feed"])
    G = G[G["url"].str.startswith("http", na=False)]
    for sid, g in G.groupby("sample_id"):
        c = pick(g[g["crypto"]].sort_values("gkg_id"), 8, rng)
        n = pick(g[~g["crypto"]].sort_values("gkg_id"), 4, rng)
        for _, r in pd.concat([c, n]).iterrows():
            add("S_GDELT_GKG", sid, r["gkg_id"], r["url"], pd.Timestamp(r["slice_utc"]))
            out[-1]["crypto"] = bool(r["crypto"])
            out[-1]["feed"] = r["feed"]
    return pd.DataFrame(out)


def archive() -> None:
    rng = np.random.default_rng(SEED)
    C = candidates(rng)
    print(C.groupby("source_id").size(), flush=True)
    rows = []
    for i, r in C.iterrows():
        row = r.to_dict() | first_capture(r["url"])
        if isinstance(r.get("alt_url"), str):
            alt = first_capture(r["alt_url"])
            row |= {f"alt_{k}": v for k, v in alt.items()}
        if r["source_id"] == "S_GDELT_GKG":
            live = get(r["url"], purpose="archive:live", lookup=r["url"], retries=1)
            row |= {"live_status": live.status, "live_outcome": live.outcome}
        rows.append(row)
        if i % 50 == 0:
            print(i, r["source_id"], row.get("cdx_outcome"), flush=True)
    pd.DataFrame(rows).to_parquet(INTERIM / "archive_checks.parquet", index=False)


def binance_slug_url(code: str, title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
    return f"https://www.binance.com/en/support/announcement/{slug}-{code}"


def binance_recheck() -> None:
    """Deviation D6: Binance article URLs since ~2023 carry a title slug before the code, so the
    code-only URL used by `archive` misses their captures. Re-check every Binance row of the archive
    subsample under three URL forms and keep the earliest capture."""
    A = pd.read_parquet(INTERIM / "archive_checks.parquet")
    B = pd.read_parquet(INTERIM / "binance_catalog.parquet").set_index("code")
    idx = A.index[A["source_id"] == "S_BINANCE_CMS"]
    for i in idx:
        code = A.at[i, "source_document_key"]
        variants = {"slug": binance_slug_url(code, B.at[code, "title"]),
                    "detail": f"https://www.binance.com/en/support/announcement/detail/{code}"}
        caps = [A.at[i, "first_capture_utc"]] if A.at[i, "captured"] is True else []
        outcomes = [A.at[i, "cdx_outcome"]]
        for name, u in variants.items():
            r = first_capture(u)
            if r["cdx_outcome"] == "ACCESS_BLOCKED":  # IA 'Temporarily Offline': one slow retry
                time.sleep(30)
                r = first_capture(u)
            outcomes.append(r["cdx_outcome"])
            A.at[i, f"{name}_cdx_outcome"] = r["cdx_outcome"]
            if r.get("captured"):
                caps.append(r["first_capture_utc"])
        A.at[i, "cdx_outcome"] = "OK" if all(o == "OK" for o in outcomes) else "PARTIAL"
        A.at[i, "captured"] = bool(caps)
        A.at[i, "first_capture_utc"] = min(caps) if caps else pd.NaT
        A.at[i, "url_forms_checked"] = "code;slug;detail"
    A.to_parquet(INTERIM / "archive_checks.parquet", index=False)
    b = A.loc[idx]
    print(b["captured"].mean(), (pd.to_datetime(b["first_capture_utc"], utc=True) <= pd.to_datetime(b["t_utc"], utc=True)).mean())


def text_of(html_bytes: bytes) -> str:
    h = html_bytes.decode("utf-8", "replace")
    m = re.search(r'<div[^>]+id="article"[^>]*>(.*?)<div[^>]+id="lastUpdate"', h, re.S) or re.search(
        r"<main[^>]*>(.*?)</main>", h, re.S)
    body = m.group(1) if m else h
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", body))


def refetch() -> None:
    rng = np.random.default_rng(SEED + 1)
    rows = []
    # Binance: compare with the first detail fetch
    B = pd.read_parquet(INTERIM / "binance_detail.parquet")
    B = B[B["outcome"] == "OK"]
    for _, r in pick(B.sort_values("code"), 60, rng).iterrows():
        x = get("https://www.binance.com/bapi/composite/v1/public/cms/article/detail/query", {"articleCode": r["code"]},
                purpose="refetch:binance", lookup=r["code"])
        d = (json.loads(x.content).get("data") or {}) if x.outcome == "OK" else {}
        from h20_0_collect_binance import body_text
        rows.append({"source_id": "S_BINANCE_CMS", "key": r["code"], "outcome": x.outcome,
                     "hash_1": content_hash(r["title_detail"] or "", r["body_text"] or ""),
                     "hash_2": content_hash(d.get("title") or "", body_text(d.get("body") or "")) if d else None,
                     "version_1": r["version"], "version_2": d.get("version")})
    # Fed and SEC press pages: two fetches now, main-text hash
    for name, f in (("S_FED_PRESS", "fed_feed"), ("S_SEC_PRESS", "sec_listing")):
        D = pd.read_parquet(INTERIM / f"{f}.parquet")
        W = pd.read_parquet(INTERIM / f"{f.split('_')[0]}_w7.parquet")
        D = D[D["source_document_key"].isin(W["source_document_key"])].drop_duplicates("source_document_key")
        for _, r in pick(D.sort_values("source_document_key"), 30, rng).iterrows():
            a = get(r["url"], purpose=f"refetch:{name}", lookup=r["url"])
            b = get(r["url"], purpose=f"refetch:{name}", lookup=r["url"])
            rows.append({"source_id": name, "key": r["source_document_key"], "outcome": a.outcome if a.outcome != "OK" else b.outcome,
                         "hash_1": content_hash(text_of(a.content)) if a.outcome == "OK" else None,
                         "hash_2": content_hash(text_of(b.content)) if b.outcome == "OK" else None})
    # Federal Register: document JSON twice
    F = pd.read_parquet(INTERIM / "fr_windows.parquet")
    F = F[F["fetch_outcome"] == "OK"].drop_duplicates("source_document_key")
    for _, r in pick(F.sort_values("source_document_key"), 30, rng).iterrows():
        u = f"https://www.federalregister.gov/api/v1/documents/{r['source_document_key']}.json"
        hs = []
        for _ in range(2):
            x = get(u, {"fields[]": ["title", "abstract", "publication_date", "document_number"]},
                    purpose="refetch:fr", lookup=r["source_document_key"])
            hs.append(content_hash(json.dumps(json.loads(x.content), sort_keys=True)) if x.outcome == "OK" else None)
        rows.append({"source_id": "S_FEDREG", "key": r["source_document_key"], "outcome": "OK" if all(hs) else "FAIL",
                     "hash_1": hs[0], "hash_2": hs[1]})
    # Wikipedia: the revision current at t, by oldid, against the sha1 recorded at first fetch
    P = pd.read_parquet(INTERIM / "wiki_portal.parquet").dropna(subset=["revid_at_t"])
    for _, r in pick(P.sort_values(["sample_id", "day"]), 30, rng).iterrows():
        x = get("https://en.wikipedia.org/w/api.php", {"action": "query", "prop": "revisions", "revids": int(r["revid_at_t"]),
                "rvprop": "sha1", "format": "json", "formatversion": 2}, purpose="refetch:wiki", lookup=str(int(r["revid_at_t"])))
        sha = json.loads(x.content)["query"]["pages"][0]["revisions"][0]["sha1"] if x.outcome == "OK" else None
        rows.append({"source_id": "S_WIKI_PORTAL", "key": str(int(r["revid_at_t"])), "outcome": x.outcome,
                     "hash_1": r["sha1_at_t"], "hash_2": sha})
    # GDELT: re-download slices and compare raw bytes
    for p in sorted((RAW / "gdelt").glob("*.gkg.csv.zip_*"))[:6]:
        name, sha = p.name.rsplit("_", 1)
        x = get(f"http://data.gdeltproject.org/gdeltv2/{name}", purpose="refetch:gdelt", lookup=name)
        rows.append({"source_id": "S_GDELT_GKG", "key": name, "outcome": x.outcome, "hash_1": sha, "hash_2": x.sha256[:12]})
    # ALFRED: vintages are fixed by construction; re-download a few
    for p in sorted((RAW / "alfred").glob("CPIAUCSL_20*.csv"))[:8]:
        s, vint, sha = p.stem.split("_")
        x = get("https://alfred.stlouisfed.org/graph/alfredgraph.csv", {"id": s, "vintage_date": vint},
                purpose="refetch:alfred", lookup=vint)
        rows.append({"source_id": "S_ALFRED", "key": f"{s}@{vint}", "outcome": x.outcome, "hash_1": sha, "hash_2": x.sha256[:12]})
    D = pd.DataFrame(rows)
    D["stable"] = (D["outcome"] == "OK") & (D["hash_1"] == D["hash_2"])
    D.to_parquet(INTERIM / "refetch_checks.parquet", index=False)
    print(D.groupby("source_id").agg(n=("key", "size"), ok=("outcome", lambda s: (s == "OK").mean()), stable=("stable", "mean")))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True)
    a = ap.parse_args()
    {"archive": archive, "refetch": refetch, "binance_recheck": binance_recheck}[a.part]()
