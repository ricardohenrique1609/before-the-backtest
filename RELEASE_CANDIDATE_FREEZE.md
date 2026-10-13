# RELEASE CANDIDATE FREEZE — RC1

**Status: RC1, frozen. NOT RELEASED.** Nothing has been published, submitted, uploaded, deposited or
assigned a DOI.

**Date:** 2026-10-12

---

## 1. Scientific source

| | |
|---|---|
| accepted version | **V4** |
| canonical manuscript | `versions/v4/paper_v4.md` |
| SHA-256 | `def1442cb27b048e16b5b79d3ab64f1b26f99bab9ff3a8d79bda46370009e38e` |
| source commit | **`c597ba6`** |
| referee decision | **ACCEPT** (`versions/v4/REFEREE_REPORT_V4.md`) |
| scientific freeze | `SCIENTIFIC_FREEZE.md`, SHA-256 `2dc81b11804423421695f9098ba9c62c7aacdb6643180a0d20defe1af36da93b` |

All sixteen V1–V3 frozen files plus the six V4 files were verified byte-identical before and after
the release work. **Nothing diverged.**

## 2. Changes from V4, by class

| class | items |
|---|---|
| **PROOF** | 1 — the quantile convention named in §4.4, with the convention-robust bound stated alongside |
| **PRODUCTION** | 5 — Figure 4 legend below the axis; seven stale artefact references corrected; clean release filenames; provenance header; LaTeX regenerated |
| **RELEASE METADATA** | 5 — `CITATION.cff`, `zenodo.json`, `requirements.txt`, `RELEASE_MANIFEST.json`, `RELEASE_PROVENANCE.md` |
| **REPOSITORY HYGIENE** | 9 — `README.md`, `BUILD.md`, `CHANGELOG.md`, `PUBLIC_REPO_AUDIT.md`, `DATA_RELEASE_POLICY.md`, `LICENSE_DECISION.md`, `RELEASE_BLOCKERS.md`, `PDF_QA.md`, `PUBLIC_RELEASE_PLAN.md`, plus `FUTURE_RESEARCH.md` and two build/audit scripts |

**No scientific result, verdict, sample, empirical estimate, contribution statement, novelty claim,
denominator or interpretation changed.** Ten frozen quantities and four verdict labels are asserted
mechanically and all pass.

## 3. Release hashes

| file | SHA-256 | bytes |
|---|---|---|
| `paper.md` | `c7e40a2a9fadf2dab38630446c5c69423cf9740e809b4abecee09125fb31da60` | 61,845 |
| `paper.tex` | `06d64de5f7f1935184f79a54b427efd58d5427d7c9834bc340612900850af9ba` | 67,165 |
| `paper.pdf` | **does not exist** — blocker B2 | — |
| `references.bib` | `dd98e55260855990a6e105a0ed125e3ed5a169bb02ca3cdccac345d73815c11f` | 18,931 |
| `CLAIM_EVIDENCE_MATRIX.csv` | `8e05e3a7cbcba7328afc78887533586853c0b96ed4f6c906a1ce45c272b7f281` | 46,594 |
| `README.md` | `cad6ffe324c56f596c911883a073f76a0cc998aad09c1d0e2846c023bc14bab7` | 6,701 |
| `BUILD.md` | `5154ce3e9e47b4c036e26e84fd2f67954d16b6f03aaa467718bb210f5d37485e` | 6,068 |
| `CHANGELOG.md` | `4653e4b81228e6bae97d2c9690ee6b59a0c34ea7c6c780af8908447b4dd6b5d1` | 5,238 |
| `RELEASE_PROVENANCE.md` | `0f4adaed874062f5d9908d18853b944a5de22807fae3f0eacfdcaa1ef8fa1f12` | 4,198 |
| `RELEASE_QA.md` | `4cd7180a0b9029c817ad3fdf92082043fda2d9462e5bc006b51100e2b23ceef9` | 6,535 |
| `RELEASE_BLOCKERS.md` | `6dca62778dd27c14bb05533369e551887d1c54ac9c657dac77cfeee31a07d20e` | 7,581 |
| `PUBLIC_REPO_AUDIT.md` | `ef49643de0d2608d7bc6d08b5a684ad56c4409c83e335dcb2485307a63323ab1` | 5,361 |
| `DATA_RELEASE_POLICY.md` | `48e3c72b129d5e10a7f3935bda367c78cc8beb600fcf2341f8a96282b6bbc0d8` | 5,617 |

Figure PNGs (first 24 hex): `f1_procedure` `435a14ad45628a1f50bcf90e` · `f2_event_funnel`
`dc46eefe63eb86e2bee79c7f` · `f3_support_audit` `1ecff5661b34e551cd8758b0` · `f4_full_pool_ceiling`
`5473d91d36e07da89f380551`.

`RELEASE_MANIFEST.json` carries the full hash of all 34 release files. Note that its own hash and the
hashes of `figures/*.pdf` change on every build, because matplotlib stamps a creation time into PDF
metadata; compare PNG hashes when checking for content drift.

## 4. Contents

| | |
|---|---|
| body words | **7,530** |
| total words | 9,567 |
| figures | **4** |
| tables | **9** (3 body, 6 appendix) |
| references | **25**, every one stating its access level |
| claim rows | **165**, unsupported numerical claims **0** |
| files in the release manifest | **34** |
| **PDF page count** | **n/a — not built** |

## 5. Release QA status

```
[freeze]      quantities 10 missing 0 | verdicts 4 missing 0
[claims]      tokens 89 | unsupported 0
[xrefs]       section refs 16 | appendix refs 6 | file refs checked
[latex]       environments balanced | 8 packages, all standard
[bibtex]      entries 25 | duplicate keys 0 | missing notes 0
RESULT: PASS (0 issues)
```

Two real defects inherited from V4 were found and fixed in the release copy: the data-availability
section and three figure captions pointed at V3 artefacts that do not exist in the release package.
V4 itself is unedited.

## 6. Unresolved blockers

| id | blocker | severity | owner |
|---|---|---|---|
| **B1** | nine cited artefacts excluded from version control by the `data/` rule (78,794 bytes of derived summaries) | high | user |
| **B2** | manuscript never typeset; no LaTeX toolchain or `pandoc` on the machine; `PDF_QA.md` is a stub | high | user |
| **B3** | no public repository, no DOI | high | user |
| **B4** | personal contact email in 54 tracked source files | medium | user |
| **B5** | licences undecided for code, manuscript and derived data | medium | user |
| **B6** | no independent verification of any result (disclosed in the paper; not a release gate) | low | future work |

**B1–B5 must be resolved before any public release.** None is a scientific issue.

## 7. What this freeze permits and forbids

**Permits:** reviewing RC1; building a PDF; resolving B1–B5; and, with explicit approval for each
step, the sequence in `PUBLIC_RELEASE_PLAN.md`.

**Forbids:** any change to the science without reopening review, as `SCIENTIFIC_FREEZE.md` sets
out; any external action — public repository, remote push, deposition, DOI, preprint, submission —
without explicit approval for that specific action; and any of the future-work items in
`FUTURE_RESEARCH.md`, which remain closed while alpha discovery is paused.
