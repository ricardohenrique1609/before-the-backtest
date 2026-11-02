"""Render paper/manuscript.md from paper/manuscript_src.md by inlining the generated tables.

Every {{TABLE:<stem>}} marker is replaced by paper/tables/<stem>.md, which build_paper_assets.py
generates from frozen artefacts, so a manuscript table can never drift from its source.

    .venv/Scripts/python "Contextual Alpha/paper/scripts/render_manuscript.py"
"""

import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]


def main() -> int:
    src = (PAPER / "manuscript_src.md").read_text(encoding="utf-8")
    missing = []

    def sub(m):
        p = PAPER / "tables" / f"{m.group(1)}.md"
        if not p.exists():
            missing.append(m.group(1))
            return m.group(0)
        return p.read_text(encoding="utf-8").strip()

    out = re.sub(r"\{\{TABLE:([A-Za-z0-9_]+)\}\}", sub, src)
    if missing:
        print("missing tables:", missing)
        return 1
    (PAPER / "manuscript.md").write_text(out, encoding="utf-8", newline="\n")
    body = out.split("## References")[0]
    body = re.sub(r"^---.*?---", "", body, flags=re.S)
    prose = "\n".join(l for l in body.splitlines() if not l.startswith("|") and not l.startswith("!["))
    words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-\.%]*", prose))
    print(f"manuscript.md written; main-text words (excluding tables, figures, references, appendices) ~ {words}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
