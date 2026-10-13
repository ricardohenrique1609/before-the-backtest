# Table 1 — The pre-freeze common-support audit

Inputs, computation and stop rule. The audit runs before the pre-registration is frozen and before any outcome column is opened.

| element | symbol | definition | fixed when? |
|---|---|---|---|
| event set | E | proposed treated events | before the audit |
| PIT control universe | C(t_e) | entities admissible at t_e using only information available by t_e | recomputed per event |
| matching rule | M(e, c, t) | exact strata written in full | before the audit |
| minimum controls | m | support required per event | before the audit |
| minimum events | N_min | confirmatory sample required | before the audit |
| attainable support | S_e | count of c in C(t_e) with M(e, c, t_e) = 1, over the COMPLETE pool | computed |
| support indicator | I_e | 1 if S_e >= m | computed |
| implied sample | N* | sum of I_e over events | computed |
| stop rule | — | if N* < N_min, stop before outcome access | pre-registered |
| status on stop | — | DESIGN INFEASIBLE UNDER THIS SPECIFICATION — not a null, not a rejection, hypothesis untested | — |
