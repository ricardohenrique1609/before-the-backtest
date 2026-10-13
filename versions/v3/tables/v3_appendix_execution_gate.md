# Table 5 — H19 execution and feasibility gate

## H19.0 — execution and shortability (12 of 15, verdict PARTIAL PASS)

| criterion | bar | measured | result |
|---|---|---|---|
| 1 §22 — >=80 Tier-1 USD-M derivative events at T0 | >= 80 | 75 | **FAIL** |
| 2 §22 — >=60 CLEAN public-information events | >= 60 | 63 | PASS |
| 3 §22 — clean sample spans >=4 calendar years | >= 4 | 4 | PASS |
| 4 §22 — no year above 40% of the clean sample | <= 40% | 0.4603 | **FAIL** |
| 5 §23 — derivative instrument identity >=99% | >= 99% | 1.0 | PASS |
| 6 §23 — listing/termination time reconstruction >=95% | >= 95% | 1.0 | PASS |
| 7 §23 — market-data availability around T0 >=95% | >= 95% | 1.0 | PASS |
| 8 §25 — >=90% of clean events TRADING >=60 min after T0 | >= 90% | 1.0 | PASS |
| 9 §25 — >=75% of clean events TRADING >=6h after T0 | >= 75% | 1.0 | PASS |
| 10 §24 — >=90% small-capital sanity ($1k <=1% of median hourly) | >= 90% | 0.5079 | **FAIL** |
| 11 §26 — derivative notice precedes spot in <=25% | <= 25% | 0.0769 | PASS |
| 12 §28 — no major survivorship differential | <= 10.0 pp | 0.0 | PASS |
| §23 — T0 precision usable for intraday alignment >=90% | >= 90% | 1.0 | PASS |
| §27 — no unexplained missingness gap above 10 pp | <= 10.0 pp | 0.0 | PASS |
| §38 — gold >=40 double reviewed, churn <=5% | >=40 and <=5% | {'double_reviewed': 40, 'churn': 0.0} | PASS |

## H19.2 — pre-freeze feasibility (verdict STOP, BLOCKED BEFORE FREEZE)

| criterion | bar | measured | result |
|---|---|---|---|
| H19.2 §A7 — confirmatory events | >= 40 | 10 | **FAIL** |
| H19.2 §A7 — matched controls per event | >= 20 | median 1; 52 of 62 events below 20 | **FAIL** |
| H19.2 §A8-A10 — valid 15-minute transitions | >= 73 | median 92; 1 of 62 events below 73 | PASS |
| H19.2 §A11 — VWAP fields available | fallback not triggered | 62 of 62 (100%) | PASS |
| H19.2 — leg availability | >= 95% | 2,857 of 2,877 legs (99.3%) | PASS |

No pre-registration was frozen for H19.2 and no price column was ever read, so no
economic inference about H19-P3A exists. H19.0's status is PARTIAL PASS: the sample
gate fails for the small-capital thesis, and no return was computed for any event.
