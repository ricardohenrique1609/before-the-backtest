# RELEASE QA — RC1

Final production audit of the release candidate. **Date:** 2026-10-12.

**Audit command:** `.venv/Scripts/python -I scripts/release_audit.py`

```
[freeze]      quantities 10 missing 0 | verdicts 4 missing 0
[claims]      tokens 89 | unsupported 0
[xrefs]       section refs 16 | appendix refs 6 | file refs checked
[latex]       environments balanced | packages: inputenc, fontenc, lmodern, geometry, graphicx,
              microtype, csquotes, hyperref
[bibtex]      entries 25 | duplicate keys 0 | missing notes 0
[manifest]    33 files hashed | pdf_built=False
RESULT: PASS (0 issues)
```

---

## 1. Science — unchanged

Ten frozen quantities and four verdict labels are asserted mechanically against `paper.md`. All
present.

| frozen quantity | value | present |
|---|---|---|
| candidate events | 62 | ✔ |
| support floor *m* | 20 | ✔ |
| support quantiles | 0 / 0 / 1 / 2 / 57 | ✔ |
| events below floor | 52 of 62 | ✔ |
| full-pool ceiling range | 0 to 27 | ✔ |
| full-pool ceiling median | 7 | ✔ |
| dates reaching the floor | 3 of 25 | ✔ |
| implied confirmatory sample N\* | 10 | ✔ |
| required minimum *N_min* | 40 | ✔ |
| price columns loaded | none | ✔ |

| verdict | present |
|---|---|
| H18.3 `PRE-REGISTERED NULL` | ✔ |
| H19.2 `DESIGN INFEASIBLE UNDER THIS SPECIFICATION` | ✔ |
| H14 `OPEN` | ✔ |
| H13 `IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED` | ✔ |

**Contribution statement, novelty positioning, Rubin concession and registry denominator:** verified
by reading, unchanged from V4. The 31-entry registry with its nine economic rejections and archived
promotion is intact in §7 and Appendix B, as is *"a claim about a **procedure**, not about a
prevalence."*

**Verification that V1–V4 were not touched:** `scripts/paper_audit_v4.py` reports
`V1+V2+V3 files 16 | changed 0`, and the V4 files were checked separately. See
`RELEASE_PROVENANCE.md` §2.

## 2. Proof items

| referee V4 item | state |
|---|---|
| 1 — name the quantile convention | **done.** `pandas.Series.quantile`, default `interpolation="linear"`, in `scripts/h19_2_prefreeze.py`, rounded to one decimal. Established by inspecting committed source, not by re-running. The convention-robust bound (at most 16 under nearest-rank) is stated alongside, so the conclusion holds under either reading |
| 2 — reposition Figure 4's legend | **done.** Legend moved below the axis; no overlap with the hatched band or the marker at 27. Plotted values byte-identical to V4 |

## 3. Production

| check | result |
|---|---|
| unsupported numerical claims | **0**, over 89 distinct numeric tokens |
| section cross-references resolve to headings | **16 of 16** |
| appendix references resolve to headings | **6 of 6** (A–F) |
| references to the removed Appendix A.2 | **none** |
| file references exist on disk | **all** |
| stale current-version references (`_v3`, `_v4`) | **none**, after fixing seven found by this audit |
| LaTeX environments balanced | **yes** |
| LaTeX braces balanced | **yes** |
| `\includegraphics` targets present | **4 of 4** |
| stray unescaped `%`, `&`, `#` | **none** |
| BibTeX duplicate keys | **0** of 25 entries |
| BibTeX entries lacking a title | **0** |
| BibTeX entries lacking an access-level note | **0** |
| **PDF compiles** | **NOT DONE** — no toolchain; blocker **B2** |
| **PDF visually inspected** | **NOT DONE** — `PDF_QA.md` is a stub |

### Defects this audit found and fixed

Both were real and both originated in V4, which the referee did not catch:

1. **Stale artefact references.** The data-availability section pointed at
   `CLAIM_EVIDENCE_MATRIX_V3.csv`, `scripts/paper_build_v3.py`, `scripts/paper_audit_v3.py` and
   `references_v3.bib`. A reader of V4 would have been sent to the wrong files.
2. **Stale figure-data references.** Three figure captions pointed at `figures/data/v3_*.csv`, which
   do not exist in the release package.

Fixed in the release copy only. **V4 is not edited**, and its references remain as reviewed.

## 4. Repository

| check | result |
|---|---|
| secrets, keys, tokens, passwords, certificates | **none found** — `PUBLIC_REPO_AUDIT.md` |
| cloud credentials, `.env`, cookies, session IDs | **none found** |
| absolute local paths or usernames in tracked files | **none found** |
| proprietary employer data | **none found**; the matches reviewed were a publicly listed issuer appearing in a takeover-offer dataset, which is public market information |
| personal data | **one item**: a contact email in 54 tracked source files, required by the SEC fair-access policy. Zero occurrences under `papers/`. Blocker **B4** |
| data licensing reviewed | **yes** — `DATA_RELEASE_POLICY.md`; no raw corpus redistributed |
| cited artefacts available to a reader | **partial** — 34 of 43 tracked; nine excluded by the `data/` rule. Blocker **B1** |
| licensing | **undecided** — `LICENSE_DECISION.md`, blocker **B5** |
| README complete | **yes**, including the limitations a reader should meet first |
| reproduction instructions complete | **yes** — `BUILD.md`, with the deterministic and non-deterministic paths separated |

## 5. Contents

| | V4 | RC1 |
|---|---|---|
| body words | 7,394 | **7,530** |
| figures | 4 | 4 |
| tables | 9 (3 body, 6 appendix) | 9 |
| references | 25 | 25 |
| claim rows | 165 | 165 |
| files in the release manifest | — | **33** |

The 136-word increase is the quantile-convention proof note and the expanded data-availability
section. No section was added and none was padded.

## 6. Experiments

**Zero.** The only programs run in the release phase were `scripts/release_build.py` (re-renders one
figure from the same committed values; regenerates LaTeX) and `scripts/release_audit.py` (reads
files, hashes them). No experiment, backtest, matching, sensitivity analysis, bootstrap, model,
return, P&L, price load, event reconstruction, independent replication or order-book analysis. No
gate, verdict, pre-registration or historical artefact altered.

## 7. Open blockers

| id | blocker | severity |
|---|---|---|
| **B1** | nine cited artefacts excluded from version control | high |
| **B2** | manuscript never typeset; `PDF_QA.md` is a stub | high |
| **B3** | no public repository, no DOI | high |
| **B4** | personal email in 54 tracked files | medium |
| **B5** | licences undecided | medium |
| **B6** | no independent verification (disclosed; not a release gate) | low |

**RC1 is not releasable until B1–B5 are resolved by the user.** The science is complete; the
production work is not.
