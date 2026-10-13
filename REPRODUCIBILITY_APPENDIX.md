# REPRODUCIBILITY APPENDIX

Everything needed to re-derive the paper's numbers from the repository, and an honest statement of
what cannot be re-derived.

---

## 1. Environment

| item | value |
|---|---|
| Python | 3.12.14 |
| platform | Windows 11 (10.0.26200) |
| environment | project-local virtual environment at `.venv`, invoked as `.venv/Scripts/python -I` |
| numpy | 2.5.3 |
| pandas | 3.0.6 |
| scipy | 1.18.1 |
| matplotlib | 3.11.2 |
| pyarrow | 25.0.1 |
| requests | 2.34.2 |
| httpx | 0.28.1 |
| ruff | 0.16.8 (lint gate for every committed script) |
| statsmodels | **not installed** |
| scikit-learn | **not installed** |

The last two entries are load-bearing. The modelling in H18.3 — ridge logistic regression by L-BFGS
with an analytic gradient and a numerically stable sigmoid, average-precision PR-AUC, Brier score,
calibration slope from a univariate logistic fit on the logit of the predicted probability, a cluster
bootstrap over asset-eras, and a Breslow partial-likelihood Cox model with time-varying covariates —
is implemented directly in numpy and scipy. There is no estimator library in the environment, so the
estimators are inspectable in the committed scripts rather than delegated.

Scripts are run with `-I` (isolated mode), which ignores the user site directory and the current
directory on `sys.path`.

---

## 2. Data-source hierarchy

Sources are ranked, and a lower rank may never substitute for a higher one to make a gate pass.

1. **Primary venue or registry surfaces.** The venue's own public endpoints and archives; the
   regulator's own full-text and structured filings. These are the only sources that may establish
   that an event occurred, when it occurred, or what instruments existed.
2. **Primary documents fetched from those surfaces**, parsed by committed scripts.
3. **Internal derived datasets**, rebuilt from 1 and 2 by committed scripts.
4. **Academic literature**, used for priors, novelty assessment and mechanism, never as data.
5. **`PAID_REFERENCE`.** Paid sources may be cited for context and may never be used to make a gate
   pass or to fill a missing field.

Rules in force throughout:

- **No API keys or credentials of any kind.** Only public, keyless endpoints were used.
- **Bot protections were never circumvented.** A challenge response is recorded as `ACCESS_BLOCKED`
  and the affected page is counted against coverage. The H18.1b refusal record
  (`data/alpha_sprint/h18_1b_discover_incomplete.json`) shows exactly this: one blocked page, catalog
  coverage 0.9887, and a universe that was not written.
- **A web archive is not a primary venue source**, and third-party calendars may not form a sample or
  supply a missing cessation date or ticker mapping.
- **No hardcoded fees or venue parameters.**

---

## 3. Immutable ingestion and the two clocks

Raw documents and raw market data are written once. Derived artefacts are rebuilt by script. A
correction is a new derivation; the single exception in this program is a correction note appended
to `H18_1B_DATA_AUDIT.md` about four asset-era labels, which is marked as a correction in the
document itself rather than applied silently.

`event_time` is when the event occurred or was stated to occur. `ingest_time` is when the program
could first have observed it. Features predicting an outcome at `event_time` must be constructible
from information whose `ingest_time` precedes it. H18.1b established that event data needs a third
and fourth clock: announcement time, stated cessation time and measured cessation time differ, and
execution time differs again.

---

## 4. Hashes and the pre-registration process

| document | SHA-256 | size | frozen |
|---|---|---|---|
| `H18_3_PREREG.md` | `5a1703d8d7a17a10a453b1bee484f95ec1bdb4c3aa9cb5a03400760511360fc8` | 20,128 bytes | 2026-10-10 |
| `H18_3_PREREG_AMENDMENT_01.md` | `79e2df2253af9fa3956cf5ccad2630b8fc61dd67278acc64569f92e4f5415344` | 11,204 bytes | 2026-10-10 |
| `H18_3_PRE_HOLDOUT_FREEZE.json` | `aec92fe448bc61da76774a82e9d96083cd45d0196de614e7ac825a2e1451cf5c` | — | before the holdout was opened |

The process, in the order the commit graph shows it:

1. Write the pre-registration in full: estimand, risk set, splits, folds, features, baseline,
   challenger, metrics, decision rule, verdict vocabulary.
2. Freeze it, compute SHA-256 into a `.sha256` file beside it, and commit (`522bafb`).
3. If the design must change, write a **separate amendment** before any model is fitted and before
   the holdout is opened, freeze, hash, commit (`203390b`). The original is never overwritten.
4. Fit on development only. Freeze the development state and hash it
   (`H18_3_PRE_HOLDOUT_FREEZE.json`) before the holdout is touched.
5. Open the holdout once. Commit the execution (`4aa4180`).

**H19.2 has no entry in this table, and that is the evidence for its status.** No pre-registration
was frozen and no hash was computed; `H19_2_PREREG_DRAFT.md` is a draft and is labelled as one.

---

## 5. Seeds and determinism

| seed | where | use |
|---|---|---|
| `20261010` | `h18_3_fit.py` | cluster bootstrap, 2,000 replications over asset-era clusters |
| `20261010` | `h19_2_prefreeze.py` | candidate-control sampling, 120 candidates evaluated per date |

Penalty grid for H18.3, declared before any result: `0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300`.
Selected inside development only: 30.0 for the baseline, 300.0 for the challenger. Feature counts:
18 baseline, 23 challenger.

The H19.2 ceiling in §8 of the paper is **not** sampled: it is computed on the complete eligible
pool, which is why the conclusion does not depend on the seed.

---

## 6. Commits

| commit | content |
|---|---|
| `aca53bf` | H13 data phase, red team, pre-registration (before any aggregate return) |
| `9e73558` | H13 analysis, gate and paper summary — REJECT |
| `61f0bc8` | H14 discovery universe and data audit — nothing pre-registered |
| `7c44e67`, `58bd03f`, `eabd336` | H14.1, H14.2, H14.3 data gates — all FAIL |
| `cb722dd` | H15 13D data gate — FAIL 5/22 |
| `dcefafe` | H16.1 FDA/PDUFA data gate — FAIL 2/23 |
| `e96ba10` | H17.0 market-data / survivorship gate — FAIL 14/32 |
| `6f7dbf4` | H18.0 three-venue probe — FAIL |
| `55f68ec` | H18.0b deep re-run — PASS 14/14 |
| `2a746cc` | H18.1 spot lifecycle universe — PARTIAL PASS 11/12 |
| `27c3283` | H18.1b full-delisting universe — STRONG PASS 19/19, 84 to 201 |
| `45d575d` | H18.2 hypothesis selection — SELECT H18-P1 |
| `522bafb` | **H18.3 pre-registration FROZEN** |
| `203390b` | **H18.3 amendment 01 frozen** |
| `4aa4180` | H18.3 executed — NULL |
| `320ce41` | H19.0 execution/shortability gate — PARTIAL PASS 12/15 |
| `564baf8` | H19.1 selection — SELECT H19-P3A with three modifications |
| `42f35df` | H19.2 pre-freeze feasibility — STOP, BLOCKED BEFORE FREEZE |
| `1148352` | paper: architecture and evidence map |
| `8c816c5` | paper: the five tables, generated from artefacts by a committed script |
| `59d204a` | paper: draft falsification-first alpha discovery manuscript |
| `ba1642d` | paper: figures bibliography and reproducibility appendix |
| `f17d3e7` | paper: evidence and language audit |
| `813228d` | paper: embed the six figures in the manuscript |

Paper commits are kept separate from experiment commits throughout; no commit in this table touches
a gate, a verdict, a pre-registration or an experiment artefact. The freeze commit and its hashes are
recorded in `PAPER_V1_FREEZE.md`.

The ordering is itself evidence: `522bafb` and `203390b` precede `4aa4180`, so the specification was
committed before any fitted result existed.

---

## 7. Experiment state transitions

A family moves through these states, and the ledger records the transition with its date.

```
PROPOSED → DATA GATE → SEMANTIC GATE → SUBSTRATE GATE → HYPOTHESIS SELECTED
    → PRE-REGISTERED (frozen, hashed) → EXECUTED (development) → HOLDOUT OPENED (once)
    → VERDICT → CLOSED
```

Terminal states reachable before a verdict: `DATA-GATE FAIL`, `INFRASTRUCTURE BLOCKED`,
`IDENTIFICATION BLOCKED`, `OPEN` (universe built, no hypothesis chosen). A closed family is not
reopened: H18-P1 was closed as `NULL` and the next family was a different question.

---

## 8. Holdout handling

- The holdout block is defined in the frozen pre-registration and is not recomputed afterwards.
- Development and holdout are checked programmatically for shared outcome events; the check is
  recorded (`h18_3_eligibility.json`, field `FROZEN_event_sharing`), and the recorded value is zero.
- The holdout is opened exactly once, by a separate script (`h18_3_holdout.py`), after the
  development state has been frozen and hashed. The gate artefact carries `holdout_opened_once:
  true`.
- Event accounting across blocks: 110 development, 72 embargo (dropped) and 86 holdout outcome
  events sum to more than the 201-event universe because a single announcement can be the outcome of
  landmarks in more than one block. Development and holdout share none.

---

## 9. Deviations and known issues

**H18.3 execution deviation.** A numerical overflow in the logistic link was found during execution.
It was fixed, development was re-run, and `H18_3_EXECUTION_DEVIATION.md` records that every reported
number was unchanged to four decimal places. The specification — estimand, splits, folds, features,
metrics — was not altered.

**H18.3 calibration bar.** Materiality criterion 5 penalises any calibration-slope movement of 0.10
or more, including an improvement, and it failed on an improvement. The bar was not renegotiated. The
flaw is carried to the next pre-registration.

**Timestamp units.** For the same date, the venue's spot archive stores microseconds while its
futures archive stores milliseconds. Scripts that read both legs detect the unit per file by
magnitude (values above 1e14 are microseconds) and abort if any timestamp falls outside a plausible
date range. Without this, the spot leg lands outside any plausible range and the spot-perpetual
intersection is empty, which looks exactly like missing spot data.

**Pagination safeguards.** Archive listings continue from the last key returned, because the storage
service returns a continuation marker only when a delimiter is set. Catalog harvests compare the
number of titles retrieved against the catalog's own reported total and refuse to write the universe
below 99%, retrying and re-sweeping first. Blocked pages are recorded, never circumvented.

**No-price pre-freeze checks.** Feasibility work that must precede a freeze loads only non-price
columns. `h19_1_feasibility.py` uses `usecols=[0, 5, 8]` (open time, volume, trade count) and
`h19_2_prefreeze.py` uses `usecols=[0, 5, 7, 8]` (open time, base volume, quote volume, trade count).
The OHLC columns are never read into memory, which makes the zero-return guarantee verifiable from
the source rather than asserted in prose.

**Known issue H10.** A control-byte issue in the H10 family is pre-existing, out of scope for this
paper, and recorded in `docs/DECISIONS.md`. It was not fixed as part of the paper work and is not
presented as a finding.

---

## 10. What cannot be reproduced from this repository

Stated explicitly, because a reproducibility appendix that omits these is misleading.

- **Live venue surfaces change.** Re-running a discovery script fetches the catalog as it exists at
  the time of the run. The committed parquet and JSON artefacts are the record of what was served
  when the experiment ran.
- **Blocked pages may differ.** Bot-protection responses are not deterministic across time or
  network location, so a re-run may encounter a different set of `ACCESS_BLOCKED` pages and a
  different coverage figure.
- **The H19.2 per-date ceiling series** is recorded for 8 of 25 announcement dates in
  `H19_2_PREFREEZE_FEASIBILITY.md`; the full 25-date series was summarised to its median rather than
  persisted. Figure 6b therefore plots the 8 recorded dates and states that it does so. Regenerating
  the full series would be a new computation, which this phase forbids.
- **No price data was ever loaded for H19.2**, so there is nothing to reproduce for that hypothesis.

---

## 11. Regenerating the paper's artefacts

```bash
.venv/Scripts/python -I scripts/paper_build_tables.py
.venv/Scripts/python -I scripts/paper_build_figures.py
```

Both read only committed artefacts, write into
`papers/falsification_first_alpha_discovery/{tables,figures}`, and compute no economic quantity.
Figure source data is written to `figures/data/` with a provenance line naming the artefact and field
each value came from.
