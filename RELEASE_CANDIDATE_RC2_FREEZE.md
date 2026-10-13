# RELEASE CANDIDATE FREEZE — RC2

**Status: RC2 — READY FOR USER RELEASE REVIEW.** Nothing has been published, submitted, uploaded,
deposited or assigned a DOI.

**Date:** 2026-10-12

---

## 1. Source

| | |
|---|---|
| scientific source | **V4**, `versions/v4/paper_v4.md`, SHA-256 `def1442c…`, commit `c597ba6`, referee #4 **ACCEPT** |
| scientific freeze | `SCIENTIFIC_FREEZE.md`, SHA-256 `2dc81b11…` |
| **RC1 source** | `paper.md` SHA-256 `c7e40a2a9fadf2dab38630446c5c69423cf9740e809b4abecee09125fb31da60`, commit **`6fec94b`** |
| V1–V4 frozen files | **16 of 16 verified byte-identical**, plus the six V4 files |

## 2. RC1 → RC2 changes

All are PROOF, PRODUCTION, RELEASE METADATA or REPOSITORY HYGIENE. **No scientific result, verdict,
sample, empirical estimate, contribution, novelty claim, denominator or interpretation changed.**

### PROOF

| # | change |
|---|---|
| 1 | **Quantile bound stated consistently.** RC1 spliced the proof note mid-sentence. The passage now distinguishes the two bounds explicitly: `N* ≤ 15` under the documented `pandas.Series.quantile(..., interpolation="linear")` convention, infeasible for every *N_min* > 15; `N* ≤ 16` under the conservative nearest-rank reading, convention-robust infeasibility for every *N_min* > 16. Every occurrence of the three forms now names its basis. **The accepted bound is not replaced.** |

### PRODUCTION

| # | change |
|---|---|
| 2 | **PDF built** — Tectonic 0.17.0, 21 pages, no package substitutions |
| 3 | registry table renders as `longtable`, breaking across pages instead of overflowing the page bottom and the right margin |
| 4 | table column widths proportional under square-root weighting, so narrow columns no longer collide |
| 5 | Markdown backslash escapes interpreted: `N\*` no longer emits a stray backslash and a runaway italic span |
| 6 | `↔` and four other characters mapped; "CEX↔DEX" renders |
| 7 | cover date corrected to 2026-10-12 |
| 8 | the sentence stating the manuscript had never been typeset corrected — this build falsified it |
| 9 | data-availability section names `release_build.py`, and states which artefacts it regenerates versus which are carried byte-identically from frozen V4 |
| 10 | manifest counts disambiguated: `package_files_total` 72, `payload_files_hashed` 71, manifest excluded from its own hash set |

All table and converter changes live in `scripts/release_md_to_tex.py`, **a separate converter**, so
regenerating the frozen V1–V4 `.tex` files stays byte-exact.

### REPOSITORY HYGIENE AND METADATA

| # | change |
|---|---|
| 11 | `evidence/` with the nine cited derived artefacts and `EVIDENCE_MANIFEST.csv` |
| 12 | `release_path` and `availability` columns on every claim row |
| 13 | `scripts/` — the 16-script paper-only public set, with contact details read from `QIE_CONTACT_EMAIL` |
| 14 | `LICENSE` (MIT), `LICENSE-manuscript` (CC BY 4.0), `LICENSE-evidence` (CC0 1.0) |
| 15 | README, `DATA_RELEASE_POLICY.md`, `CITATION.cff`, `zenodo.json` updated for licences, evidence and the contact variable |
| 16 | `PDF_QA.md` replaced the stub with a page-by-page record; `BUILD.md` §4 rewritten with the real build; `RELEASE_QA_RC2.md` added |

## 3. RC2 hashes

| file | SHA-256 | bytes |
|---|---|---|
| `paper.md` | `aa4fa9afcd16d5c5d89b0157913c0229506c4a359e8194973f65c01b55a29640` | 62,765 |
| `paper.tex` | `dadab347cb96bc963010ad30951a5e9d7ef2b646ee8cc07567a965d17d276e69` | 68,534 |
| **`paper.pdf`** | **`ab58cdecd8b4b52b2fac2879184b535a09cbf695f011556d70de3edeab20e45e`** | **577,844** |
| `CLAIM_EVIDENCE_MATRIX.csv` | `88ea6fb0ae2f16398338aa4a5cc3170c62d821a9043f60dfe78f1bd107f9d464` | 53,289 |
| `EVIDENCE_MANIFEST.csv` | `c261c4e0acb5ac82a19099d07ba69525a71e5bcadb4429b28758ddd21b0e695e` | 2,068 |
| `README.md` | `4493acfa66a79da80b394c5723456b5bbdd310ffd7bbb3c2967e2bd37edee333` | 9,524 |
| `BUILD.md` | `062030cf6bea6dbd991e8ca67f686795cfc268319ac2ce84f3a6df951f14fffa` | 6,896 |
| `PDF_QA.md` | `c22ecfbacfd4402d2b1d5baecc9d6f7f52107eed5ad2468740c424d638f39ae7` | 6,532 |

`RELEASE_MANIFEST.json` carries all 71 payload hashes. Figure PDFs and the manifest's own
`built_utc` change on every build; compare PNG hashes for content drift.

## 4. PDF

| | |
|---|---|
| engine | **Tectonic 0.17.0** |
| source | official GitHub release, `tectonic-typesetting/tectonic` |
| archive SHA-256 | `f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f`, **verified before execution** |
| install | extracted to `.tools/tectonic/`; no system-wide install, no PATH change, no other tooling |
| **pages** | **21** |
| page-by-page inspection | **complete** — `PDF_QA.md` |
| margin ink / blank pages / `??` | **0 / 0 / 0** |

## 5. Evidence manifest

| | |
|---|---|
| artefacts | **9** |
| total bytes | **78,794** |
| all rows `derived` | **yes** |
| raw corpus included | **none** |
| claim rows resolving to a reachable file | **165 of 165 (100%)** |

## 6. Security audit

| | |
|---|---|
| secrets, keys, tokens, passwords, certificates, cloud credentials | **none** |
| absolute local paths, usernames | **none** |
| proprietary employer data | **none** — the matches reviewed were a publicly listed issuer appearing in a takeover-offer dataset, which is public market information |
| **personal email in the public candidate** | **0 occurrences** |
| scripts sanitised | 2 of 16, via `QIE_CONTACT_EMAIL` with no fallback |

## 7. Licence split

| component | licence |
|---|---|
| code | **MIT** |
| manuscript, figures, tables | **CC BY 4.0** |
| derived evidence artefacts | **CC0 1.0** |

> The CC0 dedication applies only to project-created derived artefacts and does not grant rights over
> the underlying exchange, regulatory, market-data, or publication sources.

## 8. Blockers

| id | state |
|---|---|
| **B1** cited artefacts unavailable | **CLOSED** |
| **B2** manuscript never typeset | **CLOSED** |
| **B4** personal email | **CLOSED** |
| **B5** licences undecided | **CLOSED** |
| **B3** no public repository, no DOI | **OPEN, intentionally** — irreversible external action, requires explicit approval |
| **B6** no independent replication | **OPEN, disclosed, non-blocking** — named in the manuscript, not performed |

## 9. Does RC2 meet the test?

> *A stranger can read the compiled paper, inspect every cited derived artefact, reproduce the paper
> package without private information, understand the licence of every component, and verify that
> production changed no accepted scientific result.*

| requirement | state |
|---|---|
| read the actual compiled paper | **yes** — 21-page PDF, hash recorded |
| inspect every cited derived artefact | **yes** — 165 of 165 claim rows resolve to a reachable file |
| reproduce the package without private information | **yes** — pinned environment, exact commands, zero personal data in the candidate |
| understand the licence of every component | **yes** — three licences, scopes stated, third-party rights disclaimed |
| verify production changed no accepted result | **yes** — 10 frozen quantities and 4 verdicts asserted mechanically against both the Markdown and the compiled PDF; 16 frozen files verified byte-identical |

## 10. What this freeze forbids

No change to the science without reopening review. No external action — public repository, remote
push, Zenodo deposition, DOI, SSRN, arXiv, journal submission — without explicit approval for that
specific action. No future-work item from `FUTURE_RESEARCH.md`; alpha discovery remains **PAUSED**.

**Next action: the user reviews `paper.pdf` and decides on B3.**
