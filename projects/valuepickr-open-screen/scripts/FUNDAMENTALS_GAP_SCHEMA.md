# Fundamentals-gap blocks — data contract

**Four** optional blocks added 2026-09-11 (`shareholding_pattern`, `working_capital`,
`sector_kpis`, `scenario_analysis`) on top of the existing `deepdive-top100` blocks
(`deep_dive`, `commitments[]`, `earnings_chain`, `market_expectation`, `catalyst`,
`value_chain`, `earnings_quality`, `growth_trajectory`, `management_quality`,
`track_record`, `quality_metrics`, `four_box` — see `GUIDANCE_EXPECTATION_SCHEMA.md` /
`ISHMOHIT_SIGNALS_SCHEMA.md`). Written by `deepdive-top100`'s **deep lane only**, from the
SAME filings it already reads (3y annual reports, ~4 quarters of results/concalls, 6 months
of exchange announcements) — no new document layer, just extract more from what's already
being read. **Informational only**: none of the four feed `compute_conviction_score.py`,
`compute_expectation_gap_score.py`, `compute_quality_score.py`, or `compute_master_score.py`.
All four are optional — absence is valid, and a thin SME that can't cleanly source one should
leave it absent rather than guess (same convention as every other block: absent beats wrong).

Enum handling follows the project convention: an unrecognised enum value is treated as the
**most conservative** option and the consuming code (currently just `make_stock_doc.js`)
renders it as given without erroring.

---

## 1. `shareholding_pattern`

From the exchange filings already being read (quarterly shareholding disclosures — BSE/NSE
Reg. 31 filings, or the shareholding-pattern page on screener.in / Trendlyne). Object:

```jsonc
{
  "promoter_pct": 54.2,
  "promoter_pct_trend": "stable",       // enum: "rising" | "stable" | "falling" | "unclear"
  "pledge_pct": 0,
  "pledge_pct_trend": "stable",         // enum: "rising" | "stable" | "falling" | "unclear"
  "fii_dii_pct": 12.4,
  "fii_dii_pct_trend": "rising",        // enum: "rising" | "stable" | "falling" | "unclear"
  "quarters_checked": ["Q3FY26", "Q4FY26", "Q1FY27"],   // ~4 most recent disclosed quarters, oldest->newest
  "concurrent_red_flag": false,          // bool — see below
  "note": "1-2 sentences: what moved and why, if anything"
}
```

- `pledge_pct` — 0 (not null) when the filings show no pledge; use `null` only if genuinely
  not disclosed/derivable.
- `concurrent_red_flag: true` **only** when `pledge_pct_trend == "rising"` **and**
  `promoter_pct_trend == "falling"` in the **same** window — the classic promoter-exit signal
  (rising leverage on promoter shares while the promoter is also reducing skin in the game).
  Flag this prominently in `note` when true. This does **not** by itself set `red_flag_tier`
  (that's still the forensic-tier rules in `DEEPDIVE_QUICKREF.md`) — it's a soft flag for a
  human to weigh, though a genuinely severe case should also trip `HIGH CAUTION` per the
  existing red-flag rules.
- Fewer than ~2 quarters of disclosed history (e.g. just-listed SME) → leave the whole block
  absent rather than call a trend off one data point.

---

## 2. `working_capital`

From the SAME annual-report / quarterly balance-sheet read used for `quality_metrics`. Object:

```jsonc
{
  "inventory_days": 45,
  "receivable_days": 60,
  "payable_days": 30,
  "cash_conversion_cycle": 75,           // inventory_days + receivable_days - payable_days
  "trend_3y": "elongating",              // enum: "improving" | "stable" | "elongating" | "unclear"
  "sector_relative": "in-line",          // enum: "tighter-than-sector" | "in-line" | "looser-than-sector" | "unclear"
  "note": "1-2 sentences — note working-capital intensity RELATIVE to the sector, not in absolute terms"
}
```

- `trend_3y` — direction of the cash conversion cycle over the trailing 3 years:
  `improving` (cycle shortening), `stable`, `elongating` (cycle lengthening — a cash-drag
  warning, especially alongside revenue growth), `unclear`.
- `sector_relative` — a rough peer comparison (1-2 named peers is enough, doesn't need a new
  search if the peer set from `value_chain.adjacent_peers` already gives a feel) —
  `tighter-than-sector` (better working-capital discipline than peers), `in-line`,
  `looser-than-sector` (worse — flag if paired with revenue growth, since growth funded by an
  elongating cycle burns cash faster than the P&L shows), `unclear`.
- Any one of the three day-count fields not derivable (e.g. no inventory for a pure-services
  business) → leave that field `null`, keep the rest of the block.

---

## 3. `sector_kpis`

2-4 sector-specific **operating** metrics — whatever the company itself uses on concalls to
describe performance, not a forced generic template. Array of objects:

```jsonc
[
  { "metric": "Capacity utilisation", "value": "72%, up from 58% YoY", "trend": "improving", "note": "" },
  { "metric": "Order book / TTM revenue", "value": "2.4x", "trend": "improving", "note": "up from 1.8x a year ago" },
  { "metric": "Realisation per unit", "value": "Rs 42,000/tonne", "trend": "stable", "note": "" }
]
```

- `metric` — short label, follow the company's own terminology (capacity utilisation +
  realisation/tonne for a cement/metals name; NIM/CASA/GNPA for a bank; ARR/NRR/net-revenue-
  retention for a SaaS business; order-book-to-revenue + execution velocity for an EPC/project
  name; same-store-sales + store count for retail — pick what the concall actually reports).
  `trend` is optional per-metric (`"improving"|"stable"|"declining"|"unclear"`, omit if not
  meaningful for that metric).
- Cap at 4 — pick the metrics that most directly drive the earnings chain, not everything the
  concall mentioned. A business where no such sector-specific metric is meaningfully disclosed
  (generic small-cap manufacturer, nothing beyond standard financials) → leave the array
  absent, don't force generic P&L ratios in here (those belong in `quality_metrics`).

---

## 4. `scenario_analysis`

A **numeric** bull/base/bear — distinct from the prose `bull_case[]` / `bear_case[]`, which
stay exactly as they are (this is the numbers behind the narrative, not a replacement for it).
Object:

```jsonc
{
  "bull": { "revenue_cagr_fy26_28_pct": 45, "fy28_margin_pct": 15.0, "fy28_eps": 62.0,
    "exit_multiple": 30, "implied_price": 1860, "pct_vs_cmp": 62 },
  "base": { "revenue_cagr_fy26_28_pct": 30, "fy28_margin_pct": 13.0, "fy28_eps": 48.0,
    "exit_multiple": 24, "implied_price": 1152, "pct_vs_cmp": 0 },
  "bear": { "revenue_cagr_fy26_28_pct": 15, "fy28_margin_pct": 10.5, "fy28_eps": 32.0,
    "exit_multiple": 18, "implied_price": 576, "pct_vs_cmp": -50 },
  "closest_to": "base",     // enum: "bull" | "base" | "bear" — which scenario current price sits nearest
  "note": "1-2 sentences on what has to be true for bull vs bear"
}
```

- Each scenario: `revenue_cagr_fy26_28_pct`, `fy28_margin_pct`, `fy28_eps`, `exit_multiple`,
  `implied_price`, `pct_vs_cmp` (signed, % vs current market price).
- **Anchor to the SAME FY27/FY28 estimates already in `market_expectation`** when that block
  exists — `base` should read as the numeric form of `market_expectation.our_fy28_estimate`,
  not a second, inconsistent set of assumptions. If `market_expectation` is absent this pass,
  build `scenario_analysis` from the same commitments/concall numbers `market_expectation`
  would have used.
- `closest_to` should agree with `market_expectation.gap_direction` when both blocks are
  present: `gap_direction: "priced-in"` ↔ `closest_to: "base"`; `"underestimated"` ↔ price
  sits below `bull` (market hasn't paid for it yet, i.e. `closest_to` is `bear`/`base` while
  the analyst's own view leans `bull`); `"over-optimistic"` ↔ `closest_to: "bull"` or beyond
  (price already needs the bull case). A mismatch isn't an error, just re-check both blocks'
  numbers before writing them.
- Can't build a defensible number for one leg (e.g. margin structurally undeterminable for a
  pre-revenue name) → leave the whole block absent rather than half-fill it with a guess.

---

## `make_stock_doc.js` rendering

New section **"Fundamentals-Gap Checks (shareholding · working capital · sector KPIs ·
scenario analysis)"**, placed **after** "Ishmohit-Lens Checks" and **before** "Technical
Read". Each of the four sub-blocks renders only if present, as a kv-table (`shareholding_pattern`,
`working_capital`, `scenario_analysis` — the last as three side-by-side rows, one per
scenario) or a short bullet list (`sector_kpis`). `shareholding_pattern.concurrent_red_flag ==
true` renders bold in the bear colour. Guarded by
`if (d.shareholding_pattern || d.working_capital || d.sector_kpis || d.scenario_analysis)`.

## Step placement in `deepdive-top100`

Deep lane only, same reading as the guidance + Ishmohit-lens blocks (Step 3 of the SKILL) —
extract these 4 alongside them, no new WebSearch/WebFetch budget. Never written by the light
lane (which reads only one narrow filing layer per its `missing` list, not the full 3-layer
deep read these blocks need). Skip any block that can't be sourced cleanly from what was
already read rather than spending extra searches or guessing.
