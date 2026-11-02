**Table 7. Primary, robustness and exploratory results (only the primary determines the verdict)**

| analysis | status | development Δ, pooled OOF | development Δ, mean of folds | LCUV Δ | note |
|---|---|---|---|---|---|
| primary: logistic, λ = 10 (A02) | primary | −0.0095 | −0.0055 | −0.0240 | verdict: PRE-REGISTERED NULL |
| CONTEXT_CORE (classifier-free), λ = 10 | robustness | +0.0003 | −0.0039 | −0.0158 | two-way CI [−0.042, +0.045]; 3 of 8 folds positive |
| logistic, fold-selected λ (the v1 primary rule) | exploratory | +0.0273 | +0.0003 | −0.0167 | λ = 1000 selected for both M0 and M2; verdict under the v1 rule: PRE-REGISTERED NULL (S4 fails) |
| LightGBM, a-priori configuration | exploratory | +0.0285 | +0.0116 | −0.0080 | 7 leaves, 200 trees for every arm; M0 pooled PR-AUC 0.174 |
| LightGBM, fold-selected | exploratory | +0.0271 | +0.0107 | −0.0030 | selected: M0 15 leaves, 200 trees; M2 7 leaves, 200 trees |
