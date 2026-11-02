"""H20.3 P1 — the 18 frozen context features at every landmark decision time, with the H20.1 audits.

The H20.1 rules module (h20_1_rep.py) and the H20.1 collector / builder logic are used unchanged;
only the list of decision times (the H20.3 landmark calendar) and the output folders differ.
Federal Register and SEC raw pages and the Fed feed bytes are already on disk and are parsed, not
re-requested; ALFRED vintages and Wikipedia revisions are collected for the new times.

  --part collect    fed, fr, sec, alfred, wiki for the calendar -> data/interim/h20_3/context/
  --part build      build the 18 features + provenance into --out (default data/derived/h20_3/context)
  --part audit      P1.1-P1.9 -> data/derived/h20_3/p1_audit.json (runs build twice for P1.6)

No outcome is read.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_3_context.py" --part collect|build|audit
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

import h20_1_build as b1
import h20_1_collect as c1
import h20_1_rep as rep
from h20_3_common import CAL, INT3, OUT, ROOT, iso, now_utc, p0, sha256_file, spec, write_calendar

CTX_IN = INT3 / "context"
CTX_OUT = OUT / "context"
KEEP = None  # filled from the frozen CONTEXT_EXPANDED (feature ids)


def frozen_ids() -> dict:
    s = spec()["context"]
    return {e["feature_id"]: e["feature_name"] for e in s["CONTEXT_EXPANDED"]}


def collect(parts: str = "fed,fr,sec,alfred,wiki") -> int:
    p0()
    write_calendar()
    CTX_IN.mkdir(parents=True, exist_ok=True)
    c1.SAMPLE, c1.OUT = CAL, CTX_IN
    for part in parts.split(","):
        getattr(c1, part)()
    print("collect done", iso(now_utc()))
    return 0


class CtxBuilder(b1.Builder):
    """H20.1 Builder restricted to the sources of the 18 eligible features (no GDELT, no CFTC)."""

    def __init__(self) -> None:  # noqa: D107 - mirrors Builder.__init__ for the needed tables only
        IN = CTX_IN
        self.values, self.prov = [], []
        self.sample = [(s["sample_id"], pd.Timestamp(s["t_utc"]).to_pydatetime())
                       for s in json.loads(CAL.read_text(encoding="utf-8"))["sample"]]
        self.fed = pd.read_parquet(IN / "fed.parquet")
        self.fr = pd.read_parquet(IN / "fr.parquet")
        self.fr_status = pd.read_parquet(IN / "fr_status.parquet")
        self.sec = pd.read_parquet(IN / "sec.parquet")
        self.sec_status = pd.read_parquet(IN / "sec_status.parquet")
        self.alfred = pd.read_parquet(IN / "alfred.parquet")
        self.wpages = pd.read_parquet(IN / "wiki_pages.parquet")
        self.witems = pd.read_parquet(IN / "wiki_items.parquet")
        for d in (self.fed, self.fr, self.sec):
            d["public_availability_time"] = pd.to_datetime(d["public_availability_time"], utc=True)
            d.sort_values(["public_availability_time", "source_document_key"], inplace=True, kind="mergesort")
        self.fed["doc_id"] = [b1.doc_id("S_FED_PRESS", k, t) for k, t in zip(self.fed["source_document_key"], self.fed["title"])]
        self.fr["doc_id"] = [b1.doc_id("S_FEDREG", k, t, a) for k, t, a in zip(self.fr["source_document_key"], self.fr["title"], self.fr["abstract"])]
        self.sec["doc_id"] = [b1.doc_id("S_SEC_PRESS", k, t) for k, t in zip(self.sec["source_document_key"], self.sec["title"])]
        self.fr["crypto"] = (self.fr["title"].fillna("") + " " + self.fr["abstract"].fillna("")).str.contains(rep.K_CRYPTO)
        self.fr["finreg"] = self.fr["agencies"].fillna("").map(lambda s: bool(set(s.split(";")) & rep.FR_FINREG))
        self.fr["rulemaking"] = self.fr["doc_type"].isin(rep.FR_RULEMAKING)
        self.sec["crypto"] = self.sec["title"].str.contains(rep.K_CRYPTO)
        self.sec["enforcement"] = self.sec["title"].str.contains(rep.K_SEC_ENFORCEMENT)
        self.fed["fomc"] = (self.fed["doc_type"] == rep.FOMC_DOC_TYPE) & self.fed["title"].str.contains(rep.K_FOMC_TITLE)
        self.witems["crypto"] = self.witems["text"].str.contains(rep.K_CRYPTO)
        self.witems["stress"] = self.witems["crypto"] & self.witems["text"].str.contains(rep.K_CRYPTO_STRESS)
        self.alf = {(r.series, r.vintage_date): r for r in self.alfred.itertuples()}

    def run(self) -> None:
        for sid, t in self.sample:
            self.c1_fed(sid, t)
            self.c1_alfred(sid, t)
            fr10 = self.c2_fr(sid, t)
            sec7 = self.c2_sec(sid, t)
            self.c2_composite(sid, t, fr10, sec7)
            self.c3_wiki(sid, t)


def build(out: Path) -> int:
    ids = frozen_ids()
    out.mkdir(parents=True, exist_ok=True)
    b = CtxBuilder()
    b.run()
    order = {f[0]: i for i, f in enumerate(rep.FEATURES)}
    vals = sorted((v for v in b.values if v["feature_id"] in ids), key=lambda r: (r["sample_id"], order[r["feature_id"]]))
    prov = sorted((p for p in b.prov if p["feature_id"] in ids),
                  key=lambda r: (r["sample_id"], order[r["feature_id"]], r["record_type"], r["source_id"],
                                 r["source_document_key"], r["detail"]))
    b1.write_csv(out / "features_long.csv", vals, ["sample_id", "t_utc", "feature_id", "feature_name", "value", "status", "missing_reason"])
    b1.write_csv(out / "provenance.csv", prov, b1.PROV_FIELDS)
    wide = {}
    for r in vals:
        wide.setdefault(r["sample_id"], {"sample_id": r["sample_id"], "t_utc": r["t_utc"]})[r["feature_name"]] = b1.fmt(r["value"])
    cols = ["sample_id", "t_utc", *ids.values()]
    pd.DataFrame([wide[k] for k in sorted(wide)])[cols].to_csv(out / "features_wide.csv", index=False, lineterminator="\n")
    print(f"context values {len(vals)} provenance {len(prov)} -> {out}")
    return 0


def audit() -> int:
    import h20_1_audit as a1

    p0()
    files = ("features_long.csv", "features_wide.csv", "provenance.csv")
    runs = {}
    for run in ("run1", "run2"):
        d = OUT / f"context_det_{run}"
        subprocess.run([sys.executable, __file__, "--part", "build", "--out", str(d)], check=True, cwd=str(ROOT))
        runs[run] = {f: sha256_file(d / f) for f in files}
    runs["primary"] = {f: sha256_file(CTX_OUT / f) for f in files}
    det = runs["run1"] == runs["run2"] == runs["primary"]
    V = pd.read_csv(CTX_OUT / "features_long.csv", dtype={"value": str}, keep_default_na=False)
    V["value"] = V["value"].replace("", float("nan"))
    P = pd.read_csv(CTX_OUT / "provenance.csv", dtype=str, keep_default_na=False)
    B = a1.pit(P)
    prov = a1.provenance_complete(V, P)
    mz = {"missing_with_value": int(((V["status"] == "MISSING") & V["value"].notna()).sum()),
          "missing_without_reason": int(((V["status"] == "MISSING") & (V["missing_reason"] == "")).sum())}
    ids = frozen_ids()
    produced = sorted(V["feature_id"].unique())
    weeks = V["sample_id"].nunique()
    all_missing_weeks = int(V.groupby("sample_id")["status"].apply(lambda s: (s == "MISSING").all()).sum())
    cov = V.assign(nm=V["status"] != "MISSING").groupby("feature_name")["nm"].mean().round(4).to_dict()
    checks = {
        "P1.1_rules_module_unchanged": True,  # p0() raised otherwise
        "P1.2_availability_after_t": B["availability_after_t"],
        "P1.3_vintage_after_asof_or_revision_after_t": B["vintage_date_after_asof"] + B["by_record_type"].get("WIKI_PAGE", {}).get("violations", 0)
        + B["by_record_type"].get("WIKI_ITEM", {}).get("violations", 0),
        "P1.4_window_end_after_t": B["window_end_after_t"],
        "P1.5_provenance_completeness": prov["completeness"],
        "P1.6_deterministic": det,
        "P1.7_missing_encoding_violations": mz["missing_with_value"] + mz["missing_without_reason"],
        "P1.8_common_to_all_assets": "by construction: one value per decision time, joined to every asset at that t",
        "P1.9_only_frozen_features": produced == sorted(ids),
    }
    passed = (checks["P1.2_availability_after_t"] == 0 and checks["P1.3_vintage_after_asof_or_revision_after_t"] == 0
              and checks["P1.4_window_end_after_t"] == 0 and checks["P1.5_provenance_completeness"] == 1.0 and det
              and checks["P1.7_missing_encoding_violations"] == 0 and checks["P1.9_only_frozen_features"]
              and B["timed_record_types_missing_time"] == 0)
    res = {"stage": "P1", "computed_utc": iso(now_utc()), "decision_times": weeks, "checks": checks, "PASS": passed,
           "pit_detail": B, "provenance": {k: v for k, v in prov.items() if k != "incomplete_sample"},
           "determinism_hashes": runs, "nonmissing_share_by_feature": cov, "weeks_with_every_context_missing": all_missing_weeks,
           "outputs_sha256": runs["primary"]}
    (OUT / "p1_audit.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"PASS": passed, **checks, "weeks_all_missing": all_missing_weeks}, indent=1, default=str))
    return 0 if passed else 3


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=["collect", "build", "audit"])
    ap.add_argument("--out", default=str(CTX_OUT))
    ap.add_argument("--parts", default="fed,fr,sec,alfred,wiki")
    a = ap.parse_args()
    sys.exit({"collect": lambda: collect(a.parts), "build": lambda: build(Path(a.out)), "audit": audit}[a.part]())
