# Context Timestamp Schema

Every context record carries up to six times and two quality classes. All times are tz-aware UTC
(repository convention, `src/qie/time.py`). A missing time is `null`, never a guessed value.

## 1. The six times

| field | meaning | who sets it |
|---|---|---|
| `event_time` | when the thing described happened (a rate decision, a hack, a court ruling) | the content |
| `publication_time` | when the publisher states the document was released | the publisher's own metadata or text |
| `first_observed_time` | earliest independent evidence that the document existed (archive capture, feed slice, revision timestamp) | a third party |
| `public_availability_time` | **the admissibility time**: the earliest instant at which the document can be shown to have been public | derived by the rule in §3 |
| `ingest_time` | when H20 fetched it (receive clock) | H20 |
| `last_updated_time` | the publisher's latest modification stamp, if exposed | the publisher |

Two equalities are forbidden by default: `event_time = publication_time` and
`publication_time = public_availability_time`. Either may hold for a given source, but only when the
source's mechanism has been measured to make it hold (e.g. a feed slice whose file time **is** the
observation).

## 2. Timestamp quality classes

The class is assigned from the **best evidence for `public_availability_time`**, not from
`event_time`.

| class | definition | example |
|---|---|---|
| `T0_EXACT` | instant to ≤ 1 minute with an explicit timezone or epoch | Binance CMS `releaseDate` (epoch ms); GDELT 15-minute slice time; Wikipedia revision timestamp |
| `T1_MINUTE_OR_HOUR` | time of day known to the hour or minute, but the timezone or exactness rests on a documented convention or a statement in the text | Fed press release "For release at 2:00 p.m. EST" on a dated page |
| `T2_DAY_ONLY` | the date is known, intraday ordering is not | Federal Register `publication_date`; dated press-release listings |
| `T3_AMBIGUOUS` | timezone, version or publication semantics uncertain (e.g. a date that might be an update date; relative dates "2 days ago"; conflicting stamps) | a page showing only "Updated: …" |
| `T4_RETROSPECTIVE` | the record was written after the fact and carries no evidence it was available at the event's time | current Wikipedia article text; hack leaderboards; current CoinGecko descriptions |

T4 records may be retained as **pointers** (e.g. to locate a primary document) but are never
admissible content.

## 3. Rule for `public_availability_time`

| evidence | rule |
|---|---|
| T0 publisher stamp, no contradiction | `public_availability_time = publication_time` |
| T0 publisher stamp **and** an archive capture earlier than it | flag `STAMP_AFTER_CAPTURE`; `public_availability_time = first_observed_time`; record the gap |
| T1 | the stated time in the stated (or documented) zone, converted to UTC; flag `CONVENTION_TZ` when the zone is a convention |
| T2 | **end of the publication day** in the publisher's home timezone, converted to UTC — i.e. the document is admissible only from the next local midnight. Never the start of the day. Flag `DAY_END_CONSERVATIVE` |
| T3 | `public_availability_time = null`; not admissible until resolved |
| T4 | `null`; never admissible as content |
| only `first_observed_time` (archive or feed) | `public_availability_time = first_observed_time`, class T0 if the observer's clock is exact |

The day-end rule is conservative by construction: it can only make a document arrive later than it
did, never earlier. Its cost (lost intraday information) is a measured quantity in H20.0, not a
choice made here.

## 4. Admissibility at `t`

A record is admissible for decision time `t` iff `public_availability_time ≤ t` **and**
the content used is the version that existed at or before `t` (§5). Information at `t + 1 minute` is
future information.

## 5. Version quality classes

| class | definition | counts as |
|---|---|---|
| `V0_IMMUTABLE` | the publisher guarantees a fixed record (Federal Register document number, a GDELT slice file, an EDGAR accession) | immutable |
| `V1_ARCHIVED_AT_T` | an independent archive capture with capture time ≤ `t` exists, so the content as of `t` is retrievable | historically archived |
| `V2_VERSIONED` | mutable, but the full revision history is public and the revision current at `t` is retrievable (Wikipedia `oldid`) | mutable-but-versioned |
| `V3_CURRENT_ONLY_NO_EDIT_EVIDENCE` | only the current version survives; no evidence it was edited after `t` | current-version-only |
| `V4_CURRENT_ONLY_EDITED` | only the current version survives **and** there is evidence of a post-`t` edit (update stamp > `t`, "(Updated …)" marker, or hash ≠ archived copy) | current-version-only, known contaminated |
| `V5_UNRETRIEVABLE` | listed or referenced, but the content cannot be fetched now and no archive exists | — |

Gate G4 counts V0 + V1 + V2. V3 is not credited: absence of edit evidence is not evidence of no edit.

## 6. What is deliberately not decided here

The thresholds a future model would use to admit documents — e.g. whether T2 records are usable at
daily frequency, whether V3 is tolerable for some sources — are **not** set in H20.0. They depend on
the distributions H20.0 measures and will be fixed in H20.2's pre-registration.
