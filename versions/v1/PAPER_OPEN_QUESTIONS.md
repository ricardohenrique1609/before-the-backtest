# PAPER OPEN QUESTIONS

Quantities or decisions the manuscript needs and that are **not** computed here. The rule for this
phase is explicit: no new experiment, no new return, no rescue of a failed family, no H19.2 price
load, no H8 re-optimisation. Anything the writing exposes is recorded here and left for the user to
decide.

Each entry states what is missing, why it is not computed, and what the manuscript does instead.

---

## Q1 — The H19.2 design decision — **RESOLVED**

**Status: RESOLVED. Option E — accept `STOP`.** The research program's decision is that the H19-P3A
confirmatory design **remains blocked**. The control bars are not relaxed: tag matching is not
dropped, `MIN_CONTROLS` is not lowered, and no price is loaded.

**What this fixes.** H19-P3A carries no economic result and will not acquire one by weakening the
design that was specified before the data were seen. The family's terminal state is
`BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL`, with no pre-registration frozen, no SHA-256 computed
and no OHLC column ever read.

**What the manuscript does.** Reports that status, presents the five options and their costs as the
pre-freeze document recorded them, and states that the design remains blocked rather than that the
decision is pending. It makes no economic claim about H19-P3A.

*(Original formulation: which of the five options recorded in `H19_2_PREFREEZE_FEASIBILITY.md`
H19-P3A should take — A drop tag matching and control statistically; B lower `MIN_CONTROLS`;
C restrict to 2026; D replace the control concept; E accept STOP. B was forbidden by the frozen bar
A7; C and D were shown infeasible in the same document; A would have preserved a confirmatory design
at the cost of a real weakening of identification. The program chose E.)*

---

## Q2 — H13's economic question is unresolved, and the data to resolve it was not available

**Missing.** A survivorship-free *price* panel for US micro-caps that left the listed universe, which
would allow the net-net question to be tested rather than only the implementation.

**Why not computed.** The free sources used do not carry post-delisting prices for these issuers;
constructing one would be a new experiment, and paid sources may not be used to make a gate pass.

**What the manuscript does.** Labels H13 `ECONOMIC REJECT` of the **implementation** and states that
the economic hypothesis for net-nets remains **unresolved**. It reports the bias-bounding exercise
(+18.3% to +3.7% central and 0.0% severe) as a bound, not as the true return.

---

## Q3 — Two H13 denominators that must not be conflated

**The facts, both verified.** 52.9% (2,965 of 5,604) is the share of the *screen candidate universe*
with no current SEC ticker. 50.1% (1 − 0.49875) is the share of the *1,197-company Test A panel*
without one. They measure different populations and are both correct.

**Status.** Resolved, not open. Recorded here because the two numbers are close enough to be mistaken
for a contradiction, and the manuscript must state the denominator each time either appears.

---

## Q4 — Derivative-notice coverage is a limit, not a measurement

**Missing.** Whether the 184 of 201 events with no derivative notice found truly had none, or whether
the official surfaces reached do not carry them.

**Why not resolved.** Establishing it would require sources beyond the official keyless surfaces, and
third-party calendars may not form the sample.

**What the manuscript does.** Reports 184 `NO_DERIV_NOTICE_FOUND`, 12 after spot, 5 before spot, and
states explicitly that this is a coverage limit **never read as proof of absence**. The
announcement-ordering subgroup is declared **not estimable**, not null.

---

## Q5 — Tier-3 margin shortability is unknown for the whole universe

**Missing.** Point-in-time margin eligibility and borrow availability at T0 for the 201 events.

**Why not computed.** No official keyless surface exposes historical margin eligibility, and
inferring it from current asset support is forbidden by the same rule that forbids using current
instrument lists as history.

**What the manuscript does.** Reports the execution funnel as a **lower bound** on shortability and
labels Tier 3 `UNKNOWN` rather than zero.

---

## Q6 — H14 is open, not negative

**Missing.** A selected hypothesis for the 6,491-event B3 universe. Three sub-families (H14.1, H14.2,
H14.3) failed data gates; the parent family never selected a hypothesis.

**Why not resolved.** Selecting one would open a new family, which this phase forbids.

**What the manuscript does.** Reports H14 as `OPEN` in the registry and uses only the three
sub-family gate failures as evidence, with their measured criteria.

---

## Q7 — Three events where the venue's own stated cessation time was not the traded reality

**The facts.** OST, RCN and WPR, all announced for 2021-07-16, traded materially for three days past
the cessation instant stated in Binance's notices. Two H18.1b diagnostics therefore sit at 0.9851 and
0.9847 against a 0.99 bar.

**Missing.** Why the venue traded past its own stated end. No official explanation was found.

**Why not pursued.** It would require sources beyond the official surfaces, and the three cases do
not change any gate outcome.

**What the manuscript does.** Names the three events, reports both diagnostics below bar rather than
smoothing them, and uses the case as the clearest instance of the principle that announcement time,
cessation time and traded reality are three distinct quantities.

---

## Q8 — H18.3's calibration bar was mis-specified, and the consequence must not be overstated

**The fact.** Materiality criterion 5 penalises any calibration-slope movement of 0.10 or more,
including improvement. The challenger's calibration slope moved 0.1948 and is closer to 1 in all 8
folds, so the criterion failed on an improvement.

**Missing.** Nothing. The bar was not renegotiated after results, and the flaw is carried to the next
pre-registration rather than patched into this one.

**What the manuscript does.** Reports it as a researcher error with its methodological lesson, and
states in the same paragraph that the verdict does not depend on it: scientific-support criterion 2
(the cluster-bootstrap interval) fails independently, and so does the holdout. The manuscript must
not imply the result would otherwise have been positive.

---

## Q9 — Event accounting across the H18.3 blocks needs one explicit sentence

**The fact.** Development has 110 unique outcome events, the dropped embargo year 72, the holdout 86.
These sum to more than the 201-event universe because one announcement can be the outcome of
landmarks in more than one block. Development and holdout share **zero** events.

**Status.** Resolved from `h18_3_eligibility.json`. Recorded here so that §6 states it rather than
leaving a reader to find an apparent contradiction.

---

## Q10 — H10 control-byte issue

**Status.** Pre-existing known issue, out of scope for this paper, recorded in
`REPRODUCIBILITY_APPENDIX.md` and in `docs/DECISIONS.md`. Not fixed as part of the paper work, and
not presented as a finding.

---

## Q12 — The H15 accession split disagrees between two artefacts

**The conflict.** `H15_13D_GATE.json` records `population.initial_13d = 23,187` and
`population.amendments = 70,849`. The hypothesis ledger's H15 row records 33,196 initial filings and
60,840 amendments. Both splits sum to the same 94,036 accessions, and the gate is the
machine-readable primary artefact.

**Why not resolved here.** Determining which split is correct requires re-deriving the classification
over the 94,036-accession index, which is a new computation.

**What the manuscript does.** Reports 94,036 accessions, 502 filings read and 497 campaigns — all
three agree across artefacts — and **does not state the initial-versus-amendment split at all**. The
discrepancy is recorded here rather than resolved or silently taken from one side.

---

## Q11 — Literature access levels

**Missing.** Full text for some cited works. Where access was abstract-level only, the bibliography
and the text must say so and must not imply the full text was read.

**What the manuscript does.** Flags access level per reference in `references.bib` notes and keeps
external literature in its own evidentiary category, never blended with internal evidence or venue
documentation.
