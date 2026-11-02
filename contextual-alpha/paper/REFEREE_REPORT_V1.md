# REFEREE REPORT — *Beyond Market Data: Does Point-in-Time Public Context Add Incremental Predictive Signal?*

**Manuscript version:** pre-referee draft, research commit `79647ed` (`paper.md` / `paper.pdf`, 24 pages)
**Referee:** internal hostile review, round 1
**Date of report:** 2026-11-02

Every factual statement below about the study was checked against the frozen artefacts. The file
and field are named where it matters. No model was refitted and no new outcome was computed for
this report.

---

## Recommendation

# **MAJOR REVISION**

I do not recommend rejection. The execution is unusually clean:
- the pre-registration chain is hashed;
- the verdict rule is closed and was applied mechanically;
- the PIT, target and reproducibility audits pass;
- the paper reports the null without spin.

Those are real strengths, and most published "news predicts X" papers have none of them.

But the manuscript claims more than the design can bear, in three ways:
1. **Power.** The primary comparison was close to unable to detect any plausible increment, and the
   paper never quantifies this. That is awkward for a companion to a paper whose whole argument is
   that a design should be stopped before freezing when it cannot support its question.
2. **The penalty.** The primary result is a statement about one penalty value, and the
   development-sample sign of Δ flips along the penalty path. The paper does not show this.
3. **Pre-registration story.** The amendment that created the current primary is under-reported,
   and the timing claims cannot be verified by a reader of the public package.

None of this would change the verdict, and I explain why. All of it would change how the result
should be read.

---

## Summary of the paper

The paper asks whether public context available at decision time (macro, US regulatory and crypto
systemic information) adds out-of-time predictive information to a market baseline, for the
prediction of Binance full-asset delisting announcements within 365 days. It proceeds in four
gated stages:
- **H20.0:** a data gate. C4 and C5 fail.
- **H20.1:** a representation gate. 18 of 25 features survive; no text model qualifies as
  transform-time PIT.
- **H20.2:** a frozen pre-registration with one pre-outcome amendment.
- **H20.3:** one opening of the outcome.

The primary is an L2 logistic regression at a fixed λ = 10. Development pooled out-of-fold
ΔPR-AUC is −0.0095 (two-way 95% CI [−0.0621, +0.0405], 2 of 8 folds positive). The locked 2025
block gives Δ −0.0240. The verdict is PRE-REGISTERED NULL. Tuned and flexible models show about
+0.03 in development and turn negative on the locked block.

---

## Major concerns

### MC1 — The test had almost no power for the question it asks, and the paper never says how little

Every surviving context feature is common to all assets in a week (§10, point 3). In a linear
model a week-common feature adds the same shift to every asset's score that week. The primary
comparison can therefore gain only through ranking **across weeks**: context can help only by
predicting *when* delistings cluster, not *which* asset is delisted. The paper says this only in
the Discussion, as an interpretation. It should be the first thing said about the design, because
it defines what was actually tested.

What was tested is whether US macro and regulatory context predicts time variation in the 365-day
delisting base rate. The information available for that is very small:
- the out-of-fold evaluation spans **104 weeks** (2022–2023);
- each week's label looks 52 weeks ahead, so consecutive weeks' labels overlap by 51/52, and the
  104 test weeks contain about **two non-overlapping label windows**;
- the training windows contain a handful more.

The pre-registration knew this. `H20_2_PREREG.md` lists "Low effective power for context … A null
is the likely outcome under modest effects", and `H20_2_EXPERIMENT_PLAN.md` says the same. Neither
quantifies it, and neither sets a stop rule. The paper inherits that gap.

A rough post-hoc yardstick comes from the frozen interval itself:
- the 95% CI half-width implies SE ≈ 0.026;
- the increment detectable with 80% power is then about **+0.07 PR-AUC**, roughly **30% of M0's
  0.23**.

An increment of that size from macro calendars and regulatory document counts was implausible
before any data were opened.

**Why this matters more here than usual.** The paper now presents itself (§1) as the companion of
*Before the Backtest*. That paper argues that a design must be shown to have adequate support
**before** the pre-registration is frozen, with a numeric stop rule. This paper ran gates for
**data** feasibility and **representation** feasibility, but no gate for **statistical**
feasibility. A reader who knows the companion paper will ask why H20.2 was not stopped as
`DESIGN INFEASIBLE` and the effort redirected to C4 and C5. The paper must answer this directly,
not leave it to the reader.

**Required.**
- (a) Move the week-level mechanism from the Discussion into §2 and §7, and restate the question
  accordingly.
- (b) Report the effective number of independent label windows next to the 104 weeks.
- (c) Report the post-hoc detectable increment, clearly labelled post-hoc.
- (d) Add a paragraph acknowledging that no statistical-feasibility gate was run, and what such a
  gate would have said.
- (e) Soften §1's "both fix a design and check its feasibility before any outcome is opened". As
  written it implies a feasibility check of the kind the companion paper defines, which this paper
  did not run.

### MC2 — The development sign of Δ depends on the penalty, and the paper shows only one point

The primary uses a fixed a-priori λ = 10. The A02 rationale calls it "weak shrinkage" and "an
engineering choice". The frozen exploratory artefact (`H20_3_EXPLORATORY_RESULTS.json →
logistic_selected_lambda`) records the mean fold PR-AUC of every arm at every λ:

| λ | M0 mean-fold | M2 mean-fold | Δ (M2 − M0) |
|---|---|---|---|
| 0.1 | 0.2242 | 0.2195 | −0.0047 |
| 1 | 0.2246 | 0.2199 | −0.0048 |
| 10 (primary) | 0.2283 | 0.2228 | −0.0055 |
| 100 | 0.2467 | 0.2411 | −0.0056 |
| 1000 | 0.2793 | 0.2796 | +0.0003 |

Three things follow, and the paper reports none of them.

1. **The primary baseline is far from its own attainable performance.** M0 gains about 22% in
   mean-fold PR-AUC from λ = 10 to λ = 1000. The optimum sits at the **edge of the grid** for M0,
   M2 and M2_core, so it may lie beyond it. The primary compares two models that, on this evidence,
   are badly under-regularised.
2. **At the strongest penalty the pooled and mean-fold increments disagree.** At λ = 1000:
   - the pooled out-of-fold Δ is **+0.0273** (M2 0.2799, M0 0.2526);
   - the mean-fold Δ is **+0.0003**.

   A gain that appears only when folds are pooled comes from aligning score **levels across
   quarters**, not from ranking within a fold. That is exactly the week-level base-rate channel of
   MC1. It is the most informative pattern in the data, and the paper calls it "selection
   optimism".
3. **Selection optimism is not established.** The fold-selected λ is the same (1000) for M0 and M2,
   so the selection is symmetric. The +0.027 is not obviously an artefact of M2 being tuned harder.
   It is an artefact of **pooling**, and possibly a real but tiny base-rate signal that the 2025
   block, with a different base rate (11.8% against 5.8%), did not confirm.

**Required.**
- (a) Report the Δ(λ) path above from the frozen artefact. This needs no refit.
- (b) Report pooled **and** mean-fold Δ for the primary and the exploratory rows.
- (c) Replace "consistent with selection optimism" with the pooling explanation, or show why
  pooling is not the mechanism.
- (d) State plainly that the development sign of Δ is not robust to the penalty, while the LCUV sign
  is negative at every penalty reported.

**What does not change.** The verdict. Under every specification reported, S4 (LCUV Δ > 0) fails,
so INCREMENTAL CONTEXT SIGNAL SUPPORTED is unreachable.

### MC3 — The amendment that created the primary is under-reported

§7 says Addendum 02 "fixed the primary penalty a priori". What it does not say is what the primary
was **before** the amendment. In the v1 specification (`H20_2_MODEL_SPEC.json`), the primary
selected λ from {0.1, 1, 10, 100, 1000} by mean fold PR-AUC. That rule selects λ = 1000 for both M0
and M2, which gives development Δ **+0.0273** (S1 passes) and LCUV Δ **−0.0167** (S4 fails).

The amendment was made before any outcome was opened, so this is not outcome-driven switching. But
the paper should state three things:
- the original primary rule;
- that the amendment moved the development point estimate from positive to negative territory
  (known only now);
- that the verdict under the original rule would also have been PRE-REGISTERED NULL, because S4
  fails.

Without this, a reader who finds the v1 file will suspect the worst. With it, the paper shows that
its verdict survives its own amendment, which is a strength.

**Required.** One paragraph and one row in Table 6 or Table 7: "verdict under the v1 primary rule".

### MC4 — The title and abstract claim a question the experiment did not test

Title: *Does Point-in-Time Public Context Add Incremental Predictive Signal?* What entered the
experiment was:
- 8 US macro calendar and as-of value features;
- 9 US regulatory document counts and flags;
- one count of crypto items on English-Wikipedia Current-Events pages.

There was no news text, no exchange or asset information, no non-US regulation and no text
representation. The abstract's last sentence scopes the claim correctly ("concerns that surviving
representation, not public context in general"). The title, the first line of the abstract and §2's
question do not.

**Required.** Narrow the title and the question. For example: "… Do Point-in-Time Macro and
Regulatory Calendars Add Incremental Signal …", or keep the general title as a question and put the
operational scope in the subtitle. State the scope in the abstract's first paragraph, not only in
its last sentence.

### MC5 — Pre-registration timing cannot be verified by a reader, and reproducibility is overstated

The paper's credibility rests on order: freeze, then open. In the public package:
- the frozen commits cited in "Data and code availability" (`a14c347`, `e21c264`, `9932e20`,
  `180def4`) belong to the private research repository and **do not exist** in the public one;
- the freeze files carry hashes, so a reader can verify that the files match the freezes, but not
  **when** the freezes were made;
- there is no third-party timestamp: no OSF, AsPredicted, Zenodo deposit or signed tag.

Separately, the paper says "All stages are reproducible from the Contextual Alpha project
directory". The public package's own notes (`PUBLIC_PACKAGE_NOTES.md`) say that raw data and the
H18 inputs are not included and that the scripts "do not run end to end from this directory alone".
The two statements contradict each other.

**Required.**
- (a) Rewrite the availability statement to match the package: what is verifiable (hashes, evidence
  tables, claim ledger, scripts), what is not (raw data, inherited H18 inputs, commit history), and
  how to obtain the latter.
- (b) Disclose that the freeze timing is attested by the author's own version history, not by a
  third party.
- (c) **Strongly recommended, and time-sensitive.** Deposit the H20.2 freeze files and their hashes
  with a third-party timestamp (OSF registration or a Zenodo deposit) **now**. The
  PROSPECTIVE_CONFIRMATION outcomes mature after 2027-09-28. A timestamped deposit made before then
  turns the pending confirmation into one that any reader can verify, which is the paper's strongest
  possible future evidence. Without it, the prospective block has the same verifiability problem as
  everything else.

### MC6 — The role of the AI research agent is mentioned but never disclosed

The text refers to "the AI research agent" three times (§6, §9, §11) without ever introducing it.
The research was executed, and the manuscript drafted, with an AI agent. Journals and preprint
servers now require a statement of AI use. The paper also needs one for a substantive reason: an
agent produced the semantic-audit labels that decide 8 of the 18 features.

**Required.** A short "Use of AI tools" statement covering:
- which stages the agent executed;
- what it decided;
- what the human author decided and verified;
- that every number is checked against frozen artefacts by the claim audit.

---

## Minor concerns

1. **Figure order.** Figure 6 appears in §6 before Figure 1, and Figure 1 (the research funnel)
   appears only at the end of §6. Renumber in order of appearance, or move the funnel to §1, where
   it does most work.
2. **Notation in tables.** The tables print `lambda`, `Delta` and ASCII minus signs, and drop
   trailing zeros (0.23, 0.327). The text uses λ, Δ, the true minus sign and four decimals (0.2300,
   0.3270). Make them consistent.
3. **Table 7, raw program output.** It prints Python dictionaries (`{'num_leaves': 7, …}`) and
   "1000.0". It also reports only M2's selected configuration, while M0 selected a different
   LightGBM configuration (`num_leaves` 15). Report both arms' selections in words.
4. **LightGBM baseline.** The a-priori LightGBM M0 reaches a development pooled PR-AUC of only 0.174,
   far below the logistic M0 (0.230). The +0.029 "gain" is measured against a weak baseline. Say
   so.
5. **The LCUV "informational interval"** ([−0.061, +0.001]) is never defined. The artefact shows a
   two-way asset-era × month bootstrap, 2,000 replicates, with 3.05% of replicates positive. Define
   it, and say why it is informational rather than confirmatory.
6. **S7's "era blocks"** are never defined in the text. They are {2022 folds, 2023 folds, 2025
   LCUV}. One line in §7 fixes this.
7. **Development calibration.** The calibration slope falls from 0.67 (M0) to 0.52 (M2) in
   development. S5 is evaluated on LCUV only, so this is not a criterion failure. It is, however,
   consistent with MC2 (added week-level variance under weak shrinkage) and should be reported, not
   left in a table.
8. **Base-rate shift.** The positive landmark rate doubles from 5.82% (development) to 11.79%
   (LCUV). PR-AUC levels are not comparable across the two blocks, and Figure 3 invites the
   comparison. Note it in the caption.
9. **Citation labels.**
   - "Journal of Behavioral and Experimental Finance n.d." is not a usable author-year label.
   - `bedowska2025zombie` has no year field, so a 2025 journal article (vol. 81, DOI
     `10.1016/j.najef.2025.102543`) prints as "n.d.". Add the year only after verifying it against
     the publisher record.
   - "Binance n.d." could carry the page's stated update date.
10. **References section.** It still opens with production notes ("The reference list is
    `paper/references.bib`", counts of reused entries). Move them to the build notes.
11. **Abstract, first sentence.** "A common proposal in event-driven research is …" is an uncited
    empirical claim about the literature. Cite it, or rephrase it as the paper's own premise.
12. **Typography.** Straight double quotes ("no event") appear in the PDF. Use proper quotation
    marks.

---

## What I checked and found correct

- **Headline numbers.**
  - M0/M2 development pooled PR-AUC is 0.2300 / 0.2205.
  - The development bootstrap CI and the LCUV values match `H20_3_*` artefacts.
  - The claim ledger reports 119 of 119 claims supported.
- **Verdict logic.** Table 6 matches `H20_2_VERDICT_RULES_A02.json`, and NEGATIVE INCREMENTAL RESULT
  is correctly excluded because the development upper bound is above zero.
- **Companion paragraph.**
  - 201 events (`H20_3_TARGET_AUDIT.json → events_in_table`) match *Before the Backtest* §3.
  - H18.3 is listed there as PRE-REGISTERED NULL.
- **Amendment timing.** A02 kept the v1 grid as exploratory and adopted λ = 10, which v1 had already
  listed as the "a-priori default". The A02 file states that no outcome was read.
- **Disclosure of the LCUV block's history** (context-unseen, not programme-untouched) is accurate
  and prominent.

## What would move me to Accept

All of MC1–MC6 addressed in text, with three conditions:
- the Δ(λ) path, the pooled and mean-fold split, and the v1-rule verdict are reported from existing
  artefacts, without any refit;
- the title is scoped;
- the availability statement matches the public package.

A third-party timestamp of the H20.2 freeze before 2027-09-28 is not required for acceptance. It is
the single most valuable thing the author can do for this line of work.

## What would move me to Reject

- Any change to the verdict, the frozen specification or the reported numbers made in response to
  this report.
- Replacing the primary with the fold-selected or pooled-λ = 1000 result.
- Any wording that turns the development +0.027 into evidence of a context effect.
