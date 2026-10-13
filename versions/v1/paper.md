# Falsification-First Alpha Discovery: How Data Construction, Survivorship, Semantic Errors and Execution Constraints Manufacture Trading Strategies

**Working paper.** Version 1, 2026-10-11.

---

## Abstract

Quantitative research on trading strategies is usually defended against overfitting: out-of-sample
testing, multiple-testing corrections, and pre-registration of model specifications. We document a
class of failure that occurs earlier, before any model is fitted, and that these defenses do not
address. Universe construction, event semantics, identifier stability, timestamp attribution, join
design, point-in-time validity, control support and execution feasibility each determine whether an
apparent opportunity exists at all. We report a sequence of seventeen hypothesis families (H13 to
H19.2) run as a single research program on free public data, in which each family had to pass
explicit, pre-specified gates before an economic test was permitted. Four cases carry the argument. A
micro-cap screen with a median 12-month outcome of +18.3% is reduced to +3.7% under central
assumptions, and to 0.0% under severe ones, once the 52.9% of candidate issuers with no current
ticker are restored; the inverted risk gradient in its returns is the fingerprint of the hole rather
than evidence about the risk factor. A venue-owned archive is shown to retain delisted instruments
that third-party aggregators drop, which permits a delisting universe to be rebuilt from 84 to 201
events, with the 119 missing events attributable to catalog coverage rather than to absence of the
events. A pre-registered predictive test that is positive in all eight rolling-origin folds, with a
pooled ΔPR-AUC of +0.0270 (+13.5% relative), is declared `NULL` when its cluster-bootstrap interval
crosses zero, its materiality gate fails, and its single-use holdout reverses sign at −0.0075. And a
design with near-perfect data quality is stopped before pre-registration was frozen, because
requiring twenty controls matched on both liquidity and the venue's public risk warning is
arithmetically impossible on a venue that has ever tagged 134 assets; the median number of eligible
matched controls per event date is 7, and no price column was ever read, so the family carries no
economic conclusion. We organise these outcomes into a six-label result taxonomy that distinguishes
an economic null from a data-gate failure, an infrastructure block, an identification block and an
execution failure, and we extract ten methodological principles. The contribution is not a strategy.
It is evidence that apparent alpha can be created or destroyed by the dataset, semantic and execution
assumptions themselves, and a set of audits that make those assumptions falsifiable before a model is
fitted.

**Keywords:** survivorship bias, point-in-time data, event studies, pre-registration, common support,
execution feasibility, research methodology, cryptocurrency delisting.

---

## 1. Introduction

The standard concern in quantitative strategy research is that a model will fit noise. The standard
defenses follow from that premise: hold out data, correct for multiple testing, penalise complexity,
pre-register the specification, and report out-of-sample results. All of these act on the step where
a model meets a dataset.

This paper is about the steps before that one. In the research program we report, the decisive
question was almost never which model was fitted. It was whether the dataset represented the
population it claimed to represent; whether the events in it meant what their labels said; whether
the identifiers were stable; whether the dates were attributable to a decision; whether the join
preserved the outcome distribution; whether the features could have been known when the decision was
made; whether a comparison group existed; and whether the instrument could be traded once the
information was public. Each of these is a hypothesis. Each can be false in a way that produces
output which looks entirely reasonable.

The distinction matters because the two failure classes have different signatures. An overfitted
model produces a result that degrades out of sample. A badly constructed dataset produces a result
that is *stable*, *replicable*, and wrong: re-running the pipeline reproduces it exactly, a second
researcher using the same source reproduces it, and out-of-sample testing on the same contaminated
universe confirms it. Survivorship in the universe does not look like noise. It looks like an effect.

We report a sequence of hypothesis families from a single research program, the Quant Intelligence
Engine (QIE), run on free and public data by one researcher. The program's governance requires that
each family pass explicit gates — data, semantic, point-in-time, identification and execution —
before any economic quantity is computed, and that any predictive test be pre-registered, hashed and
committed before execution. Families that fail a gate are recorded as untested rather than as
negative economic results.

Four families carry the argument, and they fail in four different places. H13 is a micro-cap screen
whose apparent performance is traced to the construction of its universe. H18 is a sequence that
rebuilds a venue's delisting universe from the venue's own records, and then pre-registers and
executes a predictive test that returns a null. H19.0 shows that a documented market event need not
be a tradable one. H19.2 shows that a design can have excellent data and still fail to identify
anything, because the comparison group it requires does not exist.

Our contributions are four classes of demonstrated failure mode (§2.3), a formal result taxonomy
(§3), ten methodological principles with linked cases (§9), and a complete artefact trail: every
numerical claim in this paper is mapped to a field in a committed artefact
(`CLAIM_EVIDENCE_MATRIX.csv`), and every family's pre-registration, gate, audit and scripts are
indexed (`ARTIFACT_INDEX.md`).

We do not claim that the economic hypotheses we examined are false. In most cases we did not test
them. That is the point.

---

## 2. Research governance

The protocol described here was in force for every family reported. It is not presented as optimal;
it is presented because the results in §§4–8 are only interpretable against the rules that produced
them.

### 2.1 Ingestion and time

**Immutable raw ingestion.** Raw documents and raw market data are written once and never edited.
Derived datasets are rebuilt from raw by committed scripts. A correction is a new derivation, not an
in-place edit.

**Two clocks, minimum.** `event_time` is when the economic event occurred or was stated to occur;
`ingest_time` is when the research program could first have observed it. Any feature used to predict
an outcome at `event_time` must be constructible from information whose `ingest_time` precedes it.
The program later found that two clocks are insufficient for event data: announcement time, stated
cessation time and actual cessation time are three distinct quantities, and they disagree (§5.3).

**Point-in-time reconstruction.** Where a venue or registry publishes a current state, that current
state may not be used as history. The instrument universe, the route topology and the risk set are
rebuilt from records that existed at each date.

### 2.2 Gates, pre-registration and the handling of results

**Data and semantic gates.** Before an economic hypothesis may be selected, the family must pass a
gate with criteria fixed in advance: coverage, identity accuracy, date accuracy, semantic accuracy
against a manually labelled gold set, and outcome-differential missingness. Gold sets are built in
two passes, the first persisted before the second begins, with reviewer churn reported.

**Pre-registration.** A predictive test is specified in full — estimand, risk set, splits, features,
baseline, challenger, metrics, decision rule and verdict vocabulary — then frozen, hashed with
SHA-256, and committed. Only then may it be executed. Amendments are separate documents, also frozen
and hashed, and are written before the relevant results are seen.

**Frozen splits and a single-use holdout.** Splits are fixed in the pre-registration. The holdout is
opened once, and the artefact records that it was opened once.

**Bars are not moved.** A criterion that fails as written fails, including when the researcher later
judges the criterion itself to be poorly specified (§6.5 contains exactly such a case).

**Deviations are recorded, not absorbed.** A bug found during execution is documented in a deviation
record with its effect on every reported number, rather than fixed silently.

**Execution before P&L.** Returns are not computed until the family has demonstrated that the
instrument existed, traded, and could absorb the intended order at the relevant time.

### 2.3 The four contribution classes

The failures we document group into four classes, used throughout as C1–C4.

- **C1 — data construction.** Survivorship can enter through the universe; blocked upstream it
  reappears in the market-data join; archive ownership determines whether dead instruments remain
  observable; and pagination, vocabulary or unit changes can fabricate historical coverage.
- **C2 — semantics.** Standardized form is not standardized meaning; pair removal is not asset
  delisting; a ticker is not a permanent identity; a date is not a datum until attributed.
- **C3 — point-in-time and researcher leakage.** Future-derived classifications; controls built from
  the future; outcome-selected risk sets; event overlap between splits; contaminated historical
  controls; common-support collapse.
- **C4 — execution.** A documented event is not a tradable event; data retention is not instrument
  existence; a served candle is not a traded market; a clean sample can collapse under capacity.

### 2.4 `NO_TEST` and `NO_TRADE` as outputs

Two outputs are treated as valid terminal states rather than as failures to report.

`NO_TEST` means the family did not reach an economic test, because a gate specified in advance was
not met. It makes no claim about the economic hypothesis.

`NO_TRADE` means the strategy's own rules produced no position, or the execution gate showed that no
tradable instrument existed. It is not a zero return; it is an absence of a position.

Collapsing these into "the strategy did not work" destroys the information that distinguishes them
(§3).

---

## 3. A taxonomy of research outcomes

A single verdict vocabulary is used across the program. Six labels, and the families that carry them.

| label | meaning | what may be concluded | families |
|---|---|---|---|
| `ECONOMIC REJECT` | tested against pre-registered bars and rejected | the specific implementation does not meet the bar; the economic question may remain open | H13 |
| `PRE-REGISTERED NULL` | the design and the data survived; the predictive claim did not | the claim, as pre-registered, is not supported | H18.3 |
| `DATA-GATE FAIL / UNTESTED` | a data or semantic gate failed; no economic test ran | nothing about the economics | H14.1, H14.2, H14.3, H15, H16.1 |
| `INFRASTRUCTURE BLOCKED` | the substrate was unavailable at the required quality | nothing about the economics | H17.0, H18.0 |
| `IDENTIFICATION BLOCKED` | data adequate; the design does not identify the effect | nothing about the economics | H19.2 |
| `EXECUTION FAIL` | the event is real and the instrument traded; capacity fails | the opportunity is not accessible at the stated size | H19.0 |

The distinction between the first two rows and the remaining four is the substantive one. Only
`ECONOMIC REJECT` and `PRE-REGISTERED NULL` carry information about an economic claim. The other four
are statements about the research program's ability to measure, and treating them as evidence about
markets would be an error in the opposite direction from the one this paper documents.

Table 1 is the registry of all families with their gate counts; Table 2 is the failure taxonomy by
mechanism; Table 3 lists the classes of silent failure that produced plausible output.

**Figure 1** shows the stages a hypothesis must survive and where each family's outcome was decided.
**Figure 2** shows each family's gate outcome as the family's own gate JSON recorded it.

---

## 4. Data construction before modeling (H13–H17)

This section is organised by failure mechanism rather than chronology.

### 4.1 Survivorship in the universe: a spectacular backtest (H13)

The question was whether reading financial statements separates securities that are cheap because
they are ignored from those that are cheap because the cash will be consumed. The screen is a
net-net: price below net current asset value, among US micro-caps, built from public filings.

The screen's raw output is attractive. Across 472 screen observations, the median 12-month outcome is
**+18.34%**, with a win rate of 65.5%. A naive portfolio construction turns a small initial stake
into a large one. If the research had stopped there — as a backtest with out-of-sample periods and a
sensible-looking rule would have permitted — the conclusion would have been that the screen works and
that the fundamental filter adds to it.

Two audits change the conclusion.

**The universe audit.** Of the 5,604 CIKs that ever reported positive net current asset value in the
frames data, **2,965 (52.9%) have no current SEC ticker**. The hole is monotone in cohort age: 68%
for 2011, 55% for 2015, 42% for 2018, 27% for 2022, 14% for the 2023–26 holdout, and 4% for 2026. A
300-company sample of the missing was classified from EDGAR forms: 48% delisted or dark, 31% acquired
or merged, 19% stopped filing, 2% still filing. The fate mix was measured, not assumed. Any return
statistic computed on the priced subset is conditioned on survival to the sample's end.

**The fundamental-filter audit.** The filter does not improve the screen. The best filter beats the
raw screen by **+1.9 pp** against a pre-registered bar of +10 pp. Requiring a cash runway of at least
eight quarters — the most intuitive form of the filter, and the one that most directly encodes the
hypothesis — lowers the median to **+2.47%** on 150 observations, 15.9 pp *worse* than the raw
screen.

The two audits connect through a single diagnostic. In the priced sample the risk gradient inverts:
cheap-and-low-burn minus cheap-and-high-burn is **−23.46 pp**, meaning high-burn names returned more.
This is what a survivorship hole looks like when the hole correlates with the variable under study.
High-burn companies that actually died left the price sample; "high burn" in the return test
therefore means "high burn *and survived*", a selected and favourable subpopulation. The inversion is
the fingerprint of the bias, not a finding about cash burn.

A separate, survivorship-free test was run to measure the mechanism directly. On a panel of **1,197
companies** — of which **50.1% no longer have a ticker**, which is the entire point of the design —
cash burn predicts disappearance monotonically: P(GONE) by burn tertile is **11.90% / 15.95% /
23.04%**, a T3−T1 difference of **+11.14 pp** with a confidence interval of [+5, +17] pp, against a
pre-registered bar of +20 pp. The discriminating power is weak: AUC **0.5930**. Dilution gives +7 pp
against a +10 pp bar. Fates in the panel: 901 alive, 203 gone, 93 acquired.

> **Two denominators.** 52.9% is the share of the 5,604-CIK *screen candidate universe* with no
> current ticker. 50.1% is the share of the 1,197-company *Test A panel*. They measure different
> populations and must not be used interchangeably.

Finally, bias bounds. Re-adding the missing companies under labelled assumptions, using the measured
fate mix, moves the median from +18.3% to **+3.66%** under mild and central assumptions and to
**0.0%** under severe ones. The holdout underperformed a micro-cap benchmark by 4.9 pp.

**Verdict.** `ECONOMIC REJECT` of the implementation. The predictive mechanism exists but is too weak
for the pre-registered bar, and the return result is not usable because the universe is
survival-conditioned. **The economic hypothesis about net-nets is unresolved**: establishing it would
require a survivorship-free *price* panel for delisted US micro-caps, which the free sources used do
not provide (§11, and `PAPER_OPEN_QUESTIONS.md` Q2).

The generalisable statement is narrow and strong: *a spectacular backtest is a bug candidate until
the universe is audited*, and *an inverted risk gradient in returns is a diagnostic for selection,
not a discovery about risk*.

### 4.2 Standardized form is not standardized meaning (H15)

Schedule 13D filings are a standardized form. Activists disclose a position, state an intention in
Item 4, amend as the campaign develops, and the campaign ends in a resolvable corporate outcome. The
form's standardisation is what makes the family attractive.

The universe is large and the identity layer is clean: **94,036 accessions** from 2010 to 2026, with
**502 filings read** (0.53% of the universe) covering **497 campaigns**. Issuer identity,
reporting-person identity and acceptance timestamps all resolve at **100%**.

The gate passes **5 of 22** criteria. What fails is meaning: the intention stated in Item 4, its
evolution across amendments, and the mapping from campaign to corporate outcome. The form is
standardized; what the form says is not.

**Verdict.** `DATA-GATE FAIL / UNTESTED`. No economic test was run, and the paper makes no claim
about activist event-driven returns.

### 4.3 Identifiers, date attribution and joins (H16.1)

A binary regulatory catalyst requires three things: an ex ante universe of decisions with a known
target date, the decision date itself, and a reliable map from the applicant to a traded security.

The discovery layer performs well. Full-text search over regulatory filings yields **16,444 candidate
filings** across **1,728 issuers**, 2010–2026, with no coverage cliff (549 to 1,374 filings per
year); **6,107 announcement documents** were read, producing **1,108 decision cycles** across 407
applications, of which **496** carry an approval against a bar of 120.

The gate passes **2 of 23**. The binding failures are attribution and joining: which date is the
decision, which document establishes it, and which traded security belongs to the applicant. A date
appearing in a document is not yet a datum; it becomes one when it can be attributed to a specific
decision by a specific issuer at a specific time.

**Verdict.** `DATA-GATE FAIL / UNTESTED`.

### 4.4 Survivorship migrates downstream (H17.0)

H17.0 is the clearest demonstration that fixing survivorship in one layer does not remove it from the
research.

The family's seed was deliberately built from filings rather than from a current security list:
**851,552 insider transaction records** across 17 quarters produce **1,870 issuer-date
observations** over 1,579 issuers, about 110 per year. The identity layer then passes at high
accuracy: point-in-time symbol resolution **99.36%**, symbol matching the filing **98.4%**, share
class identifiable **99.6%**.

The family is nonetheless blocked, at **14 of 32** criteria, by *historical market data*, and the
decisive measurement is one that uses no outcome label at all. Splitting the 1,870 observations by
whether the issuer has a current ticker — a split that cannot be contaminated by a fate
classification — pre-event price and liquidity coverage is **87.1%** for the 1,212 observations with
a current ticker and **9.1%** for the 658 without: a gap of **78.0 pp**. Overall coverage is 60.2%,
and only **1 of 17** sampled years reaches the 85% floor the gate required.

The survivorship problem was removed from the universe and reappeared, undiminished, in the price
join. Note also what this does *not* say: the gate's own fate labels were themselves audited and
found unreliable for one class, with a dominant error of a delisting notice filed for a non-common
security being read as the issuer delisting. The 78.0 pp measurement is reported precisely because it
does not depend on those labels.

**Verdict.** `INFRASTRUCTURE BLOCKED`.

### 4.5 What H14 contributes, and what it does not

H14 built a 6,491-event universe of Brazilian corporate special situations and **never selected a
hypothesis**; it is recorded as `OPEN`. Three sub-families were gated and failed: takeover-offer
terms resolution (price precision 86.1% against a 95% bar; recall 83.8% against 85%), judicial
reorganisation (1 of 7 criteria; state accuracy 62.9%), and recapitalizations (0 of 9; share
reconciliation 51.1% on the broad universe but 9.8% on the 904 material cases). The last of these is
itself a lesson about denominators: a reconciliation rate computed on the full universe and one
computed on the economically material subset differ by a factor of five, and only the second is
relevant to a strategy that would trade the material cases.

**Verdict.** `OPEN` for the parent; `DATA-GATE FAIL / UNTESTED` for the three sub-families.

---

## 5. Reconstructing lifecycle data from the venue's own records (H18.0b, H18.1, H18.1b)

The H17.0 block raised a specific question: is there any market where the *venue* retains the history
of instruments that no longer trade? This section answers it, and then shows how much work remains
after the answer is yes.

### 5.1 Who owns the record determines what stays observable (H18.0, H18.0b)

A three-venue probe tested whether a cryptocurrency exchange serves historical OHLCV for spot pairs
it has delisted. The gate required two of three venues to pass; Binance scored 4 of 9, Bybit 1 of 9,
OKX 2 of 9, so the probe **failed as a gate**.

The informative result is inside the failure, and it is the opposite of H17.0's. Binance's
active-versus-delisted retrieval gap is **0.0 pp**: 28 of 30 active pairs and 28 of 30 delisted pairs
retrieved, delisted hourly completeness 100%, and no candles served after the delisting instant.

A deeper confirmation run (H18.0b) passed **14 of 14** criteria — the first pass in the program's
data-gate sequence — and established an official universe of 440 notices, 228 spot-removal notices,
and **1,403 unique pairs with both a symbol and a stated trading end**.

This is a structural point rather than a fact about one company. A third-party aggregator has
commercial reason to drop an instrument nobody trades; a venue's history is the venue's own book.
Prior work on cryptocurrency survivorship attributes the bias explicitly to reliance on aggregators
that provide historical data only for currently listed assets, and quantifies the resulting
distortion [Ammann et al. 2022]. The venue-side measurement here is the same asymmetry seen from the
other side.

**Verdict.** `INFRASTRUCTURE BLOCKED` for H18.0 as a gate; `PASS` for H18.0b as a substrate
confirmation. Neither is a claim about alpha.

### 5.2 Pair removal is not asset delisting (H18.1)

With a usable substrate, the next question is what the venue's removal notices actually describe.

Of **1,422 pair-removal events**, resolving into **1,271 asset-lifecycle episodes** across 532 unique
assets, only **102 pair events and 84 episodes** are an asset leaving spot entirely — **7.2%**. The
remainder are minor pair removals (688), quote migrations (510), fiat pair removals (95) and partial
delistings (25). **Figure 3a** shows the classification.

Treating "delisting notice" as a single event type would have produced a sample in which 93% of the
events are not the economic event the research intended to study. Notice horizons are also narrower
than they appear: the median is 48 hours, p10 is 24 hours, and no event in the sample had less than
24 hours' notice.

The gate passed **11 of 12** criteria, failing only on category viability: at 84 episodes the
full-delisting category fell below its pre-specified minimum of 100. That failure is what motivated
H18.1b. The audit also recorded that the documentary period begins 2022-02-17 and that earlier years
are **unavailable, never zero events** — a distinction that turns out to matter.

**Verdict.** `PARTIAL PASS`.

### 5.3 The catalog is not the population (H18.1b)

H18.1b asked one question: was the 84-event universe truncated by its source catalog? It was, and by
more than half. The validated universe is **201 asset-level full-delisting events across nine
calendar years**, 2018-10-12 to 2026-09-24, with **119 events missed** by the previous construction —
more than it had held. **Figure 3b** shows the decomposition: 75 events sat in a different catalog
category, 39 predate the previously used catalog, and 5 were visible only in the pair universe.
Eighty-two of H18.1's 84 episodes appear in the new universe; the two that do not (AUD, GBP) are
fiat quote assets rather than delisted assets.

Reaching that universe required repairing several defects, each of which had produced plausible
output. They are reported here as *classes* (Table 3), because each generalises.

**Catalog coverage.** The notices live across several catalogs with different vocabularies, and
pre-2022 notices use different wording. Searching one catalog with current vocabulary yields a
universe with a clean horizon at a round date, which reads as "the venue started delisting in 2022".

**Date-format change.** Notices before 2021 write dates with slashes. A parser that accepts only the
later format silently dropped every stated trading end before 2021 — the third occasion in this
program on which a format change manufactured a false data horizon.

**Unit of analysis.** The economic unit is the asset-decision, not the announcement: one notice can
delist several assets. Correcting this expanded the event count, and a subsequent correction for
date fragments misread as tickers *reduced* it, because those events were spurious.

**Product-word collision.** A filter intended to remove non-spot notices matched the bare word
"alpha", deleting a legitimate announcement covering five assets. The repair was to anchor the filter
to the notice's subject rather than to a word anywhere in the title.

**Pagination.** A transient empty page was treated as the end of a catalog, truncating the harvest
and deleting the 2018–2019 notices. The repair was a retry, a slow re-sweep, and a coverage guard
that refuses to write the universe below 99% of the catalog's self-reported total. The guard fired:
the retained refusal record shows catalog 49 at 4,392 of 4,442 titles (0.9887) with one blocked page,
and the universe was not written. Blocked pages were recorded as `ACCESS_BLOCKED` and never
circumvented.

**Identity reuse.** An era rule intended to separate an original asset from a later asset that took
the same ticker compared gaps between consecutive pairs' *first* candles rather than tracking the
running last candle, so it fired whenever a new route was added to an asset that had never left. In
the previous family the same defect had flagged **297 episodes** as relistings when the true count
was **zero**; here it reproduced on four assets. After the correction, the committed data audit
carries an explicit correction note naming them — the only post-hoc edit made to a historical
artefact in this work, and it is marked as a correction rather than applied silently. The corrected
statement is the more interesting one: only two tickers in the universe are genuine reuse, and on
this venue reuse appears as the *absence* of any candle trace for the earlier asset, not as two
cohorts in the same series.

The repaired universe was then validated rather than asserted. Recall against the previous
classifier is **0.9762**; recall against candle-measured cessation is **0.9801**, with four true false
negatives. Of 257 assets that stopped being served, 197 carry a full-delisting announcement and the
remaining 60 are explained: 34 pair removals only, 11 official rebrands or merges, 7 quote assets, 4
with no official record found, and 4 ticker reuses. Route validation confirms zero remaining routes
for 189 events, with 5 confirmed by document and 4 showing a vestigial tail. A gold set of **100
events** with **40 double-reviewed** returned all-field accuracy of **1.0** and reviewer churn of
**0.0**, and the audit records that several PASS-1 fields are partly self-confirming, with the
independent evidence being the PASS-2 re-fetch and the route state.

Two diagnostics sit below their 0.99 bar, at **0.9851** and **0.9847**, and are named rather than
smoothed. Both are the same three events — OST, RCN and WPR, all with a stated cessation of
2021-07-16 — where the venue continued trading materially for three days past the instant its own
notices state. The recorded dates are faithful to the documents. The venue's behaviour was not. This
is the cleanest instance in the program of a principle that recurs: **announcement time, stated
cessation time and traded reality are three different quantities**.

**Verdict.** `STRONG PASS`, 19 of 19 criteria, with two named diagnostics below bar.

---

## 6. A pre-registered predictive test (H18.2, H18.3)

This is the program's flagship example of a convincing development result that was rejected.

### 6.1 Selecting the question before seeing a result

H18.2 performed the literature review, the mechanism map and the hypothesis selection with **zero
returns computed**. The literature establishes what is not available as a novelty claim: generic
price-and-volume machine learning on this venue's delistings has been done, with features enumerated
in the closest study [Yang & Kwon 2026]; low volume predicting asset death has been done, with a high
bar [Będowska-Sójka et al. 2025]; the definition of asset death is itself a modelling choice with
consequences, and the best model depends on asset age and horizon [Fantazzini 2022]. What none of
these use is the venue's own market structure: the set of trading routes the venue maintains for an
asset, and how that set contracts over time.

The selected hypothesis, **H18-P1**, is that among assets trading on the venue's spot market, the
point-in-time contraction of the venue's native routes predicts a higher hazard of full-asset
delisting, incrementally to price, volume, liquidity and asset age.

Two design decisions were made at this stage and are load-bearing.

First, the risk set was rebuilt **without passing through the announcement layer**: the symbol
universe comes from the venue's own instrument archive (3,745 archive directories plus 4 live-only
symbols, 3,749 symbols over 835 base assets). A risk set assembled from announcements would be
outcome-selected by construction. The alternative — comparing delisted assets against a sample of
survivors — would reintroduce precisely the attrition bias quantified in the survivorship literature.

Second, the mechanism map was built from official venue documentation only and was **deliberately not
converted into features**, so that the mechanism could not silently become the model.

### 6.2 The estimand and the design

**Estimand.** A landmark formulation: for asset-era *i* at weekly landmark *t*, the outcome is 1 if a
full-asset delisting announcement occurs in (*t*, *t*+365 days]. This is a dynamic risk at a fixed
horizon, not a discrete-time hazard, and it was chosen because it matches the decision a user of such
a model would face.

**Censoring.** Administrative censoring at **2026-10-09**. Landmarks without complete 365-day
follow-up are ineligible: of 134,732 panel asset-weeks, **112,963 are eligible** and **21,769** are
excluded for incomplete follow-up. Omitting this rule would have counted incomplete follow-up as
evidence of non-events.

**Risk-set entry** is 90 days after an asset-era's first served candle, which removed a 6.22 pp
coverage differential — diagnosed as listing-age arithmetic rather than as data loss — reducing it to
0.09 pp.

**Baseline and challenger.** The baseline is deliberately strong: it absorbs price, volume,
liquidity, age, the asset's **current route state**, and a point-in-time calendar regime (18
features). The challenger adds at most four route-*history* features (23 features total). The
comparison is therefore not "route information versus nothing" but "route history versus everything
already observable, including the current route state".

**Splits.** Development 2018–2023, an embargoed 2024, and a single-use holdout from 2025 to the last
eligible landmark (2025-10-06). Eight frozen quarterly rolling-origin folds lie entirely inside
development, and the penalty parameter may be chosen only there.

The split design is itself a finding. Measured **as landmark dates**, the originally specified
boundaries shared outcome events across blocks: train and validation shared 16 events, and validation
and holdout shared **41 of the holdout's 86**. A one-horizon embargo repairs the first boundary and
cannot repair the second, because validation outcomes reach beyond the last landmark with complete
follow-up. Reporting a validation block would therefore have half-previewed the holdout, so the
validation block was **dropped** and its role given to the rolling-origin folds. In the frozen
design, development and holdout share **zero** events.

### 6.3 Point-in-time repair before execution

The structural leakage audit found that the removal classifications inherited from H18.2 were not
point-in-time. Under a strictly backward-looking window, **676 of 2,352 removals (28.7%)** change
class. One class was worse than the aggregate suggests: **314 of 390** quote-retirement labels had
been assigned using information published after the decision, with a median lag of 49 days.

The repair was written as a frozen amendment, before any model was fitted and before the holdout was
opened, and it made exactly three changes: batch-prune classification fixed as of the removal date;
quote retirement derived strictly from notices available at the time; and a **directional veto**
requiring the holdout ΔPR-AUC to be positive for any support label. The amendment was hashed and
committed before execution.

The generalisable lesson is that a leakage test that checks values and dates is insufficient. The
values here were correct and the dates were correct. The *classification* used the future.

### 6.4 Development results

The development block contains 78,244 landmark weeks over 522 asset-eras, with 4,555 positive
landmarks from **110 unique events**, a base rate of **5.822%**.

> **Event accounting.** Development has 110 unique outcome events, the dropped embargo year 72, and
> the holdout 86. These sum to more than the 201-event universe, and must not be read as 268 distinct
> delistings: with a 365-day horizon, one announcement can be the outcome of landmarks in more than
> one block. What the design requires is that development and holdout share none, and the frozen
> artefact records that they share zero.

All eight rolling-origin folds are positive: ΔPR-AUC of +0.0361, +0.0119, +0.0238, +0.0441, +0.0424,
+0.0229, +0.0479 and +0.0824, with a median of **+0.0393**. Pooled out of fold, baseline PR-AUC is
**0.20038** and challenger PR-AUC is **0.22736**, a difference of **+0.0270**, or **+13.46%**
relative, over 37,782 landmarks and 440 asset-eras. Top-decile lift improves from 3.9909 to 4.7899
(+20.0%). The Brier score improves, from 0.05332 to 0.05138. Incidence is monotone across the
contraction buckets frozen ex ante: 4.647%, 8.904%, 9.125%.

This is a convincing development result by the standards normally applied. Every fold agrees, the
effect is material, calibration improves, and the dose-response is monotone in the pre-specified
direction.

The pre-registered decision rule nonetheless fails, in two places (Table 4).

**Scientific support fails on criterion 2.** The cluster bootstrap — 2,000 replications resampling
**asset-eras**, not asset-weeks, so that temporal rows stay together, seed 20261010 — gives a 95%
interval of **[−0.0074, +0.0628]**, which includes zero. The one-sided evidence is **93.45%**, short
of the pre-registered 95%. With 110 unique events across 440 clusters, the interval is wide. The bar
was not moved.

**Materiality fails on criterion 5.** The calibration-slope shift is **0.1948** against a bar of 0.10.

### 6.5 The holdout, and a researcher error that did not determine the verdict

The holdout was opened once. On 86 events with a base rate of 11.792%, baseline PR-AUC is **0.30007**
and challenger PR-AUC is **0.29254**: **ΔPR-AUC = −0.00753**. The sign reverses. The directional veto
added by the amendment triggers. Top-decile lift on the holdout does improve, 2.8672 to 2.9777, and
is reported because it is part of the pre-registered output, but it does not enter the decision rule.

**Figure 4** shows the eight development folds and the holdout, drawn so that the holdout is
visually separated: it is a different evaluation role, not a ninth fold.

**Verdict.** `PRE-REGISTERED NULL`. The claim — that the venue's route-contraction history adds
temporally stable incremental information about future full delisting, beyond price, volume,
liquidity, age and *current route state* — is not supported. The verdict is triply determined: the
bootstrap interval, the materiality gate and the holdout each suffice on their own.

Three further results explain *why*, and they matter more than the headline.

**Most of the headline was the baseline specification.** The falsification suite shows that a
market-only variant reaches PR-AUC 0.2184 against the full challenger's 0.22736, and that adding the
current route state to a market baseline reaches the same 0.2184. The incremental content of route
*history*, once current state is present, is small.

**A placebo confirms the specification is not generating signal from nothing.** A placebo shifted by
1,092 days and a within-week permutation both fail to reproduce the effect. The shift length is
itself a recorded detail: 1,095 days, the initially chosen value, is not a multiple of seven and
returned zero coverage on a weekly landmark grid.

**One bar was mis-specified by the researcher, and it did not decide the outcome.** Materiality
criterion 5 penalises any calibration-slope movement of 0.10 or more — including improvement. The
challenger's calibration slope is closer to 1 in **all eight folds** (0.440→0.693, 0.524→0.742,
0.590→0.833, and so on), so the criterion failed on a better-calibrated model. The bar was written by
the researcher and failed as written; it was not renegotiated after the result, and the flaw is
carried forward to the next pre-registration rather than patched into this one. **The verdict does
not depend on it:** scientific-support criterion 2 and the holdout each fail independently. This
paper does not describe the result as having nearly passed.

A separate deviation is recorded for completeness: a numerical overflow in the logistic link was
found during execution, fixed, and development re-run. Every reported number was unchanged to four
decimal places.

---

## 7. From a documented event to an executable one (H19.0)

H18.1b produced 201 documented full-asset delistings. H19.0 asked a question that precedes any return
calculation: when the market received the information, did a tradable short actually exist?

The answer to the narrow question is yes. In **all 63** clean events, the perpetual futures contract
kept trading through every observed window — 5 minutes, 30 minutes, 60 minutes, 6 hours and 24 hours
after the announcement — and the execution window exceeded three days in every case.

The funnel to get there is the section's point (**Figure 5**).

**201 documented events → 75 with a Tier-1 USDⓈ-M perpetual live at T0.** The reduction is instrument
existence *at the event*, not today. The program's rules forbid using current instrument lists as
history, because a contract listed now may not have existed then, and a contract that existed then
may have been terminated since. Both directions were present.

**75 → 64 materially shortable at T0.** A contract whose archive contains candles at T0 is not
necessarily a market in which an order would have executed. Materiality here requires minutes with
actual trading after T0, not merely a served candle. This is the third occurrence of the same
distinction in the program.

**64 → 63 clean public-information events.** One event had already been signalled by a derivative
notice before the spot announcement and is therefore not a clean information event. The notice
census behind this step is itself bounded: across the 201 events, 12 carry a derivative notice after
the spot announcement, 5 before it, and for **184 no derivative notice was found**. That last figure
is a limit of the official surfaces reached, **not 184 events proven to have had no notice**, and the
announcement-ordering subgroup is therefore declared not estimable rather than null.

**63 → 32 feasible for small capital.** Imposing a sanity rule that a US$1,000 order be at most 1% of
the median hourly notional leaves **32** events, 50.8% of the clean sample. The liquidity
distribution explains it: 31 of the clean events trade below US$100k per hour, 30 between US$100k and
US$1m, and 2 above US$1m.

Three further results support the funnel rather than the thesis.

**Terminated derivatives are retained.** Of 17 terminated and 67 current derivative contracts, both
groups are observable at 1.0, with zero contracts carrying an empty archive. Missingness differentials
by year, liquidity bucket, timestamp precision and notice order are all **0.0 pp**. Data retention is
excellent — and it is not the same thing as the instrument having existed.

**An identity guard rejected one mapping.** The event concerns an asset delisted in 2021; the archive
symbol with the same ticker belongs to a different asset that took the ticker in 2025. Asset-era
keying caught it. A ticker-keyed join would have silently substituted a live asset for a dead one.

**Margin shortability is `UNKNOWN`, not zero.** No official keyless surface exposes historical margin
eligibility or borrow availability, and inferring it from current support is forbidden by the same
rule that forbids current instrument lists as history. The funnel is therefore a **lower bound** on
shortability.

**Verdict.** `PARTIAL PASS`, 12 of 15 criteria. The three failures are the Tier-1 count (75 against a
bar of 80), the concentration of the clean sample in its largest year (46.0% against a 40% bar), and
the small-capital sanity rule (50.8% against a 90% bar).

> **What this section does not claim.** No return, carry, holding period or P&L was computed for any
> event. Nothing here implies that shorting delistings is or is not profitable. The claim is narrower
> and verifiable: a short existed and stayed open, and for a US$1,000 order it was plausibly
> accessible in 32 of the 63 clean events.

The central sentence: *a documented market event is not a tradable event until the relevant
instrument is shown to remain accessible after public knowledge time.*

---

## 8. Excellent data, failed identification (H19.1, H19.2)

The final case is the one in which nothing was wrong with the data.

### 8.1 The question and its design constraints (H19.1)

The question is whether the derivative market moves before the spot-delisting announcement in a way
the spot market does not — an incremental, derivative-specific signal in the window from 24 hours to
1 hour before the announcement.

The literature does not answer it, and does not supply a safe prior. Leadership between spot and
perpetual markets in this asset class is contested and venue-dependent; one study finds a mid-tier
venue Granger-causing the venue studied here in 62% of windows. The equity literature supplies the
*mechanism* — insiders sell before delistings — but no study tests it with a derivative leg in this
market. Three mechanisms were registered with explicit rivals: anticipatory derivative trading (the
only one under which the hypothesis is true), common fundamental deterioration (the default, given a
median 1,036 days of wind-down), and derivative-market mechanics, which no available design can
exclude.

The wording is bounded by a measured fact: **52 of the 62 usable events already carried a public risk
warning before the announcement**. The permitted term is therefore *anticipatory price discovery*.
This paper does not use the term "insider trading" for these events and makes no causal claim about
private information.

Data feasibility is excellent. Spot 1-minute coverage is **100%**, perpetual 98.41%, and
synchronized minutes in the primary window 98.41% on average with a median of 100%. Mark price, index
price, premium index, funding and open interest are all 98.41%. **62 of 63 events are usable against
a bar of 50**; the single failure is an asset whose derivative is a coin-margined contract, so a
USDⓈ-M path correctly returns nothing for it.

Two design modifications were forced by measurement, and both are themselves findings.

**The control could not be the asset's own history.** With a median of 1,036 days from first pair
removal to the announcement, the window from 180 to 14 days before the event sits *inside* the
wind-down for **62 of 63 events**; only one is uncontaminated. Availability was essentially perfect
(100% and 98.2%); the problem is contamination, not data.

**The grid had to require trading on both legs.** Spot has no trades in a median **25%** of the
primary window's minutes — p25 6%, p75 54%, p90 66% — and more than half the window is empty for 19
of 63 events, against **0.42%** for the perpetual. Forward-filling a flat spot price would have
manufactured precisely the derivative-specific divergence the hypothesis looks for.

Two defects were found and recorded at this stage, both of which had produced plausible output.
Pagination of the archive listing continued from a marker the storage service only returns when a
delimiter is set, so listings stopped at the 1,000 oldest keys and recent events read as uncovered;
the signature was synchronization of 1.00 in 2023 and exactly 0.00 in 2025–26. And the two legs of
the comparison are stored in **different time units** — the spot archive in microseconds and the
futures archive in milliseconds for the same date — so reading both as milliseconds placed the spot
leg outside any plausible range and emptied the intersection. The first run reported spot coverage of
2.7% and a median synchronization of 0.0, which would have concluded that no test was possible, on a
researcher error. The microsecond fact was already recorded in the program's own notes from the
previous family.

**Verdict.** `SELECT` with three pre-specified and flagged modifications. Still zero returns: the
feasibility probe loaded only open time, volume and trade count, so the price columns were never read
into memory.

### 8.2 The pre-freeze feasibility check (H19.2)

The program's order is strict: finalise the pre-registration, run only feasibility checks that carry
no price, freeze, hash, commit, and only then load price. The feasibility check is what stopped the
family.

The confirmatory design requires each event to be matched to controls in the same liquidity band
**and** the same public-risk-warning state, with a minimum of **20** matched controls, a minimum of
**73** valid 15-minute both-legs-traded transitions, and a floor of 40 confirmatory events.

The result is **a final confirmatory n of 10**. Of 62 clean candidate events, **52 fall below the
20-control floor** (one of which also falls below the transition floor), leaving ten. The
controls-per-event distribution is bimodal: p10 0, p25 0, **median 1**, p75 2, p90 57. Events whose
asset was not tagged find large pools; events whose asset *was* tagged find almost none — and 52 of
the 62 event assets were tagged.

Three checks establish that this is structural rather than a sampling artefact (**Figure 6**).

**Availability is not the constraint.** Of 2,877 non-event legs evaluated, **2,857 (99.3%)** clear
the 95% availability bar.

**The transition grid never binds.** Zero events had at least 20 candidates of which fewer than 20
survived the shared-transition test. The matching cell is empty before the grid is reached.

**The ceiling is arithmetic.** Computed on the **complete** eligible pool with no sampling, the
number of assets that were simultaneously tagged, still listed, not yet delisted and carrying both a
live perpetual and a live spot route ranges from 0 to 27 across the announcement dates, with a
**median of 7**. Only 3 of 25 dates reach 20 — and that is before the liquidity band is matched at
all. The cause is the size of the tagged universe: the venue has tagged **134 assets in total, ever,
across 28 notices**, a universe verified against six notice vocabularies, with a different product
(an innovation tag applied to 71 notices) correctly excluded. Evaluating more candidates cannot
repair it: raising the per-date evaluation from 120 to the full pool would move the median matched
cell from 1 to roughly 3.

Everything else the design specified came through: the 15-minute both-legs-traded grid is validated
with a median of 92 valid transitions of 91 possible consecutive pairs and only one event below the
floor; volume-weighted price fields are available for **62 of 62 events**, so the specified fallback
is not triggered; per-file timestamp-unit detection worked; and point-in-time control eligibility was
implemented with the draft's look-ahead rule removed.

After deterministic exclusions the design would have had **9 development events and 1 holdout event**.
A one-event holdout is not a holdout.

**Verdict.** `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL`.

> **What exists and what does not.** No pre-registration was frozen. No SHA-256 was computed. No
> price column was ever read: the loader requests open time, base volume, quote volume and trade
> count, and the OHLC columns never entered memory, so no return, VWAP, abnormal score, basis or
> funding direction could be computed even by accident. **There is therefore no economic inference
> about this hypothesis at all** — it is not null, and it is not rejected. The absence of a frozen
> pre-registration file and of any hash for it is itself the evidence that the family stopped where
> it says it stopped.

The options the check hands back were enumerated with their costs: drop the warning-state matching
and control for it statistically; lower the control minimum; restrict to the most recent year; or
replace the control concept. The second is forbidden by a frozen bar. The third destroys the split
and still leaves too few events. The fourth was already shown infeasible, since same-asset history is
wind-down-contaminated. The first preserves a confirmatory design and is a real weakening of
identification, because the public warning is the main observable signal and matching on it was what
kept the comparison honest. That decision belongs to the research program, not to this paper
(`PAPER_OPEN_QUESTIONS.md` Q1).

The principle: **covariate adjustment cannot manufacture common support.** Two individually
reasonable requirements — match on the observable warning, and require twenty controls — are jointly
impossible on this venue, and no amount of statistical sophistication applied afterwards changes the
fact that the cells are empty.

---

## 9. General principles

Each principle is stated as a proposition and linked to the case that established it.

**P1. The identifier is the experiment.** A ticker is a lease, not an identity. Asset-era keying
caught a reused ticker that would have substituted a live asset for a dead one. *(H18.1b, H19.0)*

**P2. A date is not a datum until it is attributed.** A date in a document becomes data when it can
be tied to a specific decision by a specific issuer at a specific time. *(H16.1, H18.1b)*

**P3. Every join needs its own outcome-differential audit.** Measure whether coverage correlates with
the outcome being studied, at each join, separately. *(H17.0, H18.1b, H19.0)*

**P4. Who owns the record determines whether dead instruments remain observable.** An aggregator has
no reason to keep what nobody trades; a venue's history is its own book. *(H18.0b versus H17.0)*

**P5. Event time, knowledge time, cessation time and execution time are different clocks.** Three
events in the validated universe traded materially for three days past the cessation instant their
own notices state. *(H18.1b, H19.0)*

**P6. A served candle is not a traded market.** Zero-volume candles are served; orders do not execute
against them. *(H18.1b, H19.0, H19.1)*

**P7. Common support must be demonstrated, not assumed.** Compute the ceiling on the full pool before
freezing a matched design. *(H19.2)*

**P8. A positive development result is not evidence until a frozen out-of-sample evaluation
survives.** Eight of eight folds positive, and the holdout reversed the sign. *(H18.3)*

**P9. A data-gate failure is not an economic rejection.** Five families in this program were never
tested; none of them says anything about the markets they would have studied. *(H14.1–H14.3, H15,
H16.1, H17.0)*

**P10. `NO_TEST` and `NO_TRADE` are valid research outputs.** Reporting them as such preserves the
information that a single "it did not work" destroys. *(§3)*

---

## 10. Implications for quantitative research

**Academic backtests.** Replication of a result on the same vendor universe does not test the
universe. Where a study's sample is assembled from a source that retains only currently listed
entities, the survivorship correction is not a robustness check but a precondition; the magnitude of
the distortion in one documented cryptocurrency sample is 0.93% annualised value-weighted and 62.19%
equal-weighted [Ammann et al. 2022], and in our own micro-cap case it is the difference between
+18.3% and 0.0%.

**Retail and small-capital systematic research.** The execution funnel in §7 is the specific warning:
a sample can survive every data check and still lose half its events to a capacity rule that a
professional desk would rarely encounter. Capacity must be imposed at the event date, with the
instrument's own measured liquidity.

**Machine learning on financial panels.** Three of our findings bear directly on ML practice. First,
the leakage test must cover feature *classification*, not only feature values and dates: 28.7% of
our removal labels changed class under a strictly backward window while every value and date was
correct. Second, event sharing between splits is not prevented by date boundaries when the outcome
has a horizon; measured as landmark dates, our originally specified boundaries shared 41 of 86
holdout events. Third, cluster the bootstrap at the unit that generates the dependence — here the
asset-era — and expect the interval to be wide when the number of *events* is small, however many
rows the panel has: 37,782 landmarks carry only 110 events.

**Event studies.** Classify to the economic unit, not the document unit. Only 7.2% of the removal
notices in our venue sample are the event most readers would assume the phrase describes.

**Alternative data.** The source's own reported totals are a measurable quantity; use them. Catalog
coverage, pagination behaviour, vocabulary drift and storage-unit changes each produced, in this
program, a plausible but false picture of history.

---

## 11. Limitations

These are stated without softening.

**One research program, one codebase, one researcher.** Every result shares a single set of habits
and blind spots. The defects reported in Table 3 were found by this program's own audits, which means
the undetected defects are also this program's.

**Venue concentration.** H18 and H19 rest on one cryptocurrency venue. The substrate findings are
specific to a venue that retains its delisted instruments, and the §5.1 contrast with two other
venues is based on a nine-criterion probe, not on a deep audit of those venues.

**Free and public data only.** No paid vendor data, no institutional order-book archive, no
consolidated historical quote data. Several blocks — notably H17.0 — might not occur with
institutional data, and we cannot establish whether they would.

**Small effective event samples.** The decisive statistics rest on 110 development events and 86
holdout events in H18.3, 63 clean events in H19.0 and 62 candidate events in H19.2. Wide intervals
are a property of the samples, and we report them rather than narrowing the inference.

**Judgement-based gates.** Criteria were written by the researcher before seeing results, but they
were written by *this* researcher. The H18.3 calibration bar is a documented instance of a
poorly-specified criterion; others may exist and may not have failed visibly.

**Historical margin eligibility is unavailable.** The H19.0 funnel is a lower bound on shortability,
and no part of this paper should be read as establishing that the margin route did not exist.

**Literature access.** Several works were available only at abstract or metadata level, and are
flagged as such in the bibliography. We do not imply full-text reading where it did not occur.

**H19.2 never tested its price hypothesis.** It has no economic result, and the design decision it
hands back is unresolved.

**H13's economic question is unresolved.** We rejected an implementation. We did not establish
anything about net-net investing.

**Generalisation.** The negative results are about these designs on these data. They do not establish
that the underlying economic phenomena are absent, and a reader who takes them that way is making the
same category error, in reverse, that this paper is about.

**H8 is excluded by design.** One family in the broader program — a slow multi-asset trend strategy —
survived the same falsification process and was moved to a paper portfolio run monthly under a frozen
rule. It is mentioned here only to establish that the framework does not reject everything. Its
performance is out of scope and is reserved for a separate paper; mixing it into this one would
convert a methodological argument into a performance claim.

---

## 12. Conclusion

The research program reported here spent most of its effort on questions that are usually treated as
preliminary: what is in the universe, what do the events mean, which identifier is stable, which date
is the decision, what could have been known, what is the comparison group, and whether the instrument
could be traded. In four of the families, one of those questions decided the outcome. In none of them
did the choice of model.

The strongest form of the argument is the pair of opposite cases. A micro-cap screen produced a
median outcome of +18.3% that survives re-running, replication and out-of-sample testing on its own
universe, and is reduced to 0.0% under severe assumptions once the missing half of the universe is
restored; nothing about the model was wrong. And a pre-registered predictive test produced eight
positive folds out of eight, a material effect size and improved calibration, and was declared null
by a decision rule written before the data were seen; nothing about the data was wrong.

Between them sit two further cases that are easy to mistake for economic results and are not. A
documented market event reduced to roughly half its count once instrument existence, trading
materiality and capacity were imposed at the event date — without a single return being computed. And
a design with near-perfect data was stopped before its pre-registration was frozen, because the
comparison group it required does not exist on the venue, which is an arithmetic fact about 134
tagged assets rather than a statement about markets.

We therefore propose that dataset construction, event semantics, point-in-time validity,
identification and execution feasibility be treated as hypotheses in their own right, each falsified
before the trading hypothesis is tested, and that research outputs distinguish an economic null from
a data-gate failure, an infrastructure block, an identification block and an execution failure. The
article has served its purpose if a reader finishes it less willing to trust a backtest merely
because the model, the statistics and the code look sophisticated.

---

## Figures

![](figures/f1_research_lifecycle.png)

**Figure 1.** The stages a hypothesis must survive, and what each stage did to a family.
*Source: `HYPOTHESIS_LEDGER.md` and the per-family gate JSONs.*

![](figures/f2_gate_outcomes.png)

**Figure 2.** Gate outcomes as each family's own gate recorded them.
*Source: each family's gate JSON, field `criteria_passed`; H18.0 is the Binance column of the
three-venue probe. Data: `figures/data/f2_gate_outcomes.csv`.*

![](figures/f3_lifecycle_reconstruction.png)

**Figure 3.** Lifecycle reconstruction. (a) 102 of 1,422 pair-removal events are a full asset
delisting. (b) 82 shared episodes plus 119 recovered events give the validated 201-event universe.
*Source: `H18_1_GATE.json`, `H18_1B_GATE.json`. Data: `figures/data/f3_lifecycle_reconstruction.csv`.*

![](figures/f4_h18_3_folds_vs_holdout.png)

**Figure 4.** Eight positive development folds and the single-use holdout that reversed the sign. The
holdout is drawn apart from the folds because it has a different evaluation role; it is not a ninth
fold.
*Source: `H18_3_DEVELOPMENT_REPORT.md` §3, `h18_3_development.json`, `H18_3_GATE.json`. Data:
`figures/data/f4_h18_3_folds_vs_holdout.csv`.*

![](figures/f5_execution_funnel.png)

**Figure 5.** The execution funnel: 201 documented events to 32 feasible for a US$1,000 order.
*Source: `H19_0_GATE.json`. Data: `figures/data/f5_execution_funnel.csv`.*

![](figures/f6_common_support.png)

**Figure 6.** Common-support collapse. (a) The realised matched-control distribution against the
frozen floor. (b) The ceiling computed on the full pool, for the 8 of 25 announcement dates the
artefact reports. Two panels are used because the collapse and its cause are distinct measurements.
*Source: `h19_2_prefreeze.json`, `H19_2_PREFREEZE_FEASIBILITY.md` Check 3. Data:
`figures/data/f6_common_support.csv`.*

## Tables

**Table 1.** Experiment registry, H13 to H19.2. `tables/table1_experiment_registry.md`
**Table 2.** Research failure taxonomy. `tables/table2_failure_taxonomy.md`
**Table 3.** Classes of silent failure that produced plausible outputs.
`tables/table3_silent_failure_classes.md`
**Table 4.** H18.3 pre-registered metrics. `tables/table4_h18_3_preregistered_metrics.md`
**Table 5.** H19 execution and feasibility gate. `tables/table5_h19_execution_gate.md`

## Data and code availability

Every number in this paper maps to a field in a committed artefact. The mapping is
`CLAIM_EVIDENCE_MATRIX.csv`; the artefacts, with their commits and hashes, are listed in
`ARTIFACT_INDEX.md`; the environment, seeds and state transitions are in
`REPRODUCIBILITY_APPENDIX.md`. Tables and figures are regenerated by
`scripts/paper_build_tables.py` and `scripts/paper_build_figures.py`.

## Evidence classes

Three categories are kept separate throughout and are never merged into a single evidentiary claim:
**internal empirical evidence** (this program's experiments), **external literature** (academic work,
with abstract-only access flagged), and **official venue documentation** (the venue's own published
surfaces). Paid sources appear only as reference and never as the evidence that allows a gate to
pass.

## References

See `references.bib`.
