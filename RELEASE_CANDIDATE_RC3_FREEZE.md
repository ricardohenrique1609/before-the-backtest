# RELEASE CANDIDATE FREEZE — RC3

**Status: RC3 — PUBLICATION-GRADE, AWAITING RELEASE AUTHORISATION.**
Nothing has been published, submitted, uploaded, deposited or assigned a DOI.

**Date:** 2026-10-13

> **One item blocks publication: B7, author metadata.** The title page reads
> `AUTHOR_METADATA_REQUIRED` because no authoritative author identity exists and none was inferred.

> **Superseded by v1.0.0, and not amended.** B7 was closed by an explicit statement from the author;
> `RELEASE_v1.0.0_FREEZE.md` is the freeze record of the published release. This file is the RC3
> record and is kept as written.

---

## 1. Source

| | |
|---|---|
| scientific source | **V4**, `versions/v4/paper_v4.md`, SHA-256 `def1442c…`, commit `c597ba6`, referee #4 **ACCEPT** |
| scientific freeze | `SCIENTIFIC_FREEZE.md`, SHA-256 `2dc81b11…` |
| **RC2 source commit** | **`e93c024`** |
| RC2 `paper.md` | `aa4fa9afcd16d5c5d89b0157913c0229506c4a359e8194973f65c01b55a29640` |
| RC2 `paper.pdf` | `ab58cdecd8b4b52b2fac2879184b535a09cbf695f011556d70de3edeab20e45e`, 21 pages |
| V1–V4 frozen files | **16 of 16 verified byte-identical**, plus the six V4 files |

## 2. RC3 hashes

| file | SHA-256 | bytes |
|---|---|---|
| `paper.md` | `3a5bda458e707c132357d1b8c4161c25dbd1e95c03449cf60204fe0c476a9f42` | 74,628 |
| `paper.tex` | `f1bf89543c075f633c846be1e7cc9a2d1cfb89ee1e1e0df0ddf5ec44259f15a8` | 80,788 |
| **`paper.pdf`** | **`88901f2e5dcc27830d0b867b6ca319988ffbbe1237b25872f6e0870ae1057216`** | **610,184** |
| `references.bib` | `dd98e55260855990a6e105a0ed125e3ed5a169bb02ca3cdccac345d73815c11f` | 18,931 |
| `CLAIM_EVIDENCE_MATRIX.csv` | `88ea6fb0ae2f16398338aa4a5cc3170c62d821a9043f60dfe78f1bd107f9d464` | 53,289 |
| `EVIDENCE_MANIFEST.csv` | `c261c4e0acb5ac82a19099d07ba69525a71e5bcadb4429b28758ddd21b0e695e` | 2,068 |
| `REFERENCES_QA.md` | `6e4b9a6f76a5f1ad3e885a4750f41e2e69420ea2a4a8ccbfdbd7db22d09fe290` | 3,369 |
| `PUBLICATION_PROOF_QA.md` | `7c790423fc3feaa2bcae1b8dd8f0a80f964fe39d4089b150dd0a89d780c299aa` | 8,289 |
| `CHANGELOG.md` | `cc32bd64be0205c0b99920e7fea54ffd44bb2425d7018f90af4d6988dc1aef1e` | 9,078 |

`references.bib` is byte-identical to RC2: **no citation was added, removed or edited.**

## 3. Contents

| | RC2 | RC3 |
|---|---|---|
| **PDF pages** | 21 | **24** |
| body words | 7,530 | 7,514 |
| figures | 4 | 4 |
| tables | 9 | 9 |
| **references rendered in the PDF** | **0 — a pointer to the .bib** | **25** |
| claim rows | 165 | 165 |
| package files | 72 | **73** (72 payload + the manifest) |
| evidence artefacts | 9, 78,794 bytes, all `derived` | unchanged |

Three extra pages are the References section. The 16-word drop in the body is the removal of the
internal release block, offset by the neutral availability line.

## 4. RC2 → RC3 changes

**SCIENTIFIC CHANGES: 0.** Full detail in `CHANGELOG.md`; summary:

| class | count | items |
|---|---|---|
| **PRODUCTION — mathematics** | 6 | membership symbol restored; summation restored; indicator, identifiers, inequalities and bounds set as mathematics; accented author names emitted as accent commands |
| **PRODUCTION — lists** | 2 | the §2.3 procedure survives inside its quote; §2.6 renders 1, 2, 3 |
| **PRODUCTION — bibliography** | 3 | a real References section in the PDF, generated at build time from `references.bib`; `REFERENCES_QA.md` added |
| **PRODUCTION — front matter** | 4 | internal release block removed from the paper; neutral availability line; PDF metadata; cover date |
| **RELEASE METADATA** | 1 | author placeholder `AUTHOR_METADATA_REQUIRED`, blocker B7 |
| **TOOLING** | 3 | release converter rewritten; 14 regression tests; two new audit scripts |

The historical converter is **unmodified**: V1–V4 `.tex` regeneration remains byte-exact.

## 5. Author metadata state

| field | state |
|---|---|
| author | **`AUTHOR_METADATA_REQUIRED`** — no authoritative identity exists; a git commit identity is a configuration value, not an authorised byline, and was not used |
| affiliation | **absent**, not inferred. No employer affiliation may be used without explicit approval |
| ORCID | **absent**, not invented |
| correspondence | **absent**; the personal address was removed from the public candidate at RC2 |
| date | 2026-10-13 |

The same placeholder stands in `CITATION.cff` and `zenodo.json`, and the build warns whenever it is
used.

## 6. Evidence, licence and security

| | |
|---|---|
| claim rows resolving to a reachable file | **165 of 165 — 100%** (53 in the package, 112 in the repository) |
| evidence artefacts | 9, 78,794 bytes, every row `derived`, no raw corpus |
| licences | **MIT** (code) · **CC BY 4.0** (manuscript, figures, tables) · **CC0 1.0** (derived artefacts), with the statement that CC0 grants no rights over the underlying sources |
| personal email in the public candidate | **0 occurrences** |
| secrets, keys, tokens, local paths, proprietary data | **none** |

## 7. QA

```
release_audit.py        freeze 10/10 quantities, 4/4 verdicts | claims 90 tokens, 0 unsupported
                        xrefs 16 sections, 6 appendices | LaTeX balanced | BibTeX 25, 0 duplicates
                        RESULT: PASS (0 issues)
release_pdf_audit.py    9 must-not patterns at 0 | 7 must-appear present | 14 frozen patterns present
                        RESULT: PASS (0 issues)
test_release_converter  14 passed, 0 failed
paper_audit_v4.py       V1+V2+V3 files 16 | changed 0
page pixel analysis     24 pages | 0 with margin ink | 0 blank
references QA           25 entries | 0 unresolved citations | 0 duplicates | 25 access notes
```

## 8. Blockers

| id | state |
|---|---|
| **B1** cited artefacts unavailable | **CLOSED at RC2** |
| **B2** manuscript never typeset | **CLOSED at RC2** |
| **B4** personal email | **CLOSED at RC2** |
| **B5** licences undecided | **CLOSED at RC2** |
| **B7** author / public identity metadata not approved | **OPEN — BLOCKS PUBLICATION** |
| **B3** no public repository, no DOI | **OPEN, intentionally** |
| **B6** no independent replication | **OPEN, disclosed, non-blocking** |

## 9. What this freeze forbids

No change to the science without reopening review. **No publication while B7 is open.** No external
action — public repository, remote push, Zenodo deposition, DOI, SSRN, arXiv, journal submission —
without explicit approval for that specific action. No future-work item from `FUTURE_RESEARCH.md`;
alpha discovery remains **PAUSED**.

**Next action: the author resolves B7 — the name as it should appear, and separately whether to state
an affiliation, an ORCID and a correspondence address.**
