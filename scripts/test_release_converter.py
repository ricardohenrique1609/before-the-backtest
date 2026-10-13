"""Regression tests for the release converter.

Each test pins a defect found in a compiled release PDF, so it cannot return silently. Run directly
or under pytest.

    .venv/Scripts/python -I scripts/test_release_converter.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("rel", ROOT / "scripts" / "release_md_to_tex.py")
rel = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rel)


def render(md: str) -> str:
    rel._slots.clear()
    return "\n".join(rel.render_block(md.split("\n")))


# ---------------------------------------------------------------- mathematics (RC2 defects)
def test_support_definition_is_math() -> None:
    """RC2 rendered the set-builder as text and dropped the membership symbol."""
    out = render("**S_e = |{ c ∈ C(t_e) : M(e, c, t_e) = 1 }|**")
    assert r"\in" in out, out
    assert r"\bigl|\{" in out, out
    assert "S_e" in out and "C(t_e)" in out
    assert "$" in out, "must be set in math mode"


def test_indicator_is_math() -> None:
    out = render("**I_e = 1[S_e ≥ m]**")
    assert r"\mathbf{1}" in out, out
    assert r"\ge" in out, out


def test_sum_is_math() -> None:
    r"""RC2 rendered `N* = \Sigma_e I_e` as "N* = _e I_e": the sigma was lost."""
    out = render("**N\\* = Σ_e I_e**")
    assert r"\sum_{e} I_e" in out, out
    assert r"N^{*}" in out, out
    assert "_e I_e" not in out.replace(r"\sum_{e} I_e", ""), "bare subscript must not survive"


def test_stop_rule_is_math() -> None:
    out = render("**N\\* < N_min**")
    assert r"N^{*} < N_{\min}" in out, out


def test_bounds_are_math() -> None:
    for src, want in [("N\\* ≤ 15", r"N^{*} \le 15"),
                      ("N\\* ≤ 16", r"N^{*} \le 16"),
                      ("N_min > 15", r"N_{\min} > 15"),
                      ("N_min > 16", r"N_{\min} > 16"),
                      ("m ≥ 3", r"m \ge 3"),
                      ("N\\* = 10", r"N^{*} = 10"),
                      ("N_min = 40", r"N_{\min} = 40")]:
        out = render(src)
        assert want in out, f"{src!r} -> {out!r}"


def test_math_identifier_in_code_span_becomes_math() -> None:
    """A mathematical object in backticks was typewritten with a literal underscore."""
    out = render("the universe `C(t_e)` is built")
    assert "$C(t_e)$" in out, out
    assert r"\texttt{C" not in out, out


def test_no_stray_backslash_before_asterisk() -> None:
    r"""RC2 printed "N\ = 10" because `N\*` emitted \textbackslash and opened an italic span."""
    out = render("the sample **N\\* = 10** against 40")
    assert "textbackslash" not in out, out
    assert r"\emph{" not in out, out


# ---------------------------------------------------------------- unicode
def test_arrow_survives() -> None:
    out = render("CEX↔DEX funding fragmentation")
    assert r"\leftrightarrow" in out, out


def test_symbols_map() -> None:
    out = render("ΔPR-AUC of −0.0075, ≈ 7, ≥ 3, ≤ 15, §3")
    for want in (r"\Delta", r"\approx", r"\geq", r"\leq", r"\S"):
        assert want in out, f"{want} missing from {out!r}"


# ---------------------------------------------------------------- lists (RC2 defect)
def test_numbered_list_with_continuation_keeps_one_enumerate() -> None:
    """RC2 restarted numbering at 1 for every item, because wrapped lines closed the list."""
    md = ("1. **First item**, which wraps\n"
          "   onto a second line and a third.\n"
          "2. **Second item**, also wrapping\n"
          "   onto another line.\n"
          "3. **Third item**.\n")
    out = render(md)
    assert out.count(r"\begin{enumerate}") == 1, out
    assert out.count(r"\item") == 3, out
    assert "onto a second line and a third." in out


def test_list_inside_blockquote_survives() -> None:
    """The procedure box lost its list entirely: every line was joined into one paragraph."""
    md = ("> **PROCEDURE**\n"
          ">\n"
          "> For each event:\n"
          "> 1. construct the universe;\n"
          "> 2. apply the rule;\n"
          "> 3. compute the support.\n")
    out = render(md)
    assert r"\begin{quote}" in out
    assert r"\begin{enumerate}" in out, out
    assert out.count(r"\item") == 3, out


# ---------------------------------------------------------------- structure
def test_table_long_uses_longtable() -> None:
    rows = "\n".join(f"| r{i} | v{i} |" for i in range(20))
    out = render("| a | b |\n|---|---|\n" + rows)
    assert r"\begin{longtable}" in out, out


def test_table_short_uses_tabular() -> None:
    out = render("| a | b |\n|---|---|\n| 1 | 2 |")
    assert r"\begin{tabular}" in out and "longtable" not in out


def test_image_becomes_includegraphics() -> None:
    out = render("![](figures/f1_procedure.png)")
    assert r"\includegraphics" in out and "figures/f1_procedure.png" in out


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {t.__name__}: {str(e)[:200]}")
    print(f"\n{len(tests) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
