"""H20.1 — collect the C1-C3 substrate for the frozen evaluation sample (plan section 5).

  fed     parse the H20.0 raw Fed feed bytes (no new request)
  fr      Federal Register, every document by publication month (no term query), months touching W30
  sec     SEC monthly press-release listings for months touching W30 (H20.0 raw pages reused)
  cftc    parse the CFTC listing pages received in H20.0 (no new request; plan section 5)
  alfred  ALFRED vintages of CPIAUCSL, UNRATE, DFF at asof(t) and asof(t - 7d)
  wiki    Portal:Current events day pages D7(t), revision current at t, every item line kept
  gdelt   GKG slice files S7(t), English + translingual; file stats, crypto records, schema widths

Every request goes through h20_common.get (logged, guarded, paced). Raw bytes are write-once; a raw
file already on disk is parsed, not re-requested. Output: data/interim/h20_1/*.parquet.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_1_collect.py" --only fed,fr,sec,cftc,alfred,wiki,gdelt
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import json
import re
import zipfile
from collections import Counter
from datetime import UTC, date, datetime, timedelta

import pandas as pd

import h20_1_rep as rep
from h20_common import CA, INTERIM, RAW, get, iso, save_raw, sha256_bytes

OUT = INTERIM / "h20_1"
SAMPLE = CA / "H20_1_SAMPLE_FREEZE.json"
csv.field_size_limit(2**31 - 1)


def stamps() -> list[tuple[str, datetime]]:
    j = json.loads(SAMPLE.read_text(encoding="utf-8"))
    return [(s["sample_id"], datetime.fromisoformat(s["t_utc"].replace("Z", "+00:00"))) for s in j["sample"]]


def months_touching(lo: datetime, hi: datetime) -> list[tuple[int, int]]:
    out, d = [], date(lo.year, lo.month, 1)
    while d <= hi.date():
        out.append((d.year, d.month))
        d = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return out


def need_months(pad_days: int = 1) -> list[tuple[int, int]]:
    ms = set()
    for _, t in stamps():
        lo = (t - rep.W30 - timedelta(days=pad_days)).astimezone(rep.ET)
        ms.update(months_touching(lo, t.astimezone(rep.ET)))
    return sorted(ms)


def cached(source: str, prefix: str):
    hits = sorted((RAW / source).glob(prefix + "*"))
    return hits[0] if hits else None


# ---------------------------------------------------------------- Fed (H20.0 raw bytes)
def fed() -> None:
    files = sorted((RAW / "fed").glob("ne-press_*.json"))
    assert len(files) == 1, files
    raw = files[0].read_bytes()
    rows = []
    for x in json.loads(raw.decode("utf-8-sig")):
        if "d" not in x:
            continue
        has_time = " " in x["d"].strip()
        if has_time:
            local = datetime.strptime(x["d"], "%m/%d/%Y %I:%M:%S %p").replace(tzinfo=rep.ET)
            avail, tq = local.astimezone(UTC), "T1_MINUTE_OR_HOUR"
        else:
            avail, tq = rep.day_end_et(datetime.strptime(x["d"], "%m/%d/%Y").date()), "T2_DAY_ONLY"
        rows.append({"source_id": "S_FED_PRESS", "source_document_key": x["l"], "title": html.unescape(x["t"]),
                     "doc_type": x.get("pt"), "raw_date": x["d"], "public_availability_time": avail,
                     "timestamp_quality": tq, "url": "https://www.federalreserve.gov" + x["l"]})
    D = pd.DataFrame(rows)
    D["raw_file"] = files[0].name
    D["raw_sha256"] = sha256_bytes(raw)
    D.to_parquet(OUT / "fed.parquet", index=False)
    print("fed items", len(D), D["public_availability_time"].min(), D["public_availability_time"].max())


# ---------------------------------------------------------------- Federal Register by month
FR_FIELDS = ["document_number", "publication_date", "type", "title", "abstract", "agencies", "html_url"]


def fr() -> None:
    docs, status = [], []
    for y, m in need_months():
        lo = date(y, m, 1)
        hi = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
        page, ok, j = 1, True, {}
        while True:
            name = f"h20_1_{y}_{m:02d}_p{page}_"
            c = cached("federal_register", name)
            if c is not None:
                content = c.read_bytes()
            else:
                p = {"conditions[publication_date][gte]": lo.isoformat(),
                     "conditions[publication_date][lte]": hi.isoformat(),
                     "per_page": 1000, "page": page, "order": "oldest", "fields[]": FR_FIELDS}
                r = get("https://www.federalregister.gov/api/v1/documents.json", p, purpose="h20_1:fr_month")
                if r.outcome != "OK":
                    ok = False
                    status.append({"month": f"{y}-{m:02d}", "page": page, "outcome": r.outcome})
                    break
                save_raw("federal_register", f"{name}{r.sha256[:12]}.json", r.content)
                content = r.content
            j = json.loads(content)
            for x in j.get("results") or []:
                d = date.fromisoformat(x["publication_date"])
                docs.append({"source_id": "S_FEDREG", "source_document_key": x["document_number"],
                             "publication_date": d.isoformat(), "doc_type": x.get("type"), "title": x.get("title") or "",
                             "abstract": x.get("abstract") or "",
                             "agencies": ";".join(sorted({(a.get("name") or a.get("raw_name") or "") for a in x.get("agencies") or []})),
                             "public_availability_time": rep.day_end_et(d), "timestamp_quality": "T2_DAY_ONLY",
                             "url": x.get("html_url"), "month": f"{y}-{m:02d}"})
            total_pages = j.get("total_pages") or 1
            if page >= total_pages:
                break
            page += 1
        status.append({"month": f"{y}-{m:02d}", "page": page, "outcome": "OK" if ok else "INCOMPLETE",
                       "count_reported": j.get("count") if ok else None})
        print("fr", y, m, ok, flush=True)
    D = pd.DataFrame(docs).drop_duplicates("source_document_key")
    D.to_parquet(OUT / "fr.parquet", index=False)
    S = pd.DataFrame(status)
    S.to_parquet(OUT / "fr_status.parquet", index=False)
    print("fr docs", len(D), "months", S["month"].nunique(), "not OK", int((S["outcome"] != "OK").sum()))


# ---------------------------------------------------------------- SEC monthly listings
SEC_ITEM = re.compile(
    r'<time[^>]*datetime="([^"]+)"[^>]*>.*?href="(/newsroom/press-releases/[^"#?]+)"[^>]*>(.*?)</a>', re.S
)


def sec() -> None:
    rows, status = [], []
    for y, m in need_months():
        seen, page, outcome = set(), 0, "INCOMPLETE_PAGE_CAP"
        while page < 10:
            c = cached("sec", f"list_{y}_{m:02d}_p{page}_")
            if c is not None:
                h = c.read_bytes().decode("utf-8", "replace")
            else:
                p = {"year": str(y), "month": str(m)} | ({"page": str(page)} if page else {})
                r = get("https://www.sec.gov/newsroom/press-releases", p, purpose="h20_1:sec_listing")
                if r.outcome != "OK":
                    outcome = r.outcome
                    break
                save_raw("sec", f"list_{y}_{m:02d}_p{page}_{r.sha256[:12]}.html", r.content)
                h = r.content.decode("utf-8", "replace")
            new = 0
            for ts, href, title in SEC_ITEM.findall(h):
                if href in seen:
                    continue
                seen.add(href)
                new += 1
                st = pd.Timestamp(ts)
                st = st.tz_convert("UTC") if st.tzinfo else st.tz_localize("UTC")
                rows.append({"source_id": "S_SEC_PRESS", "source_document_key": href.rsplit("/", 1)[-1],
                             "title": html.unescape(re.sub(r"<[^>]+>", "", title)).strip(),
                             "public_availability_time": st.to_pydatetime(), "timestamp_quality": "T0_EXACT",
                             "url": "https://www.sec.gov" + href, "listing": f"{y}-{m:02d}"})
            if new == 0:
                outcome = "OK"
                break
            page += 1
        status.append({"month": f"{y}-{m:02d}", "pages": page, "outcome": outcome, "items": len(seen)})
        print("sec", y, m, outcome, len(seen), flush=True)
    D = pd.DataFrame(rows).drop_duplicates("source_document_key", keep="first")
    D.to_parquet(OUT / "sec.parquet", index=False)
    pd.DataFrame(status).to_parquet(OUT / "sec_status.parquet", index=False)
    print("sec docs", len(D))


# ---------------------------------------------------------------- CFTC (H20.0 pages only)
CFTC_ROW = re.compile(
    r'<time datetime="([^"]+)">(\d{2}/\d{2}/\d{4})</time>.*?href="(/PressRoom/PressReleases/(\d+-\d+))"[^>]*>(.*?)</a>', re.S
)


def cftc() -> None:
    rows = []
    for p in sorted((RAW / "cftc").glob("list_*.html")):
        h = p.read_bytes().decode("utf-8", "replace")
        for ts, _ds, href, key, title in CFTC_ROW.findall(h):
            rows.append({"source_id": "S_CFTC_PRESS", "source_document_key": key,
                         "title": html.unescape(re.sub(r"<[^>]+>", "", title)).strip(),
                         "public_availability_time": pd.Timestamp(ts).tz_convert("UTC").to_pydatetime(),
                         "timestamp_quality": "T0_EXACT", "url": "https://www.cftc.gov" + href, "raw_file": p.name})
    D = pd.DataFrame(rows).drop_duplicates("source_document_key")
    D.to_parquet(OUT / "cftc.parquet", index=False)
    print("cftc docs", len(D), D["public_availability_time"].min(), D["public_availability_time"].max())


# ---------------------------------------------------------------- ALFRED
def alfred() -> None:
    rows = []
    vints = sorted({rep.alfred_asof(x) for _, t in stamps() for x in (t, t - rep.W7)})
    for vd in vints:
        for s in rep.ALFRED_SERIES:
            v = vd.isoformat()
            c = cached("alfred", f"{s}_{v}_")
            if c is not None:
                content, outcome = c.read_bytes(), "OK"
            else:
                r = get("https://alfred.stlouisfed.org/graph/alfredgraph.csv", {"id": s, "vintage_date": v},
                        purpose="h20_1:alfred_vintage")
                content, outcome = r.content, r.outcome
                if outcome == "OK":
                    c = save_raw("alfred", f"{s}_{v}_{r.sha256[:12]}.csv", content)
            row = {"series": s, "vintage_date": v, "fetch_outcome": outcome}
            if outcome == "OK":
                d = pd.read_csv(io.BytesIO(content))
                d.columns = ["obs_date", "value"]
                d["value"] = pd.to_numeric(d["value"], errors="coerce")
                d = d.dropna().sort_values("obs_date")
                last = d.iloc[-1]
                row |= {"raw_file": c.name, "raw_sha256": sha256_bytes(content), "n_obs": len(d),
                        "last_obs_date": last["obs_date"], "last_value": float(last["value"])}
                if s == "CPIAUCSL":
                    prev_date = (pd.Timestamp(last["obs_date"]) - pd.DateOffset(months=12)).date().isoformat()
                    prev = d[d["obs_date"] == prev_date]
                    row |= {"yoy_base_date": prev_date, "yoy_base_value": float(prev["value"].iloc[0]) if len(prev) else None}
            rows.append(row)
        print("alfred", vd, flush=True)
    pd.DataFrame(rows).to_parquet(OUT / "alfred.parquet", index=False)


# ---------------------------------------------------------------- Wikipedia portal
API = "https://en.wikipedia.org/w/api.php"


def wiki_rev_at(title: str, t: datetime) -> tuple[str, dict | None]:
    p = {"action": "query", "format": "json", "formatversion": 2, "prop": "revisions", "titles": title,
         "rvlimit": 1, "rvdir": "older", "rvstart": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
         "rvprop": "ids|timestamp|size|sha1|content", "rvslots": "main"}
    r = get(API, p, purpose="h20_1:wiki_portal_at_t")
    if r.outcome != "OK":
        return r.outcome, None
    pages = (json.loads(r.content).get("query") or {}).get("pages") or []
    if not pages or pages[0].get("missing") or not pages[0].get("revisions"):
        return "PAGE_ABSENT_AT_T", None
    rv = pages[0]["revisions"][0]
    rv["content"] = rv.get("slots", {}).get("main", {}).get("content", "")
    return "OK", rv


def wiki() -> None:
    pages, items = [], []
    for sid, t in stamps():
        for d in rep.wiki_days(t):
            title = f"Portal:Current events/{d.year} {d.strftime('%B')} {d.day}"
            outcome, rv = wiki_rev_at(title, t)
            row = {"sample_id": sid, "t_utc": t, "day": d.isoformat(), "title": title, "outcome": outcome}
            if rv:
                save_raw("wiki", f"portal_{rv['revid']}.wikitext", rv["content"].encode("utf-8"))
                lines = rep.wiki_items(rv["content"])
                row |= {"revid": rv["revid"], "rev_utc": rv["timestamp"], "sha1": rv["sha1"], "size": rv["size"],
                        "n_lines": len(rv["content"].splitlines()), "n_items": len(lines)}
                for i, ln in enumerate(lines):
                    items.append({"sample_id": sid, "day": d.isoformat(), "revid": rv["revid"], "rev_utc": rv["timestamp"],
                                  "item_idx": i, "text": ln})
            pages.append(row)
        print("wiki", sid, flush=True)
    pd.DataFrame(pages).to_parquet(OUT / "wiki_pages.parquet", index=False)
    pd.DataFrame(items).to_parquet(OUT / "wiki_items.parquet", index=False)


# ---------------------------------------------------------------- GDELT
LANG = re.compile(r"srclc:([a-z]{2,3})")


def gdelt() -> None:
    files, crypto = [], []
    done: dict[str, dict] = {}
    for sid, t in stamps():
        for k, sl in enumerate(rep.gdelt_slices(t)):
            stamp = sl.strftime("%Y%m%d%H%M%S")
            for feed, suffix in (("en", "gkg.csv.zip"), ("translingual", "translation.gkg.csv.zip")):
                name = f"{stamp}.{suffix}"
                base = {"sample_id": sid, "t_utc": t, "k": k, "slice_utc": sl, "feed": feed, "file": name}
                if name in done:
                    files.append(base | done[name])
                    continue
                c = cached("gdelt", f"{name}_")
                if c is not None:
                    content, outcome = c.read_bytes(), "OK"
                else:
                    r = get(f"http://data.gdeltproject.org/gdeltv2/{name}", purpose="h20_1:gdelt_slice")
                    content, outcome = r.content, r.outcome
                    if outcome == "OK":
                        c = save_raw("gdelt", f"{name}_{r.sha256[:12]}", content)
                stats = {"outcome": outcome}
                if outcome == "OK":
                    try:
                        z = zipfile.ZipFile(io.BytesIO(content))
                        text = z.read(z.namelist()[0]).decode("utf-8", "replace")
                    except (zipfile.BadZipFile, KeyError):
                        stats = {"outcome": "BAD_ZIP"}
                        done[name] = stats
                        files.append(base | stats)
                        continue
                    n, n_crypto, widths, langs = 0, 0, Counter(), Counter()
                    for f in csv.reader(io.StringIO(text), delimiter="\t", quoting=csv.QUOTE_NONE):
                        widths[len(f)] += 1
                        if len(f) < 24:
                            continue
                        n += 1
                        lm = LANG.search(f[25]) if len(f) > 25 else None
                        lang = lm.group(1) if lm else ("en" if feed == "en" else "und")
                        langs[lang] += 1
                        blob = " ".join((f[7] + ";" + f[8], f[13], f[23], f[4]))
                        if rep.K_GDELT_CRYPTO.search(blob):
                            n_crypto += 1
                            tone = f[15].split(",")[0] if f[15] else ""
                            m = rep.K_GDELT_CRYPTO.search(blob)
                            crypto.append({"file": name, "feed": feed, "gkg_id": f[0], "source_name": f[3], "url": f[4],
                                           "lang": lang, "tone": float(tone) if tone else None,
                                           "match": m.group(0), "themes": (f[7] + ";" + f[8])[:1500],
                                           "orgs": f[13][:1000], "allnames": f[23][:1500]})
                    stats = {"outcome": "OK", "raw_file": c.name, "raw_sha256": sha256_bytes(content), "records": n,
                             "crypto_records": n_crypto, "rows_by_width": json.dumps(dict(sorted(widths.items()))),
                             "short_rows": sum(v for w, v in widths.items() if w < 24),
                             "langs_top": json.dumps(dict(langs.most_common(5)))}
                done[name] = stats
                files.append(base | stats)
        print("gdelt", sid, iso(t), flush=True)
    pd.DataFrame(files).to_parquet(OUT / "gdelt_files.parquet", index=False)
    pd.DataFrame(crypto).drop_duplicates(["file", "gkg_id"]).to_parquet(OUT / "gdelt_crypto_records.parquet", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="fed,fr,sec,cftc,alfred,wiki,gdelt")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for part in a.only.split(","):
        {"fed": fed, "fr": fr, "sec": sec, "cftc": cftc, "alfred": alfred, "wiki": wiki, "gdelt": gdelt}[part]()
    print("done", iso(datetime.now(tz=UTC)))
