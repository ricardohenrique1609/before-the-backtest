# Table 2 — The support audit, with every quantity and its artefact

All values read from committed artefacts. No price column was loaded at any point (`usecols=[0, 5, 7, 8]`).

| quantity | value | artefact field |
|---|---|---|
| candidate events | 62 | H19_2_PREFREEZE_FEASIBILITY.md §1 |
| minimum controls per event, m | 20 | h19_2_prefreeze.json frozen_bars.MIN_CONTROLS |
| minimum confirmatory events, N_min | 40 | H19_2_PREFREEZE_FEASIBILITY.md §A7 |
| attainable support p10 / p25 / median / p75 / p90 | 0 / 0 / 1 / 2 / 57.3 | h19_2_prefreeze.json 2_controls_per_event |
| events below the floor | 52 | h19_2_prefreeze.json 3_events_with_fewer_than_20_controls |
| implied confirmatory sample, N* | 10 | h19_2_prefreeze.json 1_final_candidate_n |
| warned universe, ever | 134 assets across 28 notices | H19_2_PREFREEZE_FEASIBILITY.md Check 3 |
| full-pool ceiling per date | 0 to 27, median 7; 3 of 25 dates reach 20 | H19_2_PREFREEZE_FEASIBILITY.md Check 3 |
| eligible pool per date | min 177, median 327, max 380 | h19_2_prefreeze.json metadata_eligible_pool_per_date |
| leg availability (not binding) | 2,857 of 2,877 = 99.3% | H19_2_PREFREEZE_FEASIBILITY.md Check 1 |
| transition filter (never binds) | 0 events | H19_2_PREFREEZE_FEASIBILITY.md Check 2 |
| implied development / holdout | 9 / 1 | h19_2_prefreeze.json 7_development_holdout_after_exclusions |
| decision | N* = 10 < 40 → STOP before freeze | h19_2_prefreeze.json hard_sample_rule_A7 |
| price columns read | none; OHLC never entered memory | scripts/h19_2_prefreeze.py; h19_2_prefreeze.json no_price_field_loaded |
