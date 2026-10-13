"""Release-only Markdown to LaTeX converter, publication grade.

Separate from scripts/paper_md_to_tex.py by design: the V1-V4 `.tex` files are frozen and must keep
regenerating byte-exactly, so the historical converter is never modified. This one owns the whole
conversion loop so that it can get right the things the historical converter degrades:

  * **inline mathematics** - identifiers and expressions render as mathematics, not as literal text
    with underscores;
  * **numbered lists with continuation lines** - an item that wraps onto an indented line stays one
    item, instead of closing the list and restarting the numbering at 1;
  * **block quotes containing lists** - the list survives inside the quote;
  * **long tables** - break across pages, with column widths proportional to content;
  * **Markdown backslash escapes** - `N\\*` is a literal asterisk, not the start of an emphasis span;
  * **Unicode** - mathematical symbols become LaTeX commands rather than being dropped.

Nothing here changes any word of the manuscript. Production only.

Run via scripts/release_build.py. Regression tests: scripts/test_release_converter.py
"""

from __future__ import annotations

import importlib.util
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("base", ROOT / "scripts" / "paper_md_to_tex.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

# --------------------------------------------------------------------------------------
# Unicode the historical converter does not map. Added here, not there, so frozen
# regeneration stays byte-identical.
# --------------------------------------------------------------------------------------
base.UNICODE.update({
    "\u2194": r"$\leftrightarrow$",
    "\u2191": r"$\uparrow$",
    "\u2193": r"$\downarrow$",
    "\u2208": r"$\in$",
    "\u2211": r"$\sum$",
    "\u2032": r"$'$",
    "\u00d7": r"$\times$",
    # Accented letters in cited authors' names. Emitted as LaTeX accent commands rather than left
    # as raw bytes: a character the engine's font does not carry is dropped silently, which
    # misspells the name. "B\u0119dowska-S\u00f3jka" printed as "Bdowska-S\u00f3jka" in an earlier build.
    "\u0119": r"\k{e}", "\u0105": r"\k{a}",
    "\u00f3": r"\'{o}", "\u00f6": r'\"{o}', "\u00fc": r'\"{u}', "\u00e4": r'\"{a}',
    "\u00e1": r"\'{a}", "\u00e9": r"\'{e}", "\u00ed": r"\'{i}", "\u00fa": r"\'{u}",
    "\u00e0": r"\`{a}", "\u00e8": r"\`{e}",
    "\u00e7": r"\c{c}", "\u00f1": r"\~{n}", "\u00e3": r"\~{a}", "\u00f5": r"\~{o}",
    "\u0161": r"\v{s}", "\u010d": r"\v{c}", "\u017c": r"\.{z}", "\u0142": r"\l{}",
})

SENTINEL = "\ue000"
_slots: list[str] = []


def _protect(latex: str) -> str:
    """Park a finished LaTeX fragment so escaping and emphasis cannot touch it."""
    _slots.append(latex)
    return SENTINEL + chr(0xE100 + len(_slots) - 1) + SENTINEL


def _restore(text: str) -> str:
    for i, latex in enumerate(_slots):
        text = text.replace(SENTINEL + chr(0xE100 + i) + SENTINEL, latex)
    return text


# --------------------------------------------------------------------------------------
# Mathematics. Ordered longest-first: a whole expression must match before its parts do.
# Each pattern may appear in the Markdown bare, inside `code spans`, or inside **bold**.
# --------------------------------------------------------------------------------------
MATH: list[tuple[str, str]] = [
    # whole expressions
    (r"S_e\s*=\s*\|\{\s*c\s*\u2208\s*C\(t_e\)\s*:\s*M\(e,\s*c,\s*t_e\)\s*=\s*1\s*\}\|",
     r"S_e = \bigl|\{\, c \in C(t_e) : M(e,c,t_e) = 1 \,\}\bigr|"),
    (r"I_e\s*=\s*1\[S_e\s*\u2265\s*m\]", r"I_e = \mathbf{1}\!\left[S_e \ge m\right]"),
    (r"N\\?\*\s*=\s*\u03a3\s*_?\s*e\s*I_e", r"N^{*} = \sum_{e} I_e"),
    (r"N\\?\*\s*=\s*\u03a3\s*1\[S_e\s*\u2265\s*m\]", r"N^{*} = \sum \mathbf{1}[S_e \ge m]"),
    (r"\u03a3\s*_?\s*e\s*I_e", r"\sum_{e} I_e"),
    (r"\u03a3\s*1\[S_e\s*\u2265\s*m\]", r"\sum \mathbf{1}[S_e \ge m]"),
    # comparisons
    (r"N\\?\*\s*<\s*N_min", r"N^{*} < N_{\min}"),
    (r"N\\?\*\s*\u2264\s*(\d+)", r"N^{*} \le \1"),
    (r"N\\?\*\s*=\s*(\d+)", r"N^{*} = \1"),
    (r"N_min\s*>\s*(\d+)", r"N_{\min} > \1"),
    (r"N_min\s*=\s*(\d+)", r"N_{\min} = \1"),
    (r"N_min\s*\u2264\s*(\d+)", r"N_{\min} \le \1"),
    (r"m\s*\u2265\s*(\d+)", r"m \ge \1"),
    (r"m\s*=\s*(\d+)", r"m = \1"),
    # identifiers
    (r"C\(t_e\)", r"C(t_e)"),
    (r"C\(t\)", r"C(t)"),
    (r"M\(e,\s*c,\s*t_e\)", r"M(e,c,t_e)"),
    (r"M\(e,\s*c,\s*t\)", r"M(e,c,t)"),
    (r"N_min", r"N_{\min}"),
    (r"N\\\*", r"N^{*}"),
    (r"S_e", r"S_e"),
    (r"I_e", r"I_e"),
    (r"t_e", r"t_e"),
]
_MATH_RE = [(re.compile(p), r) for p, r in MATH]


def mathify(text: str) -> str:
    """Replace mathematical identifiers and expressions with protected inline math.

    Applies inside `code spans` and **bold** too, because a mathematical object set in typewriter or
    bold text is the defect this function exists to remove.
    """
    # Unwrap code spans and bold that contain only a mathematical object, so the object is set as
    # mathematics rather than as typewriter or bold text. `N*` inside a code span carries no
    # Markdown backslash, so it is first normalised to the escaped form the math table expects.
    text = re.sub(r"`N\*`", "`N" + chr(92) + "*`", text)
    for pat, _ in _MATH_RE:
        text = re.sub(r"`(" + pat.pattern + r")`", r"\1", text)
        text = re.sub(r"\*\*(" + pat.pattern + r")\*\*", r"\1", text)
    for pat, rep in _MATH_RE:
        text = pat.sub(lambda m, r=rep: _protect("$" + _expand(m, r) + "$"), text)
    return text


def _expand(m: re.Match, template: str) -> str:
    r"""Substitute \1..\9 only.

    `re.Match.expand` cannot be used here: the replacements are LaTeX, so a sequence such as
    `\le` or `\min` is a command, not a regex escape, and `expand` rejects it.
    """
    out = []
    i = 0
    while i < len(template):
        if template[i] == "\\" and i + 1 < len(template) and template[i + 1].isdigit():
            out.append(m.group(int(template[i + 1])))
            i += 2
        else:
            out.append(template[i])
            i += 1
    return "".join(out)


# --------------------------------------------------------------------------------------
# Inline markup: Markdown escapes, then the historical escaper and emphasis pass.
# --------------------------------------------------------------------------------------
_MD_ESCAPES = {r"\*": "*", r"\_": "_", r"\|": "|", r"\#": "#", r"\`": "`"}


def inline(text: str) -> str:
    text = mathify(text)
    order: list[str] = []
    for seq, literal in _MD_ESCAPES.items():
        while seq in text:
            text = text.replace(seq, "\ue200" + chr(len(order)), 1)
            order.append(literal)
    out = base.inline(text)
    for i, literal in enumerate(order):
        out = out.replace("\ue200" + chr(i), base.SPECIALS.get(literal, literal))
    return _restore(out)


# --------------------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------------------
LONG_TABLE_ROWS = 12
WIDE_TABLE_COLS = 6


def table(block: list[str]) -> list[str]:
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in block]
    header, body = rows[0], rows[2:]
    ncol = len(header)
    widths = []
    for i in range(ncol):
        cells = [header[i]] + [r[i] if i < len(r) else "" for r in body]
        widths.append(max(len(c) for c in cells) or 1)
    weights = [math.sqrt(w) for w in widths]
    tw = sum(weights)
    frac = [max(w / tw, 0.055) for w in weights]
    scale = 0.93 / sum(frac)
    frac = [f * scale for f in frac]
    spec = "".join("p{" + f"{f:.3f}" + r"\linewidth}" for f in frac)
    size = r"\scriptsize" if ncol > WIDE_TABLE_COLS else (
        r"\footnotesize" if ncol > 4 else r"\small")
    head_row = " & ".join(r"\textbf{" + inline(c) + "}" for c in header) + r" \\"

    out: list[str] = []
    if len(body) > LONG_TABLE_ROWS:
        out += ["{" + size, r"\setlength{\tabcolsep}{3pt}",
                r"\begin{longtable}{" + spec + "}", r"\hline", head_row, r"\hline",
                r"\endfirsthead", r"\hline", head_row, r"\hline", r"\endhead",
                r"\hline", r"\endfoot"]
        for r in body:
            out.append(" & ".join(inline(c) for c in (r + [""] * ncol)[:ncol]) + r" \\")
        out += [r"\end{longtable}", "}", ""]
    else:
        out += [r"\begin{center}", size, r"\setlength{\tabcolsep}{4pt}",
                r"\begin{tabular}{" + spec + "}", r"\hline", head_row, r"\hline"]
        for r in body:
            out.append(" & ".join(inline(c) for c in (r + [""] * ncol)[:ncol]) + r" \\")
        out += [r"\hline", r"\end{tabular}", r"\end{center}", ""]
    return out


# --------------------------------------------------------------------------------------
# Block structure
# --------------------------------------------------------------------------------------
IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
ORDERED_RE = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")
BULLET_RE = re.compile(r"^(\s*)[-*]\s+(.*)$")
TABLE_SEP_RE = re.compile(r"^\|[\s:|-]+\|?\s*$")


def _is_table_start(lines: list[str], i: int) -> bool:
    return (lines[i].startswith("|") and i + 1 < len(lines)
            and TABLE_SEP_RE.match(lines[i + 1]) is not None)


def render_block(lines: list[str], depth: int = 0) -> list[str]:
    """Render a sequence of Markdown lines. Recursive, so quotes keep their structure."""
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        if line.strip() in ("---", "***", "___"):
            i += 1
            continue

        if _is_table_start(lines, i):
            block = []
            while i < n and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            out += table(block)
            continue

        m = IMAGE_RE.match(line)
        if m:
            out += [r"\begin{center}",
                    r"\includegraphics[width=\linewidth]{" + m.group(2) + "}",
                    r"\end{center}", ""]
            i += 1
            continue

        if line.startswith(">"):
            inner: list[str] = []
            while i < n and lines[i].lstrip().startswith(">"):
                inner.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append(r"\begin{quote}")
            out += render_block(inner, depth + 1)
            out.append(r"\end{quote}")
            out.append("")
            continue

        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            title = inline(line[level:].strip())
            cmd = {2: r"\section*", 3: r"\subsection*", 4: r"\subsubsection*"}.get(
                level, r"\paragraph*")
            out += [cmd + "{" + title + "}", ""]
            i += 1
            continue

        m = ORDERED_RE.match(line)
        if m:
            items, i = _collect_list(lines, i, ORDERED_RE)
            out.append(r"\begin{enumerate}")
            out += [r"\item " + inline(t) for t in items]
            out += [r"\end{enumerate}", ""]
            continue

        m = BULLET_RE.match(line)
        if m:
            items, i = _collect_list(lines, i, BULLET_RE)
            out.append(r"\begin{itemize}")
            out += [r"\item " + inline(t) for t in items]
            out += [r"\end{itemize}", ""]
            continue

        para = [line]
        i += 1
        while i < n and lines[i].strip() and not (
                lines[i].startswith(("#", ">", "|", "!["))
                or ORDERED_RE.match(lines[i]) or BULLET_RE.match(lines[i])
                or lines[i].strip() in ("---", "***", "___")):
            para.append(lines[i].rstrip())
            i += 1
        out += [inline(" ".join(para)), ""]
    return out


def _collect_list(lines: list[str], i: int, item_re: re.Pattern) -> tuple[list[str], int]:
    """Collect list items, folding indented continuation lines into the item they belong to.

    This is the fix for the defect where a wrapped item closed the list and the numbering restarted
    at 1 for every subsequent item.
    """
    items: list[str] = []
    n = len(lines)
    while i < n:
        m = item_re.match(lines[i])
        if not m:
            break
        text = m.group(3) if item_re is ORDERED_RE else m.group(2)
        i += 1
        while i < n and lines[i].strip() and not item_re.match(lines[i]) and \
                not lines[i].startswith(("#", ">", "|", "![")) and lines[i][:1] in (" ", "\t"):
            text += " " + lines[i].strip()
            i += 1
        items.append(text)
        if i < n and not lines[i].strip():
            # a blank line ends the list unless the next non-blank line is another item
            j = i
            while j < n and not lines[j].strip():
                j += 1
            if j < n and item_re.match(lines[j]):
                i = j
                continue
            break
    return items, i


PREAMBLE_EXTRA = r"""\usepackage{longtable}
\usepackage{amsmath}
\usepackage{amssymb}
"""


def convert(md: str, date: str, title: str, author: str, keywords: str,
            subject: str, affiliation: str | None = None) -> str:
    """Convert the release manuscript, with publication front matter and PDF metadata."""
    _slots.clear()
    lines = md.split("\n")
    # The first `# ` heading is the title; it is set by the front matter, not by the body. The
    # byline block that follows it in paper.md is also front matter, so it is consumed here rather
    # than rendered - otherwise \\maketitle and the body would both print the author. Only byline
    # lines may appear there, and anything else is a build error rather than silently dropped text.
    body_start = 0
    for idx, ln in enumerate(lines):
        if ln.startswith("# "):
            body_start = idx + 1
            break
    front = body_start
    while front < len(lines) and not lines[front].startswith("## "):
        front += 1
    dropped = [ln for ln in lines[body_start:front] if ln.strip()]
    allowed = [author, date] + ([affiliation] if affiliation else [])
    for ln in dropped:
        stripped = ln.strip().strip("*_")
        if stripped not in allowed:
            raise ValueError(
                "release/paper.md has content between the title and the first section that is not "
                f"part of the byline and would be dropped: {ln!r}")
    out = render_block(lines[front:])

    preamble = base.PREAMBLE.replace(
        "%% Generated from paper.md by scripts/paper_md_to_tex.py - do not edit by hand.",
        "%% Generated from paper.md by scripts/release_md_to_tex.py - do not edit by hand.")
    preamble = preamble.replace(
        r"\usepackage{graphicx}", "\\usepackage{graphicx}\n" + PREAMBLE_EXTRA.rstrip())
    preamble = preamble.replace(
        r"\usepackage[hidelinks]{hyperref}",
        "\\usepackage[hidelinks,\n"
        f"  pdftitle={{{title}}},\n"
        f"  pdfauthor={{{author}}},\n"
        f"  pdfsubject={{{subject}}},\n"
        f"  pdfkeywords={{{keywords}}}]{{hyperref}}")

    head = preamble
    head += "\\title{" + base.inline(title) + "}\n"
    # The affiliation sits under the name on the title page. Its line break and italics are
    # LaTeX and are assembled here: passing them through base.inline() would escape the break
    # to \textbackslash{} twice and print it as literal text on the byline.
    author_tex = base.inline(author)
    if affiliation:
        author_tex += "\\\\[2pt]\\textit{" + base.inline(affiliation) + "}"
    head += "\\author{" + author_tex + "}\n"
    head += "\\date{" + date + "}\n"
    head += "\\begin{document}\n\\maketitle\n\n"
    return head + "\n".join(out) + "\n\\end{document}\n"
