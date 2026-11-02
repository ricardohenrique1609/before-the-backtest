# Context Taxonomy

Five layers, defined by **who the information is about**, not by its tone or its later importance.
A document can carry more than one layer; it is stored once with a primary layer and a list of
secondary layers. Layer assignment uses only the document's own content and source, never what
happened afterwards.

| layer | scope | typical entity | example document types | candidate representation (H20.1, not chosen here) |
|---|---|---|---|---|
| **C1 — Macro** | economy-wide conditions and policy | jurisdiction, central bank | rate decisions, CPI/employment releases, financial-stress statements, macro data vintages | event flags (FOMC day), surprise vs prior vintage, counts |
| **C2 — Political / regulatory** | law, enforcement, sanctions, regulator speech | regulator, jurisdiction, named firm | rule proposals and final rules, enforcement press releases, court rulings, sanctions designations | event flags by type × jurisdiction, counts |
| **C3 — Crypto systemic** | market-wide crypto stress | the crypto market as a whole, a systemically large firm | exchange failures, stablecoin depegs, large hacks, insolvencies | counts/intensities, frozen text representations |
| **C4 — Exchange-specific** | the venue whose market data Model A uses (initially Binance) | exchange | venue announcements, listing/warning programmes, maintenance and withdrawal suspensions, regulatory actions naming the venue | event flags by notice type, counts |
| **C5 — Asset-specific** | one asset / project / ticker era | asset era (`identifier ≠ identity`) | project announcements, exploits, governance events, network changes, venue notices naming the asset, asset-specific enforcement | per-asset event flags, counts in `W7/W30` |

## Rules

1. **Layer by subject, not by consequence.** A Binance notice listing five tokens is C4 (venue
   action) with C5 secondary for each named asset era. It is not C3 because a later market move made
   it look systemic.
2. **No outcome vocabulary in the taxonomy.** There is no "negative", "scam", "collapse" or "failure"
   category. Sentiment and polarity, if ever used, are an H20.1 representation question with a frozen
   rule.
3. **Overlap is recorded, not resolved by judgement.** `context_layer` holds the primary layer by a
   fixed source→layer default (registry column `context_layer`), and `secondary_layers` lists the
   others found by fixed rules (e.g. a parenthesised ticker in a venue title adds C5).
4. **Jurisdiction is a field, not a layer.** C1 and C2 records carry `jurisdiction` (ISO country /
   `EU` / `GLOBAL`).
5. **The taxonomy can fail.** H20.0 tests each layer separately; a layer that cannot be reconstructed
   point-in-time is reported as such and is not silently merged into another.

## Status after H20.0

The per-layer feasibility verdicts are in `H20_0_FEASIBILITY_REPORT.md` §3 and `H20_0_GATE.json`.
