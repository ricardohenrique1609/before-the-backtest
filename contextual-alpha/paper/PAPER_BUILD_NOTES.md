# Paper build notes

**Status:** working-paper draft, pre-referee. Not peer-reviewed, not submitted, no DOI, no tag.
Published on 2026-11-02 as a working draft in the public repository `before-the-backtest`,
directory `contextual-alpha/`, at the author's request.

## Rebuild

From the repository root, with the project venv:

```bash
.venv/Scripts/python "Contextual Alpha/paper/scripts/build_paper_assets.py"
```

```bash
.venv/Scripts/python "Contextual Alpha/paper/scripts/render_manuscript.py"
```

```bash
.venv/Scripts/python "Contextual Alpha/paper/scripts/claim_audit.py"
```

```bash
.venv/Scripts/python -I "Contextual Alpha/paper/scripts/build_release.py"
```

1. **`build_paper_assets.py`** writes `tables/` and `figures/` and `PAPER_DATA_MANIFEST.json`.
   - It reads only frozen artefacts and records the sha256 of every input and output.
   - It refits, rescores and tunes nothing.
   - The one recomputation is the 2,000-replicate two-way bootstrap distribution drawn in
     Figure 6. The H20.3 run stored only its summary, so the distribution is regenerated with the
     frozen seed (20261103) and procedure from the frozen out-of-fold predictions. The script refuses
     to draw the figure unless the recomputed 95% interval equals the frozen one; it does, to
     machine precision.
2. **`render_manuscript.py`** turns `manuscript_src.md` into `manuscript.md` by inlining each
   `{{TABLE:...}}` marker from `tables/`, so manuscript tables cannot drift from the artefacts.
3. **`claim_audit.py`** writes `CLAIM_LEDGER.csv` and `CLAIM_AUDIT_REPORT.json`. It checks that:
   - every ledgered value is resolved from its frozen source and compared with the manuscript within
     rounding;
   - every numeric token in the manuscript prose is ledgered or structural;
   - forbidden phrasings are absent ("untouched holdout", "external validation", "fully prospective",
     "proves", "novel", trading/profitability language and similar);
   - the LCUV terminology and the "prospective confirmation is pending" statement are present.

4. **`build_release.py`** writes the reader-facing `paper.md`, `paper.tex` and `paper.pdf` at the top of
   `Contextual Alpha/`. Production only:
   - citation keys become author-year labels taken from `references.bib`, and the reference list is
     rendered from it, with each entry's access note;
   - figure captions are set under their figures, and the PDF figures are used;
   - the title page carries the pre-referee draft notice.
   It reuses the Before the Backtest release converter (`scripts/release_md_to_tex.py`) and
   bibliography reader (`scripts/release_refs.py`) read-only, switches off that paper's
   mathematics table, and adds the Unicode this manuscript needs at run time. It fails if any
   citation key is missing from the bibliography or any non-ASCII character reaches `paper.tex`.

## PDF build record

| | |
|---|---|
| engine | Tectonic 0.17.0, the binary verified for Before the Backtest (`.tools/tectonic/`, its BUILD.md §4.1) |
| build date | 2026-11-02 |
| pages | 24 |
| overfull vertical boxes | 0 |
| overfull horizontal boxes | 18, the widest 16.1pt (wide tables and one long reference URL) |

The PDF embeds a creation timestamp, so its hash changes on every build; `paper.tex` and `paper.md`
are byte-reproducible.

## Manuscript change after pass 2

One paragraph was added to §1, **"Relation to the companion paper"**, stating how this study relates
to *Before the Backtest*: same research programme, same 201-event delisting universe (H18.1b), same
design-before-outcome discipline, different question; the earlier market-only H18.3 test is listed in
that paper's registry as a pre-registered null. Two ledger rows cover it (C118, C119). No result,
number or verdict changed.

## Figures

- Six figures are produced, as PNG at 300 dpi and PDF.
- **Palette:** two categorical hues, M0 blue `#2a78d6` and M2 orange `#eb6834`. They are validated
  with the dataviz validator: CVD ΔE 24.7, normal-vision ΔE 33.6, contrast ≥ 3:1 on the light
  surface. All other ink is neutral grey. Figures carry direct labels and a single y-axis, and use
  no decoration.
- PDF files embed renderer metadata, so only PNG hashes are recorded in the manifest.

## Inputs (frozen commits)

| stage | commit | role here |
|---|---|---|
| H20.0 | `a14c347` | data gate (Table 1, §3, §5) |
| H20.1 | `e21c264` | representation gate (Table 2, A1, Figure 2) |
| H20.2 + A02 | `9932e20` | design (Table 3, §7, Figure 3) |
| H20.3 | `180def4` | results (Tables 4–8, A2, Figures 4–6) |

No frozen experiment file was modified to build the paper. All paper outputs live under
`Contextual Alpha/paper/`.

## Bibliography

`references.bib` has 26 entries:
- 11 reused **verbatim** from the author's previous paper's verified bibliography, with their
  access-level notes;
- 1 entry for that previous paper, from its `CITATION.cff`;
- 14 added in verification pass 2 (2026-10-19). Each was read in full text or as official
  documentation, as recorded in `REFERENCE_VERIFICATION.md`.

No reference was invented, and none was cited from a snippet or an aggregator. Gap outcomes are in
`REFERENCE_GAPS.md`: 10 resolved and 1 partially resolved (7B purging/embargo has no readable primary
source, so it is stated as the design's own rationale). All manuscript edits in pass 2 are logged
old→new in `MANUSCRIPT_CHANGES_PASS2.json`: null-language, literature and referee-pass edits.

## Not done (deliberately)

- No DOI, tag, Zenodo deposit or submission. The PDF is a pre-referee draft, not a v1.0.0.
- The hostile-referee rounds that *Before the Backtest* went through before its PDF have not been run.
- No H20.4, no new hypothesis, no opening of PROSPECTIVE_CONFIRMATION.
- The human re-annotation of the H20.1 semantic audit has not been done, and is disclosed as a
  limitation.

## Revision 1 (2026-11-02), after `REFEREE_REPORT_V1.md`

Every referee point is answered in `AUTHOR_RESPONSE_V1.md`. In short:
- **Text.** Scope in the subtitle and abstract; the week-level mechanism and the post-hoc yardstick
  (§2, §7, §8.3); the A02 amendment and the verdict under the v1 rule (§7); the penalty path and
  the pooled versus mean-of-folds split (§9); a "Use of AI tools" section; an availability
  statement that matches the public package; the production notes left the References section.
- **Tables.** Table 7 gains the primary row, a mean-of-folds column and the v1-rule verdict; new
  Table 8 (penalty path). Both are read from the frozen exploratory artefact; nothing was refitted.
  Markdown tables now print fixed decimals and λ, Δ and true minus signs; the CSVs keep raw values.
- **Figures.** Renumbered in order of appearance (funnel to §1). Every PNG is byte-identical to its
  earlier file under the new name.
- **Bibliography.** `bedowska2025zombie` gained `year = {2026}` from the Crossref record of its DOI
  (issued and published-print January 2026, volume 81). It is otherwise the entry reused from the
  previous paper. Entries without an author now lead with their title, in the text and in the list.
- **Claim audit.** 142 ledger rows, all supported. Rows C120–C142 cover the revision; C030, C031,
  C095 and C117 were updated to the new wording.
- No result, number, verdict or frozen file changed.
