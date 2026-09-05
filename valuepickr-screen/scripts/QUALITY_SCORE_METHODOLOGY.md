# Quality Score Methodology

`scripts/compute_quality_score.py` computes a 0-100 **`quality_score`** for every
researched stock whose `data/<slug>.json` carries a `quality_metrics` block
(schema: `ISHMOHIT_SIGNALS_SCHEMA.md` §6). Purely mechanical, deterministic — no
LLM calls, no network calls, same input always produces the same output. Same
discipline as `compute_conviction_score.py` / `compute_expectation_gap_score.py`.

## Why this exists

The user's own stated stock-selection framework (2026-09-04): *"growth + margins
+ ROCE + debt + capex + free cash flow + competitive advantage + management
quality. Good business will always be overpriced. We need to bet on future
rerating."*

That last sentence is already how the pipeline works — `expectation_gap_score`
*is* the rerating bet, mechanically: it zeroes a name once its guidance is fully
priced in (the `no-edge` flag) and rewards a name whose catalyst isn't in the
multiple yet. But of the eight legs in the framework, four already had a
numeric home and four didn't:

| Leg | Existing home |
|---|---|
| Growth | `growth_trajectory.yoy_trend` (Ishmohit-lens) |
| Competitive advantage | `value_chain` (Ishmohit-lens) |
| Management quality | `management_quality` → `conviction_score`'s `management_component` |
| Margins (direction) | `earnings_quality.margin_driver` / `peak_margin_risk` |
| **ROCE** | **nothing** |
| **Debt** | **nothing** (only promoter-pledge governance flags, not balance-sheet leverage) |
| **Free cash flow** | **nothing** |
| **Capex (efficiency, not just timing)** | tracked as *catalyst timing* (capex-grace-period rule), never as a quality signal |

`quality_score` is the missing piece: a mechanical, comparable number for the
four legs nothing else was scoring. It is deliberately narrow — it does not
re-score growth, moat, or management (those already have scores) — so it can
sit alongside `conviction_score` and `expectation_gap_score` as a third,
orthogonal axis without duplicating either.

## Scope: this score answers a different question from the other two

- `conviction_score` — *is this a good business that trusted people are backing?*
- `expectation_gap_score` — *is it mispriced, with a catalyst, on acceptable risk?*
- `quality_score` — ***is the balance sheet and cash generation actually as good
  as the growth story suggests?***

A name can clear both existing bars — real growth, trusted-thread conviction,
an underpriced catalyst — and still be quietly funding that growth with rising
leverage or earnings that never convert to cash. Neither existing score would
catch that. `quality_score` is built specifically to.

## The formula

```
raw   = roce_component     (0-25,  level 0-18 + trend 0-7)
      + debt_component     (0-20,  net_debt_to_ebitda, or interest_coverage as fallback)
      + fcf_component      (0-25,  fcf_conversion_pct — CAN be negative)
      + margin_component   (0-15,  margin_trend)
      + capex_component    (0-15,  capex_efficiency)

quality_score = clamp(raw, 0, 100)
                * 0.5  if red_flag_tier == "HIGH CAUTION"
                = 0    if red_flag_tier in {AVOID, EXCLUDE}
```

Components sum to exactly 100 at the ceiling by design (unlike
`conviction_score`, whose components can overshoot 100 and get clamped) — there
is no "impossible to max out" headroom here, since none of these five legs are
double-counting the same underlying fact the way trust + corroboration can.

### 1. ROCE component (0-25 = level 0-18 + trend 0-7)

| `roce_pct` | level pts |
|---|---|
| ≥ 25% | 18 |
| 20–24.99% | 14 |
| 15–19.99% | 10 |
| 10–14.99% | 5 |
| < 10% | 0 |
| missing | 0 |

| `roce_trend` | trend pts |
|---|---|
| `improving` | 7 |
| `stable` | 3 |
| `declining` | 0 |
| `unclear` / missing | 0 |

A high but *declining* ROCE (peak-margin-adjacent story) scores well on level
but nothing on trend — deliberately, since a fading ROCE on an already-rich
multiple is exactly the setup this score exists to flag.

### 2. Debt / leverage component (0-20)

Primary input `net_debt_to_ebitda`:

| value | pts |
|---|---|
| ≤ 0 (net cash) | 20 |
| 0 < x ≤ 1 | 16 |
| 1 < x ≤ 2 | 10 |
| 2 < x ≤ 3 | 4 |
| > 3 | 0 |

If `net_debt_to_ebitda` isn't derivable (null), fall back to
`interest_coverage`:

| value | pts |
|---|---|
| ≥ 8x | 16 |
| 4–7.99x | 10 |
| 2–3.99x | 4 |
| < 2x | 0 |

If *neither* field is populated, the component is 0 — the conservative
default, same convention as every other missing field in this pipeline.

### 3. Free cash flow component (0-25)

From `fcf_conversion_pct` (trailing 3y avg (CFO − capex) / EBITDA, %):

| value | pts |
|---|---|
| ≥ 80% | 25 |
| 60–79.99% | 20 |
| 40–59.99% | 14 |
| 20–39.99% | 7 |
| 0–19.99% | 2 |
| < 0% (negative conversion) | 0 |
| missing | 0 |

This is the field most likely to catch a name the other two scores would
happily hold: strong revenue/EBITDA growth with cash generation that never
shows up, usually working-capital bloat or aggressive revenue recognition —
exactly the failure mode capex-heavy order-book names (cables, EPC, capital
goods) are prone to.

### 4. Margin trend component (0-15)

| `margin_trend` | pts |
|---|---|
| `expanding` | 15 |
| `stable` | 9 |
| `contracting` | 0 |
| `unclear` / missing | 0 |

Distinct from `earnings_quality.margin_driver` (structural vs. cyclical —
*why* margins are where they are) — this is the simpler *direction* question,
scored numerically for the first time.

### 5. Capex efficiency component (0-15)

| `capex_efficiency` | pts |
|---|---|
| `productive` | 15 |
| `neutral` | 7 |
| `value-destructive` | 0 |
| `unclear` / missing | 0 |

Is new capital actually earning back above the cost of capital — asset turn
holding up as capex lands on schedule — versus serial capex raises with
declining returns, repeated commissioning slippage, or capex funding an
unrelated diversification.

### Red-flag interaction

Identical convention to `conviction_score` / `expectation_gap_score`:
`HIGH CAUTION` halves the score, `AVOID`/`EXCLUDE` forces it to exactly 0,
regardless of how strong the underlying balance sheet looks. A governance red
flag means the numbers can't be trusted in the first place, so no combination
of ROCE/debt/FCF/margin/capex should be able to offset it.

## Missing/null handling

Every component treats a missing field as its most conservative (lowest-
scoring) value — never guesses upward, never crashes. Critically: a stock with
**no `quality_metrics` block at all** is NOT scored 0. It is left without a
`quality_score` key entirely and reported under `not_assessed` in
`data/quality-scores.json` — the same "not yet assessed" convention
`expectation_gap_score` uses for a stock with no `market_expectation` block.
This is a strict no-op on the whole registry (671 stocks as of 2026-09-04, most
without any Ishmohit-lens blocks yet) until `deepdive-top100` starts populating
`quality_metrics` per stock — it will not silently zero out unscored names in
any ranking or gate that reads this file.

## Worked example — Dynamic Cables (current Rs 1L portfolio holding)

From its existing `data/dynamic-cables.json` fundamentals (deep-dive pass 1,
2026-09-02): ROCE ~26.2% (steady, not yet flagged improving/declining in the
existing prose — would need an explicit `roce_trend` read), net adjusted
leverage 0.68x, interest coverage 11.3x, OPM held 9%→10%→10%→11% across FY23-26
and stable at ~11% through the last 6 quarters (margin trend: `stable`, not yet
`expanding` since the level itself isn't rising, just holding), greenfield
capex ~Rs 45 Cr at a 6x asset turn, on a dated schedule (capex efficiency:
`productive`).

- `roce_component`: level 18 (≥25%) + trend 3 (assume `stable` pending an
  explicit multi-year read) = 21
- `debt_component`: net_debt_to_ebitda 0.68 → 16
- `fcf_component`: not yet derivable from the existing narrative (no explicit
  CFO/capex figure captured) → 0 pending a `deepdive-top100` pass that
  extracts it
- `margin_component`: `stable` → 9
- `capex_component`: `productive` → 15

`raw = 21 + 16 + 0 + 9 + 15 = 61`. No red flag → `quality_score = 61.0`
(`35-59` acceptable / `≥60` strong banding — this lands just at the strong
line, consistent with the name's real strengths: low leverage, high ROCE,
disciplined small-ticket capex — with FCF conversion the one leg that needs a
proper number rather than an inferred 0.

## Reading the score

Same tier bands as `conviction_score` for familiarity: **≥60** strong quality
· **35-59** acceptable · **<35** weak. Unlike `conviction_score`/
`expectation_gap_score`, this is **not yet wired into `portfolio-rs1l-
revision`'s add/exit gates** — coverage is too thin (a handful of stocks
hand-backfilled as a smoke test vs. 671 in the registry) to make it a hard
gate without it defaulting to the not-yet-assessed fallback on almost every
candidate. It is read and reported alongside the other two scores as an
annotation for now; promoting it to a hard AND-gate (the same way
`expectation_gap_score` was added 2026-08-30) is a decision to revisit once
`deepdive-top100` has meaningfully populated `quality_metrics` across the
portfolio-relevant universe (tierA/tierB names, current holdings, watchlist).

## Running it

```
cd valuepickr-screen/scripts   # or project root — both work
python3 compute_quality_score.py
```

Writes `quality_score` onto every stock entry in `state.json` whose
`data/<slug>.json` has a `quality_metrics` block, and writes the full ranked
report — `{ranked, weak, not_assessed}`, each with a `score_breakdown` per
stock — to `data/quality-scores.json`.

`refresh_derived.py --quality` (or `--all`, the default) runs it as part of the
standard post-batch salvo, alongside `--scores` and `--gap`.
