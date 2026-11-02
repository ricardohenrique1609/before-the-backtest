"""H20.0 step 8-9 — unified document table, every measured quantity of plan section 5, and the gate.

Reads only H20's own collected tables (data/interim) and the frozen sample. No outcome table, no
price, no return. The sealed survivorship stage runs separately, after this script has hashed its
inputs and outputs (manifests/H20_0_PRE_SEAL_HASHES.json).

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_audit.py"
"""

from __future__ import annotations

import json
import re
from datetime import timedelta

import numpy as np
import pandas as pd

from h20_common import CA, DERIVED, to_lf, EVIDENCE, INTERIM, MANIFESTS, content_hash, iso, load_freeze, now_utc, read_request_logs, sha256_file

F = load_freeze()
T = {s["sample_id"]: pd.Timestamp(s["t_utc"]) for s in F["sample"]}
YEAR = {k: v.year for k, v in T.items()}
EARLY, LATE = {2018, 2019, 2020}, {2024, 2025, 2026}
W7, W30 = timedelta(days=7), timedelta(days=30)

# licence classes (registry); G6 asks whether derived-feature research use is permitted
LICENCE = {
    "S_BINANCE_CMS": ("PROPRIETARY_TOS", False, True),
    "S_FED_PRESS": ("US_GOV_PUBLIC_DOMAIN", True, True),
    "S_FEDREG": ("US_GOV_PUBLIC_DOMAIN", True, True),
    "S_SEC_PRESS": ("US_GOV_PUBLIC_DOMAIN", True, True),
    "S_CFTC_PRESS": ("US_GOV_PUBLIC_DOMAIN", True, True),
    "S_ALFRED": ("FRED_TERMS_ATTRIBUTION", False, True),
    "S_GDELT_GKG": ("GDELT_OPEN_CITATION_METADATA_ONLY", True, True),
    "S_WIKI_PORTAL": ("CC_BY_SA_4_0", True, True),
    "S_WIKI_ASSET": ("CC_BY_SA_4_0", True, True),
}
LAYER_SOURCES = {
    "C1": ["S_FED_PRESS", "S_ALFRED", "S_WIKI_PORTAL"],
    "C2": ["S_FEDREG", "S_SEC_PRESS", "S_CFTC_PRESS", "S_FED_PRESS", "S_WIKI_PORTAL"],
    "C3": ["S_GDELT_GKG", "S_WIKI_PORTAL"],
    "C4": ["S_BINANCE_CMS"],
    "C5": ["S_BINANCE_CMS", "S_GDELT_GKG", "S_WIKI_ASSET"],
}


def rd(name: str) -> pd.DataFrame:
    p = INTERIM / f"{name}.parquet"
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


def utc(s) -> pd.Series:
    return pd.to_datetime(s, utc=True)


def window_of(ts: pd.Series, width=W7) -> pd.Series:
    """sample_id whose (t - width, t] contains ts (windows of different quarters never overlap)."""
    out = pd.Series(None, index=ts.index, dtype=object)
    for sid, t in T.items():
        out[(ts > t - width) & (ts <= t)] = sid
    return out


# ------------------------------------------------------------------ archive subsample
A = rd("archive_checks")
if len(A):
    A["t_utc"] = utc(A["t_utc"])
    A["first_capture_utc"] = utc(A.get("first_capture_utc"))
    A["alt_first_capture_utc"] = utc(A.get("alt_first_capture_utc")) if "alt_first_capture_utc" in A else pd.NaT
    A["publication_time"] = utc(A["publication_time"])
    A["cap_any"] = A["first_capture_utc"].notna() | A["alt_first_capture_utc"].notna()
    first = A[["first_capture_utc", "alt_first_capture_utc"]].min(axis=1)
    A["stamp_after_capture"] = first < A["publication_time"] - pd.Timedelta(minutes=1)
    # a capture that predates a publisher's own stamp shows a different document at a reused URL (one Fed
    # release: capture 1998, release 2022); it cannot certify content as of t, so it is not V1. GDELT's
    # clock is first observation, so an earlier capture there is the article itself.
    A["url_reuse_suspect"] = A["stamp_after_capture"] & (A["source_id"] != "S_GDELT_GKG")
    A["cap_le_t"] = ((A["first_capture_utc"] <= A["t_utc"]) | (A["alt_first_capture_utc"] <= A["t_utc"])) & ~A["url_reuse_suspect"]
    A["capture_lag_hours"] = (first - A["publication_time"]).dt.total_seconds() / 3600
    A["year"] = A["sample_id"].map(YEAR)
    ARCH = {(r.source_id, str(r.source_document_key)): r for r in A.itertuples()}
else:
    ARCH = {}


def arch_v1(src: str, key: str) -> bool | None:
    r = ARCH.get((src, str(key)))
    return None if r is None else bool(r.cap_le_t)


# ------------------------------------------------------------------ unified documents
docs: list[dict] = []


def add(**k):
    docs.append(k)


B = rd("binance_catalog")
BD = rd("binance_detail")
B["published_utc"] = utc(B["published_utc"])
B["sample_id"] = window_of(B["published_utc"])
bdet = BD.set_index("code") if len(BD) else pd.DataFrame()
for r in B[B["sample_id"].notna()].itertuples():
    d = bdet.loc[r.code] if len(bdet) and r.code in bdet.index else None
    t = T[r.sample_id]
    av = arch_v1("S_BINANCE_CMS", r.code)
    edited = False
    if d is not None and d["outcome"] == "OK":
        v = pd.to_numeric(d.get("version"), errors="coerce")
        lu = pd.to_numeric(d.get("last_update_ms"), errors="coerce")
        edited = bool((v == v and v > 1) or (lu == lu and lu > 0) or re.search(r"\(?updated?\b", str(r.title), re.I))
    if av:
        vq = "V1_ARCHIVED_AT_T"
    elif d is None or d["outcome"] != "OK":
        vq = "V5_UNRETRIEVABLE" if d is not None and d["outcome"] in ("NO_DATA", "HTTP_ERROR") else "V3_CURRENT_ONLY_NO_EDIT_EVIDENCE"
    else:
        vq = "V4_CURRENT_ONLY_EDITED" if edited else "V3_CURRENT_ONLY_NO_EDIT_EVIDENCE"
    arow = ARCH.get(("S_BINANCE_CMS", r.code))
    sac = bool(arow.stamp_after_capture) if arow is not None and arow.cap_any else False
    add(source_id="S_BINANCE_CMS", source_document_key=r.code, sample_id=r.sample_id, context_layer="C4",
        title=r.title, publication_time=r.published_utc, public_availability_time=r.published_utc,
        timestamp_quality="T0_EXACT", timestamp_flags="STAMP_AFTER_CAPTURE" if sac else "",
        version_quality=vq, language="en", crypto=True,
        detail_outcome=None if d is None else d["outcome"],
        cms_version=None if d is None else d.get("version"), cms_last_update_ms=None if d is None else d.get("last_update_ms"),
        content_hash=None if d is None or d["outcome"] != "OK" else content_hash(d.get("title_detail") or "", d.get("body_text") or ""))

CRYPTO_T = re.compile(r"crypto|digital asset|virtual currenc|bitcoin|stablecoin|blockchain|token|coin offering|binance|\bether\b", re.I)
FED = rd("fed_feed")
FW = rd("fed_w7")
if len(FW):
    FED = FED.merge(FW, on="source_document_key")
    for r in FED.itertuples():
        av = arch_v1("S_FED_PRESS", r.source_document_key)
        add(source_id="S_FED_PRESS", source_document_key=r.source_document_key, sample_id=r.sample_id,
            context_layer="C1" if r.doc_type == "Monetary Policy" else "C2", title=r.title,
            publication_time=r.publication_time, public_availability_time=r.public_availability_time,
            timestamp_quality="T1_MINUTE_OR_HOUR" if r.has_time else "T2_DAY_ONLY",
            timestamp_flags="CONVENTION_TZ" if r.has_time else "DAY_END_CONSERVATIVE",
            version_quality="V1_ARCHIVED_AT_T" if av else "V3_CURRENT_ONLY_NO_EDIT_EVIDENCE", language="en",
            crypto=bool(CRYPTO_T.search(r.title)), jurisdiction="US")

FR = rd("fr_windows")
if len(FR):
    FR = FR[(FR["fetch_outcome"] == "OK") & FR["in_w7"].fillna(False)].drop_duplicates(["sample_id", "source_document_key"])
    for r in FR.itertuples():
        add(source_id="S_FEDREG", source_document_key=r.source_document_key, sample_id=r.sample_id, context_layer="C2",
            title=r.title, publication_time=None, public_availability_time=r.public_availability_time,
            timestamp_quality="T2_DAY_ONLY", timestamp_flags="DAY_END_CONSERVATIVE", version_quality="V0_IMMUTABLE",
            language="en", crypto=True, jurisdiction="US")

for name, src in (("sec", "S_SEC_PRESS"), ("cftc", "S_CFTC_PRESS")):
    L, LW = rd(f"{name}_listing"), rd(f"{name}_w7")
    if not len(LW):
        continue
    L = L[L["fetch_outcome"] == "OK"].merge(LW, on="source_document_key")
    for r in L.itertuples():
        av = arch_v1(src, r.source_document_key)
        arow = ARCH.get((src, str(r.source_document_key)))
        sac = bool(arow.stamp_after_capture) if arow is not None and arow.cap_any else False
        add(source_id=src, source_document_key=r.source_document_key, sample_id=r.sample_id, context_layer="C2",
            title=r.title, publication_time=r.publication_time, public_availability_time=r.publication_time,
            timestamp_quality="T0_EXACT", timestamp_flags="CMS_STAMP" + (";STAMP_AFTER_CAPTURE" if sac else ""),
            version_quality="V1_ARCHIVED_AT_T" if av else "V3_CURRENT_ONLY_NO_EDIT_EVIDENCE", language="en",
            crypto=bool(CRYPTO_T.search(r.title)), jurisdiction="US")

G = rd("gdelt_records")
GF = rd("gdelt_files")
for r in G.itertuples():
    add(source_id="S_GDELT_GKG", source_document_key=r.gkg_id, sample_id=r.sample_id,
        context_layer="C3" if r.crypto else "GENERAL", title=None, publication_time=None,
        public_availability_time=r.slice_utc, timestamp_quality="T0_EXACT", timestamp_flags="FIRST_OBSERVED_SLICE",
        version_quality="V0_IMMUTABLE", language=r.lang, crypto=bool(r.crypto), feed=r.feed)

P = rd("wiki_portal")
for r in P.itertuples():
    if not r.exists_at_t:
        continue
    add(source_id="S_WIKI_PORTAL", source_document_key=str(int(r.revid_at_t)), sample_id=r.sample_id,
        context_layer="C1C2C3", title=r.title, publication_time=utc(pd.Series([r.rev_at_t_utc]))[0],
        public_availability_time=utc(pd.Series([r.rev_at_t_utc]))[0], timestamp_quality="T0_EXACT",
        timestamp_flags="REVISION_TIMESTAMP", version_quality="V2_VERSIONED", language="en",
        crypto=bool(r.crypto_items_at_t), items=r.items_at_t, crypto_items=r.crypto_items_at_t)

AL = rd("alfred_vintages")
for r in AL[AL["fetch_outcome"] == "OK"].itertuples() if len(AL) else []:
    d = pd.Timestamp(r.vintage_date).tz_localize("America/New_York") + pd.Timedelta(days=1)
    add(source_id="S_ALFRED", source_document_key=f"{r.series}@{r.vintage_date}", sample_id=r.sample_id, context_layer="C1",
        title=r.series, publication_time=None, public_availability_time=d.tz_convert("UTC"),
        timestamp_quality="T2_DAY_ONLY", timestamp_flags="DAY_END_CONSERVATIVE;VINTAGE", version_quality="V0_IMMUTABLE",
        language="en", crypto=False, jurisdiction="US")

WA = rd("wiki_assets")
for r in WA.itertuples() if len(WA) else []:
    if getattr(r, "wiki_status", None) != "PIT_ARTICLE":
        continue
    add(source_id="S_WIKI_ASSET", source_document_key=str(int(r.revid_at_t)), sample_id=r.sample_id, context_layer="C5",
        title=r.resolved_title, publication_time=utc(pd.Series([r.rev_at_t_utc]))[0],
        public_availability_time=utc(pd.Series([r.rev_at_t_utc]))[0], timestamp_quality="T0_EXACT",
        timestamp_flags="REVISION_TIMESTAMP", version_quality="V2_VERSIONED", language="en", crypto=True,
        entity_id=f"asset:{r.asset_ticker}")

D = pd.DataFrame(docs)
D["public_availability_time"] = utc(D["public_availability_time"])
D["t_utc"] = D["sample_id"].map(T)
D["year"] = D["sample_id"].map(YEAR)
D["pit_eligible"] = D["public_availability_time"].notna() & (D["public_availability_time"] <= D["t_utc"]) & ~D[
    "version_quality"].isin(["V4_CURRENT_ONLY_EDITED", "V5_UNRETRIEVABLE"])
D["pit_exclusion_reason"] = np.where(D["public_availability_time"] > D["t_utc"], "AVAILABLE_AFTER_T",
                                     np.where(D["version_quality"].isin(["V4_CURRENT_ONLY_EDITED", "V5_UNRETRIEVABLE"]),
                                              D["version_quality"], ""))
for c, (lc, redis, _) in {k: v for k, v in LICENCE.items()}.items():
    D.loc[D["source_id"] == c, "license_class"] = lc
    D.loc[D["source_id"] == c, "redistribution_allowed"] = redis
D["document_id"] = [content_hash(a, str(b), str(c))[:32] for a, b, c in zip(D["source_id"], D["source_document_key"], D["public_availability_time"])]
DERIVED.mkdir(parents=True, exist_ok=True)
D.to_parquet(DERIVED / "context_documents.parquet", index=False)

# ------------------------------------------------------------------ per (t, source) status: missing vs zero
status = []
harvest = json.loads((INTERIM / "binance_harvest_summary.json").read_text())
bin_complete = all(c.get("status") == "COMPLETE" for c in harvest["catalogs"].values())
gfile = GF.groupby("sample_id")["outcome"].apply(lambda s: (s == "OK").any()) if len(GF) else pd.Series(dtype=bool)
gfile_en = GF[GF["feed"] == "en"].set_index("sample_id")["outcome"].eq("OK") if len(GF) else pd.Series(dtype=bool)
cftc_l = rd("cftc_listing")
cftc_ok_years = set(cftc_l.loc[cftc_l["fetch_outcome"] == "OK", "publication_time"].pipe(utc).dt.year) if len(cftc_l) else set()
cftc_ok = cftc_l[cftc_l["fetch_outcome"] == "OK"] if len(cftc_l) else pd.DataFrame()
cftc_min_pub = utc(cftc_ok["publication_time"]).groupby(cftc_ok["listing"].astype(int)).min().to_dict() if len(cftc_ok) else {}
cftc_blocked_years = set(cftc_l.loc[cftc_l["fetch_outcome"] != "OK", "listing"].astype(int)) if len(cftc_l) else set()
sec_l = rd("sec_listing")
sec_bad = set(sec_l.loc[sec_l["fetch_outcome"] != "OK", "listing"]) if len(sec_l) else set()
fr_bad = set(rd("fr_windows").query("fetch_outcome != 'OK'")["sample_id"]) if len(rd("fr_windows")) else set()
al_ok = AL.groupby("sample_id")["fetch_outcome"].apply(lambda s: (s == "OK").all()) if len(AL) else pd.Series(dtype=bool)
portal_ok = P.groupby("sample_id")["exists_at_t"].any() if len(P) else pd.Series(dtype=bool)
for sid, t in T.items():
    yrs = {(t - W7).year, t.year}
    months = {f"{(t - W7).year}-{(t - W7).month:02d}", f"{t.year}-{t.month:02d}"}
    avail = {
        "S_BINANCE_CMS": bin_complete,
        "S_FED_PRESS": True,
        "S_FEDREG": sid not in fr_bad,
        "S_SEC_PRESS": not (months & sec_bad),
        # newest-first listing: a window is covered only if every year it touches was either walked to
        # the end, or walked past the window start before the 429 block (deviation D2)
        "S_CFTC_PRESS": all(y not in cftc_blocked_years or (y in cftc_min_pub and cftc_min_pub[y] <= t - W7) for y in yrs),
        "S_GDELT_GKG": bool(gfile_en.get(sid, False)),
        "S_WIKI_PORTAL": bool(portal_ok.get(sid, False)),
        "S_ALFRED": bool(al_ok.get(sid, False)),
    }
    for src, ok in avail.items():
        n = int(((D["source_id"] == src) & (D["sample_id"] == sid) & D["pit_eligible"]).sum())
        n_layer = {L: int(((D["source_id"] == src) & (D["sample_id"] == sid) & D["pit_eligible"] & (
            D["context_layer"].str.contains(L[1]) if L != "C3" else D["crypto"])).sum()) for L in ("C1", "C2", "C3", "C4")}
        status.append({"sample_id": sid, "t_utc": iso(t.to_pydatetime()), "year": t.year, "source_id": src, "available": ok,
                       "n_docs_w7": n if ok else None, "status": "MISSING" if not ok else ("ZERO" if n == 0 else "OBSERVED")}
                      | {f"n_{k}": v if ok else None for k, v in n_layer.items()})
S = pd.DataFrame(status)
EVIDENCE.mkdir(exist_ok=True)
S.to_csv(EVIDENCE / "H20_0_SOURCE_TIMESTAMP_STATUS.csv", index=False)

# ------------------------------------------------------------------ C5 asset-specific coverage per asset-time unit
E = rd("entity_resolution")
gd = G[["sample_id", "allnames", "orgs"]] if len(G) else pd.DataFrame()
c5 = []
for e in E.itertuples():
    t = T[e.sample_id]
    tk = e.asset_ticker
    pat = rf"\(\s*{re.escape(tk)}\s*\)|\b{re.escape(tk)}/" if len(tk) <= 2 else rf"(?<![A-Za-z0-9]){re.escape(tk)}(?![A-Za-z0-9])"
    bw = B[(B["published_utc"] > t - W30) & (B["published_utc"] <= t)]
    nb = int(bw["title"].str.contains(pat, regex=True).sum())
    ng = None
    if e.name_status == "RESOLVED" and len(gd):
        g = gd[gd["sample_id"] == e.sample_id]
        rx = re.compile(rf"(?<![A-Za-z0-9]){re.escape(e.pit_name)}(?![A-Za-z0-9])", re.I)
        ng = sum(bool(rx.search(a or "") or rx.search(o or "")) for a, o in zip(g["allnames"], g["orgs"]))
    w = WA[(WA["sample_id"] == e.sample_id) & (WA["asset_ticker"] == tk)] if len(WA) else pd.DataFrame()
    ws = w["wiki_status"].iloc[0] if len(w) else "NO_PIT_NAME"
    we = int(w["edits_w30"].fillna(0).iloc[0]) if len(w) and "edits_w30" in w and ws == "PIT_ARTICLE" else 0
    c5.append({"sample_id": e.sample_id, "year": t.year, "asset_ticker": tk, "liquidity_tercile": e.liquidity_tercile,
               "entity_type": e.entity_type, "asset_age_days": e.asset_age_days, "name_status_v2": e.name_status,
               "name_status_v1": e.v1_name_status, "binance_notices_w30": nb, "gdelt_slice_name_hits": ng,
               "wiki_status": ws, "wiki_edits_w30": we,
               "any_asset_doc_w30": nb > 0 or (ng or 0) > 0 or we > 0, "non_venue_doc_w30": (ng or 0) > 0 or we > 0})
C5 = pd.DataFrame(c5)
C5.to_csv(EVIDENCE / "H20_0_C5_ASSET_COVERAGE.csv", index=False)

# ------------------------------------------------------------------ C4 ticker mentions -> era as of publication
WIN = pd.read_parquet(CA / "data/raw/inherited/symbol_windows_whitelist.parquet")
WIN["first_candle"] = utc(WIN["first_candle"])
known_first = WIN.groupby("base_asset")["first_candle"].min()
bw = B[B["sample_id"].notna()].copy()
c4 = []
LISTING_V = re.compile(r"\b(?:will list|lists|will add|adds|launchpool|launchpad|megadrop|introducing|pre-market)\b", re.I)
for r in bw.itertuples():
    for tk in set(re.findall(r"\(([A-Z0-9]{2,15})\)", r.title)):
        fc = known_first.get(tk)
        if fc is not None and fc <= r.published_utc:
            res = "RESOLVED_EXISTING_ERA"
        elif LISTING_V.search(r.title):
            res = "RESOLVED_NEW_ENTITY_BY_NOTICE"
        elif fc is not None:
            res = "UNRESOLVED_FUTURE_ROUTE_ONLY"
        else:
            res = "UNRESOLVED_NO_SPOT_ROUTE"
        c4.append({"sample_id": r.sample_id, "code": r.code, "ticker": tk, "resolution": res})
C4 = pd.DataFrame(c4)
C4.to_csv(EVIDENCE / "H20_0_C4_TICKER_RESOLUTION.csv", index=False)

# ------------------------------------------------------------------ reproducibility
R = rd("refetch_checks")
rep = R.groupby("source_id").agg(n=("key", "size"), refetch_success=("outcome", lambda s: float((s == "OK").mean())),
                                 hash_stable=("stable", "mean")).reset_index() if len(R) else pd.DataFrame()
if len(R) and "version_1" in R:
    vb = R[R["source_id"] == "S_BINANCE_CMS"]
    rep.loc[rep["source_id"] == "S_BINANCE_CMS", "version_stable"] = float((vb["version_1"].astype(str) == vb["version_2"].astype(str)).mean())
rep.to_csv(EVIDENCE / "H20_0_REPRODUCIBILITY.csv", index=False)
logs, malformed = read_request_logs()
RL = pd.DataFrame(logs)
RL["src"] = RL["purpose"].str.split(":").str[0]
req = RL.groupby(["src", "outcome"]).size().unstack(fill_value=0).reset_index()
req.to_csv(EVIDENCE / "H20_0_REQUEST_OUTCOMES.csv", index=False)

# ------------------------------------------------------------------ archive persistence
if len(A):
    A["period"] = np.where(A["year"].isin(EARLY), "EARLY_2018_2020", np.where(A["year"].isin(LATE), "LATE_2024_2026", "MID_2021_2023"))
    arch = A.groupby(["source_id", "period"]).agg(
        n=("url", "size"), cdx_ok=("cdx_outcome", lambda s: float((s == "OK").mean())), captured_ever=("cap_any", "mean"),
        captured_le_t=("cap_le_t", "mean"), stamp_after_capture=("stamp_after_capture", "mean"), url_reuse_suspect=("url_reuse_suspect", "sum"),
        median_capture_lag_h=("capture_lag_hours", "median")).reset_index()
    if "live_status" in A:
        live = A[A["source_id"] == "S_GDELT_GKG"].copy()
        live["live_ok"] = live["live_outcome"] == "OK"
        lr = live.groupby(["period", "crypto"]).agg(n=("url", "size"), live_ok=("live_ok", "mean"), captured_ever=("cap_any", "mean"),
                                                    captured_le_t=("cap_le_t", "mean")).reset_index()
        lr.to_csv(EVIDENCE / "H20_0_GDELT_LINK_ROT.csv", index=False)
    arch.to_csv(EVIDENCE / "H20_0_ARCHIVE_PERSISTENCE.csv", index=False)
    if "alt_captured" in A:
        sec = A[A["source_id"] == "S_SEC_PRESS"]
        sec_url = {"n": len(sec), "current_url_captured_le_t": float((sec["first_capture_utc"] <= sec["t_utc"]).mean()),
                   "at_time_url_captured_le_t": float((sec["alt_first_capture_utc"] <= sec["t_utc"]).mean())}
    else:
        sec_url = {}
else:
    arch, sec_url = pd.DataFrame(), {}

# ------------------------------------------------------------------ quality distributions
def shares(df, by, col):
    x = df.groupby(by)[col].value_counts(normalize=True).unstack(fill_value=0)
    return x.reset_index()


ts_src = shares(D, "source_id", "timestamp_quality")
ts_year = shares(D[D["source_id"] != "S_GDELT_GKG"], "year", "timestamp_quality")
vq_src = shares(D, "source_id", "version_quality")
ts_src.to_csv(EVIDENCE / "H20_0_TIMESTAMP_QUALITY_BY_SOURCE.csv", index=False)
ts_year.to_csv(EVIDENCE / "H20_0_TIMESTAMP_QUALITY_BY_YEAR.csv", index=False)
vq_src.to_csv(EVIDENCE / "H20_0_VERSION_QUALITY_BY_SOURCE.csv", index=False)

# version quality for archive-dependent sources is estimated on the archive subsample
def g4_share(src: str) -> tuple[float, str]:
    sub = D[D["source_id"] == src]
    if not len(sub):
        return float("nan"), "NO_DOCS"
    if src in ("S_BINANCE_CMS", "S_FED_PRESS", "S_SEC_PRESS", "S_CFTC_PRESS"):
        a = A[A["source_id"] == src] if len(A) else pd.DataFrame()
        if not len(a):
            return float("nan"), "NOT_MEASURED"
        return float(a["cap_le_t"].mean()), f"ARCHIVE_SUBSAMPLE_n={len(a)}"
    return float(sub["version_quality"].isin(["V0_IMMUTABLE", "V1_ARCHIVED_AT_T", "V2_VERSIONED"]).mean()), f"ALL_DOCS_n={len(sub)}"


# ------------------------------------------------------------------ Wikipedia retrospective editing and ALFRED revisions
wr = {}
if len(P):
    past = P[pd.to_datetime(P["day"]).dt.date < P["sample_id"].map(T).dt.date]
    wr = {"day_pages": int(len(P)), "exists_at_t": float(P["exists_at_t"].mean()),
          "items_at_t": int(P["items_at_t"].fillna(0).sum()), "items_now": int(P["items_now"].fillna(0).sum()),
          "share_of_current_items_absent_at_t": float(1 - P["items_at_t"].fillna(0).sum() / max(P["items_now"].fillna(0).sum(), 1)),
          "pages_edited_after_t": float((P["edits_after_t"].fillna(0) > 0).mean()),
          "median_edits_after_t": float(P["edits_after_t"].median()),
          "completed_days_share_of_items_absent_at_t": float(1 - past["items_at_t"].fillna(0).sum() / max(past["items_now"].fillna(0).sum(), 1)),
          "crypto_items_at_t": int(P["crypto_items_at_t"].fillna(0).sum()), "crypto_items_now": int(P["crypto_items_now"].fillna(0).sum())}
alf = AL.groupby("series")[["recent_obs_compared", "recent_obs_revised"]].sum().reset_index() if len(AL) else pd.DataFrame()
if len(alf):
    alf["revised_share"] = alf["recent_obs_revised"] / alf["recent_obs_compared"]
    alf.to_csv(EVIDENCE / "H20_0_ALFRED_REVISIONS.csv", index=False)

# ------------------------------------------------------------------ entity resolution
EV = rd("entity_resolution_validation")
gold = pd.read_csv(EVIDENCE / "H20_0_ENTITY_GOLD_VALIDATION.csv") if (EVIDENCE / "H20_0_ENTITY_GOLD_VALIDATION.csv").exists() else pd.DataFrame()
ent = []
for lab, df in (("frozen_sample", E), ("validation_sample", EV)):
    if not len(df):
        continue
    for parser, col in (("v1", "v1_name_status"), ("v2", "name_status")):
        ent.append({"sample": lab, "parser": parser, "n": len(df), "resolved": float((df[col] == "RESOLVED").mean()),
                    "ambiguous": float((df[col] == "AMBIGUOUS").mean()), "not_found": float((df[col] == "NOT_FOUND").mean()),
                    "ticker_only_notice": float((df["name_detail"] == "TICKER_ONLY_NOTICE").mean()) if parser == "v2" else None,
                    "no_listing_notice": float((df["name_detail"] == "NO_LISTING_NOTICE").mean()) if parser == "v2" else None,
                    "ticker_era_conflict": float(df["ticker_era_conflict"].mean()), "blvt_share": float((df["entity_type"] == "BLVT").mean()),
                    "tuned_on_this_sample": lab == "frozen_sample" and parser == "v2"})
ENT = pd.DataFrame(ent)
ENT.to_csv(EVIDENCE / "H20_0_ENTITY_RESOLUTION.csv", index=False)
gold_precision = float((gold["gold_label"] != "WRONG_ASSET").mean()) if len(gold) else None
gold_exact = float((gold["gold_label"] == "CORRECT").mean()) if len(gold) else None
def period(y: int) -> str:
    return "EARLY_2018_2020" if y in EARLY else ("LATE_2024_2026" if y in LATE else "MID_2021_2023")


ev_by_period = (
    EV.assign(period=pd.to_datetime(EV["t_utc"], utc=True).dt.year.map(period))
    .groupby("period")["name_status"].apply(lambda s: float((s == "RESOLVED").mean())).to_dict()
    if len(EV) else {}
)

# ------------------------------------------------------------------ coverage by source and year
cov = S.groupby(["source_id", "year"]).agg(timestamps=("sample_id", "size"), available=("available", "mean"),
                                           mean_docs_w7=("n_docs_w7", "mean"),
                                           share_ge1_doc=("n_docs_w7", lambda s: float((s.fillna(0) > 0).mean()))).reset_index()
cov.to_csv(EVIDENCE / "H20_0_COVERAGE_BY_SOURCE_YEAR.csv", index=False)

# ------------------------------------------------------------------ missingness
miss = []
for keys, grp in S.groupby(["source_id", "year"]):
    miss.append({"dimension": "source_x_year", "key": f"{keys[0]}|{keys[1]}", "n": len(grp),
                 "missing": float((grp["status"] == "MISSING").mean()), "zero": float((grp["status"] == "ZERO").mean()),
                 "observed": float((grp["status"] == "OBSERVED").mean())})
C5["age_bucket"] = pd.cut(C5["asset_age_days"], [-1, 365, 3 * 365, 100000], labels=["<1y", "1-3y", ">3y"])
for dim in ("year", "liquidity_tercile", "age_bucket", "entity_type", "name_status_v2"):
    for k, grp in C5.groupby(dim, observed=True):
        miss.append({"dimension": f"C5_{dim}", "key": str(k), "n": len(grp), "missing": None,
                     "zero": float((~grp["any_asset_doc_w30"]).mean()), "observed": float(grp["any_asset_doc_w30"].mean()),
                     "non_venue_observed": float(grp["non_venue_doc_w30"].mean())})
MISS = pd.DataFrame(miss)
MISS.to_csv(EVIDENCE / "H20_0_MISSINGNESS.csv", index=False)

# ------------------------------------------------------------------ bias audits
def bias(name, layer, a_lab, a, b_lab, b):
    ratio = (b / a) if a else (float("inf") if b else 1.0)
    gap = (b - a) * 100
    severe = (max(ratio, 1 / ratio if ratio else float("inf")) >= 3) or abs(gap) >= 30
    return {"audit": name, "layer": layer, "group_a": a_lab, "value_a": a, "group_b": b_lab, "value_b": b,
            "ratio_b_over_a": ratio, "gap_pp": gap, "severe": bool(severe)}


BIAS = []
for L, srcs in LAYER_SOURCES.items():
    if L == "C5":
        continue
    col = f"n_{L}"
    sub = S[S["source_id"].isin(srcs) & S["available"]]
    per_t = sub.groupby("sample_id")[col].sum()
    cov_t = (per_t > 0)
    e = float(cov_t[[s for s in cov_t.index if YEAR[s] in EARLY]].mean())
    l_ = float(cov_t[[s for s in cov_t.index if YEAR[s] in LATE]].mean())
    BIAS.append(bias("temporal_coverage_share_ge1_doc", L, "2018-2020", e, "2024-2026", l_))
    me = float(per_t[[s for s in per_t.index if YEAR[s] in EARLY]].mean())
    ml = float(per_t[[s for s in per_t.index if YEAR[s] in LATE]].mean())
    BIAS.append(bias("temporal_mean_docs_w7 (descriptive)", L, "2018-2020", me, "2024-2026", ml) | {"severe": None})
c5e = float(C5.loc[C5["year"].isin(EARLY), "any_asset_doc_w30"].mean())
c5l = float(C5.loc[C5["year"].isin(LATE), "any_asset_doc_w30"].mean())
BIAS.append(bias("temporal_coverage_share_ge1_doc", "C5", "2018-2020", c5e, "2024-2026", c5l))
lo = float(C5.loc[C5["liquidity_tercile"] == "T1_LOW", "any_asset_doc_w30"].mean())
hi = float(C5.loc[C5["liquidity_tercile"] == "T3_HIGH", "any_asset_doc_w30"].mean())
BIAS.append(bias("entity_popularity_any_doc_w30", "C5", "T1_LOW", lo, "T3_HIGH", hi))
lo2 = float(C5.loc[C5["liquidity_tercile"] == "T1_LOW", "non_venue_doc_w30"].mean())
hi2 = float(C5.loc[C5["liquidity_tercile"] == "T3_HIGH", "non_venue_doc_w30"].mean())
BIAS.append(bias("entity_popularity_non_venue_doc_w30", "C5", "T1_LOW", lo2, "T3_HIGH", hi2))
if ev_by_period:
    BIAS.append(bias("temporal_name_resolution_v2_validation", "C5", "2018-2020", ev_by_period.get("EARLY_2018_2020", np.nan),
                     "2024-2026", ev_by_period.get("LATE_2024_2026", np.nan)))
ts0 = D[D["source_id"] != "S_GDELT_GKG"].assign(t0=lambda x: x["timestamp_quality"] == "T0_EXACT")
BIAS.append(bias("timestamp_exact_share (all sources ex GDELT)", "ALL", "2018-2020", float(ts0.loc[ts0["year"].isin(EARLY), "t0"].mean()),
                 "2024-2026", float(ts0.loc[ts0["year"].isin(LATE), "t0"].mean())))
for src in ("S_BINANCE_CMS", "S_FED_PRESS", "S_SEC_PRESS", "S_CFTC_PRESS", "S_GDELT_GKG"):
    a = A[A["source_id"] == src] if len(A) else pd.DataFrame()
    if len(a):
        BIAS.append(bias("archive_captured_le_t", src, "2018-2020", float(a.loc[a["year"].isin(EARLY), "cap_le_t"].mean()),
                         "2024-2026", float(a.loc[a["year"].isin(LATE), "cap_le_t"].mean())))
if len(G):
    BIAS.append(bias("language_non_english_share_of_gdelt_records", "C3", "en_feed_share", float((G["feed"] == "en").mean()),
                     "translingual_share", float((G["feed"] != "en").mean())) | {"severe": None})
    ce = float(G.loc[G["feed"] == "en", "crypto"].mean())
    ct = float(G.loc[G["feed"] != "en", "crypto"].mean())
    BIAS.append(bias("language_crypto_tag_rate", "C3", "english", ce, "translingual", ct))
BIAS = pd.DataFrame(BIAS)
BIAS.to_csv(EVIDENCE / "H20_0_BIAS_AUDITS.csv", index=False)

# ------------------------------------------------------------------ gate
def layer_docs(L: str) -> pd.DataFrame:
    if L == "C3":
        return D[(D["source_id"].isin(LAYER_SOURCES[L])) & D["crypto"]]
    if L == "C5":  # asset-specific: PIT Wikipedia articles and venue notices naming a ticker in parentheses
        named = (D["source_id"] == "S_BINANCE_CMS") & D["title"].fillna("").str.contains(r"\([A-Z0-9]{2,15}\)", regex=True)
        return D[(D["source_id"] == "S_WIKI_ASSET") | named]
    if L == "C4":
        return D[D["source_id"] == "S_BINANCE_CMS"]
    return D[(D["source_id"].isin(LAYER_SOURCES[L])) & D["context_layer"].str.contains(L[1])]


gate_layers = {}
for L, srcs in LAYER_SOURCES.items():
    crit = {}
    if L == "C5":
        g1 = float(C5["any_asset_doc_w30"].notna().mean())  # Binance catalogue reachable for every unit
        g1_note = "share of asset-time units with >=1 available asset-specific source (Binance notices by ticker)"
        yrs = C5.loc[C5["any_asset_doc_w30"], "year"].nunique()
    else:
        avail = S[S["source_id"].isin(srcs)].groupby("sample_id")["available"].any()
        g1, g1_note = float(avail.mean()), "share of sample timestamps with >=1 available+retrievable source"
        yrs = int(S[S["source_id"].isin(srcs) & S["available"]].assign(n=lambda x: x[f"n_{L}"].fillna(0)).groupby("year")["n"].sum().gt(0).sum())
    crit["G1_coverage"] = {"value": g1, "bar": 0.90, "pass": g1 >= 0.90, "note": g1_note}
    crit["G2_year_span"] = {"value": int(yrs), "bar": 8, "pass": int(yrs) >= 8}
    ld = layer_docs(L)
    tq = ld["timestamp_quality"].value_counts(normalize=True)
    g3 = float(tq.reindex(["T0_EXACT", "T1_MINUTE_OR_HOUR", "T2_DAY_ONLY"]).fillna(0).sum()) if len(ld) else float("nan")
    t4 = float(tq.get("T4_RETROSPECTIVE", 0.0)) if len(ld) else float("nan")
    crit["G3_timestamp"] = {"value": g3, "t4": t4, "bar": "T0+T1+T2 >= 0.80 and T4 <= 0.05", "n_docs": int(len(ld)),
                            "pass": bool(len(ld) and g3 >= 0.80 and t4 <= 0.05)}
    num, den, parts = 0.0, 0, {}
    for src in srcs:
        n = int((ld["source_id"] == src).sum())
        v, basis = g4_share(src)
        parts[src] = {"docs": n, "v012_share": v, "basis": basis}
        if n and v == v:
            num, den = num + v * n, den + n
    g4 = num / den if den else float("nan")
    crit["G4_version"] = {"value": g4, "bar": 0.70, "pass": bool(den and g4 >= 0.70), "by_source": parts}
    rr = rep[rep["source_id"].isin(srcs + (["S_WIKI_PORTAL"] if L in ("C1", "C2", "C3") else []))] if len(rep) else pd.DataFrame()
    if L == "C5":
        rr = rep[rep["source_id"].isin(["S_BINANCE_CMS", "S_WIKI_PORTAL"])] if len(rep) else pd.DataFrame()
    if len(rr):
        succ = float((rr["refetch_success"] * rr["n"]).sum() / rr["n"].sum())
        stab = float((rr["hash_stable"] * rr["n"]).sum() / rr["n"].sum())
    else:
        succ = stab = float("nan")
    crit["G5_reproducibility"] = {"refetch_success": succ, "hash_stable": stab, "bar": 0.95,
                                  "pass": bool(len(rr) and succ >= 0.95 and stab >= 0.95),
                                  "sources": rr["source_id"].tolist() if len(rr) else []}
    crit["G6_licensing"] = {"pass": all(LICENCE[s][2] for s in srcs if s in LICENCE),
                            "classes": {s: LICENCE[s][0] for s in srcs if s in LICENCE}}
    if L == "C4":
        res = C4["resolution"].str.startswith("RESOLVED").mean() if len(C4) else float("nan")
        crit["G7_entity"] = {"value": float(res), "ambiguous": 0.0, "bar": "resolved >= 0.80, ambiguous <= 0.10",
                             "basis": "parenthesised tickers in W7 Binance notices -> era as of publication", "n": int(len(C4)),
                             "pass": bool(res >= 0.80)}
    if L == "C5":
        v = ENT[(ENT["sample"] == "validation_sample") & (ENT["parser"] == "v2")]
        res = float(v["resolved"].iloc[0]) if len(v) else float("nan")
        amb = float(v["ambiguous"].iloc[0]) if len(v) else float("nan")
        crit["G7_entity"] = {"value": res, "ambiguous": amb, "bar": "resolved >= 0.80, ambiguous <= 0.10",
                             "basis": "PIT name resolution, parser v2, untuned validation sample (deviation D1)",
                             "gold_same_asset_precision": gold_precision, "gold_exact_string": gold_exact,
                             "pass": bool(res >= 0.80 and amb <= 0.10)}
    passed = all(c["pass"] for c in crit.values())
    sev = BIAS[(BIAS["layer"] == L) & (BIAS["severe"] == True)]["audit"].tolist()  # noqa: E712
    # conservative reading of the plan's severe-bias rule: an early-vs-late archive gap in a source that
    # carries this layer's documents is a temporal bias of the layer's reconstructible content
    src_sev = BIAS[BIAS["layer"].isin(srcs) & (BIAS["severe"] == True)]  # noqa: E712
    sev += [f"{a}:{s}" for a, s in zip(src_sev["audit"], src_sev["layer"])
            if int((layer_docs(L)["source_id"] == s).sum()) > 0]
    gate_layers[L] = {"criteria": crit, "all_criteria_pass": passed, "severe_bias": sev,
                      "layer_verdict": ("PASS" if not sev else "CONDITIONAL") if passed else "FAIL",
                      "failed": [k for k, c in crit.items() if not c["pass"]]}

verdicts = [v["layer_verdict"] for v in gate_layers.values()]
if all(v == "PASS" for v in verdicts):
    overall = "PASS"
elif any(v in ("PASS", "CONDITIONAL") for v in verdicts):
    overall = "PARTIAL PASS"
else:
    overall = "DATA-GATE FAIL / UNTESTED"

metrics = {
    "documents_total": int(len(D)), "documents_pit_eligible": int(D["pit_eligible"].sum()),
    "documents_by_source": D["source_id"].value_counts().to_dict(),
    "binance_harvest": harvest, "binance_snapshot_diff": json.loads((INTERIM / "binance_snapshot_diff.json").read_text()) if (INTERIM / "binance_snapshot_diff.json").exists() else None,
    "binance_detail_outcomes": BD["outcome"].value_counts().to_dict() if len(BD) else {},
    "binance_cms_version_values": BD["version"].astype(str).value_counts().to_dict() if len(BD) else {},
    "binance_cms_last_update_nonzero": float((pd.to_numeric(BD.get("last_update_ms"), errors="coerce").fillna(0) > 0).mean()) if len(BD) else None,
    "wiki_portal": wr, "sec_url_migration": sec_url,
    "gdelt": {"slices_ok": int((GF["outcome"] == "OK").sum()) if len(GF) else 0, "slices_total": int(len(GF)),
              "records": int(len(G)), "crypto_records": int(G["crypto"].sum()) if len(G) else 0},
    "request_log_malformed_lines": malformed, "requests_total": int(len(RL)),
    "entity_validation_v2_by_period": ev_by_period,
    "c5_any_asset_doc_w30": float(C5["any_asset_doc_w30"].mean()), "c5_non_venue_doc_w30": float(C5["non_venue_doc_w30"].mean()),
}
(EVIDENCE / "H20_0_METRICS.json").write_text(json.dumps(metrics, indent=1, default=str))
gate = {
    "experiment": "H20.0 Context Data Feasibility", "computed_utc": iso(now_utc()),
    "freeze_sha256": F["freeze_sha256"], "plan_sha256": F["plan_sha256"],
    "verdict": overall, "verdict_scope": "data substrate only; never an economic REJECT",
    "layers": gate_layers, "survivorship_audit": "see evidence/H20_0_SEALED_SURVIVORSHIP.json (sealed stage)",
    "outcome_tables_read": False, "returns_computed": False,
}
(CA / "H20_0_GATE.json").write_text(json.dumps(gate, indent=1, default=str))
print(json.dumps({k: (v["layer_verdict"], v["failed"], v["severe_bias"]) for k, v in gate_layers.items()}, indent=1))
print("OVERALL", overall)

# ------------------------------------------------------------------ pre-seal hashes
MANIFESTS.mkdir(exist_ok=True)
to_lf(list(EVIDENCE.glob("*")) + [CA / "H20_0_GATE.json"])
seal = {"written_utc": iso(now_utc()),
        "files": {str(p.relative_to(CA)).replace("\\", "/"): sha256_file(p)
                  for p in sorted(list(INTERIM.glob("*.parquet")) + list(EVIDENCE.glob("H20_0_*")) + [DERIVED / "context_documents.parquet", CA / "H20_0_GATE.json"])
                  if p.name != "H20_0_SEALED_SURVIVORSHIP.json"}}
(MANIFESTS / "H20_0_PRE_SEAL_HASHES.json").write_text(json.dumps(seal, indent=1))
