# Ishmohit-lens signal blocks — data contract

**Four** blocks added 2026-08-30 (`value_chain`, `earnings_quality`, `growth_trajectory`,
`management_quality`) + a **fifth** added 2026-08-31 (`global_signal_check`, §5) + a **sixth**
added 2026-09-04 (`quality_metrics`, §6 — ROCE/debt/FCF/margin/capex, the user's own stated
screening framework: "growth + margins + ROCE + debt + capex + free cash flow + competitive
advantage + management quality"). All **optional** top-level blocks on `data/<slug>.json`.
Source of the method: `playbook/ishmohit-soic-style.md`. The first four (plus `quality_metrics`)
are written by `deepdive-top100` from the same filings it already reads (3y annual reports + ~4
quarters of results/concalls + 6 months of exchange announcements) — this changes only what it
*extracts*, not what it reads. `value_chain` may also be written by `vpscreen-scan` when the
forum deep-read makes the chain obvious. `global_signal_check` is written by the
`global-proxy-scan` task's Stage C (see that SKILL + `../global_bellwethers.json`).

**All blocks are optional.** A `data/<slug>.json` without them is valid and behaves
exactly as before: `make_stock_doc.js` skips the section, `compute_expectation_gap_score.py`
applies no haircut. Absence = "not yet assessed through this lens", which is distinct from an
explicit `"unclear"` / `"na"` value = "looked, couldn't tell".

Enum handling follows the project convention (`compute_conviction_score.py` /
`GUIDANCE_EXPECTATION_SCHEMA.md`): an unrecognised enum value is treated as the **most
conservative** option and the consuming script logs a warning.

---

## 1. `value_chain`

Ishmohit's "do a PhD on the value chain, then buy the node with the highest barrier AND
fastest growth; be a student of the supply side". Object:

```jsonc
{
  "theme": "AI data-centre power",              // the demand driver, short phrase
  "position": "gas-genset / prime-power supplier to Indian hyperscale DCs",  // where THIS company sits
  "bottleneck_node": "grid interconnection + prime power",   // the constrained link in the chain (where pricing power concentrates); "" if none
  "supply_side_status": "adding",              // enum, see below — what capacity is doing across this node globally + in India
  "adjacent_peers": ["Cummins India", "Kirloskar Oil Engines"],  // 2-4 named cos in the same or neighbouring nodes, for triangulation
  "note": "DC order-book share ~15% and rising; Europe forging/gensets capacity closing on power costs -> shift to India"  // 1-2 sentences, free text
}
```

### `supply_side_status` enum
| value | meaning | capital-cycle read |
|---|---|---|
| `adding` | capacity being added fast across the node | late-cycle risk — watch for the glut ("all shortages are followed by gluts") |
| `balanced` | supply roughly tracking demand | neutral |
| `consolidating` | weak players exiting, capex restraint, discipline returning | early-cycle — survivors gain pricing power |
| `exiting` | net capacity being withdrawn (China shutdowns, European plant closures, bankruptcies) | strongest — the "any company still standing has massive pricing power" setup |
| `unclear` | looked, couldn't determine | neutral |

---

## 2. `earnings_quality`

His most-repeated bear tell: "Inventory gains + Realisation gains are artificially inflating
the E in PE. Don't value them on peak margins." Object:

```jsonc
{
  "margin_driver": "structural",   // enum: "structural" | "cyclical" | "mixed" | "unclear"
  "drivers": ["operating leverage on completed capex", "VAP mix up ~400bps"],  // what's actually moving margins, most-important first
  "peak_margin_risk": false,       // bool — are current margins near a cyclical peak that shouldn't be capitalised?
  "normalised_note": "Mgmt guides 13.5-14% through-cycle EBITDA; current 14.2% is roughly mid-cycle, not a spike"  // 1-2 sentences: what a normalised margin looks like vs the reported one
}
```

- `margin_driver`:
  - `structural` — mix shift, operating leverage from utilisation, VAP, genuine cost-out.
  - `cyclical` — realisation/price gains, inventory gains, FX, a one-off, a demand spike that
    pulls forward.
  - `mixed` — both present and material.
  - `unclear` — conservative default for an unrecognised value.
- `peak_margin_risk: true` only when the reported margin is well above a defensible through-
  cycle level AND the driver is at least partly cyclical. This is the field the expectation-gap
  haircut reads.

---

## 3. `growth_trajectory`

"If the rate of change of growth changes from high to moderate, expect Mr Market to adjust the
multiples." + the growth-trap rule (100x P/E needing ever-rising growth). Object:

```jsonc
{
  "yoy_trend": "accelerating",     // enum: "accelerating" | "steady" | "decelerating" | "lumpy" | "unclear"
  "last_quarters_note": "YoY revenue growth by quarter (oldest->newest): 9%, 14%, 18%, 22%, 27%, 31%",  // the actual print sequence, ~4-8 quarters
  "reverse_pe_note": "At 34x trailing, ~20% EPS CAGR FY26-28 is required to hold the multiple at a 22x exit; recent trend supports this"  // what growth the CURRENT multiple demands, vs the observed trend
}
```

- `yoy_trend`:
  - `accelerating` — the YoY growth *rate* is rising over the window (the re-rating setup).
  - `steady` — roughly flat growth rate.
  - `decelerating` — growth rate falling quarter over quarter (the de-rating / growth-trap
    risk, especially at a high multiple).
  - `lumpy` — order-driven / project business where QoQ YoY is noisy and a trend read is not
    meaningful; treat as neutral.
  - `unclear` — conservative default.
- `reverse_pe_note` overlaps in spirit with `market_expectation.implied_growth_cagr` but is
  specifically the **rate-of-change** framing: is the *trend* heading toward or away from what
  the multiple needs.

---

## 4. `management_quality`

TVGP's "P": promoters who care for minorities and are hell-bent to grow — a **positive**
attribute, not just the absence of a red flag. Built from the 3y annual-report read
`deepdive-top100` already does. Object:

```jsonc
{
  "capital_allocation": "Reinvested at 18-22% incremental ROCE; one small unrelated diversification in FY24, since exited",
  "capital_allocation_track_record": "disciplined",  // enum: "disciplined" | "neutral" | "value-destructive" | "unclear" — added 2026-09-04
  "rpt_trend": "flat",             // enum: "clean" | "flat" | "rising" | "concerning" | "unclear"
  "guidance_credibility": "reliable",   // enum: "reliable" | "mixed" | "over-promises" | "no-track-record" | "unclear"
  "shareholder_returns": "consistent",  // enum: "consistent" | "initiated" | "none" | "erratic" | "unclear" — added 2026-09-04
  "capability_ladder_note": "Explicitly moving up the VAP curve — commodity wheels -> alloy -> machined assemblies for Japan OEMs",
  "assessment": "positive"         // enum: "positive" | "neutral" | "concern"
}
```

- `guidance_credibility` — cross-check the last ~3 years of guidance given (in ARs/concalls)
  against what was delivered. This is the same information the `commitments[]` ladder captures
  per-commitment; here it's rolled up to a management-level verdict. `reliable` = met or beat
  most material guidance; `over-promises` = a pattern of guided-then-missed;
  `no-track-record` = too new / too little guided to judge.
- `capital_allocation_track_record` (added 2026-09-04, user-requested — the same annual-report
  read that already produces the `capital_allocation` prose, just also classified) —
  `disciplined`: capital reinvested at/above the company's own cost of capital, in the core
  business, no unrelated diversification. `neutral`: mixed or too early to judge.
  `value-destructive`: capital going into unrelated diversification, serial value-destructive
  M&A, or reinvestment at incremental returns visibly below the historical ROCE. `unclear`: not
  assessable this pass. Distinct from `quality_metrics.capex_efficiency` (§6 below) — that one
  is specifically whether *new capex* earns back its cost; this is the broader pattern across
  capex, M&A, and diversification.
- `rpt_trend` — `clean` (negligible), `flat` (present but stable and explained), `rising`
  (growing as a share of revenue/assets), `concerning` (large, unexplained, or to
  promoter-linked entities), `unclear`. **Now actually scored** (see below) — previously
  collected on every block but not consumed by any formula.
- `shareholder_returns` (added 2026-09-04, user-requested) — dividend/buyback discipline as a
  distinct positive signal from mere debt-free-ness: `consistent` (a multi-year, stable payout
  policy), `initiated` (a real but recent/modest payout — e.g. a first dividend or "modest
  dividend" language — not yet a multi-year track record), `none` (no payout policy — fine for
  a genuine reinvestment-stage growth company, and not penalised as heavily as `erratic`),
  `erratic` (a stop-start or discontinued payout history), `unclear`. About capital *returned*
  specifically — a company diluting via serial equity raises instead should reflect that in
  `capital_allocation_track_record` / `rpt_trend` / the free-text narrative, not by forcing this
  field to double as a dilution flag.
- `assessment` — the one-word roll-up. `concern` here does **not** by itself set a
  `red_flag_tier` (that's still the forensic tiers' job) — it's a soft negative.

**Consumed mechanically by `compute_conviction_score.py` (component 6, added 2026-08-30,
widened 2026-09-04):** `management_component` in `[-12, +12]` = `clamp(assessment_pts +
guidance_pts + capital_alloc_pts + rpt_pts + shareholder_returns_pts, -12, +12)`:
- `assessment`: `positive` +6 · `neutral` 0 · `concern` -6 · absent/unrecognised 0.
- `guidance_credibility`: `reliable` +2 · `over-promises` -4 · `mixed` / `no-track-record` /
  `unclear` / absent 0.
- `capital_allocation_track_record`: `disciplined` +3 · `neutral` 0 · `value-destructive` -4 ·
  `unclear` / absent 0.
- `rpt_trend`: `clean` +2 · `flat` +1 · `rising` -2 · `concerning` -5 · `unclear` / absent 0.
- `shareholder_returns`: `consistent` +2 · `initiated` +1 · `none` 0 · `erratic` -3 ·
  `unclear` / absent 0.
Guarded — exactly 0 when the `management_quality` block is absent, so it is a strict no-op on
every stock until `deepdive-top100` populates the block; each of the 5 sub-terms is *also*
independently guarded (0 if that one field is missing/unclear), so a block with only the
original 2 fields populated scores identically to before the widen. It is added to `raw`
alongside the other components (skipped entirely on an AVOID/EXCLUDE-forced-zero stock). ±12 is
still smaller than the thesis (20) or trust (25) terms — it's one of four TVGP legs, and the
signal is softer than hard fundamentals — but wide enough that several genuinely bad sub-signals
firing at once (concerning RPT + value-destructive capital allocation + erratic payouts) move
the score more than one soft "concern" word would alone. Also rendered in the docx and available
as an LLM input to `vpscreen-scan`'s conviction call.

---

## 5. `global_signal_check`

Ishmohit's "global-first → Indian proxy" motion, with the loop closed: after a global
bellwether shows a signal (e.g. "packaging sold out to 2027", "transformer lead times 2+ years
and prices rising", "HBM sold out, DRAM +30%"), does the Indian proxy's **own** latest
disclosure show the *same* signal? Written by `global-proxy-scan` Stage C for a proxy that is
already `researched` and sits under an `accelerating` (or `steady` + tight) tailwind. Object:

```jsonc
{
  "bellwether": "GE Vernova + Siemens Energy",           // the global name(s) that generated the signal
  "theme": "Grid + transmission equipment",              // theme label from global_bellwethers.json
  "global_tailwind": "accelerating",                     // enum: "accelerating" | "steady" | "decelerating" — the theme's rate_of_change at check time
  "signal_hypothesis": "multi-quarter un-executable export order book + 2-yr lead times + price hikes",  // the specific thing to look for in THIS company
  "india_datapoint": "Q1FY27 concall: order book Rs 4,300cr (2.4x TTM revenue), export mix up to 34%, realising 8-10% higher prices on new orders",  // the actual quoted datapoint found (or "none found" for not-yet-visible / diverging)
  "alignment": "confirmed",                              // enum: "confirmed" | "partial" | "not-yet-visible" | "diverging" | "unclear"
  "checked_date": "2026-09-05",
  "note": "Direct exposure; the Indian order book is inflecting on the SAME driver (US/EU grid capex) the bellwethers cited."  // 1-2 sentences
}
```

### `alignment` enum
| value | meaning | downstream |
|---|---|---|
| `confirmed` | the Indian name's own numbers show the same signal, with a quoted datapoint | `global-proxy-scan` sets `revisit_after_30d: true` (if conviction < High, no red flag); becomes a watchlist/allocation candidate for `portfolio-rs1l-revision` (still gated on EMA + expectation-gap) |
| `partial` | some alignment, not yet full / not in the reported numbers | monitor; no portfolio action |
| `not-yet-visible` | global tailwind real, nothing in the Indian name's disclosures reflects it yet | re-checked on `stage_c_recheck_days` (~30d) |
| `diverging` | the Indian name's own numbers **contradict** the tailwind (flat/declining order book, margin give-back, lost customers) | `revisit_after_30d: true`; a review trigger for `portfolio-rs1l-revision` if the name is held (never an auto-cut) |
| `unclear` | looked, couldn't tell — conservative default for an unrecognised value | treated as `not-yet-visible` |

Also surfaced as a row in `../global-signal-alignment.md` (the file `portfolio-rs1l-revision`
reads). This block never sets `red_flag_tier`, `conviction`, `status`, or `thesis_fit` —
`global-proxy-scan` only ever writes the block + the `revisit_after_30d` flag + the alignment
row; re-rating is `vpscreen-scan` / `deepdive-top100`'s job.

**Not consumed by `compute_conviction_score.py` / `compute_expectation_gap_score.py`** — it's a
qualitative routing signal, not a scored input (kept deliberately out of the mechanical scores
so a model-derived read can't move a tier band on its own).

---

## 6. `quality_metrics`

The four legs of the screen the user (not a ValuePickr/Ishmohit source — this is the account
owner's own stated framework, 2026-09-04) actually asked for, in numbers: **ROCE, debt, free
cash flow, margin trend, capex efficiency**. `growth` and `competitive advantage` /
`management quality` already have homes (`growth_trajectory`, `value_chain`,
`management_quality`) — this block is specifically the balance-sheet/cash-generation quality
legs nothing else captured. Written by `deepdive-top100` from the same 3-year annual-report +
balance-sheet read it already does for `management_quality` — no new document layer. Object:

```jsonc
{
  "roce_pct": 26.2,                  // most recent FY ROCE, %; null if not disclosed/derivable
  "roce_trend": "improving",         // enum: "improving" | "stable" | "declining" | "unclear"
  "net_debt_to_ebitda": 0.68,        // number; <=0 for a net-cash balance sheet; null if not derivable
  "interest_coverage": 11.3,         // EBIT / interest expense; null if not meaningful (near-zero debt) or not derivable
  "fcf_conversion_pct": 65,          // trailing 3y avg (CFO - capex) / EBITDA, %; CAN be negative (heavy investment phase) - only null if not derivable
  "margin_trend": "expanding",       // enum: "expanding" | "stable" | "contracting" | "unclear"
  "capex_efficiency": "productive",  // enum: "productive" | "neutral" | "value-destructive" | "unclear"
  "assessment": "positive"           // enum roll-up: "positive" | "neutral" | "concern"
}
```

- `roce_trend` — direction over the trailing 3 years, not a single-year read.
- `net_debt_to_ebitda` is the primary leverage field; `interest_coverage` is a fallback for a
  business with near-zero debt where the ratio isn't meaningful (e.g. a net-cash company still
  carrying a small working-capital facility). Populate whichever is the more informative number
  for this balance sheet; leave the other `null` rather than forcing a number that doesn't mean
  anything.
- `fcf_conversion_pct` — **do not** write `null` just because the number is negative or ugly; a
  capex-heavy name mid-ramp can legitimately show negative FCF conversion, and that's exactly
  the signal this field exists to surface. Only use `null` when CFO/capex genuinely can't be
  sourced (e.g. a just-listed SME with one year of financials).
- `capex_efficiency` — is the capital actually being deployed getting deployed above the
  company's own cost of capital: `productive` (asset turn / incremental ROCE holding up as
  capex lands, on schedule), `neutral` (too early / in-line with guidance, nothing to flag
  either way), `value-destructive` (serial capex raises with declining asset turn or ROCE
  dilution, repeated commissioning slippage with no revenue to show for it, capex funding an
  unrelated diversification). Distinct from `earnings_quality.peak_margin_risk` (that's about
  whether *current* margins are cyclically inflated; this is about whether *new* capital is
  being well spent).
- `assessment` — one-word roll-up, same convention as `management_quality.assessment`:
  `positive` (ROCE strong/improving, low leverage, FCF converts, margins holding or expanding,
  capex productive — most legs pull the same direction), `neutral` (mixed — some legs strong,
  some weak, no clear overall lean), `concern` (leverage rising into weak FCF, or capex
  chronically value-destructive, or margins genuinely eroding — a real balance-sheet-quality
  worry, distinct from a governance red flag).

**Consumed mechanically by `compute_quality_score.py` (new script, 2026-09-04):**
`quality_score` (0-100) = `roce_component (0-25) + debt_component (0-20) + fcf_component (0-25)
+ margin_component (0-15) + capex_component (0-15)`, then the same red-flag multiplier
convention as `conviction_score`/`expectation_gap_score` (`HIGH CAUTION` ×0.5, `AVOID`/`EXCLUDE`
→ forced 0). See `QUALITY_SCORE_METHODOLOGY.md` for the full formula and worked examples.
Guarded exactly like every other lens block: a `data/<slug>.json` with no `quality_metrics`
block scores nothing (bucketed `not_assessed`, not zero) — this is a strict no-op on the whole
registry until `deepdive-top100` starts populating it, identical to how `management_component`
landed as a no-op in `compute_conviction_score.py`.

This is a **third, orthogonal** score alongside `conviction_score` ("is this a good business
trusted people back?") and `expectation_gap_score` ("is it mispriced, with a catalyst, on
acceptable risk?"): `quality_score` answers **"is the balance sheet and cash generation actually
as good as the growth story suggests?"** — a name can have a real growth story, a trusted-thread
endorsement, and an underpriced catalyst, and still be quietly funding that growth with
deteriorating leverage or non-converting cash flow. None of the other two scores would catch
that on their own.

---

## `make_stock_doc.js` rendering

New section **"Ishmohit-Lens Checks (value chain · earnings quality · growth trajectory ·
management · quality metrics · global-signal check)"**, placed **after** "Guidance &
Expectation Gap" and **before** "Technical Read". Each of the six sub-blocks renders only if
present. `value_chain`, `management_quality`, `quality_metrics` and `global_signal_check` as
kv-tables (the global-signal one with a bold coloured lead line — green for `confirmed`, red
for `diverging`/`not-yet-visible`); `earnings_quality` and `growth_trajectory` as a bold-label
line + detail lines. Guarded by
`if (d.value_chain || d.earnings_quality || d.growth_trajectory || d.management_quality || d.quality_metrics || d.global_signal_check)`.

## `compute_expectation_gap_score.py` consumption

Two guarded multiplicative haircuts (see the script's `ISHMOHIT-LENS HAIRCUTS` section):

| condition | effect | flag |
|---|---|---|
| `earnings_quality.peak_margin_risk == true` AND `gap_direction` in {`underestimated`, `partially-priced`} | `score *= 0.70` | `peak-margin-risk` |
| `growth_trajectory.yoy_trend == "decelerating"` AND `gap_direction` in {`priced-in`, `partially-priced`} | `score *= 0.60` | `growth-decelerating` |

Both are no-ops when the block is absent or the value is anything else, so a `data/<slug>.json`
without these blocks scores exactly as it did before 2026-08-30. Applied after the HIGH CAUTION
multiplier and before the final clamp; skipped entirely when the score has already been zeroed
(red-flag / no-edge).
