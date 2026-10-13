# SCIENTIFIC FREEZE

**Date:** 2026-10-12
**Manuscript:** *Before the Backtest: Pre-Freeze Common-Support Ceilings for Event-Driven Strategy
Research*, **V4**
**Canonical file:** `v4/paper_v4.md`, SHA-256
`def1442cb27b048e16b5b79d3ab64f1b26f99bab9ff3a8d79bda46370009e38e`
**Referee status:** `REFEREE_REPORT_V4.md` — **ACCEPT**, subject to two proof-stage items and the
production requirements below.

> **The scientific content of this manuscript is frozen.** No further change to its science — claims,
> results, verdicts, interpretation, scope, novelty positioning or limitations — may be made without
> reopening review. Production work (§3) and future science (§4) are separate, explicitly scoped
> phases.

---

## 1. Accepted scientific content

### The contribution

> **Pre-freeze common-support ceiling.** Given a proposed event set, a complete point-in-time
> candidate-control universe, an intended matching rule, a minimum support per event *m* and a
> minimum admissible confirmatory sample *N_min*: compute the attainable support
> `S_e = |{c ∈ C(t_e) : M(e, c, t_e) = 1}|` on the **complete** eligible pool at each event time,
> form `N* = Σ 1[S_e ≥ m]`, and if `N* < N_min`, stop **before** the pre-registration is frozen and
> **before** any outcome column is opened.
>
> Status on stop: `DESIGN INFEASIBLE UNDER THIS SPECIFICATION` — not a null, not a rejection,
> hypothesis untested.

### Novelty, as accepted

The design-stage principle is **Rubin's (2008)**: observational studies must be designed without
examining outcome data, and a candidate dataset may have to be rejected for lack of overlap.
Outcome-free two-stage design is codified (Li 2023); design-stage overlap diagnostics exist as
tooling (`PSweight`); positivity and its remedies are established (Petersen et al. 2012).

The accepted claim is only the **combination**: complete population, point-in-time reconstruction,
pre-freeze timing, outcome-blind enforcement, a pre-registered numeric stop rule, in a systematic
event-study context — stated as *"we are not aware of prior work that operationalises…"*, never as
priority, with the fallback that if the combination exists elsewhere the contribution reduces to the
empirical demonstration.

### The empirical demonstration — frozen, every component

| quantity | value |
|---|---|
| candidate events | **62** |
| support floor *m* | **20** |
| attainable support p10 / p25 / median / p75 / p90 | **0 / 0 / 1 / 2 / 57** |
| events below the floor | **52 of 62** |
| full-pool ceiling, range | **0 to 27** |
| full-pool ceiling, median | **7** |
| dates reaching the floor | **3 of 25** |
| implied confirmatory sample **N\*** | **10** |
| required minimum *N_min* | **40** |
| price columns loaded | **none** |
| pre-registration frozen | **none** |
| hypothesis | **untested** |

### Bounds carried with the result

- **Floor invariance.** `N* ≤ 15` for any *m* ≥ 3, hence infeasible for any *N_min* > 15. Arithmetic
  on committed quantities; **not** a sensitivity analysis.
- **Detection, not specificity.** One demonstration, one specification, infeasible. No case is
  reported in which the audit returned feasible, the study proceeded, and the design was later shown
  well identified. The research registry does not supply that evidence and is not used as a negative
  control.
- **Largest unmeasured sensitivity: the matching rule** — exact warning-state match, liquidity-band
  definition, matching exactness, covariate set.
- **The verdict belongs to the specification, not to the research question.**

### Verdicts — frozen

| family | label |
|---|---|
| H18.3 | `PRE-REGISTERED NULL`; the pre-registered support criteria were not met; **not** evidence of no effect |
| H19.2 | `DESIGN INFEASIBLE UNDER THIS SPECIFICATION`; substantively the earlier `BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL`; no price read |
| H19.0 | capacity and liquidity screen only; **not** execution feasibility, **not** profitability |
| H13 | implementation rejected; the economics of net-nets unresolved |
| H14 | `OPEN` |

### Scope — frozen

Event-driven systematic research; event populations from public institutional documents and venue
archives; free or public historical data; matched or controlled event designs; time-varying
eligibility. The 31-entry registry, the nine economic rejections, the single archived promotion and
the retrospective case selection remain in the manuscript. **The claim is about a procedure, not a
prevalence.**

---

## 2. What may no longer change without reopening review

Any edit to: the contribution statement; the novelty positioning or the Rubin concession; any of the
twelve frozen quantities above; any verdict label or its interpretation; the scope paragraph; the
registry denominator; the floor-invariance bound; the specificity disclosure; the matching-rule
ranking; or the limitations section.

Reopening review means a new version, a new referee report, and a new freeze — the process used for
V1 through V4.

---

## 3. Unresolved production blockers

None is addressed by V4. None affects the accepted science. **All three must be resolved before any
external release.**

| # | blocker | status |
|---|---|---|
| P1 | **The manuscript has never been compiled.** No LaTeX distribution and no `pandoc` exist in this environment; `paper_v4.tex` is generated from `paper_v4.md` by a committed converter and is syntactically unverified. | **open** |
| P2 | **No public repository and no DOI.** For a paper whose contribution includes an artefact trail, the referee treats a citable archive as a condition of publication. | **open** |
| P3 | **Figure 4 legend overlaps the hatched band and the rightmost marker.** Cosmetic; proof stage. | **open** |

### Proof-stage items from `REFEREE_REPORT_V4.md`

Deliberately **not applied to V4**, so the referee report continues to describe the text it reviewed
— the rule observed through all four rounds. They are the first items of the production phase.

| # | item | nature |
|---|---|---|
| F1 | Name the quantile convention in §4.4, or state the bound as "at most 15 (16 under a nearest-rank convention)". The referee verified the arithmetic and classifies this as a precision-of-statement correction, not an error. | one clause |
| F2 | Reposition Figure 4's legend. | layout |

---

## 4. Unresolved future-work science

Out of scope for this manuscript, named within it, and **not performed**. Each would be a new study
with its own feasibility audit and pre-registration.

| # | work | why it is new science |
|---|---|---|
| S1 | **Matching-rule ceiling frontier**: compute ceilings across a family of matching rules, coarse to exact, turning one verdict into a feasibility frontier. The referee calls this the most promising follow-up. | new computation across new specifications |
| S2 | **Threshold sensitivity** by re-running the gates and fits across a grid of bars. | new computation |
| S3 | **Independent reconstruction** of the 201-event population by a second party, compared on asset identity, announcement date and time, stated trading end, and lifecycle classification, accepted at the reported recall of 0.9801. | requires a second party |
| S4 | **A weighted, trimmed or coarsened redesign** of the blocked question. Because no outcome column has ever been opened, this would be a genuinely prospective study, not a rescue. | new design; would require reading price |
| S5 | **Specificity evidence**: a case in which the audit returns feasible, the study proceeds, and the design is later shown well identified. | requires further studies run under the procedure |
| S6 | **Second-venue replication** of the archive-asymmetry measurement. | new data collection |

---

## 5. Release status

**Nothing has been submitted, uploaded, posted, or assigned a DOI.** Release preparation is a
separate, explicit phase and is not authorised by this freeze.

The alpha-discovery research programme remains **PAUSED**. This freeze closes the manuscript's
science; it does not reopen the research.

---

## 6. Version history

| version | state | canonical SHA-256 (manuscript) | referee |
|---|---|---|---|
| V1 | frozen, commit `52a980a` | `1853bce01e638da159733ab61fd3d4945ba51a160d3ddc156ab26fa57da95cef` | MAJOR REVISION |
| V2 | frozen | `b2c3ddaed36fd7371a16cf9f5b75c39272dbd38edc10a482d114c9a187bfd157` | MAJOR REVISION |
| V3 | frozen, commit `c219704` | `5f5468eb80e44fba50b8fb240e526b346f536f76d4ee900b6149ad1cb28cc547` | MINOR REVISION |
| **V4** | **frozen; science accepted** | `def1442cb27b048e16b5b79d3ab64f1b26f99bab9ff3a8d79bda46370009e38e` | **ACCEPT** |

All sixteen earlier frozen files were verified byte-identical at the V4 freeze.
