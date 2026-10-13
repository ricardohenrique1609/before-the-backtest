# DATA RELEASE POLICY

What may be redistributed with this paper, what may not, and how a reader obtains the rest.

**Governing principle: public does not mean redistributable.** A document being free to fetch from an
institution's website says nothing about the right to republish it. Where the right is unclear, the
raw data is **not** included and the retrieval path is documented instead.

---

## 1. Classification of every raw source

| source | used by | class | reason |
|---|---|---|---|
| **Cryptocurrency venue market-data archive** (daily and monthly bar files) | H18, H19 | **LINK-ONLY** | The venue's terms govern bulk redistribution of its market data. The files are large, fetchable without credentials, and stable by filename. Retrieval scripts are included; the archives are not. |
| **Venue announcement catalogue** (delisting and risk-tag notices) | H18.0b–H19.2 | **LINK-ONLY** | Published web content owned by the venue. Our *derived* classifications and event tables are included; the fetched notice bodies are not. |
| **SEC EDGAR filings and structured datasets** | H13, H15, H16.1, H17.0, H10, H11, H12 | **REDISTRIBUTABLE in principle, LINK-ONLY in practice** | US government works are generally not copyrightable, so redistribution is permissible; they are excluded for size, not rights. EDGAR's fair-access policy requires an identifying `User-Agent`, which the retrieval scripts set. |
| **Brazilian regulatory filings (CVM)** | H14, H14.1–H14.3 | **UNCERTAIN** | Public filings under a regulator's own terms of use, not reviewed here. Excluded. |
| **FDA public datasets** | H16.1 | **UNCERTAIN** | Excluded; a bulk file is already gitignored by name. |
| **Free price data for listed equities** | H10–H13, H17.0 | **LINK-ONLY** | Third-party API terms typically prohibit redistribution of bulk historical prices. |
| **Academic literature** | all | **NOT REDISTRIBUTABLE** | Publisher-held copyright. `references.bib` carries identifiers and a stated access level per entry. Several entries were read only at abstract or metadata level and say so. |

**No raw corpus from any source above is included in the release package.**

## 2. What the release package does include

| included | class | rationale |
|---|---|---|
| all analysis, build and audit **code** | our work | the procedure must be inspectable |
| **derived summary artefacts** — gate JSONs, audit JSONs, event tables | our work, computed from public sources | small, non-substitutable for the sources, and necessary to verify the paper's numbers |
| **manifests and SHA-256 hashes** | our work | integrity checking without redistribution |
| **retrieval scripts** | our work | the documented path from public sources to the derived artefacts |
| **figures, tables, the manuscript, the claim–evidence matrix** | our work | the paper itself |

A derived artefact is included when it is a *summary* — counts, quantiles, verdicts, coverage rates —
rather than a copy. None of the included artefacts reconstitutes a source corpus.

## 3. The evidence bundle — gap closed

Nine derived artefacts cited by `CLAIM_EVIDENCE_MATRIX.csv` sit under `data/`, which the repository's
`.gitignore` excludes wholesale. Rather than weaken that rule, the nine are **copied into
`evidence/`** inside the release package, which is tracked. They total **78,794 bytes** and contain
only summary statistics.

`EVIDENCE_MANIFEST.csv` records, for each: release path, original repository path, producing family,
source commit, byte size, SHA-256, evidence role, and `raw_or_derived` — **every row is `derived`**.
The copying script refuses any file that is not JSON or that exceeds a size ceiling, so a raw corpus
cannot enter the directory even by mistake.

`CLAIM_EVIDENCE_MATRIX.csv` now carries `release_path` and `availability` columns. **All 165 claim
rows resolve to a file a reader can open**: 50 inside the release package and 115 tracked elsewhere
in the repository. There is no remaining gap, and none is claimed where one exists.

### Licence of the derived artefacts

**CC0 1.0** — see `LICENSE-evidence`. The dedication applies **only** to these project-created
derived artefacts and confers no rights over the underlying exchange, regulatory, market-data or
publication sources.

## 4. Two reproduction paths, which must not be confused

| path | determinism | what it needs |
|---|---|---|
| **Paper regeneration** — figures, tables, LaTeX and audits from committed artefacts | **deterministic**; PNG, tables and `.tex` are byte-reproducible (figure PDFs carry a timestamp) | the pinned environment in `requirements.txt` |
| **Raw reconstruction** — rebuilding the derived artefacts from public sources | **not deterministic** | network access, and acceptance that the sources are live |

Raw reconstruction cannot be promised to reproduce the committed artefacts, for reasons already
documented in `REPRODUCIBILITY_APPENDIX.md`: venue catalogues change as new notices are published,
bot-protection responses vary by time and network location so the set of pages recorded as
`ACCESS_BLOCKED` differs between runs, and third-party price coverage changes. The committed
artefacts are the record of what the sources served when the experiments ran. **The paper's claims
are verifiable against those artefacts; they are not verifiable by re-fetching the world.**

This asymmetry is itself one of the paper's findings, and the policy states it rather than papering
over it.

## 5. If a reader wants the raw data

1. Install the pinned environment (`BUILD.md` §1).
2. Run the family's retrieval script from `scripts/` — for example `scripts/h18_1b_discover.py` for
   the delisting notice catalogue, or `scripts/h19_2_prefreeze.py` for the support audit. Each fetches
   from the public source and writes its derived artefact.
3. Compare the result against the hashes in `RELEASE_MANIFEST.json` and, for the nine artefacts in
   §3, against the hashes in `RELEASE_BLOCKERS.md`.
4. Expect differences in anything time-dependent, and read §4 before concluding that a discrepancy is
   an error.

**No API key or credential is required for any retrieval script.** The project used only public,
keyless endpoints, never bypassed bot protection, and recorded blocked pages as blocked rather than
working around them.
