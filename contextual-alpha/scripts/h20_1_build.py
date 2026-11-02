"""H20.1 — build the feature matrix and its provenance from the frozen inputs (plan sections 7-9).

Reads only data/interim/h20_1/*.parquet (written by h20_1_collect.py) and the sample freeze. Applies
the frozen rules in h20_1_rep.py. Writes, into --out (default data/derived/h20_1):

  features_long.csv   sample_id, t_utc, feature_id, feature_name, value, status, missing_reason
  features_wide.csv   one row per timestamp, one column per feature (NaN = missing)
  provenance.csv      one row per (timestamp, feature, contributing record)

Output is byte-deterministic: fixed sort orders, fixed float formatting, LF line endings. No outcome is
read; no model is fitted; no network request is made.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_1_build.py" [--out <dir>]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

import h20_1_rep as rep
from h20_common import CA, DERIVED, INTERIM, content_hash, iso, sha256_bytes

IN = INTERIM / "h20_1"
SAMPLE = CA / "H20_1_SAMPLE_FREEZE.json"
FEED_FETCHED = datetime(2026, 10, 18, 0, 0, tzinfo=UTC)  # H20.0 raw Fed feed fetch date (lower bound)
PROV_FIELDS = ["sample_id", "t_utc", "feature_id", "record_type", "source_id", "source_document_key",
               "document_id", "public_availability_time", "window_lo", "window_hi", "rule_id", "detail",
               "transform_version"]


def doc_id(source_id: str, key: str, *content: str) -> str:
    return sha256_bytes(f"{source_id}\n{key}\n{content_hash(*content)}".encode("utf-8"))[:32]


def fmt(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    if isinstance(v, (int,)) and not isinstance(v, bool):
        return str(v)
    return f"{float(v):.10g}"


def utc(x) -> datetime:
    return pd.Timestamp(x).tz_convert("UTC").to_pydatetime() if pd.Timestamp(x).tzinfo else pd.Timestamp(x, tz="UTC").to_pydatetime()


class Builder:
    def __init__(self) -> None:
        self.values: list[dict] = []
        self.prov: list[dict] = []
        self.sample = [(s["sample_id"], datetime.fromisoformat(s["t_utc"].replace("Z", "+00:00")))
                       for s in json.loads(SAMPLE.read_text(encoding="utf-8"))["sample"]]
        self.fed = pd.read_parquet(IN / "fed.parquet")
        self.fr = pd.read_parquet(IN / "fr.parquet")
        self.fr_status = pd.read_parquet(IN / "fr_status.parquet")
        self.sec = pd.read_parquet(IN / "sec.parquet")
        self.sec_status = pd.read_parquet(IN / "sec_status.parquet")
        self.cftc = pd.read_parquet(IN / "cftc.parquet")
        self.alfred = pd.read_parquet(IN / "alfred.parquet")
        self.wpages = pd.read_parquet(IN / "wiki_pages.parquet")
        self.witems = pd.read_parquet(IN / "wiki_items.parquet")
        self.gfiles = pd.read_parquet(IN / "gdelt_files.parquet")
        self.grec = pd.read_parquet(IN / "gdelt_crypto_records.parquet")
        for d in (self.fed, self.fr, self.sec, self.cftc):
            d["public_availability_time"] = pd.to_datetime(d["public_availability_time"], utc=True)
            d.sort_values(["public_availability_time", "source_document_key"], inplace=True, kind="mergesort")
        self.fed["doc_id"] = [doc_id("S_FED_PRESS", k, t) for k, t in zip(self.fed["source_document_key"], self.fed["title"])]
        self.fr["doc_id"] = [doc_id("S_FEDREG", k, t, a) for k, t, a in zip(self.fr["source_document_key"], self.fr["title"], self.fr["abstract"])]
        self.sec["doc_id"] = [doc_id("S_SEC_PRESS", k, t) for k, t in zip(self.sec["source_document_key"], self.sec["title"])]
        self.cftc["doc_id"] = [doc_id("S_CFTC_PRESS", k, t) for k, t in zip(self.cftc["source_document_key"], self.cftc["title"])]
        self.fr["crypto"] = (self.fr["title"].fillna("") + " " + self.fr["abstract"].fillna("")).str.contains(rep.K_CRYPTO)
        self.fr["finreg"] = self.fr["agencies"].fillna("").map(lambda s: bool(set(s.split(";")) & rep.FR_FINREG))
        self.fr["rulemaking"] = self.fr["doc_type"].isin(rep.FR_RULEMAKING)
        self.sec["crypto"] = self.sec["title"].str.contains(rep.K_CRYPTO)
        self.sec["enforcement"] = self.sec["title"].str.contains(rep.K_SEC_ENFORCEMENT)
        self.fed["fomc"] = (self.fed["doc_type"] == rep.FOMC_DOC_TYPE) & self.fed["title"].str.contains(rep.K_FOMC_TITLE)
        self.witems["crypto"] = self.witems["text"].str.contains(rep.K_CRYPTO)
        self.witems["stress"] = self.witems["crypto"] & self.witems["text"].str.contains(rep.K_CRYPTO_STRESS)
        self.alf = {(r.series, r.vintage_date): r for r in self.alfred.itertuples()}

    # ------------------------------------------------------------------ recording
    def put(self, sid, t, fid, value, reason=None):
        name = next(f[1] for f in rep.FEATURES if f[0] == fid)
        if value is None or (isinstance(value, float) and math.isnan(value)):
            status, value = "MISSING", None
        else:
            status = "ZERO" if value == 0 else "VALUE"
        self.values.append({"sample_id": sid, "t_utc": iso(t), "feature_id": fid, "feature_name": name,
                            "value": value, "status": status, "missing_reason": reason if status == "MISSING" else ""})

    def p(self, sid, t, fid, rtype, source, key="", did="", avail=None, lo=None, hi=None, rule="", detail=""):
        self.prov.append({"sample_id": sid, "t_utc": iso(t), "feature_id": fid, "record_type": rtype,
                          "source_id": source, "source_document_key": key, "document_id": did,
                          "public_availability_time": iso(avail) if avail is not None else "",
                          "window_lo": iso(lo) if lo else "", "window_hi": iso(hi) if hi else "",
                          "rule_id": rule, "detail": detail, "transform_version": rep.REP_VERSION})

    def docs(self, sid, t, fid, D, w, source, rule):
        """Count documents of D (already filtered by rule) in window w; record provenance."""
        m = (D["public_availability_time"] > t - w) & (D["public_availability_time"] <= t)
        sel = D[m]
        for r in sel.itertuples():
            self.p(sid, t, fid, "DOCUMENT", source, r.source_document_key, r.doc_id, r.public_availability_time.to_pydatetime(),
                   t - w, t, rule)
        if not len(sel):
            self.p(sid, t, fid, "EMPTY_WINDOW", source, lo=t - w, hi=t, rule=rule)
        return len(sel), sel

    # ------------------------------------------------------------------ sources
    def months_ok(self, status: pd.DataFrame, lo: datetime, hi: datetime) -> bool:
        need, d = set(), (lo - timedelta(days=1)).date().replace(day=1)
        while d <= (hi + timedelta(days=1)).date():
            need.add(f"{d.year}-{d.month:02d}")
            d = d.replace(year=d.year + (d.month == 12), month=d.month % 12 + 1)
        st = status.drop_duplicates("month", keep="last").set_index("month")["outcome"]
        return all(st.get(m) == "OK" for m in need)

    def c1_fed(self, sid, t):
        span_ok = lambda w: t - w >= self.fed["public_availability_time"].min().to_pydatetime() and t <= FEED_FETCHED
        F = self.fed
        for fid, w, D, rule in (("F01", rep.W7, F, "ALL_ITEMS"),
                                ("F02", rep.W30, F[F["doc_type"] == rep.FED_MONETARY], "DOC_TYPE=Monetary Policy"),
                                ("F16", rep.W30, F[F["doc_type"] == rep.FED_ENFORCEMENT], "DOC_TYPE=Enforcement Actions")):
            if not span_ok(w):
                self.put(sid, t, fid, None, "OUT_OF_SOURCE_SPAN")
                continue
            n, _ = self.docs(sid, t, fid, D, w, "S_FED_PRESS", rule)
            self.put(sid, t, fid, n)
        if not span_ok(rep.W7):
            self.put(sid, t, "F03", None, "OUT_OF_SOURCE_SPAN")
        else:
            n, _ = self.docs(sid, t, "F03", F[F["fomc"]], rep.W7, "S_FED_PRESS", "K_FOMC_STATEMENT")
            self.put(sid, t, "F03", int(n >= 1))

    def c1_alfred(self, sid, t):
        a_t, a_7 = rep.alfred_asof(t).isoformat(), rep.alfred_asof(t - rep.W7).isoformat()

        def vint(series, vd, fid, role):
            r = self.alf.get((series, vd))
            if r is None or r.fetch_outcome != "OK":
                return None
            avail = rep.day_end_et(datetime.fromisoformat(vd).date())
            self.p(sid, t, fid, "VINTAGE", "S_ALFRED", f"{series}@{vd}", r.raw_sha256[:32], avail, rule=role,
                   detail=f"last_obs={r.last_obs_date};file={r.raw_file}")
            return r

        for fid, s in (("F04", "CPIAUCSL"), ("F05", "UNRATE")):
            r1, r0 = vint(s, a_t, fid, "VINTAGE_ASOF_T"), vint(s, a_7, fid, "VINTAGE_ASOF_T_MINUS_7D")
            self.put(sid, t, fid, None if r1 is None or r0 is None else int(r1.last_obs_date > r0.last_obs_date),
                     "FETCH_FAILED")
        for fid, s in (("F06", "DFF"), ("F08", "UNRATE")):
            r = vint(s, a_t, fid, "VINTAGE_ASOF_T")
            self.put(sid, t, fid, None if r is None else float(r.last_value), "FETCH_FAILED")
        r = vint("CPIAUCSL", a_t, "F07", "VINTAGE_ASOF_T")
        if r is None or r.yoy_base_value is None or (isinstance(r.yoy_base_value, float) and math.isnan(r.yoy_base_value)):
            self.put(sid, t, "F07", None, "FETCH_FAILED")
        else:
            self.p(sid, t, "F07", "VINTAGE_OBS", "S_ALFRED", f"CPIAUCSL@{a_t}", "", rule="YOY_BASE",
                   detail=f"base_obs={r.yoy_base_date}")
            self.put(sid, t, "F07", round(100.0 * (r.last_value / r.yoy_base_value - 1.0), 6))

    def c2_fr(self, sid, t):
        R = self.fr
        ok7 = self.months_ok(self.fr_status, (t - rep.W7).astimezone(rep.ET), t.astimezone(rep.ET))
        ok30 = self.months_ok(self.fr_status, (t - rep.W30).astimezone(rep.ET), t.astimezone(rep.ET))
        out = {}
        for fid, w, D, rule, ok in (("F09", rep.W7, R[R["finreg"]], "FR_FINREG", ok7),
                                    ("F10", rep.W7, R[R["crypto"]], "K_CRYPTO(title+abstract)", ok7),
                                    ("F11", rep.W30, R[R["crypto"]], "K_CRYPTO(title+abstract)", ok30),
                                    ("F12", rep.W30, R[R["crypto"] & R["rulemaking"]], "K_CRYPTO&FR_RULEMAKING", ok30)):
            if not ok:
                self.put(sid, t, fid, None, "FETCH_FAILED")
                out[fid] = None
                continue
            n, sel = self.docs(sid, t, fid, D, w, "S_FEDREG", rule)
            self.put(sid, t, fid, n)
            out[fid] = sel
        return out.get("F10")

    def c2_sec(self, sid, t):
        S = self.sec
        ok7 = self.months_ok(self.sec_status, t - rep.W7, t)
        ok30 = self.months_ok(self.sec_status, t - rep.W30, t)
        sec7 = None
        for fid, w, D, rule, ok in (("F13", rep.W7, S, "ALL_RELEASES", ok7),
                                    ("F14", rep.W7, S[S["enforcement"]], "K_SEC_ENFORCEMENT", ok7),
                                    ("F15", rep.W30, S[S["crypto"]], "K_CRYPTO(title)", ok30)):
            if not ok:
                self.put(sid, t, fid, None, "FETCH_FAILED")
                continue
            n, _ = self.docs(sid, t, fid, D, w, "S_SEC_PRESS", rule)
            self.put(sid, t, fid, n)
        if ok7:
            m = (S["public_availability_time"] > t - rep.W7) & (S["public_availability_time"] <= t) & S["crypto"]
            sec7 = S[m]
        return sec7

    def c2_cftc(self, sid, t):
        if not rep.cftc_walked(t - rep.W30, t):
            reason = "ACCESS_BLOCKED" if t.year >= 2021 and not rep.cftc_walked(t - rep.W30, t) else "NOT_WALKED"
            self.put(sid, t, "F17", None, reason)
            return
        n, _ = self.docs(sid, t, "F17", self.cftc, rep.W30, "S_CFTC_PRESS", "ALL_RELEASES")
        self.put(sid, t, "F17", n)

    def c2_composite(self, sid, t, fr10, sec7):
        if fr10 is None or sec7 is None:
            self.put(sid, t, "F18", None, "COMPONENT_MISSING")
            return
        for src, D, rule in (("S_FEDREG", fr10, "K_CRYPTO(title+abstract)"), ("S_SEC_PRESS", sec7, "K_CRYPTO(title)")):
            for r in D.itertuples():
                self.p(sid, t, "F18", "DOCUMENT", src, r.source_document_key, r.doc_id,
                       r.public_availability_time.to_pydatetime(), t - rep.W7, t, rule)
        n = len(fr10) + len(sec7)
        if n == 0:
            self.p(sid, t, "F18", "EMPTY_WINDOW", "S_FEDREG;S_SEC_PRESS", lo=t - rep.W7, hi=t, rule="K_CRYPTO")
        self.put(sid, t, "F18", int(n >= 1))

    def c3_gdelt(self, sid, t):
        G = self.gfiles[self.gfiles["sample_id"] == sid].sort_values(["k", "feed"])
        recs = self.grec
        ok = G[G["outcome"] == "OK"]
        both = ok.groupby("k")["feed"].nunique()
        slices_both = sorted(both[both == 2].index)
        slices_en = sorted(ok.loc[ok["feed"] == "en", "k"])

        def files(fid, sel):
            for r in sel.itertuples():
                self.p(sid, t, fid, "GDELT_FILE", "S_GDELT_GKG", r.file, r.raw_sha256[:32],
                       utc(r.slice_utc) + rep.GDELT_PUBLISH_LAG, rule="S7",
                       detail=f"k={r.k};feed={r.feed};records={int(r.records)}")

        def records(fid, sel_files):
            rr = recs[recs["file"].isin(set(sel_files["file"]))].sort_values(["file", "gkg_id"])
            slice_of = dict(zip(sel_files["file"], sel_files["slice_utc"]))
            for r in rr.itertuples():
                self.p(sid, t, fid, "GDELT_RECORD", "S_GDELT_GKG", r.gkg_id, "",
                       utc(slice_of[r.file]) + rep.GDELT_PUBLISH_LAG, rule="K_GDELT_CRYPTO",
                       detail=f"file={r.file};match={r.match}")
            return rr

        # F19 count: all 14 files required
        if len(G) == 14 and (G["outcome"] == "OK").all():
            files("F19", G)
            rr = records("F19", G)
            self.put(sid, t, "F19", len(rr))
        else:
            self.put(sid, t, "F19", None, "FILE_MISSING")
            rr = None
        # F20 / F21 shares
        for fid, ks, feeds in (("F20", slices_both, ("en", "translingual")), ("F21", slices_en, ("en",))):
            if len(ks) < rep.GDELT_MIN_SLICES:
                self.put(sid, t, fid, None, "INSUFFICIENT_SLICES")
                continue
            sel = ok[ok["k"].isin(ks) & ok["feed"].isin(feeds)]
            files(fid, sel)
            num = len(records(fid, sel))
            den = int(sel["records"].sum())
            self.put(sid, t, fid, None if den == 0 else num / den, "INSUFFICIENT_SLICES")
        # F22 tone
        if rr is None:
            self.put(sid, t, "F22", None, "FILE_MISSING")
        else:
            tones = rr["tone"].dropna()
            if not len(tones):
                files("F22", G)
                self.put(sid, t, "F22", None, "UNDEFINED_NO_RECORDS")
            else:
                files("F22", G)
                records("F22", G)
                self.put(sid, t, "F22", round(float(tones.mean()), 8))

    def c3_wiki(self, sid, t):
        P = self.wpages[self.wpages["sample_id"] == sid].sort_values("day")
        if len(P) != 7 or not P["outcome"].isin(["OK", "PAGE_ABSENT_AT_T"]).all():
            for fid in ("F23", "F24", "F25"):
                self.put(sid, t, fid, None, "FETCH_FAILED")
            return
        I = self.witems[self.witems["sample_id"] == sid].sort_values(["day", "item_idx"])
        for fid, sel, rule in (("F23", I[I["crypto"]], "K_CRYPTO(item)"), ("F24", I[I["crypto"]], "K_CRYPTO(item)"),
                               ("F25", I[I["stress"]], "K_CRYPTO&K_CRYPTO_STRESS(item)")):
            for r in P.itertuples():
                rev = utc(r.rev_utc) if r.outcome == "OK" else None
                self.p(sid, t, fid, "WIKI_PAGE" if r.outcome == "OK" else "PAGE_ABSENT_AT_T", "S_WIKI_PORTAL",
                       r.title, str(int(r.revid)) if r.outcome == "OK" else "", rev, rule="D7",
                       detail=f"day={r.day};items={int(r.n_items) if r.outcome == 'OK' else 0}")
            for r in sel.itertuples():
                self.p(sid, t, fid, "WIKI_ITEM", "S_WIKI_PORTAL", f"{r.revid}#{r.item_idx}",
                       doc_id("S_WIKI_PORTAL", f"{r.revid}#{r.item_idx}", r.text), utc(r.rev_utc), rule=rule,
                       detail=f"day={r.day}")
            n = len(sel)
            self.put(sid, t, fid, n if fid == "F23" else int(n >= 1))

    def run(self):
        for sid, t in self.sample:
            self.c1_fed(sid, t)
            self.c1_alfred(sid, t)
            fr10 = self.c2_fr(sid, t)
            sec7 = self.c2_sec(sid, t)
            self.c2_cftc(sid, t)
            self.c2_composite(sid, t, fr10, sec7)
            self.c3_gdelt(sid, t)
            self.c3_wiki(sid, t)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (fmt(r[k]) if k == "value" else r[k]) for k in fields})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DERIVED / "h20_1"))
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    b = Builder()
    b.run()
    order = {f[0]: i for i, f in enumerate(rep.FEATURES)}
    vals = sorted(b.values, key=lambda r: (r["sample_id"], order[r["feature_id"]]))
    write_csv(out / "features_long.csv", vals,
              ["sample_id", "t_utc", "feature_id", "feature_name", "value", "status", "missing_reason"])
    wide: dict[str, dict] = {}
    for r in vals:
        wide.setdefault(r["sample_id"], {"sample_id": r["sample_id"], "t_utc": r["t_utc"]})[r["feature_name"]] = fmt(r["value"])
    with (out / "features_wide.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sample_id", "t_utc", *rep.FEATURE_NAMES], lineterminator="\n")
        w.writeheader()
        w.writerows(wide[k] for k in sorted(wide))
    prov = sorted(b.prov, key=lambda r: (r["sample_id"], order[r["feature_id"]], r["record_type"],
                                         r["source_id"], r["source_document_key"], r["detail"]))
    write_csv(out / "provenance.csv", prov, PROV_FIELDS)
    print(f"values {len(vals)}  provenance rows {len(prov)}  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
