"""H20.0 — GDELT 2.0 GKG slices (C1/C2/C3 news flow; C5 name mentions; language and link-rot audits).

For each sample timestamp t, the slice is the last 15-minute GKG file whose stamp is <= t - 15 min,
so the file had been published by t. Both the English and the translingual GKG files are taken.
A GKG record's availability is its slice stamp: GDELT is the observer, and the article was public no
later than GDELT saw it (CONTEXT_TIMESTAMP_SCHEMA.md section 3, `first_observed_time`).

Crypto relevance uses the fixed list of governance section 3. Raw zips are kept write-once.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_0_collect_gdelt.py"
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from datetime import datetime, timedelta

import pandas as pd

from h20_common import INTERIM, RAW, get, load_freeze, save_raw

csv.field_size_limit(2**31 - 1)
CRYPTO = re.compile(r"bitcoin|cryptocurrenc|crypto|blockchain|binance|stablecoin", re.I)
LANG = re.compile(r"srclc:([a-z]{2,3})")


def slice_for(t: datetime) -> datetime:
    s = t - timedelta(minutes=15)
    return s.replace(minute=(s.minute // 15) * 15, second=0, microsecond=0)


def main() -> int:
    rows, files = [], []
    for s in load_freeze()["sample"]:
        t = datetime.fromisoformat(s["t_utc"].replace("Z", "+00:00"))
        sl = slice_for(t)
        stamp = sl.strftime("%Y%m%d%H%M%S")
        for feed, suffix in (("en", "gkg.csv.zip"), ("translingual", "translation.gkg.csv.zip")):
            name = f"{stamp}.{suffix}"
            cached = list((RAW / "gdelt").glob(f"{name}_*"))
            if cached:
                content, outcome, sha = cached[0].read_bytes(), "OK", cached[0].name.rsplit("_", 1)[-1]
            else:
                r = get(f"http://data.gdeltproject.org/gdeltv2/{name}", purpose="gdelt:slice")
                content, outcome, sha = r.content, r.outcome, r.sha256[:12]
                if outcome == "OK":
                    save_raw("gdelt", f"{name}_{sha}", content)
            files.append({"sample_id": s["sample_id"], "slice_utc": sl, "feed": feed, "outcome": outcome,
                          "bytes": len(content) if outcome == "OK" else 0})
            if outcome != "OK":
                continue
            z = zipfile.ZipFile(io.BytesIO(content))
            text = z.read(z.namelist()[0]).decode("utf-8", "replace")
            n = 0
            for f in csv.reader(io.StringIO(text), delimiter="\t", quoting=csv.QUOTE_NONE):
                if len(f) < 24:
                    continue
                n += 1
                themes = f[7] + ";" + f[8]
                blob = " ".join((themes, f[13], f[23], f[4]))
                lang = LANG.search(f[25]) if len(f) > 25 else None
                rows.append(
                    {
                        "sample_id": s["sample_id"],
                        "slice_utc": sl,
                        "feed": feed,
                        "gkg_id": f[0],
                        "source_name": f[3],
                        "url": f[4],
                        "lang": lang.group(1) if lang else ("en" if feed == "en" else "und"),
                        "crypto": bool(CRYPTO.search(blob)),
                        "orgs": f[13][:2000],
                        "allnames": f[23][:4000],
                    }
                )
            files[-1]["records"] = n
        print(s["sample_id"], sl, flush=True)
    pd.DataFrame(files).to_parquet(INTERIM / "gdelt_files.parquet", index=False)
    D = pd.DataFrame(rows)
    D.to_parquet(INTERIM / "gdelt_records.parquet", index=False)
    print(D.groupby("feed")["crypto"].agg(["size", "sum"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
