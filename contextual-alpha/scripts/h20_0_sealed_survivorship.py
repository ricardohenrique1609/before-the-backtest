"""H20.0 — SEALED source-survivorship audit (plan section 7; governance section 6).

The only H20.0 stage that reads a lifecycle flag. It refuses to run unless every file hashed in
manifests/H20_0_PRE_SEAL_HASHES.json is present and unchanged, so nothing it reads can have shaped
sampling, source choice, collection or classification, which are all finished by then.

It reads exactly one column of the lifecycle layer: whether a base asset had any Binance spot symbol
live at the 2026-10 harvest (inheritance A6). It compares C5 coverage between still-listed and
no-longer-listed assets and writes aggregates only. Its only effect on the gate is the pre-registered
severe-bias downgrade (PASS -> CONDITIONAL); it can never upgrade a layer.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_sealed_survivorship.py"
"""

from __future__ import annotations

import json
import sys

import pandas as pd
import pyarrow.parquet as pq

from h20_common import CA, EVIDENCE, MANIFESTS, ROOT, iso, now_utc, sha256_file, to_lf

SEAL = MANIFESTS / "H20_0_PRE_SEAL_HASHES.json"
FLAG_SRC = ROOT / "data/raw/h18_2/spot_symbols.parquet"


def verify_seal() -> dict:
    if not SEAL.exists():
        sys.exit("REFUSED: no pre-seal hash manifest; run h20_0_audit.py first")
    seal = json.loads(SEAL.read_text())
    bad = [f for f, h in seal["files"].items() if not (CA / f).exists() or sha256_file(CA / f) != h]
    if bad:
        sys.exit(f"REFUSED: {len(bad)} sealed files changed or missing: {bad[:5]}")
    return seal


def rate(df: pd.DataFrame, col: str) -> float:
    return float(df[col].mean()) if len(df) else float("nan")


def main() -> int:
    seal = verify_seal()
    flag = pq.read_table(FLAG_SRC, columns=["base_asset", "is_live_now"]).to_pandas()
    live = flag.groupby("base_asset")["is_live_now"].any()
    C5 = pd.read_csv(EVIDENCE / "H20_0_C5_ASSET_COVERAGE.csv")
    C5["listed_now"] = C5["asset_ticker"].map(live)
    C5["name_resolved"] = C5["name_status_v2"] == "RESOLVED"
    C5["wiki_pit_article"] = C5["wiki_status"] == "PIT_ARTICLE"
    rows = []
    for col in ("any_asset_doc_w30", "non_venue_doc_w30", "name_resolved", "wiki_pit_article"):
        a = rate(C5[C5["listed_now"] == False], col)  # noqa: E712
        b = rate(C5[C5["listed_now"] == True], col)  # noqa: E712
        ratio = b / a if a else (float("inf") if b else 1.0)
        gap = (b - a) * 100
        severe = bool((max(ratio, 1 / ratio if ratio else float("inf")) >= 3) or abs(gap) >= 30)
        rows.append({"metric": col, "no_longer_listed": a, "still_listed": b, "ratio_listed_over_removed": ratio,
                     "gap_pp": gap, "severe": severe})
    R = pd.DataFrame(rows)
    out = {
        "computed_utc": iso(now_utc()),
        "seal_verified": True,
        "seal_written_utc": seal["written_utc"],
        "flag_source": {"path": str(FLAG_SRC.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(FLAG_SRC),
                        "column": "is_live_now (any symbol of the base asset)", "as_of": "2026-10 harvest (H18.2)"},
        "units": int(len(C5)),
        "units_no_longer_listed": int((C5["listed_now"] == False).sum()),  # noqa: E712
        "units_still_listed": int((C5["listed_now"] == True).sum()),  # noqa: E712
        "units_flag_missing": int(C5["listed_now"].isna().sum()),
        "caveat": "ticker-level flag; no sampled ticker has a later era (ticker_era_conflict = 0), so the join "
                  "does not splice two assets. The flag is coarse: it says nothing about why an asset left.",
        "comparisons": R.to_dict(orient="records"),
    }
    (EVIDENCE / "H20_0_SEALED_SURVIVORSHIP.json").write_text(json.dumps(out, indent=1, default=str))
    # pre-registered effect on the gate: downgrade only
    gp = CA / "H20_0_GATE.json"
    gate = json.loads(gp.read_text())
    sev = R.loc[R["severe"], "metric"].tolist()
    c5 = gate["layers"]["C5"]
    c5["severe_bias"] = sorted(set(c5["severe_bias"]) | {f"survivorship_{m}" for m in sev})
    if c5["layer_verdict"] == "PASS" and sev:
        c5["layer_verdict"] = "CONDITIONAL"
    gate["survivorship_audit"] = {"file": "evidence/H20_0_SEALED_SURVIVORSHIP.json", "severe": sev,
                                  "pre_seal_gate_sha256": seal["files"].get("H20_0_GATE.json")}
    gp.write_text(json.dumps(gate, indent=1, default=str))
    to_lf([gp, EVIDENCE / "H20_0_SEALED_SURVIVORSHIP.json"])
    print(R.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
