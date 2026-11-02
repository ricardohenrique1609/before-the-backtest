# Context Data Model

An immutable, append-only document/event store. A record, once written, is never edited: a newer
version of the same source document is a **new record** with a new `document_id` and the same
`source_document_key`, and the old record stays.

## 1. Storage layers

| layer | path | content | mutability |
|---|---|---|---|
| raw | `data/raw/<source_id>/` | exactly the bytes received (JSON, HTML, zip), named by request hash | write-once |
| request log | `data/raw/_requests.jsonl` | one line per HTTP request: URL, params, status, bytes, sha256, `ingest_time`, purpose | append-only |
| interim | `data/interim/` | parsed per-source tables | regenerated from raw |
| derived | `data/derived/context_documents.parquet` | the unified table below | regenerated from interim |
| evidence | `evidence/` | aggregate tables that support the report (tracked in git) | regenerated |

`data/` is gitignored by the repository-wide rule (`data/`), consistent with the rest of Quant
Intelligence; reproducibility rests on the scripts, the request log, and the hashes in
`CONTEXT_EVIDENCE_MANIFEST.csv`.

## 2. `context_documents` — one row per document version

| field | type | notes |
|---|---|---|
| `document_id` | str | sha256 of (`source_id`, `source_document_key`, `content_hash`), first 32 hex |
| `source_document_key` | str | the publisher's own id (CMS code, FR document number, `oldid`, GDELT record id) |
| `source_id` | str | registry key |
| `source_type` | str | `OFFICIAL_REGULATOR`, `CENTRAL_BANK`, `OFFICIAL_EXCHANGE`, `NEWS_INDEX`, `WIKI`, `ARCHIVE`, … |
| `source_url` | str | canonical URL |
| `source_domain` | str | host |
| `entity_id` | str / null | `asset:<TICKER>#<era>`, `exchange:BINANCE`, `regulator:SEC`, `jurisdiction:US` |
| `entity_type` | str / null | `ASSET`, `EXCHANGE`, `REGULATOR`, `JURISDICTION`, `PROJECT`, `PROTOCOL` |
| `entity_era` | int / null | era index **as of `public_availability_time`** (§4) |
| `ticker_at_time` | str / null | the ticker in force at that time |
| `event_time` | ts / null | |
| `publication_time` | ts / null | |
| `first_observed_time` | ts / null | |
| `public_availability_time` | ts / null | rule in `CONTEXT_TIMESTAMP_SCHEMA.md` §3 |
| `ingest_time` | ts | |
| `last_updated_time` | ts / null | |
| `timestamp_quality` | enum | `T0_EXACT` … `T4_RETROSPECTIVE` |
| `timestamp_flags` | str | `DAY_END_CONSERVATIVE`, `CONVENTION_TZ`, `STAMP_AFTER_CAPTURE`, … |
| `version_quality` | enum | `V0_IMMUTABLE` … `V5_UNRETRIEVABLE` |
| `title` | str | |
| `raw_text_reference` | str | path of the raw bytes under `data/raw/` (never inline text in evidence) |
| `language` | str | ISO 639-1 as declared by the source, else `und` |
| `context_layer` | enum | `C1` … `C5` |
| `secondary_layers` | str | `;`-separated |
| `jurisdiction` | str / null | |
| `retrieval_method` | str | `API_JSON`, `HTML`, `CSV_ZIP`, `MEDIAWIKI_API`, `CDX` |
| `archive_reference` | str / null | Wayback capture URL with timestamp, or `oldid` |
| `content_hash` | str | sha256 of the normalised content bytes (§3) |
| `license_class` | str | registry value |
| `redistribution_allowed` | bool | registry value |
| `pit_eligible` | bool | `public_availability_time` not null and version class ≠ V4/V5 |
| `pit_exclusion_reason` | str / null | |

## 3. Content hashing

`content_hash` is computed on the content the model would read (title + body text after a fixed,
versioned normaliser: Unicode NFC, whitespace collapsed), not on the HTTP bytes, which carry tracking
tokens and render-time noise. The raw bytes keep their own sha256 in the request log. Refetch
stability (gate G5) compares `content_hash` across two fetches.

## 4. Identity

`identifier ≠ identity`. A ticker is a versioned attribute of an asset era:

- an **era** of a ticker starts with its first Binance spot route and ends after > 365 days with no
  served route (inherited rule A7);
- the era of a document is the era **current at `public_availability_time`** — later reuse of the
  ticker is invisible to it;
- a name↔ticker link is admissible only if it comes from a document available ≤ `t` (e.g. a Binance
  listing notice "Binance Will List NAME (TICKER)" published before `t`);
- current third-party metadata (CoinGecko, CoinMarketCap, today's Wikipedia infobox) is never used to
  resolve an entity as of a past `t`.

## 5. Events vs documents

H20.0 stores **documents**. Events (an FOMC decision reported by many documents) are a
representation choice for H20.1 and would live in a separate table keyed to `document_id`s, never
replacing them.
