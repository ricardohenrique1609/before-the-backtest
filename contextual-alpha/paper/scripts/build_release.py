"""Build the reader-facing paper.md, paper.tex and paper.pdf for Contextual Alpha.

Input: paper/manuscript.md (rendered by render_manuscript.py) and paper/references.bib.
Output, at the top of the Contextual Alpha directory, beside the stage reports:
  * paper.md  - the manuscript with citations resolved to author-year and a rendered reference list;
  * paper.tex - generated from paper.md; never edit by hand;
  * paper.pdf - typeset with the same Tectonic binary as Before the Backtest (BUILD.md there, §4).

Production only. No word of the manuscript is changed: citation keys become author-year labels, the
reference list is rendered from references.bib, and figure captions are set under their figures.
The PDF is marked as a pre-referee working draft on its title page.

The LaTeX conversion reuses the release converter of Before the Backtest
(scripts/release_md_to_tex.py) and its bibliography reader (scripts/release_refs.py), read-only. Their
mathematics table is specific to that paper, so it is switched off here, and the Unicode this
manuscript needs is added at run time. Neither file is modified.

Run from the repository root:
  .venv/Scripts/python -I "Contextual Alpha/paper/scripts/build_release.py" [--no-pdf] [--keep-log]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util

import re
import subprocess
import sys
from pathlib import Path

# reconfigure rather than rewrap: release_refs.py rewraps sys.stdout on import, and a discarded
# wrapper would close the shared buffer when it is collected
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PAPER = Path(__file__).resolve().parents[1]
CA = PAPER.parent
ROOT = CA.parent
SRC = PAPER / "manuscript.md"
BIB = PAPER / "references.bib"
OUT_MD, OUT_TEX, OUT_PDF = CA / "paper.md", CA / "paper.tex", CA / "paper.pdf"
TECTONIC = ROOT / ".tools" / "tectonic" / "tectonic.exe"

DRAFT_NOTE = ("Working-paper draft, pre-referee. Not peer-reviewed, not submitted, no DOI. "
              "Prospective confirmation pending.")
KEYWORDS = ("point-in-time data, look-ahead bias, pre-registration, cryptocurrency delisting, "
            "public context, out-of-time evaluation")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def front_matter(md: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    if not m:
        raise ValueError("manuscript.md has no front matter")
    meta = {}
    for ln in m.group(1).splitlines():
        k, v = ln.split(":", 1)
        meta[k.strip()] = v.strip().strip('"')
    return meta, md[m.end():]


def cite_labels(refs, entries: list[dict]) -> dict[str, str]:
    """Author-year label per key, from the bibliography fields only."""
    labels = {}
    for e in entries:
        author = e.get("author", "")
        if author.startswith("{") or not author:
            venue = e.get("howpublished", "")
            venue = "" if venue.startswith("http") else venue
            who = refs.clean(author or e.get("journal", "") or venue or e.get("title", ""))
        else:
            names = [refs.clean(x.strip()) for x in author.split(" and ")]
            others = "others" in names
            names = [n for n in names if n != "others"]
            surnames = [n.split(",")[0].strip() for n in names]
            if others or len(surnames) > 2:
                who = f"{surnames[0]} et al."
            elif len(surnames) == 2:
                who = f"{surnames[0]} and {surnames[1]}"
            else:
                who = surnames[0]
        labels[e["key"]] = f"{who} {e.get('year', 'n.d.')}"
    return labels


def resolve_citations(text: str, labels: dict[str, str]) -> str:
    def group(m: re.Match) -> str:
        keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
        missing = [k for k in keys if k not in labels]
        if missing:
            raise KeyError(f"citation keys not in references.bib: {missing}")
        return "(" + "; ".join(labels[k] for k in keys) + ")"
    out = re.sub(r"\[(@[^\]]+)\]", group, text)
    if "[@" in out:
        raise ValueError("unresolved citation left in the manuscript")
    return out


def reference_list(refs, entries: list[dict]) -> list[str]:
    lines = ["", "Rendered from `paper/references.bib`, the source of truth. Each entry carries the "
             "access level recorded for it in `paper/REFERENCE_VERIFICATION.md`; no metadata was "
             "inferred.", ""]
    for e in sorted(entries, key=refs.sort_key):
        lines += [f"- {refs.render_entry(e)}", ""]
    return lines


def build_md(meta: dict, body: str, labels: dict[str, str], refs_lines: list[str]) -> str:
    body = resolve_citations(body, labels)
    # the reference list goes at the end of the References section, before the appendices
    head, sep, tail = body.partition("\n## Appendix A.")
    if not sep:
        raise ValueError("manuscript.md has no Appendix A heading")
    body = head.rstrip("\n") + "\n" + "\n".join(refs_lines).rstrip() + "\n\n" + sep.lstrip("\n") + tail
    # figures live in paper/figures; paper.md sits one level up
    body = body.replace("](figures/", "](paper/figures/")
    byline = [f"# {meta['title']}", "", f"*{meta['subtitle']}*", "", f"**{meta['author']}**", "",
              f"*{meta['affiliation']}*", "", meta["date"], "", f"> **Status.** {DRAFT_NOTE}", ""]
    return "\n".join(byline) + body.lstrip("\n")


NESTED_RE = re.compile(r"^ {2,}[-*]\s+(.*)$")
SUB = ""


def _expand_sub(m: re.Match) -> str:
    parent, *children = m.group(1).split(SUB)
    if not children:
        return parent
    return (parent + "\n\\begin{itemize}\n" + "\n".join(r"\item " + c.strip() for c in children)
            + "\n\\end{itemize}")


def build_tex(rel, base, meta: dict, paper_md: str) -> str:
    rel._MATH_RE = []  # Before the Backtest's mathematics table does not apply to this manuscript
    base.UNICODE.update({
        "\u03bb": r"$\lambda$", "\u03b2": r"$\beta$", "\u03a3": r"$\Sigma$",
        "\u2260": r"$\neq$", "\u2016": r"$\Vert$", "\u00bd": r"$\tfrac{1}{2}$", "\u00b2": r"$^{2}$",
    })
    lines = paper_md.split("\n")
    # subtitle and status are set by the title page below, not by the body
    drop = {f"*{meta['subtitle']}*", f"> **Status.** {DRAFT_NOTE}"}
    lines = [ln for ln in lines if ln not in drop]
    # an image line becomes the image plus its caption, set under it. The converter has no nested
    # lists, so a sub-bullet is folded into its parent item behind a marker and expanded into an
    # inner itemize after conversion; otherwise sub-items would print as siblings of their parent.
    md_lines: list[str] = []
    in_sub = False
    for ln in lines:
        m = rel.IMAGE_RE.match(ln)
        sub = NESTED_RE.match(ln)
        if m:
            path = re.sub(r"\.png$", ".pdf", m.group(2))
            md_lines += [f"![]({path})", "", f"*{m.group(1)}*", ""]
            in_sub = False
        elif sub and md_lines and md_lines[-1].strip():
            md_lines[-1] += SUB + sub.group(1)
            in_sub = True
        elif in_sub and ln.startswith("    ") and ln.strip():
            md_lines[-1] += " " + ln.strip()
        else:
            md_lines.append(ln)
            in_sub = False
    tex = rel.convert("\n".join(md_lines), date=meta["date"], title=meta["title"],
                      author=meta["author"], keywords=KEYWORDS,
                      subject="Working paper (draft)", affiliation=meta["affiliation"])
    tex = re.sub(r"(?m)^(\\item .*)$", _expand_sub, tex)
    if SUB in tex:
        raise ValueError("a nested-list marker survived outside a list item")
    # long identifiers (file names, block names) may break after an underscore; loose lines are
    # preferred to text running into the margin
    tex = tex.replace(r"\_", r"\_\allowbreak{}")
    tex = re.sub(r"https?://[^\s}]+", lambda m: m.group(0).replace("/", r"/\allowbreak{}"), tex)
    # the converter sizes columns to 93% of the line but ignores the gaps between them, which
    # pushes the widest (scriptsize) tables into the margin; tighter gaps keep them inside it
    tex = tex.replace("\\scriptsize\n\\setlength{\\tabcolsep}{4pt}", "\\scriptsize\n\\setlength{\\tabcolsep}{1.5pt}")
    # justified narrow cells stretch their words apart; table cells are set ragged-right
    tex = re.sub(r"(?m)^(\\begin\{(?:tabular|longtable)\}\{)(.*)\}$",
                 lambda m: m.group(1) + m.group(2).replace(
                     "p{", r">{\raggedright\arraybackslash}p{") + "}", tex)
    tex = tex.replace("\\usepackage{longtable}", "\\usepackage{longtable}\n\\usepackage{array}", 1)
    tex = tex.replace("\\begin{document}", "\\emergencystretch=3em\n\\begin{document}", 1)
    tex = tex.replace("%% Generated from paper.md by scripts/release_md_to_tex.py",
                      "%% Generated from paper.md by Contextual Alpha/paper/scripts/build_release.py")
    title_tex = base.inline(meta["title"])
    tex = tex.replace("\\title{" + title_tex + "}",
                      "\\title{" + title_tex + "\\\\[6pt]\\large " + base.inline(meta["subtitle"]) + "}")
    tex = tex.replace("\\maketitle\n",
                      "\\maketitle\n\\begin{center}\\fbox{\\parbox{0.9\\linewidth}{\\centering\\small "
                      + base.inline(DRAFT_NOTE) + "}}\\end{center}\n", 1)
    leftover = sorted({ch for ch in tex if ord(ch) > 127})
    if leftover:
        raise ValueError(f"unmapped non-ASCII characters in paper.tex: {leftover}")
    return tex


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--keep-log", action="store_true")
    args = ap.parse_args()

    refs = _load("release_refs", ROOT / "scripts" / "release_refs.py")
    rel = _load("release_md_to_tex", ROOT / "scripts" / "release_md_to_tex.py")
    base = rel.base

    bib = re.sub(r"\\url\{([^}]*)\}", r"\1", BIB.read_text(encoding="utf-8"))
    entries = refs.parse_bib(bib)
    labels = cite_labels(refs, entries)
    meta, body = front_matter(SRC.read_text(encoding="utf-8"))

    paper_md = build_md(meta, body, labels, reference_list(refs, entries))
    OUT_MD.write_text(paper_md, encoding="utf-8", newline="\n")
    tex = build_tex(rel, base, meta, paper_md)
    OUT_TEX.write_text(tex, encoding="utf-8", newline="\n")
    print(f"paper.md {len(paper_md):,} chars | paper.tex {len(tex):,} chars | "
          f"{len(entries)} references, {len(set(re.findall(r'@([\w-]+)', body)))} cited keys")

    if args.no_pdf:
        return
    if not TECTONIC.exists():
        sys.exit(f"Tectonic not found at {TECTONIC}; see Before the Backtest BUILD.md §4.1")
    res = subprocess.run([str(TECTONIC), "-X", "compile", OUT_TEX.name], cwd=CA,
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = res.stdout + res.stderr
    if args.keep_log:  # build logs are not tracked; write one only on request
        (PAPER / "_tectonic.log").write_text(log, encoding="utf-8", newline="\n")
    if res.returncode != 0:
        print(log[-3000:])
        sys.exit(f"tectonic exit {res.returncode}")
    overfull_v = len(re.findall(r"Overfull \\vbox", log))
    overfull_h = [float(x) for x in re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide", log)]
    digest = hashlib.sha256(OUT_PDF.read_bytes()).hexdigest()
    print(f"paper.pdf {OUT_PDF.stat().st_size:,} bytes | sha256 {digest}")
    print(f"overfull vbox {overfull_v} | overfull hbox {len(overfull_h)}"
          + (f" (max {max(overfull_h):.1f}pt)" if overfull_h else ""))


if __name__ == "__main__":
    main()
