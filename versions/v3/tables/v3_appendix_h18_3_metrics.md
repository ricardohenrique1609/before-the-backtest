# Table 4 — H18.3 pre-registered metrics

| gate | bar as frozen | measured | verdict |
|---|---|---|---|
| scientific support 1 | aggregate ΔPR-AUC > 0 | +0.0270 | PASS |
| scientific support 2 | cluster-bootstrap 95% CI excludes zero | [-0.0074, +0.0628], 93.45% of draws > 0 | FAIL |
| scientific support 3 | median fold ΔPR-AUC > 0 | +0.0393 | PASS |
| scientific support 4 | positive in a clear majority of folds | 8 of 8 | PASS |
| materiality 1 | relative ΔPR-AUC ≥ 10% | +13.46% | PASS |
| materiality 2 | absolute ΔPR-AUC ≥ 0.01 | +0.0270 | PASS |
| materiality 3 | top-decile lift improvement ≥ 15% | 3.9909 to 4.7899 = +20.02% | PASS |
| materiality 4 | Brier does not worsen | 0.05332 to 0.05138 | PASS |
| materiality 5 | \|calibration slope shift\| < 0.10 | 0.1948 | FAIL |
| holdout directional veto (A3) | ΔPR-AUC on the single-use holdout > 0 | baseline 0.30007, challenger 0.29254, Δ -0.00753 | FAIL |

Development pooled out-of-fold: baseline 0.20038, challenger 0.22736, over 37,782 landmarks and 440 asset-eras. Bootstrap: 2,000 replications over asset-era clusters, seed 20261010.

Verdict **NULL**, and no bar was renegotiated after the result. Criterion 5 of
materiality fails on an *improvement* in calibration, which is a defect in the bar as
the researcher wrote it; it is recorded for the next pre-registration and not patched
into this one. The verdict does not depend on it: scientific-support criterion 2 and
the holdout each fail independently.
