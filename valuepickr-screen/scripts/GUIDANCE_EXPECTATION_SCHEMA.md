# Guidance / Commitment-Chain / Expectation-Gap schema

Defines four new top-level blocks on `data/<slug>.json`. Method and rationale:
`playbook/guidance-and-expectation-gap.md` (the 8-step Orbit Research method). This file is
the **data contract** — Phase 2 (`deepdive-top100` rework) writes it, Phase 3
(`expectation_gap_score`) reads it, `make_stock_doc.js` renders it.

Status: **Phases 1–4 built.** `deepdive-top100` writes the blocks (deep pass) and
`guidance-backfill` writes them for tier-A/B names it won't reach soon (light pass, Phase 4);
`make_stock_doc.js` renders them; `compute_expectation_gap_score.py` +
`make_expectation_gap_ranking.js` score and rank them, wired into `vpscreen-rerank` (Phase 3);
`portfolio-rs1l-revision` gates new adds on **both** scores and `regen_lists.py` writes a
catalyst calendar into `revisit-list.md` (Phase 4). All four blocks stay **optional** — a
`data/<slug>.json` without them is valid and behaves exactly as before (no
`expectation_gap_score`, listed under "not yet guidance-assessed").

---

## Ownership

| Block | Written by | Recomputed by | Notes |
|---|---|---|---|
| `commitments[]` | `deepdive-top100` (deep) / `guidance-backfill` (light) | — | replaced wholesale each pass |
| `earnings_chain` | `deepdive-top100` / `guidance-backfill` | — | replaced each pass |
| `market_expectation` | `deepdive-top100` / `guidance-backfill` (research fields) | `vpscreen-rerank` (price-derived fields only) | see per-field "recompute" column |
| `catalyst` | `deepdive-top100` / `guidance-backfill` | scoring treats an elapsed window as `lapsed` (not written back) | |

`deepdive-top100` already reads 3y annual reports + ~4 quarters of results/concalls + 6
months of exchange filings — it additionally emits these blocks instead of folding everything
into prose. `guidance-backfill` (2x/day, 4 stocks/run, `conviction_score` order) does a
**lighter pass** — latest 1–2 concalls + current multiple + one forward-estimate check — for
researched tier-A/B names (`conviction_score >= 35`, no red flag, `thesis_fit != "neither"`)
with no `market_expectation` block yet, so every portfolio-relevant name gets an
`expectation_gap_score` without waiting for `deepdive-top100`'s ~9/day crawl. When
`deepdive-top100` later reaches a name it overwrites the light blocks with its deeper version
(wholesale replacement — no conflict). Queue: `data/guidance-backfill-queue.json`
(`scripts/build_guidance_backfill_queue.py`); bookkeeping: `scripts/guidance_backfill_apply.py`.

---

## 1. `commitments[]`

Array. One entry per material management commitment found in the filings/concalls. Empty
array = "deep-dive ran, no material forward commitments found" (distinct from the key being
absent = "not yet deep-dived for guidance").

```jsonc
{
  "area": "orders",                 // enum, see below — the 8 buckets
  "text": "Japan alloy-wheel supply to Toyota-group OEM",   // <= ~20 words, management's claim
  "specifics": "Rs 70-90cr FY27, Rs 250cr FY28 run-rate",   // numbers/names as stated; "" if none given
  "timeline_bucket": "FY27",        // enum: "3M" | "6M" | "12M" | "FY27" | "FY28" | "beyond"
  "quality_stage": "commercial",    // enum: "expectation" | "action" | "operational" | "commercial" | "financial"
  "source": "Q1 FY27 concall 2026-07-XX",   // where the commitment was stated
  "dependency": "programme ramp at the customer + Karoli utilisation headroom",  // what it relies on; "" if none
  "single_point_of_failure": "programme/ramp execution",    // the one thing to monitor; "" if diversified
  "thesis_critical": true           // bool — is this one of the 1-2 commitments the investment case hinges on?
}
```

### `area` enum (the 8 buckets)

`growth` · `capacity` · `orders` · `margin` · `capex` · `balance_sheet` · `strategy` ·
`new_business`

(Mapping to the report's classification: `orders` covers "Orders / Commercialisation";
`margin` covers "Margin & Earnings"; `new_business` is a distinct new revenue stream, kept
separate from `growth` on purpose so Step 2 can connect it along the new-product chain.)

### `quality_stage` enum + ordinal (Step 3 ladder)

| value | ordinal | test |
|---|---|---|
| `expectation` | 1 | management says it will happen — a target/guidance/aspiration, nothing committed |
| `action` | 2 | capital or resources committed, a concrete step taken (capex raised, order placed, approval filed) |
| `operational` | 3 | capacity/process/product becoming operational — dated commissioning schedule, line running |
| `commercial` | 4 | a customer/order/commercial activity validates demand — order booked, first shipment, programme won |
| `financial` | 5 | already visible in a reported quarter's revenue/EBITDA/PAT/cash |

Rule: a *delivered* result outranks a *future financial target*. If management has a "FY27
EBITDA 14%" target that is still a forecast, that commitment is `expectation` (an earnings
target), **not** `financial`. `financial` requires the number to have shown up in an actual
reported period.

### Null / missing handling

- Key absent → stock not yet guidance-deep-dived. Neutral; no effect on any score.
- `[]` → deep-dived, nothing material. `evidence_quality` downstream = `none`.
- Any enum field unrecognised → treated as the **most conservative** value
  (`quality_stage` → `expectation`; `timeline_bucket` → `beyond`) and the script logs a
  warning, same convention as `compute_conviction_score.py`.

---

## 2. `earnings_chain`

Object. The connected sequence from Step 2 + Step 5, and where it can break (Step 6).

```jsonc
{
  "chain": ["new programmes/orders", "capacity ramp (Karoli ~80% util)",
            "revenue growth", "operating leverage", "EBITDA margin 13.5-14%", "PAT"],
  "bottleneck_link": "capacity ramp (Karoli ~80% util)",   // which link in `chain` is the constraint
  "operating_leverage": "yes — mgmt guides EBITDA margin up ~150bps on mix + utilisation, i.e. EBITDA growing faster than revenue",
  "evidenced_links": ["new programmes/orders", "capacity ramp (Karoli ~80% util)"],  // links backed by commercial/financial-stage evidence
  "assumed_links": ["operating leverage", "EBITDA margin 13.5-14%"]                    // links still resting on expectation/action-stage evidence
}
```

More `evidenced_links` relative to `assumed_links` = a stronger case. Phase 3 uses the
ratio as a cross-check on `market_expectation.evidence_quality`.

---

## 3. `market_expectation`

Object. Step 7 — what the price already assumes vs. our path.

```jsonc
{
  "as_of": "2026-08-30",              // date the price-derived fields were last set
  "price": 812.0,                     // recompute: vpscreen-rerank
  "current_pe": 34.0,                 // recompute: vpscreen-rerank (price / trailing EPS)
  "current_ev_ebitda": 19.0,         // recompute: vpscreen-rerank where obtainable, else null
  "valuation_tool": "P/E",           // which multiple is the right lens for this business: "P/E" | "EV/EBITDA" | "P/B" | "other"
  "implied_growth_cagr": "~20% EPS CAGR FY26-FY28 to justify 34x at a 22x exit",  // reverse-engineered, prose ok
  "our_fy27_estimate": "Revenue +high-teens, EBITDA margin ~13.5-14%, PAT +25-30%",
  "our_fy28_estimate": "second leg from Japan run-rate + full Karoli utilisation",
  "gap_direction": "underestimated",  // enum: "priced-in" | "partially-priced" | "underestimated" | "over-optimistic"
  "gap_type": "margin",               // enum: "volume" | "capacity" | "mix" | "margin" | "timing" | "duration" | "new_business"
  "gap_magnitude_pct": 15,            // our FY28 PAT vs implied FY28 PAT, % — signed; null if not estimable
  "gap_basis": "operating leverage from utilisation + Japan mix not in the current multiple; market pricing flat margins",
  "evidence_quality": "strong",       // enum: "strong" | "moderate" | "monitor" | "weak" | "none" — see derivation
  "data_caveat": "no broker consensus; implied path is a reverse-P/E estimate + screener.in forward figures + VP thread view"
}
```

### `gap_direction` enum (Step 7)

`priced-in` · `partially-priced` · `underestimated` · `over-optimistic`
(`over-optimistic` → Phase 3 sets `expectation_gap_score` to 0 and raises a "no edge" flag.)

### `gap_type` enum (Step 8)

`volume` · `capacity` · `mix` · `margin` · `timing` · `duration` · `new_business`

### `evidence_quality` — derivation rule (not free choice)

Derive from the **furthest-right `quality_stage`** among `commitments[]` entries with
`thesis_critical: true`:

| furthest-right thesis-critical stage | `evidence_quality` |
|---|---|
| `financial` or `commercial` | `strong` |
| `operational` | `moderate` |
| `action` | `monitor` |
| `expectation` only | `weak` |
| no thesis-critical commitment / `commitments: []` | `none` |

Downgrade one notch if `earnings_chain.assumed_links` outnumbers `evidenced_links`.

### Recompute cadence

`vpscreen-rerank` refreshes `price`, `current_pe`, `current_ev_ebitda`, `as_of` from live
Yahoo/screener data every cycle and **may flip `gap_direction`** (`underestimated` →
`partially-priced` → `priced-in`) as price rises toward the implied path — with no new
research. It does **not** touch `our_*_estimate`, `gap_type`, `gap_basis`, `evidence_quality`
— those only change on a `deepdive-top100` pass.

---

## 4. `catalyst`

Object. Step 8 — the event that makes the market re-recognise the gap.

```jsonc
{
  "event": "Japan programme first shipments + Q2/Q3 FY27 margin print showing the step-up",
  "expected_window_months": 9,        // integer months from `as_of`; the milestone-cluster window from Step 4
  "window_start": "2026-08-30",       // = market_expectation.as_of at time of writing
  "evidence_quality": "high",         // enum: "high" | "med" | "low" — how concrete/dated the event is
  "is_dated": true,                   // bool — is there an actual date/quarter on record, vs. "sometime in FY27"?
  "status": "pending"                 // enum: "pending" | "in-progress" | "hit" | "missed" | "lapsed"
}
```

Scoring treats a `pending`/`in-progress` catalyst as **effectively `lapsed`** once
`window_start + expected_window_months` is in the past (not written back to the data file —
the next deep-dive/backfill pass refreshes the real block); an effectively-lapsed catalyst
zeroes the `catalyst_q` term. `compute_expectation_gap_score.py` emits a `catalyst_calendar`
array in `data/expectation-gap-scores.json` (each scored stock's `event` + computed
`target_date`, soonest first), and `regen_lists.py` renders it as a **"## Catalyst calendar"**
section at the bottom of `revisit-list.md` — split into "Overdue / due — re-check now" and
"Upcoming". `portfolio-rs1l-revision` cross-checks that section: a holding whose catalyst row
is past its date with status still `pending` is flagged as a monitorable (re-underwrite), not
an automatic exit.

---

## Worked example — ASK Automotive (the report's running example; illustrative, not researched here)

```jsonc
{
  "commitments": [
    { "area": "growth", "text": "high-teens FY27 revenue growth; exports >20%",
      "specifics": "core + export", "timeline_bucket": "FY27", "quality_stage": "expectation",
      "source": "FY26 concall", "dependency": "programme wins + capacity", "single_point_of_failure": "",
      "thesis_critical": false },
    { "area": "capex", "text": "FY27 capex raised to ~Rs 700cr",
      "specifics": "from Rs 450-500cr", "timeline_bucket": "FY27", "quality_stage": "action",
      "source": "FY26 concall", "dependency": "", "single_point_of_failure": "ramp-up",
      "thesis_critical": false },
    { "area": "capacity", "text": "Karoli utilisation to ~80%",
      "specifics": "existing + new lines", "timeline_bucket": "6M", "quality_stage": "operational",
      "source": "Q1 FY27 concall", "dependency": "programme ramp", "single_point_of_failure": "utilisation ramp speed",
      "thesis_critical": true },
    { "area": "orders", "text": "Japan alloy-wheel + Ford export programmes",
      "specifics": "Rs 70-90cr + Rs 40-45cr FY27", "timeline_bucket": "FY27", "quality_stage": "commercial",
      "source": "Q1 FY27 concall", "dependency": "customer programme ramp", "single_point_of_failure": "programme/ramp execution",
      "thesis_critical": true },
    { "area": "margin", "text": "EBITDA margin recovery to 13.5-14%",
      "specifics": "scale + mix", "timeline_bucket": "FY27", "quality_stage": "expectation",
      "source": "FY26 concall", "dependency": "utilisation + mix", "single_point_of_failure": "",
      "thesis_critical": true }
  ],
  "earnings_chain": {
    "chain": ["new programmes/orders", "capacity ramp (Karoli ~80%)", "revenue growth",
              "operating leverage", "EBITDA margin 13.5-14%", "PAT"],
    "bottleneck_link": "capacity ramp (Karoli ~80%)",
    "operating_leverage": "yes — margin guided up on utilisation + mix",
    "evidenced_links": ["new programmes/orders", "capacity ramp (Karoli ~80%)"],
    "assumed_links": ["operating leverage", "EBITDA margin 13.5-14%"]
  },
  "market_expectation": {
    "as_of": "2026-08-30", "price": null, "current_pe": null, "current_ev_ebitda": null,
    "valuation_tool": "P/E",
    "implied_growth_cagr": "market appears to price continued growth + steady margins",
    "our_fy27_estimate": "revenue high-teens, margin toward 13.5-14%, PAT +25-30%",
    "our_fy28_estimate": "second leg from Japan run-rate (Rs 250cr) + full Karoli utilisation",
    "gap_direction": "partially-priced", "gap_type": "margin", "gap_magnitude_pct": null,
    "gap_basis": "operating leverage from utilisation not fully in the multiple; market pricing flat margins",
    "evidence_quality": "strong",
    "data_caveat": "no broker consensus; reverse-P/E + screener.in + VP view"
  },
  "catalyst": {
    "event": "Japan programme first shipments + a Q2/Q3 FY27 margin print showing the step-up",
    "expected_window_months": 9, "window_start": "2026-08-30",
    "evidence_quality": "med", "is_dated": false, "status": "pending"
  }
}
```

---

## `make_stock_doc.js` rendering (Phase 2)

New section **"Guidance & Expectation Gap"**, placed after "Deep-Dive: Primary Documents"
and before "Technical Read":

1. **Commitment ladder table** — columns: Area · Commitment · Specifics · By when · Stage ·
   Thesis-critical. Sort thesis-critical first, then by `quality_stage` ordinal descending
   (most-proven at the top).
2. **Earnings chain** — the `chain` rendered as `A → B → C`, with `bottleneck_link` bolded
   and a line noting evidenced vs. assumed links.
3. **Market expectation** — kv-table of `market_expectation` (price-derived fields +
   `gap_direction` / `gap_type` / `gap_basis` / `evidence_quality`), with `data_caveat` as a
   muted footnote.
4. **Catalyst** — one line: event, window, `is_dated`, `status`.

All four blocks guarded by `if (d.commitments && d.commitments.length)` etc. so old docs
render unchanged.

---

## Phase 3 consumption (`expectation_gap_score`, BUILT — `scripts/compute_expectation_gap_score.py`)

Mechanical, deterministic, no network — same discipline as `compute_conviction_score.py`.
The as-built formula (the script's docstring is the source of truth):

```
gap_points  0-40   base by gap_direction: underestimated 28 / partially-priced 18 / priced-in 4
                   / over-optimistic 0 ; + min(12, |gap_magnitude_pct| * 0.5) for the first two
gap_frac    = gap_points / 40

quality  = 0.35 * evidence_q + 0.30 * catalyst_q + 0.20 * timing_q + 0.15 * risk_q   (each in [0,1])
  evidence_q  strong 1.0 / moderate 0.75 / monitor 0.5 / weak 0.25 / none 0.05
  catalyst_q  high 1.0 / med 0.65 / low 0.35 (of catalyst.evidence_quality);  x0.6 if not is_dated;
              x0 if effective status "lapsed", x0.3 if "missed";  0.15 if no catalyst at all
  timing_q    window <=6M 1.0 / <=12M 0.75 / <=18M 0.45 / >18M 0.25 / unknown 0.4
  risk_q      thesis-critical open SPOF count: 0 -> 1.0 / 1 -> 0.65 / 2 -> 0.40 / 3+ -> 0.20
              +0.15 if earnings_chain has >=2 evidenced_links AND <=1 open SPOF

expectation_gap_score = clamp(gap_frac * quality * 100, 0, 100)
                        x0.5 if red_flag_tier == "HIGH CAUTION"
                        = 0  if red_flag_tier in {AVOID, EXCLUDE}   (flag "red-flag-zeroed")
                        = 0  if gap_direction == "over-optimistic"   (flag "no-edge")
```

A weighted-average `quality` (not a product of four sub-1.0 factors) so the 0-100 band is
actually used. "Effective status": a `pending`/`in-progress` catalyst whose
`window_start + expected_window_months` is in the past is treated as `lapsed` for scoring —
the script does **not** write that back; the next `deepdive-top100` pass refreshes the block.

`flags` emitted per stock: `no-edge` · `priced-in` · `catalyst-lapsed` · `no-catalyst` ·
`thin-evidence` · `high-caution` · `red-flag-zeroed`.

Output: `expectation_gap_score` onto `state.json` (only for stocks with a `market_expectation`
block); `data/expectation-gap-scores.json` = `{ranked, no_edge, not_assessed}` with a
`score_breakdown` each. `vpscreen-rerank` runs the script (Step 2) and renders
`docs/00d_EXPECTATION_GAP_RANKING.docx` via `make_expectation_gap_ranking.js` (Step 5.5) every
cycle. `portfolio-rs1l-revision` (Phase 4, not yet built) will require a candidate to clear a
bar on **both** scores and flag any held name whose gap has decayed to `priced-in` / `no-edge`.
