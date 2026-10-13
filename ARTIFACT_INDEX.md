# ARTIFACT INDEX — H13 to H19.2

Every artefact the manuscript cites, by family. Paths are relative to the repository root. This
index is the reproducibility backbone: a claim in `CLAIM_EVIDENCE_MATRIX.csv` names an artefact here,
and an artefact here names the commit that created it.

**Conventions.** *Prereg* is a frozen pre-registration; a *draft* is explicitly not frozen and has no
hash. *Gate* is the machine-readable verdict. *Audit* is the human-readable data audit. Hashes exist
only where a document was frozen before execution. Historical experiment artefacts are **not
modified** by the paper work, with the single exception noted under H18.1b.

---

## Cross-family governance

| artefact | path | role |
|---|---|---|
| Hypothesis ledger | `docs/alpha_sprint/HYPOTHESIS_LEDGER.md` | one row per family with the verdict as recorded at the time |
| Idea register | `docs/alpha_sprint/IDEA_REGISTER.md` | ideas raised and their disposition |
| Decisions log | `docs/DECISIONS.md` | governance decisions, including the known H10 issue |
| Governance V2 | commit `6b2f0bc` | research governance rewritten after the H1–H7 post-mortem |

---

## H13 — net-nets and cash shells

| kind | artefact |
|---|---|
| prereg | `docs/alpha_sprint/PREREGISTRATION_H13.md` (commit `aca53bf`, written before any aggregate return) |
| red team | `H13_RED_TEAM.md` |
| discovery | `H13_CURRENT_NETNETS_2026.md`, `HIGH_RETURN_MARKETS_MAP_2026.md`, `SMALL_CAPITAL_OPPORTUNITY_SHORTLIST.md` (commit `64a4c9c`) |
| gate | `H13_NETNET_GATE.md` |
| final report | `H13_PAPER_SUMMARY.md` |
| datasets | `data/alpha_sprint/h13_results.json`, `h13_events.parquet`, `h13_fate.csv`, `h13_current.csv`, `h13_tables.md` |
| figures (pre-existing) | `data/alpha_sprint/h13_fig1_fate_by_burn.png` … `h13_fig4_equity.png` |
| scripts | `scripts/h13_universe.py`, `h13_survivorship.py`, `h13_fate.py`, `h13_prices.py`, `h13_deep.py`, `h13_dq.py`, `h13_current.py`, `h13_run.py` |
| commits | `aca53bf` (data phase, red team, prereg), `9e73558` (analysis, gate, paper summary — REJECT) |
| hash | none; H13 predates the SHA-256 freeze protocol |

## H14 — B3 deep special situations (open)

| kind | artefact |
|---|---|
| prereg | none. Pre-registration was forbidden at this phase because no hypothesis was selected |
| discovery | `H14_B3_EVENT_UNIVERSE.csv`, `H14_B3_SOURCES.md` |
| audit | `H14_B3_DATA_AUDIT.md` |
| datasets | `data/alpha_sprint/h14_universe.parquet`, `h14_audit.json`, `h14_tables.md` |
| scripts | `scripts/h14_map.py`, `h14_events.py`, `h14_download.py`, `h14_docs_probe.py`, `h14_terms_probe.py`, `h14_audit.py`, `h14_prices.py` |
| commit | `61f0bc8` |

### H14.1 — takeover-offer terms resolution

`H14_1_OPA_TERMS_AUDIT.md`, `H14_1_OPA_CASES.parquet`, `H14_1_OPA_TIMELINES.json`,
`H14_1_OPA_GOLD_SET.csv`, `data/alpha_sprint/h14_1_gate.json`, `h14_1_coverage.json`,
`h14_1_terms_summary.json`; scripts `scripts/h14_1_*.py`; commit `7c44e67`.

### H14.2 — judicial reorganisation

`H14_2_RJ_DATA_AUDIT.md`, `H14_2_RJ_GATE.json`, `H14_2_RJ_CASES.parquet`, `H14_2_RJ_EVENTS.parquet`,
`H14_2_RJ_PLAN_TERMS.parquet`, `H14_2_RJ_CAP_TABLES.parquet`, `H14_2_RJ_TIMELINES.json`,
`H14_2_RJ_GOLD_SET.csv`, `data/alpha_sprint/h14_2_*.json`; scripts `scripts/h14_2_*.py`; commit
`58bd03f`.

### H14.3 — recapitalizations and rights issues

`H14_3_DATA_AUDIT.md`, `H14_3_GATE.json`, `H14_3_RECAP_CASES.parquet`,
`H14_3_RECAP_VERSIONS.parquet`, `H14_3_RECAP_OUTCOMES.parquet`, `H14_3_RIGHTS_TERMS.parquet`,
`H14_3_CAP_TABLES.parquet`, `H14_3_TIMELINES.json`, `H14_3_GOLD_SET.csv`,
`data/alpha_sprint/h14_3_*.json`; scripts `scripts/h14_3_*.py`; commit `eabd336`.

## H15 — Schedule 13D activist event-driven

| kind | artefact |
|---|---|
| prereg | none; pre-registration was forbidden before the gate |
| audit | `H15_13D_DATA_AUDIT.md` |
| gate | `H15_13D_GATE.json` (5 of 22) |
| datasets | `H15_13D_FILINGS.parquet`, `H15_13D_AMENDMENTS.parquet`, `H15_13D_CAMPAIGNS.parquet`, `H15_13D_ITEM4.parquet`, `H15_13D_OWNERSHIP.parquet`, `H15_13D_OWNERSHIP_CAMPAIGN.parquet`, `H15_13D_OUTCOMES.parquet`, `H15_13D_TIMELINES.json` |
| gold sets | `H15_13D_GOLD_SET.csv`, `H15_13D_OUTCOME_GOLD.csv` |
| intermediates | `data/alpha_sprint/h15_*.json` |
| scripts | `scripts/h15_index.py`, `h15_fetch.py`, `h15_campaigns.py`, `h15_item4.py`, `h15_ownership.py`, `h15_outcomes.py`, `h15_linkage.py`, `h15_market.py`, `h15_gold_*.py`, `h15_outcome_gold*.py`, `h15_gate.py` |
| commit | `cb722dd` |

## H16.1 — FDA / PDUFA binary catalysts

| kind | artefact |
|---|---|
| audit | `H16_1_DATA_AUDIT.md` |
| gate | `H16_1_GATE.json` (2 of 23) |
| datasets | `H16_1_APPLICATIONS.parquet`, `H16_1_DECISION_CYCLES.parquet`, `H16_1_PDUFA_VERSIONS.parquet`, `H16_1_PIVOTAL_TRIALS.parquet`, `H16_1_REGULATORY_OUTCOMES.parquet`, `H16_1_ADCOM.parquet`, `H16_1_SPONSOR_ISSUER_MAP.parquet`, `H16_1_MARKET_COVERAGE.parquet`, `H16_1_TIMELINES.json` |
| gold sets | `H16_1_GOLD_PASS1.csv`, `H16_1_GOLD_SET.csv` (two-pass) |
| intermediates | `data/alpha_sprint/h16_1_*.json` |
| scripts | `scripts/h16_1_discover.py`, `h16_1_fetch.py`, `h16_1_cases.py`, `h16_1_fda.py`, `h16_1_trials.py`, `h16_1_adcom.py`, `h16_1_market.py`, `h16_1_gold_pass1.py`, `h16_1_gold_pass2.py`, `h16_1_gate.py` |
| commit | `dcefafe` |

## H17.0 — historical market data and survivorship

| kind | artefact |
|---|---|
| audit | `H17_0_DATA_AUDIT.md` |
| gate | `H17_0_GATE.json` (14 of 32) |
| datasets | `H17_0_ISSUER_DATE_SAMPLE.parquet`, `H17_0_SECURITY_MASTER.parquet`, `H17_0_MARKET_COVERAGE.parquet`, `H17_0_CORPORATE_ACTIONS.parquet`, `H17_0_PROVIDER_COMPARISON.parquet` |
| gold sets | `H17_0_SECURITY_GOLD.csv`, `H17_0_FATE_GOLD.csv`, `H17_0_GOLD_PASS1_FATE.csv` |
| intermediates | `data/alpha_sprint/h17_0_*.json` |
| scripts | `scripts/h17_0_seed.py`, `h17_0_actions.py`, `h17_0_fate.py`, `h17_0_market.py`, `h17_0_gold.py`, `h17_0_gate.py` |
| commit | `e96ba10` |

## H18.0 and H18.0b — venue-owned substrate

| kind | artefact |
|---|---|
| audit | `H18_0_DATA_AUDIT.md`, `H18_0B_DATA_AUDIT.md` |
| gate | `H18_0_GATE.json` (FAIL, 2 of 3 venues required), `H18_0B_GATE.json` (PASS, 14 of 14) |
| frozen sample | `H18_0_PROBE_SAMPLE.csv`, `H18_0B_FROZEN_SAMPLE.csv` (frozen before retrieval) |
| datasets | `H18_0_PROBE_RESULTS.parquet`, `H18_0B_RESULTS.parquet`, `H18_0B_ANNOUNCEMENT_UNIVERSE.parquet` |
| intermediates | `data/alpha_sprint/h18_0_probe.json`, `h18_0_announcements.json`, `h18_0_binance_surfaces.json`, `h18_0b_probe.json`, `h18_0b_universe.json`, `h18_0b_freeze.json` |
| scripts | `scripts/h18_0_probe.py`, `h18_0_announcements.py`, `h18_0_gate.py`, `h18_0b_probe.py`, `h18_0b_universe.py`, `h18_0b_freeze.py`, `h18_0b_gate.py` |
| commits | `6f7dbf4` (H18.0), `55f68ec` (H18.0b) |

## H18.1 — spot lifecycle semantic audit

| kind | artefact |
|---|---|
| audit | `H18_1_DATA_AUDIT.md` |
| gate | `H18_1_GATE.json` (11 of 12) |
| datasets | `H18_1_PAIR_EVENTS.parquet`, `H18_1_ASSET_LIFECYCLE.parquet`, `H18_1_ASSET_PAIR_STATE.parquet`, `H18_1_REASONS.parquet`, `H18_1_TIMELINES.json` |
| gold sets | `H18_1_GOLD_PASS1.csv`, `H18_1_GOLD_SET.csv` |
| intermediates | `data/alpha_sprint/h18_1_classify.json`, `h18_1_asset_state.json`, `h18_1_market.json`, `h18_1_gold.json` |
| scripts | `scripts/h18_1_classify.py`, `h18_1_asset_state.py`, `h18_1_market.py`, `h18_1_gold.py`, `h18_1_gate.py` |
| commit | `2a746cc` |

## H18.1b — full-delisting universe expansion

| kind | artefact |
|---|---|
| audit | `H18_1B_DATA_AUDIT.md` |
| gate | `H18_1B_GATE.json` (19 of 19, two named diagnostics below bar) |
| datasets | `H18_1B_FULL_DELIST_ANNOUNCEMENTS.parquet`, `H18_1B_FULL_DELIST_EVENTS.parquet`, `H18_1B_H18_1_CROSSWALK.parquet`, `H18_1B_FALSE_NEGATIVES.csv` |
| gold sets | `H18_1B_GOLD_PASS1.csv`, `H18_1B_GOLD_SET.csv` (PASS 1 persisted before PASS 2) |
| intermediates | `data/alpha_sprint/h18_1b_discover.json`, `h18_1b_discover_incomplete.json`, `h18_1b_crosswalk.json`, `h18_1b_tail.json`, `h18_1b_rebrand.json`, `h18_1b_falseneg.json`, `h18_1b_gold.json` |
| scripts | `scripts/h18_1b_discover.py`, `h18_1b_crosswalk.py`, `h18_1b_tail.py`, `h18_1b_rebrand.py`, `h18_1b_falseneg.py`, `h18_1b_gold.py`, `h18_1b_gate.py` |
| commit | `27c3283` |

`h18_1b_discover_incomplete.json` is retained deliberately: it is the refusal record written by the
coverage guard when a harvest falls below 99% of the catalog's self-reported total. The persisted
instance shows catalog 49 at 4,392 of 4,442 titles (coverage 0.9887) with page 32 blocked, so the
universe was not written. It is kept so that the guard, and what it rejected, are auditable.
`H18_1B_DATA_AUDIT.md` carries an explicit CORRECTION block about the ARK, FTM, IQ and STPT asset-era
labels — the one post-hoc edit made to a historical artefact, and it is marked as a correction rather
than a silent change.

## H18.2 — literature, mechanism and hypothesis selection

| kind | artefact |
|---|---|
| literature | `H18_2_LITERATURE_REVIEW.md` |
| mechanism | `H18_2_MECHANISM_MAP.md` (official venue sources only, deliberately not converted into features) |
| risk set | `H18_2_RISK_SET_AUDIT.md` |
| monitoring tag | `H18_2_MONITORING_TAG_AUDIT.md` |
| candidates | `H18_2_HYPOTHESIS_CANDIDATES.md` |
| decision | `H18_2_DECISION.md` (SELECT H18-P1) |
| intermediates | `data/alpha_sprint/h18_2_universe.json`, `h18_2_riskset.json`, `h18_2_monitoring_tag.json`, `h18_2_mechanism.json`, `h18_2_audit.json` |
| scripts | `scripts/h18_2_universe.py`, `h18_2_riskset.py`, `h18_2_monitoring_tag.py`, `h18_2_mechanism.py`, `h18_2_audit.py` |
| commit | `45d575d` |

## H18.3 — route contraction to landmark 365-day delisting risk

| kind | artefact | hash |
|---|---|---|
| prereg (frozen) | `H18_3_PREREG.md`, 20,128 bytes, frozen 2026-10-10 | `5a1703d8d7a17a10a453b1bee484f95ec1bdb4c3aa9cb5a03400760511360fc8` (`H18_3_PREREG.sha256`) |
| amendment 01 (frozen) | `H18_3_PREREG_AMENDMENT_01.md`, 11,204 bytes, frozen 2026-10-10 | `79e2df2253af9fa3956cf5ccad2630b8fc61dd67278acc64569f92e4f5415344` (`H18_3_PREREG_AMENDMENT_01.sha256`) |
| pre-holdout freeze | `H18_3_PRE_HOLDOUT_FREEZE.json` | `aec92fe448bc61da76774a82e9d96083cd45d0196de614e7ac825a2e1451cf5c` (`H18_3_PRE_HOLDOUT_FREEZE.sha256`) |
| draft (not frozen) | `H18_3_PREREG_DRAFT.md` | none, by design |
| PIT audit | `H18_3_PIT_AUDIT.md` (five structural checks, hard gate of zero) | — |
| development report | `H18_3_DEVELOPMENT_REPORT.md` | — |
| deviation record | `H18_3_EXECUTION_DEVIATION.md` | — |
| gate | `H18_3_GATE.json` (verdict NULL) | — |
| final report | `H18_3_FINAL_REPORT.md` | — |
| feature manifest | `H18_3_FEATURE_MANIFEST.json` | — |
| result datasets | `H18_3_ROLLING_ORIGIN_RESULTS.parquet`, `H18_3_BOOTSTRAP.parquet`, `H18_3_HOLDOUT_RESULTS.parquet` | — |
| intermediates | `data/alpha_sprint/h18_3_eligibility.json`, `h18_3_pit_audit.json`, `h18_3_development.json`, `h18_3_falsification.json`, `h18_3_cox.json`, `h18_3_missingness.json` | — |
| scripts | `scripts/h18_3_eligibility.py`, `h18_3_classes_pit.py`, `h18_3_market.py`, `h18_3_features.py`, `h18_3_fit.py`, `h18_3_holdout.py`, `h18_3_falsify.py` | — |
| commits | `522bafb` (prereg frozen), `203390b` (amendment), `4aa4180` (executed, NULL) | — |

The order is visible in the commit graph and is the point: the pre-registration and the amendment
were committed **before** the commit that contains any fitted result, and the holdout script is
separate from the development script.

## H19.0 — execution and shortability feasibility

| kind | artefact |
|---|---|
| audit | `H19_0_DATA_AUDIT.md` |
| gate | `H19_0_GATE.json` (PARTIAL PASS, 12 of 15) |
| datasets | `H19_0_DERIVATIVE_SECURITY_MASTER.parquet`, `H19_0_EVENT_DERIVATIVE_CROSSWALK.parquet`, `H19_0_EXECUTION_WINDOWS.parquet`, `H19_0_DERIVATIVE_NOTICES.parquet`, `H19_0_MARKET_COVERAGE.parquet` |
| gold sets | `H19_0_GOLD_PASS1.csv`, `H19_0_GOLD_SET.csv` |
| intermediates | `data/alpha_sprint/h19_0_probe.json`, `h19_0_build.json` |
| scripts | `scripts/h19_0_probe.py` (hand probe first), `h19_0_build.py`, `h19_0_gate.py` |
| commit | `320ce41` |

## H19.1 — derivative price discovery selection

| kind | artefact |
|---|---|
| literature | `H19_1_LITERATURE_REVIEW.md` |
| mechanism | `H19_1_PRICE_DISCOVERY_MECHANISM.md` (M1, M2, M3 with explicit rivals) |
| feasibility | `H19_1_DATA_FEASIBILITY.md` |
| control design | `H19_1_CONTROL_DESIGN.md` |
| candidates | `H19_1_HYPOTHESIS_CANDIDATES.md` |
| decision | `H19_1_DECISION.md` (SELECT H19-P3A with three pre-specified modifications) |
| draft prereg | `H19_2_PREREG_DRAFT.md` — a draft, never frozen, never hashed |
| intermediates | `data/alpha_sprint/h19_1_feasibility.json` |
| scripts | `scripts/h19_1_feasibility.py` (loads `usecols=[0, 5, 8]` only) |
| commit | `564baf8` |

## H19.2 — derivative-specific pre-delisting discovery

| kind | artefact |
|---|---|
| prereg | **none.** No pre-registration was frozen and no SHA-256 was computed |
| pre-freeze feasibility | `H19_2_PREFREEZE_FEASIBILITY.md` (verdict STOP) |
| intermediates | `data/alpha_sprint/h19_2_prefreeze.json` |
| scripts | `scripts/h19_2_prefreeze.py` (loads `usecols=[0, 5, 7, 8]`; OHLC columns never read) |
| commit | `42f35df` |

The absence of `H19_2_PREREG.md` and of any `.sha256` for it is itself the evidence that the family
stopped before freeze. The zero-return guarantee is structural: the only columns the script can see
are open time, base volume, quote volume and trade count.

## H8 — referenced only

`docs/alpha_sprint/PREREGISTRATION_H8.md`, `PREREGISTRATION_H8_2.md`, `scripts/h8_paper_run.py`,
commits `e771727`, `0e865bd`, `e6f30d4`, `032fc25`, `f0977bc`. Cited in one short section to show
that the framework does not reject everything. Performance is out of scope here and is reserved for a
separate paper.

---

## Paper artefacts (this directory)

| artefact | role |
|---|---|
| `PAPER_ARCHITECTURE.md` | thesis, contributions, outline, mapping, planned figures and tables, claim inventory, gaps |
| `CLAIM_EVIDENCE_MATRIX.csv` | every substantive numerical claim mapped to an artefact field |
| `ARTIFACT_INDEX.md` | this file |
| `PAPER_OPEN_QUESTIONS.md` | quantities the manuscript needs that are not computed, by instruction |
| `REPRODUCIBILITY_APPENDIX.md` | environment, hashes, commits, seeds, state transitions, known issues |
| `paper.md`, `paper.tex`, `references.bib` | the manuscript |
| `tables/`, `figures/` | generated from the artefacts above, by committed scripts |
