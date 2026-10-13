# Before the Backtest — v1.0.0

A working paper and its complete evidence trail.

**Ricardo H. Ramos Silva** · Independent Researcher · October 2026

---

## The contribution

**A pre-freeze common-support ceiling.** Given a proposed event set, a complete point-in-time
candidate-control universe, an intended matching rule, a minimum support per event *m* and a minimum
admissible confirmatory sample *N_min*:

1. construct the candidate-control universe at each event time from information available then;
2. apply the intended matching rule exactly;
3. compute the attainable support *S_e* over the **complete** eligible pool;
4. form *N\** = Σ 1[*S_e* ≥ *m*];
5. if *N\** < *N_min*, **stop before the pre-registration is frozen and before any outcome is opened**.

The status on stopping is `DESIGN INFEASIBLE UNDER THIS SPECIFICATION` — not a null result, not a
rejected hypothesis, not evidence that the effect is absent. The hypothesis is untested.

The design-stage principle is **Rubin's (2008)** and is conceded as such: observational studies must
be designed without examining outcome data, and a candidate dataset may have to be rejected for lack
of overlap. What is claimed here is the narrower combination — complete population, point-in-time,
pre-freeze, outcome-blind, with a pre-registered numeric stop rule, in a systematic event-study
setting.

## The demonstration

62 candidate cryptocurrency delisting events, exact matching on liquidity band and public-warning
state, floor of 20 matched controls.

| quantity | value |
|---|---|
| attainable support p10 / p25 / median / p75 / p90 | 0 / 0 / **1** / 2 / 57 |
| events below the floor | **52 of 62** |
| full-pool ceiling across announcement dates | 0 to 27, median **7** |
| dates reaching the floor | **3 of 25** |
| implied confirmatory sample *N\** | **10** |
| required minimum *N_min* | **40** |
| **price columns loaded** | **none** |

The data loader requested four non-price fields, which makes the outcome-blindness of the decision
checkable from source.

## What is in this release

The manuscript (`paper.pdf`, 24 pages) and its Markdown and LaTeX sources; four figures and nine
tables; the nine derived evidence artefacts the claims cite, with a 165-row claim-evidence matrix in
which **every row resolves to a file you can open**; 22 audited scripts; the four reviewed versions
with their referee reports; and the 31-entry research registry that supplies the paper's denominator.

## What this release does not claim

- **No external peer review and no journal acceptance.** The four referee reports are this project's
  own hostile-review process, and every document that mentions them says so.
- **No institutional endorsement.** No employer or university affiliation is stated.
- **No DOI and no archival deposition.** Nothing was uploaded to Zenodo, SSRN or arXiv. A GitHub tag
  is not an archival identifier.
- **No independent replication.** One researcher, one codebase, one venue.
- **No profitability claim.** No return, carry, P&L or Sharpe ratio is computed anywhere.

## Limitations worth meeting before the paper

- **One demonstration.** The procedure is applied once, to one specification, which returned
  infeasible. Nothing here estimates its specificity or false-positive rate.
- **The matching rule is the largest unmeasured sensitivity.** The floor and *N_min* are bounded by
  an arithmetic argument on committed quantities; the matching rule is not. A coarser stratification
  could produce a different ceiling.

## Licences

MIT (code) · CC BY 4.0 (manuscript, figures, tables) · CC0 1.0 (derived evidence artefacts). The CC0
dedication applies only to project-created derived artefacts and grants no rights over the underlying
exchange, regulatory, market-data or publication sources.

## How to cite

> Ramos Silva, R. H. (2026). *Before the Backtest: Pre-Freeze Common-Support Ceilings for
> Event-Driven Strategy Research*. Working paper, v1.0.0.
