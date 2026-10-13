# Table 3 — Classes of silent failure that produced plausible outputs

These are classes of defect, not a list of mistakes. Each produced output that looked
reasonable, which is what makes the class worth naming. A software defect is recorded
separately from the economic question it was obscuring, and finding a defect is not
itself a research result.

| class | instance | what it produced | how it was detected | generalised lesson |
|---|---|---|---|---|
| catalog truncation | H18.1b: the source catalog did not cover pre-2022 notices | a universe of 84 full delistings that looked complete | cross-catalog expansion plus recall against candle-measured cessation | measure source reach; never infer absence of event from absence of record |
| date-format change | H18.1b: pre-2021 notices use slash dates | every trading_end before 2021 silently dropped | coverage discontinuity at a format boundary | a format change is a false data horizon until proven otherwise |
| ticker collision | H18.1b era rule compared gaps between first candles | 297 assets marked as reused tickers, none of them true | reproduced a known artefact from the previous family | asset-era keying, and test the era rule against known reuse cases |
| pagination without a delimiter | H19.1: S3 NextMarker is only returned with a delimiter | listings stopped at the 1,000 oldest keys | synchronization of 1.00 in 2023 and exactly 0.00 in 2025-26 | a suspiciously clean temporal pattern is a pagination symptom |
| timestamp-unit divergence | H19.1: spot archives in microseconds, futures in milliseconds for the same date | the spot leg landed outside any plausible range and the intersection was empty | first run reported spot coverage 2.7% | detect units per file by magnitude; two legs of one venue can differ |
| NaN truthiness | H19.0 identity guard | 125 valid mappings rejected | rejection count implausibly high | test for type, not for truthiness |
| zero-is-falsy gate logic | H19.0 churn rate, and the same defect in H17.0 | a perfect 0.0 churn read as a missing value and failed the gate | a passing metric produced a failing gate | compare against None explicitly |
| future-derived removal class | H18.2 to H18.3 amendment A1 and A2 | 28.7% of removals carried a class that used information from after the decision | classification changed under a backward-only window | a leakage test must cover feature classification, not only values and dates |
| right censoring | H18.3 administrative censoring at 2026-10-09 | landmarks without complete follow-up would have counted as non-events | 21,769 landmarks excluded once the rule was applied | state the censoring date in the pre-registration |
| event sharing across splits | H18.3 frozen splits | validation would have previewed 41 of the holdout's 86 events | measured directly on landmark dates | measure event sharing, do not assume date boundaries separate events |
| common-support collapse | H19.2 tagged-control matching | a design that passed every data check and could not be estimated | ceiling computed on the full pool with no sampling | demonstrate common support before freezing, not after |
| numerical instability | H18.3 sigmoid overflow | an exception rather than a wrong number | caught at runtime, fixed, development re-run | record the deviation; every number was unchanged to four decimals |
