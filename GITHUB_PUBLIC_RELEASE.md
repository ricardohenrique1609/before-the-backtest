# GITHUB PUBLIC RELEASE — v1.0.0

**State: PUBLISHED.**

| | |
|---|---|
| repository | <https://github.com/ricardohenrique1609/before-the-backtest> |
| release | <https://github.com/ricardohenrique1609/before-the-backtest/releases/tag/v1.0.0> |
| published commit | `9aaaa6da992c34d33127f0c6c7d78eb408b78d3b` |
| tag | `v1.0.0`, annotated, pointing at that commit |
| visibility | **public** |
| default branch | `main` |
| release asset | `paper.pdf`, 612,592 bytes, SHA-256 `85a87a47…` |
| release state | published — not a draft, not a pre-release |

---

## 1. What was published

| | |
|---|---|
| files | **186**, all tracked |
| size | 4.6 MB |
| commits | **1** — a clean initial history; the research repository's history is **not** exported |
| commit author | `Ricardo H. Ramos Silva <125686216+ricardohenrique1609@users.noreply.github.com>` |
| topics | `research-methods`, `causal-inference`, `common-support`, `event-study`, `reproducibility`, `pre-registration` |
| licences | MIT (code) · CC BY 4.0 (manuscript) · CC0 1.0 (derived evidence) |

The repository is the paper and its evidence trail: the manuscript as Markdown, LaTeX and a 24-page
PDF; four figures and nine tables; nine derived evidence artefacts with a 165-row claim-evidence
matrix in which every row resolves to a file a reader can open; 22 audited scripts; the four reviewed
versions with their referee reports; and the 31-entry research registry that supplies the paper's
denominator.

GitHub reports no detected licence because the package carries **three**, each scoped to a different
component. That is deliberate and is stated in `README.md`, in `LICENSE_DECISION.md` and in each
licence file.

## 2. Checks performed before the push

| check | result |
|---|---|
| working tree clean, 186 of 186 files tracked | ✔ |
| `scripts/release_public_audit.py` on the exact published directory | **11 checks, 0 findings** |
| frozen V1–V4 files byte-identical to the accepted versions | **94 of 94** |
| relative Markdown links resolving | **0 broken** |
| no published file excluded by `.gitignore` | ✔ |
| `paper.pdf` hash local vs published release asset | **identical** — `85a87a47…` |

## 3. The commit identity

The commit does **not** carry the author's personal address. The machine's global git identity is a
personal name variant and a personal email, and a commit author address is public forever once
pushed, so the **local** configuration of this repository alone was set to the canonical byline and
to the account's GitHub private address:

```
user.name   Ricardo H. Ramos Silva
user.email  125686216+ricardohenrique1609@users.noreply.github.com
```

**The global git configuration was not modified.**

## 4. Credential handling

Publication used a GitHub CLI that was already authenticated, with its token held in the OS keyring.

**No credential was seen, requested, improvised, written to disk, pasted into source or printed to a
log**, and none appears anywhere in the published package — the audit's token checks return zero. No
credential exists in this project at all: every retrieval in this work uses public, keyless
endpoints.

## 5. What was not done, and is not authorised

- **no DOI** of any kind;
- **no Zenodo deposition** — `zenodo.json` is prepared metadata, not a deposition, and nothing was
  uploaded;
- **no SSRN**, **no arXiv**, no other preprint server;
- **no journal submission**.

Each is an irreversible external action requiring explicit approval for that specific action. This is
blocker **B3b**, open by decision, with the consequence stated plainly: a GitHub tag is not an
archival identifier, and a repository can be renamed, made private or deleted.

## 6. What the release claims

The paper, one procedure and one demonstration of it. It claims **no** profitability, **no**
identified economic effect, **no** external peer review, **no** journal acceptance, **no**
institutional endorsement and **no** independent replication. The four referee reports in `versions/`
are this project's own hostile-review process, and every document that mentions them says so.

The byline is **Ricardo H. Ramos Silva, Independent Researcher** — no employer, no university, no
ORCID, no correspondence address, no location.

## 7. One known imperfection in the tagged tree

`v1.0.0` was tagged before the repository existed, so the tree at that tag still carries
`repository-code: "https://github.com/<owner>/before-the-backtest"` in `CITATION.cff`, and the
documents in it describe the package as ready to push rather than published. The owner could not be
known before the repository was created.

A later commit on `main` fills in the real URL and records the publication. **The tag was not moved**:
re-pointing a published tag would break the one guarantee a tag is for. Readers who clone the default
branch get the corrected metadata; readers who check out `v1.0.0` get the exact tree whose hashes
`RELEASE_v1.0.0_FREEZE.md` asserts.
