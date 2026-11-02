"""H20.1 semantic audit (plan section 12): draw the audit sample, then score the annotations.

  --part draw    up to 30 positives and 20 negatives per classifier from documents in H20.1 windows
                 that are not H20.0 design documents (rng 20261102). Writes the annotation sheet
                 evidence/H20_1_SEMANTIC_AUDIT_SHEET.csv in shuffled order WITHOUT the classifier's
                 decision; the decision key goes to data/derived/h20_1/semantic_key.csv.
  --part score   joins evidence/H20_1_SEMANTIC_AUDIT_LABELS.csv (audit_id, label YES/NO/UNDETERMINABLE,
                 evidence_span, note) to the key; writes evidence/H20_1_SEMANTIC_AUDIT.csv (row level)
                 and evidence/H20_1_SEMANTIC_AUDIT_SCORES.csv (per classifier, against the frozen bar).

    .venv/Scripts/python "Contextual Alpha/scripts/h20_1_semantic.py" --part draw|score
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import zipfile
from datetime import datetime

import numpy as np
import pandas as pd

import h20_1_rep as rep
from h20_common import CA, DERIVED, EVIDENCE, INTERIM, RAW, to_lf

IN = INTERIM / "h20_1"
SEED = 20261102
N_POS, N_NEG = 30, 20
KEY = DERIVED / "h20_1" / "semantic_key.csv"
SHEET = EVIDENCE / "H20_1_SEMANTIC_AUDIT_SHEET.csv"
LABELS = EVIDENCE / "H20_1_SEMANTIC_AUDIT_LABELS.csv"
QUESTION = {
    "K1a": "CRYPTO: is this SEC press release about crypto-assets / blockchain digital assets?",
    "K1b": "CRYPTO: is this Federal Register document about crypto-assets / blockchain digital assets?",
    "K2": "ENFORCEMENT: does this SEC title announce an enforcement action or outcome?",
    "K3": "FOMC_STATEMENT: is this Fed release the FOMC policy statement / decision?",
    "K4": "CRYPTO: does this current-events item describe an event concerning crypto-assets?",
    "K5": "CRYPTO_STRESS: does this crypto item report a theft/hack, insolvency, failure/collapse, depeg, withdrawal halt, fraud charge or crash?",
    "K6": "CRYPTO: does this GDELT record (URL, organisations, names, themes) refer to an article about crypto-assets?",
}
csv.field_size_limit(2**31 - 1)


def stamps():
    j = json.loads((CA / "H20_1_SAMPLE_FREEZE.json").read_text(encoding="utf-8"))
    return [datetime.fromisoformat(s["t_utc"].replace("Z", "+00:00")) for s in j["sample"]]


def in_any(avail: pd.Series, w) -> pd.Series:
    a = pd.to_datetime(avail, utc=True)
    m = pd.Series(False, index=a.index)
    for t in stamps():
        m |= (a > t - w) & (a <= t)
    return m


def design_sets() -> dict:
    """Documents read while writing the dictionaries: everything in H20.0's W7 windows."""
    out = {}
    out["sec"] = set(pd.read_parquet(INTERIM / "sec_w7.parquet")["source_document_key"])
    out["fed"] = set(pd.read_parquet(INTERIM / "fed_w7.parquet")["source_document_key"])
    fr = pd.read_parquet(INTERIM / "fr_windows.parquet")
    out["fr"] = set(fr.loc[fr["in_w7"].fillna(False), "source_document_key"])
    out["wiki_days"] = set(pd.read_parquet(INTERIM / "wiki_portal.parquet")["day"])
    g0 = pd.read_parquet(INTERIM / "gdelt_files.parquet")
    stamp = pd.to_datetime(g0["slice_utc"], utc=True).dt.strftime("%Y%m%d%H%M%S")
    out["gdelt_files"] = set(stamp + np.where(g0["feed"] == "en", ".gkg.csv.zip", ".translation.gkg.csv.zip"))
    return out


def take(rng, df: pd.DataFrame, n: int) -> pd.DataFrame:
    df = df.sort_values("document_key", kind="mergesort").reset_index(drop=True)
    if len(df) <= n:
        return df
    return df.iloc[sorted(rng.choice(len(df), size=n, replace=False))]


def gdelt_negatives(rng, files: list[str], n: int, crypto_ids: set) -> pd.DataFrame:
    rows = []
    files = sorted(files)
    picks = rng.choice(len(files), size=n, replace=True)
    for i, fi in enumerate(picks):
        name = files[fi]
        p = sorted((RAW / "gdelt").glob(f"{name}_*"))[0]
        z = zipfile.ZipFile(p)
        text = z.read(z.namelist()[0]).decode("utf-8", "replace")
        recs = [f for f in csv.reader(io.StringIO(text), delimiter="\t", quoting=csv.QUOTE_NONE)
                if len(f) >= 24 and f[0] not in crypto_ids]
        f = recs[int(rng.integers(0, len(recs)))]
        rows.append({"document_key": f[0], "source_id": "S_GDELT_GKG", "decision": 0,
                     "text": f"URL: {f[4]} | ORGS: {f[13][:300]} | NAMES: {f[23][:400]} | THEMES: {(f[7] + ';' + f[8])[:400]}",
                     "file": name})
    return pd.DataFrame(rows)


def draw() -> int:
    if SHEET.exists():
        print("audit sheet exists; refusing to redraw")
        return 1
    rng = np.random.default_rng(SEED)
    ds = design_sets()
    parts = []
    sec = pd.read_parquet(IN / "sec.parquet")
    sec = sec[~sec["source_document_key"].isin(ds["sec"])]
    s30 = sec[in_any(sec["public_availability_time"], rep.W30)].assign(document_key=lambda d: d["source_document_key"], text=lambda d: d["title"])
    s30["decision"] = s30["title"].str.contains(rep.K_CRYPTO).astype(int)
    s7 = sec[in_any(sec["public_availability_time"], rep.W7)].assign(document_key=lambda d: d["source_document_key"], text=lambda d: d["title"])
    s7["decision"] = s7["title"].str.contains(rep.K_SEC_ENFORCEMENT).astype(int)
    fr = pd.read_parquet(IN / "fr.parquet")
    fr = fr[~fr["source_document_key"].isin(ds["fr"])]
    fr = fr[in_any(fr["public_availability_time"], rep.W30)].assign(
        document_key=lambda d: d["source_document_key"],
        text=lambda d: "TITLE: " + d["title"].fillna("") + " | ABSTRACT: " + d["abstract"].fillna("").str.slice(0, 700))
    fr["decision"] = (fr["title"].fillna("") + " " + fr["abstract"].fillna("")).str.contains(rep.K_CRYPTO).astype(int)
    fed = pd.read_parquet(IN / "fed.parquet")
    fed = fed[(fed["doc_type"] == rep.FOMC_DOC_TYPE) & ~fed["source_document_key"].isin(ds["fed"])]
    fed = fed[in_any(fed["public_availability_time"], rep.W7)].assign(document_key=lambda d: d["source_document_key"],
                                                                       text=lambda d: "[" + d["doc_type"] + "] " + d["title"])
    fed["decision"] = fed["title"].str.contains(rep.K_FOMC_TITLE).astype(int)
    it = pd.read_parquet(IN / "wiki_items.parquet")
    it = it[~it["day"].isin(ds["wiki_days"])].drop_duplicates(["revid", "item_idx"])
    it = it.assign(document_key=lambda d: d["revid"].astype(str) + "#" + d["item_idx"].astype(str), text=lambda d: d["text"].str.slice(0, 900))
    it["decision"] = it["text"].str.contains(rep.K_CRYPTO).astype(int)
    ic = it[it["decision"] == 1].copy()
    ic["decision"] = ic["text"].str.contains(rep.K_CRYPTO_STRESS).astype(int)
    for grp, D, src in (("K1a", s30, "S_SEC_PRESS"), ("K2", s7, "S_SEC_PRESS"), ("K1b", fr, "S_FEDREG"),
                        ("K3", fed, "S_FED_PRESS"), ("K4", it, "S_WIKI_PORTAL"), ("K5", ic, "S_WIKI_PORTAL")):
        D = D.drop_duplicates("document_key")
        for dec, n in ((1, N_POS), (0, N_NEG)):
            x = take(rng, D[D["decision"] == dec][["document_key", "text", "decision"]], n).assign(group=grp, source_id=src)
            parts.append(x)
        print(grp, "population pos", int((D["decision"] == 1).sum()), "neg", int((D["decision"] == 0).sum()))
    gr = pd.read_parquet(IN / "gdelt_crypto_records.parquet")
    gr = gr[~gr["file"].isin(ds["gdelt_files"])].drop_duplicates("gkg_id")
    gr = gr.assign(document_key=gr["gkg_id"], decision=1,
                   text="URL: " + gr["url"] + " | ORGS: " + gr["orgs"].str.slice(0, 300) + " | NAMES: "
                   + gr["allnames"].str.slice(0, 400) + " | THEMES: " + gr["themes"].str.slice(0, 400))
    parts.append(take(rng, gr[["document_key", "text", "decision"]], N_POS).assign(group="K6", source_id="S_GDELT_GKG"))
    gf = pd.read_parquet(IN / "gdelt_files.parquet")
    files = sorted(set(gf.loc[gf["outcome"] == "OK", "file"]) - ds["gdelt_files"])
    parts.append(gdelt_negatives(rng, files, N_NEG, set(gr["gkg_id"]))[["document_key", "text", "decision"]].assign(group="K6", source_id="S_GDELT_GKG"))
    print("K6 population pos", len(gr))
    A = pd.concat(parts, ignore_index=True)
    A = A.iloc[rng.permutation(len(A))].reset_index(drop=True)
    A["audit_id"] = [f"A{i + 1:04d}" for i in range(len(A))]
    A["question"] = A["group"].map(QUESTION)
    KEY.parent.mkdir(parents=True, exist_ok=True)
    A[["audit_id", "group", "source_id", "document_key", "decision"]].to_csv(KEY, index=False, lineterminator="\n")
    A[["audit_id", "group", "source_id", "document_key", "question", "text"]].to_csv(SHEET, index=False, lineterminator="\n")
    to_lf([SHEET])
    print("audit items", len(A), A.groupby(["group", "decision"]).size().to_dict())
    return 0


def score() -> int:
    K = pd.read_csv(KEY)
    L = pd.read_csv(LABELS)
    assert set(L["label"]) <= {"YES", "NO", "UNDETERMINABLE"}, set(L["label"])
    M = K.merge(L, on="audit_id", how="left", validate="one_to_one")
    assert M["label"].notna().all(), "unlabelled items"
    M.to_csv(EVIDENCE / "H20_1_SEMANTIC_AUDIT.csv", index=False, lineterminator="\n")
    rows = []
    for g, d in M.groupby("group"):
        pos, neg = d[d["decision"] == 1], d[d["decision"] == 0]
        pdet, ndet = pos[pos["label"] != "UNDETERMINABLE"], neg[neg["label"] != "UNDETERMINABLE"]
        prec = float((pdet["label"] == "YES").mean()) if len(pdet) else None
        nagr = float((ndet["label"] == "NO").mean()) if len(ndet) else None
        und = float((d["label"] == "UNDETERMINABLE").mean())
        ok = (prec is not None and prec >= 0.90 and len(pdet) >= 10 and nagr is not None and nagr >= 0.90
              and len(ndet) >= 10 and (g != "K6" or und <= 0.20))
        rows.append({"classifier": g, "n_pos": len(pos), "n_pos_determinable": len(pdet), "precision": prec,
                     "n_neg": len(neg), "n_neg_determinable": len(ndet), "negative_agreement": nagr,
                     "overall_agreement": float(((d["decision"] == 1) & (d["label"] == "YES") | (d["decision"] == 0) & (d["label"] == "NO")).sum() / max(1, (d["label"] != "UNDETERMINABLE").sum())),
                     "undeterminable_share": und, "meets_bar": bool(ok),
                     "false_positive_ids": ";".join(pos.loc[pos["label"] == "NO", "audit_id"]),
                     "false_negative_ids": ";".join(neg.loc[neg["label"] == "YES", "audit_id"])})
    S = pd.DataFrame(rows)
    S.to_csv(EVIDENCE / "H20_1_SEMANTIC_AUDIT_SCORES.csv", index=False, lineterminator="\n")
    to_lf([EVIDENCE / "H20_1_SEMANTIC_AUDIT.csv", EVIDENCE / "H20_1_SEMANTIC_AUDIT_SCORES.csv"])
    print(S.to_string())
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=["draw", "score"])
    raise SystemExit({"draw": draw, "score": score}[ap.parse_args().part]())
