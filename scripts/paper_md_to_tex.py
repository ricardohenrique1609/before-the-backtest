"""Generate paper.tex from paper.md.

paper.md is canonical prose. This converter exists so the LaTeX version cannot drift from it: any
change to the manuscript is made in the Markdown and the .tex is regenerated.

It is a deliberately small converter covering exactly the constructs the manuscript uses -
headings, paragraphs, emphasis, inline code, block quotes, bullet and numbered lists, horizontal
rules and pipe tables. It is not a general Markdown implementation.

Run: .venv/Scripts/python -I scripts/paper_md_to_tex.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "falsification_first_alpha_discovery"
SRC = PAPER / "paper.md"
DST = PAPER / "paper.tex"

UNICODE = {
    "Δ": r"$\Delta$",
    "−": "$-$",
    "≤": r"$\leq$",
    "≥": r"$\geq$",
    "×": r"$\times$",
    "≈": r"$\approx$",
    "±": r"$\pm$",
    "—": "---",
    "–": "--",
    "’": "'",
    "‘": "`",
    "“": "``",
    "”": "''",
    "Ⓢ": r"\textcircled{\scriptsize S}",
    "§": r"\S{}",
    "→": r"$\rightarrow$",
    "…": r"\ldots{}",
    " ": "~",
}

SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
ITAL = re.compile(r"(?<!\*)\*([^*]+?)\*(?!\*)")


def esc(text: str) -> str:
    out = []
    for ch in text:
        out.append(SPECIALS.get(ch, UNICODE.get(ch, ch)))
    return "".join(out)


def inline(text: str) -> str:
    """Escape, then apply the three inline markups, protecting code spans first."""
    spans: list[str] = []

    def stash(m: re.Match) -> str:
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = CODE.sub(stash, text)
    text = esc(text)
    text = BOLD.sub(lambda m: r"\textbf{" + m.group(1) + "}", text)
    text = ITAL.sub(lambda m: r"\emph{" + m.group(1) + "}", text)
    for i, raw in enumerate(spans):
        text = text.replace(f"\x00{i}\x00", r"\texttt{" + esc(raw) + "}")
    return text


def table(block: list[str]) -> list[str]:
    rows = []
    for line in block:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    header, body = rows[0], rows[2:]
    ncol = len(header)
    spec = "p{" + f"{0.92 / ncol:.3f}" + r"\linewidth}"
    out = [r"\begin{center}", r"\footnotesize",
           r"\begin{tabular}{" + spec * ncol + "}", r"\hline"]
    out.append(" & ".join(r"\textbf{" + inline(c) + "}" for c in header) + r" \\")
    out.append(r"\hline")
    for r in body:
        r = (r + [""] * ncol)[:ncol]
        out.append(" & ".join(inline(c) for c in r) + r" \\")
    out += [r"\hline", r"\end{tabular}", r"\end{center}", ""]
    return out


PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=2.5cm]{geometry}
\usepackage{graphicx}
\usepackage{microtype}
\usepackage{csquotes}
\usepackage[hidelinks]{hyperref}
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0pt}

%% Generated from paper.md by scripts/paper_md_to_tex.py - do not edit by hand.
%% Edit paper.md and regenerate, so the two versions cannot diverge.

"""


def convert(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    title = ""
    i = 0
    in_list: str | None = None

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append(r"\end{" + in_list + "}")
            in_list = None

    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("|") and i + 1 < len(lines) and set(lines[i + 1].replace("|", "")
                                                               .strip()) <= set("-: "):
            close_list()
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            out += table(block)
            continue

        m = IMAGE.match(line)
        if m:
            close_list()
            out.append(r"\begin{center}")
            out.append(r"\includegraphics[width=\linewidth]{" + m.group(2) + "}")
            out.append(r"\end{center}")
            out.append("")
            i += 1
            continue

        if line.startswith("> "):
            close_list()
            quote = []
            while i < len(lines) and (lines[i].startswith(">")):
                quote.append(lines[i].lstrip(">").strip())
                i += 1
            out.append(r"\begin{quote}")
            out.append(inline(" ".join(q for q in quote if q)))
            out.append(r"\end{quote}")
            out.append("")
            continue

        if line.startswith("# "):
            close_list()
            title = inline(line[2:].strip())
            i += 1
            continue
        if line.startswith("## "):
            close_list()
            out.append(r"\section*{" + inline(line[3:].strip()) + "}")
            out.append("")
            i += 1
            continue
        if line.startswith("### "):
            close_list()
            out.append(r"\subsection*{" + inline(line[4:].strip()) + "}")
            out.append("")
            i += 1
            continue

        if line.strip() in ("---", "***", "___"):
            close_list()
            i += 1
            continue

        m = re.match(r"^(\s*)-\s+(.*)$", line)
        if m:
            if in_list != "itemize":
                close_list()
                out.append(r"\begin{itemize}")
                in_list = "itemize"
            out.append(r"\item " + inline(m.group(2)))
            i += 1
            continue

        m = re.match(r"^(\s*)\d+\.\s+(.*)$", line)
        if m:
            if in_list != "enumerate":
                close_list()
                out.append(r"\begin{enumerate}")
                in_list = "enumerate"
            out.append(r"\item " + inline(m.group(2)))
            i += 1
            continue

        if not line.strip():
            close_list()
            out.append("")
            i += 1
            continue

        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{1,6} |\||> |\s*-\s+|\s*\d+\.\s+|---$)", lines[i]):
            para.append(lines[i].rstrip())
            i += 1
        close_list()
        out.append(inline(" ".join(para)))
        out.append("")

    close_list()
    head = PREAMBLE + r"\title{" + title + "}\n" + r"\date{2026-10-11}" + "\n"
    head += r"\author{}" + "\n\\begin{document}\n\\maketitle\n\n"
    return head + "\n".join(out) + "\n\\end{document}\n"


def main() -> None:
    DST.write_text(convert(SRC.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"wrote {DST.relative_to(ROOT)} ({DST.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
