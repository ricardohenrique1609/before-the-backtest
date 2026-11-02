# H18.1b catalogue-snapshot truncation — impact on frozen results

**Status:** read-only impact assessment. Nothing outside `Contextual Alpha/` was written, re-run or
regenerated. No return, gap, drawdown or payoff was computed. No verdict is reopened here; this note
only says whether a sponsor-level re-check is warranted.

**Assessed 2026-10-18.**

## 1. The defect

| Item | Value |
|---|---|
| Truncated snapshot | `data/raw/h18_1b/catalog_titles.parquet`, sha256 `db3848adb069c08fd147156dd7f617abf999c7185d1e2f53aaf25125cf455bba` (re-verified), 9,631 rows, newest title 2026-10-09 11:00:05 UTC |
| Complete re-harvest | `Contextual Alpha/data/interim/binance_catalog_memberships.parquet` (10,503 unique articles; 10,473 released on or before the snapshot's newest title) |
| Missing from the snapshot | **842** articles, all catalogue 49, published 2017-07-02 → 2020-12-21 (98 / 136 / 197 / 411 for 2017–2020) |
| Cause | `scripts/h18_1b_rebrand.py:115` — `if not a: break` ends a catalogue on the first empty (rate-limited) page; catalogue 49 stopped at 3,600 of 4,452 rows |
| Not in the gap | The 30 articles published after 2026-10-09 (872 − 842) are post-snapshot releases, not truncation, and are excluded below |

The six scripts that read the snapshot all filter it by **title regex**, so the question for each is
whether any of the 842 missing titles would have matched that script's own patterns.

## 2. Method

A scratch script (session scratchpad, not in the repo) loaded each frozen script as a module with
`importlib` — which only defines its constants and functions; no `main()` was called, no network
request was made — and applied the script's own compiled regexes and helper functions
(`h18_1b_rebrand.tickers` logic, `h18_3_classes_pit.quote_notices`) to the 842 missing titles. Two
regexes are local to `main()` and were copied verbatim: `h18_1b_falseneg.py:136` (`PAIR_REMOVAL`) and
`h18_2_mechanism.py:52` (`monitoring\s+tag`). Each hit was then traced into the frozen output it
feeds (read-only reads of `rebrand_notices.parquet`, `H18_1B_FALSE_NEGATIVES.csv`,
`H18_1B_FULL_DELIST_EVENTS.parquet`, `pair_removals.parquet`, `pair_removals_pit.parquet`,
`quote_retirement_notices.parquet`, `landmarks_pit.parquet`, `candidate_map.parquet` and the
`data/alpha_sprint/*.json` summaries).

## 3. Per-script results

| Script | What it uses the titles for | Matches among the 842 missing titles | Frozen numbers that could move | Severity |
|---|---|---|---|---|
| `h18_1b_rebrand.py` | `REBRAND` regex → rebrand / token-swap / ticker-change notices and the parenthesised tickers they retire (written to `rebrand_notices.parquet`); `PAIR_REMOVAL` regex → count only | **31** `REBRAND` titles (2018-03 → 2020-12), yielding tickers RPX, REP, ADX, ENG, OCEAN — **4 new** (ADX, ENG, REP, RPX; OCEAN is already in the frozen set). **0** `PAIR_REMOVAL` titles | Descriptive counts in `h18_1b_rebrand.json`: `catalog_titles` 9,631 → 10,473; `oldest_title` 2017-07-19 → 2017-07-02; `rebrand_notices` 133 → 164; `assets_named_in_rebrand_notices` 31 → 35; `pair_removal_notices` 137 unchanged. Effects downstream are in the next two rows | LOW |
| `h18_1b_falseneg.py` | Its own `PAIR_REMOVAL` regex → which notice bodies to fetch for the pair-removal reason; reads the rebrand ticker set to class unmatched assets as `OFFICIAL_REBRAND_OR_MERGE` | **0** pair-removal titles (bodies fetched would be identical). Via the rebrand set: **1** unmatched asset affected — **ADX** (frozen reason `PAIR_REMOVAL_ONLY`) would become `OFFICIAL_REBRAND_OR_MERGE`. ENG and RPX have no pairs in the state table; REP is a found full-delisting event (2022-12), so it is never classed. None of the 4 true false negatives (ERN, KLAY, ORN, UST) is named in any missing title | Reason mix only: `PAIR_REMOVAL_ONLY` 34 → 33, `OFFICIAL_REBRAND_OR_MERGE` 11 → 12. Both are "explained" reasons, so **recall on the explained denominator stays 197 / 201 = 98.01%**, the true-false-negative list is unchanged, and the H18.1b gate's ≥ 97% recall criterion is unaffected | LOW |
| *(2nd-order)* `h18_1b_gate.py` — not a snapshot reader, but reads `rebrand_notices.parquet` | Excludes rebranded tickers from the candle-measured denominator | n/a (inherits the rebrand row) | The display list `denominator_corrections.after_removing_official_rebrands.excluded` would gain **ADX and REP** (12 → 14 names). The reported recall is overwritten by the audited false-negative decomposition (`h18_1b_gate.py:177-180`), so `against_candle_measured` stays 197 / 201 | LOW |
| `h18_2_mechanism.py` | `monitoring\s+tag` → which cached bodies are tagged `MONITORING_TAG` vs `FULL_DELISTING` / other in the factor tabulation | **0** (the Monitoring Tag was introduced 2023-07-26; the gap ends 2020-12-21) | None. The body cache it globs is not changed by the snapshot | NONE |
| `h18_2_monitoring_tag.py` | `TAG_TITLE` → the list of Monitoring Tag notices whose bodies are parsed | **0** (also 0 for a looser `seed tag\|monitoring` probe) | None: 28 notices, `tag_exists_since` 2023-07-26, 63.18% coverage, NOT TIER-1 verdict all unchanged | NONE |
| `h18_3_classes_pit.py` | `RETIRE_VERB` minus `PRODUCT_ONLY` / `NETWORK_ONLY` / `PAIRISH`, then `is_object_of_retirement` per quote → the date each quote's retirement became knowable (A2), which drives `QUOTE_RETIREMENT` | 8 titles contain a retirement verb, 5 survive the exclusions, and **1** names a quote as its object: **TRX**, from *"Discontinuation of BTT Airdrop for TRX Holders on Binance"* (2020-06-15). No missing title moves any existing date: **ZAR stays 2021-03-31** (its notice is after the gap), and BUSD, VAI, NGN, BIDR, IDRT, AEUR and USDP are all post-2023 | TRX would gain `retirement_known_from` 2020-06-15 (frozen: none). Both TRX-quoted removals would become `QUOTE_RETIREMENT`: **BTTTRX** (2022-01-17, frozen `ASSET_SPECIFIC_REMOVAL`) and **WINTRX** (2026-05-08, frozen `ASSET_SPECIFIC_REMOVAL`). PIT mix: ASSET_SPECIFIC 1,179 → 1,177, QUOTE_RETIREMENT 41 → 43 (BATCH_PRUNE 1,132 unchanged). `classifications_changed` stays 676 (BTTTRX becomes a change, WINTRX stops being one). Landmark features: **2 of 112,963** rows (BTT, weeks 2022-01-17 and 2022-01-24) would see `signal_removals_365d` and `asset_specific_removals_365d` drop by 1 and `quote_retirement_removals_365d` rise by 1, and possibly `days_since_last_signal_removal`; the WINTRX removal is after the last landmark (2025-10-06). Leakage check 5 still passes by construction, so `HARD_GATE` stays PASS | LOW |
| `h19_0_build.py` | `FUT_DELIST` → futures delisting notices and their tickers, used for `derivative_notice_order` and `public_information_state` per event | **0**. The gap holds 60 futures/contract titles from 2019-09 onward (launches, fee changes, leverage updates, cross-collateral), none a delisting | None: 201 events, `derivative_notice_order` (184 / 12 / 5), `public_information_state` (137 / 63 / 1) and `SHORTABLE_AT_T0` 64 unchanged, so H19.0 gate, H19.1 and H19.2 inputs are unaffected | NONE |

## 4. Observations a re-check would need to know

1. **Both non-zero hits are false positives of the frozen rules, not missed events.**
   - The ADX title is *"Binance Will Support the Adex (ADX) & Ocean Protocol (OCEAN) Smart Contract
     Swaps"* — two separate contract swaps in which both tickers survive. The `tickers()` helper
     reads "last parenthesised ticker = destination" and so credits ADX as retired into OCEAN. The
     frozen `PAIR_REMOVAL_ONLY` reason for ADX is the better-supported one.
   - The TRX title is about a BTT airdrop to TRX holders, not about TRX leaving the venue as a quote.
     "Airdrop" is not in `PRODUCT_ONLY`. `h18_3_classes_pit.py`'s own docstring lists TRX among the
     live assets that H18.2 wrongly marked as retired quotes, which A2 was written to correct.

   A mechanical re-run on the complete catalogue would therefore make these two frozen outputs
   slightly *less* correct.
2. **The delisting universe is not a snapshot reader.** `H18_1B_FULL_DELIST_ANNOUNCEMENTS.parquet` is
   built by `h18_1b_discover.py` from its own harvest of catalogues 48, 49 and 161, with a re-sweep of
   blocked or empty pages. Three of the four delisting titles in the gap (BCN/CHAT/ICN/TRIG
   2018-10-09, CLOAK/MOD/SALT/SUB/WINGS 2019-02-15, BCHSV 2019-04-15) are already in that file. The
   fourth (*"…Distribute ETH to DGD holders and Delist DGD…"*, 2020-03-26) is not, but its wording
   does not match the discovery regex and DGD has no rows in the pair-state table, so it sits in no
   denominator. This is outside the truncation defect.
3. **A near-miss.** *"Notice of Removal of Trading Pairs – 2020/12/18"* is in the gap, but neither
   `PAIR_REMOVAL` regex matches it (both require "spot"). Because the scripts would not select it
   either way, it cannot move a frozen number. Its body is not cached anywhere, so its pair list was
   not inspected.

## 5. Recommendation

The truncation does not warrant re-opening any frozen H18 or H19 result. The scripts' own patterns
match only 32 of the 842 missing titles (31 rebrand titles and 1 quote-retirement title). They move
no verdict, gate or headline figure:

- H18.1b recall stays 197 / 201, with the same four true false negatives.
- H18.2's Monitoring Tag and mechanism outputs are untouched.
- The H18.3 point-in-time leakage gate stays PASS, and the ZAR knowable-from date is unchanged.
- The H19.0 crosswalk is identical.

The residual effects are one asset moving between two explained reason classes in H18.1b, two of
2,352 pair removals reclassified in H18.3, and two of 112,963 landmark rows with a ±1 change in
trailing removal counts. In both cases the change would come from a frozen rule misreading a title.

I recommend that the sponsor record this as a documented erratum with severity LOW rather than
order a re-run. If any downstream H18.3 model statistic is ever re-quoted at a precision where two
BTT landmark rows could matter, a sponsor-level re-check of that statistic alone is the proportionate
response. Separately, Contextual Alpha should use only the complete re-harvest and must not inherit
`data/raw/h18_1b/catalog_titles.parquet`.
