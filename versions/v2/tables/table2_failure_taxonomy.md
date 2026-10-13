# Table 2 — Research failure taxonomy

Each row is instantiated by an experiment in this paper; the examples carry their
family tag so the claim can be traced to its artefact.

| failure mode | mechanism | observable symptom | QIE example | defense |
|---|---|---|---|---|
| universe survivorship | candidates that left the listed universe are absent from the sample | returns look high and the risk factor looks protective | H13: 52.9% of candidates have no current ticker | rebuild the universe from a point-in-time source and bound the bias explicitly |
| outcome-selected join | the join key exists only for surviving entities | coverage correlates with the outcome | H17.0: identity passes at 98-99% while price history fails | run a missingness differential by outcome for every join |
| semantic drift | a standardized form carries non-standard meaning | field-level accuracy collapses on a human gold set | H15: 100% identity, 5 of 22 criteria | gold set with two passes, the first persisted before the second |
| category conflation | one document type covers several economic events | the event count is implausibly large | H18.1: 102 of 1,422 pair events are a full delisting | classify to the economic unit, not the document unit |
| identity reuse | a ticker is reassigned to a different asset | an entity appears to be relisted or to have impossible history | H18.1b: asset-era keying; H19.0: SKY | key on asset-era, never on ticker alone |
| catalog truncation | the source index is not the population | coverage has a clean horizon at a round date | H18.1b: 84 to 201 events, 39 missed before 2022 | measure source reach against the source's own reported total |
| future-derived labels | a classification window reaches past the decision date | label changes when the window is made backward-only | H18.3: 676 of 2,352 removals (28.7%) change class | classify as of the decision date and audit classification, not only values |
| event sharing across splits | one outcome event supports landmarks in two blocks | validation performance tracks the holdout too closely | H18.3: 41 of 86 holdout events shared under the original boundaries | one-horizon embargo, and drop a block that cannot be separated |
| contaminated control | the control window sits inside the treatment process | the event looks normal relative to its own history | H19.1: 62 of 63 same-asset windows inside the wind-down | require the control to be outside the process, and say so before freezing |
| common-support collapse | the matched cell is empty at the required strata | n falls far below the pre-registered floor | H19.2: median 7 eligible controls against a floor of 20 | compute the ceiling on the full pool before freezing the design |
| execution assumption | a documented event is assumed tradable | the sample survives every data gate and dies at capacity | H19.0: 201 to 32 under a US$1,000 order | impose instrument existence, materiality and capacity at T0, in that order |
| served-but-untraded data | a candle exists without a trade | a leg looks liquid while its trade count is zero | H19.1: spot has no trades in a median 25% of window minutes | require both legs to have traded in each bucket |
