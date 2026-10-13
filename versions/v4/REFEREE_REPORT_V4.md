# REFEREE REPORT — V4

**Manuscript:** *Before the Backtest: Pre-Freeze Common-Support Ceilings for Event-Driven Strategy
Research*, V4 (acceptance revision).
**Referee:** #2 (same referee; I have read V1–V4 and all prior correspondence).
**Date:** 2026-10-12

---

## Recommendation

# **ACCEPT**

subject to one clarification at proof stage (§2 below) and to the production requirements in §9,
which are outside the manuscript.

I recommended Minor Revision on V3 and listed six changes, five mandatory. All six are made, none is
made partially, and none introduced a new claim. The manuscript is now bounded in every place I
previously pushed on, and I can find no remaining objection that would change a reader's assessment
of what the paper establishes.

I note for the record that I looked for a reason to withhold this and did not find one that survived
contact with the text. The one thing I did find is a precision issue in a derivation, not an error
in it (§2).

---

## 1. Were all six V3 requests answered?

| # | request | answered | note |
|---|---|---|---|
| 1 | extend floor invariance to *N_min* | **yes** | §4.4, with a scope note enumerating what the bound does *not* cover |
| 2 | state the evidence is detection-only | **yes** | §4.4 set-off note **and** §8; explicitly refuses the registry as a negative control |
| 3 | rank the matching rule as the largest unmeasured sensitivity | **yes** | §8, ranked above the floor and *N_min*, both now bounded |
| 4 | Figure 4 must not read as a confidence interval | **yes** | hatched unfilled band, legend and title both say "NOT a confidence interval"; caption carries all six required facts |
| 5 | resolve the orphaned Appendix A.2 | **yes** | removed; Appendix A retitled to what it actually contains |
| 6 | relocate the base-rate paragraph (optional) | **yes** | one sentence in the body, full detail in a new Appendix F |

Request 2 is the one I expected to be softened, and it was not. The sentence *"reading their outcomes
as negative controls would be an inference the design does not support"* closes the exact escape
route I was watching for — an author under pressure to show specificity would have been tempted to
point at the registry's nine economic rejections and imply that those studies passed some analogous
gate. They did not, and the manuscript says so.

## 2. Is the *N_min* extension correct?

**The arithmetic is correct. The statement of it is one clause short of precise, and that clause
should be added at proof.**

I verified it. The reported 75th percentile of attainable support is 2 over 62 candidate events.
Under the interpolating quantile convention that produced the reported p90 of 57.3 — a non-integer,
so interpolation is in use — a p75 of exactly 2.0 requires the 46th and 47th order statistics both
to be 2, hence at least 47 events have support ≤ 2 and **at most 15** exceed it. For any *m* ≥ 3,
`N* ≤ 15`; for any *N_min* > 15, `N* < N_min`. The claim holds.

**The clarification.** The bound's exact value depends on the quantile convention. Under a different
convention — a nearest-rank definition, say — the same reported p75 is consistent with at most 16
events exceeding 2 rather than 15. This does not matter for the conclusion, which needs only
`N* ≪ 40`, but the manuscript derives a specific integer and should either name the convention used
or state the bound as "at most 15 (at most 16 under a nearest-rank convention)". One clause.

I raise it because the paper's own standard is that a derived number names its basis, and this one
currently does not. It is a proof correction, not a revision.

The scope note is otherwise exactly right: it states that the bound is arithmetic on committed
quantities, that it is not a sensitivity analysis, that nothing was recomputed, and that it
establishes nothing about *N_min* ≤ 15, the matching rule, the liquidity band, matching exactness,
the covariate set, weighting, trimming or estimand redefinition. Marking it in the claim matrix with
its own status — `ARITHMETIC DERIVATION FROM COMMITTED VALUES`, distinct from `VERIFIED` — is a good
touch and I would keep it.

## 3. Is the single-demonstration limitation explicit enough?

**Yes.** It is stated immediately after the central result, repeated in Limitations, and phrased in
the two-error-rate framing that makes it legible to a methods reader: the paper reports evidence on
detection and none on specificity. The three-part construction — the audit returned feasible, the
study proceeded, the design was later shown well identified — makes it unambiguous what evidence is
missing rather than merely conceding that some is.

This is the limitation most likely to be quoted against the paper, and the paper states it better
than a critic would.

## 4. Is the matching-rule sensitivity correctly identified?

**Yes, and the ranking is the right one.** With *m* and *N_min* bounded by §4.4, the matching rule is
what remains, and §8 enumerates its four components. The closing distinction — `DESIGN INFEASIBLE
UNDER THIS SPECIFICATION` rather than a claim that the question cannot be identified — is carried in
every place the verdict appears, which I checked.

One observation, not a request: this limitation is also the paper's most promising follow-up. A
second paper that computed ceilings across a family of matching rules — coarse to exact — would turn
a single verdict into a feasibility frontier, and that is a more interesting object than either.
That is future work and correctly not attempted here.

## 5. Is Figure 4 still misleading?

**No.** The hatched unfilled band cannot be mistaken for a density or an interval, the legend says so
in words, and the title repeats it. The caption now states that 8 of 25 dates have individually
persisted values, that all 25 contribute to the median, that the range is 0–27, that the median is 7,
that 3 of 25 reach the floor, and that the 17 remaining dates are neither plotted nor interpolated.

Production note only: the legend box overlaps the top of the hatched region and the rightmost marker
at 27. Move the legend below the axis or outside the plot area.

## 6. Is the paper cleaner after the removals?

**Yes.** Removing Appendix A.2 cost nothing because nothing referred to it, and retitling Appendix A
to what it contains is an improvement. Moving the base-rate discussion keeps Supporting Case C
supporting, which was my concern: in V3 it had begun to read as a second paper.

The body grew by 368 words, which I would normally criticise in an acceptance revision. Here the
growth is entirely the two set-off notes I asked for plus the explicit ranking; it is offset by the
removals, and the total is inside the author's own stated target. No objection.

## 7. Does Rubin remain correctly credited?

**Yes, and unchanged.** §1.2 opens on it, §2.6 itemises inherited against added, the abstract
concedes the design-stage principle in its second paragraph, and the "We do **not** claim" list is
intact. The cautious formulation and its fallback both survive verbatim.

I said in my V3 report that had I found Rubin and the author had not, this would have been a novelty
rejection. I will restate the converse: the fact that the author found it, cited it against their own
claim, and narrowed the contribution accordingly is why I am comfortable accepting a paper whose
novelty I continue to describe as borderline. A borderline contribution that is accurately described
is publishable. An overstated one is not.

## 8. Has any claim widened, and is there still one contribution?

**No claim widened.** I checked the places where widening would be easiest: the abstract, §1.5, §7's
denominator discussion and §9. The registry denominator is intact with its nine economic rejections
and the archived promotion; "a claim about a procedure, not about a prevalence" survives; no banned
broad phrasing reappears.

**One contribution, stated identically in the abstract, §1.5 and §9.** The architecture is
unchanged from V3, which was its point.

## 9. Scoring and conditions

| dimension | V3 | V4 |
|---|---|---|
| novelty | 3 | **3** — unchanged and correctly described |
| importance | 3 | **3** |
| identification | 3 | **3** |
| empirical rigor | 5 | **5** |
| statistical rigor | 4 | **4** |
| reproducibility | 4 | **4** — unchanged; production items below |
| clarity | 5 | **5** |
| generalizability | 3 | **3** |
| journal fit | 5 | **5** |
| honesty of reporting | 5 | **5** |

### Required at proof

1. Name the quantile convention in §4.4, or state the bound as "at most 15 (16 under a nearest-rank
   convention)" (§2).
2. Reposition Figure 4's legend clear of the band and the top marker (§5).

### Production requirements, outside the manuscript

These do not affect my recommendation on the science, and I note that the manuscript discloses all
three:

- **the manuscript has never been compiled** — a typeset proof is required before publication;
- **no public repository and no DOI** — for a paper whose contribution includes an artefact trail,
  a citable archive is a condition of publication, not an optional extra;
- **no independent verification of any result** — this is not a condition of publication at a methods
  venue, and the author names the cheapest viable check in §8 without performing it. A reader is
  entitled to know it has not happened, and §8 says so.

### Future science, correctly deferred

The matching-rule ceiling frontier (§4), threshold sensitivity by re-running the gates, and the
independent reconstruction. None is required for this paper. All three are named in it.

---

**I have no further scientific objections.** My recommendation is Accept.

*Referee #2*
