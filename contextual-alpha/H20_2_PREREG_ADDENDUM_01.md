# H20.2 — Pre-Registration Addendum 01 (disclosure only)

Written on 2026-10-19, immediately after `H20_2_FREEZE.json`. **It changes no rule, set, split,
metric, bar or verdict.** The frozen files keep their recorded hashes.

## Additional design-time exposure

`H20_2_FREEZE.json → state_at_freeze` describes H20.2 itself: no lifecycle row was read while
designing H20.2. The same AI agent session had earlier, in a different task, performed the read-only
H18 truncation impact assessment (`docs/H18_SNAPSHOT_TRUNCATION_IMPACT.md`, 2026-10-18). That
assessment read:

- rows of `H18_1B_FULL_DELIST_EVENTS.parquet`: the earliest `trading_end` (2018-10-12) and whether
  five tickers (ADX, ENG, REP, RPX, OCEAN) appear as events (only REP does, 2022-12);
- `H18_1B_FALSE_NEGATIVES.csv` and the frozen H18.1b recall figures (197 / 201);
- the H18.3 point-in-time class tables, including the counts of `QUOTE_RETIREMENT` removals and 2 BTT
  landmark rows' removal counts.

None of this concerns the relationship between any predictor and the outcome. No H18.3 model result
was read, then or now. The exposure is recorded alongside H20.2 §8 item 2 ("design-time knowledge")
because researcher ignorance is not claimed; structural outcome exclusion is.
