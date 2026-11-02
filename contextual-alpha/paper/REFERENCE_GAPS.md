# Reference gaps

These claims, methods or framings would normally carry a citation. No reference was found for them
in the repository's verified bibliography
(`papers/falsification_first_alpha_discovery/release/references.bib`), and none has been
invented. Each item lists the exact claim and where it appears. In the current manuscript the claim
is either uncited or phrased without attribution. **Before release, each gap needs a source that is
read and verified (author, year, title, venue, DOI) or the claim must be removed.**

| # | manuscript location | claim or method needing support | what to look for |
|---|---|---|---|
| 1 | §7, `H20_2_INFERENCE_SPEC_A02.md` | the pigeonhole two-way cluster bootstrap is used as the primary interval | the original source for the pigeonhole bootstrap for two-way crossed random effects (attributed in the spec to "Owen 2007" — **unverified attribution; must be checked before it is printed**) |
| 2 | §7 | average precision / PR-AUC is preferred over ROC-AUC when positives are rare | a methodological source on precision–recall evaluation under class imbalance |
| 3 | §3, §4 | real-time macro data vintages (ALFRED) avoid revision look-ahead | the real-time data / data-vintage literature for macroeconomic research |
| 4 | §3, §4, §12 | models trained on later corpora can leak future knowledge into historical text features (transform-time look-ahead) | recent work on look-ahead bias in language-model or embedding features for financial prediction |
| 5 | §4, App. C | description of GDELT GKG (themes, tone computed at ingest) | the GDELT project's own documentation or paper |
| 6 | §7 | landmark (dynamic) prediction design for time-to-event outcomes | a landmarking reference from the survival-analysis literature |
| 7 | §7 | rolling-origin / expanding-window evaluation with an embargo | a forecasting-evaluation reference on rolling-origin evaluation and, separately, on purging/embargo for overlapping labels |
| 8 | §8.2, §11 | correlated observations require clustered inference; row counts overstate information | a cluster-robust inference reference |
| 9 | §1, §10 | public news/sentiment as a predictor in crypto markets (the premise being tested) | empirical studies using news, social-media or regulatory-event data to predict crypto outcomes; `yang2026delistings` (Coinness news, Reddit features, per its Table 5) is the only verified one in the repository |
| 10 | §1, §13 | Binance's own stated delisting review criteria | Binance's official delisting-criteria page (data source, not literature); quote the version in force, with access date |
| 11 | §2 contributions | any claim of novelty for the document-time / transform-time distinction or the staged framework | a targeted literature review. **The manuscript makes no novelty claim**, and none may be added without this review |

## Resolution (verification pass 2, 2026-10-19)

The table above is the original gap list, kept as history. Each gap's outcome is below. The sources
are documented in `REFERENCE_VERIFICATION.md`.

| # | outcome | how |
|---|---|---|
| 1 | **RESOLVED** | Owen (2007), *Ann. Appl. Stat.* 1(2):386–411, read in full. The "Owen 2007" attribution in the frozen spec is correct. The manuscript now describes the implementation as an *adaptation*: calendar blocks as the column entities, product weights, and a rank-based PR-AUC statistic where Owen's results cover means. It states that the results are an approximation, not a guarantee. The frozen procedure is unchanged. |
| 2 | **RESOLVED** | Saito & Rehmsmeier (2015), *PLoS ONE*, full text. The wording is "can be misleading under heavy class imbalance". |
| 3 | **RESOLVED** | Croushore & Stark (1999), FRB Philadelphia WP 99-4, full text, plus the ALFRED help page (official, accessed 2026-10-19). |
| 4 | **RESOLVED** | Glasserman & Lin (2023, arXiv) and Kelly et al. (2026, NBER WP 35247), full text. They are cited for the *risk* only. "Transform-time PIT" stays this paper's operational term and is not attributed to them. Glasserman & Lin's own in-sample finding (look-ahead not dominant) is respected: no magnitude is claimed. |
| 5 | **RESOLVED** | GDELT GKG Codebook V2.1 (official, dated 2/19/2015) supports 15-minute update batches, themes and tone. The "+15 minutes" admission rule is labelled as our own rule. |
| 6 | **RESOLVED** | Putter & van Houwelingen (2017), *Stat. Biosci.*, open-access full text. The manuscript says the design is landmark-*style* and fits no survival model. The original van Houwelingen (2007) was not readable and is not cited. |
| 7 | **PARTIALLY RESOLVED** | 7A rolling-origin evaluation: RESOLVED (Hyndman & Athanasopoulos 2021, §5.10). 7B purging/embargo: no primary source could be read (López de Prado 2018 is not openly available; only secondary sources were found), so **no citation was added**. The manuscript instead states the embargo's rationale from the paper's own label construction: a training row's 365-day outcome window must end before the test window, so no event labels both. This needs no external attribution. |
| 8 | **RESOLVED** | Petersen (NBER WP 11280, rev. 2006), full text, supports dependence across firms and across time. |
| 9 | **RESOLVED** | A balanced related-work paragraph (§2.1) was added. Its sources: Auer & Claessens (2018, BIS QR; effects and nulls), Shen, Urquhart & Wang (2019; volume and volatility yes, returns mixed), Steinert & Herff (2018; short-horizon, limited), and the previously verified Yang & Kwon. Kraaijeveld & De Smedt was rejected (not readable). |
| 10 | **RESOLVED** | Binance "Delisting Guidelines & Frequently Asked Questions" (official, published 2022-12-19, updated 2026-06-10, accessed 2026-10-19) is cited explicitly as **current** documentation that does not establish the criteria used in earlier sample years. |
| 11 | **RESOLVED (no novelty claim)** | The targeted review found an active point-in-time language-model literature (Kelly et al. 2026, verified; others seen only in search results and not cited). The contributions now state that none is claimed as new and position transform-time PIT against that literature. The staged design is described as applying design-before-outcome principles (Rubin 2008; registered reports). |

## Known inconsistencies in frozen materials (recorded, not edited)

- `H20_0_FEASIBILITY_REPORT.md` states 141,732 documents. `evidence/H20_0_METRICS.json →
  documents_total` gives 141,751, which equals the per-source sum. The paper uses the metrics value.
- `H20_0_FEASIBILITY_REPORT.md` states 33 registered sources. `CONTEXT_SOURCE_REGISTRY.csv` has 32
  rows. The paper uses the registry.
- The H18.3 pre-registration quotes Aldhahi & Alsamaani as reporting prospective AUC between 0.43
  and 0.79 across years. The verified bibliography note records only an approximately 0.68
  cross-validated AUC at abstract level. The paper cites the work without either figure.

These frozen files were not modified (H20.0 and H18.3 are closed scientific history).
