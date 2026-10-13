# REFEREE REPORT — V2

**Manuscript:** *Falsification-First Alpha Discovery: How Data Construction, Survivorship, Semantic
Errors and Execution Constraints Create and Destroy Apparent Trading Opportunities*, V2.
**Referee:** #2 (same referee; I have read V1, my first report, the author response, and V2 in full).
**Date:** 2026-10-11

---

## Recommendation

# **MAJOR REVISION**

I want to be precise about why, because this is not the same Major Revision as last time.

V1 had five conditions under which I would have rejected it. **All five are resolved.** The author
did the expensive, unflattering work: the full denominator is reported and it undercuts the paper's
own story; the governance section now admits that most of the protocol is the output of the program
rather than its input; the literature positioning is rebuilt; `NULL` no longer carries the weight of
"no effect"; and the two overclaimed sentences are gone. I have rarely seen a revision concede this
much, and the concessions are backed by artefacts rather than by assurances.

The paper is now **honest and small**. My remaining objection is that it may be *too* small, and
that the author has not yet decided what the single contribution is. That is a framing problem, and
it is fixable without any new experiment — which is precisely why I am not recommending Accept
today: the paper as submitted asks the reader to assemble the contribution themselves.

---

## 1. Are MC2, MC4 and MC10 actually resolved?

**MC2 (case selection): yes, and more than I asked for.** §4.2 reports all 31 registry entries with
stage, terminal state, whether an economic quantity was computed, whether the family was
pre-registered, and a commit. §4.1 carries the required sentence. Figure 1 plots the distribution.
Most importantly, §4.4 does not merely report the denominator — it states what the denominator does
to the thesis, in the author's own words: *"Any claim that pre-model failure is the typical case is
not supported by this registry."* An author who writes that sentence about their own paper has
earned the reader's trust. See §3 below for what it costs.

**MC4 (ex post governance): yes.** §2A and §2B are what I asked for, with dated commits, and the
headline is correct. I checked three rows against the commit dates given and they are consistent.
One quibble: §2A claims seven rules were in force at the start, and the evidence column for three of
them points at the ledger and early pre-registrations generically rather than at a specific artefact.
That is weaker evidence than §2B's, which names a commit per row. Since §2A is the half that
*supports* the author, it should be held to the higher standard, not the lower one.

**MC10 (novelty): the positioning, yes; the novelty itself, see §2.** §1.1 now opens by stating what
Bailey & López de Prado, Hou/Xue/Zhang, Menkveld et al., Shumway, Shumway & Warther, Kapoor &
Narayanan and Petersen et al. already establish, and §1.3 restates the contribution as four
procedures. The bibliography is 22 entries with access levels stated per entry and no invented
metadata — I checked the Hou/Xue/Zhang entry, which flags a discrepancy between the RePEc and NBER
author lists rather than resolving it by assumption, and the Petersen entry, which records that the
page numbers came from a secondary reference list. This is better citation hygiene than most
submissions.

---

## 2. Is the novelty still too weak?

This is now the central question, and my answer is: **borderline, and it depends entirely on which
procedure the author leads with.**

Taking the four in turn, as a hostile reader:

**Procedure 1, venue-side archive asymmetry.** One venue. Two other venues failed the same probe at
4/9, 1/9 and 2/9, which the manuscript reports honestly. A 0.0 pp retrieval differential on 30 active
and 30 delisted pairs is a small sample for a structural claim, and the honest reading is "this
venue, at this time, published its archive." The author's framing — *constructible* rather than
*correctable* — is the right distinction and is genuinely useful to anyone doing event research
without a data budget. But it is a fact about an institution's current policy, and institutions
change policy. **Contribution: real, narrow, perishable.**

**Procedure 2, validated universe with a measured recall denominator.** Measuring recall against a
denominator derived from market data rather than from the document source is correct practice and I
endorse it. Is it new? I do not think the *idea* is — triangulating a document-derived sample against
an independent trace is ordinary good practice in empirical work. What is unusual is that the author
actually did it and reported the four residual false negatives by name. **Contribution: exemplary
execution of a known practice. That is worth a paragraph, not a headline.**

**Procedure 3, pre-freeze full-pool common-support ceiling.** This is the paper's best idea and I
said so last time. Positivity diagnostics in the literature are run on the analysed sample, after
the study exists; the author computes the ceiling on the complete eligible pool, before the design is
frozen and before any outcome column is opened, and uses it to decide not to run the study. I have
not seen it stated this way, and the procedure transfers immediately to any matched design in any
field. **Contribution: the one thing here I would cite.**

**Procedure 4, structural outcome blinding.** `usecols=[0, 5, 7, 8]`. As a *technique* this is two
lines of code and nobody will cite it as a method. As an *epistemic object* it is more interesting
than that: it converts a claim about researcher behaviour into a property of the artefact, which is
the same move as pre-registration hashing and is rarer than it should be. **Contribution: a good
paragraph inside procedure 3's section, not a standalone contribution.**

**My assessment:** there is one contribution here (procedure 3), one useful measurement (procedure
1), and two good practices (procedures 2 and 4). The paper presents four items at equal weight, which
makes all four look smaller. A paper built around the pre-freeze ceiling — *how to decide a matched
design is infeasible before you look at the outcome, and what it cost us to apply that rule* — with
the other three as supporting evidence, would be a clearly publishable methods contribution. The
current V2 is four quarter-contributions.

---

## 3. Does the full denominator change the paper's story?

**Yes, and the author should confront this more directly than §4.4 does.**

The registry shows 9 entries rejected on a completed economic test, 1 promoted, 1 pre-registered
null, and 1 implementation reject — against 5 data-gate failures, 2 infrastructure blocks, 1
identification block and 1 capacity screen. On the raw count, **the economic test was decisive more
often than the data layer was.**

§4.4 says this. What it does not do is work out the consequence. Two readings are available:

1. **The domain changed.** Cycles 1–4 are liquid crypto and prediction markets where data is cheap
   and the question is economic; cycles 5–10 are regulatory filings and venue archives where the data
   layer is the binding constraint. On this reading the paper's thesis is a claim about *research
   domains*, not about research in general — and the paper should say which domains.
2. **The protocol tightened.** Later families faced more gates, so more of them died at gates. On
   this reading the denominator partly measures the author's own increasing strictness.

§4.4 names both and says the data cannot separate them. That is honest, but it leaves the paper's
central claim resting on a selection the author has just shown to be unrepresentative. **The fix is
to narrow the claim explicitly to the domain**: in research on institutional event data assembled
from public documents and venue archives, the binding constraint was upstream of the model in every
case we examined. That is defensible, checkable, and still useful. The current framing invites a
reader to generalise further than §4.4 permits.

I also note, with some discomfort for the author, that **the one promoted family was archived for
falling below a later return hurdle**. The author reports this. A reader will ask what the framework
has actually promoted that survived, and the honest answer in this manuscript is: nothing yet. That
is worth one sentence in §13 rather than being left for the reader to compute.

---

## 4. Is the governance trajectory now honest?

**Yes.** §2B's table is the strongest single addition in V2, and it improves the paper beyond
answering my objection: the trajectory — each rule traceable to the failure that produced it — is
itself the most convincing evidence in the manuscript that the process does something. A protocol
that grew fourteen rules in response to fourteen named failures is more credible than a protocol
asserted at the outset.

Two residual complaints. First, §2A's evidence standard (above). Second, the paper does not ask
whether any rule in §2B was **over-fitted to the failure that produced it**. A rule written in
response to one incident, by the person who caused the incident, is a plausible candidate for
over-restriction — and §11.1 lists "rate of gates later found unnecessarily restrictive" as
`UNMEASURED`, which is exactly the right observable and is left empty. H19.2 is the obvious test
case: a 20-control floor written by the same researcher who then discovered it could not be met.

---

## 5. Is H18.3 interpreted correctly now?

**Yes.** The set-off note in §6.3 is accurate and appropriately uncomfortable: failed criteria, 8/8
development folds, an interval consistent with an effect roughly twice the point estimate, a sign
reversal, a base-rate shift from 5.822% to 11.792%, and the explicit statement that absence of effect
is not demonstrated. The abstract and §13 carry it. The verdict is unchanged, which is correct.

Remaining objections, both carried from V1 and both now disclosed rather than fixed:

- The bootstrap remains one-way on asset-era. §12 now names batch announcements, policy waves and
  cross-sectional route shocks, and states that the reported interval is **too narrow** with unknown
  magnitude. Disclosure is the right response given the author's constraints; it is not a remedy, and
  a referee at a quantitative venue will say so.
- The base-rate shift is treated as an observation. It is also a potential violation of the design's
  own stationarity assumption, and the manuscript does not say what the landmark estimand means when
  the hazard environment changes between blocks. One paragraph would fix this.

---

## 6. Is H19.0's claim now bounded?

**Yes, and this is the cleanest fix in V2.** "Feasible for small capital" is gone; the replacement
wording is used consistently in the text, the figure title and the caption; the eight missing
ingredients are listed; the count is unchanged. §7 now says plainly that the result is instrument
availability plus coarse screening and is neither an execution-feasibility nor a profitability
result.

One residual: the 1% rule is still unjustified, and §9 now classifies it as engineering judgement
driving the 63→32 reduction. That is the honest treatment. But a reader will reasonably ask why
report 32 at all, if the threshold producing it has no basis. My suggestion: report the **whole
distribution** — the manuscript already has it, with 3.17% of events at ≤0.10%, 33.3% at ≤0.50% and
50.8% at ≤1.00% — and let the reader choose the bar. That removes the arbitrary number from the
headline without losing any information, and it costs nothing.

---

## 7. Is H19.2 still overclaimed?

**No.** The general claim is gone, the bounded claim is correct, five alternatives are named as
unexecuted different designs, and the structural-versus-practical positivity distinction is used
properly rather than decoratively. §8.3 gives the no-price guarantee its own subsection.

I will add something I did not say in my first report, because V2 earns it: **the combination of
"the ceiling was computed before the design was frozen" and "no outcome column was ever read" is a
genuinely strong epistemic position**, and it is stronger than most registered reports achieve. If
the author ever does run the weighted redesign, that redesign will be a clean prospective study. Very
few abandoned analyses leave their successor in that condition. This should be the paper's closing
argument, not a subsection in the middle.

---

## 8. Do thresholds still dominate the conclusions?

**Yes — and the paper now says so, which converts a hidden weakness into a stated one.** §9
classifies 19 thresholds, finds none theoretical and only two conventional, identifies three
threshold-determined headline conclusions, and §9.1 adds a four-level hierarchy ending in the correct
statement that level-3 discipline protects sequence rather than value.

I accept the author's position that measuring sensitivity requires re-running gates and fits, and
that this is out of scope. But I want to register what that leaves: **three of the paper's conclusions
are, by the author's own classification, consequences of numbers nobody can defend.** Disclosure
makes the paper honest; it does not make those conclusions strong. Any future version that can report
even a coarse sensitivity — two or three alternative bars on the two or three binding thresholds —
would change my assessment of the paper's empirical weight substantially. This is the single highest
-value piece of future work in the plan, well above the two-way bootstrap.

---

## 9. Does the paper now have one clear contribution?

**No, and this is my principal remaining objection.**

§1.3 lists four contributions at equal weight. §2 is a governance section. §4 is a registry. §5–§8
are four empirical cases. §9 is a threshold taxonomy. §10 is a defect taxonomy. §11 is ten principles
plus a falsifiability discussion. A reader finishing this manuscript can tell you it is careful; they
will struggle to tell you, in one sentence, what it established.

My diagnosis is that V2 fixed every *claim* but did not fix the *architecture*. The revision plan's
R13 ("restructure to a methodological paper with empirical cases as evidence") is marked done because
the defects moved to an appendix and the governance shrank — but the body still carries four
co-equal contributions, a ten-item principle list, two taxonomies and a registry.

**What I would do:** lead with procedure 3, retitle around it, demote procedures 1, 2 and 4 to
evidence for the general point that feasibility is checkable in advance, compress §9 and §10 into one
section on researcher-controlled decisions, and cut the ten principles to the four that §11 marks
`GENERAL` and that the evidence actually supports. That paper would be half the length and twice as
citable.

Related, smaller problems:

1. **§11.1 undercuts the paper and should be moved or reframed.** Stating that "the framework's own
   evidence base is thinner than the empirical results it governs" is admirable and correct, but it
   sits in the middle of the paper and reads as a withdrawal. It belongs in the limitations.
2. **The ten principles are of very unequal weight.** P7 is a contribution. P10 is a definition. P2
   and P5 are restatements of each other at different granularities.
3. **Two taxonomies (§3 results, §10 defects) plus a threshold classification (§9)** is a lot of
   apparatus for one paper's worth of evidence.
4. **§13 ends on a question the paper cannot answer** ("whether that discipline improves returns").
   True, and appropriately modest, but it is a weak close. Close on procedure 3.

---

## 10. Scoring, and recommendation

| dimension | V1 | V2 | note |
|---|---|---|---|
| novelty | 2 | **3** | positioning fixed; one real contribution, correctly identified; three smaller ones oversold by equal billing |
| importance | 3 | **3** | unchanged; the cost-of-enforcement question matters, the n=1 program bounds it |
| identification | 2 | **2** | unchanged by design: a wide-interval null, a blocked design, a screen, a bias bound |
| empirical rigor | 4 | **5** | the denominator, the recall denominator and the named residuals are better than most submissions |
| statistical rigor | 3 | **3** | one-way clustering now disclosed rather than remedied; thresholds classified but unmeasured |
| reproducibility | 4 | **4** | byte-for-byte regeneration, hashes, a committed audit script; still no public repository, still never compiled |
| clarity | 3 | **3** | sentences improved, architecture did not (§9 above) |
| generalizability | 2 | **3** | principles now marked `GENERAL`/`CONDITIONAL`; the domain claim still needs narrowing (§3) |
| journal fit | 2 | **4** | the methods/data-science positioning is now coherent |
| **honesty of reporting** | — | **5** | added because it is the paper's distinguishing feature; the denominator section argues against the author's own thesis |

**Recommendation: MAJOR REVISION**, for one reason that is fixable without any new experiment —
choose and lead with a single contribution (§9) — and two that are not fixable by the author alone:
no independent verification of any result, and no public artefact. I would move to **Minor Revision**
on seeing a restructured manuscript built around the pre-freeze ceiling with the domain claim
narrowed as in §3.

### What would still make me reject

1. If a future version **re-widens** any claim that V2 narrowed. The hashes exist; I will check.
2. If the denominator is quietly dropped or moved to a supplement in a later version.
3. If "the framework" is ever presented as validated by its own outputs, which §11.1 currently and
   correctly refuses to do.

### What would move me to Accept

1. Restructure around one contribution (no new experiment).
2. Narrow the thesis to the domain the registry supports (no new experiment).
3. Report the full liquidity distribution instead of the 1%-rule endpoint (no new experiment; the
   numbers are already in the manuscript).
4. One paragraph on what the landmark estimand means under a changing base rate (no new experiment).
5. A public, citable artefact archive and a compiled manuscript (no new experiment; external action).
6. Any independent check of any result, however small (requires a second party).
7. A coarse threshold sensitivity on the two or three binding thresholds (requires new computation;
   the single most valuable item in the author's future-work bucket).

Items 1–5 are within the author's control and do not require running anything. **Under the author's
own release rule — no external release while a referee recommends Reject or Major for a reason
fixable without new experiment — this manuscript is not yet release-ready, and item 1 is the reason.**

---

*Referee #2*
