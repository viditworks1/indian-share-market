# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only). Two sibling books are tracked separately and folded into the same dashboard: the continuously-rebalanced `live-recommendation/` tracker (own `TRACKER.md`) and the weekly frozen `swing-6m/cohorts.json` series (own `TRACKER.md`) — see those files, not this one, for their detail.

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-10-05 (generated 2026-10-05 19:49). Daily history: 23 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 45 | 109,707.91 | -0.42% | **+9.71%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 38 | 106,361.21 | -0.35% | **+6.36%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 38 | 102,035.20 | +0.21% | **+2.04%** |
| 2026-W37 | standard | 2026-09-07 | 2026-09-04 | 31 | 103,222.14 | -0.37% | **+3.22%** |
| 2026-W37 | concentrated | 2026-09-07 | 2026-09-04 | 31 | 105,152.55 | +1.68% | **+5.15%** |
| 2026-W39 | standard | 2026-09-21 | 2026-09-18 | 17 | 99,982.10 | -0.60% | **-0.02%** |
| 2026-W39 | concentrated | 2026-09-21 | 2026-09-18 | 17 | 103,873.05 | +0.30% | **+3.87%** |
| 2026-W40 | standard | 2026-09-28 | 2026-09-25 | 10 | 100,578.20 | -0.06% | **+0.58%** |
| 2026-W40 | concentrated | 2026-09-28 | 2026-09-25 | 10 | 104,217.00 | +2.09% | **+4.22%** |

*Concentrated series: 4 cohort(s), average return **+3.82%**.*
*Standard series: 5 cohort(s), average return **+3.97%**.*

**Age-matched:** ~1wk old: standard +0.58% vs concentrated +4.22%; ~2wk old: standard -0.02% vs concentrated +3.87%; ~4wk old: standard +3.22% vs concentrated +5.15%; ~5wk old: standard +6.36% vs concentrated +2.04%.

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | 30W Slope | vs 52W Hi | RS/13wk | Conv-only rank | Δ | Flags |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 ★ | Venus Remedies | **62.4** | 56 | 81 | 4 | 90 | 74/94 | +25.3% | +28.6% | +14.2% | -7.7% | +9.2pp | 1 | 0 | DECELERATING |
| 2 ★ | Aeroflex Industries | **59.3** | 51 | 75 | 6 | 90 | 79/90 | +23.8% | +26.2% | +20.4% | -7.6% | +20.9pp | 2 | 0 | - |
| 3 ★ | Yash Highvoltage | **56.8** | 50 | 49 | 37 | 70 | 65/91 | +33.0% | +32.9% | +17.7% | +0.0% | +31.7pp | 3 | 0 | LEADER (+32pp vs benchmark/13wk) |
| 4 ★ | Macpower CNC Machines | **52.6** | 48 | 44 | 4 | 90 | 51/87 | +43.7% | +38.3% | +29.7% | +0.0% | +53.2pp | 4 | 0 | LEADER (+53pp vs benchmark/13wk) |
| 5 ★ | Bansal Roofing Products | **50.7** | 39 | 22 | 6 | 88 | 77/100 | +25.7% | +19.4% | +11.5% | +0.0% | +40.7pp | 7 | ▲2 | LEADER (+41pp vs benchmark/13wk) |
| 6 | Entero Healthcare Solutions | **44.1** | 31 | 34 | 33 | 90 | 76/97 | +20.2% | +17.8% | +18.2% | -8.0% | +44.5pp | 6 | 0 | PEAKED (-8.0% off 52W hi), FADING (-22pp ext/4wk), LEADER (+44pp vs benchmark/13wk) |
| 7 | L. T. Elevators | **40.5** | 35 | 36 | 24 | 70 | 87/15 | +20.0% | — | +21.1% | -14.8% | +33.5pp | 5 | ▼2 | PEAKED (-14.8% off 52W hi), EMA50 BREAK, LEADER (+34pp vs benchmark/13wk) |
| 8 | Haldyn Glass | **26.1** | 4 | 3 | 45 | 88 | 87/100 | +19.5% | +17.6% | +12.1% | -0.6% | +17.4pp | 11 | ▲3 | - |
| 9 | Asahi Songwon Colors | **25.6** | 3 | 3 | 45 | 88 | 89/100 | +18.2% | +13.8% | +15.4% | -7.8% | +45.3pp | 9 | 0 | LEADER (+45pp vs benchmark/13wk) |
| 10 | Novartis India | **25.1** | 10 | 20 | 45 | 88 | 60/85 | +35.1% | +37.4% | +23.3% | -17.8% | +37.4pp | 8 | ▼2 | PEAKED (-17.8% off 52W hi), LEADER (+37pp vs benchmark/13wk) |
| 11 | GPT Healthcare | **17.9** | 16 | 3 | 45 | 88 | 13/39 | +0.4% | +2.0% | +3.0% | -11.2% | -3.1pp | 10 | ▼1 | PEAKED (-11.2% off 52W hi), THIN CUSHION (+0.4% vs 30W EMA), EMA50 BREAK |

*Out of pool:* Dynamic Cables (below 30W EMA -6.9%)

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

Decided 2026-08-25, entry-priced off 2026-08-21 close. 45 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 1,967.80 | 2026-10-05 | +2.54% | +38.68% | +3.84 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 1,155.60 | 2026-10-05 | +7.33% | +26.68% | +2.19 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 2,160.50 | 2026-10-05 | +3.08% | +15.24% | +1.43 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 167.80 | 2026-10-05 | -1.90% | +22.89% | +1.34 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 109.75 | 2026-10-05 | -0.02% | +25.21% | +1.26 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 142.35 | 2026-10-05 | -8.19% | +7.64% | +0.45 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,778.00 | 2026-10-05 | -1.01% | +2.30% | +0.24 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 366.20 | 2026-10-05 | -5.90% | -0.49% | -0.05 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 149.56 | 2026-10-05 | -0.78% | -0.72% | -0.06 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 129.95 | 2026-10-01* | -2.99% | -7.97% | -0.95 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.42% | **+9.71%** | +9.71 |

\* price carried forward — data source has not yet posted a 2026-10-05 close (Dynamic Cables).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 38 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 1,967.80 | 2026-10-05 | +2.54% | +32.40% | +3.37 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 1,155.60 | 2026-10-05 | +7.33% | +17.19% | +1.53 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,778.00 | 2026-10-05 | -1.01% | +9.30% | +1.06 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 2,160.50 | 2026-10-05 | +3.08% | +7.64% | +0.46 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 167.80 | 2026-10-05 | -1.90% | +7.22% | +0.28 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 142.35 | 2026-10-05 | -8.19% | +2.52% | +0.15 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 366.20 | 2026-10-05 | -5.90% | -0.14% | -0.01 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 149.56 | 2026-10-05 | -0.78% | -1.42% | -0.13 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 129.95 | 2026-10-01* | -2.99% | -5.83% | -0.35 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.35% | **+6.36%** | +6.36 |

\* price carried forward — data source has not yet posted a 2026-10-05 close (Dynamic Cables).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 38 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,778.00 | 2026-10-05 | -1.01% | +9.30% | +2.27 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 2,160.50 | 2026-10-05 | +3.08% | +7.64% | +1.23 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 544.35 | 2026-10-05 | +4.41% | +0.42% | +0.08 |
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 315.40 | 2026-10-05 | -3.94% | -3.87% | -0.76 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,697.10 | 2026-10-05 | -0.69% | -6.16% | -0.78 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.21% | **+2.04%** | +2.04 |


## Cohort: 2026-W37 (standard)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 31 days live. Invested Rs 82,850.92 / cash Rs 17,149.08.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,646.70 | 6 | 9,880.20 | 1,967.80 | 2026-10-05 | +2.54% | +19.50% | +1.93 |
| Yash Highvoltage | 9 | 950.65 | 9 | 8,555.85 | 1,155.60 | 2026-10-05 | +7.33% | +21.56% | +1.84 |
| Macpower CNC Machines | 8 | 1,904.90 | 4 | 7,619.60 | 2,160.50 | 2026-10-05 | +3.08% | +13.42% | +1.02 |
| Venus Remedies | 12 | 1,694.40 | 7 | 11,860.80 | 1,778.00 | 2026-10-05 | -1.01% | +4.93% | +0.59 |
| Bansal Roofing Products | 4 | 157.05 | 25 | 3,926.25 | 167.80 | 2026-10-05 | -1.90% | +6.84% | +0.27 |
| Haldyn Glass | 6 | 146.40 | 40 | 5,856.00 | 142.35 | 2026-10-05 | -8.19% | -2.77% | -0.16 |
| Asahi Songwon Colors | 10 | 372.65 | 26 | 9,688.90 | 366.20 | 2026-10-05 | -5.90% | -1.73% | -0.17 |
| Thyrocare Technologies | 5 | 576.15 | 8 | 4,609.20 | 542.05 | 2026-10-05 | +1.58% | -5.92% | -0.27 |
| GPT Healthcare | 9 | 158.17 | 56 | 8,857.52 | 149.56 | 2026-10-05 | -0.78% | -5.44% | -0.48 |
| Dynamic Cables | 12 | 146.30 | 82 | 11,996.60 | 129.95 | 2026-10-01* | -2.99% | -11.18% | -1.34 |
| **Cash** | | | | 17,149.08 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.37% | **+3.22%** | +3.22 |

\* price carried forward — data source has not yet posted a 2026-10-05 close (Dynamic Cables).

## Cohort: 2026-W37 (concentrated)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 31 days live. Invested Rs 91,727.25 / cash Rs 8,272.75.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Yash Highvoltage | 17 | 950.65 | 17 | 16,161.05 | 1,155.60 | 2026-10-05 | +7.33% | +21.56% | +3.48 |
| Macpower CNC Machines | 20 | 1,904.90 | 10 | 19,049.00 | 2,160.50 | 2026-10-05 | +3.08% | +13.42% | +2.56 |
| Venus Remedies | 25 | 1,694.40 | 14 | 23,721.60 | 1,778.00 | 2026-10-05 | -1.01% | +4.93% | +1.17 |
| Aeroflex Industries | 13 | 537.45 | 24 | 12,898.80 | 544.35 | 2026-10-05 | +4.41% | +1.28% | +0.17 |
| Dynamic Cables | 20 | 146.30 | 136 | 19,896.80 | 129.95 | 2026-10-01* | -2.99% | -11.18% | -2.22 |
| **Cash** | | | | 8,272.75 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.68% | **+5.15%** | +5.15 |

\* price carried forward — data source has not yet posted a 2026-10-05 close (Dynamic Cables).

## Cohort: 2026-W39 (standard)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 17 days live. Invested Rs 81,052.54 / cash Rs 18,947.46.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 12 | 1,582.20 | 7 | 11,075.40 | 1,778.00 | 2026-10-05 | -1.01% | +12.38% | +1.37 |
| Yash Highvoltage | 9 | 1,059.20 | 8 | 8,473.60 | 1,155.60 | 2026-10-05 | +7.33% | +9.10% | +0.77 |
| Bansal Roofing Products | 4 | 156.30 | 25 | 3,907.50 | 167.80 | 2026-10-05 | -1.90% | +7.36% | +0.29 |
| Macpower CNC Machines | 8 | 2,104.50 | 3 | 6,313.50 | 2,160.50 | 2026-10-05 | +3.08% | +2.66% | +0.17 |
| Haldyn Glass | 6 | 141.80 | 42 | 5,955.60 | 142.35 | 2026-10-05 | -8.19% | +0.39% | +0.02 |
| Thyrocare Technologies | 5 | 555.80 | 8 | 4,446.40 | 542.05 | 2026-10-05 | +1.58% | -2.47% | -0.11 |
| Asahi Songwon Colors | 10 | 372.80 | 26 | 9,692.80 | 366.20 | 2026-10-05 | -5.90% | -1.77% | -0.17 |
| Novartis India | 11 | 2,046.80 | 5 | 10,234.00 | 1,967.80 | 2026-10-05 | +2.54% | -3.86% | -0.39 |
| GPT Healthcare | 9 | 166.21 | 54 | 8,975.34 | 149.56 | 2026-10-05 | -0.78% | -10.02% | -0.90 |
| Dynamic Cables | 12 | 142.60 | 84 | 11,978.40 | 129.95 | 2026-10-01* | -2.99% | -8.87% | -1.06 |
| **Cash** | | | | 18,947.46 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.60% | **-0.02%** | -0.02 |

\* price carried forward — data source has not yet posted a 2026-10-05 close (Dynamic Cables).

## Cohort: 2026-W39 (concentrated)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 17 days live. Invested Rs 93,431.00 / cash Rs 6,569.00.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,582.20 | 15 | 23,733.00 | 1,778.00 | 2026-10-05 | -1.01% | +12.38% | +2.94 |
| Aeroflex Industries | 20 | 510.90 | 39 | 19,925.10 | 544.35 | 2026-10-05 | +4.41% | +6.55% | +1.30 |
| Bansal Roofing Products | 13 | 156.30 | 83 | 12,972.90 | 167.80 | 2026-10-05 | -1.90% | +7.36% | +0.95 |
| Macpower CNC Machines | 17 | 2,104.50 | 8 | 16,836.00 | 2,160.50 | 2026-10-05 | +3.08% | +2.66% | +0.45 |
| Dynamic Cables | 20 | 142.60 | 140 | 19,964.00 | 129.95 | 2026-10-01* | -2.99% | -8.87% | -1.77 |
| **Cash** | | | | 6,569.00 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.30% | **+3.87%** | +3.87 |

\* price carried forward — data source has not yet posted a 2026-10-05 close (Dynamic Cables).

## Cohort: 2026-W40 (standard)

Decided 2026-09-28, entry-priced off 2026-09-25 close. 10 days live. Invested Rs 82,912.50 / cash Rs 17,087.50.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Valiant Communications | 8.43 | 1,476.85 | 5 | 7,384.25 | 1,686.25 | 2026-10-05 | -2.75% | +14.18% | +1.05 |
| Venus Remedies | 9.83 | 1,668.40 | 5 | 8,342.00 | 1,778.00 | 2026-10-05 | -1.01% | +6.57% | +0.55 |
| Aries Agro | 8.17 | 473.30 | 17 | 8,046.10 | 501.25 | 2026-10-05 | +4.31% | +5.91% | +0.48 |
| Macpower CNC Machines | 8.43 | 2,062.50 | 4 | 8,250.00 | 2,160.50 | 2026-10-05 | +3.08% | +4.75% | +0.39 |
| ADF FOOD | 8.56 | 270.60 | 31 | 8,388.60 | 282.15 | 2026-10-05 | +0.27% | +4.27% | +0.36 |
| Engineers India | 8.43 | 315.65 | 26 | 8,206.90 | 307.85 | 2026-10-05 | -1.57% | -2.47% | -0.20 |
| Matrimony.com | 8.69 | 535.40 | 16 | 8,566.40 | 514.05 | 2026-10-05 | -1.86% | -3.99% | -0.34 |
| Thyrocare | 9.83 | 566.85 | 17 | 9,636.45 | 542.05 | 2026-10-05 | +1.58% | -4.38% | -0.42 |
| Dynamic Cables | 9.2 | 456.95 | 20 | 9,139.00 | 434.85 | 2026-10-05 | +1.60% | -4.84% | -0.44 |
| SJS Enterprises | 8.43 | 2,317.60 | 3 | 6,952.80 | 2,039.60 | 2026-10-05 | -5.57% | -12.00% | -0.83 |
| **Cash** | | | | 17,087.50 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.06% | **+0.58%** | +0.58 |


## Cohort: 2026-W40 (concentrated)

Decided 2026-09-28, entry-priced off 2026-09-25 close. 10 days live. Invested Rs 91,059.40 / cash Rs 8,940.60.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,668.40 | 14 | 23,357.60 | 1,778.00 | 2026-10-05 | -1.01% | +6.57% | +1.53 |
| Yash Highvoltage | 17 | 1,086.40 | 15 | 16,296.00 | 1,155.60 | 2026-10-05 | +7.33% | +6.37% | +1.04 |
| Macpower CNC Machines | 20 | 2,062.50 | 9 | 18,562.50 | 2,160.50 | 2026-10-05 | +3.08% | +4.75% | +0.88 |
| Aeroflex Industries | 20 | 525.70 | 38 | 19,976.60 | 544.35 | 2026-10-05 | +4.41% | +3.55% | +0.71 |
| Bansal Roofing Products | 13 | 167.10 | 77 | 12,866.70 | 167.80 | 2026-10-05 | -1.90% | +0.42% | +0.05 |
| **Cash** | | | | 8,940.60 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +2.09% | **+4.22%** | +4.22 |


---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
