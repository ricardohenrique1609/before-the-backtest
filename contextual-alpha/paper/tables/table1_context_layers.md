**Table 1. Context layers and H20.0 data-gate status**

| layer | G4 version share | G7 entity resolution | failed criteria | severe biases | H20.0 status |
|---|---|---|---|---|---|
| C1 Macro | 0.986 | n/a | none | archive_captured_le_t:S_FED_PRESS | CONDITIONAL (reconstructible) |
| C2 Political / regulatory | 0.875 | n/a | none | archive_captured_le_t:S_FED_PRESS | CONDITIONAL (reconstructible) |
| C3 Crypto-systemic | 1.0 | n/a | none | language_crypto_tag_rate; archive_captured_le_t:S_GDELT_GKG | CONDITIONAL (reconstructible) |
| C4 Exchange-specific | 0.385 | 0.795 | G4_version, G7_entity | archive_captured_le_t:S_BINANCE_CMS | DATA-GATE FAIL / UNTESTED |
| C5 Asset-specific | 0.398 | 0.581 | G4_version, G7_entity | archive_captured_le_t:S_BINANCE_CMS; entity_popularity_any_doc_w30 | DATA-GATE FAIL / UNTESTED |
