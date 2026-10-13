# AUTHOR RESPONSE TO REFEREE #2 — V1

**Manuscript:** *Falsification-First Alpha Discovery*, V1, frozen at commit `52a980a`
(`paper.md` SHA-256 `1853bce0…`). Nothing in V1 has been edited in writing this response; every
change named here is a **V2** change, tracked in `PAPER_REVISION_PLAN_V2.md`.

**Summary of disposition.** Of fifteen major concerns: **9 ACCEPT**, **5 PARTIALLY ACCEPT**,
**1 DISAGREE in part**. Three concerns additionally contain a component marked
`DEFERRED — REQUIRES NEW EXPERIMENT`, which is not executed. **No experiment was run in preparing
this response.**

The referee is right about the most important thing, and it is the thing I would have defended
hardest: **the paper's framing claims a contribution that the methodology literature already owns,
and buries the three or four measurements that are actually mine.** MC10 and MC4 are the two
concerns that change the paper rather than its prose.

---

## MC1 — Is this science or an engineering post-mortem?

**Response: PARTIALLY ACCEPT.**

**Accepted.** The referee's test — strip the proper nouns and ask what survives — is the right test,
and I had not applied it. Table 3 has twelve rows and does not earn twelve. I accept that a reader
can read the paper as a defect catalogue, and that the manuscript does not pre-empt that reading.

**Where I disagree, specifically.** The referee dismisses `0.0`-is-falsy and NaN-truthiness as
"Python idiom hazards". The `0.0`-is-falsy defect is not a language anecdote, for one checkable
reason: **it occurred twice, in two different families, in gate code, on a gate metric**. In H17.0
and again in H19.0, an expression of the form `(metric or default)` converted a perfect measured
value of `0.0` into a missing value and failed a criterion that had in fact passed. The
generalisable class is not "Python has falsy zeros"; it is **gate logic that tests a metric's
truthiness rather than its presence will silently invert exactly the results that are perfect**, and
a perfect score is the one a researcher is least likely to re-examine. The recurrence across two
independent families is the evidence that it is a class.

I make the same argument, more weakly, for the timestamp-unit row: two legs of one comparison stored
under different conventions by the same provider is a property of data distribution, not of a
language.

NaN-truthiness I concede. The regex row I concede. The date-format row I keep, because it is the
third independent occurrence in this program of a format change producing a false data horizon, and
the recurrence is the finding.

**Evidence.** `H17_0_GATE.json` and `H19_0_GATE.json` both record churn/metric fields where the
defect occurred; `H18_1B_DATA_AUDIT.md` records the date-format and era defects;
`CLAIM_EVIDENCE_MATRIX.csv` rows C-H18B-*.

**Revision.** V2: Table 3 reduced from twelve rows to the five with cross-family recurrence or
distributional cause (coverage measurement, unit divergence, gate-metric truthiness, format-change
horizons, classification-level leakage). The remaining rows move to an appendix table labelled
"implementation defects, retained for completeness, not claimed as contributions". §5.3 adds one
sentence stating that discovering one's own defect carries no information about markets.

**New experiment required? NO.**

---

## MC2 — Selection of H13 to H19

**Response: ACCEPT.**

The referee is correct and the fix is cheap. Case selection for the manuscript was retrospective, the
thesis was formed after the families ran, and the paper's heavy description of pre-registration
invites a reader to assume otherwise. That is my error of presentation.

I want to keep one distinction the referee already grants: **hypothesis selection** inside each
family was pre-registered and is auditable by hash and commit order; **case selection for the paper**
was not. The paper must say both.

**Evidence.** `docs/alpha_sprint/HYPOTHESIS_LEDGER.md` contains all families H1–H19.2 with verdicts,
and it is committed and dated. No new computation is needed to report it.

**Revision.** V2: (a) a new appendix table listing **every** family H1 through H19.2 with its
verdict, failure class and commit — the full denominator; (b) an explicit paragraph in §1 stating
that the four case studies were selected after the fact to illustrate a thesis formed after the fact,
and that this is case selection, not hypothesis selection; (c) the referee's question — "would the
methodology be the same if these families had produced different outcomes?" — answered in the text,
honestly: the *protocol* would be, because it is recorded in frozen documents predating the results;
the *paper* would not, because its cases were chosen for their illustrative value.

**New experiment required? NO.**

---

## MC3 — Gate arbitrariness

**Response: PARTIALLY ACCEPT.**

**Accepted in full for the first two requests.** The thresholds are engineering judgements. The paper
should say so, and should name the conclusions that are threshold-determined. The referee's list of
three is correct: H19.2's `IDENTIFICATION BLOCKED` follows from `MIN_CONTROLS = 20`, H19.0's 32
follows from the 1% rule, and H18.3's materiality failure follows from a 0.10 calibration bar I
already describe as defective.

**One clarification, not a defence.** The rhetorical weight I place on "the bar was not moved" is not
a claim that the bar was correct. It is a claim about *sequence*: the bar was fixed before the
measurement and not adjusted after seeing it. A bar chosen by judgement and held is weaker evidence
than a bar derived from theory, and stronger than a bar chosen after the result. The paper should
state that ordering explicitly instead of letting the phrase imply more.

**Where I cannot comply.** The third request — report what a reasonable perturbation would do —
requires re-running fits and gates at alternative thresholds. That is a new computation.

**Evidence.** Thresholds and their sources are in `H18_3_PREREG.md`, `H19_2_PREFREEZE_FEASIBILITY.md`
(`frozen_bars`), `H19_0_GATE.json` (`criteria[].bar`), and `docs/alpha_sprint/PREREGISTRATION_H13.md`.

**Revision.** V2: a new table in §2 classifying every threshold as `THEORETICAL`,
`CONVENTIONAL` (borrowed from an established practice) or `ENGINEERING JUDGEMENT`, with the
conclusion it drives; plus an explicit statement that three conclusions are threshold-determined and
that their sensitivity is **unmeasured**.

**New experiment required? Partly — `DEFERRED — REQUIRES NEW EXPERIMENT` for the sensitivity
analysis.** The classification table and the statement of unmeasured sensitivity require none.

---

## MC4 — Ex post governance presented as ex ante

**Response: ACCEPT, without qualification.**

This is the strongest objection in the report and I had not seen it. The referee's list is accurate:
SHA-256 freezing starts at H18.3; classification-level leakage auditing starts at H18.3; the
directional holdout veto is amendment A3; asset-era keying starts at H18.1b; "a served candle is not
a traded market" starts at H18.1b; the no-price pre-freeze check starts at H19.1. §2 presents the
mature protocol as the frame for all seventeen families, and the reproducibility appendix even
contains the contradicting sentence — "H13 predates the SHA-256 freeze protocol" — without the
manuscript drawing the consequence.

The referee's characterisation stings and is fair: presenting a protocol's final state as its initial
state is using information from the end of the program at its beginning.

**Evidence.** The commit graph dates every rule's introduction: `aca53bf` (H13, no hash), `27c3283`
(asset-era keying), `522bafb` (first frozen hash), `203390b` (amendment A3), `564baf8` (first
no-price probe). `REPRODUCIBILITY_APPENDIX.md` §4 already carries the hash table and its gap.

**Revision.** V2: §2 split into **§2a — rules in force from the start of the reported program** and
**§2b — rules added in response to a named failure**, each row in §2b naming the family, the failure
and the commit that introduced the rule. The title's claim is then restated accurately: the program
*became* falsification-first across H13–H19, and the paper documents that trajectory rather than
asserting it as a starting condition. I expect this to make the paper better, because the trajectory
is itself evidence for the thesis.

**New experiment required? NO.**

---

## MC5 — Generalizability

**Response: PARTIALLY ACCEPT.**

**Accepted.** P4 and P6 are conditional on the research being done without paid data and without
order-book history, and the paper states all ten principles at one confidence level. That is wrong.

**Partially disputed.** The referee writes that P4 is "largely moot for a funded desk". I would say
*differently instantiated* rather than moot: a funded desk buys a vendor database whose construction
choices it does not control and often cannot inspect, which is the same dependence on someone else's
retention policy, with the inspection channel removed. The CRSP delisting-return literature the
referee cites in MC10 is precisely a case of a paid, institutional database whose construction choice
distorted a published result for years. I will make that argument in the text rather than claim
general applicability.

**Evidence.** `H18_0_GATE.json` (venue retrieval differential 0.0 pp); H17.0's 78.0 pp label-free
coverage gap on free data.

**Revision.** V2: §9 marks each principle `GENERAL` or `CONDITIONAL (free data / no order book)`, and
§11 expands venue concentration from one sentence to a paragraph naming which results are
venue-specific.

**New experiment required? NO.**

---

## MC6 — H18.3: null or underpowered?

**Response: ACCEPT.**

The referee is right that the manuscript lets the label `NULL` carry interpretive weight it cannot
bear, and right that three statements are being conflated. The honest reading of my own numbers is
the referee's (2): a small, unstable, possibly regime-dependent effect, not a demonstrated absence.
The falsification suite supports this — a market-only variant reaches 0.2184 against the challenger's
0.22736, which is "small", not "zero".

**I am not changing the verdict, and the referee does not ask me to.** The frozen rule produced
`PRE-REGISTERED NULL` and that stands. What changes is the interpretation attached to it.

One point in the manuscript's defence, for the record: §3's taxonomy already defines
`PRE-REGISTERED NULL` as "the design and the data survived; the predictive claim did not", and §11
already says the intervals are a property of the sample. The failure is that neither statement is in
the abstract or the conclusion, where the label does its work.

**Evidence.** `h18_3_development.json` (`cluster_bootstrap.ci95_low = -0.00743`, `ci95_high =
0.06279`, `share_positive = 0.9345`); `H18_3_GATE.json` holdout block; `h18_3_falsification.json`.

**Revision.** V2: one sentence added to the abstract and one paragraph to §6.5 stating that
`PRE-REGISTERED NULL` means "failed the pre-registered support criteria", that the interval is
consistent with a small positive effect, that the development-to-holdout reversal with a base rate
moving from 5.822% to 11.792% is instability under a possible regime change, and that absence of
effect is **not** demonstrated at this sample size. §12 adjusted to match.

**New experiment required? NO.**

---

## MC7 — Dependence structure and the one-way cluster bootstrap

**Response: ACCEPT as a limitation; the remedy is deferred.**

All three channels the referee names are real and are unmodelled. Batch announcements are documented
in my own §5.3 — one notice can delist several assets, which is why the unit of analysis had to
change — and I did not carry that fact into the inference. Policy regimes are documented in
`H18_1_GATE.json` (`policy_regimes`: `BUSD_SUNSET` 271, `STABLE_QUOTE_ROTATION` 199), which is direct
evidence for the referee's second channel. The third follows from the first two.

The referee asks which direction the bias runs, and I should answer it in the text: unmodelled
positive dependence makes the reported interval **too narrow**, so the true interval is wider than
[−0.0074, +0.0628]. That cuts against the development result's meaningfulness and *for* the null,
which is worth stating plainly because it is the direction less favourable to an interesting paper.

**Evidence.** `H18_1_GATE.json: policy_regimes`; `h18_3_development.json: cluster_bootstrap.unit =
"asset-era"`.

**Revision.** V2: a dependence paragraph in §6.4 naming the three channels, stating that the reported
interval is likely too narrow, and listing two-way clustering (asset-era × announcement date) and a
temporal block bootstrap as the standard remedies, explicitly not performed.

**New experiment required? YES for the remedy — `DEFERRED — REQUIRES NEW EXPERIMENT`.** Stating the
limitation requires none.

---

## MC8 — H19.0's execution claim

**Response: ACCEPT.**

The referee is right and the correction is one the paper's own rules require. "Feasible for small
capital" implies an execution analysis I did not perform and state elsewhere I could not perform. The
evidence supports only "passes a coarse volume-based liquidity screen".

I note that the paper already discloses the absence of order-book data and already disclaims
profitability; the referee's point is that neither disclaimer covers *feasibility*, and that is
correct.

On "why 1%": no justification exists beyond judgement, which is MC3's point and is handled there.

**Evidence.** `H19_0_GATE.json`: `small_order_1k_share_of_median_hourly`, `liquidity_buckets_clean`
(31 events below US$100k/hour).

**Revision.** V2: every occurrence of "feasible for small capital" and "small-capital feasible"
replaced with "passes a coarse volume-based liquidity screen"; Figure 5's final bar relabelled
likewise; one sentence added to §7 listing what an execution analysis would require and this one
lacks — order book, spread, market impact, taker fees, funding cost, latency, and the intraday
distribution of volume around T0. The funnel's count of 32 is unchanged; only its description
changes.

**New experiment required? NO.**

---

## MC9 — H19.2: identification blocked, or design too rigid?

**Response: PARTIALLY ACCEPT — and the part I accept is the one that matters.**

**Accepted.** "Covariate adjustment cannot manufacture common support" is false as a general claim
about causal inference, and I should not have written a general principle from a specific design
failure. The referee's narrowed version — exact matching on a rare binary covariate can leave no
usable comparison set, and the ceiling should be computed on the full pool before the design is
frozen — is both true and the useful statement.

**Where I push back.** The referee suggests propensity weighting, overlap weights or trimming would
identify something. With 52 of 62 event assets tagged and a full-pool median of **7** eligible tagged
assets per announcement date, weighting does not create comparison information that is absent; it
replaces an empty cell with an extrapolation whose weight is concentrated on a handful of units, and
the estimand silently becomes one defined by the overlap region rather than by the events of
interest. The positivity literature the referee cites in MC10 makes exactly this distinction —
structural versus practical violations, with structural ones calling for a redefined estimand rather
than a cleverer estimator. A tagged pool of 134 assets *ever* is closer to structural than to
practical.

So: the **principle** is overclaimed and will be narrowed. The **decision** — that this confirmatory
design is not estimable on this venue — stands, and the referee partly grants it ("a well-powered
confirmatory design is unlikely under any weighting scheme").

**On the zero-price guarantee.** The referee says it deserves more prominence. I agree and will act
on it; it is the one feature of this family that makes a future redesign scientifically clean rather
than a rescue.

**Evidence.** `H19_2_PREFREEZE_FEASIBILITY.md` Check 3 (ceiling 0–27, median 7, 3 of 25 dates reach
20); `h19_2_prefreeze.json` (`2_controls_per_event.median = 1`, `frozen_bars`); `scripts/
h19_2_prefreeze.py` (`usecols=[0,5,7,8]`).

**Revision.** V2: §8's closing principle narrowed as above; two sentences added acknowledging
weighting and trimming, and explaining why a tagged universe of 134 makes this closer to a structural
positivity violation; the zero-price guarantee promoted to its own short subsection with the
`usecols` evidence.

**New experiment required? NO for the revision.** Any weighted redesign would be
`DEFERRED — REQUIRES NEW EXPERIMENT`, and because no price has ever been read it would be a new
design rather than a rescue.

---

## MC10 — Novelty

**Response: ACCEPT the positioning failure; PARTIALLY ACCEPT the novelty assessment.**

**Accepted without reservation.** The bibliography is fourteen entries of crypto delisting prediction
and crypto microstructure, and it does not contain the literature this paper competes with. For a
manuscript whose contribution is methodological, that is a serious failure and the referee is right
to weight it heavily. Bailey & López de Prado, Hou/Xue/Zhang, Menkveld et al., Shumway, Shumway &
Warther, Kapoor & Narayanan and the positivity literature all belong in §1 and §10.

**I also accept a novelty concession the referee did not press.** Checking Kapoor & Narayanan's
taxonomy: its second top-level category is "model uses features which are not legitimate". A feature
whose *classification* was derived using post-decision information is plausibly an instance of that
category. I should therefore not claim the **category** as new. What I can claim is the **detection
procedure and its measured rate**: re-deriving every removal classification under a strictly
backward-looking window and finding that 676 of 2,352 (28.7%) change class while every value and
every date in the record is correct. A procedure plus a rate is a contribution; a category is not.

**Where I partially disagree.** Menkveld et al. measures dispersion across many teams given *the same
dataset and the same hypothesis*. Its object is variation in analysis choices. This paper's object is
upstream of that: whether the dataset that all those teams would share represents the population it
claims to. The two are complementary, and I will say so rather than claim independence — but they are
not the same measurement, and "non-standard errors already covers this" would be wrong.

Similarly, Shumway and Shumway & Warther document delisting bias inside a vendor database and supply
a correction. The measurement in §5.1 is from the venue side: the venue retains what the aggregator
drops, at a 0.0 pp retrieval differential, which makes a survivorship-free risk set *constructible*
rather than merely *correctable*. That is a different claim, and it is the one I should foreground.

**Revision.** V2: (a) §1 and §10 rebuilt against the named literature; (b) the contribution restated
as the four measurements the referee himself identifies — venue-side archive asymmetry, the validated
universe reconstruction with a measured recall denominator, the pre-freeze full-pool common-support
ceiling, and the structural zero-price guarantee; (c) the four C1–C4 classes demoted from
"contributions" to "organising structure", with each class explicitly attributed to the prior
literature that established it; (d) the classification-level leakage claim narrowed from category to
procedure-plus-rate, with Kapoor & Narayanan cited.

**New experiment required? NO.**

---

## MC11 — Falsifiability of the framework

**Response: ACCEPT.**

I cannot construct a falsifying observation either, and the referee is right that a framework under
which every outcome is confirmation is not an empirical claim.

The honest answer is the referee's option (a): the framework is a **governance protocol**, not a
hypothesis about markets, and it should be judged on observables appropriate to a protocol. I would
name four, all of which this program can in principle report: the rate at which gates catch defects
*before* an economic result is produced versus after; the rate of post-freeze reversals (how often a
verdict changed after the hash was computed — in this program, zero); reproducibility of the
artefacts; and the number of hypotheses the protocol stopped from being promoted that a conventional
process would have promoted (H13 and H18.3 are both candidates).

**Revision.** V2: a new §9.1, "What would falsify this framework", stating that it is a governance
protocol, naming the four observables, and reporting the two this program can report from committed
artefacts (post-freeze reversals: zero; defects caught at a gate before an economic result: the
count is available from the ledger). The other two are declared unmeasured.

**New experiment required? NO** for stating it; counting defects caught per stage uses the existing
ledger.

---

## MC12 — Unit of contribution

**Response: ACCEPT.**

The paper is four papers and the referee's prescription matches my own reading: **methodological
quant-research paper, with the empirical cases as evidence**, governance compressed to one section,
and the implementation-defect material in an appendix.

**Revision.** V2: restructure per MC12 and MC1; §2 compressed after the MC4 split (the split adds
precision, not length, if the mature-protocol description is tightened); Table 3's retained rows move
into the taxonomy section and the rest to an appendix.

**New experiment required? NO.**

---

## MC13 — Negative-result selection

**Response: PARTIALLY ACCEPT.**

**Accepted.** The full-denominator table is the right fix and is cheap, and one withheld promoted
hypothesis against six documented failures is a denominator problem. I will report the registry in
full.

**Where the referee overlooks existing evidence.** On "would H18.3 be in the paper if the holdout had
been positive" — this one is checkable rather than rhetorical. `H18_3_PREREG.md` was frozen, hashed
and committed (`522bafb`) **before** any model was fitted, and it specifies the reporting obligations
and the verdict vocabulary for *both* outcomes, including the support labels `STRONG_SUPPORT` and
`SUPPORTED_BUT_SMALL`. The directional veto added by amendment A3 was likewise committed (`203390b`)
before the holdout was opened. So the *reporting* of H18.3 was not conditioned on its outcome, and
the hash and commit order are the evidence. What *was* conditioned on outcome is the family's
promotion to flagship case in the manuscript — which is MC2's point, and which I concede there.

On H8: the referee is right that one paragraph is insufficient. I will not move H8's performance into
this paper, because that would convert a methodological argument into a performance claim and the
evidence belongs to a separate paper. I will instead report, from the registry, **how many families
reached each terminal state**, so the denominator is visible without importing H8's results.

**Evidence.** `H18_3_PREREG.sha256` and commit `522bafb` predate `4aa4180`;
`H18_3_PREREG_AMENDMENT_01.sha256` and `203390b` predate the holdout; `HYPOTHESIS_LEDGER.md` has
every family.

**Revision.** V2: full-registry appendix table (shared with MC2); a paragraph in §6.1 noting that the
pre-registration specified reporting for both outcomes before the holdout was opened, with the commit
order as evidence; H8's paragraph extended to state what it does and does not establish.

**New experiment required? NO.**

---

## MC14 — "The model is almost never decisive"

**Response: ACCEPT.**

The sentence generalises from a retrospectively selected sample. The referee is right that it is the
most quotable and least supported claim in the paper.

**Revision.** V2: §1 and §12 narrowed to "in the seventeen families reported here, the decisive step
was the model in none of the cases we document", with an explicit note that twelve further families
are summarised but not analysed, and that the four cases were selected to illustrate the thesis.

**New experiment required? NO.**

---

## MC15 — Single researcher, single codebase

**Response: ACCEPT.**

The referee's sharpest sentence is the correct one: churn of 0.0 across 40 double-reviewed events
shows the reader is self-consistent, not that the reader is right. The same person set the
thresholds, wrote the code, found the defects, judged them, and wrote the audit that certifies the
result. `scripts/paper_audit.py` verifies that numbers trace to artefacts; it cannot verify that the
artefacts measure what I say they measure.

I should name the cheapest viable independent check rather than gesture at replication. My candidate:
**an independent reconstruction of the 201-event universe from the venue's public archive by a second
party**, compared against `H18_1B_FULL_DELIST_EVENTS.parquet` on asset, announcement date and stated
trading end. It requires no credentials, no paid data and no coordination with me, and it tests the
construction claim that most of the paper rests on.

**Revision.** V2: §11's one sentence expanded to a subsection naming the single-point-of-failure
explicitly, stating what the double-pass gold sets do and do not control for, and naming the
independent check above with its acceptance criterion.

**New experiment required? NO** for naming it. Performing it requires a second party and is
`DEFERRED`.

---

## Minor concerns

| # | concern | response | V2 action |
|---|---|---|---|
| 1 | "Manufacture" overstates | **ACCEPT** | Subtitle changed to "…How Data Construction, Survivorship, Semantic Errors and Execution Constraints Create and Destroy Apparent Trading Opportunities". |
| 2 | "Alpha discovery" is practitioner vocabulary | **PARTIALLY ACCEPT** | Keep in the title (it is the program's name and is accurate about the activity); define it once in §1 and use "systematic strategy research" in the body. |
| 3 | Abstract too broad | **ACCEPT** | Rewritten to lead with the four measurements identified in MC10. |
| 4 | Family nomenclature | **PARTIALLY ACCEPT** | Descriptive names in the body; codes retained in parentheses on first use and in the registry, because they are the key into the artefact trail and removing them would break traceability. |
| 5 | Artefact references in prose | **ACCEPT** | Moved to footnotes or the appendix. |
| 6 | Figure 1 carries no quantities | **ACCEPT** | Dropped; its content merges into Figure 2. |
| 7 | Figure 6b shows 8 of 25 dates | **PARTIALLY ACCEPT** | Moved to an appendix with the limitation restated. I decline to recompute the full series: it would be a new computation, and reporting 8 recorded dates with the limitation stated is more honest than regenerating data to make a figure look complete. |
| 8 | Captions not self-contained | **ACCEPT** | Units and sample sizes added. |
| 9 | H8 placement | **ACCEPT** | See MC13. |
| 10 | Table 3 length | **ACCEPT** | See MC1. |
| 11 | PIT and common support undefined | **ACCEPT** | Both formally defined at first use. |
| 12 | No public repository or DOI | **ACCEPT** | Public archive with a DOI before any external release; listed as a blocking item. |
| 13 | `ECONOMIC REJECT` doing two jobs | **ACCEPT** | Relabelled `IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED` in the taxonomy and used consistently. |
| 14 | §10 asserts what desks should do | **ACCEPT** | Narrowed to implications for research under comparable constraints. |
| 15 | No LaTeX compilation | **ACCEPT** | Blocking item before external release. |

---

## The result taxonomy — defended

The referee did **not** conflate the categories, and I note that explicitly, because most readers
will. The taxonomy stands as written, with one relabelling (minor 13), and I restate it here for the
record:

- **H19.2 `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL` is not a null.** No pre-registration was
  frozen, no hash computed, and no price column was ever read — the loader requests four non-price
  columns and the OHLC columns never entered memory. There is no economic inference about H19-P3A of
  any kind, in either direction.
- **H14's data-gate failures are not negative economic results.** They say nothing about Brazilian
  corporate events; they say the extraction could not be validated.
- **H18.3's `PRE-REGISTERED NULL` is not a data failure.** The data and the design survived every
  structural check, including a zero-violation leakage audit. The predictive claim did not survive
  its own pre-registered criteria. MC6's correction is to the *interpretation* of that label, not to
  the label.
- **H19.0's execution gate is not a profitability test.** No return, carry or holding period was
  computed for any event, and the paper may not be read as evidence that the trade is or is not
  profitable.

---

## Items deferred

| item | source | why deferred |
|---|---|---|
| Threshold sensitivity analysis | MC3 | Requires re-running gates and fits at alternative thresholds. `DEFERRED — REQUIRES NEW EXPERIMENT`. |
| Two-way cluster / block bootstrap for H18.3 | MC7 | Requires refitting and resampling. `DEFERRED — REQUIRES NEW EXPERIMENT`. |
| Weighted or trimmed redesign of H19-P3A | MC9 | Requires a new design and would require reading price. `DEFERRED — REQUIRES NEW EXPERIMENT`. Because no price has ever been read, such a redesign would be a new study, not a rescue. |
| Independent reconstruction of the 201-event universe | MC15 | Requires a second party. `DEFERRED`. |

**None of these was executed in preparing this response**, and none is required for the V2 revision
to answer the referee's eleven no-experiment items.
