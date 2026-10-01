# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only). Two sibling books are tracked separately and folded into the same dashboard: the continuously-rebalanced `live-recommendation/` tracker (own `TRACKER.md`) and the weekly frozen `swing-6m/cohorts.json` series (own `TRACKER.md`) — see those files, not this one, for their detail.

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-10-01 (generated 2026-10-01 20:29). Daily history: 21 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 41 | 110,193.79 | +0.08% | **+10.19%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 34 | 106,598.95 | +0.05% | **+6.60%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 34 | 101,632.00 | +0.17% | **+1.63%** |
| 2026-W37 | standard | 2026-09-07 | 2026-09-04 | 27 | 103,511.70 | -0.26% | **+3.51%** |
| 2026-W37 | concentrated | 2026-09-07 | 2026-09-04 | 27 | 104,401.90 | +0.18% | **+4.40%** |
| 2026-W39 | standard | 2026-09-21 | 2026-09-18 | 13 | 100,352.79 | -0.35% | **+0.35%** |
| 2026-W39 | concentrated | 2026-09-21 | 2026-09-18 | 13 | 103,744.90 | +0.30% | **+3.74%** |
| 2026-W40 | standard | 2026-09-28 | 2026-09-25 | 6 | 100,115.25 | +0.03% | **+0.12%** |
| 2026-W40 | concentrated | 2026-09-28 | 2026-09-25 | 6 | 102,765.80 | +1.11% | **+2.77%** |

*Concentrated series: 4 cohort(s), average return **+3.14%**.*
*Standard series: 5 cohort(s), average return **+4.15%**.*

**Age-matched:** ~0wk old: standard +0.12% vs concentrated +2.77%; ~1wk old: standard +0.35% vs concentrated +3.74%; ~3wk old: standard +3.51% vs concentrated +4.40%; ~4wk old: standard +6.60% vs concentrated +1.63%.

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | 30W Slope | vs 52W Hi | RS/13wk | Conv-only rank | Δ | Flags |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 ★ | Venus Remedies | **62.5** | 56 | 81 | 4 | 90 | 74/96 | +25.2% | +27.3% | +14.2% | -7.8% | +4.6pp | 1 | 0 | DECELERATING |
| 2 ★ | Aeroflex Industries | **58.6** | 51 | 75 | 6 | 90 | 76/88 | +27.1% | +36.1% | +20.7% | -4.8% | +11.2pp | 2 | 0 | - |
| 3 ★ | Yash Highvoltage | **57.2** | 50 | 49 | 37 | 70 | 71/87 | +29.8% | +37.7% | +17.4% | -0.9% | +28.7pp | 4 | ▲1 | - |
| 4 ★ | Bansal Roofing Products | **56.0** | 46 | 53 | 6 | 88 | 74/100 | +27.4% | +20.3% | +11.7% | +0.0% | +37.7pp | 3 | ▼1 | LEADER (+38pp vs benchmark/13wk) |
| 5 ★ | Macpower CNC Machines | **52.6** | 48 | 44 | 4 | 90 | 56/79 | +40.7% | +45.9% | +29.5% | -0.4% | +56.1pp | 5 | 0 | LEADER (+56pp vs benchmark/13wk) |
| 6 | Entero Healthcare Solutions | **42.9** | 31 | 34 | 33 | 90 | 73/90 | +22.0% | +32.6% | +18.4% | -6.5% | +42.9pp | 7 | ▲1 | FADING (-20pp ext/4wk), LEADER (+43pp vs benchmark/13wk) |
| 7 | L. T. Elevators | **39.9** | 35 | 36 | 24 | 70 | 83/15 | +22.2% | — | +21.3% | -13.0% | +32.5pp | 6 | ▼1 | PEAKED (-13.0% off 52W hi), LEADER (+32pp vs benchmark/13wk) |
| 8 | Novartis India | **24.7** | 10 | 20 | 45 | 88 | 66/74 | +32.2% | +49.3% | +23.1% | -19.8% | +37.4pp | 8 | 0 | PEAKED (-19.8% off 52W hi), LEADER (+37pp vs benchmark/13wk) |
| 9 | Asahi Songwon Colors | **24.7** | 3 | 3 | 45 | 88 | 83/100 | +23.5% | +22.8% | +15.8% | -3.4% | +48.8pp | 9 | 0 | LEADER (+49pp vs benchmark/13wk) |
| 10 | Haldyn Glass | **24.2** | 4 | 3 | 45 | 88 | 76/98 | +25.8% | +23.1% | +12.6% | +0.0% | +25.4pp | 10 | 0 | - |

*Out of pool:* GPT Healthcare (below 30W EMA -0.1%); Dynamic Cables (below 30W EMA -4.2%)

★ = would be in next Monday's concentrated cohort at 25/20/20/17/13% by rank.

**Flags.** None of these gate the pool or the frozen cohorts above; the weekly ext≤0 break stays the only hard exclusion. `THIN CUSHION` and `FADING` are also baked directly into the Tech (wk/mo) score itself (see below) — the other three are advisory-only annotations on top of the score. Added after two post-mortems: Novartis India peaked 2026-09-10 and rolled over ~19% while its Ext/Tech columns, gated to the *last completed* weekly/monthly close, didn't reflect it until the following Monday; Dynamic Cables sat at a paper-thin +1.3%/+1.7% vs its 30W EMA for weeks — inside the old formula's full-marks cushion — before breaking below it; Venus Remedies's Ext vs 30W EMA visibly decayed (+24.9%→+17.8%→+10.6% over three straight weekly reads) while still comfortably positive.
- `THIN CUSHION` *(affects the Tech score)* — Ext vs 30W EMA is positive but under 3% — the old formula scored anything inside the 8% cushion as full marks; this discounts the score toward 0 as ext approaches 0, restoring full marks at the threshold, so a razor-thin cushion no longer looks as safe as a comfortable one right up until the week it breaks.
- `FADING` *(affects the Tech score)* — Ext vs 30W EMA has *shrunk* by 15pp or more over the trailing 4 weeks (a fixed 10-point score penalty) — the cushion is eroding even though it's still comfortably positive, the opposite case from `FAST-EXTENDING` below.
- `PEAKED` — price is already -8% or more off its trailing 52-week high even though it's still above its 30W EMA — the name has cracked before the EMA cushion itself has eroded.
- `FAST-EXTENDING` — Ext vs 30W EMA has gained 25pp or more in the trailing 4 weeks — a blow-off in progress, independent of the absolute extension level (Novartis went +28%→+81.5% in ~1 week).
- `EMA50 BREAK` — the *daily* 50-day EMA has already been broken, well before the slower weekly 30W EMA hard gate would trip.
- `DECELERATING` — the daily 50-day EMA's own slope (trailing 20 days) has turned negative — the short-term trend is rolling over even though price is still above both EMAs.
- `LEADER` / `LAGGING MARKET` — trailing-13-week return vs the Nifty Smallcap 250 benchmark (`30W Slope`/`RS/13wk` columns above) is at or above +30pp / at or below -15pp. Checked against Vikram Thermo (paper-trading's best swing performer, +83pp) and Novartis India (best standard-cohort performer, +34pp) vs Venus Remedies (-17pp) and Dynamic Cables (-25pp, the two worst) — sorting by this one number alone almost exactly reproduced the real return ranking, more cleanly than Ext-vs-EMA alone.

**Trend quality** *(affects the Tech score, additive bonus, capped, never a penalty)* — Vikram Thermo and Novartis India shared three things beyond Ext-vs-EMA: a steeply rising EMA (`30W Slope` column), sitting at/near a fresh 52-week high (`vs 52W Hi`), and strong relative strength (`RS/13wk`). Dynamic Cables and Venus Remedies had none of the three. See `technical`/`technical_monthly`'s `slope_bonus_*`/`rs_bonus_*`/`near_high_*`/`trend_quality_cap` in `config.json` for the exact scaling.

---

## Cohort: 2026-W35-inaugural (standard)

Decided 2026-08-25, entry-priced off 2026-08-21 close. 41 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 1,965.00 | 2026-10-01 | +2.13% | +38.49% | +3.82 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 1,105.75 | 2026-10-01 | +0.36% | +21.22% | +1.74 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 111.95 | 2026-10-01 | +4.02% | +27.72% | +1.39 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 168.45 | 2026-10-01 | +3.22% | +23.36% | +1.37 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 2,144.80 | 2026-10-01 | +0.78% | +14.40% | +1.35 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 146.65 | 2026-10-01 | -4.68% | +10.89% | +0.65 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,796.70 | 2026-10-01 | +5.03% | +3.37% | +0.35 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 371.25 | 2026-10-01 | -3.37% | +0.88% | +0.09 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 151.47 | 2026-10-01 | -1.51% | +0.55% | +0.04 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 133.95 | 2026-09-30* | -4.29% | -5.13% | -0.61 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.08% | **+10.19%** | +10.19 |

\* price carried forward — data source has not yet posted a 2026-10-01 close (Dynamic Cables).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 34 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 1,965.00 | 2026-10-01 | +2.13% | +32.21% | +3.35 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,796.70 | 2026-10-01 | +5.03% | +10.45% | +1.19 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 1,105.75 | 2026-10-01 | +0.36% | +12.13% | +1.08 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 2,144.80 | 2026-10-01 | +0.78% | +6.86% | +0.41 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 146.65 | 2026-10-01 | -4.68% | +5.62% | +0.34 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 168.45 | 2026-10-01 | +3.22% | +7.64% | +0.30 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 371.25 | 2026-10-01 | -3.37% | +1.24% | +0.12 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 151.47 | 2026-10-01 | -1.51% | -0.16% | -0.01 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 133.95 | 2026-09-30* | -4.29% | -2.93% | -0.17 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.05% | **+6.60%** | +6.60 |

\* price carried forward — data source has not yet posted a 2026-10-01 close (Dynamic Cables).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 34 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,796.70 | 2026-10-01 | +5.03% | +10.45% | +2.55 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 2,144.80 | 2026-10-01 | +0.78% | +6.86% | +1.10 |
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 321.80 | 2026-10-01 | -0.05% | -1.92% | -0.38 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 521.35 | 2026-10-01 | -3.38% | -3.83% | -0.75 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,680.80 | 2026-10-01 | -4.77% | -7.07% | -0.89 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.17% | **+1.63%** | +1.63 |


## Cohort: 2026-W37 (standard)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 27 days live. Invested Rs 82,850.92 / cash Rs 17,149.08.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,646.70 | 6 | 9,880.20 | 1,965.00 | 2026-10-01 | +2.13% | +19.33% | +1.91 |
| Yash Highvoltage | 9 | 950.65 | 9 | 8,555.85 | 1,105.75 | 2026-10-01 | +0.36% | +16.32% | +1.40 |
| Macpower CNC Machines | 8 | 1,904.90 | 4 | 7,619.60 | 2,144.80 | 2026-10-01 | +0.78% | +12.59% | +0.96 |
| Venus Remedies | 12 | 1,694.40 | 7 | 11,860.80 | 1,796.70 | 2026-10-01 | +5.03% | +6.04% | +0.72 |
| Bansal Roofing Products | 4 | 157.05 | 25 | 3,926.25 | 168.45 | 2026-10-01 | +3.22% | +7.26% | +0.28 |
| Haldyn Glass | 6 | 146.40 | 40 | 5,856.00 | 146.65 | 2026-10-01 | -4.68% | +0.17% | +0.01 |
| Asahi Songwon Colors | 10 | 372.65 | 26 | 9,688.90 | 371.25 | 2026-10-01 | -3.37% | -0.38% | -0.04 |
| Thyrocare Technologies | 5 | 576.15 | 8 | 4,609.20 | 533.60 | 2026-10-01 | -2.47% | -7.39% | -0.34 |
| GPT Healthcare | 9 | 158.17 | 56 | 8,857.52 | 151.47 | 2026-10-01 | -1.51% | -4.24% | -0.38 |
| Dynamic Cables | 12 | 146.30 | 82 | 11,996.60 | 133.95 | 2026-09-30* | -4.29% | -8.44% | -1.01 |
| **Cash** | | | | 17,149.08 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.26% | **+3.51%** | +3.51 |

\* price carried forward — data source has not yet posted a 2026-10-01 close (Dynamic Cables).

## Cohort: 2026-W37 (concentrated)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 27 days live. Invested Rs 91,727.25 / cash Rs 8,272.75.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Yash Highvoltage | 17 | 950.65 | 17 | 16,161.05 | 1,105.75 | 2026-10-01 | +0.36% | +16.32% | +2.64 |
| Macpower CNC Machines | 20 | 1,904.90 | 10 | 19,049.00 | 2,144.80 | 2026-10-01 | +0.78% | +12.59% | +2.40 |
| Venus Remedies | 25 | 1,694.40 | 14 | 23,721.60 | 1,796.70 | 2026-10-01 | +5.03% | +6.04% | +1.43 |
| Aeroflex Industries | 13 | 537.45 | 24 | 12,898.80 | 521.35 | 2026-10-01 | -3.38% | -3.00% | -0.39 |
| Dynamic Cables | 20 | 146.30 | 136 | 19,896.80 | 133.95 | 2026-09-30* | -4.29% | -8.44% | -1.68 |
| **Cash** | | | | 8,272.75 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.18% | **+4.40%** | +4.40 |

\* price carried forward — data source has not yet posted a 2026-10-01 close (Dynamic Cables).

## Cohort: 2026-W39 (standard)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 13 days live. Invested Rs 81,052.54 / cash Rs 18,947.46.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 12 | 1,582.20 | 7 | 11,075.40 | 1,796.70 | 2026-10-01 | +5.03% | +13.56% | +1.50 |
| Yash Highvoltage | 9 | 1,059.20 | 8 | 8,473.60 | 1,105.75 | 2026-10-01 | +0.36% | +4.39% | +0.37 |
| Bansal Roofing Products | 4 | 156.30 | 25 | 3,907.50 | 168.45 | 2026-10-01 | +3.22% | +7.77% | +0.30 |
| Haldyn Glass | 6 | 141.80 | 42 | 5,955.60 | 146.65 | 2026-10-01 | -4.68% | +3.42% | +0.20 |
| Macpower CNC Machines | 8 | 2,104.50 | 3 | 6,313.50 | 2,144.80 | 2026-10-01 | +0.78% | +1.91% | +0.12 |
| Asahi Songwon Colors | 10 | 372.80 | 26 | 9,692.80 | 371.25 | 2026-10-01 | -3.37% | -0.42% | -0.04 |
| Thyrocare Technologies | 5 | 555.80 | 8 | 4,446.40 | 533.60 | 2026-10-01 | -2.47% | -3.99% | -0.18 |
| Novartis India | 11 | 2,046.80 | 5 | 10,234.00 | 1,965.00 | 2026-10-01 | +2.13% | -4.00% | -0.41 |
| Dynamic Cables | 12 | 142.60 | 84 | 11,978.40 | 133.95 | 2026-09-30* | -4.29% | -6.07% | -0.73 |
| GPT Healthcare | 9 | 166.21 | 54 | 8,975.34 | 151.47 | 2026-10-01 | -1.51% | -8.87% | -0.80 |
| **Cash** | | | | 18,947.46 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.35% | **+0.35%** | +0.35 |

\* price carried forward — data source has not yet posted a 2026-10-01 close (Dynamic Cables).

## Cohort: 2026-W39 (concentrated)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 13 days live. Invested Rs 93,431.00 / cash Rs 6,569.00.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,582.20 | 15 | 23,733.00 | 1,796.70 | 2026-10-01 | +5.03% | +13.56% | +3.22 |
| Bansal Roofing Products | 13 | 156.30 | 83 | 12,972.90 | 168.45 | 2026-10-01 | +3.22% | +7.77% | +1.01 |
| Aeroflex Industries | 20 | 510.90 | 39 | 19,925.10 | 521.35 | 2026-10-01 | -3.38% | +2.05% | +0.41 |
| Macpower CNC Machines | 17 | 2,104.50 | 8 | 16,836.00 | 2,144.80 | 2026-10-01 | +0.78% | +1.91% | +0.32 |
| Dynamic Cables | 20 | 142.60 | 140 | 19,964.00 | 133.95 | 2026-09-30* | -4.29% | -6.07% | -1.21 |
| **Cash** | | | | 6,569.00 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.30% | **+3.74%** | +3.74 |

\* price carried forward — data source has not yet posted a 2026-10-01 close (Dynamic Cables).

## Cohort: 2026-W40 (standard)

Decided 2026-09-28, entry-priced off 2026-09-25 close. 6 days live. Invested Rs 82,912.50 / cash Rs 17,087.50.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Valiant Communications | 8.43 | 1,476.85 | 5 | 7,384.25 | 1,686.35 | 2026-10-01 | +2.07% | +14.19% | +1.05 |
| Venus Remedies | 9.83 | 1,668.40 | 5 | 8,342.00 | 1,796.70 | 2026-10-01 | +5.03% | +7.69% | +0.64 |
| ADF FOOD | 8.56 | 270.60 | 31 | 8,388.60 | 281.40 | 2026-10-01 | +4.88% | +3.99% | +0.33 |
| Macpower CNC Machines | 8.43 | 2,062.50 | 4 | 8,250.00 | 2,144.80 | 2026-10-01 | +0.78% | +3.99% | +0.33 |
| Aries Agro | 8.17 | 473.30 | 17 | 8,046.10 | 477.40 | 2026-10-01 | +0.55% | +0.87% | +0.07 |
| Engineers India | 8.43 | 315.65 | 26 | 8,206.90 | 312.75 | 2026-10-01 | +0.82% | -0.92% | -0.08 |
| SJS Enterprises | 8.43 | 2,317.60 | 3 | 6,952.80 | 2,159.80 | 2026-10-01 | -6.49% | -6.81% | -0.47 |
| Thyrocare | 9.83 | 566.85 | 17 | 9,636.45 | 533.60 | 2026-10-01 | -2.47% | -5.87% | -0.57 |
| Dynamic Cables | 9.2 | 456.95 | 20 | 9,139.00 | 428.00 | 2026-10-01 | -1.36% | -6.34% | -0.58 |
| Matrimony.com | 8.69 | 535.40 | 16 | 8,566.40 | 497.00 | 2026-10-01 | -4.29% | -7.17% | -0.61 |
| **Cash** | | | | 17,087.50 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.03% | **+0.12%** | +0.12 |


## Cohort: 2026-W40 (concentrated)

Decided 2026-09-28, entry-priced off 2026-09-25 close. 6 days live. Invested Rs 91,059.40 / cash Rs 8,940.60.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,668.40 | 14 | 23,357.60 | 1,796.70 | 2026-10-01 | +5.03% | +7.69% | +1.80 |
| Macpower CNC Machines | 20 | 2,062.50 | 9 | 18,562.50 | 2,144.80 | 2026-10-01 | +0.78% | +3.99% | +0.74 |
| Yash Highvoltage | 17 | 1,086.40 | 15 | 16,296.00 | 1,105.75 | 2026-10-01 | +0.36% | +1.78% | +0.29 |
| Bansal Roofing Products | 13 | 167.10 | 77 | 12,866.70 | 168.45 | 2026-10-01 | +3.22% | +0.81% | +0.10 |
| Aeroflex Industries | 20 | 525.70 | 38 | 19,976.60 | 521.35 | 2026-10-01 | -3.38% | -0.83% | -0.17 |
| **Cash** | | | | 8,940.60 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.11% | **+2.77%** | +2.77 |


---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
