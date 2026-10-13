# PAPER POSITIONING

Where this paper fits, who would review it, and how it should first be released. **Nothing is
submitted.** No claim is made about acceptance probability at any venue — that is not estimable and
anyone who offers a number for it is guessing.

This document assumes the V2 revisions in `PAPER_REVISION_PLAN_V2.md`, particularly the restated
contribution (R3) and the rebuilt novelty positioning (R2). V1 as frozen does not have a clear
audience, which is the referee's MC12 and the reason this document exists.

---

## 1. Candidate audiences, assessed

| audience | fit | what they would want | what they would reject |
|---|---|---|---|
| **Empirical finance** (JF, RFS, JFE, JFQA, RF) | **poor** | an identified economic effect, a new factor, or a replication with consequences for an established result | no identified effect; the empirical content is a venue-specific event universe and a bias-bounding exercise; the methodology is the point and they do not publish methodology-first papers of this kind |
| **Financial data science / computational finance** (*Journal of Financial Data Science*, *Quantitative Finance*, *Journal of Computational Finance*) | **good** | reusable methodology, honest negative results, implementable procedures | would want the defect catalogue compressed and the procedures stated as procedures, which R13 does |
| **Quantitative finance methodology / practitioner-academic** (*Journal of Portfolio Management*, *Journal of Investment Strategies*, *Journal of Financial Econometrics* for the inference parts) | **good for JPM-style; moderate elsewhere** | the backtest-overfitting lineage lives here (Bailey & López de Prado published the deflated Sharpe in JPM); an audience that already accepts "most backtests are artefacts" and wants the next step | JPM would want shorter and less apparatus; a econometrics venue would want the inference strengthened, which is deferred work F2 |
| **Reproducibility / meta-research** (*Patterns*, *Nature Human Behaviour* registered-report track, *PLOS ONE*, *Scientific Data*) | **moderate to good** | exactly this kind of process documentation; Kapoor & Narayanan's leakage work was published in *Patterns* | would want the finance-specific microstructure cut down and the generalisable procedure foregrounded; would ask for the independent replication (F4) |
| **ML for finance** (ICAIF, *Journal of Financial Data Science* ML track, NeurIPS workshops) | **moderate** | the leakage and common-support material; ICAIF in particular accepts negative and methodological results | would find the filings and venue-archive material slow; would want the H18.3 inference strengthened |

---

## 2. Recommended positioning

**Primary: financial data science / quantitative research methodology, with the contribution stated
as four reusable procedures and two measurements.**

The paper should be positioned as answering: *what must be falsified about a dataset and an execution
path before a trading hypothesis is testable, and what do those checks cost in sample size?* That is
a methodology question with empirical answers, which is the shape the evidence actually has.

The four procedures to foreground, in order of how defensible they are after the referee's novelty
attack:

1. **Compute the common-support ceiling on the full eligible pool before freezing a matched design.**
   Positivity diagnostics in the causal-inference literature are predominantly post hoc, run on the
   analysed sample. Doing it pre-freeze, on the complete pool, converts an unidentifiable study from
   a failed estimation into a design decision made before any outcome is visible. This is the
   paper's best idea.
2. **Structural blinding by column selection.** A guarantee that no outcome could have been observed,
   because the loader physically could not read the outcome columns, is stronger than a declaration
   of blinding and is checkable from the source. Transferable to any study with a pre-registration
   phase.
3. **Classification-level leakage auditing**: re-derive every categorical label under a strictly
   backward-looking window and report the change rate. Here, 28.7% of labels changed class while
   every value and every date in the record was correct. Stated as a procedure plus a rate, not as a
   new leakage category (R4).
4. **Coverage measured against the source's own reported total**, with a guard that refuses to write
   a universe below a stated fraction. Cheap, and it caught a truncation that would have deleted four
   years of events.

The two measurements to foreground:

1. **Venue-side archive asymmetry.** The delisting-bias literature documents the problem inside
   vendor databases and supplies corrections. This measures the other side: the venue retains what
   the aggregator drops, at a 0.0 pp retrieval differential, which makes a survivorship-free risk set
   *constructible* rather than merely *correctable* — and does so without paid data.
2. **A validated event universe with a measured recall denominator.** 201 events, recall 0.9801
   against candle-measured cessation, with all 60 unexplained non-announcements individually
   classified. The validation method transfers to any event study built from an institution's own
   notices.

---

## 3. What reviewers at the recommended venues will ask

Anticipated, so the V2 revision can pre-empt them:

1. **"What is new relative to Menkveld et al., Kapoor & Narayanan, Shumway, and the
   backtest-overfitting literature?"** — R2 and R3 exist for this question and it will be the first
   one asked.
2. **"Show me the denominator."** — R25 and R26. Any meta-research reviewer will ask immediately how
   many hypotheses there were in total.
3. **"Was the protocol in place from the start?"** — R1. A reproducibility audience is unusually
   well equipped to spot an ex post protocol presented as ex ante, because that is their subject.
4. **"Is the H18.3 null underpowered?"** — R5 and R6. An econometrics-literate reviewer will go
   straight to the interval width and the clustering.
5. **"Why these thresholds?"** — R27.
6. **"Where is the code?"** — a public archive with a DOI is a hard requirement at reproducibility
   venues and increasingly at data-science venues.
7. **"Has anyone independent checked any of this?"** — F4. The honest answer is no, and naming the
   cheapest viable check (R11) is the best available response.

---

## 4. First release

**Recommended: working-paper preprint first, journal afterwards.** Specifically:

1. **SSRN** as the primary preprint venue. It is where the finance audience for this material reads,
   it is where the backtest-overfitting and replication literature circulated before journal
   publication, and it carries a citable identifier. Post V2, not V1.
2. **arXiv (`q-fin.ST` or `q-fin.CP`, cross-listed `stat.ME`)** as a secondary posting if the
   methodological framing of R3 holds up. arXiv reaches the ML-for-finance and meta-research readers
   that SSRN does not.
3. **A public code and artefact archive with a DOI** — Zenodo linked to a public repository — posted
   **at the same time** as the preprint, not after. For this paper the artefact trail is a substantial
   part of the contribution, and a reproducibility claim that resolves to a local Windows path is not
   a reproducibility claim.
4. **Journal submission after the preprint has been up long enough to attract correction.** The whole
   argument of the paper is that a single researcher's self-audit is insufficient; inviting public
   correction before submission is the consistent move, and it is also the cheapest route to the
   independent check that F4 describes.

**Not recommended: journal-first.** Two reasons. The novelty positioning (R2) is the weakest part of
the paper and is exactly the sort of thing a preprint reader will improve for free by pointing at a
reference the author missed. And a desk rejection on fit — likely at an empirical finance journal,
given MC12 — costs months and produces no feedback.

**Sequencing.** Do not release anything, in any venue, until the seven MUST FIX items in
`PAPER_REVISION_PLAN_V2.md` are done. Items 1, 3 and 4 of that list are the ones a reader would raise
publicly and permanently.

---

## 5. Framing to avoid

- **Do not frame it as "quant research is broken."** The paper documents seventeen families in one
  program on free data. The claim the evidence supports is about what must be checked, not about the
  state of a field.
- **Do not lead with the defect catalogue.** It invites the "bug diary" reading (MC1) and that
  reading is fatal at every venue listed above.
- **Do not present the governance protocol as the contribution.** It is a synthesis of existing
  recommendations — pre-registration, frozen splits, single-use holdouts, leakage audits — and
  reviewers in the reproducibility community will recognise each component. The contribution is what
  the protocol *found*, and the three or four procedures that are not already in the literature.
- **Do not describe H18.3 as a near miss**, and do not describe H19.0 or H19.2 as results about
  profitability. The taxonomy exists to prevent exactly these readings; the paper should not
  undermine it in its own positioning.
