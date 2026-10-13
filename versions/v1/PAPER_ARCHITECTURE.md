# PAPER ARCHITECTURE — *Falsification-First Alpha Discovery*

**Working title.** Falsification-First Alpha Discovery: How Data Construction, Survivorship,
Semantic Errors and Execution Constraints Manufacture Trading Strategies

> **Historical planning document.** The manuscript has since been completed. Current manuscript
> status is recorded in `PAPER_QA.md`. This file is preserved as evidence of the plan that existed
> *before* any prose was written, so the finished paper can be checked against it. The only later
> additions are this note and the resolution note under section 8, item 1.

**Status.** Architecture and evidence map. No manuscript prose has been polished yet. Alpha
discovery is **PAUSED FOR PAPER CONSOLIDATION**: no new hypothesis, no new backtest and no new
return is computed while this document stands.

**Scope.** Primary empirical and methodological scope is **H13 → H19.2**. H1–H12 appear as
motivation, discovery funnel and experiment registry only. H8 appears in one short section as
evidence that the framework does not reject everything; it is not the protagonist and is reserved
for a separate paper.

---

## 1. Thesis (one paragraph)

Many apparent quantitative trading opportunities are created or destroyed **before model fitting**,
through universe construction, survivorship, event semantics, point-in-time violations,
outcome-selected joins, execution assumptions and researcher degrees of freedom. We document this
with an auditable sequence of real experiments on free public data in which the decisive step is
almost never the model: a spectacular micro-cap screen collapses once the 52.9% of candidate issuers
with no current ticker are restored to the universe; four consecutive filing-based families fail
data or semantic gates before any return is computed; a venue-owned archive turns out to preserve
the dead instruments that aggregators drop, which allows a delisting universe to be rebuilt from 84
to 201 events; a pre-registered predictive test that is positive in **8 of 8** rolling-origin folds
is nonetheless declared **NULL** when its cluster bootstrap crosses zero, its materiality gate fails
and its untouched holdout reverses sign; 201 documented delistings reduce to 32 that a US$1,000
order could plausibly enter; and a design with near-perfect data is **blocked before freeze**
because two individually reasonable control requirements are jointly impossible on the venue. The
contribution is not a strategy. It is a demonstration that dataset construction, semantics,
point-in-time validity, identification and execution are themselves hypotheses, each of which must
be falsified before the trading hypothesis is tested — together with the taxonomy, governance
protocol and audits that make such falsification routine.

---

## 2. Contributions

Four classes, each stated as a claim the paper evidences from its own experiments.

### C1 — Data construction

1. **Survivorship can enter through the universe.** 2,965 of 5,604 candidate CIKs (**52.9%**) have
   no current SEC ticker, monotone in cohort age (68% for 2011 to 4% for 2026); re-adding them under
   labelled assumptions moves a median screen outcome from **+18.3%** to **+3.7%** (central) and
   **0.0%** (severe). *(H13)*
2. **Blocked upstream, it reappears in the market-data join.** The identity layer of a Form 4 study
   passes at 98–99% and the family is still blocked at the *price-history* gate. *(H17.0)*
3. **Venue-owned archives can preserve dead instruments where aggregators do not.** Binance's own
   archive shows a **0.0 pp** retrieval gap between active and delisted spot pairs, and retains
   1,936 delisted symbols with history. *(H18.0, H18.0b, H18.1)*
4. **Pagination, vocabulary and timestamp-unit changes can fabricate historical coverage.** Four
   independent instances, each of which produced a plausible but false data horizon. *(H18.1b,
   H19.1)*

### C2 — Semantics

1. **Standardized form is not standardized meaning.** A 94,036-accession 13D/13D-A universe with
   100% issuer and filer identity still fails 17 of 22 criteria on *meaning*. *(H15)*
2. **Pair removal is not asset delisting.** Only **102 of 1,422** Binance pair-removal events (7.2%)
   are an asset leaving spot. *(H18.1)*
3. **A ticker is not a permanent asset identity.** Asset-era keying is required; a ticker-keyed join
   silently substituted a different asset in two separate families. *(H18.1b, H19.0)*
4. **An event date is not a datum until attribution is resolved**, and **announcement time, cessation
   time and execution time are different quantities**: 3 of 201 events traded materially for three
   days past the cessation instant stated in the venue's own notice. *(H16.1, H18.1b)*

### C3 — Point-in-time and researcher leakage

1. **Future-derived classifications.** 676 of 2,352 removals (**28.7%**) change class once the
   classification window is made strictly backward-looking; 314 of 390 quote retirements had been
   forward-looking, with a median lag of 49 days. *(H18.2 into H18.3 amendment 01)*
2. **Controls built from the future.** A ±180-day control-eligibility rule was removed from a draft
   pre-registration *before* freeze because its forward half is look-ahead. *(H19.2, A5)*
3. **Event overlap between splits.** Measured as landmark dates, the briefing's own split boundaries
   shared 41 of the holdout's 86 outcome events; a one-horizon embargo is required, one boundary
   cannot be repaired at all, and the validation block was therefore dropped rather than
   half-previewed. *(H18.3)*
4. **A leakage test must cover feature *classification*, not only values and dates.** *(H18.2,
   H18.3)*
5. **Common-support collapse.** Matching on the venue's only public risk warning leaves a median of
   **7** eligible controls per announcement date against a pre-registered floor of 20. *(H19.2)*

### C4 — Execution

1. **A documented event is not a tradable event.** 201 → 75 → 64 → 63 → **32**. *(H19.0)*
2. **Available historical data does not establish that the instrument existed at event time**, which
   is why current instrument lists may not be used as history. *(H19.0 §29)*
3. **A served candle is not an actively traded market.** Three independent occurrences; in one
   primary window spot has no trades in a median 25% of minutes, against 0.42% for the perpetual.
   *(H18.1b, H19.0, H19.1)*
4. **A clean shortable sample can collapse once liquidity and capacity are imposed**, without any
   return being computed. *(H19.0)*

---

## 3. Section outline

| § | title | core content |
|---|---|---|
| 1 | Introduction | why systematic alpha discovery fails; **model overfitting versus pre-model research failure**; contributions |
| 2 | Research governance | immutable ingestion; event_time and ingest_time; PIT; pre-registration; frozen splits; single-use holdout; NO_TRADE; costs and execution; experiment ledger; bug and deviation policy; negative-result taxonomy |
| 3 | Failure taxonomy | formal taxonomy built from QIE: failure mode, mechanism, observable symptom, example, defense (Table 2) |
| 4 | Data construction before modeling | H13–H17: survivorship, semantics, identity, joins, market-data history |
| 5 | Reconstructing venue lifecycle data | H18.0b, H18.1, H18.1b: pair-removal catalog, semantic audit, route reconstruction, full-delisting universe; **84 to 201** |
| 6 | A pre-registered predictive test | H18.2, H18.3: hypothesis, risk set, features, rolling origin, holdout; development looked positive, verdict **NULL**. The central section |
| 7 | From event to executable opportunity | H19.0: the execution funnel 201 → 75 → 64 → 63 → 32, and why each reduction matters |
| 8 | When identification fails despite excellent data | H19.1, H19.2: 62 excellent events, tagged-control common-support failure, confirmatory n = 10, **STOP before price** |
| 9 | General principles | ten reusable rules (P1–P10 below) |
| 10 | Implications for quant research | academic backtests; retail systematic research; ML prediction; event studies; alternative data |
| 11 | Limitations | one researcher and one codebase; venue concentration in the later cases; free and public data only; no institutional order-book archive; non-exhaustive experiment family; some gates judgement-based; negative results do not generalise universally; H19.2 never tested a price outcome; no causal insider claim; H8 held separate |
| 12 | Conclusion | construction, semantics, PIT validity, identification and execution are hypotheses to be falsified before the trading hypothesis is tested |

**Principles fixed for §9.** P1 the identifier is the experiment. P2 a date is not a datum until
attributed. P3 every join needs its own outcome-differential audit. P4 who owns the record determines
whether dead instruments remain observable. P5 event time, knowledge time and execution time are
different clocks. P6 a served candle is not necessarily a traded market. P7 common support must be
demonstrated, not assumed. P8 a positive development result is not evidence until frozen
out-of-sample evaluation survives. P9 data-gate failure is not economic rejection. P10 NO_TRADE and
NO_TEST are valid research outputs.

### Result taxonomy, and the per-family labels it forces

| label | meaning | families |
|---|---|---|
| ECONOMIC REJECT | tested against pre-registered bars and rejected | H13 (implementation rejected; economic hypothesis **unresolved**) |
| PRE-REGISTERED NULL | design and data survived; the predictive claim did not | **H18.3** |
| DATA-GATE FAIL / UNTESTED | no economic test was ever run | H14.1, H14.2, H14.3, H15, H16.1 |
| INFRASTRUCTURE BLOCKED | substrate unavailable at the required quality | H17.0, H18.0 |
| IDENTIFICATION BLOCKED | data adequate, design does not identify the effect | **H19.2 — BLOCKED BEFORE FREEZE** |
| EXECUTION FAIL | event real and tradable, capacity gate fails | **H19.0 — PARTIAL PASS** |

**Language rules, binding on every section.**

- **H19.2** is `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL`. Never *rejected*, never *null*. No
  price column was ever read, therefore **no economic inference about H19-P3A exists**.
- **H18.3** is a `PRE-REGISTERED NULL`. Never a data failure. The data and the design survived; the
  predictive claim did not.
- **H19.0** is `PARTIAL PASS`, and for the small-capital thesis the sample gate fails. The paper must
  **not** imply that shorting delistings is unprofitable — **returns were never computed**.
- **H13** rejects an implementation, not the economics of net-nets.

---

## 4. Experiment-to-section mapping

| family | question | status label | gate | body § | case |
|---|---|---|---|---|---|
| H1–H12 | cycles 1–4 discovery | registry / appendix | mixed | §1, §3, App. A | — |
| H8 | slow multi-asset trend | survived, moved to paper portfolio | pre-registered | §2 (short) | — |
| H13 | do filings separate *cheap because ignored* from *cheap because the cash will disappear*? | ECONOMIC REJECT (implementation) | pre-registered, commit `aca53bf` | §4.1 | **A** |
| H14 | B3 deep special situations | OPEN — universe built, no hypothesis chosen | — | §4.2 | — |
| H14.1 | B3 takeover-offer terms resolution | DATA-GATE FAIL (gold-set accuracy) | 64-case gold set | §4.2 | — |
| H14.2 | B3 judicial recovery / distressed | DATA-GATE FAIL, 1 of 7 | — | §4.2 | — |
| H14.3 | B3 recapitalizations and rights issues | DATA-GATE FAIL, 0 of 9 | — | §4.2 | — |
| H15 | 13D activist intent and outcome | DATA-GATE FAIL, 5 of 22, UNTESTED | semantic gate | §4.3 | **B** |
| H16.1 | FDA / PDUFA binary catalysts | DATA-GATE FAIL, 2 of 23, UNTESTED | identity, date and join gate | §4.4 | **B** |
| H17.0 | historical market data for a Form 4 study | INFRASTRUCTURE BLOCKED, 14 of 32 | price-history gate | §4.5 | **B** |
| H18.0 | does a venue serve delisted spot OHLCV? | INFRASTRUCTURE BLOCKED (2 of 3 venues required) | three-venue probe | §5.1 | — |
| H18.0b | venue-owned substrate confirmation | **PASS, 14 of 14** | substrate gate | §5.1 | — |
| H18.1 | pair removal versus asset delisting | PARTIAL PASS, 11 of 12 | semantic audit | §5.2 | **C** |
| H18.1b | was the full-delisting universe truncated? | **STRONG PASS, 19 of 19** | construction gate | §5.3 | **C** |
| H18.2 | literature, mechanism and hypothesis selection | SELECT H18-P1 | five preconditions | §6.1 | **D** |
| H18.3 | route contraction to landmark 365-day delisting risk | **PRE-REGISTERED NULL** | frozen prereg plus amendment 01 | §6.2–6.5 | **D** |
| H19.0 | did a short exist when the market learned? | **PARTIAL PASS, 12 of 15** | execution gate | §7 | **E** |
| H19.1 | derivative price-discovery selection | SELECT H19-P3A with three modifications | six conditions | §8.1 | **F** |
| H19.2 | derivative-specific pre-delisting discovery | **BLOCKED BEFORE FREEZE** | pre-freeze feasibility | §8.2–8.4 | **F** |

### Case-study backbone

| case | families | the turn | principle |
|---|---|---|---|
| **A** | H13 | spectacular backtest becomes a survivorship and construction artefact | every spectacular backtest is a bug candidate until the universe is audited |
| **B** | H15, H16.1, H17.0 | form semantics, then identifier semantics, then joins, then historical market data | survivorship and outcome selection migrate downstream when blocked upstream |
| **C** | H18.1, H18.1b | 84 apparent full delistings become 201 actual events | the catalog is not the population |
| **D** | H18.2, H18.3 | 8 of 8 positive folds become NULL | when a convincing development result should still be rejected |
| **E** | H19.0 | 201 documented events become 32 feasible ones | a documented market event is not a tradable event |
| **F** | H19.1, H19.2 | 62 excellent events become a confirmatory n of 10 | two individually reasonable requirements can be jointly impossible |

---

## 5. Planned figures

Six figures, from **existing artefacts only**. Each row names the fields the figure is drawn from. No
value is to be invented, smoothed or rounded for appearance.

| # | figure | content | source of every number |
|---|---|---|---|
| **F1** | QIE research lifecycle | idea, data gate, semantic gate, PIT gate, identification, pre-registration, out-of-sample, execution — with the family that died at each stage annotated | `HYPOTHESIS_LEDGER.md` and the per-family gate JSONs (stages are schematic; all counts are quoted) |
| **F2** | failure taxonomy across H13–H19 | matrix of family by failure class; each cell names the gate criterion that failed | `H15_13D_GATE.json` 5/22, `H16_1_GATE.json` 2/23, `H17_0_GATE.json` 14/32, `H18_0_GATE.json`, `H18_0B_GATE.json` 14/14, `H18_1_GATE.json` 11/12, `H18_1B_GATE.json` 19/19, `H18_3_GATE.json`, `H19_0_GATE.json` 12/15, `H19_2_PREFREEZE_FEASIBILITY.md` |
| **F3** | Binance lifecycle reconstruction | 1,422 pair-removal events, 1,271 asset-lifecycle episodes, 102 pair events and 84 episodes classed ASSET_FULL_SPOT_DELISTING, then 201 full-delisting events after catalog expansion; miss decomposition 75 DIFFERENT_CATEGORY, 39 PRE_2022_CATALOG, 5 PAIR_UNIVERSE | `H18_1_GATE.json`: `universe.pair_events`, `universe.asset_lifecycle_episodes`, `pair_event_categories`, `asset_episode_categories`; `H18_1B_GATE.json`: `universe.*` |
| **F4** | H18.3 rolling origin versus holdout | fold ΔPR-AUC +0.0361, +0.0119, +0.0238, +0.0441, +0.0424, +0.0229, +0.0479, +0.0824; median +0.0393; pooled +0.0270 with bootstrap CI [−0.0074, +0.0628]; **holdout −0.0075** | `H18_3_DEVELOPMENT_REPORT.md` §3 table; `h18_3_development.json`: `pooled_out_of_fold`, `cluster_bootstrap`, `median_fold_delta`; `H18_3_GATE.json` holdout block |
| **F5** | H19.0 execution funnel | 201 documented, 75 Tier-1 USDⓈ-M at T0, 64 materially shortable, 63 clean information events, **32** small-capital feasible; liquidity buckets 31 / 30 / 2 | `H19_0_GATE.json`: `input_events`, `tier1_usdm_at_T0`, `shortable_at_T0`, `clean_events`, `small_order_1k_share_of_median_hourly`, `liquidity_buckets_clean` |
| **F6** | H19.2 common-support collapse | 62 candidates, controls-per-event distribution p10 0 / p25 0 / median 1 / p75 2 / p90 57, 52 of 62 below 20, confirmatory **n = 10**; tagged-pool hard ceiling by date from 0 to 27, median 7, only 3 of 25 dates reaching 20 | `H19_2_PREFREEZE_FEASIBILITY.md` §§1–3 and Check 3 |

**Figure discipline.** F1 and F2 are structural diagrams whose only quantities are gate counts taken
from the artefacts above. F3 to F6 are quantitative, and every plotted value also appears in the
claim-evidence matrix. Figures are produced by a committed script so each is reproducible from the
artefacts, and no figure introduces a quantity absent from them.

---

## 6. Planned tables

| # | table | columns | source |
|---|---|---|---|
| **T1** | experiment registry H13–H19 | family, question, data gate, test status, result, failure class, paper lesson | `HYPOTHESIS_LEDGER.md` plus each gate JSON; verdicts and criteria counts quoted verbatim |
| **T2** | research failure taxonomy | failure mode, mechanism, observable symptom, QIE example, defense | §3, derived from the families; every example carries its family tag |
| **T3** | classes of silent failure that produced plausible outputs | class, instance, what it produced, how it was detected, generalised lesson | per-family audits and deviation notes; framed as **classes of silent failure, not a blooper reel** |
| **T4** | H18.3 pre-registered metrics | criterion, bar as frozen, measured, verdict — the four scientific-support and five materiality criteria, plus the holdout | `H18_3_DEVELOPMENT_REPORT.md` §§5–6, `h18_3_development.json`, `H18_3_GATE.json` |
| **T5** | H19 execution gate | criterion, bar, measured, pass or fail for the 15 H19.0 criteria, plus the H19.2 pre-freeze requirements | `H19_0_GATE.json`: `criteria[]`; `H19_2_PREFREEZE_FEASIBILITY.md` |

T3's content is fixed to these classes: catalog truncation; date-format change; ticker collision and
asset-era keying; S3 pagination without a delimiter; timestamp-unit divergence between two legs of
the same venue's archive; NaN truthiness; `0.0`-is-falsy gate logic; future-derived removal
classification; right censoring; event sharing across splits; common-support collapse. Each row must
state **separately** the software defect and the economic question it was obscuring, and no row may
imply that finding a defect is itself alpha research.

---

## 7. Claim-evidence inventory

The authoritative file is `CLAIM_EVIDENCE_MATRIX.csv`, with columns `claim_id, claim, experiment,
artifact, field_or_line, status, notes`. **No numerical claim may appear in the manuscript without a
row there.** Anchor claims:

| claim_id | claim | artefact and field |
|---|---|---|
| C-H13-01 | 2,965 of 5,604 candidate CIKs (52.9%) have no current SEC ticker | `H13_PAPER_SUMMARY.md` survivorship section; `H13_RED_TEAM.md` |
| C-H13-02 | the Test A panel is 1,197 companies, 50.1% without a current ticker | `h13_results.json`: `A_n`, `A_with_ticker_today = 0.49875` |
| C-H13-03 | P(GONE) by burn tertile 11.90 / 15.95 / 23.04%, T3 − T1 = +11.14 pp against a +20 pp bar | `h13_results.json`: `A1` |
| C-H13-04 | burn-to-death AUC 0.5930 | `h13_results.json`: `A3.auc_gone_burn` |
| C-H13-05 | raw screen median +18.34% (n = 472); the best filter beats it by +1.9 pp against a +10 pp bar | `h13_results.json`: `B3` |
| C-H13-06 | the burn effect inverts in returns: cheap and high burn minus cheap and low burn is −23.46 pp | `h13_results.json`: `B2_diff_cheap_lowburn_minus_highburn` |
| C-H13-07 | bias bounds cut the median to +3.66% (mild and central) and 0.0% (severe) | `h13_results.json`: `B4b` |
| C-H15-01 | 94,036 accessions, 502 filings read (0.53%), gate 5 of 22, UNTESTED | `H15_13D_GATE.json` |
| C-H16-01 | 16,444 candidate filings, 1,108 decision cycles, gate 2 of 23, UNTESTED | `H16_1_GATE.json` |
| C-H17-01 | identity layer 98.4–99.6%, gate 14 of 32, blocked at market data | `H17_0_GATE.json` |
| C-H18-01 | Binance active-versus-delisted retrieval gap 0.0 pp; 1,936 delisted symbols retain history | `H18_0_GATE.json`; `H18_1_GATE.json`: `universe` |
| C-H18-02 | 1,422 pair events yield 102 pair events and 84 episodes of ASSET_FULL_SPOT_DELISTING, 7.2% | `H18_1_GATE.json`: `pair_event_categories`, `asset_episode_categories` |
| C-H18-03 | 201 full-delisting events from 2018-10-12 to 2026-09-24; 119 missed by H18.1 | `H18_1B_GATE.json`: `universe` |
| C-H18-04 | miss decomposition 75 / 39 / 5 | `H18_1B_GATE.json`: `universe.miss_reasons` |
| C-H18-05 | recall 0.9801 against candle-measured full delistings; 4 true false negatives | `H18_1B_GATE.json`: `recall`, `false_negative_audit` |
| C-H18-06 | 3 of 201 events traded materially past the stated cessation instant | `H18_1B_GATE.json`: `post_cessation_activity` |
| C-H18-07 | gold set of 100 events, 40 double-reviewed, PASS-1 all-field accuracy 1.0, churn 0.0 | `H18_1B_GATE.json`: `gold` |
| C-H18-08 | 676 of 2,352 removals (28.7%) change class under strictly backward classification | `H18_3_PREREG_AMENDMENT_01.md`; `h18_3_pit_audit.json` |
| C-H183-01 | development block of 78,244 landmarks, 110 unique events, base rate 5.822% | `h18_3_development.json` |
| C-H183-02 | 8 of 8 folds positive, median fold Δ = +0.0393 | `H18_3_DEVELOPMENT_REPORT.md` §3 |
| C-H183-03 | pooled ΔPR-AUC +0.0270, +13.46% relative, 37,782 landmarks, 440 asset-eras | `h18_3_development.json`: `pooled_out_of_fold` |
| C-H183-04 | cluster bootstrap 95% CI [−0.0074, +0.0628], 93.45% of draws above zero, 2,000 replications, seed 20261010 | `h18_3_development.json`: `cluster_bootstrap` |
| C-H183-05 | materiality fails only on criterion 5, calibration shift 0.1948 against a 0.10 bar, although calibration improves in all 8 folds | `H18_3_DEVELOPMENT_REPORT.md` §6 |
| C-H183-06 | holdout of 86 events, base rate 11.792%, baseline 0.30007, challenger 0.29254, **Δ = −0.00753** | `H18_3_GATE.json` |
| C-H183-07 | holdout top-decile lift 2.8672 to 2.9777 | `H18_3_GATE.json` |
| C-H183-08 | falsification: market-only variants reach 0.2184 against the challenger's 0.2274 | `h18_3_falsification.json` |
| C-H183-09 | the briefing's own splits shared 41 of the holdout's 86 events | `h18_3_eligibility.json`: `why_the_briefing_boundaries_were_not_kept` |
| C-H190-01 | 201 to 75 Tier-1 to 64 shortable to 63 clean to 32 feasible at US$1,000 and 1% of median hourly notional | `H19_0_GATE.json` |
| C-H190-02 | in all 63 clean events the perpetual traded through the whole observed window | `H19_0_GATE.json`: `share_open_at_least` |
| C-H190-03 | terminated and current derivatives are both observable at 1.0; missingness differentials 0.0 pp | `H19_0_GATE.json`: `survivorship_test_28`, `missingness_differentials_pp` |
| C-H190-04 | Tier-3 margin shortability is UNKNOWN for all 201 events | `H19_0_GATE.json`: `tier3_margin_at_T0` |
| C-H191-01 | spot 1-minute coverage 100%, perpetual 98.41%, synchronized minutes 98.41%; 62 usable events against a bar of 50 | H19.1 feasibility documents |
| C-H191-02 | spot has no trades in a median 25% of primary-window minutes, against 0.42% for the perpetual | H19.1 documents, modification M-2 |
| C-H192-01 | final confirmatory n = 10 against a floor of 40; 52 of 62 events below 20 matched controls | `H19_2_PREFREEZE_FEASIBILITY.md` §§1, 3 |
| C-H192-02 | controls per event p10 0, p25 0, median 1, p75 2, p90 57 | `H19_2_PREFREEZE_FEASIBILITY.md` §2 |
| C-H192-03 | 134 Monitoring-Tagged assets ever across 28 notices; median 7 tagged assets eligible per date; 3 of 25 dates reach 20 | `H19_2_PREFREEZE_FEASIBILITY.md` Check 3 |
| C-H192-04 | availability 99.3%, transition-grid median 92, VWAP fields 100% — the failure is not availability | `H19_2_PREFREEZE_FEASIBILITY.md` Checks 1–2 and §§4–6 |
| C-H192-05 | no price column was ever read (`usecols=[0,5,7,8]`) | `scripts/h19_2_prefreeze.py`; `H19_2_PREFREEZE_FEASIBILITY.md` §8 |

### Source discipline, applied per claim

Three evidentiary categories, never blended: **INTERNAL EMPIRICAL EVIDENCE** (QIE experiments),
**EXTERNAL LITERATURE** (academic work, with abstract-only access flagged as such) and **OFFICIAL
VENUE DOCUMENTATION** (Binance's own surfaces). Paid sources may appear only as `PAID_REFERENCE`,
never as the evidence that lets a gate pass. The matrix carries the category in `notes`.

---

## 8. Unresolved gaps

Recorded, **not computed**. The live list is `PAPER_OPEN_QUESTIONS.md`.

1. **The H19.2 decision belongs to the user.** Option A — drop tag matching and control for tag
   status statistically — is the only route that preserves a confirmatory design, and it weakens
   identification. Until that decision, H19-P3A stays `BLOCKED BEFORE FREEZE`: nothing frozen,
   nothing hashed, no price read.
   > **Q1 resolved after manuscript planning: Option E was selected.** H19-P3A remains
   > `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL`. Tag matching and `MIN_CONTROLS` were not
   > relaxed, and no price was loaded. The open formulation above is left in place deliberately, as
   > the record that the decision was still open at planning time.
2. **H13's economic question is unresolved, not rejected.** Only the implementation was rejected. A
   survivorship-free *price* panel for delisted US micro-caps does not exist in the free sources
   used, so the paper states the question as open.
3. **H18.3's calibration bar was mis-specified by the researcher** — as written it penalises
   improvement as well as deterioration. It failed as written, the bar was not moved, and the flaw
   is carried to the next pre-registration rather than patched into this one. The paper reports this
   as a researcher error with its methodological lesson, and must not imply that the verdict would
   otherwise have been positive: scientific-support criterion 2 fails independently, as does the
   holdout.
4. **Derivative-notice coverage.** 184 of 201 events have no derivative notice found. This is a
   coverage limit of the official surfaces reached, never read as proof of absence, and it blocks the
   announcement-ordering subgroup.
5. **Tier-3 margin shortability is unknown for the whole universe.** No point-in-time margin
   eligibility or borrow source exists on official keyless surfaces, and inferring it from current
   asset support is forbidden. The execution funnel is therefore a lower bound on shortability.
6. **H14 remains open**, with a 6,491-event universe and no hypothesis selected, and three
   sub-families that failed data gates. The paper reports it as open, not as a negative result.
7. **Three H18.1b events** — OST, RCN and WPR, all announced for 2021-07-16 — traded materially for
   three days past the cessation instant stated in Binance's own notices. The recorded dates are
   faithful to the documents; the venue's behaviour was not. Both affected diagnostics sit at 0.9851
   and 0.9847 against a 0.99 bar and are named rather than smoothed.
8. **The H10 control-byte issue** is a pre-existing known issue, out of scope here, and recorded as
   such in the reproducibility appendix.
9. **Event accounting across the H18.3 blocks** needs an explicit sentence in §6: 110 development, 72
   embargo (dropped) and 86 holdout outcome events sum to more than 201 because one announcement can
   be the outcome of landmarks in more than one block. Development and holdout share **zero** events,
   which is the property the design requires.
10. **The two H13 denominators must never be conflated.** 52.9% is the share of the 5,604-CIK screen
    candidate universe with no current ticker; 50.1% is the share of the 1,197-company Test A panel.
    Both are correct, and they measure different populations.

---

## 9. What this document fixes before prose begins

- The thesis sentence, the four contribution classes and the twelve sections are settled.
- Every figure and table has a named artefact for each quantity, so drafting cannot introduce an
  unreferenced number.
- The six status labels and the three binding language rules (H18.3, H19.0, H19.2) are fixed before
  any sentence is written about those families.
- The quality check — hindsight language, overclaim, result-status mistakes, post-hoc
  reinterpretation, selection bias, unreferenced numbers, and a justification for every occurrence of
  *prove*, *obviously*, *clearly*, *always* and *never* — runs against the finished manuscript, and
  its output is recorded in this directory.
