# Context Retrieval Governance

The researcher already knows many crypto outcomes. **Researcher ignorance is not claimed.** What is
claimed, and auditable, is **structural outcome exclusion**: collection and feature construction are
built so that they never need — and cannot read — a future outcome.

## 1. Order of operations

```
freeze sample (timestamps, entities)            -> H20_0_SAMPLE_FREEZE.json (hashed)
-> define I(t) per source (fixed query rules §3)
-> retrieve only documents in the sample windows (+ the Binance title catalogue, harvested whole)
-> classify under fixed rules (timestamp, version, layer, entity)
-> hash collected tables                          -> manifests/H20_0_PRE_SEAL_HASHES.json
-> sealed survivorship audit (only stage that reads a lifecycle flag)
-> report
```

## 2. Forbidden inputs

Collection and classification code may not read: the delisting/lifecycle tables (inheritance A3, A4),
the landmark/feature/prediction panels (A9), or any price, return or post-`t` market quantity.
`tests/test_outcome_blindness.py` scans every H20 script and fails if one other than
`h20_0_sealed_survivorship.py` names any forbidden path or column.

## 3. Query rules

Every outbound request goes through `scripts/h20_common.py:get()`, which:

1. **logs** URL, parameters, status, bytes, sha256 and `ingest_time` to `data/raw/_requests.jsonl`;
2. **refuses** any URL or parameter containing an outcome term (`delist`, `crash`, `collapse`,
   `scam`, `rug`, `exploit`, `hack`, `bankrupt`, `insolven`, `lawsuit`, `why did`, `what caused`,
   `reason`) — raises `ForbiddenQueryError`; tested in `tests/test_query_guard.py`;
3. paces requests per host and identifies itself with a research User-Agent;
4. records `ACCESS_BLOCKED` (challenge pages, 202-empty, 403, 429 after retries) distinctly from
   `NO_DATA`; access controls are **never bypassed**.

Query parameters may depend only on: the sample timestamp and window, the source, a fixed term list
written in this file, and entity names resolved point-in-time. Fixed term lists:

- **Federal Register (C2):** `cryptocurrency | "digital asset" | "virtual currency" | bitcoin |
  stablecoin`, publication dates inside the window.
- **GDELT GKG (C3/C5):** themes/names matched against `bitcoin`, `cryptocurrenc`, `crypto`,
  `blockchain`, `binance`, `stablecoin` (case-insensitive), and against the PIT-resolved name of each
  sampled asset.
- **Crypto-relevance tag on listing surfaces (SEC, CFTC, Fed, DOJ, Binance titles):** a title is
  tagged crypto-relevant if it matches `crypto | digital asset | virtual currenc | bitcoin |
  stablecoin | blockchain | token | coin offering | binance | ether` (case-insensitive). The tag only
  splits counts; every document in the window is collected regardless.
- **ALFRED (C1 structured):** vintages of `CPIAUCSL`, `UNRATE`, `DFF` as of the day before `t`
  (day-end rule), and the current vintage, to measure revision.
- **Wikipedia:** the Current-Events day pages for each day in `W7`; for assets, the PIT-resolved name
  only.

**Lookups are not queries.** Fetching a document by an identifier already obtained from an
outcome-free retrieval (a Binance article code, a GDELT record URL, a Wikipedia `oldid`, an archive
capture of such a URL) is an id lookup. The guard checks the request with that identifier removed,
and the request log marks it `lookup=true`, so a news URL whose slug happens to contain a guarded
word is still checkable for archive persistence without the researcher having typed that word.

The Binance CMS catalogue is harvested **whole** (all catalogues, all pages), so no query is
outcome-shaped. Its bodies are fetched only for notices whose `releaseDate` falls in a sample window.

## 4. Prohibited practice

- Starting from a known later event (crash, hack, delisting) and searching backwards for its
  "causes".
- Adding a source, term, date or entity after seeing what it returns for a sample timestamp.
- Using a current page as evidence of what was public at `t` (T4).
- Using current metadata to map a ticker to an entity at a past `t`.

## 5. LLM extraction (future, not used in H20.0)

If H20.1 adopts LLM extraction it must have: a frozen prompt and output schema (hashed), document
ids and evidence spans in every output, no access to outcome tables, model id/version and decoding
settings recorded, deterministic settings where offered, and a hand-audited sample.

## 6. The sealed survivorship stage

§19 of the brief asks whether documents vanish disproportionately for entities that later failed.
That needs a lifecycle flag. It is handled as a governed exception:

- it runs **last**, after `manifests/H20_0_PRE_SEAL_HASHES.json` exists, and verifies those hashes
  before reading anything;
- it reads exactly one coarse flag — whether the base asset had any Binance spot symbol live at the
  2026-10 harvest (`data/raw/h18_2/spot_symbols.parquet`, column `is_live_now`, inheritance A6) — and
  nothing else from the lifecycle layer;
- it writes only aggregate coverage comparisons to `evidence/` and is reported as such;
- no later H20.0 stage consumes its output.

## 7. Licensing

Raw content stays under `data/` (not committed). Evidence files carry aggregates, ids and URLs, never
copyrighted body text. Each source's licence class is in the registry.
