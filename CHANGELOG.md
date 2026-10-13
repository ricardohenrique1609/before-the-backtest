# CHANGELOG

> **No scientific result, verdict, sample, empirical estimate or interpretation changed after
> scientific acceptance at V4.** Everything in the RC1 section below is a proof, production, metadata
> or repository-hygiene change, and each is verified in `RELEASE_QA.md`.

---

## v1.0.0 — 2026-10-13 — public release

The authorised byline and the paper-only public package. **SCIENTIFIC CHANGES: 0.** The body of
`paper.tex` is byte-identical to RC3; the compiled PDF is still 24 pages, with zero margin ink and
zero blank pages, so nothing reflowed.

Published at <https://github.com/ricardohenrique1609/before-the-backtest>, tag `v1.0.0`, with `paper.pdf`
attached to the release. See `GITHUB_PUBLIC_RELEASE.md`.

### RELEASE METADATA — blocker B7 closed

| # | change |
|---|---|
| 1 | the title page carries the authorised byline **Ricardo H. Ramos Silva**, with **Independent Researcher** beneath it, replacing `AUTHOR_METADATA_REQUIRED` |
| 2 | **no employer or university affiliation is stated**, by the author's explicit instruction, and **no institutional endorsement is implied**; no ORCID, because none was provided and none is invented; no correspondence address is published |
| 3 | the cover date is the month, **October 2026**; the exact release date 2026-10-13 stays in machine-readable metadata |
| 4 | `CITATION.cff` and `zenodo.json` carry the same byline, version `1.0.0`; `doi` remains unset — **no DOI was created and no deposition exists** |
| 5 | `RELEASE_MANIFEST.json` records the release version, the title and the authorised byline alongside the file hashes |

### TOOLING — one canonical byline

| # | change |
|---|---|
| 6 | `scripts/release_metadata.py` added: the title, cover date, version and byline are defined **once** and read by the build, the manifest and the audits, so the name cannot drift into a variant |
| 7 | the build **fails** if the byline acquires an employer name, an email address, an ORCID or the old placeholder |
| 8 | `scripts/release_pdf_audit.py` asserts the exact byline against the extracted PDF text, and rejects the placeholder, any email-shaped string, the excluded employer names and any ORCID claim — the previous pattern accepted any author-shaped string and would have passed a wrong byline |
| 9 | `scripts/release_pdf_pages.py` added: the per-page margin-ink and blank-page analysis was run ad hoc at RC2 and RC3 and is now a committed, re-runnable script |
| 10 | the release converter emits the byline block as LaTeX. Passing it through the inline escaper printed the line break as literal `\\` text on one line instead of setting the affiliation beneath the name |
| 11 | `release/paper.md` carries the byline itself — it previously read as anonymous — and the converter consumes that block so `\maketitle` does not print it twice. Anything else between the title and the first section is a build error rather than silently dropped text |

### PUBLICATION

| # | change |
|---|---|
| 12 | the paper-only public package is built by `scripts/release_public_repo.py` and audited on the exact published directory in `PUBLIC_REPO_FINAL_AUDIT.md` |
| 13 | `README.md` is publication-grade: byline, status, how to cite, licences, limitations |
| 14 | **B3a closed** — the public repository exists, tagged `v1.0.0`, with the PDF attached to the release. **B3b stays open by decision**: no DOI, no Zenodo deposition, no SSRN, no arXiv, no journal submission |

### NOT CHANGED

The manuscript body, the contribution, the novelty positioning and the Rubin concession; all twelve
frozen quantities; the four verdicts and their interpretation; the scope; the registry denominator;
the limitations; `references.bib`, byte-identical since RC2.

---

## RC3 — 2026-10-13 — publication proof

Typesetting, bibliography rendering, public-paper metadata and packaging. **SCIENTIFIC CHANGES: 0.**
Every frozen quantity and every verdict was asserted mechanically against the manuscript and against
the extracted text of the compiled PDF.

### PRODUCTION — mathematics

The RC2 PDF degraded mathematical expressions. All are fixed in the release converter, never by hand
in `paper.tex`.

| # | change |
|---|---|
| 1 | the support definition renders as mathematics with `\in` and proper set braces; RC2 had **lost the membership symbol** |
| 2 | `N* = \Sigma_e I_e` renders with a real summation; RC2 printed **"N* = _e I_e"**, the sigma lost |
| 3 | the indicator renders as $I_e = \mathbf{1}[S_e \ge m]$ |
| 4 | identifiers — $S_e$, $I_e$, $t_e$, $C(t_e)$, $M(e,c,t)$, $N^{*}$, $N_{\min}$, $m$ — set as mathematics instead of typewriter text with literal underscores, including inside code spans |
| 5 | inequalities and bounds set as mathematics with `\le`, `\ge` and a true `\min` subscript |
| 6 | accented characters in cited authors' names emitted as LaTeX accent commands; the first RC3 build silently dropped the ogonek and printed **"Bdowska-Sójka"** |

### PRODUCTION — lists

| # | change |
|---|---|
| 7 | §2.3's six-step procedure survives inside its block quote; RC2 joined it into one paragraph |
| 8 | §2.6's three components render **1, 2, 3**; RC2 numbered all three `1.` and split continuation lines into separate paragraphs |

### PRODUCTION — bibliography

| # | change |
|---|---|
| 9 | a real **References section inside the PDF**, 25 entries, replacing the pointer "See references.bib in this directory" |
| 10 | generated at build time by `scripts/release_refs.py` from `references.bib`, so the 25 entries are not duplicated by hand and the build stays reproducible |
| 11 | `REFERENCES_QA.md` added: 25 entries, 0 unresolved citations, 0 duplicate keys, access-level note on every entry |

### PRODUCTION — front matter and metadata

| # | change |
|---|---|
| 12 | the internal release block — "Release candidate RC1", the V1–V4 provenance paragraph, commit hashes — **removed from the reader-facing paper**. It is preserved in `RELEASE_PROVENANCE.md`, `CHANGELOG.md` and `SCIENTIFIC_FREEZE.md` |
| 13 | one neutral line added to Data and Code Availability: reproducibility materials and version history are available with the accompanying repository |
| 14 | PDF metadata set: title, author, subject, keywords. **No journal, no DOI, no publisher**, because none exists |
| 15 | cover date 2026-10-13 |

### RELEASE METADATA

| # | change |
|---|---|
| 16 | author metadata is **`AUTHOR_METADATA_REQUIRED`** — no authoritative identity exists, a git commit identity is not an authorised byline, and none was inferred. Tracked as **blocker B7**; affiliation and ORCID are absent rather than guessed |

### TOOLING

| # | change |
|---|---|
| 17 | `scripts/release_md_to_tex.py` rewritten to own the conversion loop: inline mathematics, list continuation, lists inside quotes, long tables, Markdown escapes, Unicode |
| 18 | `scripts/test_release_converter.py` added — **14 regression tests**, each pinning a defect found in a compiled PDF |
| 19 | `scripts/release_refs.py` and `scripts/release_pdf_audit.py` added |

The historical converter `scripts/paper_md_to_tex.py` is **unmodified**, so regenerating the frozen
V1–V4 `.tex` files stays byte-exact.

### NOT CHANGED

The contribution, the novelty positioning and the Rubin concession; all twelve frozen quantities; the
verdicts and their interpretation; the scope; the registry denominator; the limitations; the
scientific abstract text.

---

## RC1 — 2026-10-12 — release candidate

Derived from V4 (`versions/v4/paper_v4.md`, SHA-256 `def1442c…`, commit `c597ba6`), accepted by referee #4.

### PROOF

| change | referee item | what it does |
|---|---|---|
| **Quantile convention named in §4.4.** The reported support quantiles were produced by `pandas.Series.quantile` with its default `interpolation="linear"` in `scripts/h19_2_prefreeze.py`, rounded to one decimal place. Under that convention a p75 of exactly 2.0 over 62 observations requires the 46th and 47th order statistics both to equal 2, so at most 15 observations exceed 2. The text now also gives the convention-robust bound, at most 16 under a nearest-rank convention. | V4 item 1 | **Makes the existing bound precise. It does not replace it.** The published claim `N* ≤ 15` is correct under the documented convention; the added sentence states the weaker bound that holds under any convention. The conclusion `N* ≪ N_min = 40` is unchanged, and so is the infeasibility verdict. Established by **inspecting committed source**, not by re-running anything. |

### PRODUCTION

| change | referee item | what it does |
|---|---|---|
| Figure 4 legend moved below the axis | V4 item 2 | the legend no longer overlaps the hatched band or the marker at 27. **Plotted values are byte-identical to V4**; only placement changed |
| stale artefact references corrected | — | the data-availability section pointed at `CLAIM_EVIDENCE_MATRIX_V3.csv`, `scripts/paper_build_v3.py`, `scripts/paper_audit_v3.py` and `references_v3.bib`; three figure captions pointed at `figures/data/v3_*.csv`. All now point at the release artefacts. **This was a real defect in V4, found by the release cross-reference audit** |
| clean release filenames | — | `paper_v4.md` → `paper.md`, `references_v4.bib` → `references.bib`, `figures/v4_f3_…` → `figures/f3_…`, and so on |
| version header replaced by a provenance note | — | names the accepted version, its hash and its commit, and states that every difference from it is proof, production or formatting |
| `paper.tex` regenerated | — | from the release `paper.md` by the committed converter; never hand-edited |

### RELEASE METADATA

`CITATION.cff`, `zenodo.json`, `requirements.txt`, `RELEASE_MANIFEST.json`, `RELEASE_PROVENANCE.md`.
Every identifier field — DOI, repository, licence, author — is `PENDING`. **No DOI was reserved and
no deposition was created.**

### REPOSITORY HYGIENE

`README.md`, `BUILD.md`, `PUBLIC_REPO_AUDIT.md`, `DATA_RELEASE_POLICY.md`, `LICENSE_DECISION.md`,
`RELEASE_BLOCKERS.md`, `PDF_QA.md` (stub), `PUBLIC_RELEASE_PLAN.md`, `FUTURE_RESEARCH.md`, and the
new `scripts/release_build.py` and `scripts/release_audit.py`.

### NOT CHANGED

The contribution statement; the novelty positioning and the Rubin concession; all twelve frozen
quantities of the demonstration; every verdict label and its interpretation; the scope paragraph; the
31-entry registry denominator with its nine economic rejections and archived promotion; the
floor-invariance bound; the specificity disclosure; the matching-rule ranking; the limitations.

### NOT DONE

No PDF was built — no LaTeX toolchain exists in the environment (blocker **B2**). Nine cited
artefacts remain outside version control (**B1**). No public repository, DOI or licence (**B3**,
**B5**). A personal email remains in 54 tracked source files (**B4**).

---

## Scientific lineage

Four reviewed versions, each frozen with its referee report and never amended afterwards.

| version | what it was | referee |
|---|---|---|
| **V1** | a broad falsification-first paper arguing that apparent trading opportunities are manufactured before model fitting, across seventeen hypothesis families | **MAJOR REVISION** — five rejection conditions: hidden denominator, ex post governance presented as ex ante, novelty positioning absent, `NULL` over-interpreted, two overclaimed sentences |
| **V2** | denominator and governance correction: the full 31-entry registry, the §2A/§2B split dating every governance rule to the failure that produced it, the methodology literature added, `NULL` bounded, "feasible for small capital" removed | **MAJOR REVISION** — the paper still had four co-equal contributions and no single one |
| **V3** | single-contribution restructure around the pre-freeze common-support ceiling, with the thesis narrowed to the domain the registry supports; novelty conceded to Rubin (2008) after a literature search; floor-invariance bound added; body cut from 10,786 to 7,026 words | **MINOR REVISION** — six editorial items |
| **V4** | acceptance revision: all six items, none partial | **ACCEPT** |

The direction across versions was consistently **narrower**. V1 claimed that pre-model failure is
typically decisive; V4 reports the registry that refutes that and claims only a procedure. V1 listed
four contributions; V4 has one, and concedes its principle to prior work.
