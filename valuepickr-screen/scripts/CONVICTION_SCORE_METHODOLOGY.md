# Conviction Score Methodology

`scripts/compute_conviction_score.py` computes a 0-100 **`conviction_score`** for
every researched stock in `state.json`. It is a purely mechanical, deterministic
function of fields already in `state.json` (plus `trusted_users.json` and a
stock's own `data/<slug>.json`) — no LLM calls, no network calls, same input
always produces the same output.

## Why this exists alongside the existing categorical `conviction` field

The categorical field (`Low` / `Low-Medium` / `Medium` / `Medium-High` / `High`)
is re-derived by LLM judgment on every research run, with nothing mechanical to
check it against past calls. That has caused two real, observed problems:

1. The same underlying situation — small-cap, weak trailing-average ROE, but a
   real recent-quarter inflection — got classified differently across two
   different stocks in two different research runs.
2. An explicit rule ("a very-high-strength trusted-thread candidate with no red
   flag must be at least Medium-High") was violated **twice within the same
   session it was written in**, because nothing was checking the LLM's output
   against it mechanically.

`conviction_score` doesn't replace the categorical field — it's a second,
mechanical signal computed alongside it, so the two can be compared. A stock
where the categorical conviction and the numeric score disagree sharply is
worth a second look; that disagreement is now visible instead of silently
absorbed into a single LLM-chosen label.

## Scope: this score is business-quality + endorsement only, by design

`conviction_score` answers *"is this a good business that trusted people are backing?"* —
base conviction, thesis magnitude, trusted-thread sourcing, multi-user corroboration, red
flags. It deliberately has **no price-vs-expectation input**: a name priced for perfection
and a name with a large unrecognised earnings gap score the same here if their business
quality and endorsement are the same.

That second dimension is a separate, orthogonal score — **`expectation_gap_score`** (0-100),
defined in `GUIDANCE_EXPECTATION_SCHEMA.md`, method in
`../playbook/guidance-and-expectation-gap.md`. It is built from the commitment-chain /
market-expectation blocks on `data/<slug>.json` and answers *"is it mispriced, with a
catalyst, on acceptable risk?"*

A portfolio candidate should clear a bar on **both**. `portfolio-rs1l-revision` treats a
high-`conviction_score` name whose `market_expectation.gap_direction` is `priced-in` as a
watchlist name, not an add — the same way it already treats a name >40% above its 30W EMA.

## The formula

```
raw   = base_anchor          (0-40,  from categorical `conviction`)
      + thesis_bonus         (0-20,  from `thesis_fit`)
      + trust_component      (0-25,  from trusted-thread sourcing)
      + corroboration_bonus  (0-15,  from distinct trusted-user count)
      + management_component  (-8..+8, from data/<slug>.json `management_quality`)
      - red_flag_penalty     (0 or 25 subtracted; AVOID/EXCLUDE forces score to 0)

conviction_score = clamp(raw, 0, 100)
```

### 1. Base conviction anchor (0-40 pts)

Anchors the score to the existing LLM-judged research quality assessment
rather than discarding it:

| categorical `conviction` | points |
|---|---|
| Low | 8 |
| Low-Medium | 16 |
| Medium | 24 |
| Medium-High | 32 |
| High | 40 |
| missing / unrecognized | 0 (most conservative) |

### 2. Thesis-fit magnitude bonus (0-20 pts)

Deliberate design choice for **this screen specifically**: a stock that
doesn't fit the return-magnitude thesis shouldn't score high regardless of
other factors, so a smaller stock with a real 10x-in-2-3-years path ranks
above an otherwise-great business that's already too large to plausibly 10x.

| `thesis_fit` | points |
|---|---|
| `100x-in-10-years` | 20 |
| `10x-in-2-3-years` | 14 |
| `neither` | 0 |
| missing | 0 |

### 3. Red-flag penalty (subtractive / can zero the whole score)

| `red_flag_tier` | effect |
|---|---|
| `null` / `""` | no penalty |
| `"HIGH CAUTION"` | -25 points |
| `"AVOID"` | **entire score forced to 0**, regardless of every other component |
| `"EXCLUDE"` | **entire score forced to 0** |
| any other unrecognized non-empty value | treated as HIGH CAUTION-equivalent (-25) as a conservative default, and flagged in the script's console warning so it can be reviewed |

### 4. Trust / community signal (0-25 pts)

Only applies when `source == "trusted-thread"`:

1. Base points from `trusted_conviction_strength`: `very-high` = 18, `high` = 8,
   missing/unrecognized = 0.
2. Multiplied by a **floor-active** multiplier: `trusted_conviction_floor_active`
   explicitly `false` → ×0.4 (a stale or non-core-sourced signal counts for
   much less); `true` or absent → ×1.0.
3. Multiplied by a **trust-tier** multiplier, looked up via
   `trusted_conviction_source_user` on the stock entry cross-referenced
   against that user's `trust_tier` in `trusted_users.json`: `core` → ×1.0,
   `elevated` → ×0.6. If the source user can't be determined (field absent,
   or user not found in `trusted_users.json`), the neutral default is ×1.0
   (full weight) — this is a deliberate simplification, see below.
4. Capped at 25.

If `source != "trusted-thread"`, this component is 0. **Documented
simplification for this first version**: only trusted-thread-sourced stocks
get any points here, even though `top-contributors.md` / `users.json` may
show a non-trusted high-reputation user made a relevant call elsewhere. A
future version could extend this component to weigh strong non-trusted-thread
community signals too.

As of this run, no stock entries yet carry `trusted_conviction_source_user` or
`trusted_conviction_floor_active` (a concurrent agent's work-in-progress
fields) — both are coded defensively so the script keeps working once they
land, using the neutral/full-weight defaults described above.

### 5. Multi-user corroboration bonus (0-15 pts) — new signal

This is the human-requested addition: if **more than one distinct trusted
user** has independently expressed conviction on the same stock, that's a
stronger signal than a single voice, even a trusted one. The script reads
`data/<slug>.json`'s `trusted_signals` array, counts **distinct usernames**
among entries that are not `superseded` and clear a recency-weight bar (`weight_for_date(entry["date"]) >= 0.15`, using
`scripts/recency_weight.py`), and awards:

| distinct trusted users (non-superseded, reasonably recent) | bonus |
|---|---|
| 0-1 | 0 |
| 2 | +8 |
| 3+ | +15 |

`trusted_signals` entries written by the `x-trusted-cluster` task (username form
`"<handle> (X)"`) count here too — an independent X-cluster voice on a name
already backed on the VP side is genuine corroboration. They never set a
conviction floor (core-tier / `phreakv6` only); this capped bonus is their only
effect on the score.

`recency_weight.py` is a module another concurrent agent is landing in this
project (`weight_for_date(date_str, today=None) -> float`, age-bucketed decay:
≤60d → 1.0, 61-180d → 0.6, 181-365d → 0.25, >365d or unparseable → 0.05). This
script imports it if present and falls back to an inline heuristic with the
identical signature otherwise (see `_fallback_weight_for_date` in
`compute_conviction_score.py` — delete it once the shared module is
permanently in place). As of this run the real module had already landed, so
the live run used it directly.

### 6. Management-quality component (-12 .. +12 pts) — 2026-08-30, widened 2026-09-04

TVGP's "P" (from `../playbook/ishmohit-soic-style.md`): promoter/management quality as a
**positive** attribute, not merely the absence of a red flag. Read from a stock's own
`data/<slug>.json` `management_quality` block (contract:
`ISHMOHIT_SIGNALS_SCHEMA.md`), written by `deepdive-top100` from the 3-year annual-report read
it already does.

```
management_component = clamp(assessment_pts + guidance_pts + capital_alloc_pts
                              + rpt_pts + shareholder_returns_pts, -12, +12)
  assessment_pts:          positive +6 · neutral 0 · concern -6 · absent/unrecognised 0
  guidance_pts:            reliable +2 · over-promises -4 · mixed / no-track-record / unclear / absent 0
  capital_alloc_pts:       disciplined +3 · neutral 0 · value-destructive -4 · unclear/absent 0
  rpt_pts:                 clean +2 · flat +1 · rising -2 · concerning -5 · unclear/absent 0
  shareholder_returns_pts: consistent +2 · initiated +1 · none 0 · erratic -3 · unclear/absent 0
```

- **2026-09-04 widen (user-requested — see [[user_stock_selection_framework]] in memory):**
  the original two-input version only used `assessment` (a subjective one-word roll-up) and
  `guidance_credibility`. Two real gaps existed: `rpt_trend` was already being collected on
  every `management_quality` block (`ISHMOHIT_SIGNALS_SCHEMA.md` §4) but **never actually
  scored** — a stock with `rpt_trend: "concerning"` moved the score by exactly 0 unless the
  analyst's `assessment` word happened to also reflect it. And there was no field at all for
  capital allocation discipline or dividend/buyback history, despite `capital_allocation` prose
  already existing on the block (unscored, narrative-only). Added `capital_allocation_track_record`
  and `shareholder_returns` as new enum fields (schema in `ISHMOHIT_SIGNALS_SCHEMA.md` §4) and
  wired `rpt_trend` into the formula for the first time.
- **Guarded**: returns exactly 0 if the `management_quality` block is absent or the data file
  is unreadable. Any of the five sub-terms individually no-ops (contributes 0) if its field is
  missing or `unclear` — so a stock with only the original two fields populated scores
  identically to before this widen; the three new terms are additive, not replacements.
- Added into `raw` alongside the other components. On an AVOID/EXCLUDE `force_zero` stock it is
  skipped entirely (the whole score is 0 regardless).
- Magnitude: ±12 is still deliberately smaller than `thesis_bonus` (20) or `trust_component`
  (25) — it's one of four TVGP legs and the signal is softer than hard fundamentals — but the
  widen from ±8 reflects that this is now five sub-signals, not two, and a name with weak
  capital allocation AND concerning RPT AND erratic payouts (all three genuinely bad at once)
  should move more than a name that merely has one soft "concern" word attached.
- `assessment: "concern"` / `rpt_trend: "concerning"` are *soft* negatives here; neither sets
  `red_flag_tier` (that stays the forensic tiers' / `audit_state.py`'s job). A genuinely
  governance-flagged name is caught by the red-flag penalty (−25 or force-zero), which dwarfs
  this term even at its new wider range.
- `score_breakdown.management_component` and `score_breakdown.management_quality`
  (`{assessment, guidance_credibility, capital_allocation_track_record, rpt_trend,
  shareholder_returns}` or `null`) are emitted per stock in `data/conviction-scores.json`; the
  run summary prints how many stocks the component is active on.

## Missing/null handling

Every component treats a missing or null field as its most conservative
(lowest-scoring) value rather than crashing or guessing upward. `red_flag_tier`
of `""` (empty string, which appears in 14 stock entries) is treated the same
as `null` — no penalty — since that's clearly how it's being used in this
data (i.e. "checked, no red flag found" rather than "unknown").

## Worked examples (real stocks, from the 2026-08-22 run)

**Venus Remedies — 80.00, near the top, and a clean illustration of every
positive component firing together.**

- categorical `conviction`: `High` → base_anchor = 40
- `thesis_fit`: `10x-in-2-3-years` → thesis_bonus = 14
- `red_flag_tier`: `null` → no penalty
- `source`: `trusted-thread`, `trusted_conviction_strength`: `very-high` → 18
  base trust points, no floor/tier field present yet so ×1.0 → trust_component = 18
- `data/venus-remedies.json` `trusted_signals` shows **2 distinct** trusted
  users (`phreakv6` and `vikas_sinha`) with non-superseded, recent-enough
  entries → corroboration_bonus = 8

`40 + 14 + 18 + 8 - 0 = 80`. Aeroflex Industries lands at the identical 80.00
via the identical breakdown (High / 10x-in-2-3-years / very-high trust / 2
distinct corroborating users: `joinjp2003` and `phreakv6`) — a coincidence of
the discrete point buckets, not a bug.

**Man Industries (India) Limited — 0, the red-flag zeroing-out case.**

- categorical `conviction`: `Low` → base_anchor = 8 (would count, but doesn't matter)
- `thesis_fit`: `neither` → thesis_bonus = 0
- `source`: `trusted-thread`, strength `high` → trust_component = 8 (would count, but doesn't matter)
- `red_flag_tier`: `"EXCLUDE"` → **the whole score is forced to 0**, discarding
  the 8 (base) + 0 (thesis) + 8 (trust) + 0 (corroboration) = 16 raw points it
  would otherwise have earned. This is intentional: an EXCLUDE-tier red flag
  should never be partially offset by an otherwise-decent trust signal — it's
  a hard veto, not a large penalty.

**Cupid Ltd — 1.00, the "HIGH CAUTION subtracts hard but doesn't hard-zero" case, for contrast.**

- categorical `conviction`: `Low` → base_anchor = 8
- `thesis_fit`: `neither` → thesis_bonus = 0
- `source`: `trusted-thread`, strength `very-high` → trust_component = 18
- `red_flag_tier`: `"HIGH CAUTION"` → 25 points subtracted (not a hard zero
  like AVOID/EXCLUDE, but still a heavy penalty)

`raw = base_anchor + thesis_bonus + trust_component + corroboration_bonus - red_flag_penalty`
`= 8 + 0 + 18 + 0 - 25 = 1`.

Even a `very-high` trusted signal (18 pts) can't rescue a `Low`-conviction,
`HIGH CAUTION`-flagged stock — it ends up at 1/100, just short of the hard
floor that AVOID/EXCLUDE would apply. **Banco Products** shows the same
mechanism with a slightly better starting hand (`Low` conviction but
`10x-in-2-3-years` thesis fit, `high`-not-`very-high` trust): `8 + 14 + 8 + 0
- 25 = 5`. Both illustrate that HIGH CAUTION is a heavy, but not absolute,
drag — a stock would need a much stronger base/thesis/trust profile than
either of these to survive it with a non-trivial score.

*(Implementation note for anyone reading the code: `RED_FLAG_PENALTY` is
stored as a positive magnitude — 25 — and subtracted directly in
`compute_score_for_entry`. An earlier draft of this script stored it as
`-25` and then also subtracted it, which double-negated into an accidental
+25 bonus for HIGH CAUTION stocks; caught by manually re-deriving Cupid
Ltd's score by hand against the code before shipping. Worth remembering if
this formula is ever refactored: penalties should be positive magnitudes
subtracted, not pre-negated values also subtracted.)*

## Running it

```
cd valuepickr-screen/scripts   # or project root — both work
python3 compute_conviction_score.py
```

Writes `conviction_score` onto every stock entry in `state.json` with status
`researched`, `excluded`, or `avoid` (candidates with no research yet are left
without the field — there's nothing to score), and writes the full ranked
list, with a `score_breakdown` per stock, to `data/conviction-scores.json`.
