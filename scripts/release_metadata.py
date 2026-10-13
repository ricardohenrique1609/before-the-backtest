"""Single source of truth for the public release metadata of the paper.

Every file that states the release version, the title, the byline or the cover date reads it from
here. The author's name must have exactly one canonical representation across the title page, the
PDF document properties, `CITATION.cff`, `zenodo.json` and the manifest, so it is defined once and
never retyped: a byline variant is the one metadata error that cannot be corrected after
publication.

Author metadata was explicitly authorised by the author (release blocker B7). What that
authorisation does *not* include is recorded in FORBIDDEN_IN_BYLINE and enforced by
check_author_metadata(): no employer or university affiliation, no correspondence email, no ORCID.
Nothing here is inferred from version-control configuration or from any other file.
"""

from __future__ import annotations

RELEASE_VERSION = "v1.0.0"
RELEASE_DATE_ISO = "2026-10-13"      # exact date, for machine-readable metadata
RELEASE_DATE = "October 2026"        # cover date, as it appears on the title page

TITLE = ("Before the Backtest: Pre-Freeze Common-Support Ceilings for "
         "Event-Driven Strategy Research")
SUBJECT = ("Design-stage feasibility for matched event studies: computing attainable common support "
           "on the complete point-in-time eligible population before the design is frozen and "
           "before any outcome is opened")
KEYWORDS = ("common support, positivity, outcome-free design, point-in-time data, event studies, "
            "pre-registration, research feasibility")

AUTHOR = "Ricardo H. Ramos Silva"
AFFILIATION: str | None = "Independent Researcher"
ORCID: str | None = None             # none was provided, and none is invented
CORRESPONDENCE: str | None = None    # no public contact address was authorised

# Substrings that must never reach the byline. The employer and university names are excluded by the
# author's explicit instruction, and no institutional endorsement is implied by this work.
FORBIDDEN_IN_BYLINE = ("Ita", "FIAP", "@", "ORCID", "AUTHOR_METADATA_REQUIRED")

LATEX_ENGINE = "Tectonic 0.17.0"


def check_author_metadata() -> None:
    """Fail the build rather than publish an unauthorised, padded or placeholder byline."""
    if not AUTHOR or AUTHOR.strip() != AUTHOR:
        raise ValueError("AUTHOR must be set and carry no leading or trailing whitespace")
    for field in (AUTHOR, AFFILIATION or ""):
        for token in FORBIDDEN_IN_BYLINE:
            if token.lower() in field.lower():
                raise ValueError(
                    f"byline field {field!r} contains {token!r}: the author authorised no employer "
                    "or university affiliation, no correspondence email and no ORCID")
    if ORCID is not None or CORRESPONDENCE is not None:
        raise ValueError("no ORCID and no correspondence address were authorised for publication")


def pdf_author() -> str:
    """The byline name, used on the title page and as the PDF document author property.

    The affiliation is passed to the converter separately so the title page can set it on its own
    line; a LaTeX line break is not valid document metadata.
    """
    check_author_metadata()
    return AUTHOR
