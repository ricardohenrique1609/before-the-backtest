"""H20.3 P3 (seal X) and P4 (sealed target stage).

  --part seal_x   requires P1 and P2 PASS; joins X_market and the 18 context features by decision
                  time; writes data/derived/h20_3/X.parquet and H20_3_X_SEAL.json. Reads no outcome.
  --part target   THE ONLY READER OF THE LIFECYCLE TABLE. Refuses to run unless H20_3_X_SEAL.json
                  exists and every sealed file still matches. Builds y with the frozen rule, runs the
                  frozen target checks, writes data/derived/h20_3/y.parquet, H20_3_Y_SEAL.json and
                  H20_3_TARGET_AUDIT.json. X is never modified here.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_3_seal_target.py" --part seal_x|target
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

import h20_3_market as mk
from h20_3_common import CA, CAL, LCUV, OUT, ROOT, iso, now_utc, p0, sha256_file, spec, write_json

SEAL = "H20_3_X_SEAL.json"
SCRIPTS = ["scripts/h20_3_common.py", "scripts/h20_3_context.py", "scripts/h20_3_market.py", "scripts/h20_3_seal_target.py",
           "scripts/h20_1_rep.py", "scripts/h20_1_build.py", "scripts/h20_1_collect.py"]
CENSOR = pd.Timestamp("2026-10-09", tz="UTC")


def seal_x() -> int:
    p0()
    a1 = json.loads((OUT / "p1_audit.json").read_text(encoding="utf-8"))
    a2 = json.loads((OUT / "p2_audit.json").read_text(encoding="utf-8"))
    if not (a1["PASS"] and a2["PASS"]):
        raise SystemExit("P1/P2 not PASS - DATA / DESIGN FAILURE")
    sp = spec()
    ctx_feats = [e["feature_name"] for e in sp["context"]["CONTEXT_EXPANDED"]]
    core = sp["context"]["CONTEXT_CORE"]
    Xm = pd.read_parquet(OUT / "x_market.parquet")
    C = pd.read_csv(OUT / "context" / "features_wide.csv", keep_default_na=True)
    C["week"] = C["sample_id"].str[1:]
    X = Xm.merge(C[["week", *ctx_feats]], on="week", how="left", validate="many_to_one")
    assert len(X) == len(Xm)
    weeks_no_ctx = int(C[ctx_feats].isna().all(axis=1).sum())
    X.to_parquet(OUT / "X.parquet", index=False)
    mkt = a2["features"]
    arms = {"M0": mkt, "M1": ctx_feats, "M2": mkt + ctx_feats, "M1_core": core, "M2_core": mkt + core}
    files = {"data/derived/h20_3/X.parquet": OUT / "X.parquet", "data/derived/h20_3/x_market.parquet": OUT / "x_market.parquet",
             "data/derived/h20_3/context/features_long.csv": OUT / "context/features_long.csv",
             "data/derived/h20_3/context/features_wide.csv": OUT / "context/features_wide.csv",
             "data/derived/h20_3/context/provenance.csv": OUT / "context/provenance.csv",
             "data/derived/h20_3/landmark_calendar.json": CAL,
             "data/derived/h20_3/p1_audit.json": OUT / "p1_audit.json", "data/derived/h20_3/p2_audit.json": OUT / "p2_audit.json"}
    rec = {"stage": "P3", "sealed_utc": iso(now_utc()), "outcome_read_before_seal": False,
           "files": {k: sha256_file(v) for k, v in files.items()},
           "code": {s: sha256_file(CA / s) for s in SCRIPTS},
           "rows": int(len(X)), "rows_by_block": X["block"].value_counts().to_dict(), "asset_eras": int(X["asset_era_id"].nunique()),
           "decision_times": int(X["week"].nunique()), "context_weeks_with_every_feature_missing": weeks_no_ctx,
           "arms": {k: {"n_features": len(v), "features": v} for k, v in arms.items()},
           "route_state_mode": a2["route_state_mode"], "p1_PASS": a1["PASS"], "p2_PASS": a2["PASS"]}
    write_json(SEAL, rec)
    print(json.dumps({k: v for k, v in rec.items() if k not in ("arms", "files", "code")}, indent=1))
    return 0


def parse_strict(s: str) -> pd.Timestamp:
    s = s.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):  # date-only: public by the end of the UTC date (frozen rule)
        return pd.Timestamp(s, tz="UTC") + pd.Timedelta(hours=23, minutes=59, seconds=59)
    t = pd.to_datetime(s, format="ISO8601")  # raises on failure (strict; no coercion)
    return t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")


def target() -> int:
    p0()
    sealp = CA / SEAL
    if not sealp.exists():
        raise SystemExit("X is not sealed - refusing to open the outcome")
    seal = json.loads(sealp.read_text(encoding="utf-8"))
    for k, h in seal["files"].items():
        if sha256_file(ROOT / "Contextual Alpha" / k) != h:
            raise SystemExit(f"sealed file changed: {k} - DATA / DESIGN FAILURE")
    sp = spec()
    # ------------------------------------------------ the lifecycle table: opened here for the first time
    E = pq.read_table(ROOT / "H18_1B_FULL_DELIST_EVENTS.parquet",
                      columns=["full_delisting_event_id", "symbol", "announcement_public_time", "announcement_precision"]).to_pandas()
    parse_fail, times = [], []
    for v in E["announcement_public_time"]:
        try:
            times.append(parse_strict(str(v)))
        except (ValueError, TypeError):
            parse_fail.append(str(v))
            times.append(pd.NaT)
    E["A"] = times
    date_only = int(E["announcement_public_time"].astype(str).str.strip().str.fullmatch(r"\d{4}-\d{2}-\d{2}").sum())
    # eras, outcome-free, exactly as in X
    S, _R, _A = mk.load()
    S, ER = mk.eras(S)
    ER["era_start"] = pd.to_datetime(ER["era_start"]).dt.tz_localize("UTC")
    ER["era_end"] = pd.to_datetime(ER["era_end"]).dt.tz_localize("UTC")
    multi, none, att = [], [], []
    for r in E.itertuples():
        if pd.isna(r.A):
            continue
        m = ER[(ER["base_asset"] == r.symbol) & (ER["era_start"] <= r.A) & (r.A <= ER["era_end"] + pd.Timedelta(days=30))]
        if len(m) > 1:
            multi.append(r.full_delisting_event_id)
        elif len(m) == 0:
            none.append(r.symbol)
        else:
            att.append({"asset_era_id": m["asset_era_id"].iloc[0], "A": r.A, "event_id": r.full_delisting_event_id})
    T = pd.DataFrame(att).sort_values(["asset_era_id", "A"])
    first = T.groupby("asset_era_id")["A"].min()  # inherited: the era's first announcement
    X = pd.read_parquet(CA / "data/derived/h20_3/X.parquet", columns=["asset_era_id", "week", "t_utc", "block"])
    X["t"] = pd.to_datetime(X["t_utc"], utc=True)
    X["A"] = X["asset_era_id"].map(first)
    X["already_announced"] = X["A"].notna() & (X["A"] <= X["t"])
    X["in_risk_set"] = ~X["already_announced"]
    X["y"] = (X["A"].notna() & (X["A"] > X["t"]) & (X["A"] <= X["t"] + pd.Timedelta(days=365))).astype(int)
    X.loc[~X["in_risk_set"], "y"] = 0
    followup_incomplete = int((X["t"] + pd.Timedelta(days=365) > CENSOR).sum())
    Y = X[["asset_era_id", "week", "block", "in_risk_set", "y"]].copy()
    Y["announcement_time"] = X["A"].astype(str)
    Y.to_parquet(OUT / "y.parquet", index=False)
    y_hash = sha256_file(OUT / "y.parquet")
    write_json("H20_3_Y_SEAL.json", {"stage": "P4", "sealed_utc": iso(now_utc()), "y_parquet_sha256": y_hash,
                                     "x_seal_sha256": sha256_file(sealp), "rows": int(len(Y)),
                                     "in_risk_set_rows": int(Y["in_risk_set"].sum()), "code": sha256_file(CA / "scripts/h20_3_seal_target.py")})
    # ------------------------------------------------ checks and accounting (after y is hashed)
    R = Y[Y["in_risk_set"]]
    folds = sp["split"]["folds"]

    def units(d: pd.DataFrame) -> dict:
        return {"rows": int(len(d)), "asset_eras": int(d["asset_era_id"].nunique()), "weeks": int(d["week"].nunique()),
                "positive_rows": int(d["y"].sum()), "unique_positive_events": int(d.loc[d["y"] == 1, "asset_era_id"].nunique()),
                "base_rate": round(float(d["y"].mean()), 5) if len(d) else None}

    fold_units = []
    for f in folds:
        te = R[(R["week"] >= f["test_from"]) & (R["week"] <= f["test_to"])]
        tr = R[(R["week"] >= f["train_from"]) & (R["week"] <= f["train_to"])]
        fold_units.append({"fold": f["fold"], "train": units(tr), "test": units(te),
                           "shared_events": len(set(tr.loc[tr["y"] == 1, "asset_era_id"]) & set(te.loc[te["y"] == 1, "asset_era_id"]))})
    lcuv = units(R[R["block"] == LCUV])
    dev = units(R[R["block"] == "DEVELOPMENT"])
    H = pq.read_table(ROOT / "data/raw/h18_3/landmarks_pit.parquet", columns=["asset_era_id", "week", "y_365"]).to_pandas()
    H["week"] = pd.to_datetime(H["week"]).dt.date.astype(str)
    J = R.merge(H, on=["asset_era_id", "week"], how="inner")
    agree = float((J["y"] == J["y_365"].astype(int)).mean()) if len(J) else None
    checks = {
        "P4.1_unparsable_announcement_times": len(parse_fail),
        "P4.1_date_only_values": date_only,
        "P4.2_events_matching_more_than_one_era": len(multi),
        "P4.2_events_matching_no_era": sorted(set(none)),
        "P4.3_landmarks_with_announcement_le_t_remaining": int((X["in_risk_set"] & X["A"].notna() & (X["A"] <= X["t"])).sum()),
        "P4.4_followup_incomplete_landmarks": followup_incomplete,
        "P4.5_agreement_with_inherited_y_365": round(agree, 5) if agree is not None else None,
        "P4.5_matched_rows": int(len(J)), "P4.5_rows_differing": int((J["y"] != J["y_365"].astype(int)).sum()),
        "excluded_already_announced_rows": int(X["already_announced"].sum()),
    }
    floors = {"min_fold_test_events": min(u["test"]["unique_positive_events"] for u in fold_units), "fold_floor": 5,
              "lcuv_events": lcuv["unique_positive_events"], "lcuv_floor": 20}
    passed = (checks["P4.1_unparsable_announcement_times"] == 0 and checks["P4.2_events_matching_more_than_one_era"] == 0
              and checks["P4.3_landmarks_with_announcement_le_t_remaining"] == 0 and checks["P4.4_followup_incomplete_landmarks"] == 0)
    floors_ok = floors["min_fold_test_events"] >= 5 and floors["lcuv_events"] >= 20
    write_json("H20_3_TARGET_AUDIT.json", {
        "stage": "P4", "computed_utc": iso(now_utc()), "PASS": passed, "sample_floors_PASS": floors_ok, "checks": checks,
        "floors": floors, "events_in_table": int(len(E)), "events_attached_to_an_era": int(len(T)),
        "asset_eras_with_an_event": int(T["asset_era_id"].nunique()),
        "effective_units": {"DEVELOPMENT": dev, LCUV: lcuv, "folds": fold_units},
        "rule": sp["split"]["target"]["definition"], "y_parquet_sha256": y_hash,
    })
    print(json.dumps({"PASS": passed, "floors_PASS": floors_ok, **{k: v for k, v in checks.items()}, "dev": dev, "lcuv": lcuv},
                     indent=1, default=str))
    return 0 if (passed and floors_ok) else 3


if __name__ == "__main__":
    part = sys.argv[sys.argv.index("--part") + 1]
    sys.exit({"seal_x": seal_x, "target": target}[part]())
