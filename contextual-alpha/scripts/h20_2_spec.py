"""H20.2 — the single source of every frozen specification (pre-registration of H20.3).

Nothing here reads an outcome, a return after t, a model result or any data row. The temporal split
is computed from the calendar alone. The only data-file access in H20.2 is the schema / metadata
check in h20_2_freeze.py (column names, types, row counts, null counts), never row values.

The JSON / CSV specification files are generated from this module by h20_2_freeze.py and hashed in
H20_2_FREEZE.json. A change after the freeze is an amendment, never an edit.
"""

from __future__ import annotations

from datetime import date, timedelta

SPEC_VERSION = "h20_2_v1"

# ------------------------------------------------------------------ decision time and target
LANDMARK_RULE = {
    "landmark": "ISO week, identified by its Monday date w (inherited H18.2/H18.3 weekly grid, freq W-MON from 2017-07-03)",
    "decision_time_t": "t = w + 1 day at 00:00:00 UTC, i.e. the end of the landmark Monday. Every daily market row dated w is "
                       "complete at t; nothing dated after w may enter X",
    "unit": "(asset-era, landmark t); asset-era per inherited rule A7 (a new era starts only after > 365 days with no served route)",
    "risk_set": [
        "asset-era week inside the inherited H18.2 exposure window (first served candle .. min(era end + 7 d, first delisting announcement))",
        "asset age at w >= 90 days since the era's first served candle (inherited)",
        "NEW in H20: landmark excluded if the era's delisting announcement time <= t (already public at t)",
        "t + 365 d <= administrative censor 2026-10-09 (inherited), so the last landmark is w = 2025-10-06",
    ],
}
TARGET = {
    "name": "y_365",
    "definition": "y(t, a) = 1 if asset-era a has its validated full-asset delisting ANNOUNCEMENT at time A with t < A <= t + 365 d; else 0",
    "event_source": "H18_1B_FULL_DELIST_EVENTS.parquet (frozen H18.1b lifecycle universe, 201 events); columns symbol, announcement_public_time",
    "event_time": "announcement_public_time (Binance CMS releaseDate, epoch ms -> naive UTC string, per scripts/h18_1b_discover.py); never trading_end",
    "date_only_rule": "a value without a time component denotes a UTC date D and is set to D 23:59:59 UTC (public by the end of D); "
                      "with t at a UTC midnight this makes the start boundary unambiguous",
    "parse_rule": "strict: pandas.to_datetime(value, format='ISO8601'); timezone-naive values are UTC; any value that does not parse "
                  "STOPS H20.3 as DATA / DESIGN FAILURE (no coercion to NaT, unlike H18.2)",
    "era_join": "event attaches to the asset-era of the same ticker with era_start <= A <= era_end + 30 d (inherited H18.2 rule); "
                "more than one matching era for any event STOPS H20.3 as DATA / DESIGN FAILURE; events matching no era are "
                "counted and reported as unmodellable (known: IDRT, VAI have no candles)",
    "competing_exits": "an era ending without an announcement (rebrand, merge, pair-removal-only exit) is a negative (inherited "
                       "H18.3 definition)",
    "not_used": ["y_365 / event_* / days_to_delist_announcement / ever_delisted columns of H18 panels (rebuilt instead, compared "
                 "only as a reconstruction check after X is hashed)"],
}

# ------------------------------------------------------------------ market features (section 5)
# (id, name, block, source, definition, logistic transform, status, reason / audit note, H18.3 equivalent)
MARKET = [
    ("M01", "dollar_volume_90d", "market_liquidity", "asset_daily(usd_volume)", "sum of USD volume over the 90 days ending at w (min 10 obs)", "log1p", "ADMISSIBLE", "", "dollar_volume_90d"),
    ("M02", "volume_trend", "market_liquidity", "asset_daily(usd_volume)", "log1p(30d mean USD volume) - log1p(90d mean)", "none", "ADMISSIBLE", "", "volume_trend"),
    ("M03", "zero_low_volume_freq_90d", "market_liquidity", "asset_daily(trades)", "share of days with zero trades in the 90 days ending at w", "none", "ADMISSIBLE", "", "zero_low_volume_freq_90d"),
    ("M04", "realized_vol_90d", "market_liquidity", "asset_daily(usd_close)", "std of daily log returns over the 90 days ending at w (min 20)", "none", "ADMISSIBLE", "past returns as predictor only", "realized_vol_90d"),
    ("M05", "trailing_return_90d", "market_liquidity", "asset_daily(usd_close)", "close(w) / close(w - 90 d) - 1", "none", "ADMISSIBLE", "past return as predictor only; no return after t anywhere", "trailing_return_90d"),
    ("M06", "drawdown_365d", "market_liquidity", "asset_daily(usd_close)", "close(w) / max close over the 365 days ending at w - 1", "none", "ADMISSIBLE", "", "drawdown_365d"),
    ("M07", "liquidity_concentration_90d", "market_liquidity", "asset_daily(hhi_trades)", "90-day mean of the daily trade-share HHI across routes", "none", "ADMISSIBLE", "", "liquidity_concentration_90d"),
    ("M08", "asset_age_days", "market_liquidity", "symbol_windows / era", "days from the era's first served candle to w", "log1p", "ADMISSIBLE", "era start is backward-determined", "asset_age_days"),
    ("M09", "n_active_spot_pairs", "route_state", "symbol_windows", "pairs of the era with first_candle <= w <= last_candle", "log1p", "ADMISSIBLE_WITH_AUDIT", "window-based activity ignores intra-window gaps; audit P2.3 with frozen candle-based fallback", "n_active_spot_pairs"),
    ("M10", "n_quote_assets", "route_state", "symbol_windows", "distinct quote assets among M09 pairs", "log1p", "ADMISSIBLE_WITH_AUDIT", "as M09", "n_quote_assets"),
    ("M11", "has_USDT", "route_state", "symbol_windows", "1 if an M09 pair has quote USDT", "none", "ADMISSIBLE_WITH_AUDIT", "as M09", "has_USDT"),
    ("M12", "has_USDC", "route_state", "symbol_windows", "1 if an M09 pair has quote USDC", "none", "ADMISSIBLE_WITH_AUDIT", "as M09", "has_USDC"),
    ("M13", "has_BTC", "route_state", "symbol_windows", "1 if an M09 pair has quote BTC", "none", "ADMISSIBLE_WITH_AUDIT", "as M09", "has_BTC"),
    ("M14", "has_BNB", "route_state", "symbol_windows", "1 if an M09 pair has quote BNB", "none", "ADMISSIBLE_WITH_AUDIT", "as M09", "has_BNB"),
    ("M15", "has_FDUSD", "route_state", "symbol_windows", "1 if an M09 pair has quote FDUSD (0 before FDUSD existed: a real absence, not missing)", "none", "ADMISSIBLE_WITH_AUDIT", "as M09", "has_FDUSD"),
    ("M16", "venue_listed_assets", "regime", "symbol_windows", "asset-eras with >= 1 active route at w", "log1p", "ADMISSIBLE_WITH_AUDIT", "as M09", "venue_listed_assets"),
    ("M17", "venue_removal_intensity_90d", "regime", "pair_removals_pit(removal_date)", "venue-wide pair removals in (w - 90 d, w] / venue_listed_assets", "none", "ADMISSIBLE_WITH_AUDIT", "class-free count; removal-permanence caveat (audit P2.4)", "venue_removal_intensity_90d"),
    ("M18", "time_index_years", "regime", "calendar", "(w - 2017-07-03) in years", "none", "ADMISSIBLE", "deterministic calendar trend", "time_index_years"),
    ("M19", "route_ratio_to_peak", "route_history", "symbol_windows", "M09 / running peak of M09 within the era up to w", "none", "ADMISSIBLE_WITH_AUDIT", "as M09", "route_ratio_to_peak"),
    ("M20", "days_since_last_pair_removal", "route_history", "pair_removals_pit(removal_date)", "days from the era's last pair removal <= w to w; capped at 3650; never -> 3650 with indicator M22", "log1p", "ADMISSIBLE_WITH_AUDIT", "class-free replacement for H18.3 days_since_last_signal_removal; removal-permanence caveat (P2.4)", "(replaces days_since_last_signal_removal)"),
    ("M21a", "asset_specific_removals_365d_mkt", "route_history", "pair_removals_pit(removal_date, assets_losing_this_quote_prior_90d)", "era's pair removals in (w - 365 d, w] whose backward 90-day same-quote asset count < 15", "log1p", "ADMISSIBLE_WITH_AUDIT", "notice-free class: H18.3 A1 count rule without the QUOTE_RETIREMENT override", "(replaces asset_specific_removals_365d)"),
    ("M21b", "batch_prune_removals_365d_mkt", "route_history", "pair_removals_pit(removal_date, assets_losing_this_quote_prior_90d)", "era's pair removals in (w - 365 d, w] whose backward 90-day same-quote asset count >= 15", "log1p", "ADMISSIBLE_WITH_AUDIT", "notice-free class (A1 rule only)", "(replaces batch_prune_removals_365d)"),
    ("M22", "never_had_pair_removal", "route_history", "pair_removals_pit", "1 if the era had no pair removal <= w", "none", "ADMISSIBLE", "", "(replaces never_had_signal_removal)"),
    # ---- audited and excluded
    ("X01", "days_since_last_signal_removal", "route_history", "pair_removals_pit(removal_class_pit)", "", "", "EXCLUDED", "depends on QUOTE_RETIREMENT, which is classified from Binance CMS notice titles (a C4 venue-notice input, from the truncated H18.1b snapshot; the BTT-airdrop TRX false positive); M0 must be market data only", "days_since_last_signal_removal"),
    ("X02", "asset_specific_removals_365d", "route_history", "pair_removals_pit(removal_class_pit)", "", "", "EXCLUDED", "as X01", "asset_specific_removals_365d"),
    ("X03", "batch_prune_removals_365d", "route_history", "pair_removals_pit(removal_class_pit)", "", "", "EXCLUDED", "as X01 (the QUOTE_RETIREMENT override removes removals from this class)", "batch_prune_removals_365d"),
    ("X04", "never_had_signal_removal", "route_history", "features", "", "", "EXCLUDED", "as X01", "never_had_signal_removal"),
    ("X05", "quote_retirement_removals_365d", "route_history", "asset_weeks", "", "", "EXCLUDED", "notice-derived (C4)", "quote_retirement_removals_365d"),
    ("X06", "signal_removals_90d / signal_removals_365d / fraction_routes_lost_*", "route_history", "asset_weeks", "", "", "EXCLUDED", "notice-derived class and, in asset_weeks, the H18.2 non-PIT +/-45-day class", ""),
    ("X07", "asset_specific_removals_90d (asset_weeks)", "route_history", "asset_weeks", "", "", "EXCLUDED", "H18.2 class uses up to 45 days after the removal (post-t classification)", ""),
    ("X08", "pair_removals_30d/90d/180d, route_count_peak (level)", "route_history", "asset_weeks", "", "", "EXCLUDED", "admissible in principle but not added: redundant with M19-M21 (compact set; not chosen by outcome)", ""),
    ("X09", "monitoring tag (any)", "venue_notice", "h18_2/monitoring_tag_events", "", "", "EXCLUDED", "Binance notice-derived (C4) and exists only from 2023-07-26", ""),
    ("X10", "is_live_now / any_live / known_to_exchange_info", "status", "symbol_windows / eras", "", "", "EXCLUDED", "current listing status (2026-10 harvest): future information", ""),
    ("X11", "era_end / n_pairs_ever / last_candle as a level", "status", "eras / symbol_windows", "", "", "EXCLUDED", "uses the whole era, including after t", ""),
    ("X12", "event_delist_announced_within_* / y_365 / days_to_delist_announcement / ever_delisted / followup_end / eligible_365", "outcome", "asset_weeks / landmarks / features", "", "", "EXCLUDED", "outcome or outcome-derived", ""),
    ("X13", "split / date / vdate", "bookkeeping", "features", "", "", "EXCLUDED", "bookkeeping columns, not predictors", ""),
]
MARKET_ARM_FEATURES = [m[1] for m in MARKET if m[6] in ("ADMISSIBLE", "ADMISSIBLE_WITH_AUDIT")]

# ------------------------------------------------------------------ context sets (section 6)
CONTEXT_EXPANDED = [  # exactly the 18 H20.1-eligible features (H20_1_GATE.json)
    "c1_fed_release_count_W7", "c1_fed_monetary_policy_count_W30", "c1_fomc_statement_flag_W7",
    "c1_cpi_release_flag_W7", "c1_unrate_release_flag_W7", "c1_policy_rate_asof", "c1_cpi_yoy_asof",
    "c1_unrate_asof", "c2_fedreg_finreg_doc_count_W7", "c2_fedreg_crypto_doc_count_W7",
    "c2_fedreg_crypto_doc_count_W30", "c2_fedreg_crypto_rulemaking_count_W30", "c2_sec_press_count_W7",
    "c2_sec_enforcement_count_W7", "c2_sec_crypto_press_count_W30", "c2_fed_enforcement_count_W30",
    "c2_crypto_regulatory_action_flag_W7", "c3_wiki_crypto_item_count_D7",
]
# classifier-free: no dependence on the agent-audited text classifiers K1a, K1b, K2, K3, K4
CONTEXT_CORE = [
    "c1_fed_release_count_W7", "c1_fed_monetary_policy_count_W30", "c1_cpi_release_flag_W7",
    "c1_unrate_release_flag_W7", "c1_policy_rate_asof", "c1_cpi_yoy_asof", "c1_unrate_asof",
    "c2_fedreg_finreg_doc_count_W7", "c2_sec_press_count_W7", "c2_fed_enforcement_count_W30",
]
CONTEXT_LOGISTIC_TRANSFORM = {f: ("log1p" if f.endswith(("_W7", "_W30", "_D7")) and "flag" not in f else "none")
                              for f in CONTEXT_EXPANDED}
CONTEXT_RULES = {
    "rules_module": "scripts/h20_1_rep.py (h20_1_rep_v1), unchanged; its sha256 must equal H20_1_REPRESENTATION_FREEZE.json",
    "computed_at": "every landmark decision time t = w + 1 d 00:00 UTC (not the H20.1 monthly sample); common to all assets at t",
    "sources_to_extend": "Federal Register and SEC months already collected cover every W30 window; the Fed feed bytes are reused; "
                         "ALFRED vintages and Wikipedia day-page revisions are collected for each new t with the H20.1 collector logic",
    "missing": "as H20.1 (NaN + reason, never 0); in models: train-median imputation + missing indicator (logistic), native NaN (trees)",
    "c3_scope": "the only C3 feature is generic English-Wikipedia crypto attention (count of crypto items in current-events day "
                "pages). It is NOT a systemic-crypto-state representation; no stress, failure or depeg feature survived H20.1",
    "excluded": "all GDELT features (F19-F22), CFTC (F17), F24 (redundant), F25 (stress, degenerate), any C4/C5, any LLM or "
                "embedding feature, any repaired representation",
    "classifier_dependence": {
        "c1_fomc_statement_flag_W7": "K3", "c2_fedreg_crypto_doc_count_W7": "K1b", "c2_fedreg_crypto_doc_count_W30": "K1b",
        "c2_fedreg_crypto_rulemaking_count_W30": "K1b", "c2_sec_enforcement_count_W7": "K2", "c2_sec_crypto_press_count_W30": "K1a",
        "c2_crypto_regulatory_action_flag_W7": "K1a;K1b", "c3_wiki_crypto_item_count_D7": "K4",
    },
    "annotation_disclosure": "the semantic audit behind K1a/K1b/K2/K3/K4 was produced by the AI research agent (H20.1 D7); "
                             "no human re-annotation; classifiers are not retuned",
    "drift_constraint": "c2_fedreg_crypto_rulemaking_count_W30 carries the H20.1 DRIFT constraint: era-stratified reporting is mandatory",
}

# ------------------------------------------------------------------ arms (section 7)
ARMS = {
    "M0": {"role": "PRIMARY baseline", "features": "MARKET (M01-M22, 23 columns)"},
    "M1": {"role": "secondary", "features": "CONTEXT_EXPANDED (18)"},
    "M2": {"role": "PRIMARY treatment", "features": "MARKET + CONTEXT_EXPANDED"},
    "M1_core": {"role": "robustness", "features": "CONTEXT_CORE (10)"},
    "M2_core": {"role": "robustness", "features": "MARKET + CONTEXT_CORE"},
}
PRIMARY_COMPARISON = "M2 vs M0 under the primary model class (L2 logistic): Delta PR-AUC = PR-AUC(M2) - PR-AUC(M0)"

# ------------------------------------------------------------------ models (section 8)
MODEL = {
    "primary_class": {
        "name": "L2_LOGISTIC",
        "implementation": "numpy/scipy (scipy.optimize.minimize, L-BFGS-B, gtol 1e-8, maxiter 5000); objective = sum of log-loss + "
                          "0.5 * lambda * ||beta||^2 over standardised features, intercept unpenalised",
        "hyperparameter_grid": {"lambda": [0.1, 1.0, 10.0, 100.0, 1000.0]},
        "preprocessing_order": [
            "per-feature transform from the registries (log1p or none)",
            "winsorise at the training 0.5th / 99.5th percentiles",
            "median imputation from the training rows + a <feature>_missing indicator for every feature with >= 1 missing training value",
            "standardise with training mean / sd (sd 0 -> column dropped for that fit, recorded)",
        ],
        "class_weight": "none (unweighted likelihood)",
        "calibration_policy": "no post-hoc recalibration; calibration is measured, not repaired",
        "convergence": "a fit that does not converge is retried once with maxiter 20000; a second failure is a DATA / DESIGN FAILURE",
    },
    "secondary_class": {
        "name": "LIGHTGBM",
        "implementation": "lightgbm 4.7.0, objective binary, deterministic=True, force_row_wise=True, num_threads=1, seed 20261104, "
                          "learning_rate 0.03, min_child_samples 200, subsample 0.8 (bagging_freq 1), colsample_bytree 0.8, "
                          "reg_lambda 1.0, max_bin 255, no early stopping, verbose -1",
        "hyperparameter_grid": {"num_leaves": [7, 15], "n_estimators": [200, 500]},
        "preprocessing": "raw features (no transform, no scaling); missing values passed as NaN (native handling); no indicators",
        "class_weight": "none",
        "calibration_policy": "no post-hoc recalibration",
    },
    "equal_budget_rule": "every arm gets exactly the same grid (5 lambdas; 4 tree configs), the same folds, the same preprocessing "
                         "rules and the same seeds; no arm may receive an extra search, feature selection or early stopping",
    "selection": "for each arm and class separately: the configuration with the highest mean PR-AUC over the 8 development folds; "
                 "ties broken by the stronger regularisation (larger lambda; fewer leaves, then fewer trees)",
    "final_fit": "selected configuration refit on all DEVELOPMENT landmarks; the holdout is scored once with that fit",
    "sensitivity_reported": "also at the a-priori defaults (lambda = 10; num_leaves 7 / 200 trees), to show selection optimism",
    "seeds": {"lightgbm": 20261104, "bootstrap": 20261103},
    "no_feature_selection": "no feature is dropped, added or transformed differently by any result",
}

# ------------------------------------------------------------------ temporal split (section 9)
WEEK0 = date(2017, 7, 3)
DEV = (date(2018, 1, 1), date(2023, 12, 25))
EMBARGO = (date(2024, 1, 1), date(2024, 12, 30))
HOLDOUT = (date(2025, 1, 6), date(2025, 10, 6))
PROSPECTIVE = (date(2025, 10, 13), date(2026, 9, 28))
ADMIN_CENSOR = date(2026, 10, 9)
FOLD_EMBARGO_DAYS = 365


def folds() -> list[dict]:
    """H18.3's frozen fold calendar, regenerated from its rule: expanding train from 2018-01-01, 90-day test windows from
    2022-01-03, training landmarks <= test start - 366 d, all inside DEVELOPMENT."""
    out, lo = [], date(2022, 1, 3)
    while True:
        hi = lo + timedelta(days=90)
        if hi > date(2023, 12, 31):
            break
        out.append({"fold": len(out) + 1, "train_from": DEV[0].isoformat(),
                    "train_to": (lo - timedelta(days=FOLD_EMBARGO_DAYS + 1)).isoformat(),
                    "test_from": lo.isoformat(), "test_to": hi.isoformat(), "test_era": str(lo.year)})
        lo = hi + timedelta(days=1)
    return out


def mondays(a: date, b: date) -> list[date]:
    d = a + timedelta(days=(7 - a.weekday()) % 7)
    out = []
    while d <= b:
        out.append(d)
        d += timedelta(days=7)
    return out


# ------------------------------------------------------------------ metrics (section 11)
METRICS = {
    "primary": {
        "name": "PR_AUC",
        "definition": "average precision: AP = sum_k (R_k - R_{k-1}) * P_k over distinct score thresholds in descending order, "
                      "tied scores forming one threshold; with case weights w_i (bootstrap multiplicities) every count is weighted",
        "primary_quantity": "Delta PR-AUC = PR-AUC(M2) - PR-AUC(M0) on the pooled out-of-fold development predictions (8 folds) "
                            "and, separately, on the holdout",
        "relative": "Delta / PR-AUC(M0), reported but never used alone",
        "pooling": "pooled across asset-eras and weeks of the evaluation set (as specified by the sponsor)",
    },
    "secondary": {
        "ROC_AUC": "Mann-Whitney U with average ranks for ties",
        "BRIER": "mean (p - y)^2",
        "TOP_DECILE_LIFT_XSEC": "within each evaluation week rank the risk-set assets; top decile = ceil(10%) highest; "
                                "lift = (sum of positives in weekly top deciles / their count) / (overall positive rate); "
                                "never formed by pooling weeks (inherited H18.3 section 8a)",
        "CALIBRATION": "slope and intercept of a logistic regression of y on logit(p) (unpenalised); reliability table in 10 "
                       "equal-count bins; expected calibration error reported",
        "WITHIN_WEEK_PR_AUC": "mean over weeks with >= 1 positive of the within-week PR-AUC (separates cross-sectional ranking from "
                              "calendar-regime prediction, because context is common to all assets in a week)",
        "PER_FOLD": "every metric per fold with unique events, landmark weeks and asset-eras",
        "PER_ERA": "Delta PR-AUC for 2022 folds (1-4), 2023 folds (5-8) and the 2025 holdout",
    },
    "reported_counts": "always with landmark rows, unique asset-eras, unique positive events and distinct weeks; positive "
                       "landmark weeks are never called events",
    "no_outcome_tuning": "no threshold is chosen; every metric is threshold-free except the top-decile rule fixed here",
}

# ------------------------------------------------------------------ verdict rules (section 12)
VERDICTS = {
    "closed_list": ["INCREMENTAL CONTEXT SIGNAL SUPPORTED", "PRE-REGISTERED NULL", "NEGATIVE INCREMENTAL RESULT",
                    "DATA / DESIGN FAILURE"],
    "evaluated_on": "primary comparison only (M2 vs M0, L2 logistic, selected configuration)",
    "conditions_for_support": {
        "S1": "development pooled-OOF Delta PR-AUC > 0",
        "S2": "Delta > 0 in at least 5 of the 8 development folds (a strict majority)",
        "S3": "two-way cluster (pigeonhole) bootstrap 95% percentile CI for the development pooled-OOF Delta has lower bound > 0",
        "S4": "holdout Delta PR-AUC > 0 (directional confirmation; its CI is reported, not required)",
        "S5": "no severe calibration deterioration on the holdout: Brier(M2) <= 1.05 * Brier(M0) AND |slope(M2) - 1| <= |slope(M0) - 1| + 0.20",
        "S6": "every check of H20_2_PIT_AUDIT_PLAN.md passes (0 violations)",
        "S7": "not driven by one era: Delta > 0 in at least 2 of the 3 era blocks {2022 folds, 2023 folds, 2025 holdout} AND the "
              "development pooled-OOF Delta stays > 0 when each fold is left out in turn",
    },
    "rules_in_order": [
        "DATA / DESIGN FAILURE if: S6 fails; or the sealed target checks fail (unparsable announcement time, an event matching > 1 "
        "era); or any development fold has < 5 unique positive events or the holdout has < 20; or > 20% of landmark weeks lack "
        "every context source; or a model fails to converge twice; or the holdout has to be opened more than once",
        "INCREMENTAL CONTEXT SIGNAL SUPPORTED if S1-S7 all hold",
        "NEGATIVE INCREMENTAL RESULT if the development bootstrap CI upper bound < 0 AND holdout Delta < 0",
        "PRE-REGISTERED NULL otherwise (including any CI straddling zero, any fold-majority failure, any holdout veto)",
    ],
    "annotations_not_verdicts": {
        "materiality": "MATERIAL if absolute Delta >= 0.01 AND relative Delta >= 10% on both development and holdout, else SMALL "
                       "(reported with any verdict; never converts one verdict into another)",
        "classifier_free_robustness": "M2_core vs M0 evaluated identically; if the primary verdict is SUPPORTED and M2_core fails "
                                      "S1 or S4, annotate 'support depends on agent-audited classifiers'",
        "model_class_robustness": "LightGBM M2 vs M0 evaluated identically; disagreement with the primary is annotated, never "
                                  "substituted",
        "context_only": "M1 / M1_core reported for completeness; a context-only model ranks weeks, not assets",
    },
    "never": ["no new verdict label after execution", "no switch of primary metric, model class, arm or split",
              "no claim of trading profitability (H20.4 territory)"],
}

INFERENCE = {
    "primary": "pigeonhole two-way cluster bootstrap (Owen 2007): each replicate resamples asset-eras with replacement and, "
               "independently, calendar blocks with replacement; a row's weight = (multiplicity of its asset-era) x (multiplicity "
               "of its block); weighted PR-AUC of M2 and M0 recomputed on the same weights; Delta per replicate",
    "blocks": {"development": "the 8 fold test windows (13 weeks each)", "holdout": "calendar months (10)"},
    "replicates": 2000, "seed": 20261103, "ci": "95% percentile",
    "secondary": ["asset-era-only cluster bootstrap", "time-block-only bootstrap"],
    "models_not_refit": "replicates reweight fixed out-of-fold predictions; models are not refit inside the bootstrap",
}
