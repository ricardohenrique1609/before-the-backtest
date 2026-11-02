# AUTHOR RESPONSE — referee report V1

Response to `REFEREE_REPORT_V1.md` (2026-11-02). Every change uses existing frozen artefacts only.
No model was refitted, and no result, number, verdict or frozen file changed. Section numbers refer
to the revised manuscript.

## Major concerns

| point | change | where |
|---|---|---|
| **MC1(a)** Move the week-level mechanism to the design | The question is restated in its operational form: the primary comparison can gain only by ranking weeks, i.e. by predicting *when* delistings cluster, not *which* asset is delisted. | §2 Question; §7 "What the comparison can detect"; abstract; §10 point 3 now points to §7 |
| **MC1(b)** Independent label windows | Reported: 104 out-of-fold weeks with a 52-week label horizon hold about two non-overlapping label windows. | §7; abstract; §11 |
| **MC1(c)** Post-hoc detectable increment | Reported and labelled post hoc: SE ≈ 0.026 from the frozen interval, an 80%-power detectable increment of about +0.07 PR-AUC, roughly 30% of M0. | §8.3; §11; ledger C123–C125 |
| **MC1(d)** No statistical-feasibility gate | Stated: the pre-registration named low power but neither quantified it nor set a stop rule. In the author's judgement such a gate would have flagged the comparison as underpowered. | §7; §11; ledger C140 |
| **MC1(e)** Companion-paragraph wording | Rewritten. Both papers fix their design before outcomes; only *Before the Backtest* gates statistical support, which this study did not do. | §1 |
| **MC2(a)** Δ(λ) path | New Table 8, read from `H20_3_EXPLORATORY_RESULTS.json`; no refit. | §9, Table 8 |
| **MC2(b)** Pooled and mean-of-folds Δ | Table 7 now shows both for every row, including the primary (−0.0095 pooled, −0.0055 mean of folds). | Table 7 |
| **MC2(c)** Replace "selection optimism" | For the logistic model the +0.0273 is a pooling effect: the mean-of-folds Δ at λ = 1000 is +0.0003. "Selection optimism" stays only for the fold-selected configurations, where it applies. | §9; §10 |
| **MC2(d)** Penalty dependence | Stated plainly: the development sign is not robust to the penalty, while the LCUV sign is negative under every specification reported. | §9; §11; abstract; conclusion |
| **MC3** Amendment under-reported | §7 now gives the v1 rule (λ selected from the grid), its outcome (λ = 1000 for both arms, development Δ +0.0273, LCUV Δ −0.0167), and that the verdict under it would also be PRE-REGISTERED NULL because S4 fails. Table 7 carries the v1-rule verdict. | §7; Table 7; ledger C120–C122 |
| **MC4** Title and question overreach | The subtitle now names the context tested: "A pre-registered test of macro, US regulatory and crypto-attention context on Binance full-asset delistings". The abstract's first paragraph states the scope, and so does the §2 question. The title is kept as the general question, as the referee allowed. | front matter; abstract; §2 |
| **MC5(a)** Availability statement | Rewritten to match the public package: what a reader can verify (hashes, every number) and what not (raw corpora, H18 inputs, the order of events), and that the scripts do not run end to end from the package. | Data and code availability |
| **MC5(b)** Timing attested by the author | Disclosed as a limitation. | §11; ledger C141 |
| **MC5(c)** Third-party timestamp of the H20.2 freeze | **Not done.** A deposit (OSF or Zenodo) is an external publication, so it is the author's decision. It is time-sensitive: it must happen before the PROSPECTIVE_CONFIRMATION outcomes mature after 2027-09-28. | open, for the author |
| **MC6** AI use undisclosed | New "Use of AI tools" section: what the agent did, what the author decided, and that no language model built any feature. | new section; ledger C142 |

## Minor concerns

| # | change |
|---|---|
| 1 | Figures renumbered in order of appearance; the funnel moved to §1. The PNGs are byte-identical under their new names. |
| 2 | Markdown tables print λ, Δ, ≥, ≤, true minus signs and fixed decimals (0.2300, not 0.23). The CSVs keep raw values. |
| 3 | Table 7 describes configurations in words and gives both arms' LightGBM selections. |
| 4 | The weak LightGBM baseline (M0 pooled 0.174 against 0.2300) is stated in §9. |
| 5 | The LCUV interval is defined: a two-way asset-era × month bootstrap, 2,000 replicates, 3.05% of replicates positive, informational because S3 is defined on development. |
| 6 | S7's era blocks are defined in §7 and in Table 6. |
| 7 | The development calibration slopes (M0 0.67, M2 0.52) are reported in §8.3, with why S5 does not assess them. |
| 8 | The Figure 4 caption states the base rates (5.82% and 11.79%) and that levels are not comparable across blocks. |
| 9 | `bedowska2025zombie` gained the year 2026 from its Crossref record (issued January 2026). Entries without an author lead with their title. The Binance FAQ stays "n.d.": the page is undated as a work, and its update date is given in the entry's note. |
| 10 | The production notes left the References section; the related-work sentence moved to §2.1. |
| 11 | The abstract now opens with the premise as the paper's own statement. |
| 12 | Proper quotation marks. |

## One finding the referee report did not anticipate

The mean-of-folds split for LightGBM is positive: +0.0116 for the a-priori configuration and
+0.0107 for the fold-selected one. So the LightGBM development gain is not purely a pooling effect.
A nonlinear model can let week-level context interact with asset-level features and reorder assets
within a week. §9 reports this, together with the two qualifications that bound it: the baseline is
weak, and the gain did not carry into the locked block (LCUV Δ −0.0080 and −0.0030). It does not
change the verdict, and it is not presented as a context effect.

## Not changed

- The verdict, every frozen artefact, and every reported number.
- The title's main line, as the referee allowed.
- The third-party timestamp (MC5(c)), pending the author's decision.
