"""H20.0 — Wikipedia as a versioned source (V2): the Current-Events portal (C1/C2/C3) and asset articles (C5).

  portal  for each day page in W7(t): the revision current at t, the first revision, today's
          revision, and the number of edits made after t. Item counts at t vs today measure how much
          of the page was written after the fact.
  assets  for each asset-time unit whose name was resolved point-in-time (h20_0_entities.py): does an
          article exist, did it exist at t, is its text at t about a crypto asset, edits in W30.

Content is CC BY-SA 4.0 and stays under data/raw/wiki.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_collect_wiki.py" --part portal|assets
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta

import pandas as pd

from h20_common import INTERIM, get, load_freeze, save_raw

API = "https://en.wikipedia.org/w/api.php"
CRYPTO = re.compile(r"bitcoin|cryptocurrenc|crypto|blockchain|binance|stablecoin|\btoken", re.I)


def q(params: dict, purpose: str, lookup: str | None = None) -> dict:
    p = {"action": "query", "format": "json", "formatversion": 2} | params
    r = get(API, p, purpose=purpose, lookup=lookup)
    if r.outcome != "OK":
        return {"_outcome": r.outcome}
    return json.loads(r.content)


def rev(title: str, *, start: datetime | None = None, rvdir: str = "older", content: bool = False,
        purpose: str, lookup: str | None = None) -> dict | None:
    p = {"prop": "revisions", "titles": title, "rvlimit": 1, "rvdir": rvdir,
         "rvprop": "ids|timestamp|size|sha1" + ("|content" if content else "")}
    if content:
        p["rvslots"] = "main"
    if start is not None:
        p["rvstart"] = start.strftime("%Y-%m-%dT%H:%M:%SZ")
    j = q(p, purpose, lookup)
    pages = (j.get("query") or {}).get("pages") or []
    if not pages or pages[0].get("missing") or not pages[0].get("revisions"):
        return None
    r = pages[0]["revisions"][0]
    if content:
        r["content"] = r.get("slots", {}).get("main", {}).get("content", "")
        r.pop("slots", None)
    return r


def count_after(title: str, t: datetime, purpose: str, lookup: str | None = None) -> int:
    p = {"prop": "revisions", "titles": title, "rvlimit": 500, "rvdir": "newer", "rvprop": "ids",
         "rvstart": t.strftime("%Y-%m-%dT%H:%M:%SZ")}
    j = q(p, purpose, lookup)
    pages = (j.get("query") or {}).get("pages") or []
    return len(pages[0].get("revisions") or []) if pages else 0


def count_between(title: str, a: datetime, b: datetime, purpose: str, lookup: str | None = None) -> int:
    p = {"prop": "revisions", "titles": title, "rvlimit": 500, "rvdir": "newer", "rvprop": "ids",
         "rvstart": a.strftime("%Y-%m-%dT%H:%M:%SZ"), "rvend": b.strftime("%Y-%m-%dT%H:%M:%SZ")}
    j = q(p, purpose, lookup)
    pages = (j.get("query") or {}).get("pages") or []
    return len(pages[0].get("revisions") or []) if pages else 0


def items(text: str) -> tuple[int, int]:
    lines = [ln for ln in (text or "").splitlines() if ln.startswith("*")]
    return len(lines), sum(bool(CRYPTO.search(ln)) for ln in lines)


def portal() -> None:
    rows = []
    for s in load_freeze()["sample"]:
        t = datetime.fromisoformat(s["t_utc"].replace("Z", "+00:00"))
        d = (t - timedelta(days=7)).date()
        while d <= t.date():
            title = f"Portal:Current events/{d.year} {d.strftime('%B')} {d.day}"
            at_t = rev(title, start=t, content=True, purpose="wiki:portal_at_t")
            first = rev(title, rvdir="newer", purpose="wiki:portal_first")
            now = rev(title, content=True, purpose="wiki:portal_now")
            row = {"sample_id": s["sample_id"], "day": d.isoformat(), "title": title,
                   "exists_now": now is not None, "exists_at_t": at_t is not None,
                   "first_rev_utc": first["timestamp"] if first else None}
            if at_t:
                save_raw("wiki", f"portal_{at_t['revid']}.wikitext", at_t["content"].encode("utf-8"))
                n, c = items(at_t["content"])
                row |= {"revid_at_t": at_t["revid"], "rev_at_t_utc": at_t["timestamp"], "size_at_t": at_t["size"],
                        "sha1_at_t": at_t["sha1"], "items_at_t": n, "crypto_items_at_t": c}
            if now:
                save_raw("wiki", f"portal_{now['revid']}.wikitext", now["content"].encode("utf-8"))
                n, c = items(now["content"])
                row |= {"revid_now": now["revid"], "rev_now_utc": now["timestamp"], "size_now": now["size"],
                        "sha1_now": now["sha1"], "items_now": n, "crypto_items_now": c,
                        "edits_after_t": count_after(title, t, "wiki:portal_after")}
            rows.append(row)
            d += timedelta(days=1)
        print(s["sample_id"], flush=True)
    D = pd.DataFrame(rows)
    D.to_parquet(INTERIM / "wiki_portal.parquet", index=False)
    print(D[["exists_at_t", "exists_now"]].mean(), D[["items_at_t", "items_now"]].sum())


def assets() -> None:
    E = pd.read_parquet(INTERIM / "entity_resolution.parquet")
    rows = []
    for _, e in E.iterrows():
        t = pd.Timestamp(e["t_utc"]).to_pydatetime()
        row = {"sample_id": e["sample_id"], "asset_ticker": e["asset_ticker"], "pit_name": e["pit_name"]}
        if e["name_status"] != "RESOLVED":
            rows.append(row | {"wiki_status": "NO_PIT_NAME"})
            continue
        name = e["pit_name"]
        found = None
        for cand in (f"{name} (cryptocurrency)", name, f"{name} (blockchain)", f"{name} (token)"):
            j = q({"titles": cand, "redirects": 1, "prop": "pageprops|info"}, "wiki:asset_lookup", lookup=cand)
            pages = (j.get("query") or {}).get("pages") or []
            if pages and not pages[0].get("missing"):
                found = (cand, pages[0])
                break
        if not found:
            rows.append(row | {"wiki_status": "NO_ARTICLE"})
            continue
        cand, pg = found
        title = pg["title"]
        disamb = "disambiguation" in (pg.get("pageprops") or {})
        first = rev(title, rvdir="newer", purpose="wiki:asset_first", lookup=title)
        at_t = rev(title, start=t, content=True, purpose="wiki:asset_at_t", lookup=title)
        row |= {"query_title": cand, "resolved_title": title, "via_redirect": title != cand, "disambiguation": disamb,
                "first_rev_utc": first["timestamp"] if first else None, "exists_at_t": at_t is not None}
        if at_t:
            save_raw("wiki", f"asset_{at_t['revid']}.wikitext", at_t["content"].encode("utf-8"))
            txt = at_t["content"]
            row |= {"revid_at_t": at_t["revid"], "rev_at_t_utc": at_t["timestamp"],
                    "crypto_text_at_t": bool(CRYPTO.search(txt)),
                    "ticker_in_text_at_t": bool(re.search(rf"\b{re.escape(e['asset_ticker'])}\b", txt)),
                    "edits_w30": count_between(title, t - timedelta(days=30), t, "wiki:asset_w30", lookup=title)}
        if disamb:
            status = "AMBIGUOUS_DISAMBIGUATION"
        elif not at_t:
            status = "ARTICLE_CREATED_AFTER_T"
        elif row.get("crypto_text_at_t"):
            status = "PIT_ARTICLE"
        else:
            status = "AMBIGUOUS_NOT_CRYPTO"
        rows.append(row | {"wiki_status": status})
        print(e["sample_id"], e["asset_ticker"], status, flush=True)
    pd.DataFrame(rows).to_parquet(INTERIM / "wiki_assets.parquet", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True)
    a = ap.parse_args()
    {"portal": portal, "assets": assets}[a.part]()
