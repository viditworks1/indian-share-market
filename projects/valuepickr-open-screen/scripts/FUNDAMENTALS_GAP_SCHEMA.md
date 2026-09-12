# Shareholding / working-capital / sector-KPI / scenario-analysis schema

Four new **optional** top-level blocks on `data/<slug>.json`, added 2026-09-11 after
benchmarking the deep-dive schema against a third-party BYOK report generator
(researchtool.lkradvisors.in) that produces a fixed 13-section report per stock. Of its
13 sections, 9 were already covered here under different names (Business Overview,
Fundamentals, Thesis & Risks, `deep_dive.quarterly_trend` for Concall Summary,
`value_chain.adjacent_peers` for Competitors, `quality_metrics.capex_efficiency` +
commitments for Capacity & Capex, `value_chain.supply_side_status` for Demand & Supply).
These four were genuine gaps — nothing in the existing schema captured them. Method: same
filings `deepdive-top100` already reads (3y annual reports, exchange filings for
shareholding pattern, ~4 quarters of results for working-capital trend) — this only adds
what gets *extracted*, not a new document layer.

Ownership: written by `deepdive-top100` (deep pass); rendered by `make_stock_doc.js`.
Not read by any scoring script yet — these are informational sections, not scored inputs.
That can change later (e.g. a pledge-rising + promoter-selling combo could feed
`red_flag_tier`) but isn't wired in now — don't infer scoring behavior that isn't here.

All blocks optional. Absent = "not assessed"; `null` on a sub-field = "assessed, not
derivable from available filings" (e.g. an SME listing with no restated shareholding
history). Unrecognised enum value → most conservative option + warn, per project convention.

---

## 1. `shareholding_pattern`

```jsonc
{
  "as_of": "2026-06-30",                 // latest quarter-end the filing covers
  "promoter_pct": 55.2,
  "promoter_trend": "increasing",        // enum: increasing | stable | decreasing | unclear (vs ~4 preceding quarters)
  "pledge_pct": 0.0,                     // % of PROMOTER holding pledged (not % of total equity)
  "pledge_trend": "none",                // enum: none | falling | stable | rising | unclear
  "fii_pct": 12.3, "fii_trend": "stable",   // enum: buying | stable | selling | unclear
  "dii_pct": 8.1,  "dii_trend": "buying",   // same enum
  "public_pct": 24.4,
  "concurrent_red_flag": false,          // true only when pledge_trend=rising AND promoter_trend=decreasing in the same window — the classic exit-signal combo
  "note": "one line — what moved and why, if known from filings/concalls"
}
```

## 2. `working_capital`

```jsonc
{
  "as_of": "FY26 annual / Q1 FY27",
  "inventory_days": 30, "receivable_days": 40, "payable_days": 25,
  "cash_conversion_cycle_days": 45,      // inventory_days + receivable_days - payable_days
  "nwc_trend": "stable",                 // enum: improving | stable | deteriorating | unclear (vs ~3yr trend)
  "working_capital_intensity": "moderate",  // enum: light | moderate | heavy | unclear — relative to sector norm, not absolute
  "note": "one line — what's driving the cycle (e.g. export mix lengthening receivables, JIT inventory discipline)"
}
```

## 3. `sector_kpis`

Free-form array — sector-specific operating metrics don't fit one fixed shape (cement
cares about utilisation/realisation-per-tonne; a bank cares about NIM/CASA/GNPA; a SaaS
company cares about ARR/NRR). Each entry is one metric with a trend read, not a schema
per sector.

```jsonc
{
  "sector_label": "cement",              // free text, whatever the analyst calls the sector
  "kpis": [
    { "metric": "capacity utilisation", "value": "78%", "trend": "improving",
      "peer_comparison": "below UltraTech's ~85% and Ambuja's ~82%" },
    { "metric": "realisation per tonne", "value": "Rs 5,450", "trend": "stable",
      "peer_comparison": "in line with regional peers" }
  ],
  "note": "one line on which KPI is the swing factor for the thesis"
}
```

`trend` on each KPI: `improving` | `stable` | `declining` | `unclear`.

## 4. `scenario_analysis`

Numeric bull/base/bear — distinct from the existing prose `bull_case[]` / `bear_case[]`
arrays (those stay; this is the quantified version phreak/SOIC-style analysts build on top
of them). Anchor to the SAME FY27/FY28 estimates already in `market_expectation` where
present — don't re-derive a second, inconsistent set of numbers.

```jsonc
{
  "as_of": "2026-09-01",
  "bear": { "revenue_cagr_fy26_28_pct": 5, "fy28_margin_pct": 10, "fy28_eps": 12.5,
            "exit_multiple": 15, "implied_price": 190, "vs_cmp_pct": -20,
            "key_assumption": "utilisation stalls at current ~70%, no new order wins" },
  "base": { "revenue_cagr_fy26_28_pct": 15, "fy28_margin_pct": 13.5, "fy28_eps": 18.0,
            "exit_multiple": 22, "implied_price": 396, "vs_cmp_pct": 12,
            "key_assumption": "Karoli ramps to ~80% on schedule, Japan orders land as guided" },
  "bull":  { "revenue_cagr_fy26_28_pct": 25, "fy28_margin_pct": 15, "fy28_eps": 24.0,
            "exit_multiple": 28, "implied_price": 672, "vs_cmp_pct": 90,
            "key_assumption": "Japan run-rate scales faster + a second OEM programme lands" },
  "note": "which scenario the CURRENT price is closest to, one line (should agree with market_expectation.gap_direction if that block exists)"
}
```

`vs_cmp_pct` = (`implied_price` / current market price − 1) × 100, signed. `exit_multiple`
should use the same valuation lens as `market_expectation.valuation_tool` when that block
exists, for consistency.
