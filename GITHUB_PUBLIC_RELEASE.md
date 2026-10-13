# GITHUB PUBLIC RELEASE — v1.0.0

**State: `PUBLIC_REPO_READY_FOR_PUSH`.**

The paper-only package is built, audited, committed to a clean local history and tagged `v1.0.0`.
**No GitHub repository was created, nothing was pushed, and no release was published.**

---

## 1. Why it stopped here

Publishing requires GitHub authentication, and none exists in this environment:

| checked | result |
|---|---|
| `gh` CLI on PATH | **not installed** |
| git remote on the research repository | **none configured** |
| `~/.config/gh/hosts.yml` | **absent** |
| `GH_TOKEN` / `GITHUB_TOKEN` in the environment | **not set** |
| git credential helper | `manager` — present, but holds no credential for this purpose |

**No credential was improvised and no weaker route was taken.** Nothing was pasted into source,
written to disk or printed to a log, and no token was requested. An unauthenticated push, a
credential committed to make one work, or a public repository created through any side channel would
each be a worse outcome than stopping, and the stop is recorded rather than worked around.

This is blocker **B3a**, open. It is the only thing between this package and publication.

## 2. What is ready

| | |
|---|---|
| local repository | `public/before-the-backtest/` |
| branch | `main` |
| commits | 1 — a clean initial history; the research repository's history is **not** exported |
| commit identity | `Ricardo H. Ramos Silva <noreply@github.com>` — see below |
| tag | **`v1.0.0`**, annotated |
| files | **186**, all tracked — nothing excluded by `.gitignore` |
| size | 4.6 MB |
| audits | `PUBLIC_REPO_FINAL_AUDIT.md` — 11 checks, **0 findings**; 0 broken links; 94 frozen files byte-identical |

The intended repository:

| field | value |
|---|---|
| name | **`before-the-backtest`** |
| visibility | **public** |
| description | Pre-freeze common-support ceilings for event-driven strategy research — a working paper and its complete evidence trail |
| topics | `research-methods`, `causal-inference`, `common-support`, `event-study`, `reproducibility`, `pre-registration` |
| licences | MIT (code) · CC BY 4.0 (manuscript) · CC0 1.0 (derived evidence) |

### The commit identity

The commit does **not** carry the author's personal address. The global git identity on this machine
is a personal name variant and a personal email, and a commit author address is public forever once
pushed, so the local configuration was overridden with the canonical byline and GitHub's own
`noreply@github.com`.

If the commit should be attributed to the author's GitHub account, set the account's own private
address and re-create the single commit **before pushing**:

```bash
git config --local user.email "ID+USERNAME@users.noreply.github.com"
git commit --amend --reset-author --no-edit
git tag -f -a v1.0.0 -m "$(git tag -l --format='%(contents)' v1.0.0)"
```

The address is shown on GitHub under Settings → Emails → *Keep my email addresses private*. Doing
nothing is also valid: the commit stands under the published byline either way.

## 3. The exact minimal action required

One of the two, performed by the author. Nothing else about the package changes.

**Either** install the GitHub CLI and authenticate it interactively, so the credential is stored by
the CLI's own keyring and never passes through this project:

```bash
winget install --id GitHub.cli
gh auth login          # choose HTTPS, authenticate in the browser
```

**or** create the empty public repository `before-the-backtest` in the GitHub web interface and add
it as a remote, letting the existing `manager` credential helper handle the push.

### Then, from `public/before-the-backtest/`

```bash
gh repo create before-the-backtest --public --source=. --remote=origin --push
git push origin v1.0.0
```

Without the CLI, the equivalent is:

```bash
git remote add origin https://github.com/<owner>/before-the-backtest.git
git push -u origin main
git push origin v1.0.0
```

### The release

Title **`Before the Backtest — v1.0.0`**, with `paper.pdf` attached:

```bash
gh release create v1.0.0 paper.pdf --title "Before the Backtest — v1.0.0" --notes-file RELEASE_NOTES.md
```

`RELEASE_NOTES.md` is in the package. In the web interface: Releases → Draft a new release → tag
`v1.0.0` → attach `paper.pdf` → paste the notes.

## 4. After the push

Three things become true and should be recorded:

1. **B3a closes.** Update `RELEASE_BLOCKERS.md`, this file and `RELEASE_v1.0.0_FREEZE.md`.
2. `CITATION.cff` carries `repository-code: "https://github.com/<owner>/before-the-backtest"`; the
   `<owner>` placeholder is the one field that cannot be filled before the repository exists.
3. The README's citation line can name the repository. **The `doi` field stays unset** — see below.

## 5. What must not be done

The author authorised publication of a public repository and a tagged release, and **nothing
further**. Not authorised, and not performed:

- **no DOI** of any kind;
- **no Zenodo deposition** — `zenodo.json` is prepared metadata, not a deposition, and nothing was
  uploaded;
- **no SSRN**, **no arXiv**, no other preprint server;
- **no journal submission**.

Each is an irreversible external action requiring explicit approval for that specific action. This is
blocker **B3b**, open by decision, with the consequence stated plainly in `RELEASE_BLOCKERS.md`: a
GitHub tag is not an archival identifier, and a repository can be renamed, made private or deleted.

## 6. What the release claims

The paper, one procedure and one demonstration of it. It claims **no** profitability, **no**
identified economic effect, **no** external peer review, **no** institutional endorsement and **no**
independent replication. The byline states **Ricardo H. Ramos Silva, Independent Researcher** — no
employer, no university, no ORCID, no correspondence address.
