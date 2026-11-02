# H20.0 — Execution Deviations

Every departure from `H20_0_CONTEXT_FEASIBILITY_PLAN.md` (frozen, sha256 in the freeze file) and from
the code state at freeze time. None changes the frozen sample; none was decided by looking at an
outcome.

## D1 — Entity-resolution parser v2 written after v1's output was seen

**What happened.** Parser v1 (`h20_0_entities.py:names_for`) had two defects visible in its output
on the frozen sample: it discarded names equal to the ticker (`dYdX (DYDX)`, `GMX (GMX)`,
`Amp (AMP)`, `Troy (TROY)` all became NOT_FOUND), and its loose verb list accepted non-listing
phrases as names ("Airdrop for Aeron", "Update on Notcoin", "Subscription for the SafePal").

**Why that is a problem.** A parser fixed after seeing its errors on the evaluation sample scores
itself optimistically on that sample.

**What was done.** v2 (`names_v2`: strict listing verbs, names equal to the ticker allowed, latest
name wins when a project was renamed) was added **beside** v1, both are reported, and the gate's G7
for C5 uses **v2 on an independent validation draw** (`scripts/h20_0_entity_validation.py`, same
rule as plan §3, seed 20261019, never used for anything else). Resolved names on the validation
draw were hand-checked (`evidence/H20_0_ENTITY_GOLD_VALIDATION.csv`; researcher judgement from
general knowledge of project names, not an outcome source).

| sample | parser | resolved | tuned on it |
|---|---|---|---|
| frozen | v1 | see `evidence/H20_0_ENTITY_RESOLUTION.csv` | no |
| frozen | v2 | 〃 | **yes** |
| validation | v1 | 〃 | no |
| validation | v2 | 〃 — **used for G7** | no |

## D2 — CFTC pacing and a persistent HTTP 429

At the default 1 s pace the CFTC site answered 429 after five pages. The pace for `www.cftc.gov` was
raised to 10 s; the immediate re-run still received 429 for every year and was recorded as
`ACCESS_BLOCKED`. A third attempt was made ~10 h later. Access controls were never bypassed.
Pages already received are parsed from `data/raw/cftc/` rather than re-requested.

## D3 — Request log split per process

Collectors ran in parallel and appended to one `_requests.jsonl`; one line in 1,469 was interleaved
and is unparseable. From that point each process writes `_requests_<script>_<pid>.jsonl`. Readers
skip malformed lines and the count is reported (`H20_0_METRICS.json: request_log_malformed_lines`).

## D4 — Binance detail run interrupted and resumed from raw

The detail fetch stalled at 352 of 789 articles when the session was suspended for ~10 h, before it
wrote its table. The run was stopped and stage 3 made resumable: a body already saved under
`data/raw/binance_cms/` is parsed, not re-requested (flag `from_cache`). Catalogue 161, whose pages 7
and 8 were blocked in the first harvest, was re-requested by `--stage repair` before stage 3, so W7
membership reflects the repaired catalogue.

## D5 — `h20_common.py` changed after the freeze

The freeze records the sha256 of `h20_common.py` at freeze time. Later changes: per-host pace for
CFTC and SEC (D2), per-process request log (D3), a log reader. None touches sampling.

## D6 — Binance archive URLs re-checked with title slugs

The first archive pass looked Binance notices up as `/en/support/announcement/<code>`. Reading the
output (0% of 2024–2026 notices ever captured) and probing the CDX showed that recent Binance URLs
carry a title slug before the code (`/announcement/dymension-dym-listing-will-be-postponed-<code>`).
`h20_0_archive_refetch.py --part binance_recheck` re-queried every Binance row of the archive
subsample under three URL forms (code-only, slug-code, `/detail/<code>`) and kept the earliest
capture. Captured-ever rose from 52% to 80%; captured ≤ t is 38.5%. The slug is reconstructed from
the title, so a title whose published slug differs is still missed: the figure is a lower bound.

## D7 — Audit-script defects found by reading the output, fixed before the verdict

1. A variable name was reused, so `requests_total` reported 2 instead of 4,490.
2. The CFTC table de-duplicated on document key, which collapsed the blocked years into one row and
   made 2021–2026 look *available with zero documents*. Blocked rows are now kept per year, and a
   window counts as covered only if every year it touches was walked past the window start before the
   429. CFTC is MISSING for 2021–2026.
3. One Fed release's first capture (1998) predates its own stamp (2022): a reused URL. Captures earlier
   than a publisher's stamp no longer count as `V1_ARCHIVED_AT_T` (GDELT excepted, whose clock is
   first observation). Fed G4 basis 77.3% → 76.0%.

None of the three changed a layer verdict.

Also after the run: three unused imports removed (`ruff F401`) from two collector scripts; no
behaviour change.

## D8 — Line endings normalised before every hash

The repository stores text as LF (`.gitattributes: * text=auto eol=lf`). Evidence files written on
Windows in text mode had CRLF, so their sha256 in the manifest and in the pre-seal hash file would not
have matched a clean checkout. `h20_common.to_lf()` now converts text artefacts to LF before every
hash; the audit, the sealed stage and the manifest were re-run. The freeze file and the plan were
already LF, so their recorded hashes are unaffected. No number or verdict changed.
