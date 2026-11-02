# H20.1 — Execution Deviations

Every departure from `H20_1_REPRESENTATION_PLAN.md` (frozen; sha256 in
`H20_1_REPRESENTATION_FREEZE.json`) and from the frozen rules module `scripts/h20_1_rep.py`. None was
decided by looking at an outcome; no outcome table was opened.

## D1 — One design probe to the Federal Register API before the freeze

Before the plan was frozen, one request was sent to the Federal Register API for the date range of an
H20.0 **design** window (2018-02-25 → 2018-03-04) to confirm that a date-range query without a term
returns `abstract` and to size the pages (537 documents in a week). It is in the request log
(`purpose = h20_1:design_probe_fr`). It touched no evaluation window and no outcome.

## D2 — Transient network errors on two Federal Register months, retried

The first collection pass recorded `NETWORK_ERROR` (status 0, three retries each) for 2024-06 page 2
and 2024-07 page 1. Raw pages are write-once and cached, so the `fr` part was re-run; it re-used the
pages already received and requested only the missing ones. This is a retry of a transport failure,
not a change of rule; the window-completeness rule (plan §8) is unchanged.

## D3 — Outcome-blindness test narrowed from `binance` to Binance data paths

The first version of `tests/test_h20_1.py` forbade the string `binance` in any H20.1 script. That
also flagged the audit script's written justification for the inherited dictionary term. The test
now forbids the Binance and C5 **data paths** (`binance_cms`, `binance_catalog`, `binance_detail`,
`entity_resolution`, `wiki_assets`), which is what it is meant to guard. Test code only; no rule,
input or output changed.

## D4 — Collection interrupted and resumed from raw

At about 21:05 UTC on 2026-10-18 all three running jobs (the official-sources collector, the GDELT
collector and a wait loop) were terminated together by an interruption of the agent session (exit
code 4), not by a source error. ALFRED had reached vintage 2019-09-04 and GDELT timestamp E034; the
Wikipedia part had not started. Raw bytes are write-once, so the collectors were re-run unchanged:
every raw file already on disk was parsed rather than re-requested. Before resuming, the freezes were
re-verified (`pytest`, 40 passed) and every cached GDELT zip was integrity-checked (`testzip`, 0 bad).
The interim tables were rewritten in full by the resumed runs, so no partial table is used.

A second session restart (about 22:20 UTC) stopped the resumed runs again (ALFRED at vintage
2025-03-03, GDELT at E084). The third run was launched as detached Windows processes
(`Start-Process`) so that the agent session's teardown cannot stop it; the scripts are unchanged and
again parse every raw file already on disk.

## D5 — GDELT transport errors retried; genuine GDELT gaps kept as MISSING

The third GDELT run ended with 1,421 of 1,470 files OK, 12 `NETWORK_ERROR` and 37 `NO_DATA` (HTTP 404).
The collector was run a fourth time, unchanged (cached files parsed, only failed files requested):
all 12 transport failures were then received (1,433 OK). The 37 404s are files GDELT does not serve
(the whole S7 week of E034, 2020-10-20 → 26, and of E090, 2025-06-17 → 23, plus 7 files in
E002–E004 and E059). They are recorded as MISSING under the frozen rule (plan §8), never as zero.

## D6 — Plumbing written after the freeze; one debug pass on incomplete GDELT tables

The freeze pins the plan, the rules module (`scripts/h20_1_rep.py`) and the registry. The collector,
builder, audit, semantic-audit, gate and manifest scripts are plumbing that moves data through those
rules; they were finished after the freeze, and their sha256 are recorded in
`manifests/H20_1_MANIFEST.csv` instead. The rules module was not edited after the freeze
(`tests/test_h20_1.py::test_representation_freeze_matches_files` checks this).

To debug the builder and the audit, one build and one audit ran on the interim tables before the
fourth GDELT run. The tables then had 12 GDELT files missing for transport reasons. Those outputs
were overwritten by the final run. After seeing them, no dictionary, window, threshold, bar or
feature definition was changed. The only edit made after any evaluation output was a wording change
in the gate's constraint text: F12's DRIFT constraint now names its cause ("publisher category set
changed": FR type `Uncategorized Document` appears in 2020 only) instead of quoting an unrelated
denominator ratio. The eligibility outcome is unchanged.

## D7 — Semantic-audit annotator and blinding

As pre-registered (plan §12), the labels were produced by the AI research agent, not by a human. The
sheet hides the classifier's decision. Blinding is still weak, because a positive item visibly
contains the dictionary term. Every label carries a document id and an evidence span
(`evidence/H20_1_SEMANTIC_AUDIT_LABELS.csv`), and 26 judgement calls carry a written note, so a human
can re-check them. The judgement calls are: security-token items counted as crypto, a company merely
named "Blockchain" not counted, CBDC not counted as a crypto-asset, and incidental crypto mentions in
GDELT records not counted. A human re-annotation is the recommended confirmation before H20.2 relies
on these classifiers.
