# RELEASE QA — RC2

Production audit of release candidate RC2. **Date:** 2026-10-12.

```
RELEASE AUDIT - production only; no experiment, no price, no V1-V4 file touched
[freeze]      quantities 10 missing 0 | verdicts 4 missing 0
[claims]      tokens 90 | unsupported 0
[xrefs]       section refs 16 | appendix refs 6 | file refs checked
[latex]       environments balanced | packages: inputenc, fontenc, lmodern, geometry, graphicx,
              longtable, microtype, csquotes, hyperref
[bibtex]      entries 25 | duplicate keys 0 | missing notes 0
[manifest]    package 72 files = 71 payload hashed + 1 manifest (excluded from its own hash set)
              | pdf_built=True
RESULT: PASS (0 issues)
```

---

## 1. Science — unchanged

Ten frozen quantities and four verdict labels asserted mechanically against `paper.md`, and
**separately against the extracted text of the compiled PDF** (`PDF_QA.md`). All present in both.

| | |
|---|---|
| frozen quantities present | **10 of 10** |
| verdict labels present | **4 of 4** |
| contribution statement, novelty positioning, Rubin concession | unchanged |
| registry denominator: 31 entries, 9 economic rejects, 1 archived promotion | unchanged |
| V1–V4 frozen files | **16 of 16 byte-identical**, plus the six V4 files |

The one textual change with any substantive content is the quantile-convention passage, which is a
**proof precision clarification** and is covered in §2.

## 2. Proof: the quantile bound is now stated consistently

RC1 inserted the proof note **mid-sentence**, leaving a passage that read "…infeasible for any
*N_min* > 16. Therefore for any floor m ≥ 3…". That was a production defect, not a scientific one,
and it is repaired.

The passage now distinguishes the two bounds explicitly, in the required form:

- under the documented `pandas.Series.quantile(..., interpolation="linear")` convention, **`N* ≤ 15`**,
  so infeasibility holds for every *N_min* > 15;
- under the conservative nearest-rank interpretation, **`N* ≤ 16`**, so the **convention-robust**
  statement is infeasibility for every *N_min* > 16.

**The scientifically accepted bound is not replaced.** Every occurrence of the three forms was
located and now names its basis: the §4.4 passage, the scope note that follows it, and the ranking
sentence in §8.

## 3. Evidence — cited artefacts are in the package

| | |
|---|---|
| derived artefacts copied to `evidence/` | **9** |
| total bytes | **78,794** |
| rows in `EVIDENCE_MANIFEST.csv` | 9, each with release path, original path, family, source commit, bytes, SHA-256 and role |
| rows marked `derived` | **9 of 9** |
| raw corpus admitted | **none** — the copier refuses any non-JSON file and anything above a size ceiling |
| **claim rows resolving to a file a reader can open** | **165 of 165 — 100%** |
| of which, inside the release package | 53 |
| of which, tracked elsewhere in the repository | 112 |

`CLAIM_EVIDENCE_MATRIX.csv` now carries `release_path` and `availability` columns, so the crosswalk is
machine-checkable rather than described. **No gap remains, and none is claimed where one exists.**

The repository's global `data/` ignore rule was **not** weakened; the artefacts live inside the
release package, which is tracked.

## 4. Privacy

| | |
|---|---|
| personal email occurrences in the public candidate (`release/`) | **0** |
| scripts requiring sanitisation | 2 of 16 |
| sanitisation method | `QIE_CONTACT_EMAIL` read from the environment, with **no fallback address** — the script raises if it is unset |
| historical research scripts | **unchanged** |

A placeholder fallback was deliberately not used: a retrieval client identifying itself with a fake
address would violate the fair-access policies these scripts exist to respect. `README.md` explains
that a re-user must supply their own contact address.

The paper-only public candidate is `release/`, containing the manuscript, its evidence, the 16-script
public set, the figures, the tables and the release documentation — **not** the 576-file research
repository.

## 5. Licences — all three explicit

| component | licence | file |
|---|---|---|
| code | **MIT** | `LICENSE` |
| manuscript, figures, tables | **CC BY 4.0** | `LICENSE-manuscript` |
| project-created derived evidence artefacts | **CC0 1.0** | `LICENSE-evidence` |

Each file states its own scope and names what it does not cover. The required statement appears in
`LICENSE-evidence`, `README.md`, `DATA_RELEASE_POLICY.md` and `zenodo.json`:

> The CC0 dedication applies only to project-created derived artefacts and does not grant rights over
> the underlying exchange, regulatory, market-data, or publication sources.

`CITATION.cff` and `zenodo.json` carry the licence split. **No ownership is claimed over any
third-party raw data, and no DOI exists.**

## 6. PDF

| | |
|---|---|
| compiled | **yes** |
| engine | Tectonic 0.17.0, official release, archive SHA-256 verified before execution |
| pages | **21** |
| SHA-256 | `ab58cdecd8b4b52b2fac2879184b535a09cbf695f011556d70de3edeab20e45e` |
| page-by-page inspection | **complete** — `PDF_QA.md` |
| pages with ink in a margin band | **0 of 21** |
| blank pages | **0** |
| `??` unresolved references | **0** |
| package substitutions | **none** |

Three layout defects found by the first build were fixed, all confined to the release converter:
the registry table overflowing the page and the margin, column collisions in narrow columns, and a
Markdown escape that produced "N\\ = 10" with a runaway italic span. Two factual corrections were
made to the text: the cover date, and a sentence stating the manuscript had never been typeset.

## 7. Cross-references

| | |
|---|---|
| section references resolving to a heading | **16 of 16** |
| appendix references resolving to a heading | **6 of 6** |
| references to the removed Appendix A.2 | **0** |
| file references existing on disk | **all** |
| stale current-version references | **0** — the data-availability section now names `release_build.py` and states which artefacts it regenerates and which are carried byte-identically from V4 |

## 8. Claims

**Unsupported numerical claims: 0**, over 90 distinct numeric tokens.
`CLAIM_EVIDENCE_MATRIX.csv`: 165 rows, with `release_path` and `availability` on every one.

## 9. Manifest counts — contradiction resolved

RC1 reported 34 files in the freeze record and 33 in the audit. **Cause: the audit hashed the payload
and the freeze record counted the payload plus `RELEASE_MANIFEST.json` itself.** A file cannot
contain its own hash.

The manifest now states this explicitly in a `counts` object:

| field | value |
|---|---|
| `package_files_total` | **72** |
| `payload_files_hashed` | **71** |
| `manifest_excluded_from_its_own_hash_set` | `["RELEASE_MANIFEST.json"]` |

No contradictory count remains in any document.

## 10. Experiments

**Zero.** The programs run were the release build, evidence copy, crosswalk and audit scripts, plus
Tectonic. No experiment, backtest, matching, sensitivity analysis, bootstrap, model, return, P&L,
price load, event reconstruction, independent replication or order-book analysis. No gate, verdict,
pre-registration or historical artefact altered.

A PDF **renderer** (`pypdfium2`) was used for the visual QA in §6. It ran in an ephemeral environment
and was **not** added to the project's dependencies; it is not required to build the paper.

## 11. Blockers

| id | state |
|---|---|
| **B1** cited artefacts unavailable | **CLOSED** — 9 derived artefacts in `evidence/`, 100% claim coverage |
| **B2** manuscript never typeset | **CLOSED** — 21-page PDF, inspected page by page |
| **B4** personal email | **CLOSED** — 0 occurrences in the public candidate |
| **B5** licences undecided | **CLOSED** — MIT / CC BY 4.0 / CC0 1.0, boundaries explicit |
| **B3** no public repository, no DOI | **OPEN, intentionally** — requires explicit approval |
| **B6** no independent replication | **OPEN, disclosed, non-blocking** |
