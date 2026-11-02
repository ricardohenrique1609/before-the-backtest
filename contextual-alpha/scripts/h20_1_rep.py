"""H20.1 representation rules, version h20_1_rep_v1 — FROZEN (sha256 in H20_1_REPRESENTATION_FREEZE.json).

Everything that decides what a feature value means lives here: dictionaries, publisher-category
rules, time rules, windows, and the feature registry. The build script only moves data through these
rules. A change to this file after the freeze is a deviation (H20_1_EXECUTION_DEVIATIONS.md).

No outcome is referenced. No model is fitted. No parameter depends on any document.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

REP_VERSION = "h20_1_rep_v1"
ET = ZoneInfo("America/New_York")

# ------------------------------------------------------------------ dictionaries (plan section 7)
# inherited unchanged from CONTEXT_RETRIEVAL_GOVERNANCE.md section 3 (listing-surface crypto tag)
K_CRYPTO = re.compile(
    r"crypto|digital asset|virtual currenc|bitcoin|stablecoin|blockchain|token|coin offering|binance|\bether\b",
    re.I,
)
# inherited unchanged from h20_0_collect_gdelt.py (GKG crypto tag)
K_GDELT_CRYPTO = re.compile(r"bitcoin|cryptocurrenc|crypto|blockchain|binance|stablecoin", re.I)
K_SEC_ENFORCEMENT = re.compile(
    r"\bcharg(?:e|es|ed|ing)\b|\bsettle(?:s|d|ment|ments)?\b|\bto pay\b|\bpenalt|\bjudgment|asset freeze"
    r"|\bhalts?\b|\bfraud|trading suspension|suspends trading|\bbar(?:s|red)?\b|\bsanction",
    re.I,
)
K_FOMC_TITLE = re.compile(r"\bFOMC statement\b", re.I)
FOMC_DOC_TYPE = "Monetary Policy"
K_CRYPTO_STRESS = re.compile(
    r"\bhack|\bstolen\b|\btheft\b|\bexploit|insolven|bankrupt|\bcollaps|de-?peg"
    r"|(?:halt|suspend|freez)\w* (?:all )?withdrawals|\bfraud|\bponzi\b|\bcrash",
    re.I,
)
FR_FINREG = frozenset(
    {
        "Securities and Exchange Commission",
        "Commodity Futures Trading Commission",
        "Federal Reserve System",
        "Federal Deposit Insurance Corporation",
        "Comptroller of the Currency",
        "Treasury Department",
        "Financial Crimes Enforcement Network",
        "Foreign Assets Control Office",
        "Consumer Financial Protection Bureau",
    }
)
FR_RULEMAKING = frozenset({"Rule", "Proposed Rule"})
FED_MONETARY = "Monetary Policy"
FED_ENFORCEMENT = "Enforcement Actions"
ALFRED_SERIES = ("CPIAUCSL", "UNRATE", "DFF")

# terms of each dictionary, for the lexicon-vintage audit (plan section 11 L)
LEXICON = {
    "K_CRYPTO": ["crypto", "digital asset", "virtual currenc", "bitcoin", "stablecoin", "blockchain", "token",
                 "coin offering", "binance", r"\bether\b"],
    "K_GDELT_CRYPTO": ["bitcoin", "cryptocurrenc", "crypto", "blockchain", "binance", "stablecoin"],
    "K_SEC_ENFORCEMENT": [r"\bcharg(?:e|es|ed|ing)\b", r"\bsettle(?:s|d|ment|ments)?\b", r"\bto pay\b", r"\bpenalt",
                          r"\bjudgment", "asset freeze", r"\bhalts?\b", r"\bfraud", "trading suspension",
                          "suspends trading", r"\bbar(?:s|red)?\b", r"\bsanction"],
    "K_CRYPTO_STRESS": [r"\bhack", r"\bstolen\b", r"\btheft\b", r"\bexploit", "insolven", "bankrupt", r"\bcollaps",
                        "de-?peg", r"(?:halt|suspend|freez)\w* (?:all )?withdrawals", r"\bfraud", r"\bponzi\b", r"\bcrash"],
}

# ------------------------------------------------------------------ time rules (plan section 6)
W7 = timedelta(days=7)
W30 = timedelta(days=30)
GDELT_SLICES = 7
GDELT_MIN_SLICES = 4
GDELT_PUBLISH_LAG = timedelta(minutes=15)
CFTC_WALKED = (  # spans walked in H20.0 before HTTP 429 (H20_0_EXECUTION_DEVIATION.md D2, D7)
    (datetime(2018, 1, 25, 19, 57, 6, tzinfo=UTC), datetime(2019, 1, 1, tzinfo=UTC)),
    (datetime(2019, 1, 29, 17, 36, 5, tzinfo=UTC), datetime(2020, 1, 1, tzinfo=UTC)),
    (datetime(2020, 1, 8, 20, 25, 16, tzinfo=UTC), datetime(2021, 1, 1, tzinfo=UTC)),
    (datetime(2021, 9, 30, 21, 38, 58, tzinfo=UTC), datetime(2022, 1, 1, tzinfo=UTC)),
)


def day_end_et(d: date) -> datetime:
    """T2 rule: a day-only document is admissible from the next ET midnight."""
    return datetime(d.year, d.month, d.day, tzinfo=ET).astimezone(UTC) + timedelta(days=1)


def alfred_asof(t: datetime) -> date:
    """Latest admissible vintage date: a vintage dated D is public from the ET midnight ending D."""
    return t.astimezone(ET).date() - timedelta(days=1)


def in_window(avail: datetime, t: datetime, w: timedelta) -> bool:
    return t - w < avail <= t


def gdelt_slices(t: datetime) -> list[datetime]:
    """S7: the slice published by t at the same time of day on each of the 7 days ending at t."""
    out = []
    for k in range(GDELT_SLICES):
        s = t - timedelta(days=k) - GDELT_PUBLISH_LAG
        out.append(s.replace(minute=(s.minute // 15) * 15, second=0, microsecond=0))
    return out


def wiki_days(t: datetime) -> list[date]:
    """D7: the seven UTC day pages ending with date(t)."""
    d = t.astimezone(UTC).date()
    return [d - timedelta(days=k) for k in range(6, -1, -1)]


def cftc_walked(lo: datetime, hi: datetime) -> bool:
    return any(a <= lo and hi < b for a, b in CFTC_WALKED)


def wiki_items(text: str) -> list[str]:
    return [ln for ln in (text or "").splitlines() if ln.startswith("*")]


# ------------------------------------------------------------------ feature registry (plan section 7)
PIT_SAFE_COUNT = (
    "PIT_SAFE: count of documents selected by publisher metadata and fixed rules; no parameter "
    "depends on any document; inputs admitted by public_availability_time <= t"
)
PIT_SAFE_DICT = (
    "PIT_SAFE: fixed dictionary of generic terms written before evaluation (inherited unchanged from "
    "H20.0 governance or frozen here); no fitted parameter; no named post-t entity"
)
PIT_SAFE_VINTAGE = (
    "PIT_SAFE: fixed arithmetic on the ALFRED vintage in force at asof(t); no revised data, no "
    "parameter estimated from data"
)
PIT_SAFE_GDELT = (
    "PIT_SAFE: GDELT GKG fields are written into the 15-minute slice file by GDELT at ingest time "
    "(the file is immutable), so they carry no post-t knowledge; tag is the inherited fixed dictionary"
)

FEATURES = [
    # id, name, layer, family, sources, window, definition, classifiers, zero, missing, pit justification
    ("F01", "c1_fed_release_count_W7", "C1", "R2", "S_FED_PRESS", "W7",
     "Fed press-release feed items with public_availability_time in (t-7d, t]", "",
     "feed span covers the window and no item is available in it", "OUT_OF_SOURCE_SPAN", PIT_SAFE_COUNT),
    ("F02", "c1_fed_monetary_policy_count_W30", "C1", "R2", "S_FED_PRESS", "W30",
     "Fed feed items with publisher doc_type 'Monetary Policy' in (t-30d, t]", "",
     "no Monetary Policy item in the window", "OUT_OF_SOURCE_SPAN", PIT_SAFE_COUNT),
    ("F03", "c1_fomc_statement_flag_W7", "C1", "R1", "S_FED_PRESS", "W7",
     "1 if >=1 Fed feed item in W7 has doc_type 'Monetary Policy' and title matching K_FOMC_TITLE", "K3",
     "no matching item in the window", "OUT_OF_SOURCE_SPAN", PIT_SAFE_DICT),
    ("F04", "c1_cpi_release_flag_W7", "C1", "R1", "S_ALFRED", "W7",
     "1 if last CPIAUCSL observation date in vintage asof(t) is later than in vintage asof(t-7d)", "",
     "no new observation between the two vintages", "FETCH_FAILED", PIT_SAFE_VINTAGE),
    ("F05", "c1_unrate_release_flag_W7", "C1", "R1", "S_ALFRED", "W7",
     "1 if last UNRATE observation date in vintage asof(t) is later than in vintage asof(t-7d)", "",
     "no new observation between the two vintages", "FETCH_FAILED", PIT_SAFE_VINTAGE),
    ("F06", "c1_policy_rate_asof", "C1", "R4", "S_ALFRED", "asof",
     "last DFF value (percent) in vintage asof(t)", "",
     "a value of 0 is a real rate level, not an absence", "FETCH_FAILED", PIT_SAFE_VINTAGE),
    ("F07", "c1_cpi_yoy_asof", "C1", "R4", "S_ALFRED", "asof",
     "100 * (last CPIAUCSL value / value 12 months earlier - 1) within vintage asof(t)", "",
     "a value of 0 is a real rate, not an absence", "FETCH_FAILED", PIT_SAFE_VINTAGE),
    ("F08", "c1_unrate_asof", "C1", "R4", "S_ALFRED", "asof",
     "last UNRATE value (percent) in vintage asof(t)", "",
     "not applicable (level)", "FETCH_FAILED", PIT_SAFE_VINTAGE),
    ("F09", "c2_fedreg_finreg_doc_count_W7", "C2", "R2", "S_FEDREG", "W7",
     "Federal Register documents with >=1 agency in FR_FINREG, available in W7 (day-end ET)", "",
     "all pages of the window fetched and none qualifies", "FETCH_FAILED", PIT_SAFE_COUNT),
    ("F10", "c2_fedreg_crypto_doc_count_W7", "C2", "R2", "S_FEDREG", "W7",
     "Federal Register documents whose title or abstract matches K_CRYPTO, available in W7", "K1b",
     "all pages fetched and none matches", "FETCH_FAILED", PIT_SAFE_DICT),
    ("F11", "c2_fedreg_crypto_doc_count_W30", "C2", "R2", "S_FEDREG", "W30",
     "Federal Register documents whose title or abstract matches K_CRYPTO, available in W30", "K1b",
     "all pages fetched and none matches", "FETCH_FAILED", PIT_SAFE_DICT),
    ("F12", "c2_fedreg_crypto_rulemaking_count_W30", "C2", "R2", "S_FEDREG", "W30",
     "F11 documents whose publisher type is Rule or Proposed Rule", "K1b",
     "all pages fetched and none matches", "FETCH_FAILED", PIT_SAFE_DICT),
    ("F13", "c2_sec_press_count_W7", "C2", "R2", "S_SEC_PRESS", "W7",
     "SEC press releases with listing stamp in W7", "",
     "all touching months walked and none in window", "FETCH_FAILED", PIT_SAFE_COUNT),
    ("F14", "c2_sec_enforcement_count_W7", "C2", "R2", "S_SEC_PRESS", "W7",
     "SEC press releases in W7 whose title matches K_SEC_ENFORCEMENT", "K2",
     "all touching months walked and none matches", "FETCH_FAILED", PIT_SAFE_DICT),
    ("F15", "c2_sec_crypto_press_count_W30", "C2", "R2", "S_SEC_PRESS", "W30",
     "SEC press releases in W30 whose title matches K_CRYPTO", "K1a",
     "all touching months walked and none matches", "FETCH_FAILED", PIT_SAFE_DICT),
    ("F16", "c2_fed_enforcement_count_W30", "C2", "R2", "S_FED_PRESS", "W30",
     "Fed feed items with publisher doc_type 'Enforcement Actions' in W30", "",
     "no such item in the window", "OUT_OF_SOURCE_SPAN", PIT_SAFE_COUNT),
    ("F17", "c2_cftc_press_count_W30", "C2", "R2", "S_CFTC_PRESS", "W30",
     "CFTC press releases with stamp in W30, from listing pages received in H20.0 only", "",
     "window inside a walked span and no release in it", "NOT_WALKED / ACCESS_BLOCKED", PIT_SAFE_COUNT),
    ("F18", "c2_crypto_regulatory_action_flag_W7", "C2", "R1", "S_FEDREG;S_SEC_PRESS", "W7",
     "1 if F10 + (SEC press releases in W7 matching K_CRYPTO) >= 1", "K1a;K1b",
     "both components available and both zero", "COMPONENT_MISSING", PIT_SAFE_DICT),
    ("F19", "c3_gdelt_crypto_record_count_S7", "C3", "R2", "S_GDELT_GKG", "S7",
     "GKG records matching K_GDELT_CRYPTO in the 14 S7 files (7 slices x English + translingual)", "K6",
     "all 14 files OK and no record matches", "FILE_MISSING", PIT_SAFE_GDELT),
    ("F20", "c3_gdelt_crypto_record_share_S7", "C3", "R2", "S_GDELT_GKG", "S7",
     "K_GDELT_CRYPTO records / all records over the S7 slices with both files OK", "K6",
     "share 0: slices available and no record matches", "INSUFFICIENT_SLICES (<4 of 7)", PIT_SAFE_GDELT),
    ("F21", "c3_gdelt_crypto_record_share_en_S7", "C3", "R2", "S_GDELT_GKG", "S7",
     "same as F20 over the English files only", "K6",
     "share 0: English files available and no record matches", "INSUFFICIENT_SLICES (<4 of 7)", PIT_SAFE_GDELT),
    ("F22", "c3_gdelt_crypto_tone_mean_S7", "C3", "R3", "S_GDELT_GKG", "S7",
     "mean of GDELT V2Tone first component over the S7 K_GDELT_CRYPTO records", "K6",
     "not applicable: a tone of 0 is a value; no records means UNDEFINED, not 0",
     "FILE_MISSING / UNDEFINED_NO_RECORDS", PIT_SAFE_GDELT),
    ("F23", "c3_wiki_crypto_item_count_D7", "C3", "R2", "S_WIKI_PORTAL", "D7",
     "Current-events items (lines starting '*') matching K_CRYPTO in the 7 day pages, each at its revision current at t",
     "K4", "pages fetched (or absent at t) and no item matches", "FETCH_FAILED", PIT_SAFE_DICT),
    ("F24", "c3_wiki_crypto_item_flag_D7", "C3", "R1", "S_WIKI_PORTAL", "D7",
     "1 if F23 >= 1", "K4", "F23 == 0", "FETCH_FAILED", PIT_SAFE_DICT),
    ("F25", "c3_crypto_stress_flag_D7", "C3", "R1", "S_WIKI_PORTAL", "D7",
     "1 if >=1 D7 item matches K_CRYPTO and K_CRYPTO_STRESS", "K4;K5",
     "no item matches both", "FETCH_FAILED", PIT_SAFE_DICT),
]
FEATURE_NAMES = [f[1] for f in FEATURES]

# R3 candidates assessed and not built (plan section 4); classification is part of the freeze
R3_CANDIDATES = [
    ("X01", "current LLM extraction / event labelling (e.g. Claude, GPT, Gemini) of historical documents",
     "NON_PIT", "model parameters trained on corpora extending past every sample t (2018-2026); can encode "
     "knowledge of later events, names and outcomes; NON_PIT_TRANSFORM_CANDIDATE only"),
    ("X02", "current sentence-embedding models (e.g. MiniLM 2021, text-embedding-3 2024) of document text",
     "NON_PIT", "training corpora post-date most or all sample t; representation geometry reflects post-t usage"),
    ("X03", "TF-IDF / topic model / vocabulary fitted on the full 2018-2026 collected corpus",
     "NON_PIT", "IDF weights and vocabulary use documents published after early t"),
    ("X04", "TF-IDF / vocabulary re-fitted at each t on documents available <= t (expanding window)",
     "UNRESOLVED", "document-time PIT by construction, but the mapping changes with t, so equal values do not "
     "mean the same thing across eras; not stable enough for a fixed confirmatory definition without a "
     "separate stability design"),
    ("X05", "TF-IDF fitted once on a frozen corpus published before 2018-01-01",
     "UNRESOLVED", "transform-time PIT for every sample t if the corpus cutoff is verified; no such corpus was "
     "collected in H20.0, so the cutoff cannot be demonstrated here; post-2017 vocabulary (e.g. 'stablecoin' "
     "usage growth) is out-of-vocabulary"),
    ("X06", "static word embeddings trained on pre-2018 corpora (GloVe 6B 2014, word2vec GoogleNews 2013)",
     "UNRESOLVED", "training data predates every sample t, but the artefacts are third-party files whose "
     "training-data cutoff is asserted, not verified here; no hash-pinned copy exists in the project"),
    ("X07", "GDELT V2Tone written at ingest into the GKG slice file (built as F22)",
     "PIT_SAFE", "computed by GDELT's dictionary scorer when the slice was produced (file immutable); the "
     "scorer's dictionaries are GDELT's at t, not fitted on later data by this project"),
]
