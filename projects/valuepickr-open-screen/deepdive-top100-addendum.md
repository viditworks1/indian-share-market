## Addendum: 4 new fundamentals-gap blocks (added 2026-09-11)

In addition to the existing blocks (`commitments[]`, `earnings_chain`, `market_expectation`,
`catalyst`, `value_chain`, `earnings_quality`, `growth_trajectory`, `management_quality`,
`track_record`, `quality_metrics`, `four_box`), also extract and write these 4 optional
blocks onto `data/<slug>.json` from the SAME filings you already read (3y annual reports,
~4 quarters of results/concalls, 6 months of exchange filings) — no new document layer,
just extract more from what you're already reading. Full contract, enums, and worked
example: `scripts/FUNDAMENTALS_GAP_SCHEMA.md`. All four are optional and informational only
(not yet read by any scoring script) — absence is valid, don't block a pass on missing one.

1. **`shareholding_pattern`** — from the exchange filings you're already reading (quarterly
   shareholding disclosures). Promoter %, pledge %, FII/DII %, and their trends over the
   last ~4 quarters. Set `concurrent_red_flag: true` if pledge is rising WHILE promoter
   holding is falling in the same window — flag this prominently, it's the classic
   promoter-exit signal.

2. **`working_capital`** — from the same annual report / quarterly numbers you use for
   `quality_metrics`. Inventory/receivable/payable days, cash conversion cycle, and the
   3yr trend. Note working-capital intensity relative to the sector, not in absolute terms.

3. **`sector_kpis`** — 2-4 sector-specific operating metrics from the concalls (e.g.
   capacity utilisation + realisation/tonne for cement, NIM/CASA/GNPA for a bank, ARR/NRR
   for SaaS). Whatever operating metric management itself uses to describe performance —
   don't force a generic template, follow what the company reports.

4. **`scenario_analysis`** — a NUMERIC bull/base/bear (distinct from the prose
   `bull_case[]`/`bear_case[]`, which stay as-is). For each scenario: revenue CAGR FY26-28,
   FY28 margin, FY28 EPS, exit multiple, implied price, and % vs current price. Anchor to
   the SAME FY27/FY28 estimates already in `market_expectation` when that block exists —
   don't build a second, inconsistent set of numbers. State which scenario the current
   price is closest to; it should agree with `market_expectation.gap_direction` when both
   are present.

Skip any block you can't source cleanly from primary filings rather than guessing — absent
beats wrong here, same convention as every other block in this schema.
