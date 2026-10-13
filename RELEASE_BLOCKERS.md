# RELEASE BLOCKERS

Status at **v1.0.0**, 2026-10-13. **No blocker now prevents publication.** None of the remaining
open items is a scientific issue; the science is accepted and frozen (`SCIENTIFIC_FREEZE.md`).

| id | blocker | class | state | decision belongs to |
|---|---|---|---|---|
| **B1** | cited artefacts unavailable to a reader | repository hygiene | **CLOSED at RC2** | — |
| **B2** | manuscript never typeset | production | **CLOSED at RC2** | — |
| **B4** | personal email in tracked source files | privacy | **CLOSED at RC2** | — |
| **B5** | licences undecided | release metadata | **CLOSED at RC2** | — |
| **B7** | author / public identity metadata not approved | release metadata | **CLOSED at v1.0.0** | — |
| **B3a** | no public repository | release metadata | **CLOSED at v1.0.0** | — |
| **B3b** | no DOI and no archival deposition | release metadata | **OPEN by decision** | user |
| **B6** | no independent verification of any result | scientific, disclosed | **OPEN, non-blocking** | future work |

## B7 — Author and public identity metadata — **CLOSED at v1.0.0**

**What it was.** No authoritative author identity existed anywhere in the repository or the release
configuration. The only name available was a git commit identity, which is a configuration value and
not an authorised byline, so it was not used and the title page read `AUTHOR_METADATA_REQUIRED`.

**How it was closed.** The author stated the metadata explicitly. It is recorded once, in
`scripts/release_metadata.py`, and every file that prints or records it reads from there, so
the name has a single canonical representation and cannot drift into a variant.

| field | value | basis |
|---|---|---|
| author | **Ricardo H. Ramos Silva** | stated by the author |
| affiliation | **Independent Researcher** | stated by the author |
| employer / university | **none stated** | **explicitly excluded by the author**; no institutional endorsement is implied |
| ORCID | **none** | none was provided; none is invented |
| correspondence address | **none published** | the personal address was removed at RC2 and no public address was authorised |
| location | **not stated** | excluded by the author |

`scripts/release_build.py` fails the build if the byline acquires an employer name, an email, an
ORCID or the old placeholder; `scripts/release_pdf_audit.py` asserts the exact byline against the
extracted text of the compiled PDF and rejects all four at zero occurrences.

## B3a — No public repository — **CLOSED at v1.0.0**

The paper-only package is built by `scripts/release_public_repo.py`, audited by
`scripts/release_public_audit.py` on the exact directory that was published, and is live at
<https://github.com/ricardohenrique1609/before-the-backtest>, tagged `v1.0.0`, with `paper.pdf` attached to the release at
<https://github.com/ricardohenrique1609/before-the-backtest/releases/tag/v1.0.0>.

This blocker was held open through an earlier pass because no GitHub authentication existed in that
environment. **No credential was improvised, written to disk, pasted into source or logged** then,
and none was handled here either: the publication used an already-authenticated GitHub CLI whose
token lives in the OS keyring. `GITHUB_PUBLIC_RELEASE.md` records the outcome.

## B3b — No DOI and no archival deposition — **OPEN by decision**

**This is a decision, not an omission.** No DOI was created, no Zenodo deposition exists, and the
work has not been sent to SSRN, arXiv or a journal. `CITATION.cff` and `zenodo.json` carry prepared
metadata with no live identifier; neither is a deposition.

The consequence is stated plainly: a GitHub tag is not an archival identifier. A repository can be
renamed, made private or deleted, so the citation above is less durable than a DOI would be, and
referee #2 treated a citable archive as a condition of publication at a methods venue. Creating one
is an irreversible external action that requires explicit approval for that specific action.

---

## Closed at RC2

**B1 — cited artefacts.** The nine derived summary artefacts are copied into `evidence/` inside the
release package, recorded in `EVIDENCE_MANIFEST.csv` with original path, SHA-256, size, producing
family, commit and role, every row marked `derived`. The repository's global `data/` ignore rule was
left untouched. `CLAIM_EVIDENCE_MATRIX.csv` gained `release_path` and `availability` columns:
**all 165 claim rows resolve to a file a reader can open** — 53 in the package, 112 tracked
elsewhere. No raw corpus was copied, and the copier refuses anything that is not a small JSON file.

**B2 — the PDF.** Built with Tectonic 0.17.0, installed from the project's official GitHub release
with its archive SHA-256 verified before execution, extracted to `.tools/` with no system-wide
install. 21 pages, inspected page by page in `PDF_QA.md`. Three layout defects and two factual
statements were corrected; no scientific content changed. `BUILD.md` §4 records the engine, command,
date, page count, output hash and every layout change.

**B4 — the contact address.** The public script set reads `QIE_CONTACT_EMAIL` from the environment
and raises if it is unset; there is deliberately no placeholder fallback, because a false
identification would violate the fair-access policies the scripts respect. **Zero personal email
occurrences in the public candidate.** Historical research scripts are unchanged.

**B5 — licences.** MIT for code, CC BY 4.0 for the manuscript, figures and tables, CC0 1.0 for the
project-created derived artefacts, each with its own file stating its scope. Every licence document,
the README, the data policy and the Zenodo metadata carry the statement that the CC0 dedication
grants no rights over the underlying exchange, regulatory, market-data or publication sources.

---

## B1 — Nine cited artefacts excluded from version control — **CLOSED at RC2**

**What.** `.gitignore` contains `data/`, with the comment *"data never goes to git"*. Nine small
derived JSON artefacts under `data/alpha_sprint/` are cited by `CLAIM_EVIDENCE_MATRIX.csv` as the
evidence for a substantial share of the paper's claims. They are **not tracked**, so a stranger who
clones the repository cannot open them.

The root-level gate artefacts (`H19_0_GATE.json`, `H18_1B_GATE.json`,
`H19_2_PREFREEZE_FEASIBILITY.md`, the hypothesis ledger and 30 others) **are** tracked. Of 47
distinct artefacts cited by the matrix, 34 are tracked and these 9 are not.

| artefact | bytes | SHA-256 (first 16) |
|---|---|---|
| `data/alpha_sprint/h13_results.json` | 48,317 | `e14960c1594b26a0` |
| `data/alpha_sprint/h18_1b_discover_incomplete.json` | 509 | `a3bd0aa76ac2c299` |
| `data/alpha_sprint/h18_2_audit.json` | 7,204 | `f3916c4e048f0f0e` |
| `data/alpha_sprint/h18_2_universe.json` | 653 | `7de0d03fd5daba3c` |
| `data/alpha_sprint/h18_3_development.json` | 3,629 | `dfd187d931b08a11` |
| `data/alpha_sprint/h18_3_eligibility.json` | 11,862 | `731ae83c89981d14` |
| `data/alpha_sprint/h18_3_falsification.json` | 2,895 | `19d3db642368de5a` |
| `data/alpha_sprint/h18_3_pit_audit.json` | 2,488 | `8f07023f58cc618c` |
| `data/alpha_sprint/h19_2_prefreeze.json` | 1,237 | `99d1b0e34ef646e6` |
| **total** | **78,794** | |

**Why this is not resolved here.** The exclusion is a deliberate repository policy stated in
`.gitignore`. Overriding it is the user's decision, not a production detail.

**Recommended resolution.** Track these nine files — 79 KB in total, all derived summary statistics,
no raw market data, no credentials, no personal data. `DATA_RELEASE_POLICY.md` classifies them as
redistributable derived artefacts. One command:

```bash
git add -f data/alpha_sprint/h13_results.json data/alpha_sprint/h18_1b_discover_incomplete.json \
  data/alpha_sprint/h18_2_audit.json data/alpha_sprint/h18_2_universe.json \
  data/alpha_sprint/h18_3_development.json data/alpha_sprint/h18_3_eligibility.json \
  data/alpha_sprint/h18_3_falsification.json data/alpha_sprint/h18_3_pit_audit.json \
  data/alpha_sprint/h19_2_prefreeze.json
```

**If the policy is kept instead**, the paper's data-availability section must say that those nine
artefacts are available on request rather than in the repository, and the hashes above become the
integrity check. That is a weaker position for a paper whose contribution includes an evidence trail.

## B2 — The manuscript has never been typeset — **CLOSED at RC2**

**What.** No LaTeX distribution (`latexmk`, `pdflatex`, `xelatex`, `lualatex`, `tectonic`) and no
`pandoc` are present on the machine used. Searched: `PATH`, `C:\texlive`, `C:\Program Files\MiKTeX`,
`C:\Program Files\texlive`, `%LOCALAPPDATA%\Programs\MiKTeX`, `%LOCALAPPDATA%\Pandoc`. **None found.**

`release/paper.pdf` therefore does not exist, and `PDF_QA.md` is a stub.

**Why this is not resolved here.** Resolving it means installing system software or downloading an
executable, which is an action on the user's machine that requires their explicit approval. It was
not taken unilaterally.

**What was done instead.** `scripts/release_audit.py` statically validates `paper.tex`: balanced
environments, balanced braces, a complete document skeleton, every `\includegraphics` target present
on disk, no stray unescaped specials, and a clean BibTeX file. All checks pass. This catches
converter errors; it does not catch missing packages, overfull boxes or bad page breaks.

**Recommended resolution.** Install one toolchain, then follow `BUILD.md` §4.2 and complete the
page-by-page inspection in `PDF_QA.md`. `tectonic` is the lightest option (a single binary that
fetches only the packages the document needs); TeX Live or MiKTeX are the conventional ones. The
document needs eight standard packages, two of which (`microtype`, `csquotes`) are purely
typographic and may be dropped if unavailable.

## B3 — No public repository and no DOI *(the RC1 statement; see B3a and B3b above)*

**What.** The repository is local. No remote has been configured for publication, no Zenodo
deposition exists, and no DOI has been reserved. `CITATION.cff` and `zenodo.json` are prepared with
every identifier field set to `PENDING`.

**Why this is not resolved here.** Creating a public repository or a DOI is an irreversible external
action and is explicitly out of scope.

**Recommended resolution.** `PUBLIC_RELEASE_PLAN.md` sets out the sequence. For a paper whose
contribution includes an artefact trail, referee #2 treats a citable archive as a condition of
publication rather than an optional extra.

## B4 — Personal email address in 54 tracked files — **CLOSED at RC2 for the public candidate**

**What.** A personal email address appears in the `User-Agent` header of data-collection scripts. It
is **required** by the SEC EDGAR fair-access policy, which asks automated clients to identify
themselves with a contact address, so its presence is correct engineering. It is nonetheless personal
data that would become public with the repository.

It appears in **54 tracked files** (scripts and governance documents) and in **zero** files under
`papers/`. The manuscript and the release package contain no personal contact data.

**Recommended resolution.** Read the contact address from an environment variable with a documented
fallback, for example `QIE_CONTACT_EMAIL`, and record in the README that users running the collection
scripts must set their own. This is a mechanical change to the scripts and does not affect any
result; it is left to the user because publishing a contact address is a personal choice and the
address may be intended to remain.

## B5 — Licences undecided — **CLOSED at RC2**

See `LICENSE_DECISION.md`. Code, manuscript and data plausibly want different licences, the
repository currently declares none, and a licence should not be chosen on the user's behalf.

## B6 — No independent verification

Disclosed in the paper and in `README.md`, and **not** a release gate at a methods venue. The cheapest
viable external check is named in the paper and has not been performed. Listed here so the release
record is complete.

---

## Not blockers

| item | why not |
|---|---|
| matching-rule sensitivity unmeasured | disclosed in the paper as its largest unmeasured sensitivity; future science, listed in `FUTURE_RESEARCH.md` |
| threshold sensitivity unmeasured | same; the floor and *N_min* are bounded arithmetically, the matching rule is not |
| raw data not redistributed | deliberate; see `DATA_RELEASE_POLICY.md` |
| figure PDFs not byte-reproducible | matplotlib writes a creation timestamp; `BUILD.md` says to compare PNG hashes |


---

## Record of how B1, B2, B4 and B5 were closed

The sections above are the RC1 statements of each blocker, retained so the RC2 resolution can be
checked against the problem as it was originally described. The resolutions are summarised at the top
of this file and detailed in `RELEASE_QA_RC2.md` and `RELEASE_CANDIDATE_RC2_FREEZE.md`.

**At v1.0.0, B7 is also closed**, and the sections above are retained as the statements of each
blocker when it was first recorded, so each resolution can be checked against the problem as it was
originally described.

**B3b and B6 remain open.** B3b — a DOI or archival deposition — is open **by decision**, not by
omission. B3b — a DOI or archival deposition — requires explicit approval for an
irreversible external action and was deliberately not taken. B6 is disclosed in the paper itself and
is not a release gate at a methods venue; the cheapest viable external check is named in §8 of the
manuscript and has not been performed.
