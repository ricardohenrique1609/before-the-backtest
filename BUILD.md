# BUILD

How to regenerate every release artefact, and what is required to typeset the PDF.

---

## 1. Environment

| | |
|---|---|
| Python | **3.12.14** |
| packages | pinned in `requirements.txt` |
| platform used | Windows 11 (10.0.26200); the build is platform-independent |
| invocation | `.venv/Scripts/python -I` — isolated mode, ignoring the user site directory and the current directory on `sys.path` |

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r papers/falsification_first_alpha_discovery/release/requirements.txt
```

`scikit-learn` and `statsmodels` are deliberately absent. The historical estimators are implemented
directly in numpy and scipy and are inspectable in `scripts/h18_3_*.py`.

## 2. Regenerate the release package

Run from the repository root, in this order:

```bash
.venv/Scripts/python -I scripts/paper_audit_v4.py    # 1. verify all 16 frozen V1-V3 hashes, then audit V4
.venv/Scripts/python -I scripts/release_build.py     # 2. Figure 4 layout + release/paper.tex
.venv/Scripts/python -I scripts/release_audit.py     # 3. freeze quantities, claims, cross-refs, LaTeX, BibTeX, manifest
```

Expected outputs:

| step | result |
|---|---|
| 1 | `[freezes] V1+V2+V3 files 16 \| changed 0` … `RESULT: PASS (0 issues)` |
| 2 | `release/figures/f4_full_pool_ceiling.{png,pdf}` and `release/paper.tex` |
| 3 | `RESULT: PASS (0 issues)` and a rewritten `release/RELEASE_MANIFEST.json` |

If step 1 reports a changed hash it exits with status **2** and nothing else runs. That is the
intended behaviour: a frozen version has been modified and the release is invalid until that is
explained.

**Determinism.** Steps 1 and 3 are fully deterministic. In step 2 the PNG and the LaTeX are
byte-reproducible; the figure **PDF** is not, because matplotlib writes a creation timestamp into PDF
metadata. `RELEASE_MANIFEST.json` therefore changes on every run in its `built_utc` field and in the
hash of `figures/*.pdf`. Compare the `.png` hashes, not the `.pdf` hashes, when checking for content
drift.

## 3. Regenerating earlier versions

Each frozen version has its own builder and auditor, retained so that any version can be rebuilt
from the artefacts as it stood:

```bash
.venv/Scripts/python -I scripts/paper_build_tables.py    # V1 tables
.venv/Scripts/python -I scripts/paper_build_figures.py   # V1 figures
.venv/Scripts/python -I scripts/paper_md_to_tex.py       # V1 LaTeX
.venv/Scripts/python -I scripts/paper_build_v2.py        # V2
.venv/Scripts/python -I scripts/paper_build_v3.py        # V3
.venv/Scripts/python -I scripts/paper_build_v4.py        # V4
.venv/Scripts/python -I scripts/paper_audit.py           # V1 audits
.venv/Scripts/python -I scripts/paper_audit_v2.py        # V2 audits + V1 integrity
.venv/Scripts/python -I scripts/paper_audit_v3.py        # V3 audits + V1-V2 integrity
.venv/Scripts/python -I scripts/paper_audit_v4.py        # V4 audits + V1-V3 integrity
```

`paper.tex` is **generated** from `paper.md` by `scripts/paper_md_to_tex.py` in every version. Never
hand-edit a `.tex`: edit the Markdown and regenerate, so the two cannot diverge.

## 4. Typesetting the PDF

The PDF is built, and this section records exactly how.

### 4.1 Toolchain

| | |
|---|---|
| engine | **Tectonic 0.17.0** |
| source | the project's official GitHub release, `tectonic-typesetting/tectonic`, asset `tectonic-0.17.0-x86_64-pc-windows-msvc.zip` |
| verification | SHA-256 of the downloaded archive `f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f`, **matched against the digest published in the release metadata before the binary was run** |
| install method | archive extracted to `.tools/tectonic/`; **no system-wide installation**, no package manager, no PATH change |
| bibliography engine | **none needed** — the document has no `\cite`; references are discussed in prose and listed in `references.bib` |
| package fetch | Tectonic downloads the TeX packages the document needs on first run and caches them; a first build therefore requires network access, later builds do not |

Tectonic was chosen because it installs as a single verified binary and fetches only what the
document uses. **No other typesetting tooling was installed.**

### 4.2 Build command

```bash
cd papers/falsification_first_alpha_discovery/release
../../../.tools/tectonic/tectonic.exe -X compile paper.tex
```

Tectonic runs the engine as many times as the cross-references require, so no second pass is needed.

### 4.3 Build record

| | |
|---|---|
| build date | 2026-10-12 |
| exit code | **0** |
| output | `paper.pdf` |
| **pages** | **21** |
| bytes | 577,844 |
| **SHA-256** | `ab58cdecd8b4b52b2fac2879184b535a09cbf695f011556d70de3edeab20e45e` |
| packages used | `inputenc`, `fontenc`, `lmodern`, `geometry`, `graphicx`, `longtable`, `microtype`, `csquotes`, `hyperref` |
| package substitutions | **none** |
| warnings | underfull and overfull horizontal boxes in the widest tables, all below 21pt; **no overfull vertical box**, so no content overflows a page |

`Fontconfig error: Cannot load default config file` appears on Windows and is benign: Tectonic falls
back to its bundled font configuration and the output is unaffected.

### 4.4 Layout changes made to achieve this build — all PRODUCTION

No textual or scientific change was made for the compiler. Three typesetting changes were needed, and
each is confined to the release converter `scripts/release_md_to_tex.py`, which exists precisely so
that regenerating the frozen V1-V4 `.tex` files stays byte-exact:

| # | problem in the first build | fix | class |
|---|---|---|---|
| 1 | the 31-row registry table overflowed the page bottom (`Overfull box` 437.9pt) and the right margin, colliding with the page number | tables longer than 12 rows render as `longtable` and break across pages | PRODUCTION |
| 2 | equal column widths squeezed narrow columns, so `#` and `family` cells ran together | column widths are proportional to content under square-root weighting, with a 5.5% floor, and the font scales with the column count | PRODUCTION |
| 3 | `N\*` in the Markdown emitted a literal backslash and left a bare `*` that opened an italic span — visible as "N\ = 10" in the first build | Markdown backslash escapes are interpreted before the emphasis pass | PRODUCTION |

Two further corrections were made to the manuscript text itself, both factual rather than
typographic, and both recorded in `CHANGELOG.md`: the cover date was wrong (2026-10-11), and the
data-availability section still said the manuscript had never been typeset, which this build
falsified.

### 4.5 Visual QA

`PDF_QA.md` records the page-by-page inspection of all 21 pages. **Compilation exiting zero was not
treated as sufficient.**
