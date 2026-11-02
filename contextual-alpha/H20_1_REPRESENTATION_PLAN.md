# H20.1 — Context Representation Feasibility: Plan and Pre-Registration

**Status: FROZEN before the H20.1 evaluation sample was drawn and before any context was collected for
it.** The SHA-256 of this file is recorded in `H20_1_REPRESENTATION_FREEZE.json` and
`H20_1_SAMPLE_FREEZE.json`. A later change is a deviation, filed in `H20_1_EXECUTION_DEVIATIONS.md`,
never an edit to this file.

**Date:** 2026-10-18 · **Repository HEAD at start:** `a14c347` · **Write zone:** `Contextual Alpha/` only.

---

## 0. Preconditions (checked at start)

| check | result |
|---|---|
| git HEAD | `a14c347606068a80570bd11dcc1048ec01614bd9` |
| git status | clean apart from untracked `Contextual Alpha/docs/` (the truncation impact note) |
| H20.0 committed | yes — `a14c347 H20.0 context data feasibility: PARTIAL PASS …` |
| H18/H19 842-article truncation | assessed in `docs/H18_SNAPSHOT_TRUNCATION_IMPACT.md`: of the six snapshot readers 3 are NONE and 3 are LOW (plus one second-order LOW consumer), 0 MATERIAL; no frozen verdict, gate or headline figure moves. Treated as closed with no material impact on the sponsor's instruction to proceed. H18/H19 are not modified or reopened. |

## 1. Question

> Can the PIT-valid C1–C3 context substrate be transformed into stable, reproducible, auditable
> features without using any future outcome?

H20.1 is **not** a prediction experiment. It computes no return, price, volatility, PR-AUC, ROC-AUC,
correlation with any outcome, or significance against any outcome. **No outcome table is opened.**
Feature selection by outcome is forbidden (§12 of the brief). The experiment ends before any outcome
join.

Closed verdicts: **PASS · PARTIAL PASS · DATA-GATE FAIL / UNTESTED · BLOCKED.**

## 2. Scope boundaries inherited from H20.0

- Layers **C1, C2, C3 only.** C4 (exchange) and C5 (asset) remain DATA-GATE FAIL / UNTESTED. No
  Binance text, title or timestamp is used. No asset-specific feature is built. C5 naming is not
  repaired.
- Every eligible feature inherits its layer's H20.0 condition and may not be generalised beyond it:
  - **C1** reconstructible; conditional on temporal / archive bias (Fed press archive capture early vs late).
  - **C2** reconstructible; **US-only**; conditional on temporal / archive bias.
  - **C3** reconstructible **as metadata / structured records**; conditional on GDELT language and
    archive bias (English dictionary under-detects non-English crypto news ~4×).
- **MISSING ≠ ZERO.** A source that was inaccessible, blocked, or not walked for a window yields a
  missing value with a reason code, never 0.

## 3. Two kinds of point-in-time validity

- **DOCUMENT-TIME PIT:** every source record that contributes to a value at decision time `t` has
  `public_availability_time ≤ t` (rules of `CONTEXT_TIMESTAMP_SCHEMA.md` §3; the H20.1 refinements in §6).
- **TRANSFORM-TIME PIT:** the transformation that maps records to a value injects no knowledge
  unavailable at `t`. A transform is classified:
  - `PIT_SAFE` — deterministic rule whose parameters were fixed without reference to documents after
    `t` and without hindsight about events after `t`: counts, timestamps, publisher-assigned
    categories, source flags, fixed dictionaries of generic terms written before evaluation, fixed
    arithmetic on as-of vintages, and attributes computed by the publisher at ingest time (GDELT GKG
    fields are written into the 15-minute slice file at `t`);
  - `NON_PIT` — any model or statistic fitted on a corpus that includes post-`t` documents (modern
    LLMs, current embedding models, classifiers trained on post-`t` data, TF-IDF / vocabulary fitted
    on the full 2018–2026 corpus);
  - `UNRESOLVED` — plausibly PIT-safe but not demonstrated (e.g. a model whose training-data cutoff is
    asserted but not verified, an expanding-window fit whose parameters drift by construction).
  
  **Default rule:** modern LLMs / embeddings / classifiers trained on post-`t` corpora are `NON_PIT`
  and are recorded only as `NON_PIT_TRANSFORM_CANDIDATE`. No LLM or embedding model is used to build
  any H20.1 feature. Only `PIT_SAFE` features may enter a future confirmatory design.
- **Hindsight-vocabulary rule.** A dictionary may contain generic category words only. No named
  project, firm, person or event is added. The single named entity, `binance`, is inherited unchanged
  from the H20.0 governance list (Binance existed from 2017-07, before the first sample `t`). Every
  dictionary term's earliest attestation in the collected corpus is reported (lexicon audit).

## 4. Representation families

| family | content | built in H20.1 |
|---|---|---|
| **R1 — event flags** | 0/1 indicators of a rule-defined document event in a window | yes |
| **R2 — counts / intensities** | counts of rule-selected documents in a window; shares of tagged records | yes |
| **R3 — text-derived** | representations computed from document text by a model or fitted statistic | **assessment only**, plus one publisher-computed ingest-time score (GDELT V2Tone) that is the only R3 candidate meeting the default PIT_SAFE definition |
| **R4 — as-of structured values** | values read from the macro data vintage in force at `t` | yes |

R3 candidates assessed but **not built** (classification is recorded in `H20_1_TRANSFORM_PIT_AUDIT.csv`):
current LLM extraction/labelling; current sentence-embedding models; TF-IDF or topic models fitted on
the full corpus; expanding-window TF-IDF refit at each `t`; TF-IDF fitted on a frozen pre-2018 corpus;
static word embeddings trained on pre-2018 corpora (e.g. GloVe 2014, word2vec 2013).

## 5. Sources (H20.0-passed C1–C3 sources only)

| source_id | layer | used for | basis of record times |
|---|---|---|---|
| `S_FED_PRESS` | C1, C2 | Fed press-release feed items (title, publisher `doc_type`) | T1 (ET convention) or T2 day-end; the H20.0 raw feed bytes (fetched 2026-10-18) are reused, not re-fetched |
| `S_ALFRED` | C1 | vintages of `CPIAUCSL`, `UNRATE`, `DFF` | vintage date, day-end ET |
| `S_FEDREG` | C2 | Federal Register documents by publication-date range (no term query); title, abstract, type, agencies | T2 day-end ET; V0 immutable |
| `S_SEC_PRESS` | C2 | SEC newsroom monthly press-release listings (title, stamp) | T0 CMS stamp |
| `S_CFTC_PRESS` | C2 | CFTC press-release listings **already received in H20.0** (2018–2020, 2021-Q4 page 0); **no new CFTC request** | T0 stamp |
| `S_GDELT_GKG` | C3 | GKG 2.1 15-minute slice files (English and translingual) | slice stamp + 15 min |
| `S_WIKI_PORTAL` | C3 | Portal:Current events day pages, revision current at `t` | revision timestamp (V2) |

Not used: Binance (C4/C5), Wikipedia asset pages (C5), DOJ, any news site, any source not passed in
H20.0. The Federal Register crypto selection is **narrower than H20.0's**: H20.0 used FR's own
full-text search engine; H20.1 fetches every document in the date range and applies the fixed local
dictionary to title + abstract, so the transform is under the project's control (the remote engine's
matching rules are neither versioned nor PIT-documented).

## 6. Timestamp rules (decision time `t`, UTC minute)

| source | `public_availability_time` | admissible at `t` iff |
|---|---|---|
| Fed feed item with time | stated ET time → UTC (T1, `CONVENTION_TZ`) | ≤ `t` |
| Fed feed item day-only | next ET midnight → UTC (T2) | ≤ `t` |
| Federal Register | next ET midnight after `publication_date` (T2) | ≤ `t` |
| SEC / CFTC listing | stamp (T0) | ≤ `t` |
| ALFRED vintage dated `D` | next ET midnight after `D` | `D ≤ asof(t) = date_ET(t) − 1 day`. **Tightening of H20.0**, which used `date_UTC(t) − 1 day`; that admitted, for `t` between 00:00 and 04:00/05:00 UTC, a vintage dated the same ET calendar day as `t` |
| GDELT slice stamped `s` | `s + 15 min` (the file covers the 15 min to `s` and is published at `s`; +15 min is conservative) | ≤ `t`; slice `s_k = floor15(t − k·24 h − 15 min)`, `k = 0..6` |
| Wikipedia day page | timestamp of the revision current at `t` | revision ≤ `t` (the revision is selected with `rvstart = t`, `rvdir = older`) |

Windows: `W7(t) = (t − 7 d, t]`, `W30(t) = (t − 30 d, t]`; a document at `t` is in, at `t + 1 min`
is out. `S7(t)` = the seven GDELT slices `s_0 … s_6` (one per day at the same time of day; a fixed
deterministic sample of W7, because a full W7 is 672 slices ≈ 11 GB per `t`). Wikipedia `D7(t)` =
the seven UTC day pages `date(t) − 6 … date(t)`.

## 7. Feature specification (representation version `h20_1_rep_v1`)

Naming: `<layer>_<source/content>_<statistic>_<window>`, lower case; window suffix `W7`, `W30`,
`S7`, `D7` or `asof`. Dictionaries and rules are implemented in `scripts/h20_1_rep.py`, whose
SHA-256 is frozen in `H20_1_REPRESENTATION_FREEZE.json`. The machine-readable registry is
`CONTEXT_FEATURE_REGISTRY.csv`.

### Dictionaries and classifiers (frozen)

| id | applied to | rule |
|---|---|---|
| `K_CRYPTO` | SEC titles; FR title + abstract; Wikipedia day-page items | inherited H20.0 governance tag, unchanged: `crypto \| digital asset \| virtual currenc \| bitcoin \| stablecoin \| blockchain \| token \| coin offering \| binance \| \bether\b` (case-insensitive) |
| `K_GDELT_CRYPTO` | GKG themes (V1+V2) + organisations + all-names + document URL | inherited H20.0 GDELT list, unchanged: `bitcoin \| cryptocurrenc \| crypto \| blockchain \| binance \| stablecoin` |
| `K_SEC_ENFORCEMENT` | SEC titles | `\bcharg(?:e\|es\|ed\|ing)\b \| \bsettle(?:s\|d\|ment\|ments)?\b \| \bto pay\b \| \bpenalt \| \bjudgment \| asset freeze \| \bhalts?\b \| \bfraud \| trading suspension \| suspends trading \| \bbar(?:s\|red)?\b \| \bsanction` |
| `K_FOMC_STATEMENT` | Fed feed items | publisher `doc_type == "Monetary Policy"` **and** title matches `\bFOMC statement\b` |
| `K_CRYPTO_STRESS` | Wikipedia items already tagged `K_CRYPTO` | `\bhack \| \bstolen\b \| \btheft\b \| \bexploit \| insolven \| bankrupt \| \bcollaps \| de-?peg \| (?:halt\|suspend\|freez)\w* (?:all )?withdrawals \| \bfraud \| \bponzi\b \| \bcrash` |
| `FR_FINREG` | FR `agencies` | any of: Securities and Exchange Commission; Commodity Futures Trading Commission; Federal Reserve System; Federal Deposit Insurance Corporation; Comptroller of the Currency; Treasury Department; Financial Crimes Enforcement Network; Foreign Assets Control Office; Consumer Financial Protection Bureau |
| `FR_RULEMAKING` | FR `type` (publisher field) | `Rule` or `Proposed Rule` |
| Wikipedia item | revision wikitext | a line beginning with `*` (H20.0 rule, unchanged) |

### Features

| id | name | family | source | definition (all windows as §6) |
|---|---|---|---|---|
| F01 | `c1_fed_release_count_W7` | R2 | S_FED_PRESS | Fed feed items available in W7 |
| F02 | `c1_fed_monetary_policy_count_W30` | R2 | S_FED_PRESS | items with `doc_type == Monetary Policy` in W30 |
| F03 | `c1_fomc_statement_flag_W7` | R1 | S_FED_PRESS | 1 if ≥ 1 `K_FOMC_STATEMENT` item in W7 |
| F04 | `c1_cpi_release_flag_W7` | R1 | S_ALFRED | 1 if the last observation date of `CPIAUCSL` in vintage `asof(t)` is later than in vintage `asof(t − 7 d)` |
| F05 | `c1_unrate_release_flag_W7` | R1 | S_ALFRED | same for `UNRATE` |
| F06 | `c1_policy_rate_asof` | R4 | S_ALFRED | last `DFF` value in vintage `asof(t)` |
| F07 | `c1_cpi_yoy_asof` | R4 | S_ALFRED | in vintage `asof(t)`: last `CPIAUCSL` value / value 12 months earlier − 1 (percent) |
| F08 | `c1_unrate_asof` | R4 | S_ALFRED | last `UNRATE` value in vintage `asof(t)` |
| F09 | `c2_fedreg_finreg_doc_count_W7` | R2 | S_FEDREG | FR documents with ≥ 1 `FR_FINREG` agency in W7 |
| F10 | `c2_fedreg_crypto_doc_count_W7` | R2 | S_FEDREG | FR documents matching `K_CRYPTO` on title + abstract in W7 |
| F11 | `c2_fedreg_crypto_doc_count_W30` | R2 | S_FEDREG | same in W30 |
| F12 | `c2_fedreg_crypto_rulemaking_count_W30` | R2 | S_FEDREG | F11 documents with `FR_RULEMAKING` type |
| F13 | `c2_sec_press_count_W7` | R2 | S_SEC_PRESS | SEC press releases in W7 |
| F14 | `c2_sec_enforcement_count_W7` | R2 | S_SEC_PRESS | SEC press releases matching `K_SEC_ENFORCEMENT` in W7 |
| F15 | `c2_sec_crypto_press_count_W30` | R2 | S_SEC_PRESS | SEC press releases matching `K_CRYPTO` in W30 |
| F16 | `c2_fed_enforcement_count_W30` | R2 | S_FED_PRESS | Fed items with `doc_type == Enforcement Actions` in W30 |
| F17 | `c2_cftc_press_count_W30` | R2 | S_CFTC_PRESS | CFTC press releases in W30 |
| F18 | `c2_crypto_regulatory_action_flag_W7` | R1 | S_FEDREG, S_SEC_PRESS | 1 if F10 + (SEC `K_CRYPTO` releases in W7) ≥ 1; missing if either component is missing |
| F19 | `c3_gdelt_crypto_record_count_S7` | R2 | S_GDELT_GKG | `K_GDELT_CRYPTO` records in the 14 S7 files |
| F20 | `c3_gdelt_crypto_record_share_S7` | R2 | S_GDELT_GKG | F19 / all records in the available S7 files |
| F21 | `c3_gdelt_crypto_record_share_en_S7` | R2 | S_GDELT_GKG | same, English files only |
| F22 | `c3_gdelt_crypto_tone_mean_S7` | R3 | S_GDELT_GKG | mean of GDELT's own V2Tone (first component, written at ingest) over S7 crypto records |
| F23 | `c3_wiki_crypto_item_count_D7` | R2 | S_WIKI_PORTAL | `K_CRYPTO` items in the D7 day pages as of `t` |
| F24 | `c3_wiki_crypto_item_flag_D7` | R1 | S_WIKI_PORTAL | 1 if F23 ≥ 1 |
| F25 | `c3_crypto_stress_flag_D7` | R1 | S_WIKI_PORTAL | 1 if ≥ 1 D7 item matches `K_CRYPTO` and `K_CRYPTO_STRESS` |

No feature is added, removed or redefined after this freeze except as a recorded deviation.

## 8. Missing and zero semantics (frozen)

Every feature value is either a number or `NaN` with a `missing_reason` code. **A zero is written
only when the source was available and walked for the whole window and nothing qualified.**

| source | MISSING when | reason code |
|---|---|---|
| S_FED_PRESS | never for windows inside the feed's span (2006 → 2026-10-18) | `OUT_OF_SOURCE_SPAN` otherwise |
| S_ALFRED | either required vintage fetch is not OK | `FETCH_FAILED` |
| S_FEDREG | any page of the window query not OK | `FETCH_FAILED` |
| S_SEC_PRESS | any month touching the window not walked to completion | `FETCH_FAILED` |
| S_CFTC_PRESS | the window is not inside a span walked in H20.0 (2018-01-25→2018-12-31, 2019-01-29→2019-12-31, 2020-01-08→2020-12-31, 2021-09-30→2021-12-31); years 2021–2026 otherwise were HTTP 429 | `NOT_WALKED` / `ACCESS_BLOCKED` |
| S_GDELT_GKG | counts (F19): any of the 14 files not OK; shares (F20, F21): fewer than 4 of 7 slices with both files OK (English only for F21); tone (F22): F19 missing **or** zero crypto records (undefined, not zero) | `FILE_MISSING` / `INSUFFICIENT_SLICES` / `UNDEFINED_NO_RECORDS` |
| S_WIKI_PORTAL | any API call not OK. A day page that **did not exist at `t`** contributes zero items (nothing was published), recorded as `PAGE_ABSENT_AT_T` in provenance | `FETCH_FAILED` |
| composite F18 | either component missing | `COMPONENT_MISSING` |

## 9. Provenance rules (frozen)

Every non-missing value is traceable through `H20_1_FEATURE_PROVENANCE.csv`: one row per
(`t`, feature, contributing record) with `source_id`, `source_document_key`, `document_id`
(H20 data-model hash), `public_availability_time`, window, rule id and `transform_version`. Counts
must equal the number of contributing rows. Zero values carry one row of type `EMPTY_WINDOW` naming
the walked window. As-of values (R4, F04–F08) carry the series, vintage date and observation date(s)
used. GDELT shares and totals are traced to file level (slice file name and sha256, record count);
the crypto records themselves are traced individually. Provenance completeness = share of non-missing
values whose provenance satisfies these rules; the bar is **100%**.

## 10. Evaluation sample (frozen rule; `scripts/h20_1_sample_freeze.py`)

- **One decision timestamp per calendar month, 2018-01 through 2026-09 (105 timestamps).** Within each
  month an instant is drawn uniformly at minute resolution with `numpy.random.default_rng(20261101)`,
  in month order. The seed is new (H20.0 used 20261018–20261020).
- Calendar only: no date is chosen, moved, added or dropped for any reason related to events, crashes,
  delistings, or market conditions. 2026-10 is excluded as incomplete.
- No assets (C4/C5 are out of scope).
- H20.0's 35 timestamps are the **design sample**: dictionaries were read against H20.0-window
  documents only. Overlap of H20.1 windows with H20.0 W30 windows is recorded, not removed; every
  audit is also reported on the non-overlapping subset.
- Written and hashed before any context is collected for it.

## 11. Audits (computed by `scripts/h20_1_audit.py`)

| | audit | measurement |
|---|---|---|
| A | determinism | the feature matrix and provenance are built twice in separate processes from the same frozen inputs; sha256 of both outputs must be identical |
| B | PIT integrity | count of provenance records with `public_availability_time > t`; count of vintages with date > `asof(t)`; count of GDELT files with stamp + 15 min > `t`; count of Wikipedia revisions after `t`. All must be **0** |
| C | transform-time PIT | every feature and every R3 candidate classified PIT_SAFE / NON_PIT / UNRESOLVED with a written justification |
| D | coverage | non-missing share by feature × year, by source, by layer |
| E | zero vs missing | zero share and missing share per feature, separately; missing reasons tabulated |
| F | temporal stability | (i) schema: publisher category sets per year (Fed `doc_type`, FR `type`), GKG column count per file, Wikipedia items-per-page parse; (ii) publication-frequency drift: source denominators per window by era (2018–20, 2021–23, 2024–26); (iii) classifier base-rate drift; (iv) coverage drift |
| G | sparsity | per feature: nonzero share, missing share, quantiles, early (2018–20) vs late (2024–26) |
| H | redundancy | pairwise Spearman ρ between features on pairwise-complete timestamps |
| I | semantic audit | §12 |
| L | lexicon vintage | earliest attestation of each dictionary term in the collected corpus |

## 12. Semantic audit (frozen)

Classifiers audited: `K_CRYPTO` on SEC titles (K1a) and on FR title + abstract (K1b),
`K_SEC_ENFORCEMENT` (K2), `K_FOMC_STATEMENT` (K3), `K_CRYPTO` on Wikipedia items (K4),
`K_CRYPTO_STRESS` (K5), `K_GDELT_CRYPTO` (K6). Publisher-assigned categories (Fed `doc_type`, FR
`type`, FR `agencies`) are the publisher's own classification and are not audited as parsers.

- **Sample.** From documents in H20.1 evaluation windows that are **not** in any H20.0 W7 window
  (the design documents), draw with `numpy.random.default_rng(20261102)` up to **30 classifier
  positives and 20 negatives per classifier** (all positives if fewer than 30). Negatives for K5 are
  `K_CRYPTO` Wikipedia items not matching `K_CRYPTO_STRESS`; for K3, Monetary Policy items not
  matching. Items are presented in shuffled order without the classifier's decision.
- **Annotation guideline.** CRYPTO: the record's subject is crypto-assets / blockchain-based digital
  assets, their markets, firms, regulation or technology. ENFORCEMENT: the title announces an
  enforcement action or outcome (charges, settlement, judgment, penalty, trading suspension, asset
  freeze, bar, sanction); whistleblower awards, enforcement statistics and personnel news are not.
  FOMC_STATEMENT: the FOMC's policy statement / decision release, scheduled or unscheduled; minutes,
  projections and implementation notes are not. CRYPTO_STRESS: the crypto item reports a theft or
  hack, insolvency or bankruptcy, failure or collapse, depeg, withdrawal halt, fraud charge, or market
  crash. GDELT: judged from the record's URL, organisations, names and themes; `UNDETERMINABLE` is
  allowed and reported.
- **Annotator.** The labels are produced by the AI research agent running H20.1, reading the stored
  source text, and are recorded with document ids and evidence spans so that a human can re-check
  every one. This is disclosed in the report; it is not a human gold standard.
- **Quality bar (frozen):** precision on positives **≥ 0.90** and agreement on negatives **≥ 0.90**,
  each with **n ≥ 10**; for K6, `UNDETERMINABLE` ≤ 20% of audited items. A classifier below the bar,
  or with fewer than 10 positives available, is a **semantic defect** for every feature that uses it.

## 13. Frozen representational rules (no outcome involved)

- **Coverage bar:** non-missing share ≥ 0.90 overall **and** ≥ 1 non-missing value in ≥ 8 of 9
  calendar years.
- **Sparsity:** a count or flag with nonzero share < 0.05, or any feature constant over its
  non-missing values, is `SPARSE_DEGENERATE`.
- **Redundancy:** for a pair with |Spearman ρ| ≥ 0.95 on ≥ 30 pairwise-complete timestamps, the
  feature later in registry order is `REDUNDANT` with the earlier one. Not deleted; not eligible for
  the confirmatory set while its partner is.
- **Drift:** a source denominator whose era means differ by a ratio ≥ 2.0, or a change in a
  publisher category set, flags `DRIFT`; the feature stays eligible with the mandatory constraint
  *era-stratified evaluation only*. A schema change that changes what a feature counts is a
  semantic defect.

## 14. Gate (frozen)

A feature is **ELIGIBLE for H20.2** iff: transform class `PIT_SAFE`; 0 PIT violations in its
provenance; deterministic regeneration identical; provenance complete; missing and zero
distinguishable (explicit `NaN` + reason, no missing encoded as 0); coverage bar met; every classifier
it uses meets the semantic bar; not `SPARSE_DEGENERATE`; not `REDUNDANT`. Eligible features carry
their layer's H20.0 condition and any `DRIFT` constraint.

Each family (R1, R2, R3, R4) is judged independently:

- **PASS** — family-level criteria hold (100% PIT document integrity for the family; 100% transform
  classification; no feature of the confirmatory set marked NON_PIT; deterministic regeneration;
  complete provenance; missing ≠ zero; no unresolved semantic defect in any eligible feature) **and
  every** built feature of the family is eligible.
- **PARTIAL PASS** — family-level criteria hold and ≥ 1 built feature is eligible, but some are not
  (each named with its failed criterion).
- **DATA-GATE FAIL / UNTESTED** — no built feature of the family is eligible, or no PIT_SAFE
  representation of the family could be built.
- **BLOCKED** — the measurement could not be run for reasons other than the data (access, tooling).

A family-level PIT violation (any feature with a violation) is a FAIL for that family regardless of
anything else. A criterion that could not be measured is not passed. Bars are not lowered after
measurement. Layer status (C1, C2, C3) is reported as the set of eligible features per layer.

## 15. Outputs

`H20_1_REPRESENTATION_PLAN.md` (this file), `H20_1_REPRESENTATION_FREEZE.json`,
`H20_1_SAMPLE_FREEZE.json`, `CONTEXT_FEATURE_REGISTRY.csv`, `H20_1_TRANSFORM_PIT_AUDIT.csv`,
`H20_1_FEATURE_PROVENANCE.csv`, `H20_1_REPRESENTATION_METRICS.json`, `H20_1_REPRESENTATION_REPORT.md`,
`H20_1_GATE.json`, `H20_1_EXECUTION_DEVIATIONS.md`; evidence tables under `evidence/H20_1_*`; scripts
`scripts/h20_1_*.py`; tests `tests/test_h20_1.py`.

## 16. Stop rule

H20.1 ends with the gate and the report. **H20.2 is not begun. No outcome is loaded. No predictive
model is trained.**
