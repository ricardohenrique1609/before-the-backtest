# LICENCE DECISION — PENDING

**No licence has been applied.** The repository contains no `LICENSE`, `COPYING` or equivalent file,
and none is created here. Choosing a licence is the author's decision with legal consequences, and
nothing in the repository establishes a prior intent to infer from.

**Current legal status.** With no licence, default copyright applies: others may read the repository
if it is made public, but have **no** right to copy, modify or redistribute it. That is almost
certainly not the intent for a paper about reproducibility, so a decision is required before release.

Three components want different answers.

---

## 1. Code — `scripts/`, build and audit tooling

| option | effect | fit |
|---|---|---|
| **MIT** | use, modify, redistribute, including commercially; attribution required; no warranty | **recommended default.** Maximum reuse of the procedure, which is the point of the paper |
| **Apache-2.0** | as MIT, plus an explicit patent grant and a NOTICE requirement | sensible if any institutional affiliation is involved |
| **BSD-3-Clause** | as MIT, plus a no-endorsement clause | equivalent in practice |
| **GPL-3.0** | derivatives must also be GPL | works against adoption of a methodological procedure |

**Recommendation: MIT**, unless an employer or institution has a policy that requires otherwise. The
paper's contribution is a procedure meant to be copied; a permissive licence serves that directly.

## 2. Manuscript, figures and tables

| option | effect | fit |
|---|---|---|
| **CC BY 4.0** | share and adapt with attribution, including commercially | **recommended.** Compatible with every preprint server and with most journals' green open-access terms |
| **CC BY-SA 4.0** | as above, derivatives must share alike | adds friction for quotation in other works |
| **CC BY-NC 4.0** | non-commercial only | **not recommended**: blocks ordinary scholarly reuse and is incompatible with several repositories |
| **all rights reserved** | reading only | contradicts the paper's own argument |

**Recommendation: CC BY 4.0.** One caution: if the paper is later submitted to a journal, check that
venue's policy before posting a preprint under CC BY — a small number of publishers restrict it.
`PUBLIC_RELEASE_PLAN.md` places the preprint before journal submission, which makes CC BY the natural
choice, but the check belongs to the author.

## 3. Data

**No licence may be asserted over data this project did not create.** Per `DATA_RELEASE_POLICY.md`,
no raw corpus from any external source is redistributed. What can be licensed is the **derived
artefacts** — gate JSONs, audit JSONs, event tables, figure source data — which are this project's
own computed summaries.

| option | effect |
|---|---|
| **CC0 1.0** | dedicate derived artefacts to the public domain; maximum verifiability |
| **CC BY 4.0** | attribution required for the derived artefacts |
| **ODbL** | share-alike for databases; heavier than needed here |

**Recommendation: CC0 1.0 for the derived artefacts**, so that verification carries no friction at
all, with the clear statement that it applies **only** to this project's derived outputs and confers
no rights over the underlying sources.

## 4. Suggested combination

| component | licence |
|---|---|
| code | **MIT** |
| manuscript, figures, tables | **CC BY 4.0** |
| derived artefacts | **CC0 1.0** |

This is a common and well-understood split for a reproducible research release.

## 5. What to do once decided

1. Add `LICENSE` at the repository root with the code licence.
2. Add `LICENSE-manuscript` (or a licence line in the paper's front matter) for the text and figures.
3. Add `LICENSE-data` covering the derived artefacts only, with the no-rights-over-sources statement.
4. Update the `license:` field in `CITATION.cff` and `zenodo.json`, both currently `PENDING`.
5. State the split in `README.md`.

**Nothing in this list has been done.** Tracked as blocker **B5** in `RELEASE_BLOCKERS.md`.
