# RELEASE PROVENANCE

> **This release candidate is derived from the scientifically accepted V4. All changes after V4 are
> proof, production, formatting, metadata, or repository-hygiene changes only.**

**Release:** v1.0.0 · **Date:** 2026-10-13 · **Status:** built, audited and tagged locally;
**not pushed** — see `GITHUB_PUBLIC_RELEASE.md`

**Author:** Ricardo H. Ramos Silva · Independent Researcher

The release candidate line RC1 → RC2 → RC3 → v1.0.0 is recorded in `CHANGELOG.md`. Sections 1-6
below were written at RC1 and describe that candidate; section 7 records what changed through to
v1.0.0.

---

## 1. Scientific source

| | |
|---|---|
| accepted version | **V4** |
| canonical manuscript | `versions/v4/paper_v4.md` |
| canonical SHA-256 | `def1442cb27b048e16b5b79d3ab64f1b26f99bab9ff3a8d79bda46370009e38e` |
| source commit | **`c597ba6`** — *paper: v4 acceptance revision* |
| referee decision | `versions/v4/REFEREE_REPORT_V4.md` — **ACCEPT** |
| scientific freeze | `SCIENTIFIC_FREEZE.md`, SHA-256 `2dc81b11804423421695f9098ba9c62c7aacdb6643180a0d20defe1af36da93b` |

## 2. Frozen-version verification, performed before any release work began

All sixteen earlier frozen files were verified byte-identical by
`scripts/paper_audit_v4.py`, and the six V4 files were verified separately. **Nothing diverged.**

| version | manuscript SHA-256 | files checked | changed |
|---|---|---|---|
| V1 (commit `52a980a`) | `1853bce01e638da159733ab61fd3d4945ba51a160d3ddc156ab26fa57da95cef` | 5 | **0** |
| V2 | `b2c3ddaed36fd7371a16cf9f5b75c39272dbd38edc10a482d114c9a187bfd157` | 5 | **0** |
| V3 (commit `c219704`) | `5f5468eb80e44fba50b8fb240e526b346f536f76d4ee900b6149ad1cb28cc547` | 6 | **0** |
| V4 (commit `c597ba6`) | `def1442cb27b048e16b5b79d3ab64f1b26f99bab9ff3a8d79bda46370009e38e` | 6 | **0** |

V1 through V4 are **not edited by any release work**. The release package is a derived copy in
`release/`, with clean filenames, and writes nothing outside that directory.

## 3. What changed from V4 to RC1

Four classes only. Every item is itemised in `CHANGELOG.md` and verified in `RELEASE_QA.md`.

| class | items |
|---|---|
| **PROOF** | the quantile-convention clause in §4.4 (referee V4 item 1) |
| **PRODUCTION** | Figure 4 legend moved below the axis (referee V4 item 2); LaTeX regenerated; stale `v3`/`v4` artefact references corrected; clean release filenames |
| **RELEASE METADATA** | `CITATION.cff`, `zenodo.json`, `requirements.txt`, `RELEASE_MANIFEST.json`, this file |
| **REPOSITORY HYGIENE** | `README.md`, `BUILD.md`, `PUBLIC_REPO_AUDIT.md`, `DATA_RELEASE_POLICY.md`, `LICENSE_DECISION.md`, `RELEASE_BLOCKERS.md` |

**No scientific result, verdict, sample, empirical estimate, contribution statement, novelty claim,
denominator or interpretation changed.** The release audit asserts ten frozen quantities and four
verdict labels mechanically, and reports zero unsupported numerical claims.

## 4. The one substantive clarification, and why it is a proof change

Referee V4 verified the derivation `N* ≤ 15` and asked only that the quantile convention be named.
Inspection of the committed source — not re-execution — establishes it: the quantiles were produced
by `pandas.Series.quantile` with its default `interpolation="linear"` in
`scripts/h19_2_prefreeze.py`, rounded to one decimal place.

Under that convention the published bound of 15 is correct. The release text now names the
convention and additionally states the convention-robust bound of 16, so the conclusion
`N* ≪ N_min = 40` holds under either reading. **The scientific claim of V4 is not replaced; it is
made precise.** Nothing was recomputed and no experiment was run to establish it.

## 5. Guarantees

- **No experiment, backtest, matching, sensitivity analysis, bootstrap, model, return, P&L, price
  load, event reconstruction, independent replication or order-book analysis was run** at any point
  in the release phase.
- No historical gate artefact, verdict or pre-registration was modified.
- The release package is reproducible from committed artefacts by the commands in `BUILD.md`.
- The manuscript had **not** been typeset when this section was written: see `RELEASE_BLOCKERS.md`
  item **B2**, closed at RC2. The published v1.0.0 PDF is built with Tectonic 0.17.0.

## 6. Verification

```bash
.venv/Scripts/python -I scripts/paper_audit_v4.py   # V1-V3 integrity, then the V4 audits
.venv/Scripts/python -I scripts/release_build.py    # Figure 4 layout + paper.tex
.venv/Scripts/python -I scripts/release_audit.py    # freeze quantities, claims, cross-refs, LaTeX, BibTeX, manifest
```

## 7. RC1 → v1.0.0

| release | date | what it added | scientific changes |
|---|---|---|---|
| **RC1** | 2026-10-12 | the quantile-convention proof clause, Figure 4 layout, release metadata, repository hygiene | 0 |
| **RC2** | 2026-10-12 | the compiled PDF, the evidence bundle, the three licences, the contact-address removal | 0 |
| **RC3** | 2026-10-13 | mathematics and lists typeset correctly, a real References section, publication front matter | 0 |
| **v1.0.0** | 2026-10-13 | the authorised byline, the public package, the local tag | 0 |

### Author metadata — the authorisation record

Author metadata was the last blocker, **B7**. It was not resolved by inference: a git commit identity
is a configuration value, not a byline, and was never used. The author stated the metadata
explicitly, and the statement was recorded in exactly these terms:

| field | value |
|---|---|
| author | **Ricardo H. Ramos Silva** |
| affiliation | **Independent Researcher** |
| ORCID | **none** — not provided, not invented |
| correspondence address | **none published** |
| location | **not stated** |
| employer / university | **none** — explicitly excluded; **no institutional endorsement is implied** |

The canonical definition is `scripts/release_metadata.py`, read by the build, by the
manifest and by the audits, so the name has one representation everywhere it appears. The build
refuses to run if the byline acquires an employer name, an email address, an ORCID or the old
placeholder.

**No scientific content changed at any point in the RC1 → v1.0.0 sequence.** The frozen quantities
and verdicts are asserted mechanically against both the manuscript and the extracted text of the
compiled PDF on every build.
