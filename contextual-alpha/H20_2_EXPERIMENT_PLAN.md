# H20.2 — Prospective Historical Decision Design: Experiment Plan

The design narrative behind `H20_2_PREREG.md`. Frozen together with it (`H20_2_FREEZE.json`).

## 1. Principle

At each historical decision time **t**:
1. reconstruct only what was public at **t**;
2. make the prediction that could have been made at **t**;
3. score it later against what happened in **(t, t + 365 d]**.

The scientific object is the **increment** from adding context to a strong market baseline (M2 vs
M0), not the absolute skill of either.

## 2. Why the decision time is the end of the landmark Monday

The inherited H18.3 market features are joined `as-of date ≤ w`, so they include the daily candle
dated on the landmark Monday itself. That candle is only complete at Tuesday 00:00 UTC. H20 therefore
sets **t = w + 1 d, 00:00 UTC**. This has three consequences:
- **Market data:** the Monday candle is complete at `t`, and every market input is dated ≤ `w`, so
  strictly before `t`.
- **Target:** `t < A ≤ t + 365 d` coincides, up to sub-day boundaries, with H18's `0 < days ≤ 365`.
  Because `t` is a UTC midnight, a date-only announcement is unambiguous at the start boundary.
- **Context:** the H20.1 rules apply unchanged at `t`. A Federal Register document of Monday arrives
  at Tuesday 04:00/05:00 UTC and is excluded. The ALFRED vintage is the one dated on or before the
  ET date of `t` minus one day.

H18 kept in the risk set a landmark whose announcement fell on that same Monday (`days = 0`). At `t`
that announcement is already public, so H20 excludes such landmarks.

## 3. Market baseline audit (`MARKET_FEATURE_REGISTRY.csv`)

Every H18.2/H18.3 structured feature was read from code and classified as ADMISSIBLE,
ADMISSIBLE_WITH_AUDIT or EXCLUDED:

- **Admissible as is:** 90-day dollar volume, volume trend, zero-volume frequency, realised
  volatility, trailing return, 365-day drawdown, liquidity concentration, asset age, and the calendar
  trend. All are backward-looking from candles dated ≤ `w`. Past returns are predictors only.
- **Admissible with audit:** route state, venue listings, removal intensity and route-to-peak ratio.
  They are built from symbol candle windows `[first, last]`, which treat a pair as active through any
  gap in its trading. A paused pair that resumes after `t` would be counted active at `t` using
  knowledge of the resumption. Audit P2.3 measures this against a candle-based definition and switches
  to it (frozen fallback) if disagreement exceeds 1%. Removal-based counts get the analogous
  permanence audit, P2.4.
- **Replaced:** H18.3's `asset_specific_removals_365d`, `batch_prune_removals_365d` and
  `days_since_last_signal_removal`. They exclude `QUOTE_RETIREMENT` removals, which are identified from
  Binance announcement titles. That is a C4 venue-notice input, read from the H18.1b snapshot that
  H20.0 found truncated (it produced the TRX false positive). M0 must be market data, so the
  replacements use the same backward 90-day batch rule **without** the notice override:
  `*_mkt` counts, days since the last pair removal of any class, and a never-removed indicator.
- **Excluded:**
  - current listing status;
  - whole-era quantities (`era_end`, `n_pairs_ever`);
  - every outcome column;
  - the H18.2 ±45-day classes (post-`t` classification);
  - the Monitoring Tag (venue notice, post-2023 only);
  - redundant removal counts (compactness, not outcome).

## 4. Context sets (`H20_2_CONTEXT_SETS.json`)

- **CONTEXT_EXPANDED** = the 18 H20.1-eligible features:
  - C1: 8 — Fed releases, monetary-policy releases, FOMC statement flag, CPI / UNRATE release flags,
    policy rate, CPI YoY, unemployment;
  - C2: 9 — Federal Register financial-regulator documents, crypto documents W7 / W30, crypto
    rulemaking, SEC releases, SEC enforcement, SEC crypto releases, Fed enforcement, crypto regulatory
    action flag;
  - C3: 1 — Wikipedia crypto items.
- **CONTEXT_CORE** = the 10 that use no agent-audited text classifier: C1 without the FOMC flag
  (7); C2 Federal Register financial-regulator documents, SEC releases and Fed enforcement (3). C3
  has no classifier-free feature.
- Context is market-wide: at a given `t` it is identical for every asset.
  - In the linear model it can only shift week-level risk.
  - In trees it can interact with asset state.
  - It must earn its increment against a baseline that already contains a calendar trend, venue
    listings and venue removal intensity.

## 5. H20.3 execution order (authorisation required)

1. Verify the H20.2 and H20.1 freezes (P0).
2. Build the landmark calendar from `H20_2_TEMPORAL_SPLIT.json`. Compute context at every `t`: extend
   ALFRED vintages and Wikipedia revisions with the H20.1 collector logic; Federal Register, SEC and
   Fed inputs are already on disk. Run audit P1.
3. Compute X_market at every landmark from whitelisted inherited inputs (symbol windows, asset daily,
   pair removals, candles). Run audit P2, including the fallbacks if triggered.
4. Seal and hash X.
5. Sealed target stage (P4): build y with the frozen rule and run the two value checks.
6. Development: for each arm and class, fit the grid on the 8 folds, select, and record per-fold and
   pooled OOF metrics and the bootstrap. Write and hash the pre-holdout freeze.
7. Score the holdout once.
8. Apply `H20_2_VERDICT_RULES.json` mechanically and report the verdict and annotations.
9. Stop. An action rule and costs belong to H20.4, if ever authorised.

## 6. Unresolved risks (carried, not fixed)

1. The holdout block was opened by H18.3 for market models. The context increment is untouched; the
   M0 level is not. The prospective block is the clean check, available after 2027-09-28.
2. Effective power for a week-level signal is low (104 + 40 test weeks).
3. Route-state and removal-permanence approximations (audited, with fallbacks).
4. Two target checks can only run once the lifecycle table is opened (sealed stage).
5. The semantic audit for 8 context features is agent-produced.
6. Context trends upward: Federal Register crypto documents rose about 4.5× in share. The
   calendar-trend control is linear only, so an apparent increment could be trend mis-specification.
   The era-stratified rule S7 and the within-week PR-AUC exist to expose this.
7. Fed feed and SEC listing titles are current versions (H20.0 archive condition). Wikipedia
   revisions and ALFRED vintages are immutable.
8. The base rate roughly doubles from development to holdout (inherited H18.3 accounting). PR-AUC
   levels are not comparable across blocks; only within-block Δ is interpreted.
