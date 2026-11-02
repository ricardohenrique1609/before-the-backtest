"""H20.1 audits A-I and L (plan section 11). No outcome is read; no model is fitted.

  A determinism       two independent builds (separate processes) -> sha256 equality
  B PIT integrity     provenance availability <= t; vintages <= asof(t); windows end at t
  C transform PIT     H20_1_TRANSFORM_PIT_AUDIT.csv (features, classifiers, R3 candidates)
  D coverage          by feature x year, source, layer
  E zero vs missing   per feature; missing reasons
  F temporal drift    schema sets, denominators by era, classifier base rates, coverage by era
  G sparsity          nonzero/missing shares, quantiles, early vs late
  H redundancy        pairwise Spearman
  I semantic          scored by h20_1_semantic.py (read here if present)
  L lexicon vintage   earliest attestation of every dictionary term in the collected corpus

Writes H20_1_REPRESENTATION_METRICS.json, H20_1_TRANSFORM_PIT_AUDIT.csv and evidence/H20_1_*.csv.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_1_audit.py"
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime

import numpy as np
import pandas as pd

import h20_1_rep as rep
from h20_common import CA, DERIVED, EVIDENCE, INTERIM, ROOT, iso, now_utc, sha256_file, to_lf

IN = INTERIM / "h20_1"
BUILD = DERIVED / "h20_1"
SAMPLE = json.loads((CA / "H20_1_SAMPLE_FREEZE.json").read_text(encoding="utf-8"))
ERA = {**{y: "2018-20" for y in (2018, 2019, 2020)}, **{y: "2021-23" for y in (2021, 2022, 2023)},
       **{y: "2024-26" for y in (2024, 2025, 2026)}}
REG = pd.read_csv(CA / "CONTEXT_FEATURE_REGISTRY.csv")
FNAME = dict(zip(REG["feature_id"], REG["feature_name"]))
LAYER = dict(zip(REG["feature_id"], REG["context_layer"]))
FAMILY = dict(zip(REG["feature_id"], REG["representation_family"]))
SOURCES = dict(zip(REG["feature_id"], REG["source_ids"]))
OUTPUTS = ("features_long.csv", "features_wide.csv", "provenance.csv")


def r4(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 4)


# ---------------------------------------------------------------- A
def determinism() -> dict:
    py = sys.executable
    script = CA / "scripts" / "h20_1_build.py"
    res = {}
    for run in ("run1", "run2"):
        out = DERIVED / f"h20_1_det_{run}"
        subprocess.run([py, str(script), "--out", str(out)], check=True, cwd=str(ROOT), capture_output=True)
        res[run] = {f: sha256_file(out / f) for f in OUTPUTS}
    res["primary"] = {f: sha256_file(BUILD / f) for f in OUTPUTS}
    res["identical"] = res["run1"] == res["run2"] == res["primary"]
    return res


# ---------------------------------------------------------------- B
def pit(P: pd.DataFrame) -> dict:
    t = pd.to_datetime(P["t_utc"], utc=True)
    av = pd.to_datetime(P["public_availability_time"].replace("", None), utc=True)
    has = av.notna()
    viol = has & (av > t)
    by_type = P.assign(v=viol, h=has).groupby("record_type").agg(rows=("v", "size"), with_time=("h", "sum"),
                                                                 violations=("v", "sum"))
    # vintage dates against asof(t)
    vin = P[P["record_type"] == "VINTAGE"].copy()
    vin_viol = 0
    for r in vin.itertuples():
        vd = r.source_document_key.split("@")[1]
        tt = datetime.fromisoformat(r.t_utc.replace("Z", "+00:00"))
        lim = rep.alfred_asof(tt) if r.rule_id == "VINTAGE_ASOF_T" else rep.alfred_asof(tt - rep.W7)
        vin_viol += int(vd > lim.isoformat())
    w = P[P["window_hi"] != ""]
    post_t_window = int((pd.to_datetime(w["window_hi"], utc=True) > pd.to_datetime(w["t_utc"], utc=True)).sum())
    # rows that should carry a time but do not
    timed_types = {"DOCUMENT", "VINTAGE", "GDELT_FILE", "GDELT_RECORD", "WIKI_PAGE", "WIKI_ITEM"}
    untimed = int((P["record_type"].isin(timed_types) & ~has).sum())
    by_feature = P.assign(v=viol).groupby("feature_id")["v"].sum().astype(int).to_dict()
    return {"provenance_rows": int(len(P)), "rows_with_availability_time": int(has.sum()),
            "availability_after_t": int(viol.sum()), "vintage_date_after_asof": vin_viol,
            "window_end_after_t": post_t_window, "timed_record_types_missing_time": untimed,
            "violations_by_feature": by_feature,
            "by_record_type": {k: {c: int(v) for c, v in row.items()} for k, row in by_type.iterrows()},
            "total_violations": int(viol.sum()) + vin_viol + post_t_window + untimed}


# ---------------------------------------------------------------- provenance completeness (plan section 9)
def provenance_complete(V: pd.DataFrame, P: pd.DataFrame) -> dict:
    g = P.groupby(["sample_id", "feature_id"])
    kinds = g["record_type"].agg(lambda s: dict(s.value_counts()))
    files = P[P["record_type"] == "GDELT_FILE"].copy()
    files["records"] = files["detail"].str.extract(r"records=(\d+)").astype(float)
    den = files.groupby(["sample_id", "feature_id"])["records"].sum()
    bad, checked = [], 0
    for r in V[V["status"] != "MISSING"].itertuples():
        checked += 1
        k = kinds.get((r.sample_id, r.feature_id), {})
        unit = {"DOCUMENT": 0, "WIKI_ITEM": 0, "GDELT_RECORD": 0}
        n = sum(v for kk, v in k.items() if kk in unit)
        fam_val = float(r.value)
        f = r.feature_id
        ok = True
        if f in ("F06", "F08"):
            ok = k.get("VINTAGE", 0) == 1
        elif f == "F07":
            ok = k.get("VINTAGE", 0) == 1 and k.get("VINTAGE_OBS", 0) == 1
        elif f in ("F04", "F05"):
            ok = k.get("VINTAGE", 0) == 2
        elif f in ("F20", "F21"):
            d = den.get((r.sample_id, f), 0)
            need = rep.GDELT_MIN_SLICES * (2 if f == "F20" else 1)
            ok = d > 0 and abs(n / d - fam_val) < 1e-9 and k.get("GDELT_FILE", 0) >= need
        elif f == "F22":
            ok = n > 0 and k.get("GDELT_FILE", 0) == 14
        elif f in ("F03", "F18", "F24", "F25"):
            ok = (fam_val == 1 and n >= 1) or (fam_val == 0 and n == 0 and (k.get("EMPTY_WINDOW", 0) + k.get("WIKI_PAGE", 0) + k.get("PAGE_ABSENT_AT_T", 0)) >= 1)
        elif f == "F19":
            ok = n == fam_val and k.get("GDELT_FILE", 0) == 14
        elif f == "F23":
            ok = n == fam_val and (k.get("WIKI_PAGE", 0) + k.get("PAGE_ABSENT_AT_T", 0)) == 7
        else:
            ok = n == fam_val and (n > 0 or k.get("EMPTY_WINDOW", 0) == 1)
        if not ok:
            bad.append({"sample_id": r.sample_id, "feature_id": f, "value": r.value, "kinds": k})
    by_f = pd.Series([b["feature_id"] for b in bad], dtype=str).value_counts().to_dict()
    return {"values_checked": checked, "incomplete": len(bad), "completeness": 1 - len(bad) / checked if checked else None,
            "incomplete_by_feature": {f: int(by_f.get(f, 0)) for f in REG["feature_id"]},
            "incomplete_sample": [{k: str(v) for k, v in b.items()} for b in bad[:20]]}


# ---------------------------------------------------------------- C
def transform_audit() -> pd.DataFrame:
    rows = []
    for fid, name, layer, fam, src, win, defin, kls, zero, miss, just in rep.FEATURES:
        cls, why = just.split(":", 1)
        rows.append({"item_id": fid, "item_type": "FEATURE", "name": name, "family": fam, "layer": layer,
                     "transform": defin, "inputs": src, "document_time_pit": "BY_RULE; audit B",
                     "fitted_on_corpus": "no", "post_t_knowledge_route": "none identified", "class": cls,
                     "confirmatory_allowed": cls == "PIT_SAFE", "justification": why.strip()})
    kdef = {
        "K_CRYPTO": ("inherited H20.0 governance dictionary", "generic terms; single entity 'binance' existed from 2017-07"),
        "K_GDELT_CRYPTO": ("inherited H20.0 GDELT dictionary", "generic terms; single entity 'binance'"),
        "K_SEC_ENFORCEMENT": ("frozen H20.1 dictionary", "generic legal-action verbs; no entity"),
        "K_FOMC_TITLE": ("frozen H20.1 rule + publisher doc_type", "institutional term in use since 1990s"),
        "K_CRYPTO_STRESS": ("frozen H20.1 dictionary", "generic event words; no entity or event name"),
        "FR_FINREG": ("frozen agency list (publisher field)", "agency names existing before 2018"),
    }
    for k, (what, why) in kdef.items():
        rows.append({"item_id": k, "item_type": "CLASSIFIER", "name": k, "family": "R1/R2", "layer": "",
                     "transform": what, "inputs": "document titles / abstracts / items / GKG fields",
                     "document_time_pit": "n/a", "fitted_on_corpus": "no",
                     "post_t_knowledge_route": "hindsight vocabulary only; checked by lexicon audit L",
                     "class": "PIT_SAFE", "confirmatory_allowed": True, "justification": why})
    for cid, what, cls, why in rep.R3_CANDIDATES:
        rows.append({"item_id": cid, "item_type": "R3_CANDIDATE" + ("" if cid == "X07" else "_NOT_BUILT"),
                     "name": what, "family": "R3", "layer": "C1-C3", "transform": what, "inputs": "document text",
                     "document_time_pit": "inputs PIT-valid", "fitted_on_corpus": "yes" if cls != "PIT_SAFE" else "no (publisher-computed at t)",
                     "post_t_knowledge_route": why if cls != "PIT_SAFE" else "none identified", "class": cls,
                     "confirmatory_allowed": cls == "PIT_SAFE",
                     "justification": why + ("; recorded as NON_PIT_TRANSFORM_CANDIDATE" if cls == "NON_PIT" else "")})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- D, E, G
def values_tables(V: pd.DataFrame, S: pd.DataFrame):
    V = V.merge(S[["sample_id", "year", "era", "overlap"]], on="sample_id")
    V["nonmissing"] = V["status"] != "MISSING"
    cov_year = V.pivot_table(index="feature_id", columns="year", values="nonmissing", aggfunc="mean")
    per = []
    for fid in REG["feature_id"]:
        d = V[V["feature_id"] == fid]
        x = pd.to_numeric(d["value"], errors="coerce")
        nm = x.dropna()
        e = d[d["era"] == "2018-20"]
        late = d[d["era"] == "2024-26"]
        xe, xl = pd.to_numeric(e["value"], errors="coerce").dropna(), pd.to_numeric(late["value"], errors="coerce").dropna()
        per.append({
            "feature_id": fid, "feature_name": FNAME[fid], "layer": LAYER[fid], "family": FAMILY[fid],
            "n": len(d), "nonmissing_share": r4(d["nonmissing"].mean()),
            "years_with_value": int(d[d["nonmissing"]]["year"].nunique()),
            "missing_share": r4(1 - d["nonmissing"].mean()), "zero_share": r4((d["status"] == "ZERO").mean()),
            "nonzero_share_of_nonmissing": r4((nm != 0).mean()) if len(nm) else None,
            "distinct_values": int(nm.nunique()),
            "min": r4(nm.min()) if len(nm) else None, "p10": r4(nm.quantile(.1)) if len(nm) else None,
            "p50": r4(nm.median()) if len(nm) else None, "p90": r4(nm.quantile(.9)) if len(nm) else None,
            "max": r4(nm.max()) if len(nm) else None, "mean": r4(nm.mean()) if len(nm) else None,
            "early_2018_20_mean": r4(xe.mean()) if len(xe) else None, "late_2024_26_mean": r4(xl.mean()) if len(xl) else None,
            "early_nonzero_share": r4((xe != 0).mean()) if len(xe) else None,
            "late_nonzero_share": r4((xl != 0).mean()) if len(xl) else None,
            "early_nonmissing_share": r4(e["nonmissing"].mean()), "late_nonmissing_share": r4(late["nonmissing"].mean()),
            "nonoverlap_nonmissing_share": r4(d[~d["overlap"]]["nonmissing"].mean()),
            "nonoverlap_nonzero_share": r4((pd.to_numeric(d[~d["overlap"]]["value"], errors="coerce").dropna() != 0).mean()),
            "missing_reasons": json.dumps(d.loc[~d["nonmissing"], "missing_reason"].value_counts().to_dict()),
        })
    per = pd.DataFrame(per)
    src = []
    for s in sorted({x for v in REG["source_ids"] for x in v.split(";")}):
        fids = [f for f, v in SOURCES.items() if s in v.split(";")]
        d = V[V["feature_id"].isin(fids)]
        src.append({"source_id": s, "features": ";".join(fids), "nonmissing_share": r4(d["nonmissing"].mean()),
                    **{f"y{y}": r4(d[d["year"] == y]["nonmissing"].mean()) for y in range(2018, 2027)}})
    lay = V.assign(layer=V["feature_id"].map(LAYER)).groupby(["layer", "year"])["nonmissing"].mean().unstack().round(4)
    return per, cov_year.round(4), pd.DataFrame(src), lay


# ---------------------------------------------------------------- F
def drift(V: pd.DataFrame, S: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    out = {}
    fed = pd.read_parquet(IN / "fed.parquet")
    fed["y"] = pd.to_datetime(fed["public_availability_time"], utc=True).dt.year
    sets = {int(y): sorted(g["doc_type"].dropna().unique()) for y, g in fed[fed["y"].between(2017, 2026)].groupby("y")}
    out["fed_doc_type_sets"] = {"by_year": sets, "changed": len({tuple(v) for v in sets.values()}) > 1}
    fr = pd.read_parquet(IN / "fr.parquet")
    fr["y"] = pd.to_datetime(fr["publication_date"]).dt.year
    frs = {int(y): sorted(g["doc_type"].dropna().unique()) for y, g in fr.groupby("y")}
    out["fr_type_sets"] = {"by_year": frs, "changed": len({tuple(v) for v in frs.values()}) > 1}
    gf = pd.read_parquet(IN / "gdelt_files.parquet")
    ok = gf[gf["outcome"] == "OK"].drop_duplicates("file").copy()
    widths = {}
    for r in ok.itertuples():
        for w, n in json.loads(r.rows_by_width).items():
            widths[w] = widths.get(w, 0) + n
    ok["year"] = pd.to_datetime(ok["slice_utc"], utc=True).dt.year
    ok["era"] = ok["year"].map(ERA)
    out["gdelt_row_widths"] = {"total_by_width": widths, "short_row_share": round(sum(v for w, v in widths.items() if int(w) < 24) / max(1, sum(widths.values())), 6)}
    wp = pd.read_parquet(IN / "wiki_pages.parquet")
    wp["year"] = pd.to_datetime(wp["day"]).dt.year
    wp["era"] = wp["year"].map(ERA)
    okp = wp[wp["outcome"] == "OK"]
    out["wiki_pages"] = {"outcomes": wp["outcome"].value_counts().to_dict(),
                         "items_per_page_by_era": okp.groupby("era")["n_items"].mean().round(2).to_dict(),
                         "zero_item_pages_by_era": okp.assign(z=okp["n_items"] == 0).groupby("era")["z"].mean().round(4).to_dict(),
                         "items_per_line_by_era": (okp.groupby("era")["n_items"].sum() / okp.groupby("era")["n_lines"].sum()).round(4).to_dict()}
    # denominators per era
    W = V.merge(S[["sample_id", "era"]], on="sample_id")
    W["x"] = pd.to_numeric(W["value"], errors="coerce")
    den = {
        "fed_items_per_W7 (F01)": W[W["feature_id"] == "F01"].groupby("era")["x"].mean(),
        "sec_releases_per_W7 (F13)": W[W["feature_id"] == "F13"].groupby("era")["x"].mean(),
        "fedreg_finreg_docs_per_W7 (F09)": W[W["feature_id"] == "F09"].groupby("era")["x"].mean(),
        "fedreg_all_docs_per_month": fr.assign(era=fr["y"].map(ERA)).groupby(["era", "month"]).size().groupby("era").mean(),
        "cftc_releases_per_W30 (F17)": W[W["feature_id"] == "F17"].groupby("era")["x"].mean(),
        "gdelt_records_per_file_en": ok[ok["feed"] == "en"].groupby("era")["records"].mean(),
        "gdelt_records_per_file_translingual": ok[ok["feed"] == "translingual"].groupby("era")["records"].mean(),
        "wiki_items_per_page": okp.groupby("era")["n_items"].mean(),
    }
    dd = {}
    for k, s in den.items():
        s = s.dropna()
        dd[k] = {"by_era": s.round(3).to_dict(), "era_ratio": round(float(s.max() / s.min()), 3) if len(s) > 1 and s.min() > 0 else None}
    out["denominators"] = dd
    # classifier base rates by era
    sec = pd.read_parquet(IN / "sec.parquet")
    sec["era"] = pd.to_datetime(sec["public_availability_time"], utc=True).dt.year.map(ERA)
    fr["crypto"] = (fr["title"].fillna("") + " " + fr["abstract"].fillna("")).str.contains(rep.K_CRYPTO)
    it = pd.read_parquet(IN / "wiki_items.parquet")
    it["era"] = pd.to_datetime(it["day"]).dt.year.map(ERA)
    it["crypto"] = it["text"].str.contains(rep.K_CRYPTO)
    gtot = ok.groupby("era")["records"].sum()
    gcr = ok.groupby("era")["crypto_records"].sum()
    gtl = ok[ok["feed"] == "translingual"].groupby("era")
    gen = ok[ok["feed"] == "en"].groupby("era")
    out["classifier_base_rates_by_era"] = {
        "sec_crypto_share": sec.groupby("era")["title"].apply(lambda s: s.str.contains(rep.K_CRYPTO).mean()).round(4).to_dict(),
        "sec_enforcement_share": sec.groupby("era")["title"].apply(lambda s: s.str.contains(rep.K_SEC_ENFORCEMENT).mean()).round(4).to_dict(),
        "fedreg_crypto_share": fr.assign(era=fr["y"].map(ERA)).groupby("era")["crypto"].mean().round(5).to_dict(),
        "wiki_item_crypto_share": it.groupby("era")["crypto"].mean().round(5).to_dict(),
        "gdelt_crypto_share_all": (gcr / gtot).round(5).to_dict(),
        "gdelt_crypto_share_en": (gen["crypto_records"].sum() / gen["records"].sum()).round(5).to_dict(),
        "gdelt_crypto_share_translingual": (gtl["crypto_records"].sum() / gtl["records"].sum()).round(5).to_dict(),
        "gdelt_translingual_record_share": (gtl["records"].sum() / gtot).round(4).to_dict(),
    }
    W["nm"] = W["status"] != "MISSING"
    out["coverage_by_era"] = W.pivot_table(index="feature_id", columns="era", values="nm", aggfunc="mean").round(4).to_dict(orient="index")
    # per-feature drift flags under the frozen rule (ratio >= 2.0 or category-set change)
    feat_den = {"F01": "fed_items_per_W7 (F01)", "F02": "fed_items_per_W7 (F01)", "F03": "fed_items_per_W7 (F01)",
                "F16": "fed_items_per_W7 (F01)", "F09": "fedreg_all_docs_per_month", "F10": "fedreg_all_docs_per_month",
                "F11": "fedreg_all_docs_per_month", "F12": "fedreg_all_docs_per_month", "F13": "sec_releases_per_W7 (F13)",
                "F14": "sec_releases_per_W7 (F13)", "F15": "sec_releases_per_W7 (F13)", "F18": "sec_releases_per_W7 (F13)",
                "F17": "cftc_releases_per_W30 (F17)", "F19": "gdelt_records_per_file_translingual",
                "F20": "gdelt_records_per_file_translingual", "F21": "gdelt_records_per_file_en",
                "F22": "gdelt_records_per_file_translingual", "F23": "wiki_items_per_page", "F24": "wiki_items_per_page",
                "F25": "wiki_items_per_page"}
    cat = {"F02": out["fed_doc_type_sets"]["changed"], "F03": out["fed_doc_type_sets"]["changed"],
           "F16": out["fed_doc_type_sets"]["changed"], "F12": out["fr_type_sets"]["changed"]}
    rows = []
    for fid in REG["feature_id"]:
        k = feat_den.get(fid)
        ratio = dd[k]["era_ratio"] if k else None
        if fid in ("F19", "F20", "F22"):  # all-feed features: worst of the two feeds
            r2 = dd["gdelt_records_per_file_en"]["era_ratio"]
            ratio = max(x for x in (ratio, r2) if x is not None)
        flag = (ratio is not None and ratio >= 2.0) or bool(cat.get(fid, False))
        rows.append({"feature_id": fid, "denominator": k or "n/a (vintage values)", "denominator_era_ratio": ratio,
                     "category_set_changed": bool(cat.get(fid, False)), "DRIFT": flag})
    return out, pd.DataFrame(rows)


# ---------------------------------------------------------------- H
def redundancy(V: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    X = V.pivot(index="sample_id", columns="feature_id", values="value").apply(pd.to_numeric, errors="coerce")
    X = X[[f for f in REG["feature_id"] if f in X.columns]]
    pairs = []
    cols = list(X.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            d = X[[a, b]].dropna()
            if len(d) < 3 or d[a].nunique() < 2 or d[b].nunique() < 2:
                rho = None
            else:
                rho = float(d[a].rank().corr(d[b].rank()))
            pairs.append({"feature_a": a, "feature_b": b, "n_pairs": len(d), "spearman": r4(rho),
                          "redundant_rule": bool(rho is not None and abs(rho) >= 0.95 and len(d) >= 30)})
    P = pd.DataFrame(pairs)
    return P, P[P["redundant_rule"]][["feature_a", "feature_b", "spearman", "n_pairs"]].to_dict("records")


# ---------------------------------------------------------------- L
def lexicon(first_t: datetime) -> pd.DataFrame:
    fed = pd.read_parquet(IN / "fed.parquet")
    fr = pd.read_parquet(IN / "fr.parquet")
    sec = pd.read_parquet(IN / "sec.parquet")
    it = pd.read_parquet(IN / "wiki_items.parquet")
    gr = pd.read_parquet(IN / "gdelt_crypto_records.parquet")
    gf = pd.read_parquet(IN / "gdelt_files.parquet").drop_duplicates("file")[["file", "slice_utc"]]
    gr = gr.merge(gf, on="file")
    corpora = {
        "K_CRYPTO": [(pd.to_datetime(fed["public_availability_time"], utc=True), fed["title"]),
                     (pd.to_datetime(fr["public_availability_time"], utc=True), fr["title"].fillna("") + " " + fr["abstract"].fillna("")),
                     (pd.to_datetime(sec["public_availability_time"], utc=True), sec["title"]),
                     (pd.to_datetime(it["rev_utc"], utc=True), it["text"])],
        "K_GDELT_CRYPTO": [(pd.to_datetime(gr["slice_utc"], utc=True), gr["themes"] + " " + gr["orgs"] + " " + gr["allnames"] + " " + gr["url"])],
        "K_SEC_ENFORCEMENT": [(pd.to_datetime(sec["public_availability_time"], utc=True), sec["title"])],
        "K_CRYPTO_STRESS": [(pd.to_datetime(it["rev_utc"], utc=True), it["text"])],
    }
    rows = []
    for dic, terms in rep.LEXICON.items():
        for term in terms:
            rx = re.compile(term, re.I)
            first, n = None, 0
            for ts, txt in corpora[dic]:
                m = txt.fillna("").str.contains(rx)
                n += int(m.sum())
                if m.any():
                    f = ts[m].min()
                    first = f if first is None or f < first else first
            rows.append({"dictionary": dic, "term": term, "matches_in_corpus": n,
                         "earliest_attestation_utc": iso(first.to_pydatetime()) if first is not None else "",
                         "attested_by_first_sample_t": bool(first is not None and first <= pd.Timestamp(first_t)),
                         "named_entity": term in ("binance",)})
    return pd.DataFrame(rows)


def main() -> int:
    V = pd.read_csv(BUILD / "features_long.csv", dtype={"value": str}, keep_default_na=False)
    V["value"] = V["value"].replace("", np.nan)
    P = pd.read_csv(BUILD / "provenance.csv", dtype=str, keep_default_na=False)
    S = pd.DataFrame(SAMPLE["sample"])
    S["t"] = pd.to_datetime(S["t_utc"], utc=True)
    S["year"], S["overlap"] = S["t"].dt.year, S["w30_overlaps_h20_0_w30"]
    S["era"] = S["year"].map(ERA)

    A = determinism()
    B = pit(P)
    C = transform_audit()
    C.to_csv(CA / "H20_1_TRANSFORM_PIT_AUDIT.csv", index=False, lineterminator="\n")
    prov = provenance_complete(V, P)
    per, cov_year, src, lay = values_tables(V, S)
    F, drift_flags = drift(V, S)
    H_pairs, H_red = redundancy(V)
    L = lexicon(S["t"].min().to_pydatetime())
    # missing encoded as zero? (a MISSING status must have NaN value and a reason; a ZERO must have a value)
    mz = {"missing_with_value": int(((V["status"] == "MISSING") & V["value"].notna()).sum()),
          "missing_without_reason": int(((V["status"] == "MISSING") & (V["missing_reason"] == "")).sum()),
          "zero_without_value": int(((V["status"] == "ZERO") & V["value"].isna()).sum())}
    sem_p = EVIDENCE / "H20_1_SEMANTIC_AUDIT_SCORES.csv"
    sem = pd.read_csv(sem_p).to_dict("records") if sem_p.exists() else None

    per = per.merge(drift_flags, on="feature_id")
    per.to_csv(EVIDENCE / "H20_1_FEATURE_AUDIT.csv", index=False, lineterminator="\n")
    cov_year.to_csv(EVIDENCE / "H20_1_COVERAGE_BY_FEATURE_YEAR.csv", lineterminator="\n")
    src.to_csv(EVIDENCE / "H20_1_COVERAGE_BY_SOURCE_YEAR.csv", index=False, lineterminator="\n")
    lay.to_csv(EVIDENCE / "H20_1_COVERAGE_BY_LAYER_YEAR.csv", lineterminator="\n")
    H_pairs.to_csv(EVIDENCE / "H20_1_REDUNDANCY_PAIRS.csv", index=False, lineterminator="\n")
    L.to_csv(EVIDENCE / "H20_1_LEXICON_VINTAGE.csv", index=False, lineterminator="\n")
    inputs = {p.name: sha256_file(p) for p in sorted(IN.glob("*.parquet"))}
    metrics = {
        "experiment": "H20.1 Context Representation Feasibility", "computed_utc": iso(now_utc()),
        "representation_version": rep.REP_VERSION,
        "representation_freeze_sha256": json.loads((CA / "H20_1_REPRESENTATION_FREEZE.json").read_text(encoding="utf-8"))["freeze_sha256"],
        "sample_freeze_sha256": SAMPLE["freeze_sha256"], "n_timestamps": len(S),
        "n_nonoverlap_timestamps": int((~S["overlap"]).sum()), "n_features": int(len(REG)),
        "inputs_sha256": inputs, "build_outputs_sha256": A["primary"],
        "A_determinism": A, "B_pit_integrity": B, "provenance_completeness": prov,
        "C_transform_pit": {"items": int(len(C)), "classified": int(C["class"].isin(["PIT_SAFE", "NON_PIT", "UNRESOLVED"]).sum()),
                            "by_class": C.groupby(["item_type", "class"]).size().rename("n").reset_index().to_dict("records"),
                            "built_features_non_pit": C[(C["item_type"] == "FEATURE") & (C["class"] != "PIT_SAFE")]["item_id"].tolist()},
        "D_coverage": {"by_feature": per.set_index("feature_id")[["nonmissing_share", "years_with_value"]].to_dict(orient="index"),
                       "by_source": src.set_index("source_id")["nonmissing_share"].to_dict(),
                       "by_layer_year": lay.to_dict(orient="index")},
        "E_zero_vs_missing": {"encoding_checks": mz,
                              "by_feature": per.set_index("feature_id")[["zero_share", "missing_share", "missing_reasons"]].to_dict(orient="index")},
        "F_temporal_stability": F,
        "G_sparsity": per.set_index("feature_id")[["nonzero_share_of_nonmissing", "distinct_values", "p10", "p50", "p90",
                                                   "early_2018_20_mean", "late_2024_26_mean", "early_nonzero_share",
                                                   "late_nonzero_share"]].to_dict(orient="index"),
        "H_redundancy": {"pairs": int(len(H_pairs)), "redundant_pairs_rule": H_red},
        "I_semantic": sem,
        "L_lexicon": {"terms": int(len(L)), "not_attested_by_first_t": L[~L["attested_by_first_sample_t"]][["dictionary", "term", "earliest_attestation_utc", "matches_in_corpus"]].to_dict("records")},
        "outcome_tables_read": False, "returns_computed": False, "models_fitted": False,
    }
    mp = CA / "H20_1_REPRESENTATION_METRICS.json"
    mp.write_text(json.dumps(metrics, indent=1, default=str), encoding="utf-8")
    to_lf([mp, CA / "H20_1_TRANSFORM_PIT_AUDIT.csv", *EVIDENCE.glob("H20_1_*.csv")])
    print(json.dumps({"determinism": A["identical"], "pit_violations": B["total_violations"],
                      "provenance_completeness": prov["completeness"], "missing_encoding": mz,
                      "redundant": H_red}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
