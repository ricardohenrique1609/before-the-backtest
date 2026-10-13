# FINAL PUBLICATION QA — v1.0.0

**Document:** `paper.pdf`, **24 pages**, SHA-256
`85a87a474a7ecc700d46db5c6156d4458ac141ab8321b073cc7991eda2e9d41b`, 612,592 bytes
**Engine:** Tectonic 0.17.0 · **Date:** 2026-10-13 · **Exit code:** 0

> v1.0.0 closes blocker **B7**, the author metadata. **No scientific content changed**, and the body
> of `paper.tex` is byte-identical to RC3. `PUBLICATION_PROOF_QA.md` records the RC3 proof that
> preceded this and is not amended.

---

## 1. What changed in the document

`paper.tex` differs from RC3 in **three lines**, and in nothing else:

```
-  pdfauthor={AUTHOR_METADATA_REQUIRED},
+  pdfauthor={Ricardo H. Ramos Silva},
-\author{AUTHOR\_METADATA\_REQUIRED}
-\date{2026-10-13}
+\author{Ricardo H. Ramos Silva\\[2pt]\textit{Independent Researcher}}
+\date{October 2026}
```

`paper.md` gains the byline block beneath its title and changes in no other way. The manuscript
previously carried no author at all: the byline existed only in the generated front matter, so the
Markdown source read as anonymous.

Because the body is unchanged, the 24 pages inspected at RC3 remain valid. That the layout did not
move is **verified, not assumed**: the page count is still 24, and the per-page analysis reports zero
margin ink and zero blank pages.

## 2. Title page

Read on the rendered page, not only in the source.

| check | result |
|---|---|
| title | **Before the Backtest: Pre-Freeze Common-Support Ceilings for Event-Driven Strategy Research** |
| author | **Ricardo H. Ramos Silva** |
| affiliation, on its own line beneath the name | *Independent Researcher* |
| date | October 2026 |
| employer or university | **absent** — explicitly excluded by the author |
| institutional endorsement, implied or stated | **none** |
| ORCID | **absent** — none provided, none invented |
| correspondence address | **absent** |
| location | **absent** |
| private email | **absent** |
| `AUTHOR_METADATA_REQUIRED` | **absent** |
| internal release labels RC1 / RC2 / RC3 | **absent** |
| internal commit hashes, referee acceptance | **absent** |
| any implication of journal acceptance or external peer review | **none** |

### A defect caught before the final build

The first attempt produced the byline as literal text on one line:

```
Ricardo H. Ramos Silva \textbackslash{}\textbackslash{} Independent Researcher
```

The author string was passed through the inline escaper, which correctly escaped the LaTeX line
break it contained. The affiliation is now passed to the converter separately and the break is
emitted as LaTeX, so the name and the affiliation set on their own lines; the PDF document-author
property carries the plain name, because a line break is not metadata.

## 3. PDF document properties

| field | value |
|---|---|
| title | the full paper title |
| author | `Ricardo H. Ramos Silva` — the plain name, no line break |
| subject | the design-stage feasibility description |
| keywords | common support, positivity, outcome-free design, point-in-time data, event studies, pre-registration, research feasibility |
| journal, DOI, publisher | **deliberately unset** — none exists |

## 4. Automated checks on the compiled PDF

`scripts/release_pdf_audit.py`, against the extracted text of the published PDF:

```
[must not appear]  11 patterns, all 0 hits
[must appear]       9 patterns, all present
[frozen science]   14 patterns, all present
RESULT: PASS (0 issues)
```

Four must-not patterns are new at v1.0.0, and the author check was tightened:

| check | hits |
|---|---|
| `AUTHOR_METADATA_REQUIRED` | **0** |
| any email-shaped string | **0** |
| the excluded employer and university names | **0** |
| any ORCID claim | **0** |
| the exact byline `Ricardo H. Ramos Silva` | **1** |
| the exact affiliation `Independent Researcher` | **1** |

The PDF is final and is the document that would be attached to the release. **It has not been
published**: see `GITHUB_PUBLIC_RELEASE.md`.

The previous author pattern accepted the placeholder *or* any author-shaped string, so it would have
passed a PDF carrying the wrong byline. A wrong name is the one metadata error that cannot be
corrected after publication, so it is now asserted exactly.

`scripts/release_pdf_pages.py`, rasterising every page at ~144 dpi:

```
24 pages | pages with ink in a 2.5% margin band: 0 | blank pages: 0
RESULT: PASS (0 issues)
```

This analysis was run ad hoc at RC2 and RC3; it is now a committed script, so the check is
re-runnable rather than described.

## 5. Science — unchanged, asserted mechanically

`scripts/release_audit.py`, against the manuscript, and `release_pdf_audit.py`, against the extracted
PDF text:

```
[freeze]   quantities 10 missing 0 | verdicts 4 missing 0
[claims]   tokens 90 | unsupported 0
[xrefs]    section refs 16 | appendix refs 6 | file refs checked
[latex]    environments balanced | 11 packages
[bibtex]   entries 25 | duplicate keys 0 | missing notes 0
RESULT: PASS (0 issues)
```

| frozen quantity | value | in PDF |
|---|---|---|
| candidate events | 62 | ✔ |
| floor *m* | 20 | ✔ |
| support quantiles p10/p25/median/p75/p90 | 0 / 0 / 1 / 2 / 57 | ✔ |
| events below the floor | 52 of 62 | ✔ |
| full-pool ceiling range | 0 to 27 | ✔ |
| ceiling median | 7 | ✔ |
| dates reaching the floor | 3 of 25 | ✔ |
| implied confirmatory sample *N\** | 10 | ✔ |
| required minimum *N_min* | 40 | ✔ |
| price columns loaded | none | ✔ |

| verdict | in PDF |
|---|---|
| `PRE-REGISTERED NULL` | ✔ |
| `DESIGN INFEASIBLE UNDER THIS SPECIFICATION` | ✔ |
| `OPEN` | ✔ |
| `IMPLEMENTATION REJECT / ECONOMIC QUESTION UNRESOLVED` | ✔ |

Figure 4's caption still reads **"recorded range, not a confidence interval"**. ✔

Converter regression tests: **14 passed, 0 failed.** Each pins a defect found in a compiled PDF.

## 6. Remaining limitations of this QA

- Text extraction reflects font character mapping, not the source. Computer Modern extracts `\sum` as
  "P" and `^{*}` as U+2217; the audit accepts those forms deliberately, with the reason recorded in
  the script, and the glyphs were confirmed by eye.
- The pixel check detects ink in a margin band and blank pages. It cannot judge typographic quality.
- A bulleted list inside a block quote still renders as inline hyphenated text in one place. Content
  is unaffected; it is recorded rather than fixed.
- Overfull horizontal boxes are reported by the engine at three points. None places ink in the margin
  band, which is the check that matters for a printed page.
