# Master Score Methodology

`scripts/compute_master_score.py` computes a 0-100 **`master_score`** for every researched
stock — a single number synthesizing the three existing orthogonal scores
(`conviction_score`, `expectation_gap_score`, `quality_score`) plus two new sub-scores
(`consistency_score`, `asymmetry_score`) built specifically from studying how history's
highest-documented-return investors actually describe picking stocks. Purely mechanical,
deterministic — same discipline as every other score in this pipeline.

## Why this exists, and what it's built from

Built 2026-09-05 at the user's request: research real interviews/letters/frameworks from
investors with exceptional documented returns, then fold what's genuinely missing into a
composite that ranks every stock this project has researched or will research. Findings below,
each mapped to what this project already scores vs. what was a real gap.

| Investor / fund | Core mechanism (from research) | Already scored here? |
|---|---|---|
| **Rakesh Jhunjhunwala** | Market opportunity size + business transformation/change + competitive entry barriers + management integrity + price discipline; "asset allocation drives ~60% of returns, stock-picking ~40%" | `value_chain`, `four_box`, `management_quality`, `expectation_gap_score` — yes, mostly. Position-sizing/allocation is a portfolio-construction question, not a per-stock score (see [[project_paper_trading_frontest]]'s concentrated-cohort experiment) |
| **Vijay Kedia (SMILE)** | Small size (early-innings headroom) + Medium/decade-plus management experience, battle-tested through a downturn + Large aspiration + Extra-large market potential | `market_cap_tier`, `four_box.tam`, `management_quality` — yes |
| **Mohnish Pabrai (Dhandho)** | "Heads I win, tails I don't lose much" — look for large uncapped upside paired with a near-floor downside; few bets, big bets, infrequent bets | **Gap.** Nothing in this pipeline explicitly pairs upside magnitude against downside protection as one number → built `asymmetry_score` |
| **Chuck Akre (three-legged stool)** | (1) extraordinary business — enduring high ROE/FCF, (2) talented, aligned management, (3) a reinvestment machine — high returns on capital AND somewhere to keep putting new capital to work at those returns | Legs 1–2 covered (`quality_score`, `management_quality`); leg 3 (does the machine keep compounding, not just clear the bar once) is the same gap Mukherjea's mechanism below fills |
| **Terry Smith (Fundsmith)** | "Buy good companies [high ROCE, strong FCF, durable moat], don't overpay, do nothing [~5% annual turnover]" | ROCE/FCF/moat covered; "don't overpay" = `expectation_gap_score`; "do nothing" is a holding-discipline rule already built into `portfolio-rs1l-revision`'s EMA-only-sell-trigger logic, not a per-stock score |
| **Saurabh Mukherjea (Coffee Can)** | Mechanical two-part filter — revenue growth ≥10% **and** ROCE ≥15% — applied **every year for a decade**, then held untouched. The persistence-over-years is the actual mechanism, not a single good year or a "trending up" read | **Real gap.** `quality_score.roce_trend` is only a 3-level direction (improving/stable/declining) on the *current* read — it cannot distinguish "15%+ ROCE for 8 of the last 10 years" from "15%+ this year, mediocre before." Built `consistency_score` specifically for this |
| **Nick Sleep (Nomad — "scale economics shared")** | Businesses that pass scale-driven cost savings to customers, widening the moat as they grow, held 5-10+ years | Adjacent to `value_chain.supply_side_status` and `capital_allocation_track_record`, not a separate score — genuinely hard to score mechanically without over-fitting, left as an analyst judgment input to `four_box.moat` rather than inventing a fragile new field |
| **Peter Lynch** | PEG < 1 (growth vs. price), scuttlebutt/ground-level research, "know what you own," categorize by growth type | PEG-logic ≈ `expectation_gap_score`'s gap-vs-multiple math; scuttlebutt ≈ the trusted-thread/concall-tracking `trust_component`; categorization is descriptive, not a score |
| **Porinju Veliyath** | Contrarian small-cap value — undervalued, out-of-favor, temporary setbacks, holds through volatility once convinced | `market_cap_tier` + `expectation_gap_score`'s `priced-in`/`underestimated` read; conviction-through-volatility is the EMA discipline's "don't sell on doubt" rule, not a score |
| **Basant Maheshwari** | High ROE (self-funded growth, no dilution), predictable-earnings sectors with tailwinds, "cockroach theory" (one disclosed problem implies more) | ROE/self-funding ≈ `quality_score`; cockroach theory ≈ `red_flag_tier`'s existing hard-veto logic |
| **Li Lu (Himalaya Capital)** | Small, deeply-known circle of competence; concentrated positions (top-5 ≈ 94% of the book in his own 13F) | Circle-of-competence is an analyst discipline, not scorable; concentration is portfolio construction, already being tested separately, not duplicated here |

**Net result:** three genuinely new/enhanced things came out of this research —
`consistency_score` (Mukherjea), `asymmetry_score` (Pabrai), and the widened
`management_component` (Akre's leg 2 + Basant's red-flag framing, actually built the day
before this one — see [[project_quality_score_build]]). Everything else these investors
described was, on inspection, already represented somewhere in the existing scores — the value
of this research pass was mostly confirming that and finding the two real gaps, not inventing
a pile of new machinery.

---

## The two new sub-scores

### `consistency_score` (0-100) — Mukherjea's actual mechanism

Reads a new, deliberately small data field, `track_record`, on `data/<slug>.json`:

```jsonc
"track_record": {
  "years_checked": 5,      // fiscal years actually verifiable from filings (some young companies < 5)
  "years_cleared": 3,      // of years_checked, how many had BOTH revenue growth >=10% AND ROCE >=15%
  "note": "FY22 revenue +8% missed the growth bar; FY23-26 cleared both bars each year"
}
```

Written by `deepdive-top100` from the **same** 3-5 year annual-report read it already does for
`quality_metrics`/`management_quality` — this is one more number extracted from filings already
open, not a new document layer. `years_checked < 3` (too young to have a track record) is left
`null`/absent rather than penalized — Kedia and Porinju's whole edge is buying small, young
companies *before* they have a decade of history, so a brand-new small-cap must never score
worse here than a mediocre 10-year incumbent; it simply isn't assessable yet.

```
consistency_score = round(100 * years_cleared / years_checked)     if years_checked >= 3
                   = not assessed (absent)                          otherwise
```

No red-flag multiplier here — a red flag already zeroes/halves `conviction_score` and
`quality_score`, both of which feed `master_score` independently; re-penalizing here would
triple-count.

### `asymmetry_score` (0-100) — Pabrai's "heads I win, tails I don't lose much"

**Needs no new data at all** — purely derived from the two scores already computed:

```
upside              = expectation_gap_score                                    (0-100, already "is there mispriced upside")
downside_protection = ((debt_component / 20) + (fcf_component / 25)) / 2 * 100  (0-100, from quality_score's own breakdown)

asymmetry_score = 0.5 * upside + 0.5 * downside_protection
                  not assessed if either input is missing
```

`debt_component`/`fcf_component` are `quality_score`'s own sub-terms (low leverage, real cash
conversion) — reused directly rather than re-derived, so this is a free combination, not a new
research burden. A name can score high on `quality_score` overall (say, strong ROCE carrying
the total) while still scoring weak on `asymmetry_score` if that quality isn't backed by a
cash-cushioned balance sheet — exactly the distinction Pabrai's framework is making that a
single quality number can't.

---

## The composite

```
master_score = Σ(weight_i × score_i) / Σ(weight_i)     — over whichever components are present

  conviction_score       weight 0.25   (Jhunjhunwala/Kedia endorsement + thesis-fit, red-flag-gated)
  quality_score           weight 0.25   (Akre leg 1 + Terry Smith + Mukherjea's bar, point-in-time)
  expectation_gap_score   weight 0.20   (Lynch's PEG logic + Terry Smith's "don't overpay" + the user's own rerating thesis)
  consistency_score       weight 0.15   (Mukherjea's actual mechanism — persistence, not a point-in-time read)
  asymmetry_score         weight 0.15   (Pabrai's downside-capped upside)
```

Weights sum to 1.00. **Renormalized over whatever is actually present** — a stock with only
`conviction_score` computed (true for most of the 671-stock registry right now) gets
`master_score = conviction_score` outright; as `deepdive-top100` populates the others over its
normal rotation, `master_score` organically becomes the richer 5-factor blend without ever
being computed on a fabricated or zero-filled component. `master_score` is **not computed at
all** (left absent, bucketed `not_assessed`) for a stock with no `conviction_score`, since that
would mean no research has happened at all.

No red-flag multiplier is applied a second time at this level — `conviction_score` and
`quality_score` already each apply their own (AVOID/EXCLUDE forces to 0, HIGH CAUTION halves),
and those effects propagate into `master_score` through the weighted average automatically.

## Reading the score

Same tier-band convention as the others for familiarity: **≥65** strong overall case ·
**40-64** acceptable · **<40** weak. Given current coverage (`consistency_score` starts at
zero population, `asymmetry_score` gated on `quality_score`'s ~14-stock coverage as of
2026-09-05), `master_score` will closely track `conviction_score` for most of the registry for
a while — this is expected and correct, not a bug, and will visibly diverge from
`conviction_score` as coverage deepens.

**Not yet wired into `portfolio-rs1l-revision`'s add/exit gates** — same staged rollout as
`quality_score`: reported as an annotation first, promoted to an actual ranking input only once
`consistency_score`/`asymmetry_score` have real coverage across the portfolio-relevant universe.

## Running it

```
cd valuepickr-screen/scripts   # or project root
python3 compute_master_score.py
```

Writes `consistency_score`, `asymmetry_score`, and `master_score` onto every eligible stock
entry in `state.json`, and the full ranked report — `{ranked, not_assessed}`, each with a
`score_breakdown` — to `data/master-scores.json`. Wired into `refresh_derived.py --master` (part
of `--all`), which runs after `--scores --gap --quality` since it depends on all three.

---

## Sources consulted (2026-09-05)

- [What was Rakesh Jhunjhunwala's strategy for picking stocks with very high returns?](https://scroll.in/article/1046748/what-was-rakesh-jhunjhunwalas-strategy-for-picking-stocks-with-very-high-returns) — Scroll.in
- ['Stock market investment cannot be taught': Rakesh Jhunjhunwala's mantra](https://www.businesstoday.in/markets/market-commentary/story/stock-market-investment-cannot-be-taught-it-has-to-be-learnt-behind-rakesh-jhunjhunwalas-mantra-to-pick-stocks-388256-2023-07-05) — Business Today
- [Portfolio X-Ray: Vijay Kedia's SMILE is his investing secret](https://trendlyne.com/posts/3912672/portfolio-x-ray-vijay-kedias-smile-is-his-investing-secret) — Trendlyne
- [Vijay Kedia's SMiLE strategy: Transforming investing insights](https://www.valueresearchonline.com/stories/54019/how-to-invest-like-vijay-kedia/) — Value Research Online
- [Dhandho. Heads I win; Tails I don't lose much — Mohnish Pabrai](https://medium.com/@abc_40376/dhandho-heads-i-win-tails-i-dont-lose-much-mohnish-pabrai-3f23ea71466b) — Medium
- [Mohnish Pabrai's Advice on How to Win without Losing Much](https://www.oldschoolvalue.com/investing-strategy/mohnish-pabrai-advice-win/) — Old School Value
- [Chuck Akre's Three-Legged Stool: A Long-Term Investing Framework](https://quartr.com/insights/investment-strategy/chuck-akre-s-three-legged-stool-a-long-term-investing-framework) — Quartr Insights
- [Our Investment Philosophy](https://www.akrecapital.com/investment-approach/our-investment-philosophy/) — Akre Capital Management
- [Super Investors Series: Terry Smith — "Buy Good Companies, Don't Overpay, Do Nothing"](https://substack.com/home/post/p-173996585)
- [A quick summary on Saurabh Mukherjea's Coffee Can Investing](https://medium.com/@jegathshree/a-quick-summary-on-saurabh-mukherjeas-coffee-can-investing-49041d59f72b) — Medium
- [How to Build a Coffee Can Portfolio?](https://groww.in/blog/the-coffee-can-portfolio) — Groww
- [Learning from Nick Sleep](http://mastersinvest.com/newblog/2020/9/16/learning-from-nicholas-sleep) — Investment Masters Class
- [Key Lessons from Nick Sleep's Nomad Investment Letters](https://pomegra.io/wiki/nick-sleep-nomad-investment-letters-lessons/) — Pomegra Wiki
- [Chasing 10-baggers: The Timeless Wisdom of Peter Lynch](https://quartr.com/insights/edge/chasing-10-baggers-the-timeless-wisdom-of-peter-lynch) — Quartr
- [Peter Lynch's tenbaggers in 2026, the actual criteria](https://invest-like.com/blog/peter-lynch-tenbaggers-finding-them-in-2026/) — invest-like
- [The Remarkable Ascent of Porinju Veliyath](https://www.linkedin.com/pulse/remarkable-ascent-porinju-veliyath-lesson-perseverance-karan-d) — LinkedIn
- [Porinju Veliyath: India's Contrarian Value Investor & Small-Cap Czar](https://www.gripinvest.in/blog/porinju-veliyath) — Grip Invest
- [Cockroach Theory In Equity Investing](https://www.equentis.com/blog/cockroach-theory-in-equity-investing/) — Equentis
- [Know About Basant Maheshwari Portfolio Strategies](https://altiusinvestech.com/blog/basant-maheshwari-portfolio/) — Altius Investech
- [Li Lu on Circle of Competency](https://www.gurufocus.com/news/605033/li-lu-on-circle-of-competency) — GuruFocus
- [Himalaya Capital](https://en.wikipedia.org/wiki/Himalaya_Capital) — Wikipedia
