# Reference verification (pass 2, 2026-10-19)

Every reference added in this pass was read at the level stated, from the source itself:
- full text: a publisher page, an open-access repository, an author/institution working paper or
  an arXiv reprint;
- official documentation: the issuing organisation's own page.

Nothing was cited from a search snippet, abstract aggregator, citation database or another paper's
bibliography.

Status values: `VERIFIED_FULL_TEXT`, `VERIFIED_OFFICIAL_DOCUMENTATION`, `VERIFIED_ABSTRACT_ONLY`,
`REJECTED`, `UNRESOLVED`.

## Added references

### owen2007pigeonhole
| field | value |
|---|---|
| reference_id | owen2007pigeonhole |
| gap_number | 1 |
| claim_supported | §7: the uncertainty interval adapts the pigeonhole bootstrap, which resamples row entities and column entities of a crossed design independently with replacement; its consistency results concern means and it is mildly conservative there |
| source_type | peer-reviewed journal (methodological) |
| authors | Art B. Owen |
| year | 2007 |
| title | The pigeonhole bootstrap |
| venue | The Annals of Applied Statistics 1(2), 386–411 |
| DOI_or_stable_URL | 10.1214/07-AOAS122 (read via arXiv:0712.1111v1 reprint) |
| access_date_if_web | — |
| full_text_or_abstract_read | full text (27-page reprint) |
| exact_supporting_section_or_page | §3.2 (definition: rows and columns sampled IID with replacement, independently; data = intersections); §4 (variance of totals and means, Theorems 1–2); p. 2 ("mildly conservative"); p. 5 (expected reliability extends to smooth functions of means) |
| verification_notes | **The attribution "Owen 2007" in the frozen H20.2 spec is correct.** The implementation is an adaptation, disclosed in §7: (a) the columns are 8 calendar blocks (fold test windows), not individual column entities; (b) row-weight = product of asset-era and block multiplicities, which is equivalent to Owen's intersection resampling; (c) the statistic is a weighted, rank-based PR-AUC difference, not a mean or smooth function of means, so Owen's results are an approximation, not a guarantee. The frozen H20.2/H20.3 procedure is not changed. |
| status | VERIFIED_FULL_TEXT |

### saito2015precision
| field | value |
|---|---|
| reference_id | saito2015precision |
| gap_number | 2 |
| claim_supported | §7: PR-AUC is primary because the positive class is rare and ROC-based summaries can be misleading under heavy class imbalance |
| source_type | peer-reviewed journal (methodological) |
| authors | Takaya Saito; Marc Rehmsmeier |
| year | 2015 |
| title | The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets |
| venue | PLoS ONE 10(3): e0118432 |
| DOI_or_stable_URL | 10.1371/journal.pone.0118432 |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full text (open access) |
| exact_supporting_section_or_page | Abstract (ROC interpretation "can be deceptive"); Results and Discussion, simulation; Conclusion (PRC plots recommended as most informative) |
| verification_notes | Supports the wording used, which is "can be misleading", not "is invalid" |
| status | VERIFIED_FULL_TEXT |

### croushore1999realtime
| field | value |
|---|---|
| reference_id | croushore1999realtime |
| gap_number | 3 |
| claim_supported | §2.1, §4: historical modelling should use the data vintage available at the decision date, not the later revised series |
| source_type | central-bank working paper (original real-time-data paper) |
| authors | Dean Croushore; Tom Stark |
| year | 1999 (June) |
| title | A Real-Time Data Set for Macroeconomists |
| venue | Federal Reserve Bank of Philadelphia, Research Department, Working Paper No. 99-4 |
| DOI_or_stable_URL | https://www.philadelphiafed.org/-/media/FRBP/Assets/working-papers/1999/wp99-4.pdf |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full text (93 pages; abstract and Section I read) |
| exact_supporting_section_or_page | Abstract (vintages = snapshots of data available in real time); Section I, p. 4 (studies should use "the original, unrevised data available to economic agents who were around at the time") |
| verification_notes | The 2001 *Journal of Econometrics* version was not read, so the working paper actually read is cited instead |
| status | VERIFIED_FULL_TEXT |

### alfred_help
| field | value |
|---|---|
| reference_id | alfred_help |
| gap_number | 3 |
| claim_supported | §2.1, §4, App. C: ALFRED archives vintage versions of US economic data so that past analysis can use data as available at the time |
| source_type | official documentation |
| authors | Federal Reserve Bank of St. Louis |
| year | n/a (current page) |
| title | Help \| ALFRED |
| venue | alfred.stlouisfed.org |
| DOI_or_stable_URL | https://alfred.stlouisfed.org/help |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full page |
| exact_supporting_section_or_page | "What is ALFRED®?"; "What is a Release and what are Release Dates?" |
| verification_notes | The page explains revisions and vintages but does not use the term "real-time period"; the manuscript does not attribute that term to it |
| status | VERIFIED_OFFICIAL_DOCUMENTATION |

### glasserman2023lookahead
| field | value |
|---|---|
| reference_id | glasserman2023lookahead |
| gap_number | 4 |
| claim_supported | §2, §2.1, §4: a language model trained on later data can carry knowledge of what followed a document into a historical feature (look-ahead bias) |
| source_type | preprint (established researchers; Columbia) |
| authors | Paul Glasserman; Caden Lin |
| year | 2023 |
| title | Assessing Look-Ahead Bias in Stock Return Predictions Generated By GPT Sentiment Analysis |
| venue | arXiv:2309.17322 [q-fin.GN] |
| DOI_or_stable_URL | https://arxiv.org/abs/2309.17322 |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full text (v1, HTML) |
| exact_supporting_section_or_page | Abstract; §1.1 (the model "already 'knows' something about events that followed the news article"); §2.4 (anonymisation) |
| verification_notes | **Cited only for the existence of the risk.** The authors' own in-sample result is that anonymised headlines did better (a distraction effect dominated), and that look-ahead is not a concern out of sample. The manuscript does not claim a magnitude. A later journal publication is reported elsewhere; it was not verified and is not cited. |
| status | VERIFIED_FULL_TEXT |

### kelly2026pit
| field | value |
|---|---|
| reference_id | kelly2026pit |
| gap_number | 4, 11 |
| claim_supported | §2, §2.1, §4, §6: LLMs trained on unrestricted corpora embed future information; point-in-time language models trained only on text up to each date avoid this by construction; such models are a possible future route for R3 |
| source_type | working paper (NBER; not peer-reviewed) |
| authors | Bryan T. Kelly; Semyon Malamud; Johannes Schwab; Teng Andrea Xu |
| year | 2026 (May) |
| title | Scaling Point-in-Time Language Models |
| venue | NBER Working Paper No. 35247 |
| DOI_or_stable_URL | http://www.nber.org/papers/w35247 |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full text (title page, abstract, introduction) |
| exact_supporting_section_or_page | Abstract, p. 2 |
| verification_notes | Shows that "point-in-time" text modelling is an established research direction, so **no novelty claim** is made for the document-time / transform-time distinction (Gap 11). The authors disclose consulting/employment at AQR. |
| status | VERIFIED_FULL_TEXT |

### gdelt_gkg_codebook_v21
| field | value |
|---|---|
| reference_id | gdelt_gkg_codebook_v21 |
| gap_number | 5 |
| claim_supported | §4, App. C: GKG records are produced in 15-minute update batches, with themes and tone assigned by GDELT's processing |
| source_type | official documentation |
| authors | The GDELT Project (PDF metadata author: Kalev Leetaru; no author printed on the page) |
| year | 2015 (dated 2/19/2015) |
| title | The GDELT Global Knowledge Graph (GKG) Data Format Codebook V2.1 |
| venue | data.gdeltproject.org documentation |
| DOI_or_stable_URL | http://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full document |
| exact_supporting_section_or_page | p. 1 (NLP algorithms applied to each document); p. 6 (GKGRECORDID encodes "the 15 minute update batch"; "T" marks Translingual); p. 8 (V1THEMES, V2ENHANCEDTHEMES); p. 10 (Tone definition, −100 to +100) |
| verification_notes | The "+15 minutes" admission rule is **our own** conservative rule; the manuscript says so and does not attribute it to GDELT |
| status | VERIFIED_OFFICIAL_DOCUMENTATION |

### putter2017landmarking
| field | value |
|---|---|
| reference_id | putter2017landmarking |
| gap_number | 6 |
| claim_supported | §7: landmark-style design; at each landmark the risk set is the subjects still at risk and predictors use information available at the landmark |
| source_type | peer-reviewed journal (methodological) |
| authors | Hein Putter; Hans C. van Houwelingen |
| year | 2017 (issue; published online 2016-07-11) |
| title | Understanding Landmarking and Its Relation with Time-Dependent Cox Regression |
| venue | Statistics in Biosciences 9(2), 489–503 |
| DOI_or_stable_URL | 10.1007/s12561-016-9157-9 (open access, PMC5711994) |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full text |
| exact_supporting_section_or_page | Introduction (landmark time point *s*; "subset of subjects at risk at *s*"; covariate value at *s* or history summary up to *s*); Theory ("survivors at risk at time *s*"; survival "from time *s* onwards") |
| verification_notes | The manuscript states explicitly that it fits a binary-outcome logistic model, not a survival model. The original van Houwelingen (2007) paper was not readable (HTTP 403) and is not cited. |
| status | VERIFIED_FULL_TEXT |

### hyndman2021fpp3
| field | value |
|---|---|
| reference_id | hyndman2021fpp3 |
| gap_number | 7A |
| claim_supported | §7: rolling-origin evaluation, where each test window's training data contain only earlier observations |
| source_type | textbook (established authors; open online edition) |
| authors | Rob J Hyndman; George Athanasopoulos |
| year | 2021 |
| title | Forecasting: Principles and Practice (3rd edition) |
| venue | OTexts, Melbourne |
| DOI_or_stable_URL | https://otexts.com/fpp3/ (§5.10: https://otexts.com/fpp3/tscv.html) |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full section |
| exact_supporting_section_or_page | §5.10 "Time series cross-validation" ("evaluation on a rolling forecasting origin"; "no future observations can be used in constructing the forecast") |
| verification_notes | Supports rolling-origin evaluation only. It is **not** used for the embargo (Gap 7B). |
| status | VERIFIED_OFFICIAL_DOCUMENTATION |

### petersen2006standard
| field | value |
|---|---|
| reference_id | petersen2006standard |
| gap_number | 8 |
| claim_supported | §7: observations of one asset and of one period are correlated, and ignoring the correlation biases conventional standard errors |
| source_type | working paper (NBER; the version read) |
| authors | Mitchell A. Petersen |
| year | 2006 (April 2005, revised June 2006) |
| title | Estimating Standard Errors in Finance Panel Data Sets: Comparing Approaches |
| venue | NBER Working Paper No. 11280 |
| DOI_or_stable_URL | http://www.nber.org/papers/w11280 |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full text (abstract, introduction) |
| exact_supporting_section_or_page | Abstract ("residuals may be correlated across firms and across time, and OLS standard errors can be biased"); Introduction (firm effect, time effect; OLS standard errors biased downward under a firm effect) |
| verification_notes | The paper concerns regression standard errors. Here it supports only the general dependence argument; the bootstrap itself is covered by Owen. The later journal version was not read and is not cited. |
| status | VERIFIED_FULL_TEXT |

### auer2018regulating
| field | value |
|---|---|
| reference_id | auer2018regulating |
| gap_number | 9 |
| claim_supported | §2.1: regulatory news moves crypto prices, most strongly news about legal status; unspecific official warnings had no measurable effect; this is a contemporaneous event study, not prediction |
| source_type | central-bank publication (BIS Quarterly Review) |
| authors | Raphael Auer; Stijn Claessens |
| year | 2018 (September) |
| title | Regulating cryptocurrencies: assessing market reactions |
| venue | BIS Quarterly Review, September 2018 |
| DOI_or_stable_URL | https://www.bis.org/publ/qtrpdf/r_qt1809f.htm |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full article (BIS site) |
| exact_supporting_section_or_page | main text and conclusion (legal-status news strongest; "unspecific general warnings have no effect"; event study of regulatory news events) |
| verification_notes | Included for balance. It reports both effects and null effects. |
| status | VERIFIED_FULL_TEXT |

### shen2019twitter
| field | value |
|---|---|
| reference_id | shen2019twitter |
| gap_number | 9 |
| claim_supported | §2.1: tweet counts predicted next-day trading volume and realised volatility, with weaker and mixed evidence for returns |
| source_type | peer-reviewed journal (accepted version read) |
| authors | D. Shen; A. Urquhart; P. Wang (initials as printed by the repository) |
| year | 2019 |
| title | Does Twitter predict Bitcoin? |
| venue | Economics Letters 174, 118–122 |
| DOI_or_stable_URL | 10.1016/j.econlet.2018.11.007 (accepted version: https://centaur.reading.ac.uk/80420/) |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full text (accepted version, extracted in-browser) |
| exact_supporting_section_or_page | Abstract; Results (returns: weak evidence at the 10% level, mixed Granger results); Conclusion (tweets "significant drivers of Bitcoin RV and volume, but not returns") |
| verification_notes | "Mixed" wording chosen because the results report both weak and Granger-significant evidence for returns |
| status | VERIFIED_FULL_TEXT |

### steinert2018altcoin
| field | value |
|---|---|
| reference_id | steinert2018altcoin |
| gap_number | 9 |
| claim_supported | §2.1: Twitter activity and sentiment predicted short-horizon altcoin returns in a short sample, for a selected subset of coins, with low out-of-sample fit |
| source_type | peer-reviewed journal |
| authors | Lars Steinert; Christian Herff |
| year | 2018 |
| title | Predicting altcoin returns using social media |
| venue | PLoS ONE 13(12): e0208119 |
| DOI_or_stable_URL | 10.1371/journal.pone.0208119 (open access, PMC6279012) |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full text |
| exact_supporting_section_or_page | Abstract; Materials and methods (71 days; selection of coins with the strongest connection); Discussion (low test-set R²); Conclusion (short timeframe) |
| verification_notes | Positive but limited evidence, included for balance with the null and mixed results |
| status | VERIFIED_FULL_TEXT |

### binance_delisting_faq
| field | value |
|---|---|
| reference_id | binance_delisting_faq |
| gap_number | 10 |
| claim_supported | §1: Binance's **current** delisting FAQ lists legal/compliance, project going-concern, market and ethical risk among the factors it considers; it does not establish the criteria applied in each sample year |
| source_type | official documentation (venue) |
| authors | Binance |
| year | page published 2022-12-19, updated 2026-06-10 |
| title | Binance Delisting Guidelines & Frequently Asked Questions |
| venue | binance.com support FAQ |
| DOI_or_stable_URL | https://www.binance.com/en/support/faq/detail/e5a9718ccb794acda1c48db5c71753e4 |
| access_date_if_web | 2026-10-19 |
| full_text_or_abstract_read | full page (read in the built-in browser; cookie banner not accepted) |
| exact_supporting_section_or_page | FAQ 1 ("Binance considers a variety of factors… Legal/Compliance risk… Project going-concern risk… Market risk… Ethical risks") |
| verification_notes | **Current documentation, not historical.** The manuscript states this explicitly. Earlier criteria (2018–2022) were not verified. |
| status | VERIFIED_OFFICIAL_DOCUMENTATION |

## Previously verified references newly cited in this pass

| reference_id | gap | note |
|---|---|---|
| yang2026delistings | 9 | Already in the bibliography; the previous pass recorded "Full text obtained; Table 5 read". The claim that its predictors include news counts and topics and social-media metrics rests on that pass, recorded in `H18_3_PREREG.md` §1 (Coinness news counts and topics; Reddit metrics). **Not re-read in this pass.** |
| rubin2008design, jbef_registered_reports, bailey2014deflated, bedowska2025zombie, fantazzini2022creditrisk, aldhahi2026regime, ramossilva2026beforebacktest | 9, 11 | Reused unchanged at the access level recorded in their notes. They are cited only for claims those notes support. No metadata error was found. |

## Rejected candidates

| candidate | gap | reason |
|---|---|---|
| van Houwelingen (2007), "Dynamic prediction by landmarking in event history analysis", *Scand. J. Statist.* | 6 | Publisher page returned HTTP 403; full text not read. Replaced by the open-access Putter & van Houwelingen (2017). — REJECTED |
| van Houwelingen & Putter (2008), *Lifetime Data Analysis*, doi:10.1007/s10985-008-9099-8 | 6 | Behind publisher authentication; not read. — REJECTED |
| López de Prado (2018), *Advances in Financial Machine Learning*, Wiley, ch. 7 (purging/embargo) | 7B | Book not openly readable; SSRN related paper returned HTTP 403; only secondary descriptions found (Wikipedia, blogs, library docs). Not cited. — REJECTED |
| Kraaijeveld & De Smedt (2020), Twitter sentiment and crypto prices, *JIFMIM* | 9 | No openly readable copy found; only secondary summaries. — REJECTED |
| Croushore & Stark (2001), *Journal of Econometrics* version | 3 | Journal version not read; the 1999 working paper actually read is cited instead. — REJECTED (as a separate entry) |
| Petersen (2009), *Review of Financial Studies* version | 8 | Journal version not read; the NBER working paper actually read is cited instead. — REJECTED (as a separate entry) |
| Look-Ahead-Bench (arXiv:2601.13770); Gao, Jiang & Yan (arXiv:2512.23847); PALM (arXiv:2609.30316) | 11 | Seen only in search results during the novelty review; not read. Not cited. They are evidence only that the area is active, which is already supported by Kelly et al. — REJECTED |
