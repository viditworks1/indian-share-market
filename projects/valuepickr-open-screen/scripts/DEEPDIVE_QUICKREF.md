# Deep-dive block quick-ref (enums + one example)

One-page working reference for `deepdive-top100` (and its light guidance lane). The full
contracts — rationale, rendering, scoring formulas — are in `GUIDANCE_EXPECTATION_SCHEMA.md`,
`ISHMOHIT_SIGNALS_SCHEMA.md`, and `FUNDAMENTALS_GAP_SCHEMA.md` (shareholding pattern / working
capital / sector KPIs / scenario analysis); read those only if this page is ambiguous for a case.
Every block is optional; absent = "not assessed", `[]`/`null` = "assessed, nothing there".
Unrecognised enum value → consumer treats it as the most conservative option + warns.

## Guidance / expectation-gap blocks (4)

**`commitments[]`** — one per material forward commitment (cap ~10; the 1–2 `thesis_critical`
ones matter most). Fields:
`area` = growth|capacity|orders|margin|capex|balance_sheet|strategy|new_business ·
`text` (≤~20 words) · `specifics` (numbers/names as stated, or "") ·
`timeline_bucket` = 3M|6M|12M|FY27|FY28|beyond ·
`quality_stage` = **furthest-right the evidence supports**: expectation(1, just a target) →
action(2, capital/resources committed) → operational(3, going live on a dated schedule) →
commercial(4, a customer/order/shipment) → financial(5, already in a reported quarter). A
*future* financial target is `expectation`, not `financial`. ·
`source` · `dependency` ("" if none) · `single_point_of_failure` ("" if diversified) ·
`thesis_critical` (bool). No concall / no guidance → `"commitments": []`.

**`earnings_chain`** — `{ chain:[ordered links … → PAT/FCF], bottleneck_link,
operating_leverage: "yes — <why>"|"no"|"unclear", evidenced_links:[…], assumed_links:[…] }`.
No meaningful chain → `null`.

**`market_expectation`** — `{ as_of:<today>, price, current_pe, current_ev_ebitda,
valuation_tool: "P/E"|"EV/EBITDA"|"P/B"|"other", implied_growth_cagr (prose),
our_fy27_estimate, our_fy28_estimate,
gap_direction: "priced-in"|"partially-priced"|"underestimated"|"over-optimistic",
gap_type: "volume"|"capacity"|"mix"|"margin"|"timing"|"duration"|"new_business",
gap_magnitude_pct (signed int: our FY28 PAT vs implied FY28 PAT %, or null), gap_basis,
evidence_quality: "strong"|"moderate"|"monitor"|"weak"|"none", data_caveat }`.
- `implied_growth_cagr` via **reverse-P/E** when no consensus: pick a defensible exit multiple
  (steady compounder ~18–22x; high-quality franchise ~25–30x; cyclical → P/B or ~10–14x), state
  the EPS CAGR FY26→FY28 that makes today's multiple fair vs that exit. Directional is fine.
- `gap_direction`: our path ≈ implied → `priced-in`; market sees part, ours higher →
  `partially-priced`; ours materially better → `underestimated`; ours *below* what the price
  needs → `over-optimistic`.
- `evidence_quality`: furthest-right `quality_stage` among `thesis_critical` commitments →
  `financial`/`commercial`=strong · `operational`=moderate · `action`=monitor · `expectation`
  only=weak · none/`[]`=none. **Downgrade one notch** if `assumed_links` outnumber `evidenced_links`.
- `data_caveat`: verbatim `"no broker consensus; implied path is a reverse-P/E estimate + screener.in forward figures + VP thread view"`.

**`catalyst`** — `{ event, expected_window_months (int from as_of), window_start:<today>,
evidence_quality: "high"|"med"|"low", is_dated (bool), status: "pending" }`. None → `null`.

## Ishmohit-lens blocks (5 written here; `global_signal_check` is `global-proxy-scan`'s)

**`value_chain`** (or `null`) — `{ theme, position, bottleneck_node ("" if none),
supply_side_status: "adding"|"balanced"|"consolidating"|"exiting"|"unclear",
adjacent_peers:[2–4 named], note }`.
Capital-cycle read: `adding` = late-cycle glut risk · `consolidating` = survivors gain pricing
· `exiting` = strongest (pricing power to whoever's left) · `balanced`/`unclear` = neutral.

**`earnings_quality`** (populate for any real-financials company) — `{ margin_driver:
"structural"|"cyclical"|"mixed"|"unclear", drivers:[most important first], peak_margin_risk
(bool), normalised_note }`. `peak_margin_risk: true` only when reported margin is well above a
defensible through-cycle level **and** the driver is at least partly cyclical. **Get this field
right** — `compute_expectation_gap_score.py` reads it as a 0.70× haircut when `gap_direction`
is `underestimated`/`partially-priced`.

**`growth_trajectory`** — `{ yoy_trend: "accelerating"|"steady"|"decelerating"|"lumpy"|
"unclear", last_quarters_note (the actual YoY growth-rate sequence oldest→newest, ~4–8 q),
reverse_pe_note (rate-of-change vs what the multiple needs) }`. `lumpy` = order/project
business, treat neutral. **Get `yoy_trend` right** — `decelerating` + `priced-in`/
`partially-priced` → 0.60× haircut.

**`management_quality`** — `{ capital_allocation (3-yr incremental ROCE on reinvestment + any
unrelated diversification), capital_allocation_track_record: "disciplined"|"neutral"|
"value-destructive"|"unclear" (added 2026-09-04 — the scored classification of the same
capital_allocation read), rpt_trend: "clean"|"flat"|"rising"|"concerning"|"unclear" (NOW SCORED,
get it right), guidance_credibility: "reliable"|"mixed"|"over-promises"|"no-track-record"|
"unclear", shareholder_returns: "consistent"|"initiated"|"none"|"erratic"|"unclear" (added
2026-09-04 — dividend/buyback discipline specifically, distinct from debt-free-ness),
capability_ladder_note (explicit VAP/"moving up the value curve" language, or ""),
assessment: "positive"|"neutral"|"concern" }`. `guidance_credibility` = last ~3y guidance given
vs delivered. `assessment: "concern"` is a soft narrative negative — it does **not** set
`red_flag_tier`. Feeds `compute_conviction_score.py` as `management_component ∈ [−12,+12]`
(positive +6 / concern −6 ; reliable +2 / over-promises −4; disciplined +3 / value-destructive
−4; clean +2 / flat +1 / rising −2 / concerning −5; consistent +2 / initiated +1 / erratic −3).

**`track_record`** (added 2026-09-05, Mukherjea's Coffee Can mechanism — see
`MASTER_SCORE_METHODOLOGY.md`) — `{ years_checked: int, years_cleared: int, note }`. From the
SAME 3-5yr annual-report read: of the fiscal years actually verifiable, how many had **both**
revenue growth ≥10% **and** ROCE ≥15% in that same year (not "trending up," an actual per-year
pass/fail count). `years_checked < 3` (young company) → leave the whole block absent, not a
low score — never penalize a small-cap for lacking a decade of filings; that's exactly where
Kedia/Porinju hunt. Feeds `compute_master_score.py`'s `consistency_score` directly.

**`quality_metrics`** (the user's own screening framework, 2026-09-04: growth + margins + ROCE +
debt + capex + FCF + moat + management — this covers the 4 legs nothing else scored) — from the
SAME annual-report/balance-sheet read as `management_quality`, no new document layer:
`{ roce_pct (most recent FY, % — null if not derivable), roce_trend:
"improving"|"stable"|"declining"|"unclear" (trailing 3y direction), net_debt_to_ebitda (number,
<=0 for net-cash; null if not meaningful), interest_coverage (EBIT/interest — fallback only when
leverage isn't meaningful, e.g. near-zero debt; null otherwise), fcf_conversion_pct (trailing 3y
avg (CFO-capex)/EBITDA, % — CAN and should be negative if that's what the filings show, only
null if genuinely not derivable e.g. a 1-year-old SME listing), margin_trend:
"expanding"|"stable"|"contracting"|"unclear" (the level trend — distinct from
earnings_quality.margin_driver's structural-vs-cyclical read), capex_efficiency:
"productive"|"neutral"|"value-destructive"|"unclear" (is new capital earning back above cost of
capital — asset turn holding as capex lands on schedule vs. serial raises with declining
returns/serial slippage), assessment: "positive"|"neutral"|"concern" }`. **Do not leave
`fcf_conversion_pct` null just because it would be negative or ugly** — a capex-heavy name
mid-ramp legitimately showing negative conversion is exactly the signal this field exists to
catch; only use null when the number genuinely can't be sourced. Feeds
`compute_quality_score.py` (0-100, `QUALITY_SCORE_METHODOLOGY.md`) — a separate script from
`compute_conviction_score.py`, not a component of it.

## Fundamentals-gap blocks (4, added 2026-09-11 — `FUNDAMENTALS_GAP_SCHEMA.md`)

Informational only — not read by any scoring script yet. Added after benchmarking against
a third-party report generator (researchtool.lkradvisors.in) surfaced 4 sections nothing
here captured (9 of its 13 sections already existed under different names).

**`shareholding_pattern`** — `{ as_of, promoter_pct, promoter_trend: increasing|stable|
decreasing|unclear, pledge_pct, pledge_trend: none|falling|stable|rising|unclear, fii_pct,
fii_trend: buying|stable|selling|unclear, dii_pct, dii_trend (same enum), public_pct,
concurrent_red_flag (bool — true only when pledge_trend=rising AND promoter_trend=decreasing
in the same window), note }`.

**`working_capital`** — `{ as_of, inventory_days, receivable_days, payable_days,
cash_conversion_cycle_days (= inventory + receivable − payable), nwc_trend:
improving|stable|deteriorating|unclear, working_capital_intensity: light|moderate|heavy|
unclear (vs sector norm, not absolute), note }`.

**`sector_kpis`** — `{ sector_label, kpis:[{ metric, value, trend:
improving|stable|declining|unclear, peer_comparison }], note }`. Free-form list — sector
ops metrics don't share one shape (cement utilisation vs bank NIM/CASA vs SaaS NRR).

**`scenario_analysis`** — numeric bull/base/bear, distinct from the prose `bull_case[]`/
`bear_case[]` (those stay). `{ as_of, bear/base/bull: { revenue_cagr_fy26_28_pct,
fy28_margin_pct, fy28_eps, exit_multiple, implied_price, vs_cmp_pct (signed, vs CMP),
key_assumption }, note }`. Anchor to the same FY27/FY28 numbers already in
`market_expectation` where that block exists — don't re-derive a second, inconsistent set.

## Thesis-fit 4-box gate (`four_box`) — set this BEFORE `thesis_fit`

phreakv6's hurdle (*Phreak's Thoughts* #330): "tailwind + tam + moat + valuation … at least
two or three. Very rarely all 4 click." Makes `thesis_fit` an auditable checklist instead of a
prose call. Canonical home is `data/<slug>.json` (no `state.json` mirror); `audit_state.py`
reads it from there.

```jsonc
"four_box": {
  "tailwind":  "yes" | "weak" | "no",   // structural multi-year demand driver, not a cyclical bounce
  "tam":       "yes" | "weak" | "no",   // headroom to support the REQUIRED multiple off today's revenue/mcap
  "moat":      "yes" | "weak" | "no",   // pricing power / switching cost / structural cost edge that survives the growth
  "valuation": "yes" | "weak" | "no",   // room to pay — NOT "cheap", just "not already pricing the thesis in"
  "score": 2.5,                          // yes=1, weak=0.5, no=0  → 0..4 (compute it, don't eyeball)
  "note": "one line naming the weak/no boxes and why"
}
```

Decision table — the allowed `thesis_fit` given `four_box.score`:

| `score` | `thesis_fit` |
|---|---|
| **≥ 3.0** | `10x-in-2-3-years` / `100x-in-10-years` permitted (conviction still set separately) |
| **2.0–2.5** | `neither` **UNLESS** a written exception in `verdict_reasoning`: `valuation` box = `yes`, **or** growth is un-ignorable (phreak's carve-out), **or** the large-cap named-inflection exception — then the return-magnitude label is allowed but conviction caps at **Medium** with an "unconfirmed" caveat |
| **≤ 1.5** | `thesis_fit: "neither"`, hard — no exception |

When `score >= 3.0` but you deliberately keep `thesis_fit: "neither"` (size / return-magnitude /
capital-intensity call the mechanical boxes don't capture — the "Nesco logic"), set
`"analyst_override": true` inside the `four_box` block and put the one-line reason in `note`.
`audit_state.py` then treats it as intentional instead of re-flagging it as an understated
mismatch every run.

Interactions (unchanged, they just feed the boxes now): small/mid-cap live inflection → a real
recent-quarter inflection counts as `tailwind: yes` / `tam: yes` even if the 3–5yr average is
weak. Genuine large-cap → `tam: no` (can't get the headroom) → score < 3 → `neither` unless the
named-inflection exception is written. Red flag (AVOID/EXCLUDE) → skip the box exercise,
`thesis_fit: neither`.

Not the same as `data/screen-ranking.json`'s `dimensions` block (that decomposes why a name was
screened *out* — fundamentals quality / governance / technicals). `four_box` is the positive
10x/100x case. A name can have both.

## Red-flag & conviction rules (identical to vpscreen-scan)

AVOID (neg net worth / going concern) & EXCLUDE (active SEBI/fraud order) → `red_flag_tier` set,
thesis `neither`, conviction `Low`, never overridden. HIGH CAUTION (promoter-holding collapse,
auditor resignation) → keep researching, cap conviction `Low-Medium`, name the concern. If the
deep read *uncovers* one where none was recorded, set it.
Trusted-conviction floor: only if `state.json` entry has `trusted_conviction_floor_active: true`
AND no red flag → floor `Medium-High` (up to `High` on real strength, never below). `false`/
absent → no floor.
Trailing-average vs live inflection: for a small/mid-cap, judge thesis-fit on recent-quarter
trajectory + catalyst credibility, not the 3–5yr average. Weak average + strong specific recent
quarter + catalyst → `10x-in-2-3-years` at Low/Medium with an "unconfirmed" caveat, not
`neither`. Genuine large-caps exempt (size math is a legitimate `neither`).
Conviction labels exactly: `High`/`Medium-High`/`Medium`/`Low-Medium`/`Low`.
Thesis-fit exactly: `10x-in-2-3-years`/`100x-in-10-years`/`neither`.

## Worked example (ASK Automotive — illustrative)

```jsonc
{
  "commitments": [
    { "area":"capacity", "text":"Karoli utilisation to ~80%", "specifics":"existing + new lines",
      "timeline_bucket":"6M", "quality_stage":"operational", "source":"Q1 FY27 concall",
      "dependency":"programme ramp", "single_point_of_failure":"utilisation ramp speed", "thesis_critical":true },
    { "area":"orders", "text":"Japan alloy-wheel + Ford export programmes", "specifics":"Rs 70-90cr + Rs 40-45cr FY27",
      "timeline_bucket":"FY27", "quality_stage":"commercial", "source":"Q1 FY27 concall",
      "dependency":"customer programme ramp", "single_point_of_failure":"programme/ramp execution", "thesis_critical":true },
    { "area":"margin", "text":"EBITDA margin recovery to 13.5-14%", "specifics":"scale + mix",
      "timeline_bucket":"FY27", "quality_stage":"expectation", "source":"FY26 concall",
      "dependency":"utilisation + mix", "single_point_of_failure":"", "thesis_critical":true }
  ],
  "earnings_chain": {
    "chain":["new programmes/orders","capacity ramp (Karoli ~80%)","revenue growth","operating leverage","EBITDA margin 13.5-14%","PAT"],
    "bottleneck_link":"capacity ramp (Karoli ~80%)",
    "operating_leverage":"yes — margin guided up on utilisation + mix",
    "evidenced_links":["new programmes/orders","capacity ramp (Karoli ~80%)"],
    "assumed_links":["operating leverage","EBITDA margin 13.5-14%"] },
  "market_expectation": {
    "as_of":"2026-09-01", "price":null, "current_pe":null, "current_ev_ebitda":null, "valuation_tool":"P/E",
    "implied_growth_cagr":"~20% EPS CAGR FY26-28 to justify 34x at a 22x exit",
    "our_fy27_estimate":"revenue high-teens, margin toward 13.5-14%, PAT +25-30%",
    "our_fy28_estimate":"second leg from Japan run-rate + full Karoli utilisation",
    "gap_direction":"partially-priced", "gap_type":"margin", "gap_magnitude_pct":null,
    "gap_basis":"operating leverage from utilisation not fully in the multiple; market pricing flat margins",
    "evidence_quality":"strong",
    "data_caveat":"no broker consensus; implied path is a reverse-P/E estimate + screener.in forward figures + VP thread view" },
  "catalyst": { "event":"Japan first shipments + a Q2/Q3 FY27 margin print showing the step-up",
    "expected_window_months":9, "window_start":"2026-09-01", "evidence_quality":"med", "is_dated":false, "status":"pending" },
  "value_chain": { "theme":"auto lightweighting / alloy wheels", "position":"alloy-wheel + machined-assembly supplier to 2W/4W OEMs",
    "bottleneck_node":"machining capacity + OEM programme approvals", "supply_side_status":"balanced",
    "adjacent_peers":["Minda Corp","Endurance Technologies","Sundram Fasteners"], "note":"Japan OEM approvals are the moat; domestic alloy-wheel supply roughly tracks demand." },
  "earnings_quality": { "margin_driver":"structural", "drivers":["operating leverage on completed capex","VAP mix up ~400bps"],
    "peak_margin_risk":false, "normalised_note":"Mgmt guides 13.5-14% through-cycle; current ~14% is mid-cycle, not a spike." },
  "growth_trajectory": { "yoy_trend":"accelerating", "last_quarters_note":"YoY rev growth oldest->newest: 9%, 14%, 18%, 22%, 27%, 31%",
    "reverse_pe_note":"34x trailing needs ~20% EPS CAGR FY26-28 at a 22x exit; recent trend supports it." },
  "management_quality": { "capital_allocation":"Reinvested at 18-22% incremental ROCE; one small unrelated diversification FY24, since exited",
    "capital_allocation_track_record":"disciplined", "rpt_trend":"flat", "guidance_credibility":"reliable",
    "shareholder_returns":"initiated",
    "capability_ladder_note":"Explicitly moving commodity wheels -> alloy -> machined assemblies for Japan OEMs", "assessment":"positive" },
  "quality_metrics": { "roce_pct":19.5, "roce_trend":"improving", "net_debt_to_ebitda":1.2,
    "interest_coverage":null, "fcf_conversion_pct":55, "margin_trend":"stable",
    "capex_efficiency":"productive", "assessment":"positive" },
  "four_box": { "tailwind":"yes", "tam":"yes", "moat":"weak", "valuation":"weak", "score":3.0,
    "note":"moat weak (design-follower ex-Japan approvals); valuation weak at 34x, thesis partly priced. tailwind+tam carry it to 3.0 -> 10x-in-2-3-years permitted." }
}
```
