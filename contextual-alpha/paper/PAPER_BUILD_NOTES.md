# Paper build notes

**Status:** working-paper draft. Not peer-reviewed, not released, not published, no DOI, not pushed.

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

1. **`build_paper_assets.py`** writes `tables/` and `figures/` and `PAPER_DATA_MANIFEST.json`.
   - It reads only frozen artefacts and records the sha256 of every input and output.
   - It refits, rescores and tunes nothing.
   - The one recomputation is the 2,000-replicate two-way bootstrap distribution drawn in
     Figure 5. The H20.3 run stored only its summary, so the distribution is regenerated with the
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
| H20.1 | `e21c264` | representation gate (Table 2, A1, Figure 6) |
| H20.2 + A02 | `9932e20` | design (Table 3, §7, Figure 2) |
| H20.3 | `180def4` | results (Tables 4–7, A2, Figures 3–5) |

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

- **No LaTeX build.** The previous paper's Tectonic workflow can be reused later inside this
  directory.
- No public release, DOI or push.
- No H20.4, no new hypothesis, no opening of PROSPECTIVE_CONFIRMATION.
- The human re-annotation of the H20.1 semantic audit has not been done, and is disclosed as a
  limitation.
