**Table 5. LOCKED_CONTEXT_UNSEEN_VALIDATION (2025) results, scored once (L2 logistic, λ = 10)**

| arm | role | PR-AUC | ROC-AUC | Brier | top-decile lift (within-week) | within-week PR-AUC | calibration slope |
|---|---|---|---|---|---|---|---|
| M0 market | primary | 0.3270 | 0.809 | 0.0929 | 3.21 | 0.350 | 1.05 |
| M2 market + context | primary | 0.3029 | 0.806 | 0.0960 | 3.12 | 0.330 | 0.99 |
| M1 context only | secondary | 0.1193 | 0.506 | 0.1073 | 0.87 | 0.118 | 0.34 |
| M2_core market + CONTEXT_CORE | robustness | 0.3112 | 0.808 | 0.0972 | 3.10 | 0.337 | 1.01 |
| M1_core CONTEXT_CORE only | robustness | 0.1212 | 0.510 | 0.1091 | 0.87 | 0.118 | 1.25 |
