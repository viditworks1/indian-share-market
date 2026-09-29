# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only). Two sibling books are tracked separately and folded into the same dashboard: the continuously-rebalanced `live-recommendation/` tracker (own `TRACKER.md`) and the weekly frozen `swing-6m/cohorts.json` series (own `TRACKER.md`) — see those files, not this one, for their detail.

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-09-29 (generated 2026-09-29 21:10). Daily history: 20 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 39 | 110,100.42 | +0.20% | **+10.10%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 32 | 106,547.77 | +0.47% | **+6.55%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 32 | 101,461.60 | +1.06% | **+1.46%** |
| 2026-W37 | standard | 2026-09-07 | 2026-09-04 | 25 | 103,785.18 | +0.42% | **+3.79%** |
| 2026-W37 | concentrated | 2026-09-07 | 2026-09-04 | 25 | 104,216.35 | +1.79% | **+4.22%** |
| 2026-W39 | standard | 2026-09-21 | 2026-09-18 | 11 | 100,709.56 | +0.48% | **+0.71%** |
| 2026-W39 | concentrated | 2026-09-21 | 2026-09-18 | 11 | 103,435.80 | +1.53% | **+3.44%** |
| 2026-W40 | standard | 2026-09-28 | 2026-09-25 | 4 | 100,083.60 | +1.33% | **+0.08%** |
| 2026-W40 | concentrated | 2026-09-28 | 2026-09-25 | 4 | 101,640.10 | +2.05% | **+1.64%** |

*Concentrated series: 4 cohort(s), average return **+2.69%**.*
*Standard series: 5 cohort(s), average return **+4.25%**.*

**Age-matched:** ~0wk old: standard +0.08% vs concentrated +1.64%; ~1wk old: standard +0.71% vs concentrated +3.44%; ~3wk old: standard +3.79% vs concentrated +4.22%; ~4wk old: standard +6.55% vs concentrated +1.46%.

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | 30W Slope | vs 52W Hi | RS/13wk | Conv-only rank | Δ | Flags |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 ★ | Venus Remedies | **65.1** | 56 | 81 | 4 | 90 | 92/94 | +14.5% | +27.3% | +13.3% | -16.3% | -6.9pp | 1 | 0 | PEAKED (-16.3% off 52W hi), DECELERATING |
| 2 ★ | Aeroflex Industries | **57.9** | 51 | 75 | 6 | 90 | 72/86 | +22.1% | +36.1% | +20.2% | -9.0% | +14.3pp | 2 | 0 | PEAKED (-9.0% off 52W hi), FADING (-16pp ext/4wk) |
| 3 ★ | Yash Highvoltage | **57.7** | 50 | 49 | 37 | 70 | 74/87 | +27.8% | +37.7% | +17.2% | -2.5% | +25.6pp | 4 | ▲1 | - |
| 4 ★ | Bansal Roofing Products | **57.0** | 46 | 53 | 6 | 88 | 81/100 | +23.3% | +20.3% | +11.4% | -1.2% | +32.1pp | 3 | ▼1 | LEADER (+32pp vs benchmark/13wk) |
| 5 ★ | Macpower CNC Machines | **48.0** | 48 | 44 | 4 | 90 | 25/79 | +46.7% | +45.9% | +30.0% | +0.0% | +57.8pp | 5 | 0 | LEADER (+58pp vs benchmark/13wk) |
| 6 | Entero Healthcare Solutions | **43.5** | 31 | 34 | 33 | 90 | 77/90 | +27.3% | +32.6% | +18.8% | -2.1% | +48.2pp | 7 | ▲1 | LEADER (+48pp vs benchmark/13wk) |
| 7 | L. T. Elevators | **39.9** | 35 | 36 | 24 | 70 | 82/15 | +22.3% | — | +21.3% | -13.0% | +25.3pp | 6 | ▼1 | PEAKED (-13.0% off 52W hi) |
| 8 | GPT Healthcare | **37.0** | 16 | 3 | 45 | 88 | 100/100 | +3.2% | +7.9% | +3.2% | -8.4% | +3.4pp | 10 | ▲2 | PEAKED (-8.4% off 52W hi), EMA50 BREAK |
| 9 | Haldyn Glass | **24.9** | 4 | 3 | 45 | 88 | 81/98 | +23.5% | +23.1% | +12.4% | +0.0% | +34.8pp | 11 | ▲2 | LEADER (+35pp vs benchmark/13wk) |
| 10 | Asahi Songwon Colors | **24.9** | 3 | 3 | 45 | 88 | 84/100 | +22.9% | +22.8% | +15.8% | -3.9% | +52.6pp | 9 | ▼1 | LEADER (+53pp vs benchmark/13wk) |
| 11 | Novartis India | **24.4** | 10 | 20 | 45 | 88 | 64/74 | +33.2% | +49.3% | +23.2% | -19.1% | +34.0pp | 8 | ▼3 | PEAKED (-19.1% off 52W hi), LEADER (+34pp vs benchmark/13wk) |

*Out of pool:* Dynamic Cables (below 30W EMA -0.2%)

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

Decided 2026-08-25, entry-priced off 2026-08-21 close. 39 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 1,924.10 | 2026-09-29 | -0.56% | +35.61% | +3.54 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 1,101.80 | 2026-09-29 | +4.07% | +20.78% | +1.71 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 2,128.10 | 2026-09-29 | -3.03% | +13.51% | +1.27 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 163.20 | 2026-09-29 | -1.12% | +19.52% | +1.15 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 107.62 | 2026-09-29 | -0.70% | +22.78% | +1.14 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 153.85 | 2026-09-29 | +1.22% | +16.33% | +0.97 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 384.20 | 2026-09-29 | -0.77% | +4.40% | +0.44 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 153.80 | 2026-09-29 | -1.47% | +2.10% | +0.17 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 139.95 | 2026-09-28* | -0.00% | -0.89% | -0.11 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,710.60 | 2026-09-29 | +5.00% | -1.58% | -0.17 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.20% | **+10.10%** | +10.10 |

\* price carried forward — data source has not yet posted a 2026-09-29 close (Dynamic Cables).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 32 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 1,924.10 | 2026-09-29 | -0.56% | +29.46% | +3.06 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 1,101.80 | 2026-09-29 | +4.07% | +11.73% | +1.04 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 153.85 | 2026-09-29 | +1.22% | +10.80% | +0.65 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,710.60 | 2026-09-29 | +5.00% | +5.16% | +0.59 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 384.20 | 2026-09-29 | -0.77% | +4.77% | +0.47 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 2,128.10 | 2026-09-29 | -3.03% | +6.03% | +0.36 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 163.20 | 2026-09-29 | -1.12% | +4.28% | +0.17 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 153.80 | 2026-09-29 | -1.47% | +1.37% | +0.12 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 139.95 | 2026-09-28* | -0.00% | +1.41% | +0.08 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.47% | **+6.55%** | +6.55 |

\* price carried forward — data source has not yet posted a 2026-09-29 close (Dynamic Cables).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 32 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,710.60 | 2026-09-29 | +5.00% | +5.16% | +1.26 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 2,128.10 | 2026-09-29 | -3.03% | +6.03% | +0.97 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 539.60 | 2026-09-29 | +5.10% | -0.46% | -0.09 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,764.90 | 2026-09-29 | -1.41% | -2.42% | -0.31 |
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 321.95 | 2026-09-29 | -1.99% | -1.87% | -0.37 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.06% | **+1.46%** | +1.46 |


## Cohort: 2026-W37 (standard)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 25 days live. Invested Rs 82,850.92 / cash Rs 17,149.08.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,646.70 | 6 | 9,880.20 | 1,924.10 | 2026-09-29 | -0.56% | +16.85% | +1.66 |
| Yash Highvoltage | 9 | 950.65 | 9 | 8,555.85 | 1,101.80 | 2026-09-29 | +4.07% | +15.90% | +1.36 |
| Macpower CNC Machines | 8 | 1,904.90 | 4 | 7,619.60 | 2,128.10 | 2026-09-29 | -3.03% | +11.72% | +0.89 |
| Asahi Songwon Colors | 10 | 372.65 | 26 | 9,688.90 | 384.20 | 2026-09-29 | -0.77% | +3.10% | +0.30 |
| Haldyn Glass | 6 | 146.40 | 40 | 5,856.00 | 153.85 | 2026-09-29 | +1.22% | +5.09% | +0.30 |
| Bansal Roofing Products | 4 | 157.05 | 25 | 3,926.25 | 163.20 | 2026-09-29 | -1.12% | +3.92% | +0.15 |
| Venus Remedies | 12 | 1,694.40 | 7 | 11,860.80 | 1,710.60 | 2026-09-29 | +5.00% | +0.96% | +0.11 |
| Thyrocare Technologies | 5 | 576.15 | 8 | 4,609.20 | 547.10 | 2026-09-29 | -0.22% | -5.04% | -0.23 |
| GPT Healthcare | 9 | 158.17 | 56 | 8,857.52 | 153.80 | 2026-09-29 | -1.47% | -2.76% | -0.24 |
| Dynamic Cables | 12 | 146.30 | 82 | 11,996.60 | 139.95 | 2026-09-28* | -0.00% | -4.34% | -0.52 |
| **Cash** | | | | 17,149.08 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.42% | **+3.79%** | +3.79 |

\* price carried forward — data source has not yet posted a 2026-09-29 close (Dynamic Cables).

## Cohort: 2026-W37 (concentrated)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 25 days live. Invested Rs 91,727.25 / cash Rs 8,272.75.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Yash Highvoltage | 17 | 950.65 | 17 | 16,161.05 | 1,101.80 | 2026-09-29 | +4.07% | +15.90% | +2.57 |
| Macpower CNC Machines | 20 | 1,904.90 | 10 | 19,049.00 | 2,128.10 | 2026-09-29 | -3.03% | +11.72% | +2.23 |
| Venus Remedies | 25 | 1,694.40 | 14 | 23,721.60 | 1,710.60 | 2026-09-29 | +5.00% | +0.96% | +0.23 |
| Aeroflex Industries | 13 | 537.45 | 24 | 12,898.80 | 539.60 | 2026-09-29 | +5.10% | +0.40% | +0.05 |
| Dynamic Cables | 20 | 146.30 | 136 | 19,896.80 | 139.95 | 2026-09-28* | -0.00% | -4.34% | -0.86 |
| **Cash** | | | | 8,272.75 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.79% | **+4.22%** | +4.22 |

\* price carried forward — data source has not yet posted a 2026-09-29 close (Dynamic Cables).

## Cohort: 2026-W39 (standard)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 11 days live. Invested Rs 81,052.54 / cash Rs 18,947.46.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 12 | 1,582.20 | 7 | 11,075.40 | 1,710.60 | 2026-09-29 | +5.00% | +8.12% | +0.90 |
| Haldyn Glass | 6 | 141.80 | 42 | 5,955.60 | 153.85 | 2026-09-29 | +1.22% | +8.50% | +0.51 |
| Yash Highvoltage | 9 | 1,059.20 | 8 | 8,473.60 | 1,101.80 | 2026-09-29 | +4.07% | +4.02% | +0.34 |
| Asahi Songwon Colors | 10 | 372.80 | 26 | 9,692.80 | 384.20 | 2026-09-29 | -0.77% | +3.06% | +0.30 |
| Bansal Roofing Products | 4 | 156.30 | 25 | 3,907.50 | 163.20 | 2026-09-29 | -1.12% | +4.41% | +0.17 |
| Macpower CNC Machines | 8 | 2,104.50 | 3 | 6,313.50 | 2,128.10 | 2026-09-29 | -3.03% | +1.12% | +0.07 |
| Thyrocare Technologies | 5 | 555.80 | 8 | 4,446.40 | 547.10 | 2026-09-29 | -0.22% | -1.57% | -0.07 |
| Dynamic Cables | 12 | 142.60 | 84 | 11,978.40 | 139.95 | 2026-09-28* | -0.00% | -1.86% | -0.22 |
| Novartis India | 11 | 2,046.80 | 5 | 10,234.00 | 1,924.10 | 2026-09-29 | -0.56% | -5.99% | -0.61 |
| GPT Healthcare | 9 | 166.21 | 54 | 8,975.34 | 153.80 | 2026-09-29 | -1.47% | -7.47% | -0.67 |
| **Cash** | | | | 18,947.46 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.48% | **+0.71%** | +0.71 |

\* price carried forward — data source has not yet posted a 2026-09-29 close (Dynamic Cables).

## Cohort: 2026-W39 (concentrated)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 11 days live. Invested Rs 93,431.00 / cash Rs 6,569.00.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,582.20 | 15 | 23,733.00 | 1,710.60 | 2026-09-29 | +5.00% | +8.12% | +1.93 |
| Aeroflex Industries | 20 | 510.90 | 39 | 19,925.10 | 539.60 | 2026-09-29 | +5.10% | +5.62% | +1.12 |
| Bansal Roofing Products | 13 | 156.30 | 83 | 12,972.90 | 163.20 | 2026-09-29 | -1.12% | +4.41% | +0.57 |
| Macpower CNC Machines | 17 | 2,104.50 | 8 | 16,836.00 | 2,128.10 | 2026-09-29 | -3.03% | +1.12% | +0.19 |
| Dynamic Cables | 20 | 142.60 | 140 | 19,964.00 | 139.95 | 2026-09-28* | -0.00% | -1.86% | -0.37 |
| **Cash** | | | | 6,569.00 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.53% | **+3.44%** | +3.44 |

\* price carried forward — data source has not yet posted a 2026-09-29 close (Dynamic Cables).

## Cohort: 2026-W40 (standard)

Decided 2026-09-28, entry-priced off 2026-09-25 close. 4 days live. Invested Rs 82,912.50 / cash Rs 17,087.50.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Valiant Communications | 8.43 | 1,476.85 | 5 | 7,384.25 | 1,652.10 | 2026-09-29 | +15.00% | +11.87% | +0.88 |
| Macpower CNC Machines | 8.43 | 2,062.50 | 4 | 8,250.00 | 2,128.10 | 2026-09-29 | -3.03% | +3.18% | +0.26 |
| Venus Remedies | 9.83 | 1,668.40 | 5 | 8,342.00 | 1,710.60 | 2026-09-29 | +5.00% | +2.53% | +0.21 |
| Aries Agro | 8.17 | 473.30 | 17 | 8,046.10 | 474.80 | 2026-09-29 | +0.91% | +0.32% | +0.03 |
| SJS Enterprises | 8.43 | 2,317.60 | 3 | 6,952.80 | 2,309.80 | 2026-09-29 | +2.13% | -0.34% | -0.02 |
| ADF FOOD | 8.56 | 270.60 | 31 | 8,388.60 | 268.30 | 2026-09-29 | +0.64% | -0.85% | -0.07 |
| Engineers India | 8.43 | 315.65 | 26 | 8,206.90 | 310.20 | 2026-09-29 | -1.18% | -1.73% | -0.14 |
| Matrimony.com | 8.69 | 535.40 | 16 | 8,566.40 | 519.25 | 2026-09-29 | -0.40% | -3.02% | -0.26 |
| Thyrocare | 9.83 | 566.85 | 17 | 9,636.45 | 547.10 | 2026-09-29 | -0.22% | -3.48% | -0.34 |
| Dynamic Cables | 9.2 | 456.95 | 20 | 9,139.00 | 433.90 | 2026-09-29 | -0.29% | -5.04% | -0.46 |
| **Cash** | | | | 17,087.50 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.33% | **+0.08%** | +0.08 |


## Cohort: 2026-W40 (concentrated)

Decided 2026-09-28, entry-priced off 2026-09-25 close. 4 days live. Invested Rs 91,059.40 / cash Rs 8,940.60.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,668.40 | 14 | 23,357.60 | 1,710.60 | 2026-09-29 | +5.00% | +2.53% | +0.59 |
| Macpower CNC Machines | 20 | 2,062.50 | 9 | 18,562.50 | 2,128.10 | 2026-09-29 | -3.03% | +3.18% | +0.59 |
| Aeroflex Industries | 20 | 525.70 | 38 | 19,976.60 | 539.60 | 2026-09-29 | +5.10% | +2.64% | +0.53 |
| Yash Highvoltage | 17 | 1,086.40 | 15 | 16,296.00 | 1,101.80 | 2026-09-29 | +4.07% | +1.42% | +0.23 |
| Bansal Roofing Products | 13 | 167.10 | 77 | 12,866.70 | 163.20 | 2026-09-29 | -1.12% | -2.33% | -0.30 |
| **Cash** | | | | 8,940.60 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +2.05% | **+1.64%** | +1.64 |


---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
