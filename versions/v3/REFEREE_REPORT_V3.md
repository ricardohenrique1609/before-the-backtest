# REFEREE REPORT — V3

**Manuscript:** *Before the Backtest: Pre-Freeze Common-Support Ceilings for Event-Driven Strategy
Research*, V3.
**Referee:** #2 (same referee; I have read V1, V2, both prior reports, the author responses, and V3
in full).
**Date:** 2026-10-11

---

## Recommendation

# **MINOR REVISION**

In my V2 report I wrote that I would move to Minor Revision on seeing a manuscript restructured
around one contribution with the thesis narrowed to the domain the registry supports. I was asked to
honour that statement honestly rather than to find new reasons to withhold it. I have tested it, and
both conditions are met. The recommendation follows.

I want to record one thing before the detail, because it bears on how I read the rest. **The author
found the paper that most threatens this one, and cited it against themselves.** Rubin (2008) states
that observational studies must be designed without examining outcome data, and that a candidate
dataset may have to be rejected for lack of overlap between treated and control groups. That is the
principle this manuscript operationalises. Had I found it and the author had not, my report would
have been a novelty rejection. Instead §1.2 opens with it, §2.6 itemises what is inherited, and the
abstract concedes the design-stage principle in its second paragraph. That conduct is the correct
response to an inconvenient reference, and it is rarer than it should be.

---

## 1. Is there now one contribution?

**Yes.** The abstract, §1.5 and §9 state the same thing, and the architecture now serves it. The
procedure is formalised in §2.3 as a box with inputs, a computation and a decision rule; §4 is a
single demonstration of that procedure; §5 is what it prevents; §6 is three supporting results that
are explicitly subordinate; §7 is the denominator; §8 is limitations. The ten principles are four.
The three taxonomies are in appendices. The body is 7,026 words against V2's 10,786.

V2's "four co-equal contributions" problem is resolved. Structural blinding is now where it belongs
— §2.5, as the thing that makes the stop credible — rather than billed alongside the ceiling.

## 2. Is it novel enough?

**Borderline, and the manuscript is honest about why.** My assessment of what remains after Rubin,
Li, `PSweight` and Petersen et al.:

| element | status |
|---|---|
| design stage without outcome data; reject for lack of overlap | **Rubin (2008)**. Not claimed. |
| outcome-free two-stage design, codified | Li (2023). Not claimed. |
| overlap diagnostics run before outcome access | `PSweight` design module. Not claimed. |
| positivity, structural vs practical violations, remedies | Petersen et al. (2012). Not claimed. |
| **support computed on the complete point-in-time eligible population, with time-varying eligibility** | **plausibly new in this form.** This is a different quantity from a sample diagnostic, and §2.3's upper-bound argument is correct: a low realised count is ambiguous and a low ceiling is not. |
| **a pre-registered numeric stop rule rather than analyst judgement** | a genuine operational difference from Rubin's "may have to be rejected". Small, but it is the difference between a principle and a practice. |
| **structural, code-level enforcement of blinding** | a technique, not a method. §2.5 makes the right argument for why it matters more here than in a clinical setting, and that argument is the paper's own. |

The honest summary is that **one of these three is a contribution and two are refinements**, and the
manuscript presents them as a combination rather than overselling any one. §2.6's closing sentence —
that if the combination exists elsewhere the contribution reduces to the §4 demonstration — is the
correct hedge and I would keep it exactly as written.

Is a combination claim plus one demonstration enough for a methods paper? At a methods or
data-science venue, yes, provided the demonstration is clean. It is. At a top empirical finance
journal, no, and the manuscript no longer pretends to be aimed there.

## 3. Is the domain claim supported by the registry?

**Yes, and §7 is better than I asked for.** It reports the 31 entries, states that nine were rejected
on completed economic tests, says in terms that the denominator does **not** support a broad thesis,
and then narrows to a cycle-specific statement. Critically, it names the two competing explanations —
the domain changed, or the protocol tightened — and says the registry cannot separate them.

The closing move in §7 is the right one: *"the paper's claim is a claim about a procedure, not about
a prevalence."* That sentence is what makes the narrowed thesis coherent, and it should survive any
further editing.

One residual: the registry is in Appendix B, with the summary in §7. I had asked only that the
denominator remain visible, and it does. A reader who stops at §7 gets the counts and the concession;
that is sufficient.

## 4. Does the paper overclaim positivity or common support?

**No.** §1.6 defines common support as the finite-sample form of positivity and attributes it. §5's
set-off note states that weighting, overlap weights, trimming, coarsened matching and estimand
redefinition are legitimate and answer different estimands, that the objection is to reaching for
them after a counting rule has failed, and that a prospective choice of any of them with its own
feasibility audit would be a sound study. That is the correct position and it is better argued than
in V2.

§5's structural-versus-practical reading, with 134 warned assets ever and a per-date median of 7, is
appropriately hedged as an observation rather than a classification.

## 5. Is the ceiling useful beyond this venue?

**This is now my principal reservation, and the manuscript raises it before I can.** §8 states that
the binding quantity — 134 warned assets, ever — is a consequence of how aggressively one venue
applies its risk tag, that another venue would yield a different ceiling, and that an infeasibility
verdict is therefore a statement about an institution's behaviour rather than about the question.

Accepting that, two things limit the demonstration's reach and only one is acknowledged.

**Acknowledged:** one venue, one policy, one period.

**Not acknowledged, and worth a sentence:** the procedure has been demonstrated **exactly once, on a
case that returned infeasible**. There is no reported instance in which the audit returned *feasible*
and the study then proceeded. A gate is characterised by two error rates, and this manuscript
reports evidence about one of them. A reader cannot tell from §4 whether the audit would block
studies that should run. §8 lists "the rate at which gates later prove unnecessarily restrictive" as
unmeasured, which is the right observable, but §4 should say plainly that the demonstration is a
single positive detection with no reported negative controls.

**The floor-invariance result in §4.4 substantially mitigates my threshold objection**, and I want to
credit it specifically. Deriving from the reported 75th percentile of 2 that at most 15 of 62 events
can clear any floor of 3 or more — so that no defensible *m* yields 40 — is exactly the right kind of
argument: it uses only quantities already in the artefact, it is checkable in one line, and it
converts "the verdict depends on an arbitrary bar" into "the verdict is invariant over the relevant
range of that bar". The manuscript correctly notes that this says nothing about sensitivity to
*N_min* or to the matching rule.

On *N_min*: the same artefact does not permit an equivalent bound, and I accept that. But the
manuscript should state the obvious implication it currently leaves to the reader — with N\* ≤ 15
for any sensible floor, the design fails for any *N_min* above 15, so the result is likewise
insensitive to *N_min* across a wide range. That is one sentence, requires no computation, and
closes the threshold objection almost entirely.

## 6. Is structural blinding supporting evidence or a gimmick?

**Supporting evidence, and §2.5 makes the case properly.** The argument that blinding is enforced by
the calendar in settings where outcomes arrive later, and by nothing at all when the price series has
sat in the same archive since before the study was conceived, is correct and is the strongest
justification for the technique I have seen. §5's extension — that the researcher's own account is
precisely the evidence a sceptical reader should discount — is the right framing.

It remains two lines of code. The manuscript says so. That is the correct weight.

## 7. Does the full denominator remain visible?

**Yes.** §7 in the body, Appendix B in full, Figure 1 in V2 dropped but the counts retained in text.
I checked that the uncomfortable facts survived the restructure: the nine economic rejects are in
§7's table, and the archival of the single promoted family is in the same paragraph. Neither has been
softened between V2 and V3.

## 8. Are threshold arbitrariness and lack of sensitivity honestly bounded?

**Yes, and better than in V2** because of §4.4. The inventory is in Appendix C with 0 theoretical, 2
conventional and 17 engineering-judgement bars, the hierarchy of bars is stated, and the
pre-specification caveat is present. The manuscript identifies three threshold-determined conclusions
in the wider program and does not hide that one of its own bars is defective as written.

Remaining: sensitivity to the matching rule itself is unmeasured and unbounded. A coarser
stratification — say, warning state matched within a two-category liquidity split rather than a
finer band — might yield a feasible design, and the manuscript cannot say. §8 concedes that "the
exact matching rule is one design", which is honest but leaves the reader unable to judge how close
the design was to feasibility. I do not ask for this to be computed; I ask for it to be named as the
largest unmeasured sensitivity, ahead of the floor.

## 9. Is the paper clearer and shorter?

**Yes.** 7,026 body words from 10,786, four figures from six, four principles from ten, zero
taxonomies in the body. Figure 3 is a good main figure: the distribution against the floor, and the
stop rule, in one view.

Smaller points:

1. **§6.3 is doing two jobs.** It is both a supporting case (feasibility does not substitute for
   out-of-sample falsification) and the home of the base-rate discussion. The base-rate paragraph is
   good and correctly says the design does not decompose the explanations, but it slows the section
   down. Consider moving it to the appendix with the H18.3 metrics table.
2. **Figure 4's shaded band** is labelled as the recorded range 0 to 27. A reader may take the band
   as a confidence region. Hatch it or caption it as "recorded range, not an interval".
3. **The title.** "Pre-Freeze Common-Support Ceilings" is accurate but front-loads two pieces of
   jargon. I would not block on it. If a shorter alternative is wanted, the §9 sentence — *a backtest
   should begin only after the proposed comparison has been shown to exist* — is better prose than
   the title.
4. **§2.2's last line** ("the audit says nothing about it") is the right disclaimer but reads as an
   aside; it deserves to be in §8 as well, which is where a reader looks for it.
5. **Appendix A.2** (derivative notice coverage) is now orphaned: nothing in the body refers to it.
   Either cite it from §4.1 or drop it.

## 10. Scoring

| dimension | V1 | V2 | V3 |
|---|---|---|---|
| novelty | 2 | 3 | **3** — Rubin caps it; the combination and the demonstration hold |
| importance | 3 | 3 | **3** |
| identification | 2 | 2 | **3** — the object of study is now a feasibility verdict, which the design does identify |
| empirical rigor | 4 | 5 | **5** |
| statistical rigor | 3 | 3 | **4** — the floor-invariance bound |
| reproducibility | 4 | 4 | **4** — unchanged; no public repository, never compiled |
| clarity | 3 | 3 | **5** |
| generalizability | 2 | 3 | **3** — endogenous ceiling acknowledged |
| journal fit | 2 | 4 | **5** |
| honesty of reporting | — | 5 | **5** |

## Required revisions for acceptance

All are editorial. **None requires running anything.**

1. Add one sentence in §4.4 extending the floor-invariance bound to *N_min*: with N\* ≤ 15 for any
   floor of 3 or more, the design fails for any *N_min* above 15.
2. Add one sentence in §4 stating that the procedure is demonstrated once, on a case that returned
   infeasible, with no reported instance in which it returned feasible — so the evidence concerns
   detection, not specificity.
3. Name the matching rule, not the floor, as the largest unmeasured sensitivity in §8.
4. Caption Figure 4's band as a recorded range, not an interval.
5. Either cite Appendix A.2 from the body or remove it.
6. Optionally relocate the base-rate paragraph from §6.3 to the appendix.

## Not required for acceptance, but blocking for release

These are outside the manuscript and I note them because the author's own release rule turns on them:
**no independent verification of any result**, **no public repository or DOI**, and **the manuscript
has never been compiled**. A data-availability statement pointing at a live archive, and a compiled
PDF, are ordinary production requirements; the independent check is not, and the author has named the
cheapest viable one in §8 without performing it. I would not hold the paper for it. A reader should
know it has not happened, and §8 says so.

---

*Referee #2*
