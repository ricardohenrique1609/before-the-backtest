# Public package notes — Contextual Alpha

**Status: working-paper draft.** Not peer-reviewed, not submitted, no DOI. The verdict is a
**pre-registered null** (H20.3). The PROSPECTIVE_CONFIRMATION block (2025-10-13 → 2026-09-28) is
**unopened**, so the prospective confirmation is still pending.

Start with `paper.pdf` (or `paper.md`), then `H20_3_EXECUTION_REPORT.md` and `H20_3_VERDICT.json`.
`README.md` in this directory describes the stages H20.0–H20.3 and the layout.

## Where this comes from

This directory is an export of `Contextual Alpha/` from the research repository at commit `f335e79`
(`git archive` at `4eb65f4`, then the files changed since), with one edit, listed below. It is a
companion to *Before the Backtest*, the rest of this repository: same research programme and the
same 201-event delisting universe, but a separate study with its own question and verdict. Neither
paper revises the other (see the paper's §1, "Relation to the companion paper").

## The one edit

`scripts/h20_common.py`: the HTTP `User-Agent` contact address is read from the environment variable
`QIE_CONTACT_EMAIL` instead of being written into the file. The same was done for the scripts of
*Before the Backtest*. Because of this edit, the sha256 of this one file does not match the value
recorded in `manifests/H20_1_MANIFEST.csv`. Every other file is byte-identical to the research
repository commit.

## What is not included

- **Raw and interim data.** The research repository keeps it under `data/`, which is gitignored as a
  rule. The retrieval scripts are included; the fetched corpora are not. This follows the policy in
  `../DATA_RELEASE_POLICY.md`: public does not mean redistributable.
- **Inputs inherited from H18 and H19** (the delisting announcement universe and market bars). The
  scripts refer to them by their research-repository paths. `manifests/` records their hashes.

The scripts therefore document and audit the procedure; they do not run end to end from this
directory alone.

## Third-party text in the evidence files

`evidence/H20_1_SEMANTIC_AUDIT_SHEET.csv` and `evidence/H20_1_SEMANTIC_AUDIT_LABELS.csv` contain short
excerpts used for the semantic audit: titles and abstracts of US government documents (SEC and
Federal Reserve press releases, Federal Register), GDELT record metadata (URL, organisations, themes)
and Wikipedia portal snippets (CC BY-SA 4.0). They are reproduced only to make each audit label
checkable.

## Licence

The same three-part split as *Before the Backtest*, with its own scoped files in this directory:

| component | licence | file |
|---|---|---|
| code: `scripts/`, `tests/`, `paper/scripts/` | **MIT** | `LICENSE` |
| manuscript, figures, tables, bibliography, Markdown documentation | **CC BY 4.0** | `LICENSE-manuscript` |
| project-created data files (JSON, CSV, hashes) | **CC0 1.0** | `LICENSE-evidence` |

The CC0 dedication does not extend to the third-party excerpts in the semantic-audit files described
above.
