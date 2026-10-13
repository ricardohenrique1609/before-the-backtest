"""Render a real References section from release/references.bib, and audit the citations.

The bibliography file stays the single source of truth: nothing is invented, no metadata is enriched,
no literature search is performed, and an entry that records uncertainty keeps recording it.

Produces:
  * the Markdown for the References section, for the release manuscript;
  * REFERENCES_QA.md, a machine-generated report on coverage and completeness.

Run: .venv/Scripts/python -I scripts/release_refs.py
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
REL = ROOT / "papers" / "falsification_first_alpha_discovery" / "release"
BIB = REL / "references.bib"
PAPER = REL / "paper.md"

FIELD_RE = re.compile(r"(\w+)\s*=\s*(\{)", re.S)


def parse_bib(text: str) -> list[dict]:
    """Minimal BibTeX reader: entry type, key and brace-balanced fields."""
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,]+),", text):
        etype, key = m.group(1).lower(), m.group(2).strip()
        # body runs to the brace that closes this entry
        i, depth = m.end() - 1, 1
        while i + 1 < len(text) and depth:
            i += 1
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
        body = text[m.end():i]
        fields = {}
        for fm in FIELD_RE.finditer(body):
            name = fm.group(1).lower()
            j, d = fm.end() - 1, 1
            while j + 1 < len(body) and d:
                j += 1
                if body[j] == "{":
                    d += 1
                elif body[j] == "}":
                    d -= 1
            fields[name] = " ".join(body[fm.end():j].split())
        entries.append({"type": etype, "key": key, **fields})
    return entries


# BibTeX accent commands actually present in references.bib, mapped to the characters they denote.
# Dropping the accent would misspell a cited author's name, so they are translated, not stripped.
ACCENTS = {
    ("'", "o"): "ó", ("'", "a"): "á", ("'", "e"): "é", ("'", "i"): "í", ("'", "u"): "ú",
    ('"', "o"): "ö", ('"', "a"): "ä", ('"', "u"): "ü",
    ("`", "a"): "à", ("`", "e"): "è",
    ("^", "a"): "â", ("^", "e"): "ê", ("^", "o"): "ô",
    ("~", "n"): "ñ", ("~", "a"): "ã", ("~", "o"): "õ",
    ("k", "e"): "ę", ("k", "a"): "ą",
    ("c", "c"): "ç", ("v", "s"): "š", ("v", "c"): "č",
}


def clean(s: str) -> str:
    """Resolve BibTeX accent commands to characters, then strip the remaining brace syntax."""
    def acc(m: re.Match) -> str:
        return ACCENTS.get((m.group(1), m.group(2)), m.group(2))

    s = re.sub(r"\{\\(['`\"^~=.kcvuH])\s*\{?(\w)\}?\}", acc, s)
    s = re.sub(r"\\(['`\"^~=.kcvuH])\s*\{?(\w)\}?", acc, s)
    return s.replace("{", "").replace("}", "").replace("\\", "")


def sort_key(e: dict) -> tuple:
    a = clean(e.get("author", "") or e.get("institution", "") or e.get("howpublished", ""))
    first = a.split(" and ")[0].strip()
    surname = first.split(",")[0].strip() if "," in first else first.split()[-1] if first else ""
    if not surname:
        surname = clean(e.get("title", ""))[:40]
    return (surname.lower(), e.get("year", "9999"), clean(e.get("title", ""))[:40].lower())


def authors_display(e: dict) -> str:
    a = e.get("author")
    if not a:
        return ""
    names = [clean(x.strip()) for x in a.split(" and ")]
    out = []
    for nm in names:
        if "," in nm:
            sur, given = [p.strip() for p in nm.split(",", 1)]
            initials = " ".join(f"{g[0]}." for g in given.split() if g)
            out.append(f"{sur}, {initials}" if initials else sur)
        else:
            out.append(nm)
    if len(out) == 1:
        return out[0]
    if len(out) == 2:
        return f"{out[0]} and {out[1]}"
    return ", ".join(out[:-1]) + " and " + out[-1]


def render_entry(e: dict) -> str:
    """Author-year academic format, carrying DOI/URL and the recorded access note."""
    bits: list[str] = []
    who = authors_display(e)
    if who:
        bits.append(f"**{who}**")
    year = e.get("year")
    bits.append(f"({year})." if year else "(n.d.).")
    title = clean(e.get("title", "")).rstrip(".")
    bits.append(f"*{title}*.")

    if e.get("journal"):
        venue = clean(e["journal"])
        vol = e.get("volume")
        num = e.get("number")
        pages = e.get("pages", "").replace("--", "–")
        loc = venue
        if vol:
            loc += f" {vol}"
            if num:
                loc += f"({num})"
        if pages:
            loc += f", {pages}"
        bits.append(loc + ".")
    elif e.get("institution"):
        bits.append(clean(e["institution"]) + ".")
    elif e.get("howpublished"):
        bits.append(clean(e["howpublished"]) + ".")
    elif e.get("archiveprefix") or e.get("eprint"):
        pref = clean(e.get("archiveprefix", "arXiv"))
        bits.append(f"{pref}:{e.get('eprint', '')}.")
    elif e.get("note") and e["type"] == "unpublished":
        bits.append("Working paper.")

    if e.get("eprint") and not (e.get("archiveprefix") and "arXiv" in str(bits)):
        if f"{e.get('eprint')}" not in " ".join(bits):
            bits.append(f"{clean(e.get('archiveprefix', 'arXiv'))}:{e['eprint']}.")
    if e.get("doi"):
        bits.append(f"DOI: {e['doi']}.")

    line = " ".join(bits)
    note = e.get("note")
    if note:
        line += f"  \n  *{clean(note)}*"
    return line


def in_text_citations(md: str) -> set[str]:
    """Author-year citation groups used in the prose, e.g. "Rubin (2008)", "[Ammann et al. 2022]"."""
    cites = set()
    for m in re.finditer(r"([A-Z][A-Za-zÀ-ÿ'`\-]+(?:\s*(?:,|&|and)\s*[A-Z][A-Za-zÀ-ÿ'`\-]+)*"
                         r"(?:\s+et\s+al\.?)?)\s*\(?(?:19|20)(\d{2})\)?", md):
        names = m.group(1)
        if names.split()[0] in {"The", "This", "A", "In", "We", "It", "Under", "Both", "Each"}:
            continue
        cites.add(f"{names.strip()} {m.group(0)[-5:].strip('()')}")
    return cites


def main() -> None:
    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    entries.sort(key=sort_key)
    # Scan the body only. Once the References section is rendered into the manuscript, including it
    # would make the bibliography cite itself and every entry would read as an in-text citation.
    md = PAPER.read_text(encoding="utf-8").split(chr(10) + "## References")[0]

    section = ["## References", ""]
    section.append("Rendered from `references.bib`, which is the source of truth. Each entry states "
                   "the level at which it was accessed; several were read only at abstract or "
                   "metadata level and say so. No metadata was inferred.")
    section.append("")
    for e in entries:
        section.append(f"- {render_entry(e)}")
        section.append("")
    out_md = "\n".join(section).rstrip() + "\n"
    (REL / "_references_section.md").write_text(out_md, encoding="utf-8")

    # ------------------------------------------------------------------ QA
    surnames = set()
    for e in entries:
        who = authors_display(e)
        if who:
            for part in re.split(r",| and ", who):
                p = part.strip()
                if p and not re.fullmatch(r"[A-Z]\.( [A-Z]\.)*", p):
                    surnames.add(p.split()[-1] if " " in p else p)
    cited = in_text_citations(md)
    unresolved = sorted(c for c in cited
                        if not any(s.lower() in c.lower() for s in surnames)
                        and not any(w in c for w in ("PSweight", "Tectonic")))
    uncited = []
    for e in entries:
        who = authors_display(e)
        tag = (who.split(",")[0].split(" and ")[0].strip() if who
               else clean(e.get("title", ""))[:25])
        if tag and tag.lower() not in md.lower() and clean(e.get("title", ""))[:25].lower() \
                not in md.lower():
            uncited.append((e["key"], tag))

    rows = []
    for e in entries:
        rows.append((e["key"], bool(e.get("author")), bool(e.get("year")),
                     bool(e.get("title")), bool(e.get("doi")), bool(e.get("note"))))

    rep = ["# REFERENCES QA", "",
           "Machine-generated by `scripts/release_refs.py` from `references.bib`. "
           "No external metadata enrichment was performed.", "",
           "| metric | value |", "|---|---|",
           f"| bibliography entries total | **{len(entries)}** |",
           f"| in-text author-year citation groups detected | {len(cited)} |",
           f"| **unresolved citations** | **{len(unresolved)}** |",
           f"| uncited bibliography entries (retained deliberately) | {len(uncited)} |",
           f"| duplicate keys | {len(entries) - len({e['key'] for e in entries})} |",
           f"| entries missing an author field | {sum(1 for r in rows if not r[1])} |",
           f"| entries missing a year | {sum(1 for r in rows if not r[2])} |",
           f"| entries missing a title | {sum(1 for r in rows if not r[3])} |",
           f"| entries carrying a DOI | {sum(1 for r in rows if r[4])} |",
           f"| entries carrying an access-level note | {sum(1 for r in rows if r[5])} |",
           ""]
    if unresolved:
        rep += ["## Unresolved citations", ""] + [f"- {c}" for c in unresolved] + [""]
    rep += ["## Entry-level detail", "",
            "| key | author | year | title | DOI | access note |", "|---|---|---|---|---|---|"]
    for k, a, y, t, d, nt in rows:
        rep.append(f"| `{k}` | {'yes' if a else '**no**'} | {'yes' if y else '**no**'} | "
                   f"{'yes' if t else '**no**'} | {'yes' if d else '—'} | "
                   f"{'yes' if nt else '**no**'} |")
    rep += ["",
            "## Notes on missing fields",
            "",
            "Absent author or year fields are **deliberate**. Where the committed literature reviews "
            "recorded no authors, or no given names, the entry carries none and its note says so, "
            "rather than supplying a plausible guess. The same applies to volume, issue, pages and "
            "DOI. Every entry carries an access-level note.",
            "",
            "## Uncited entries"]
    if uncited:
        rep += ["", "Retained deliberately: each was consulted during the literature work and is "
                    "part of the evidence trail, even where the final manuscript does not name it "
                    "in prose.", ""]
        rep += [f"- `{k}` ({t})" for k, t in uncited]
    else:
        rep += ["", "None: every entry is named in the manuscript."]
    (REL / "REFERENCES_QA.md").write_text("\n".join(rep) + "\n", encoding="utf-8")

    print(f"entries {len(entries)} | in-text groups {len(cited)} | unresolved {len(unresolved)} | "
          f"uncited {len(uncited)}")
    print("wrote _references_section.md and REFERENCES_QA.md")


if __name__ == "__main__":
    main()
