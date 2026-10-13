# PAPER V1 — FREEZE RECORD

> **Paper V1 is frozen before the referee attack. Subsequent changes belong to V2 and may not
> silently overwrite V1's claims or interpretation.**

Any V2 revision that changes a claim, a number, a verdict label or an interpretation must say so
explicitly and must be traceable against the hashes below. A V2 that quietly rewrites a V1 sentence
is the same failure mode this paper documents, applied to the paper itself.

---

## 1. Identity

| | |
|---|---|
| title | Falsification-First Alpha Discovery: How Data Construction, Survivorship, Semantic Errors and Execution Constraints Manufacture Trading Strategies |
| version | **V1** |
| frozen | **2026-10-11** |
| repository | `C:\Projetos\Quant Intelligence`, branch `main` |
| commit at freeze | **`52a980a`** (`paper: pre-freeze housekeeping and a committed audit script`) |
| directory | `papers/falsification_first_alpha_discovery/` |

## 2. SHA-256

Computed over the exact bytes of each file at commit `52a980a`.

| file | SHA-256 | bytes |
|---|---|---|
| `paper.md` | `1853bce01e638da159733ab61fd3d4945ba51a160d3ddc156ab26fa57da95cef` | 64,682 |
| `paper.tex` | `2abad0f88b468ea542ef32d838539c7c29b8d5683a907f96cb56b2328d0d97e7` | 68,404 |
| `CLAIM_EVIDENCE_MATRIX.csv` | `a1b97453ada9f3397f317f6b3e15d720ff5791c60896e37fea0539d8e98cb781` | 29,268 |
| `PAPER_QA.md` | `357c25b9490e109d08af8092f1b0079ab91529b1b21cf26e60d206eaef8fe9be` | 12,476 |
| `REPRODUCIBILITY_APPENDIX.md` | `6ea8edaa0a94f9c989f206229ac386b47c548cbd61938a08ef70e291c72adcff` | 12,906 |

Verify with:

```bash
cd papers/falsification_first_alpha_discovery && sha256sum paper.md paper.tex CLAIM_EVIDENCE_MATRIX.csv PAPER_QA.md REPRODUCIBILITY_APPENDIX.md
```

## 3. Contents at freeze

| | |
|---|---|
| manuscript word count (body, excluding the figure and table apparatus) | **9,394** |
| manuscript word count (whole file) | 9,753 |
| sections | 12 |
| figures | **6** (PNG and PDF, all embedded in the manuscript) |
| tables | **5** |
| references | **14** (4 full text, 7 abstract or metadata only, 2 PDF level, 1 access level not recorded) |
| claim–evidence rows | **126** (110 `VERIFIED`, 16 `ARTEFACT_CITED`) |
| open questions | **12** (Q1 and Q3/Q9 resolved; the rest are genuine gaps) |
| experiment families covered | 17 (H13 to H19.2), with H1–H12 as registry only |

## 4. QA status at freeze

All four audits re-run at this commit by `scripts/paper_audit.py`, which reads only the manuscript
and its evidence files.

```
[claim]       distinct numeric tokens 252 | unsupported 0
[status]      expected labels 6 | failures 0
[language]    prove=1, proven=1, never=13, insider=3, profitab=1, alpha=4, demonstrat=4
[consistency] checks 7 | failures 0
RESULT: PASS (0 issues)
```

| target | state |
|---|---|
| unsupported numerical claims | **0** |
| H18.3 | **`PRE-REGISTERED NULL`** — tested; the data and design survived |
| H19.0 | **`PARTIAL PASS`** — execution substrate strong, small-capital thesis fails the sample and liquidity gate; no return computed |
| H19.2 | **`BLOCKED BEFORE FREEZE / IDENTIFICATION FAIL`** — never called null or rejected; no price ever read |
| H14 parent | **`OPEN`** — not an economic null |
| H13 economic hypothesis | **unresolved** — only the implementation was rejected |

## 5. Reproduction check performed at freeze

Re-running the three generators at this commit reproduced every table, every PNG and `paper.tex`
**byte for byte**. Only the six figure PDFs differ, because matplotlib writes a creation timestamp
into the PDF metadata. This is recorded so a future reader can tell a real content change from a
timestamp change.

```bash
.venv/Scripts/python -I scripts/paper_build_tables.py
.venv/Scripts/python -I scripts/paper_build_figures.py
.venv/Scripts/python -I scripts/paper_md_to_tex.py
.venv/Scripts/python -I scripts/paper_audit.py
```

## 6. What was not done

- No experiment was run, and no hypothesis was opened, during the writing or freezing of V1.
- No return, P&L or economic quantity was computed.
- No price column was loaded for H19.2, before or after the freeze.
- No gate, verdict, pre-registration or experiment artefact was altered.
- No open question was resolved by computation.
- No PDF was built: neither `pandoc` nor a LaTeX distribution is present in this environment, so
  `paper.tex` has never been compiled. This is stated rather than implied.

## 7. Paper commit history to the freeze

| commit | content |
|---|---|
| `1148352` | architecture and evidence map |
| `8c816c5` | the five tables, generated from artefacts by a committed script |
| `59d204a` | draft manuscript |
| `ba1642d` | figures, bibliography and reproducibility appendix |
| `f17d3e7` | evidence and language audit |
| `813228d` | embed the six figures in the manuscript |
| **`52a980a`** | **pre-freeze housekeeping and a committed audit script — the freeze point** |

## 8. What follows the freeze

A hostile referee report (`REFEREE_REPORT_V1.md`), an author response
(`AUTHOR_RESPONSE_V1.md`) and a revision plan (`PAPER_REVISION_PLAN_V2.md`). Those documents may
criticise V1 freely; they may not edit it. Changes agreed there land in V2, against these hashes.
