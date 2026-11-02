"""Shared plumbing for H20.0: paths, the guarded and logged HTTP client, hashing, normalisation.

Every outbound request in H20 goes through get(). It logs to data/raw/_requests.jsonl, paces per
host, refuses outcome-shaped queries (CONTEXT_RETRIEVAL_GOVERNANCE.md section 3), and distinguishes
ACCESS_BLOCKED from NO_DATA. Nothing here writes outside Contextual Alpha/.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode, urlparse

import httpx

CA = Path(__file__).resolve().parents[1]
ROOT = CA.parent
RAW = CA / "data" / "raw"
INTERIM = CA / "data" / "interim"
DERIVED = CA / "data" / "derived"
EVIDENCE = CA / "evidence"
MANIFESTS = CA / "manifests"
REGISTRIES = CA / "registries"
# one log per process: collectors run in parallel and a shared append-only file interleaved one line
# (H20_0_EXECUTION_DEVIATION.md, D3). Readers glob RAW/_requests*.jsonl and skip malformed lines.
REQUEST_LOG = RAW / f"_requests_{Path(sys.argv[0]).stem or 'interactive'}_{os.getpid()}.jsonl"

# public package: the contact address is read from the environment (see PUBLIC_PACKAGE_NOTES.md)
UA = f"Mozilla/5.0 (compatible; QIE-ContextualAlpha research; {os.environ.get('QIE_CONTACT_EMAIL', 'contact-unset')})"

# words that would make a query outcome-shaped (governance section 3)
OUTCOME_TERMS = (
    "delist",
    "crash",
    "collapse",
    "scam",
    "rug",
    "exploit",
    "hack",
    "bankrupt",
    "insolven",
    "lawsuit",
    "why did",
    "why-did",
    "what caused",
    "what-caused",
    "reason",
)
_OUTCOME_RE = re.compile("|".join(re.escape(t) for t in OUTCOME_TERMS), re.I)

# minimum seconds between requests to one host
PACE = {
    "www.binance.com": 1.9,
    "web.archive.org": 1.2,
    "en.wikipedia.org": 0.3,
    "www.federalregister.gov": 0.5,
    "data.gdeltproject.org": 0.3,
    "www.cftc.gov": 10.0,
    "www.sec.gov": 1.0,
}
DEFAULT_PACE = 1.0
_last: dict[str, float] = {}


class ForbiddenQueryError(ValueError):
    """Raised when a constructed query contains an outcome term."""


@dataclass
class Resp:
    status: int
    outcome: str  # OK | NO_DATA | ACCESS_BLOCKED | HTTP_ERROR | NETWORK_ERROR
    content: bytes
    url: str
    sha256: str
    ingest_time: str
    headers: dict


def now_utc() -> datetime:
    return datetime.now(tz=UTC)


def iso(dt: datetime | None) -> str | None:
    return None if dt is None else dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalise_text(s: str) -> str:
    """Normaliser v1 for content_hash: NFC, collapse whitespace, strip."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s or "")).strip()


def content_hash(*parts: str) -> str:
    return sha256_bytes("\n".join(normalise_text(p) for p in parts).encode("utf-8"))


def check_query(url: str, params: dict | None, lookup: str | None = None) -> None:
    """Refuse outcome-shaped queries. `lookup` is an identifier already collected elsewhere and is
    removed before checking (governance section 3, 'Lookups are not queries')."""
    text = url + "?" + urlencode(params or {}, doseq=True)
    if lookup:
        text = text.replace(lookup, "").replace(urlencode({"u": lookup})[2:], "")
    m = _OUTCOME_RE.search(text)
    if m:
        raise ForbiddenQueryError(f"outcome term {m.group(0)!r} in query: {text[:200]}")


_client: httpx.Client | None = None


def client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(headers={"User-Agent": UA}, timeout=60, follow_redirects=True)
    return _client


def _log(rec: dict) -> None:
    REQUEST_LOG.parent.mkdir(parents=True, exist_ok=True)
    with REQUEST_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def get(
    url: str,
    params: dict | None = None,
    *,
    purpose: str,
    lookup: str | None = None,
    retries: int = 3,
    headers: dict | None = None,
) -> Resp:
    check_query(url, params, lookup)
    host = urlparse(url).netloc
    status, outcome, content, final_url, hdrs = 0, "NETWORK_ERROR", b"", url, {}
    for attempt in range(retries):
        wait = PACE.get(host, DEFAULT_PACE) - (time.monotonic() - _last.get(host, 0.0))
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.monotonic()
        try:
            r = client().get(url, params=params, headers=headers)
            status, content, final_url, hdrs = r.status_code, r.content, str(r.url), dict(r.headers)
        except httpx.HTTPError as e:
            status, content, outcome = 0, str(e).encode(), "NETWORK_ERROR"
            time.sleep(2 * (attempt + 1))
            continue
        if status == 200 and content:
            outcome = "OK"
            break
        if status == 404:
            outcome = "NO_DATA"
            break
        if status in (202, 403, 429, 503) or (status == 200 and not content):
            outcome = "ACCESS_BLOCKED"
            time.sleep(5 * (attempt + 1))
            continue
        outcome = "HTTP_ERROR"
        if 400 <= status < 500:
            break
        time.sleep(2 * (attempt + 1))
    ingest = iso(now_utc())
    digest = sha256_bytes(content)
    _log(
        {
            "ingest_time": ingest,
            "purpose": purpose,
            "url": url,
            "params": params,
            "final_url": final_url,
            "status": status,
            "outcome": outcome,
            "bytes": len(content),
            "sha256": digest,
            "lookup": bool(lookup),
        }
    )
    return Resp(status, outcome, content, final_url, digest, ingest, hdrs)


def save_raw(source_id: str, name: str, content: bytes) -> Path:
    d = RAW / source_id
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    if not p.exists():  # write-once
        p.write_bytes(content)
    return p


def read_request_logs() -> tuple[list[dict], int]:
    recs, bad = [], 0
    for p in sorted(RAW.glob("_requests*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError:
                bad += 1
    return recs, bad


CRLF, LF = bytes([13, 10]), bytes([10])
TEXT_SUFFIXES = {".md", ".json", ".csv", ".py", ".txt", ".sha256"}


def to_lf(paths) -> None:
    """The repository stores text as LF (.gitattributes: text=auto eol=lf). Files written on Windows in
    text mode get CRLF, so any hash computed on them would not match a clean checkout. Every H20 hash
    of a text artefact is taken after this normalisation."""
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix in TEXT_SUFFIXES:
            b = p.read_bytes()
            if CRLF in b:
                p.write_bytes(b.replace(CRLF, LF))


def load_freeze() -> dict:
    return json.loads((CA / "H20_0_SAMPLE_FREEZE.json").read_text(encoding="utf-8"))
