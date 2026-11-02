"""Write paper/CLAIM_LEDGER.csv and audit the manuscript against frozen artefacts.

For every ledger row with a source pointer, the value is resolved from the frozen artefact and
compared with the value stated in the manuscript (within the row's rounding tolerance), and every
stated token must occur in manuscript_src.md. Then every numeric token in the manuscript prose must
be covered by a ledger row or by a structural allowlist, and forbidden phrasings must be absent.

Pointer syntax:
  json:<file>:<a/b/0/c>          value at a JSON path (integers index lists)
  len:<file>:<a/b>               length of a JSON list or dict
  csv:<file>:<col>=<val>:<col2>  value of col2 in the first row where col == val
  text:<file>:<substring>        the substring occurs in the frozen file

    .venv/Scripts/python "Contextual Alpha/paper/scripts/claim_audit.py"
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
CA = PAPER.parent
D, B, L, V = "H20_3_DEVELOPMENT_RESULTS.json", "H20_3_BOOTSTRAP_RESULTS.json", "H20_3_LCUV_RESULTS.json", "H20_3_VERDICT.json"
X, T, E = "H20_3_X_SEAL.json", "H20_3_TARGET_AUDIT.json", "H20_3_EXPLORATORY_RESULTS.json"
G0, G1, M1 = "H20_0_GATE.json", "H20_1_GATE.json", "H20_1_REPRESENTATION_METRICS.json"
SA, SP, MS, VR = "evidence/H20_1_SEMANTIC_AUDIT_SCORES.csv", "H20_2_TEMPORAL_SPLIT_A02.json", "H20_2_MODEL_SPEC_A02.json", "H20_2_VERDICT_RULES_A02.json"

# (id, section, claim, type, pointer, scale, check_value, tol, tokens, conf/expl, notes)
R = [
    ("C001", "Abstract;5", "five candidate context layers", "quantitative", f"len:{G0}:layers", 1, 5, 0, "five", "design", ""),
    ("C002", "Abstract;5", "three layers reconstructible (CONDITIONAL)", "quantitative", f"json:{G0}:layers/C3/layer_verdict", None, "CONDITIONAL", None, "three", "confirmatory (H20.0)", "C1, C2, C3 layer_verdict = CONDITIONAL; C4, C5 = FAIL"),
    ("C003", "Abstract;5", "C4 and C5 failed the data gate", "quantitative", f"json:{G0}:layers/C4/layer_verdict", None, "FAIL", None, "", "confirmatory (H20.0)", "C5 layer_verdict also FAIL"),
    ("C004", "Abstract;6", "25 representations built", "quantitative", "count_built", 1, 25, 0, "25", "confirmatory (H20.1)", "sum of features_built over families in H20_1_GATE.json"),
    ("C005", "Abstract;6", "18 passed the representation gate", "quantitative", f"len:{G1}:eligible_for_h20_2", 1, 18, 0, "18", "confirmatory (H20.1)", ""),
    ("C006", "Abstract;7", "23-feature market baseline", "quantitative", f"json:{X}:arms/M0/n_features", 1, 23, 0, "23", "design (H20.2)", ""),
    ("C007", "Abstract;8.3", "development PR-AUC M0 = 0.2300", "quantitative", f"json:{D}:pooled_oof/M0/pr_auc", 1, 0.2300, 5e-5, "0.2300", "confirmatory (H20.3)", ""),
    ("C008", "Abstract;8.3", "development PR-AUC M2 = 0.2205", "quantitative", f"json:{D}:pooled_oof/M2/pr_auc", 1, 0.2205, 5e-5, "0.2205", "confirmatory (H20.3)", ""),
    ("C009", "Abstract;8.3", "development Delta PR-AUC = -0.0095", "quantitative", f"json:{D}:delta_pr_auc_M2_M0", 1, -0.0095, 5e-5, "−0.0095", "confirmatory (H20.3)", ""),
    ("C010", "8.3", "relative development Delta = -4.1%", "quantitative", f"json:{D}:relative_delta", 100, -4.1, 0.05, "−4.1%", "confirmatory (H20.3)", "reported, never used alone"),
    ("C011", "Abstract;8.3", "two of eight folds positive", "quantitative", f"json:{D}:positive_folds_M2_M0", 1, 2, 0, "Two of eight", "confirmatory (H20.3)", ""),
    ("C012", "Abstract;8.3;8.4", "two-way bootstrap CI lower bound -0.0621", "quantitative", f"json:{B}:primary_M2_vs_M0/two_way/ci95/0", 1, -0.0621, 5e-5, "−0.0621;95%", "confirmatory (H20.3)", "95% percentile interval"),
    ("C013", "Abstract;8.3;8.4", "two-way bootstrap CI upper bound +0.0405", "quantitative", f"json:{B}:primary_M2_vs_M0/two_way/ci95/1", 1, 0.0405, 5e-5, "+0.0405", "confirmatory (H20.3)", ""),
    ("C014", "Abstract;8.3", "LCUV PR-AUC M0 = 0.3270", "quantitative", f"json:{L}:metrics/M0/pr_auc", 1, 0.3270, 5e-5, "0.3270", "confirmatory (H20.3)", ""),
    ("C015", "Abstract;8.3", "LCUV PR-AUC M2 = 0.3029", "quantitative", f"json:{L}:metrics/M2/pr_auc", 1, 0.3029, 5e-5, "0.3029", "confirmatory (H20.3)", ""),
    ("C016", "Abstract;8.3", "LCUV Delta PR-AUC = -0.0240", "quantitative", f"json:{L}:delta_pr_auc_M2_M0", 1, -0.0240, 5e-5, "−0.0240", "confirmatory (H20.3)", ""),
    ("C017", "8.3", "relative LCUV Delta = -7.4%", "quantitative", f"json:{L}:relative_delta", 100, -7.4, 0.05, "−7.4%", "confirmatory (H20.3)", ""),
    ("C018", "8.3", "LCUV informational interval lower -0.061", "quantitative", f"json:{L}:info_interval_two_way_asset_era_x_month/ci95/0", 1, -0.061, 5e-4, "−0.061", "confirmatory (informational)", "reported for information; not a criterion"),
    ("C019", "8.3", "LCUV informational interval upper +0.001", "quantitative", f"json:{L}:info_interval_two_way_asset_era_x_month/ci95/1", 1, 0.001, 5e-4, "+0.001", "confirmatory (informational)", ""),
    ("C020", "8.3", "S5 Brier ratio 1.033 <= 1.05", "quantitative", f"json:{L}:S5_values/brier_ratio", 1, 1.033, 5e-4, "1.033;1.05", "confirmatory (H20.3)", "bar 1.05 from H20_2_VERDICT_RULES_A02.json"),
    ("C021", "8.3", "S5 slope excess -0.044 <= 0.20", "quantitative", f"json:{L}:S5_values/slope_excess", 1, -0.044, 5e-4, "−0.044;0.20", "confirmatory (H20.3)", "bar 0.20 from H20_2_VERDICT_RULES_A02.json"),
    ("C022", "Abstract;8.4;13", "mechanical verdict PRE-REGISTERED NULL", "verdict", f"json:{V}:verdict", None, "PRE-REGISTERED NULL", None, "PRE-REGISTERED NULL", "confirmatory (H20.3)", ""),
    ("C023", "8.4", "S5, S6 pass; S1-S4, S7 fail", "verdict", f"json:{V}:criteria/S5/PASS", None, True, None, "", "confirmatory (H20.3)", "S1-S4, S7 PASS = false; S6 PASS = true"),
    ("C024", "8.4", "not NEGATIVE because development CI upper bound > 0", "verdict", f"json:{B}:primary_M2_vs_M0/two_way/ci95/1", 1, 0.0405, 5e-5, "", "confirmatory (H20.3)", "NEGATIVE requires CI upper < 0 and LCUV Delta < 0"),
    ("C025", "9", "CONTEXT_CORE development Delta +0.0003", "quantitative", f"json:{D}:delta_pr_auc_M2core_M0", 1, 0.0003, 5e-5, "+0.0003", "robustness (secondary)", ""),
    ("C026", "9", "CONTEXT_CORE two-way CI lower -0.042", "quantitative", f"json:{B}:robustness_M2core_vs_M0/two_way/ci95/0", 1, -0.042, 5e-4, "−0.042", "robustness (secondary)", ""),
    ("C027", "9", "CONTEXT_CORE two-way CI upper +0.045", "quantitative", f"json:{B}:robustness_M2core_vs_M0/two_way/ci95/1", 1, 0.045, 5e-4, "+0.045", "robustness (secondary)", ""),
    ("C028", "9", "CONTEXT_CORE LCUV Delta -0.0158", "quantitative", f"json:{L}:delta_pr_auc_M2core_M0", 1, -0.0158, 5e-5, "−0.0158", "robustness (secondary)", ""),
    ("C029", "9", "selected-lambda logistic dev Delta +0.027", "quantitative", f"json:{E}:logistic_selected_lambda/delta_dev_M2_M0", 1, 0.027, 5e-4, "+0.027", "EXPLORATORY", ""),
    ("C030", "7;9", "selected-lambda logistic LCUV Delta -0.0167", "quantitative", f"json:{E}:logistic_selected_lambda/delta_lcuv_M2_M0", 1, -0.0167, 5e-5, "−0.0167", "EXPLORATORY", ""),
    ("C031", "9", "LightGBM a-priori dev Delta +0.0285 pooled", "quantitative", f"json:{E}:lightgbm_default/delta_dev_M2_M0", 1, 0.0285, 5e-5, "+0.0285", "EXPLORATORY", ""),
    ("C032", "9", "LightGBM a-priori LCUV Delta -0.008", "quantitative", f"json:{E}:lightgbm_default/delta_lcuv_M2_M0", 1, -0.008, 5e-4, "−0.008", "EXPLORATORY", ""),
    ("C033", "9", "LightGBM selected dev Delta +0.027", "quantitative", f"json:{E}:lightgbm_selected/delta_dev_M2_M0", 1, 0.027, 5e-4, "+0.027", "EXPLORATORY", ""),
    ("C034", "9", "LightGBM selected LCUV Delta -0.003", "quantitative", f"json:{E}:lightgbm_selected/delta_lcuv_M2_M0", 1, -0.003, 5e-4, "−0.003", "EXPLORATORY", ""),
    ("C035", "10", "exploratory development gains of about +0.03", "quantitative", f"json:{E}:lightgbm_default/delta_dev_M2_M0", 1, 0.03, 5e-3, "+0.03", "EXPLORATORY", "range +0.027 to +0.029"),
    ("C036", "9", "context-only development ROC-AUC 0.540", "quantitative", f"json:{D}:pooled_oof/M1/roc_auc", 1, 0.540, 5e-4, "0.540", "secondary", ""),
    ("C037", "9", "context-only (core) development ROC-AUC 0.541", "quantitative", f"json:{D}:pooled_oof/M1_core/roc_auc", 1, 0.541, 5e-4, "0.541", "secondary", ""),
    ("C038", "8.1", "route-state disagreement 4.554% > 1% bar; fallback applied", "quantitative", "json:data/derived/h20_3/p2_audit.json:checks/P2.3_route_state_disagreement_share", 100, 4.554, 5e-4, "4.554%;1%", "confirmatory (PIT audit)", "fallback_applied = true"),
    ("C039", "8.1", "rebuilt target matched inherited y_365 on all 93,394 matched rows", "quantitative", f"json:{T}:checks/P4.5_matched_rows", 1, 93394, 0, "93,394", "confirmatory (target audit)", "agreement 1.0, 0 rows differing"),
    ("C040", "8.1", "353 decision times x 18 context features", "quantitative", f"json:{X}:decision_times", 1, 353, 0, "353", "confirmatory (H20.3 P1)", ""),
    ("C041", "8.2", "78,227 development landmark rows", "quantitative", f"json:{T}:effective_units/DEVELOPMENT/rows", 1, 78227, 0, "78,227", "confirmatory", ""),
    ("C042", "8.2;11", "110 unique development events", "quantitative", f"json:{T}:effective_units/DEVELOPMENT/unique_positive_events", 1, 110, 0, "110", "confirmatory", ""),
    ("C043", "8.2;11", "104 out-of-fold weeks", "quantitative", f"json:{D}:pooled_oof/M0/units/weeks", 1, 104, 0, "104", "confirmatory", ""),
    ("C044", "11", "86 unique LCUV events", "quantitative", f"json:{T}:effective_units/LOCKED_CONTEXT_UNSEEN_VALIDATION/unique_positive_events", 1, 86, 0, "86", "confirmatory", ""),
    ("C045", "11", "40 LCUV weeks", "quantitative", f"json:{T}:effective_units/LOCKED_CONTEXT_UNSEEN_VALIDATION/weeks", 1, 40, 0, "40", "confirmatory", ""),
    ("C046", "8.2", "one delisting labels up to 52 consecutive weekly landmarks", "methodological", f"text:{SP}:up to 52 consecutive positive", None, None, None, "52", "design", ""),
    ("C047", "5", "35 quarterly timestamps 2018-Q1 to 2026-Q3", "quantitative", "len:H20_0_SAMPLE_FREEZE.json:sample", 1, 35, 0, "35", "design (H20.0)", ""),
    ("C048", "5", "32 candidate sources registered", "quantitative", "csvrows:CONTEXT_SOURCE_REGISTRY.csv", 1, 32, 0, "32", "design (H20.0)", "H20_0_FEASIBILITY_REPORT.md states 33; the registry file has 32 rows - the file is used"),
    ("C049", "5", "141,751 documents collected", "quantitative", "json:evidence/H20_0_METRICS.json:documents_total", 1, 141751, 0, "141,751", "confirmatory (H20.0)", "H20_0_FEASIBILITY_REPORT.md states 141,732; the metrics file (sum by source) is used"),
    ("C050", "5", "version-quality bar 0.70", "quantitative", f"json:{G0}:layers/C1/criteria/G4_version/bar", 1, 0.70, 1e-9, "0.70", "design (H20.0)", ""),
    ("C051", "5", "entity-resolution bar 0.80", "methodological", f"text:{G0}:resolved >= 0.80", None, None, None, "0.80", "design (H20.0)", ""),
    ("C052", "3", "13.5% of today's items absent at t", "quantitative", "json:evidence/H20_0_METRICS.json:wiki_portal/share_of_current_items_absent_at_t", 100, 13.5, 0.05, "13.5%", "confirmatory (H20.0)", ""),
    ("C053", "3", "96.4% of pages edited after t", "quantitative", "json:evidence/H20_0_METRICS.json:wiki_portal/pages_edited_after_t", 100, 96.4, 0.05, "96.4%", "confirmatory (H20.0)", ""),
    ("C054", "5", "English crypto tag rate 0.54%", "quantitative", "csv:evidence/H20_0_BIAS_AUDITS.csv:audit=language_crypto_tag_rate:value_a", 100, 0.54, 0.005, "0.54%", "confirmatory (H20.0)", ""),
    ("C055", "5", "translingual crypto tag rate 0.14%", "quantitative", "csv:evidence/H20_0_BIAS_AUDITS.csv:audit=language_crypto_tag_rate:value_b", 100, 0.14, 0.005, "0.14%", "confirmatory (H20.0)", ""),
    ("C056", "5", "C4 version quality 0.385", "quantitative", f"json:{G0}:layers/C4/criteria/G4_version/value", 1, 0.385, 5e-4, "0.385", "confirmatory (H20.0)", ""),
    ("C057", "5", "C5 version quality 0.398", "quantitative", f"json:{G0}:layers/C5/criteria/G4_version/value", 1, 0.398, 5e-4, "0.398", "confirmatory (H20.0)", ""),
    ("C058", "5", "C5 PIT naming 0.581", "quantitative", f"json:{G0}:layers/C5/criteria/G7_entity/value", 1, 0.581, 5e-4, "0.581", "confirmatory (H20.0)", ""),
    ("C059", "3", "CFTC HTTP 429 for 2021-2026", "quantitative", "text:H20_0_FEASIBILITY_REPORT.md:2021–2026 blocked by", None, None, None, "429", "confirmatory (H20.0)", ""),
    ("C060", "6", "105 monthly evaluation timestamps", "quantitative", f"json:{M1}:n_timestamps", 1, 105, 0, "105", "design (H20.1)", ""),
    ("C061", "6", "0 PIT violations over 55,561 provenance records", "quantitative", f"json:{M1}:B_pit_integrity/provenance_rows", 1, 55561, 0, "55,561", "confirmatory (H20.1)", "total_violations = 0"),
    ("C062", "6", "semantic audit of 272 documents", "quantitative", "csvrows:evidence/H20_1_SEMANTIC_AUDIT_LABELS.csv", 1, 272, 0, "272", "confirmatory (H20.1)", "agent-produced labels"),
    ("C063", "6", "semantic precision bar 0.90", "quantitative", "json:H20_1_REPRESENTATION_FREEZE.json:gate_bars/semantic_precision", 1, 0.90, 1e-9, "0.90", "design (H20.1)", ""),
    ("C064", "3;6", "GDELT crypto tag precision 0.679", "quantitative", f"csv:{SA}:classifier=K6:precision", 1, 0.679, 5e-4, "0.679", "confirmatory (H20.1)", ""),
    ("C065", "6", "crypto-stress dictionary had no positives", "quantitative", f"csv:{SA}:classifier=K5:n_pos", 1, 0, 0, "", "confirmatory (H20.1)", ""),
    ("C066", "6", "8 C1, 9 C2, 1 C3 eligible", "quantitative", f"json:{G1}:layers/C2/n_eligible", 1, 9, 0, "", "confirmatory (H20.1)", "C1 n_eligible 8, C3 n_eligible 1"),
    ("C067", "7", "10 CONTEXT_CORE features", "quantitative", "len:H20_2_CONTEXT_SETS.json:CONTEXT_CORE", 1, 10, 0, "10", "design (H20.2)", ""),
    ("C068", "7", "single a-priori lambda = 10", "quantitative", f"json:{MS}:primary_class/lambda_primary", 1, 10, 0, "λ = 10", "design (H20.2 A02)", ""),
    ("C069", "7", "winsorisation at 0.5th / 99.5th percentiles", "methodological", f"text:{MS}:0.5th / 99.5th", None, None, None, "0.5;99.5", "design (H20.2)", ""),
    ("C070", "7", "2,000-replicate bootstrap", "quantitative", f"json:{VR}:inference/replicates", 1, 2000, 0, "2,000", "design (H20.2)", ""),
    ("C071", "7", "development landmarks 2018-01-01 to 2023-12-25", "quantitative", f"json:{SP}:blocks/DEVELOPMENT/last_landmark_monday", None, "2023-12-25", None, "2018-01-01;2023-12-25", "design (H20.2)", ""),
    ("C072", "7", "LCUV landmarks 2025-01-06 to 2025-10-06", "quantitative", f"json:{SP}:blocks/LOCKED_CONTEXT_UNSEEN_VALIDATION/first_landmark_monday", None, "2025-01-06", None, "2025-01-06;2025-10-06", "design (H20.2 A02)", ""),
    ("C073", "7", "prospective block 2025-10-13 to 2026-09-28, unopened", "quantitative", f"json:{SP}:blocks/PROSPECTIVE_CONFIRMATION/last_landmark_monday", None, "2026-09-28", None, "2025-10-13;2026-09-28", "design (H20.2)", "not built or scored in H20.3"),
    ("C074", "7", "365-day horizon and embargo", "quantitative", f"json:{SP}:horizon_days", 1, 365, 0, "365", "design (H20.2)", ""),
    ("C075", "7", "S2 requires at least five of eight positive folds", "methodological", f"text:{VR}:at least 5 of the 8", None, None, None, "five of eight", "design (H20.2)", ""),
    ("C076", "4", "GDELT file admitted 15 minutes after its stamp", "methodological", "text:scripts/h20_1_rep.py:GDELT_PUBLISH_LAG = timedelta(minutes=15)", None, None, None, "15", "design (H20.1)", ""),
    ("C077", "4", "t + 1 minute is future information", "methodological", "text:H20_1_REPRESENTATION_PLAN.md:at `t + 1 min`", None, None, None, "1", "design", ""),
    ("C078", "11", "IDRT, VAI no candles; SKY, USDS attach to no era", "quantitative", f"json:{T}:checks/P4.2_events_matching_no_era", None, ["IDRT", "SKY", "USDS", "VAI"], None, "", "confirmatory (target audit)", ""),
    ("C079", "6", "LLM, current embeddings, full-corpus TF-IDF classed NON_PIT and not built", "methodological", "text:H20_1_TRANSFORM_PIT_AUDIT.csv:NON_PIT_TRANSFORM_CANDIDATE", None, None, None, "", "confirmatory (H20.1)", ""),
    ("C080", "8.1", "X sealed before the lifecycle table was opened", "methodological", f"json:{X}:outcome_read_before_seal", None, False, None, "", "confirmatory (PIT audit)", "X seal 19:35:18 UTC < Y seal"),
    ("C081", "8.1", "primary LCUV scoring ran exactly once", "methodological", f"json:{L}:scoring_runs", 1, 1, 0, "", "confirmatory (PIT audit)", "lock file present"),
    ("C082", "7", "H20.2 amended once before outcomes (Addendum 02)", "methodological", "text:H20_2_PREREG_ADDENDUM_02.md:before any outcome was opened", None, None, None, "", "design", ""),
    ("C083", "2;12", "eight context features depend on agent-audited classifiers", "quantitative", "len:H20_2_CONTEXT_SETS.json:rules/classifier_dependence", 1, 8, 0, "Eight", "design (H20.2)", ""),
    ("C084", "10", "interpretations 1-5 (redundancy, target mismatch, cross-sectional, horizon, representation)", "interpretation", "", None, None, None, "", "interpretation", "hypotheses, not identified mechanisms; no causal claim"),
    ("C085", "3", "leakage concerns in ML-based science", "citation", "text:paper/references.bib:kapoor2023leakage", None, None, None, "", "citation", "access level recorded in the bib note"),
    ("C086", "3", "selection effects in backtesting", "citation", "text:paper/references.bib:bailey2014deflated", None, None, None, "", "citation", ""),
    ("C087", "3", "observational designs fixed before outcome data", "citation", "text:paper/references.bib:rubin2008design", None, None, None, "", "citation", ""),
    ("C088", "13", "C4/C5 remain untested", "scope", f"json:{G0}:layers/C5/layer_verdict", None, "FAIL", None, "", "scope", "DATA-GATE FAIL / UNTESTED; never described as tested"),
    ("C089", "8.3", "ROC-AUC and Brier moved in the same direction as PR-AUC", "quantitative", f"json:{L}:metrics/M2/brier", None, None, None, "", "secondary", "dev ROC 0.767->0.750, Brier 0.0512->0.0521; LCUV ROC 0.809->0.806, Brier 0.0929->0.0960 (worse for M2 in each case)"),
    ("C090", "8.1", "zero post-t context joins; complete provenance; deterministic rebuild", "methodological", "json:data/derived/h20_3/p1_audit.json:PASS", None, True, None, "", "confirmatory (PIT audit)", ""),
]
# ---- pass 2 (2026-10-19): softened wording, robustness/exploratory wording, new literature claims
R += [
    ("C091", "Abstract;13", "surviving context set did not provide evidence of incremental out-of-time predictive information", "EMPIRICAL_PROJECT", "ci0", None, True, None, "did not provide evidence of incremental", "confirmatory (H20.3)", "pass 2 SOFTENED from 'added no incremental ... information' (N02, N10); supported by NULL verdict and a development CI that includes zero"),
    ("C092", "Abstract;10;13", "both point estimates were negative; the development interval included zero", "EMPIRICAL_PROJECT", "neg2", None, True, None, "point estimates were negative", "confirmatory (H20.3)", "pass 2 added (N02, N07, N10)"),
    ("C093", "13", "absence of evidence of incremental value, not evidence that context has no effect", "INTERPRETATION", "ci0", None, True, None, "not evidence that context has no effect", "interpretation", "pass 2 added (N10)"),
    ("C094", "9", "the null pattern persists in the classifier-free robustness specification", "EMPIRICAL_PROJECT", f"json:{L}:delta_pr_auc_M2core_M0", 1, -0.0158, 5e-5, "The null pattern persists in the classifier-free robustness specification", "robustness (secondary)", "pass 2 SOFTENED from 'The primary null is therefore not produced by the agent-audited classifiers' (N04)"),
    ("C095", "9", "selected specifications' development gains did not persist in the locked block; consistent with selection optimism, does not identify overfitting", "EXPLORATORY", f"json:{E}:logistic_selected_lambda/delta_lcuv_M2_M0", 1, -0.017, 5e-4, "carry selection optimism", "EXPLORATORY", "revision 1: rewritten after the referee report; pass 2 SOFTENED from 'That is the optimism ...' (N05)"),
    ("C096", "10", "the study did not support the incremental-context hypothesis", "EMPIRICAL_PROJECT", f"json:{V}:verdict", None, "PRE-REGISTERED NULL", None, "did not support the incremental-context hypothesis", "confirmatory (H20.3)", "pass 2 SOFTENED from 'carried no incremental out-of-time information' (N07)"),
    ("C097", "10", "a linear model adds the same shift to every asset's score in a week", "INTERPRETATION", "", None, None, None, "", "interpretation", "pass 2 reworded (N08): context is constant within a week by construction (P1.8)"),
    ("C098", "12", "a scoped null is not evidence that no effect exists", "LIMITATION", "", None, None, None, "not evidence that no effect exists", "limitation", "pass 2 (N09)"),
    ("C099", "1", "Binance's current delisting FAQ lists legal/compliance, going-concern, market and ethical risk; current documentation only", "METHODOLOGICAL_LITERATURE", "verified:binance_delisting_faq", None, True, None, "current documentation", "citation", "Gap 10; not presented as historical criteria"),
    ("C100", "2;2.1;4", "language models trained on later text can carry later knowledge into historical features (look-ahead bias)", "METHODOLOGICAL_LITERATURE", "verified:glasserman2023lookahead", None, True, None, "", "citation", "Gap 4; risk only, no magnitude claimed"),
    ("C101", "2;2.1;4;6", "point-in-time language models trained only on text up to each date", "METHODOLOGICAL_LITERATURE", "verified:kelly2026pit", None, True, None, "", "citation", "Gaps 4 and 11; basis of the no-novelty decision"),
    ("C102", "2.1", "regulatory news moves crypto prices; unspecific warnings had no measurable effect; contemporaneous event study", "METHODOLOGICAL_LITERATURE", "verified:auer2018regulating", None, True, None, "", "citation", "Gap 9"),
    ("C103", "2.1", "tweet counts predicted next-day volume and realised volatility; weaker and mixed evidence for returns", "METHODOLOGICAL_LITERATURE", "verified:shen2019twitter", None, True, None, "", "citation", "Gap 9"),
    ("C104", "2.1", "Twitter predicted short-horizon altcoin returns in a short sample, selected coins, low out-of-sample fit", "METHODOLOGICAL_LITERATURE", "verified:steinert2018altcoin", None, True, None, "", "citation", "Gap 9"),
    ("C105", "2.1", "Binance delisting models include news counts/topics and social-media metrics", "METHODOLOGICAL_LITERATURE", "text:../H18_3_PREREG.md:Coinness news counts and topics", None, None, None, "", "citation", "Gap 9; Yang & Kwon Table 5 as recorded by the earlier full-text pass; not re-read"),
    ("C106", "2.1;4", "use the vintage available at the decision date rather than revised data", "METHODOLOGICAL_LITERATURE", "verified:croushore1999realtime", None, True, None, "", "citation", "Gap 3"),
    ("C107", "2.1;4;App. C", "ALFRED archives vintage versions of US economic data", "METHODOLOGICAL_LITERATURE", "verified:alfred_help", None, True, None, "", "citation", "Gap 3; official documentation"),
    ("C108", "4;App. C", "GKG records in 15-minute update batches; themes and tone assigned by GDELT", "METHODOLOGICAL_LITERATURE", "verified:gdelt_gkg_codebook_v21", None, True, None, "As our own conservative rule", "citation", "Gap 5; +15-minute admission labelled as our own rule"),
    ("C109", "7", "landmark-style design; risk set at each landmark; information available at the landmark; no survival model", "METHODOLOGICAL_LITERATURE", "verified:putter2017landmarking", None, True, None, "no survival model is fitted", "citation", "Gap 6"),
    ("C110", "7", "rolling-origin evaluation", "METHODOLOGICAL_LITERATURE", "verified:hyndman2021fpp3", None, True, None, "", "citation", "Gap 7A"),
    ("C111", "7", "embargo rationale from the paper's own label construction (no citation)", "EMPIRICAL_PROJECT", f"json:{SP}:fold_embargo_days", 1, 365, 0, "so no delisting event can label both", "design (H20.2)", "Gap 7B: no primary source readable; stated as own design rationale"),
    ("C112", "7", "PR-AUC primary; ROC summaries can mislead under heavy imbalance", "METHODOLOGICAL_LITERATURE", "verified:saito2015precision", None, True, None, "can be misleading under heavy class imbalance", "citation", "Gap 2"),
    ("C113", "7", "pigeonhole bootstrap: independent row and column resampling; adaptation disclosed; results for means; mildly conservative", "METHODOLOGICAL_LITERATURE", "verified:owen2007pigeonhole", None, True, None, "approximation, not a", "citation", "Gap 1; attribution verified, adaptation disclosed"),
    ("C114", "7", "correlation within asset and period biases conventional standard errors", "METHODOLOGICAL_LITERATURE", "verified:petersen2006standard", None, True, None, "", "citation", "Gap 8"),
    ("C115", "2", "no contribution is claimed as new", "LIMITATION", "", None, None, None, "none is claimed as new", "limitation", "Gap 11 decision"),
    ("C116", "2.1", "fixing design before outcomes; registered reports; selection across specifications; previous paper", "METHODOLOGICAL_LITERATURE", "text:paper/references.bib:jbef_registered_reports", None, None, None, "", "citation", "reused entries (rubin2008design, jbef_registered_reports, bailey2014deflated, ramossilva2026beforebacktest)"),
    ("C117", "References", "eleven reused entries; fourteen added in the verification pass", "EMPIRICAL_PROJECT", "bibcount", 1, 26, 0, "", "bibliography", "11 reused + 1 previous paper + 14 added = 26"),
    ("C118", "1", "same validated universe of 201 full-delisting events as the companion paper", "quantitative", f"json:{T}:events_in_table", 1, 201, 0, "201", "design (H18.1b)", "Before the Backtest v1.0.0 §3 reports the same 201 validated events (H18.1b)"),
    ("C119", "1", "H18.3 market-only test listed in the companion paper's registry as a pre-registered null", "citation", "text:paper/references.bib:ramossilva2026beforebacktest", None, None, None, "", "citation", "Before the Backtest v1.0.0 research registry row H18.3: PRE-REGISTERED NULL"),
    # ---- revision 1 (referee report REFEREE_REPORT_V1.md): power, penalty path, amendment, calibration, LCUV interval
    ("C120", "Abstract;7;9", "v1 / fold-selected lambda: pooled development Delta +0.0273", "quantitative", f"json:{E}:logistic_selected_lambda/delta_dev_M2_M0", 1, 0.0273, 5e-5, "+0.0273", "EXPLORATORY", "the v1 primary rule; reported because A02 replaced it before outcomes"),
    ("C121", "7", "v1 grid {0.1, 1, 10, 100, 1000}; both arms select 1000", "methodological", f"json:{E}:logistic_selected_lambda/M2/selected", 1, 1000, 0, "100;1000", "design (H20.2 v1)", "M0 also selects 1000; grid from H20_2_MODEL_SPEC.json"),
    ("C122", "7", "verdict under the v1 rule would also be PRE-REGISTERED NULL (S4 fails)", "INTERPRETATION", f"json:{E}:logistic_selected_lambda/delta_lcuv_M2_M0", 1, -0.0167, 5e-5, "would also have\nbeen PRE-REGISTERED NULL", "interpretation", "S4 requires LCUV Delta > 0"),
    ("C123", "8.3", "post-hoc standard error about 0.026 from the CI half-width", "quantitative", "se_ci", 1, 0.026, 5e-4, "0.026", "post hoc", "(hi - lo) / (2 x 1.96)"),
    ("C124", "Abstract;8.3;11", "post-hoc 80% power detectable increment about +0.07", "quantitative", "mde80", 1, 0.07, 5e-3, "+0.07;80%", "post hoc", "2.8 x SE"),
    ("C125", "8.3", "detectable increment about 30% of M0 PR-AUC", "quantitative", "mde80rel", 100, 30, 2, "30%", "post hoc", "2.8 x SE / M0 pooled PR-AUC"),
    ("C126", "7;Abstract;11", "evaluation period holds about two non-overlapping 365-day label windows", "methodological", f"json:{T}:effective_units/DEVELOPMENT/weeks", None, None, None, "two non-overlapping", "design", "104 out-of-fold weeks / 52-week label horizon = 2"),
    ("C127", "8.3", "LCUV informational interval: 3.05% of replicates positive", "quantitative", f"json:{L}:info_interval_two_way_asset_era_x_month/share_positive", 100, 3.05, 0.005, "3.05%", "informational", "two-way asset-era x month bootstrap, 2,000 replicates"),
    ("C128", "8.3", "development calibration slope M2 0.52", "quantitative", f"json:{D}:pooled_oof/M2/calibration/slope", 1, 0.52, 5e-3, "0.52", "confirmatory (H20.3)", "S5 is defined on LCUV only"),
    ("C129", "8.3", "development calibration slope M0 0.67", "quantitative", f"json:{D}:pooled_oof/M0/calibration/slope", 1, 0.67, 5e-3, "0.67", "confirmatory (H20.3)", ""),
    ("C130", "8.3", "development positive landmark rate 5.82%", "quantitative", f"json:{T}:effective_units/DEVELOPMENT/base_rate", 100, 5.82, 0.005, "5.82%", "design", "Figure 4 caption"),
    ("C131", "8.3", "LCUV positive landmark rate 11.79%", "quantitative", f"json:{T}:effective_units/LOCKED_CONTEXT_UNSEEN_VALIDATION/base_rate", 100, 11.79, 0.006, "11.79%", "design", "Figure 4 caption"),
    ("C132", "9", "CONTEXT_CORE development Delta as a mean of folds -0.0039", "quantitative", "foldmean:delta_M2core_M0", 1, -0.0039, 5e-5, "−0.0039", "robustness (secondary)", ""),
    ("C133", "9", "M0 mean-of-folds PR-AUC rises about 22% from lambda 10 to 1000", "quantitative", f"ratio:json:{E}:logistic_selected_lambda/M0/mean_fold_pr_auc_by_lambda/1000.0|json:{E}:logistic_selected_lambda/M0/mean_fold_pr_auc_by_lambda/10.0", 100, 22, 1, "22%", "EXPLORATORY", "Table 8"),
    ("C134", "9", "mean-of-folds Delta at lambda 1000 is +0.0003", "quantitative", f"diff:json:{E}:logistic_selected_lambda/M2/mean_fold_pr_auc_by_lambda/1000.0|json:{E}:logistic_selected_lambda/M0/mean_fold_pr_auc_by_lambda/1000.0", 1, 0.0003, 5e-5, "+0.0003", "EXPLORATORY", "Table 8"),
    ("C135", "9", "LightGBM a-priori development Delta +0.0116 as a mean of folds", "quantitative", f"diff:json:{E}:lightgbm_default/M2/mean_fold_pr_auc|json:{E}:lightgbm_default/M0/mean_fold_pr_auc", 1, 0.0116, 5e-5, "+0.0116", "EXPLORATORY", ""),
    ("C136", "9", "LightGBM a-priori M0 pooled development PR-AUC 0.174", "quantitative", f"json:{E}:lightgbm_default/M0/dev_pooled_oof_pr_auc", 1, 0.174, 5e-4, "0.174", "EXPLORATORY", ""),
    ("C137", "9", "LightGBM a-priori LCUV Delta -0.0080", "quantitative", f"json:{E}:lightgbm_default/delta_lcuv_M2_M0", 1, -0.0080, 5e-5, "−0.0080", "EXPLORATORY", ""),
    ("C138", "9", "LightGBM fold-selected LCUV Delta -0.0030", "quantitative", f"json:{E}:lightgbm_selected/delta_lcuv_M2_M0", 1, -0.0030, 5e-5, "−0.0030", "EXPLORATORY", ""),
    ("C139", "9", "LightGBM selection differs between arms (M0 15 leaves, M2 7 leaves)", "quantitative", f"json:{E}:lightgbm_selected/M0/config/num_leaves", 1, 15, 0, "15 leaves for M0", "EXPLORATORY", "M2 selects 7 leaves"),
    ("C140", "7;11", "no statistical-feasibility gate was run; the pre-registration did not quantify power", "LIMITATION", "text:H20_2_PREREG.md:Low effective power for context", None, None, None, "no statistical-feasibility gate", "limitation", "the prereg names low power without a number or a stop rule"),
    ("C141", "11", "no third-party timestamp for the freezes", "LIMITATION", "", None, None, None, "No third-party timestamp", "limitation", ""),
    ("C142", "Use of AI tools", "an AI coding agent executed H20.0-H20.3 and drafted the manuscript; semantic-audit labels agent-produced", "LIMITATION", "text:H20_1_EXECUTION_DEVIATIONS.md:produced by the AI research agent", None, None, None, "AI coding agent", "disclosure", ""),
]
TYPE_MAP = {"quantitative": "EMPIRICAL_PROJECT", "verdict": "EMPIRICAL_PROJECT", "methodological": "EMPIRICAL_PROJECT",
            "citation": "METHODOLOGICAL_LITERATURE", "interpretation": "INTERPRETATION", "scope": "LIMITATION"}
SANITY = ["no information", "no effect", "does not matter", "prove", "null is true", "useless", "efficient market",
          "all relevant information", "caused by", "not produced by", "no predictive", "no context effect"]
ALLOW_INT = set(range(0, 13))
FORBIDDEN = [r"untouched holdout", r"external validation", r"fully prospective", r"\bproves?\b", r"revolutionary", r"\bnovel\b",
             r"news does not work", r"context does not matter", r"markets are efficient", r"news is useless", r"profitab",
             r"(?<!Contextual )\balpha\b", r"trading strateg", r"\bP&L\b", r"\bproved\b", r"null (hypothesis )?is true",
             r"context is useless", r"all relevant information", r"has no predictive information", r"added no incremental",
             r"carried no incremental", r"not produced by"]
FORBID_ALLOWED_LINES = [r"is \*not\* an untouched holdout", r"`contextual-alpha/`"]


def resolve(ptr: str):
    if not ptr:
        return None
    if ptr == "count_built":
        g = json.loads((CA / G1).read_text(encoding="utf-8"))
        return sum(len(v["features_built"]) for v in g["families"].values())
    if ptr == "ci0":  # verdict NULL and the development two-way CI includes zero
        b = json.loads((CA / B).read_text(encoding="utf-8"))["primary_M2_vs_M0"]["two_way"]["ci95"]
        v = json.loads((CA / V).read_text(encoding="utf-8"))["verdict"]
        return v == "PRE-REGISTERED NULL" and b[0] < 0 < b[1]
    if ptr == "neg2":  # both point estimates negative and the development CI includes zero
        d = json.loads((CA / D).read_text(encoding="utf-8"))["delta_pr_auc_M2_M0"]
        lv = json.loads((CA / L).read_text(encoding="utf-8"))["delta_pr_auc_M2_M0"]
        b = json.loads((CA / B).read_text(encoding="utf-8"))["primary_M2_vs_M0"]["two_way"]["ci95"]
        return d < 0 and lv < 0 and b[0] < 0 < b[1]
    if ptr.startswith(("diff:", "ratio:")):
        kind, rest = ptr.split(":", 1)
        a, b = (resolve(x) for x in rest.split("|"))
        return a - b if kind == "diff" else a / b - 1
    if ptr.startswith("foldmean:"):
        folds = json.loads((CA / D).read_text(encoding="utf-8"))["folds"]
        key = ptr.split(":", 1)[1]
        return sum(f[key] for f in folds) / len(folds)
    if ptr in ("se_ci", "mde80", "mde80rel"):  # post-hoc yardstick from the frozen development interval
        lo, hi = json.loads((CA / B).read_text(encoding="utf-8"))["primary_M2_vs_M0"]["two_way"]["ci95"]
        se = (hi - lo) / (2 * 1.96)
        if ptr == "se_ci":
            return se
        m0 = json.loads((CA / D).read_text(encoding="utf-8"))["pooled_oof"]["M0"]["pr_auc"]
        return 2.8 * se if ptr == "mde80" else 2.8 * se / m0
    if ptr == "bibcount":
        return len(re.findall(r"^@\w+\{", (PAPER / "references.bib").read_text(encoding="utf-8"), re.M))
    if ptr.startswith("verified:"):  # key present in the bib and VERIFIED_* in REFERENCE_VERIFICATION.md
        key = ptr.split(":", 1)[1]
        ver = (PAPER / "REFERENCE_VERIFICATION.md").read_text(encoding="utf-8")
        sec = ver.split(f"### {key}\n", 1)
        in_bib = re.search(r"@\w+\{" + re.escape(key) + ",", (PAPER / "references.bib").read_text(encoding="utf-8")) is not None
        return in_bib and len(sec) == 2 and re.search(r"\| status \| VERIFIED_(FULL_TEXT|OFFICIAL_DOCUMENTATION) \|", sec[1].split("\n### ", 1)[0]) is not None
    kind, rest = ptr.split(":", 1)
    if kind == "csvrows":
        return sum(1 for _ in csv.DictReader((CA / rest).open(encoding="utf-8")))
    f, path = rest.split(":", 1)
    if kind == "text":
        return path in (CA / f).read_text(encoding="utf-8")
    if kind == "csv":
        cond, col = path.rsplit(":", 1)
        k, v = cond.split("=", 1)
        for row in csv.DictReader((CA / f).open(encoding="utf-8")):
            if row[k] == v:
                return float(row[col])
        return None
    obj = json.loads((CA / f).read_text(encoding="utf-8"))
    for p in path.split("/"):
        obj = obj[int(p)] if isinstance(obj, list) else obj[p]
    return len(obj) if kind == "len" else obj


def main() -> int:
    src = (PAPER / "manuscript_src.md").read_text(encoding="utf-8")
    rows, fails = [], []
    for cid, sec, claim, ctype, ptr, scale, chk, tol, toks, conf, notes in R:
        val = resolve(ptr)
        ok = True
        if ptr.startswith("text:"):
            ok = bool(val)
        elif ptr and chk is not None and isinstance(chk, (int, float)) and not isinstance(chk, bool):
            ok = val is not None and abs(float(val) * scale - chk) <= tol
        elif ptr and chk is not None:
            ok = val == chk
        for t in [x for x in toks.split(";") if x]:
            if t not in src:
                ok = False
                fails.append(f"{cid}: token '{t}' not in manuscript")
        if not ok:
            fails.append(f"{cid}: source {ptr} = {val!r} does not support {chk!r}")
        rows.append({"claim_id": cid, "section": sec, "claim": claim, "claim_type": "EXPLORATORY" if conf == "EXPLORATORY" else TYPE_MAP.get(ctype, ctype), "source_artifact": ptr.split(":")[1] if ":" in ptr else ptr,
                     "source_field_or_table": ptr, "confirmatory_or_exploratory": conf, "supported": "YES" if ok else "NO",
                     "notes": notes, "manuscript_tokens": toks, "resolved_value": json.dumps(val, default=str) if val is not None else ""})
    with (PAPER / "CLAIM_LEDGER.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    # ---- every numeric token in prose must be ledgered or structural
    ledger_tokens = {t for r in R for t in r[8].split(";") if t}
    body = re.sub(r"^---.*?---", "", src, flags=re.S)
    uncovered = set()
    for line in body.splitlines():
        if line.startswith("{{TABLE") or line.startswith("#"):
            continue
        line = re.sub(r"`[^`]*`", "", line)
        line = re.sub(r"\[@[^\]]*\]", "", line)
        line = re.sub(r"\d{4}-\d{2}-\d{2}", lambda m: m.group(0) if m.group(0) in src and any(m.group(0) in t for t in ledger_tokens) else "UNLEDGERED_DATE", line)
        if "UNLEDGERED_DATE" in line:
            uncovered.add("date")
        line = re.sub(r"\d{4}-\d{2}-\d{2}", "", line)
        line = re.sub(r"\b20(1[7-9]|2[0-7])(-Q\d|-\d{2})?\b", "", line)  # years / year-quarter / year-month
        line = re.sub(r"GDELT 2\.0|SHA-256|1st|0\.5th|99\.5th", "", line)
        line = re.sub(r"§\d+(\.\d+)?", "", line)  # section cross-references
        for t in re.findall(r"(?<![A-Za-z_\d])[−+\-]?\d[\d,\.]*%?", line):
            t = t.rstrip(".,")
            if t in ledger_tokens or any(t in lt for lt in ledger_tokens):
                continue
            if re.fullmatch(r"\d+", t) and int(t) in ALLOW_INT:
                continue
            uncovered.add(t)
    forb = []
    for line in src.splitlines():
        for f in FORBIDDEN:
            if re.search(f, line, re.I) and not any(re.search(a, line) for a in FORBID_ALLOWED_LINES):
                forb.append((f, line.strip()[:100]))
    sanity = [{"phrase": ph, "line": ln.strip()[:160]} for ln in src.splitlines() for ph in SANITY if ph in ln.lower()]
    lcuv_ok = "LOCKED_CONTEXT_UNSEEN_VALIDATION" in src and "prospective confirmation is pending" in src.lower()
    report = {"ledger_rows": len(rows), "supported": sum(r["supported"] == "YES" for r in rows), "failures": fails,
              "uncovered_numeric_tokens": sorted(uncovered), "forbidden_phrases": forb, "lcuv_terminology_and_pending_statement": lcuv_ok,
              "h20_4_mentioned": bool(re.search(r"H20\.4", src)), "sanity_phrase_occurrences_for_manual_review": sanity,
              "claim_types": {t: sum(r["claim_type"] == t for r in rows) for t in sorted({r["claim_type"] for r in rows})}, "PASS": not fails and not uncovered and not forb and lcuv_ok}
    (PAPER / "CLAIM_AUDIT_REPORT.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0 if report["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
