# REFEREE REPORT — *Falsification-First Alpha Discovery*

**Manuscript version:** V1, frozen at commit `52a980a`, `paper.md` SHA-256 `1853bce0…`
**Referee:** #2
**Date of report:** 2026-10-11

---

## Recommendation

# **MAJOR REVISION**

I considered Reject seriously, and I set out below the five conditions under which I would move to
it. I do not recommend it today for one reason only: the manuscript contains at least two
measurements that I have not seen made elsewhere and that are checkable from the committed
artefacts. Everything else in the paper — the framing, the claimed contribution, the novelty
positioning, the taxonomy, and several of the headline sentences — is either already in the
literature, is unfalsifiable as stated, or rests on thresholds the author chose and never perturbed.

The paper currently reads as though its contribution is the *process*. The process is the weakest
part. The contribution, if there is one, is two or three specific, replicable measurements, and the
author has buried them.

---

## Summary of the paper

The manuscript argues that quantitative trading research fails most often before any model is fitted,
and that the standard defenses against overfitting do not address this. It reports seventeen
hypothesis families (H13 to H19.2) run as a single research program by one researcher on free public
data, under a governance protocol requiring explicit gates, pre-registration, frozen splits and a
single-use holdout. It organises its findings into four contribution classes (data construction,
semantics, point-in-time leakage, execution), a six-label result taxonomy, and ten methodological
principles.

Four empirical cases carry the argument. H13 is a US micro-cap net-net screen whose median 12-month
outcome of +18.3% falls to +3.7% under central assumptions and 0.0% under severe ones once the 52.9%
of candidate issuers with no current ticker are restored; the paper reports an inverted risk gradient
(−23.46 pp) as the diagnostic fingerprint of the hole. H18 rebuilds a cryptocurrency venue's
full-delisting universe from the venue's own archive, expanding it from 84 to 201 events, and then
pre-registers and executes a predictive test that is positive in 8 of 8 rolling-origin folds
(pooled ΔPR-AUC +0.0270, +13.46%) and is nonetheless declared `NULL` after its cluster bootstrap
crosses zero, its materiality gate fails, and its single-use holdout reverses sign (−0.0075). H19.0
reduces 201 documented delistings to 32 that pass a small-capital liquidity rule, without computing
any return. H19.2 stops before freezing a pre-registration because matching on liquidity band and
the venue's public risk warning leaves a median of 1 matched control per event against a floor of 20,
with a full-pool ceiling whose median is 7.

The central evidence is the committed artefact trail: a 126-row claim–evidence matrix, gate JSONs,
SHA-256-hashed pre-registrations, and build scripts that regenerate every table and figure.

**My main concern is that the paper's stated contribution — "data construction, semantics, PIT
validity, identification and execution should be falsified before the trading hypothesis" — is
already established, with larger samples and stronger designs, across at least four literatures the
manuscript does not engage with.** What is genuinely new here is narrower and more interesting than
what the author claims, and the current framing actively obscures it.

---

## Major concerns

### MC1 — Is this science, or an engineering post-mortem?

The manuscript devotes substantial space (Table 3, §5.3, §8.1) to defects in the author's own code:
a pagination marker used incorrectly, two archive legs stored in different time units, a NaN treated
as truthy, a `0.0` treated as falsy, a date parser that rejected slash-formatted dates, a regular
expression that matched the word "alpha". Each is narrated with its detection and its lesson.

I accept the author's framing that these produced *plausible* output rather than crashes. That is
the only thing separating them from an ordinary bug list, and the manuscript leans on it heavily.

But the author has not done the work of showing which of these are *methodological classes* rather
than local accidents. Test: **remove every proper noun and every specific defect from the paper and
ask what survives.** My reading is that three classes survive — (i) a source's coverage is a
measurable quantity and must be measured against the source's own reported total; (ii) two legs of a
single comparison may be stored under different conventions by the same provider; (iii) a
classification can use future information while every value and every date in the record is correct.
The remaining eight or nine rows of Table 3 are competent debugging, not findings. `0.0`-is-falsy is
a Python idiom hazard. NaN truthiness is the same. A regex matching a substring is not a lesson about
markets, data or research design.

If this is an empirical finance paper, Table 3 must shrink to the classes that generalise, and the
rest belongs in an appendix or a software report. As it stands, a hostile reading — "researcher made
errors, then found them, then wrote a paper about finding them" — is available to any reviewer, and
the manuscript does not pre-empt it.

**Additionally:** the paper never acknowledges that discovering one's own bug carries *no*
information about the market. §17 of the author's own brief apparently required this separation, and
§5.3 does separate the defect from the economic question in most places. But the overall architecture
still spends more words on defects than on the two measurements that would interest a finance
audience.

### MC2 — Selection of H13 to H19

The manuscript covers families 13 through 19 and relegates H1 to H12 to a registry it does not
reproduce. The stated reason (§"Scope") is that the methodological contribution is strongest there.
That is a selection on the outcome.

Specific questions the author must answer:

1. **How many hypothesis families existed in total, and what happened to each?** The paper says H1–H12
   exist. It does not report their verdicts, their failure classes, or whether any of them failed for
   reasons that would weaken the thesis — for example, failing because a model overfitted, which is
   the mechanism the paper argues is *not* usually decisive.
2. **Were H13–H19 chosen because they illustrate the thesis?** The author cannot answer this with the
   paper as written, because the thesis was formulated after the families ran. The honest answer is
   almost certainly yes, and the paper should say so.
3. **Would the stated methodology be the same if these families had produced different outcomes?**
   This is the decisive question. If H18.3's holdout had been positive, would the paper argue that
   frozen out-of-sample evaluation is essential? Probably — but it would then be a different paper
   with a different title, and the case that carries §6 would not exist.

The author must distinguish **hypothesis selection** (which was pre-registered and is defensible)
from **case selection for the manuscript** (which was retrospective and is not). The current text
blurs them: §2.2 describes pre-registration at length, which invites the reader to assume the paper's
own case selection inherits that discipline. It does not.

**Minimum fix:** report the full denominator. All families, all verdicts, in one table, including
H1–H12 — the registry exists, so this costs nothing — and an explicit statement that the four case
studies were selected after the fact to illustrate a thesis formed after the fact.

### MC3 — Gate arbitrariness

The paper's conclusions are threshold-driven, and almost every threshold is the author's judgement.
A partial list, with my reading of its basis:

| threshold | where | basis I can identify |
|---|---|---|
| 99% catalog coverage | H18.1b harvest guard | none stated; engineering judgement |
| 95% availability bar | H19.2 legs | none stated |
| 20 matched controls | H19.2 | none stated; **this threshold alone produces the paper's §8 conclusion** |
| 40 confirmatory events | H19.2 | none stated |
| 73 valid transitions | H19.2 | appears to be 80% of 91 |
| US$1,000 at ≤1% of median hourly notional | H19.0 | none stated; **produces the 63 → 32 reduction** |
| \|calibration shift\| < 0.10 | H18.3 | none stated, and the author concedes it is defective |
| relative ΔPR-AUC ≥ 10% | H18.3 materiality | none stated |
| top-decile lift improvement ≥ 15% | H18.3 | none stated |
| 90-day risk-set entry | H18.3 | diagnosed post hoc from a coverage differential |
| +20 pp burn-tertile spread | H13 | none stated |
| +10 pp filter improvement | H13 | none stated |

I am not asking the author to defend each number theoretically; most have no theory. I am asking for
three things.

First, **say plainly which thresholds are engineering judgements**. The manuscript's rhetorical force
comes from "the bar was not moved", repeated several times. That sentence only has force if the bar
had a reason. A bar chosen by intuition and then not moved is discipline, but it is not evidence.

Second, **acknowledge which conclusions are threshold-determined.** At least three are. H19.2's
entire `IDENTIFICATION BLOCKED` verdict follows from `MIN_CONTROLS = 20`; at 10 it would have had
more events, at 5 more still. H19.0's headline funnel endpoint of 32 is a direct function of the 1%
rule. H18.3's materiality failure is a direct function of a 0.10 calibration bar the author himself
calls defective.

Third, **report what a reasonable perturbation would do.** I am explicitly *not* asking for this to
be computed during revision if it requires re-running experiments — see the author's own constraint —
but the manuscript must at minimum state which conclusions are robust to a threshold change and which
are not, and where that is unknown, say it is unknown.

The current text does the opposite: it presents threshold-determined outcomes with the vocabulary of
findings.

### MC4 — Ex post governance presented as ex ante

This is my most serious methodological objection.

The paper's title is "Falsification-First", and §2 presents a governance protocol as though it framed
the work. Yet the paper's own evidence shows the protocol *growing* as the families progressed:

- SHA-256 pre-registration freezing appears first at H18.3. The reproducibility appendix confirms
  H13 "predates the SHA-256 freeze protocol."
- The structural leakage audit covering feature *classification* was added at H18.3 after the
  H18.2 classes were found non-point-in-time.
- The directional holdout veto (amendment A3) was added at H18.3.
- Asset-era keying was introduced at H18.1b after a ticker-keyed join failed, and then used at H19.0.
- The "served candle is not a traded market" rule appears first at H18.1b and is then applied at
  H19.0 and H19.1.
- The pre-freeze no-price feasibility check appears first at H19.1/H19.2.

So the governance in §2 is substantially the *output* of H13–H19, presented as its *input*. The
manuscript must not allow a reader to believe that H13 was run under the protocol described in §2 —
it was not, and §2 never says so.

**This is the same error class the paper accuses others of: using information from the future.** The
protocol's maturity at H19 is applied retrospectively to the whole program in the framing.

**Required fix:** §2 must be split explicitly into (a) rules in force from the start, (b) rules added
at a named family in response to a named failure, with the family and the failure identified. Without
this, "falsification-first" is a claim the paper's own evidence contradicts.

### MC5 — Generalizability

The empirical content is concentrated: H18 and H19 are a single cryptocurrency venue, and H13–H17
are US regulatory filings reached through free public interfaces. The author's limitations section
concedes venue concentration in one sentence. That is not enough.

My question is the one an editor will ask: **why should an equity quant, a futures researcher or an
institutional systematic desk care?**

Several of the paper's principles look venue-specific to me, not general:

- **P4 (record ownership determines observability).** This is a finding about a venue that publishes
  a public archive and a data vendor that does not. Institutional desks buy CRSP, Refinitiv or
  Bloomberg data where delisting returns and point-in-time snapshots are a priced product. The
  finding is real for free-data research and largely moot for a funded desk.
- **P6 (a served candle is not a traded market).** True and important in illiquid crypto. On a
  consolidated equity tape with trade-level data and an order book, a desk already knows this.
- **P7 (common support must be demonstrated).** Generalises — but see MC10 on novelty.
- **P1, P2, P3, P5** generalise well and are the strongest part of §9.

The paper should say which principles are general and which are conditional on the research being
done without paid data or order-book history. At present all ten are stated at the same level of
confidence, and at least two do not deserve it.

### MC6 — H18.3: is this a null, or is it underpowered?

The paper's flagship case declares `NULL` on a design with **110 development events and 86 holdout
events**. The pooled cluster-bootstrap interval is [−0.0074, +0.0628] — a width of roughly 0.07 on a
point estimate of 0.027. That interval is consistent with no effect, and equally consistent with an
effect twice the size of the point estimate.

The manuscript says this honestly in §6.4 ("With 110 unique events across 440 clusters, the interval
is wide"). But it then uses the verdict label `NULL` throughout, including in the abstract and
conclusion, where a reader will take it as evidence against the hypothesis.

Three distinct statements are being conflated:

1. **The pre-registered support criteria were not met.** True, and demonstrated.
2. **The estimate is unstable across evaluation blocks.** Also true: 8 of 8 development folds
   positive, holdout negative, with the base rate shifting from 5.822% to 11.792% between them. That
   base-rate shift is itself a regime change the paper does not interrogate.
3. **There is no effect.** *Not* demonstrated, and not demonstrable at this sample size.

The paper's own falsification suite points at (2) rather than (3): a market-only variant reaches
0.2184 against the challenger's 0.22736, so the incremental content is small but not obviously zero.
A small, unstable, possibly regime-dependent effect is a different scientific object from a null.

I am **not** asking the author to change the verdict. The verdict is what the frozen rule produced,
and changing it after the fact would be the sin the paper is about. I am asking the author to stop
letting the verdict label do interpretive work it cannot support, and to state explicitly that
`PRE-REGISTERED NULL` means "failed pre-registered support", not "evidence of no effect". The
distinction should appear in the abstract, not only in §11.

### MC7 — H18.3: dependence structure and whether a one-way cluster bootstrap suffices

The bootstrap clusters on asset-era. That handles the repeated weekly landmarks for a single asset.
It does not handle at least three other dependence channels I can identify from the manuscript:

1. **Batch announcements.** The venue delists several assets in one notice — the paper says so
   explicitly in §5.3 ("one notice can delist several assets"), and that is why the unit of analysis
   had to change. Those assets share an outcome date and almost certainly share the decision process
   that produced it. Clustering on asset-era leaves this dependence entirely unmodelled.
2. **Calendar and regime dependence.** The base rate moves from 5.8% to 11.8% between development and
   holdout. If delisting decisions arrive in venue-policy waves — and §5.2's policy regimes
   (`BUSD_SUNSET`, `STABLE_QUOTE_ROTATION`) suggest they do — then asset-era clusters are not
   independent draws.
3. **Cross-sectional contemporaneity.** Route contraction is driven partly by venue-wide decisions
   (a quote asset being retired removes routes for many assets at once), so the predictor is itself
   cross-sectionally correlated.

A two-way cluster (asset-era and announcement date, or asset-era and calendar quarter) or a block
bootstrap over time would be the standard response. I recognise this requires recomputation and
therefore cannot happen in this revision under the author's constraints. It must at minimum be
stated as a limitation of the inference, in §6, not left to a general sentence about wide intervals.

As it stands, the reported interval is probably **too narrow**, which cuts *against* the paper's own
verdict — a wider interval makes the null more secure but makes the development result less
meaningful. The author should say which direction the bias runs.

### MC8 — H19.0: the execution claim is stronger than the measurement

The funnel's final step rests on a single rule: a US$1,000 order must be at most 1% of median hourly
notional. From this the paper reports 32 events as "feasible for small capital" and builds a
section-level conclusion.

Objections:

1. **Why 1%?** No justification is given. It is a plausible rule of thumb and nothing more.
2. **Hourly notional is a poor proxy for fill.** It says nothing about whether the volume was
   concentrated in seconds around the announcement, about the state of the order book, or about
   whether a resting order would have been filled at a usable price.
3. **No order book, no spread, no impact, no fees, no latency.** The paper acknowledges having no
   order-book archive, but then uses a volume proxy to make a feasibility claim anyway. For assets
   this illiquid — 31 of 63 clean events trade under US$100k per hour — the spread alone could
   dominate any effect the strategy might have had.
4. **"Shortable" conflates availability with cost.** A perpetual that traded is not necessarily a
   perpetual one could have shorted at a usable price with funding costs that leave anything behind.

The claim the evidence supports is narrower: *32 of 63 clean events pass a coarse volume-based
liquidity screen*. The claim the paper makes — "feasible for small capital" — implies an execution
analysis the paper did not perform and says elsewhere it could not perform.

I note, in the author's favour, that §7 explicitly disclaims profitability. The wording problem is
about *feasibility*, not profitability, and the disclaimer does not cover it.

### MC9 — H19.2: is identification blocked, or is the design unnecessarily rigid?

The paper's §8 conclusion — "covariate adjustment cannot manufacture common support" — is stated as
a principle. I do not accept it as stated.

What the evidence shows is that **exact matching on a binary warning indicator within liquidity
bands** leaves a median of one control per event. That is a fact about exact matching, not about
identification in general. Standard responses exist and are not discussed:

- **Propensity-score weighting** with the warning status as a covariate, with overlap diagnostics
  reported rather than imposed as a hard count.
- **Overlap weights** or trimming, which are designed precisely for the near-violation case.
- **A within-asset design** using the warning date itself as a second event, if the data permit.
- **Relaxing exactness to a coarsened match** on warning status and time-since-warning.

The author's own documentation lists "drop tag matching and control statistically" as Option A and
describes it as weakening identification. I agree it weakens identification. **Weaker identification
is not the same as no identification**, and the paper presents a design choice as an impossibility
theorem.

I will say clearly what I do accept: with 62 candidate events and a tagged universe of 134 assets
ever, a well-powered confirmatory design is unlikely under any weighting scheme. And I credit the
author unreservedly for the fact that **no price was ever read** — this means any future redesign is
a genuinely new design rather than a rescue after seeing an outcome, which is a materially stronger
position than almost any paper I review. That fact deserves more prominence than it currently gets.

But the section's principle must be narrowed from "covariate adjustment cannot manufacture common
support" to something like "exact matching on a rare binary covariate can leave no usable comparison
set, and the ceiling should be computed on the full pool before the design is frozen". The second
statement is defensible and useful. The first is false as a general claim about causal inference.

### MC10 — Novelty

I searched the literatures the paper positions itself against. The manuscript cites fourteen
references, of which four are read in full, and **none of them is from the methodology literature the
paper's contribution actually competes with**. The bibliography is almost entirely cryptocurrency
delisting prediction and crypto microstructure. That is a serious positioning failure.

Here is what is already established:

| claimed contribution | prior work I would expect to be cited |
|---|---|
| multiple testing and selection inflate backtested performance; the number of trials must be accounted for | Bailey & López de Prado, *The Deflated Sharpe Ratio* (JPM 2014), which corrects a reported Sharpe for the number of trials, skewness and kurtosis; the associated probability-of-backtest-overfitting work |
| the published anomaly literature does not replicate, and p-hacking is pervasive | Hou, Xue & Zhang, *Replicating Anomalies* (RFS), reporting 286 of 447 anomalies (64%) insignificant at 5% with NYSE breakpoints and value weighting |
| researcher discretion produces variation that standard errors do not capture | Menkveld et al., *Nonstandard Errors* (Journal of Finance 79(3), 2024), a multi-team design measuring exactly this dispersion across many research teams on identical data and hypotheses |
| **survivorship and delisting bias materially distort return estimates** | Shumway (1997) and Shumway & Warther (1999), which document missing CRSP delisting returns, estimate a −55% correction for performance-related Nasdaq delistings, and show the Nasdaq size effect disappears after correction |
| **data leakage is the dominant cause of irreproducible ML-based science, and admits a taxonomy** | Kapoor & Narayanan, *Leakage and the Reproducibility Crisis in ML-based Science* (Patterns, 2023): a survey across 17 fields, 294 affected papers, an **eight-type leakage taxonomy**, and model info sheets as a remedy |
| **common support / positivity must be demonstrated, and violations are structural or practical** | Petersen et al. (2012) on positivity violations and diagnostics; the structural-versus-stochastic positivity distinction; overlap weighting and trimming literature |
| pre-registration reduces questionable research practices | the registered-reports literature; the *Journal of Behavioral and Experimental Finance* registered-reports format |

Set against this, the paper's four contribution classes are not new. C1 is Shumway. C3 is Kapoor &
Narayanan plus Petersen. The "researcher degrees of freedom" framing is Menkveld et al. The
"spectacular backtest is a bug candidate" message is Bailey & López de Prado and Hou, Xue & Zhang.
Even the paper's distinctive structural claim — that leakage can occur in the *classification* of a
feature while every value and date is correct — needs to be checked against Kapoor & Narayanan's
eight-type taxonomy before it can be claimed as new.

**What I think is actually novel**, and what the author should rebuild the paper around:

1. **The venue-archive asymmetry, measured from the venue side.** Shumway documents the bias in a
   vendor database. Ammann et al. (cited) document it in crypto and attribute it to aggregator
   convention. This paper measures the *other side*: the venue retains what the aggregator drops, at
   0.0 pp retrieval differential, which makes a survivorship-free risk set constructible without paid
   data. I have not seen this measured. It is a small contribution, and it is real.
2. **The 84-to-201 universe reconstruction with a measured recall denominator.** The event-count
   expansion is itself unremarkable; the *validation* — recall 0.9801 against candle-measured
   cessation, with all 60 unexplained non-announcements individually classified — is better than most
   event-study samples I review, and the method transfers.
3. **The full-pool common-support ceiling computed before freezing a design.** Positivity diagnostics
   in the literature are mostly post hoc, on the analysed sample. Computing the ceiling on the
   complete eligible pool, before the design is frozen and before any outcome is read, is a
   procedural contribution I have not seen stated this way. This is the paper's best idea and it
   occupies half a subsection.
4. **The zero-price structural guarantee.** Demonstrating that no outcome could have been seen
   because the loader physically could not read those columns is a stronger form of blinding than the
   declarative kind. Also under-sold.

The current manuscript foregrounds (a) a governance protocol that is largely a synthesis of existing
recommendations and (b) a defect catalogue. It backgrounds the four things above. That is the wrong
way round.

### MC11 — Is the framework falsifiable?

The paper is called "Falsification-First". I ask the obvious question: **what result would falsify
the framework itself?**

As written, I cannot construct one. Every outcome appears to confirm it:

- A family fails a data gate → the framework was right to gate.
- A family passes gates and produces a null → the framework was right to pre-register.
- A family is blocked at identification → the framework was right to check common support.
- A family survives (H8) → the framework does not reject everything.

A framework under which every observation is confirmation is not an empirical claim. The author
should either (a) state explicitly that the framework is a governance protocol rather than a
hypothesis about markets, and then specify the observable quantities on which a governance protocol
can be judged — detection rate, post-freeze reversal rate, reproducibility, avoided false promotions
— or (b) state what pattern of results across families would have counted as evidence against it.

Without this, §9 and §12 are a statement of research values, not a scientific claim, and the paper
should not use the vocabulary of evidence for them.

### MC12 — What is the unit of contribution?

The paper is currently four papers:

- **A.** an empirical finance paper (H13's survivorship quantification, H18's event universe);
- **B.** a methodological quant-research paper (the taxonomy, the ten principles);
- **C.** a reproducibility/governance paper (the protocol, the hashes, the artefact trail);
- **D.** a data-engineering paper (Table 3, the pagination and unit defects).

Each audience will find half the manuscript irrelevant. An empirical finance referee will skip Table
3. A reproducibility audience will not care about perpetual futures microstructure. The author must
choose.

My own view: the strongest version is **B with A as evidence**, with C compressed to one section and
D moved to an appendix or a companion software note. That is also the version with the clearest
journal home.

### MC13 — Negative-result selection

H18.3 is compelling because development was positive and the holdout was negative. I ask directly:
**would this family be in the paper if the holdout had been positive?**

If the answer is "yes, as a demonstration that the process can promote a hypothesis", then the paper
needs to show a case where that actually happened, and H8 — mentioned in a single paragraph and
explicitly reserved for another paper — is not sufficient. One promoted hypothesis, whose evidence is
withheld, against six documented failures, is a denominator problem.

If the answer is "no", then the manuscript's case selection is conditioned on the outcome, which is
the behaviour it criticises elsewhere.

The experiment registry already exists. Reporting it in full — all families, all verdicts, including
the twelve not discussed — would cost the author nothing and would convert this objection into a
measured statement. I regard this as the single cheapest and highest-value revision in the report.

### MC14 — "The model is almost never decisive"

§1 states that "the decisive question was almost never which model was fitted" and §12 repeats the
claim. This generalises from a sample of families that were selected, after the fact, because data
and governance turned out to be decisive in them.

The paper cannot make this claim. What it can say is: *in this program, in these seventeen families,
the decisive step was the model in no case we report.* Even that is weaker than it looks, since
twelve families are not reported.

Please narrow the wording in both places. As written it is the single most quotable sentence in the
paper and the least supported.

### MC15 — Single researcher, single codebase

One person defines the gates, writes the pipeline, finds the defects, audits the finding, interprets
the verdict, and writes the paper. The gold sets use two passes with the first persisted before the
second, which is good practice and which I credit — but both passes are the same reader. Reviewer
churn of 0.0 across 40 double-reviewed events tells me the reader is self-consistent, not that the
reader is right.

The manuscript's own limitation section says this in one sentence. It deserves more, because it
interacts with every other concern in this report: the thresholds are the author's, the case
selection is the author's, the taxonomy is the author's, and the audit that certifies all of it is
also the author's. `scripts/paper_audit.py` checks that numbers trace to artefacts; it cannot check
that the artefacts measure what the author says.

**What would independent replication require?** The author should state it concretely: a second
researcher re-deriving at least one gate from the raw documents, a second gold-set pass by a
different reader, or an independent reconstruction of the 201-event universe from the venue's
archive. Naming the cheapest viable independent check would substantially strengthen the paper, even
if it is not performed.

---

## Minor concerns

1. **Title.** "Manufacture Trading Strategies" overstates. The paper documents that apparent
   opportunities can be *created or destroyed* by construction choices; "manufacture" implies
   deliberate fabrication and will read as polemical.
2. **"Alpha discovery"** is practitioner vocabulary. For a finance journal, "strategy research" or
   "systematic strategy development" is more precise and less likely to signal a non-academic
   submission.
3. **Abstract length and breadth.** It is one long paragraph covering four cases, a taxonomy and ten
   principles. It should lead with the two or three genuinely novel measurements (MC10).
4. **Family nomenclature.** "H18.1b", "H19-P3A", "H14.3" are internal identifiers. A reader cannot
   hold seventeen of them in mind. Rename to descriptive labels in the text and keep the codes in the
   registry table.
5. **Internal artefact references in the prose.** Sentences like "the artefact records
   `holdout_opened_once: true`" belong in the appendix, not the body.
6. **Figure 1** is a schematic with no quantities and conveys little a sentence could not. Consider
   dropping it or merging it with Figure 2.
7. **Figure 6b** plots 8 of 25 dates, which the caption admits. A reader will ask why the other 17
   are missing, and "it was summarised to its median" is unsatisfying in a paper about artefact
   discipline. Either report all 25 or move the panel to an appendix.
8. **Figure captions** carry source paths but not units or sample sizes; they should be
   self-contained.
9. **H8 placement.** One paragraph in §11 is the wrong place for the only counterexample to the
   paper's thesis. See MC13.
10. **Table 3 length.** Twelve rows, several of which are language-level programming hazards. Compress
    (MC1).
11. **Definitions.** "Point-in-time" and "common support" are used throughout but never formally
    defined. A finance audience will know the first; many will not know the second in the technical
    sense the paper uses.
12. **Code availability.** The paper refers to committed scripts and a repository path on a local
    Windows machine. There is no public repository, DOI or archive. For a paper whose central claim is
    reproducibility, this is a conspicuous gap.
13. **"Economic REJECT" versus "ECONOMIC NULL".** The taxonomy table uses `ECONOMIC REJECT` while the
    text sometimes says the economic question is unresolved. The label is doing two jobs.
14. **Section 10** ("Implications") asserts what desks and academics should do, without evidence from
    desks or academics. Soften to implications *for research conducted under similar constraints*.
15. **No LaTeX compilation.** `paper.tex` has never been compiled. For submission this must be fixed;
    it is honestly disclosed, which I note favourably.

---

## Scoring

| dimension | score (1–5) | rationale |
|---|---|---|
| **Novelty** | **2** | The four stated contribution classes are established in literatures the paper does not cite (MC10). Three or four specific measurements appear novel but are not foregrounded. |
| **Importance** | **3** | The questions matter and the free-data constraint makes them matter more, not less. The paper's importance is capped by its framing. |
| **Identification** | **2** | H18.3 is a wide-interval null on 110 events (MC6, MC7). H19.2 is explicitly unidentified by design (MC9). H19.0 computes no outcome. H13 is the strongest and is a bias-bounding exercise rather than an identified estimate. |
| **Empirical rigor** | **4** | Gold sets with persisted first passes, measured recall against an independent denominator, explicit missingness differentials, named diagnostics below bar. Better than most manuscripts I review. |
| **Statistical rigor** | **3** | Correct instincts — cluster bootstrap, embargo, single-use holdout, placebo — but one-way clustering with known additional dependence (MC7), and thresholds without basis (MC3). |
| **Reproducibility** | **4** | Hashes, frozen pre-registrations, build scripts, a claim–evidence matrix, a byte-for-byte regeneration check. Loses a point for no public repository and no compiled output (minor 12, 15). |
| **Clarity** | **3** | Well written sentence by sentence; the architecture asks the reader to hold too much (MC12, minor 4). |
| **Generalizability** | **2** | Venue-concentrated and free-data-concentrated; at least two of ten principles are conditional on those constraints (MC5). |
| **Journal fit** | **2** | As submitted, I cannot identify the journal. It is too methodological for an empirical finance outlet and too finance-specific for a methodology or reproducibility venue (MC12). |

---

## Rejection test

### What would make me reject this paper outright

1. **If the author declines to report the full experiment denominator** (MC2, MC13). Case selection
   conditioned on outcome, in a paper about selection effects, is not survivable.
2. **If §2's governance continues to be presented as ex ante** when the paper's own evidence shows it
   was assembled across H13–H19 (MC4). This is a correctness issue, not a framing preference.
3. **If the novelty positioning is not rebuilt** against the methodology literature (MC10). A paper
   claiming to document research-process failure modes while citing only crypto delisting prediction
   is not competitive.
4. **If `NULL` continues to carry the interpretive weight of "no effect"** in the abstract and
   conclusion (MC6). The verdict must stay; the interpretation must be corrected.
5. **If "feasible for small capital" and "covariate adjustment cannot manufacture common support"
   survive unchanged** (MC8, MC9). Both are claims the evidence does not reach.

### What would change my recommendation to Accept or Minor Revision

Concretely, and in order of value:

1. **Report every hypothesis family, H1 through H19.2, with its verdict and failure class, in one
   table**, and state in the text that the four case studies were selected retrospectively. Existing
   registry; no new computation. *(Addresses MC2, MC13.)*
2. **Split §2 into "in force from the start" and "added at family X after failure Y"**, with the
   families named. Existing commit history and amendment documents; no new computation. *(MC4.)*
3. **Rebuild §1 and §10 against the methodology literature** — at minimum Bailey & López de Prado,
   Hou/Xue/Zhang, Menkveld et al., Shumway, Shumway & Warther, Kapoor & Narayanan, and the positivity
   literature — and restate the contribution as the three or four measurements that survive that
   comparison. *(MC10.)*
4. **Add one paragraph to §6 and the abstract** stating that `PRE-REGISTERED NULL` means "failed
   pre-registered support criteria", that the interval is consistent with a small effect, and that
   the development-to-holdout reversal is instability rather than demonstrated absence. *(MC6.)*
5. **Add a dependence paragraph to §6** naming batch announcements, calendar regime and
   cross-sectional contemporaneity as unmodelled, and stating the likely direction of the bias in the
   reported interval. No recomputation required to *state* it. *(MC7.)*
6. **Replace "feasible for small capital" with "passes a coarse volume-based liquidity screen"**
   throughout §7, and add one sentence listing what an execution analysis would require that this one
   lacks. *(MC8.)*
7. **Narrow §8's principle** to exact matching on a rare binary covariate, and add two sentences
   acknowledging weighting and trimming as alternatives that would weaken but not eliminate
   identification. Give the zero-price guarantee its own short paragraph. *(MC9.)*
8. **Add a short subsection on the falsifiability of the framework**, stating that it is a governance
   protocol and naming the observables on which it should be judged. *(MC11.)*
9. **Choose a unit of contribution** and restructure accordingly; move Table 3's language-level rows
   to an appendix. *(MC1, MC12.)*
10. **Narrow the "model is almost never decisive" sentences** in §1 and §12 to the reported families.
    *(MC14.)*
11. **State concretely what independent replication would require**, even if not performed. *(MC15.)*
12. **Publish the code and artefacts at a citable location** with a DOI, and compile the manuscript.
    *(Minor 12, 15.)*

Items 1 through 11 require **no new experiment**. I note that deliberately: my recommendation of
Major Revision is not contingent on the author running anything. It is contingent on the author
claiming less, citing more, and reporting the denominator.

---

*Referee #2*
