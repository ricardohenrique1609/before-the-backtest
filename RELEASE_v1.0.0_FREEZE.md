# RELEASE FREEZE — v1.0.0

**Status: v1.0.0 built, audited, committed and tagged locally — `PUBLIC_REPO_READY_FOR_PUSH`.**

**The repository has not been created and nothing has been pushed.** No GitHub authentication exists
in this environment and none was improvised; `GITHUB_PUBLIC_RELEASE.md` states the exact minimal
step required. No DOI, no archival deposition, no preprint server, no journal submission: nothing was
uploaded to Zenodo, SSRN or arXiv.

**Date:** 2026-10-13 · **Author:** Ricardo H. Ramos Silva · Independent Researcher

---

## 1. Source

| | |
|---|---|
| scientific source | **V4**, `versions/v4/paper_v4.md`, SHA-256 `def1442c…`, commit `c597ba6`, referee #4 **ACCEPT** |
| scientific freeze | `SCIENTIFIC_FREEZE.md`, SHA-256 `2dc81b11…` |
| release candidate line | RC1 → RC2 → RC3 → **v1.0.0**, itemised in `CHANGELOG.md` |
| RC3 source commit | `7066657` |
| V1–V4 frozen files | **verified byte-identical**, before and after the release work |

## 2. Published hashes

| file | SHA-256 | bytes |
|---|---|---|
| `paper.md` | `55462ae8e48f72fd25a47307b84be02324f92f507d44732ea8bad51246782516` | 74,702 |
| `paper.tex` | `c63bb28c05df691ce4dda34f097aa359ac295c78345317f0fe9ac997223b5c22` | 80,822 |
| **`paper.pdf`** | **`85a87a474a7ecc700d46db5c6156d4458ac141ab8321b073cc7991eda2e9d41b`** | **612,592** |
| `references.bib` | `dd98e55260855990a6e105a0ed125e3ed5a169bb02ca3cdccac345d73815c11f` | 18,931 |

`references.bib` is **byte-identical to RC2**: no citation was added, removed or edited at RC3 or at
v1.0.0, and no literature search was performed.

## 3. RC3 → v1.0.0

**SCIENTIFIC CHANGES: 0.** The body of `paper.tex` is byte-identical to RC3; three front-matter lines
differ. `CHANGELOG.md` itemises all fourteen changes; the classes are:

| class | count | items |
|---|---|---|
| **RELEASE METADATA** | 5 | the authorised byline, the excluded fields, the cover date, `CITATION.cff` and `zenodo.json`, the manifest |
| **TOOLING** | 6 | one canonical metadata module; a build that fails on a bad byline; an exact byline assertion in the PDF audit; the page analysis committed as a script; the byline emitted as LaTeX; the byline in `paper.md` |
| **PUBLICATION** | 3 | the public package builder and its audit, the publication-grade README, the package prepared for push |

## 4. Author metadata — blocker B7, closed

| field | value | basis |
|---|---|---|
| author | **Ricardo H. Ramos Silva** | stated by the author |
| affiliation | **Independent Researcher** | stated by the author |
| employer / university | **none stated** | **explicitly excluded**; no institutional endorsement implied |
| ORCID | **none** | not provided, not invented |
| correspondence address | **none published** | not authorised |
| location | **not stated** | excluded |

Defined once in `scripts/release_metadata.py` and read everywhere, so the name has a single
canonical representation. The build fails if the byline acquires an employer name, an email, an
ORCID or the old placeholder; the PDF audit asserts the exact byline against the published document.

## 5. QA

```
release_audit.py          freeze 10/10 quantities, 4/4 verdicts | claims 90 tokens, 0 unsupported
                          xrefs 16 sections, 6 appendices | LaTeX balanced | BibTeX 25, 0 duplicates
                          RESULT: PASS (0 issues)
release_pdf_audit.py      11 must-not at 0 | 9 must-appear present | 14 frozen patterns present
                          RESULT: PASS (0 issues)
release_pdf_pages.py      24 pages | 0 with margin ink | 0 blank
                          RESULT: PASS (0 issues)
test_release_converter    14 passed, 0 failed
release_public_repo.py    181 files | 94 frozen files byte-identical | 0 broken links
release_public_audit.py   11 checks | 0 findings
```

Full detail in `FINAL_PUBLICATION_QA.md` and `PUBLIC_REPO_FINAL_AUDIT.md`.

## 6. Blockers

| id | state |
|---|---|
| **B1** cited artefacts unavailable | **CLOSED at RC2** |
| **B2** manuscript never typeset | **CLOSED at RC2** |
| **B4** personal email | **CLOSED at RC2** |
| **B5** licences undecided | **CLOSED at RC2** |
| **B7** author metadata not approved | **CLOSED at v1.0.0** |
| **B3a** no public repository | **OPEN — package ready, push blocked on authentication** |
| **B3b** no DOI, no archival deposition | **OPEN by decision** |
| **B6** no independent replication | **OPEN, disclosed, non-blocking** |

## 7. What this freeze forbids

No change to the science without reopening review: that means a new version, a new referee report and
a new freeze, as V1 through V4. No external action beyond the public repository and its tag — **no
DOI, no Zenodo deposition, no SSRN, no arXiv, no journal submission** — without explicit approval for
that specific action. No future-work item from `FUTURE_RESEARCH.md`; alpha discovery remains
**PAUSED**.

## 8. What is claimed, and what is not

The paper claims one procedure and one demonstration of it. It claims **no** profitability, **no**
identified economic effect, **no** external peer review, **no** institutional endorsement and **no**
independent replication. The four referee reports are this project's own hostile-review process, and
every document that mentions them says so.

A GitHub tag is not an archival identifier. A repository can be renamed, made private or deleted, so
this release will be less durable than a DOI would be even once it is pushed. That is recorded as
**B3b**, open by decision.
