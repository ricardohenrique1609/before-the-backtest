**Table A1. H20.1 feature-level eligibility**

| feature_id | feature_name | layer | family | eligible_h20_2 | failed_criteria |
|---|---|---|---|---|---|
| F01 | c1_fed_release_count_W7 | C1 | R2 | True |  |
| F02 | c1_fed_monetary_policy_count_W30 | C1 | R2 | True |  |
| F03 | c1_fomc_statement_flag_W7 | C1 | R1 | True |  |
| F04 | c1_cpi_release_flag_W7 | C1 | R1 | True |  |
| F05 | c1_unrate_release_flag_W7 | C1 | R1 | True |  |
| F06 | c1_policy_rate_asof | C1 | R4 | True |  |
| F07 | c1_cpi_yoy_asof | C1 | R4 | True |  |
| F08 | c1_unrate_asof | C1 | R4 | True |  |
| F09 | c2_fedreg_finreg_doc_count_W7 | C2 | R2 | True |  |
| F10 | c2_fedreg_crypto_doc_count_W7 | C2 | R2 | True |  |
| F11 | c2_fedreg_crypto_doc_count_W30 | C2 | R2 | True |  |
| F12 | c2_fedreg_crypto_rulemaking_count_W30 | C2 | R2 | True |  |
| F13 | c2_sec_press_count_W7 | C2 | R2 | True |  |
| F14 | c2_sec_enforcement_count_W7 | C2 | R2 | True |  |
| F15 | c2_sec_crypto_press_count_W30 | C2 | R2 | True |  |
| F16 | c2_fed_enforcement_count_W30 | C2 | R2 | True |  |
| F17 | c2_cftc_press_count_W30 | C2 | R2 | False | coverage 0.314, 4 years |
| F18 | c2_crypto_regulatory_action_flag_W7 | C2 | R1 | True |  |
| F19 | c3_gdelt_crypto_record_count_S7 | C3 | R2 | False | semantic defect K6 |
| F20 | c3_gdelt_crypto_record_share_S7 | C3 | R2 | False | semantic defect K6 |
| F21 | c3_gdelt_crypto_record_share_en_S7 | C3 | R2 | False | semantic defect K6 |
| F22 | c3_gdelt_crypto_tone_mean_S7 | C3 | R3 | False | semantic defect K6 |
| F23 | c3_wiki_crypto_item_count_D7 | C3 | R2 | True |  |
| F24 | c3_wiki_crypto_item_flag_D7 | C3 | R1 | False | REDUNDANT with F23 (rho 0.9996) |
| F25 | c3_crypto_stress_flag_D7 | C3 | R1 | False | semantic defect K5; SPARSE_DEGENERATE (nonzero share 0.0) |
