# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only). Two sibling books are tracked separately and folded into the same dashboard: the continuously-rebalanced `live-recommendation/` tracker (own `TRACKER.md`) and the weekly frozen `swing-6m/cohorts.json` series (own `TRACKER.md`) — see those files, not this one, for their detail.

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-09-26 (generated 2026-09-26 13:27). Daily history: 18 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 36 | 109,808.46 | -0.07% | **+9.81%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 29 | 106,180.64 | -0.41% | **+6.18%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 29 | 100,952.30 | -0.46% | **+0.95%** |
| 2026-W37 | standard | 2026-09-07 | 2026-09-04 | 22 | 103,811.96 | -0.37% | **+3.81%** |
| 2026-W37 | concentrated | 2026-09-07 | 2026-09-04 | 22 | 102,470.55 | -0.95% | **+2.47%** |
| 2026-W39 | standard | 2026-09-21 | 2026-09-18 | 8 | 100,786.58 | -0.32% | **+0.79%** |
| 2026-W39 | concentrated | 2026-09-21 | 2026-09-18 | 8 | 102,072.10 | +0.26% | **+2.07%** |

*Concentrated series: 3 cohort(s), average return **+1.83%**.*
*Standard series: 4 cohort(s), average return **+5.15%**.*

**Age-matched:** ~1wk old: standard +0.79% vs concentrated +2.07%; ~3wk old: standard +3.81% vs concentrated +2.47%; ~4wk old: standard +6.18% vs concentrated +0.95%.

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | Conv-only rank | Δ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 ★ | Venus Remedies | **79.2** | 77 | 91 | 70 | 90 | 86/88 | +15.5% | +27.3% | 1 | 0 |
| 2 ★ | Dynamic Cables | **75.6** | 68 | 60 | 65 | 90 | 100/100 | +5.8% | +4.7% | 5 | ▲3 |
| 3 ★ | Macpower CNC Machines | **61.5** | 65 | 81 | 30 | 90 | 38/69 | +42.4% | +45.9% | 3 | 0 |
| 4 ★ | Aeroflex Industries | **57.1** | 52 | 85 | 0 | 90 | 66/79 | +26.9% | +36.1% | 2 | ▼2 |
| 5 ★ | Bansal Roofing Products | **55.6** | 46 | 53 | 6 | 88 | 75/95 | +21.9% | +20.3% | 6 | ▲1 |
| 6 | Yash Highvoltage | **54.6** | 50 | 49 | 37 | 70 | 60/77 | +30.4% | +37.7% | 7 | ▲1 |
| 7 | Entero Healthcare Solutions | **44.2** | 37 | 61 | 33 | 90 | 53/82 | +34.1% | +32.6% | 4 | ▼3 |
| 8 | GPT Healthcare | **37.0** | 16 | 3 | 45 | 88 | 100/100 | +7.2% | +7.9% | 11 | ▲3 |
| 9 | L. T. Elevators | **36.8** | 35 | 36 | 24 | 70 | 62/15 | +29.1% | — | 8 | ▼1 |
| 10 | Haldyn Glass | **23.9** | 4 | 3 | 45 | 88 | 78/92 | +20.1% | +23.1% | 12 | ▲2 |
| 11 | Asahi Songwon Colors | **22.5** | 3 | 3 | 45 | 88 | 68/100 | +25.5% | +22.8% | 10 | ▼1 |
| 12 | Novartis India | **20.7** | 10 | 20 | 45 | 88 | 44/66 | +38.9% | +49.3% | 9 | ▼3 |

★ = would be in next Monday's concentrated cohort at 25/20/20/17/13% by rank.

---

## Cohort: 2026-W35-inaugural (standard)

Decided 2026-08-25, entry-priced off 2026-08-21 close. 36 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 1,971.40 | 2026-09-24* | +0.00% | +38.94% | +3.87 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 1,056.40 | 2026-09-24* | -5.93% | +15.81% | +1.30 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 160.00 | 2026-09-24* | +1.04% | +17.17% | +1.01 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 105.42 | 2026-09-24* | +4.99% | +20.27% | +1.01 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 2,061.10 | 2026-09-24* | +0.00% | +9.94% | +0.93 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 149.00 | 2026-09-24* | +0.91% | +5.52% | +0.66 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 161.73 | 2026-09-24* | -0.00% | +7.36% | +0.59 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 145.30 | 2026-09-24* | -1.26% | +9.87% | +0.59 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 388.00 | 2026-09-24* | +1.33% | +5.43% | +0.54 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,624.80 | 2026-09-24* | +0.00% | -6.52% | -0.68 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.07% | **+9.81%** | +9.81 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, RNIT AI Solutions, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 29 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 1,971.40 | 2026-09-24* | +0.00% | +32.64% | +3.40 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 1,056.40 | 2026-09-24* | -5.93% | +7.13% | +0.63 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 161.73 | 2026-09-24* | -0.00% | +6.60% | +0.59 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 388.00 | 2026-09-24* | +1.33% | +5.81% | +0.58 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 149.00 | 2026-09-24* | +0.91% | +7.97% | +0.47 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 145.30 | 2026-09-24* | -1.26% | +4.65% | +0.28 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 2,061.10 | 2026-09-24* | +0.00% | +2.69% | +0.16 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 160.00 | 2026-09-24* | +1.04% | +2.24% | +0.09 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,624.80 | 2026-09-24* | +0.00% | -0.12% | -0.01 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.41% | **+6.18%** | +6.18 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 29 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 342.00 | 2026-09-24* | -1.99% | +4.24% | +0.83 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 2,061.10 | 2026-09-24* | +0.00% | +2.69% | +0.43 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,852.20 | 2026-09-24* | -0.00% | +2.41% | +0.31 |
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,624.80 | 2026-09-24* | +0.00% | -0.12% | -0.03 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 525.70 | 2026-09-25* | -0.28% | -3.03% | -0.59 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.46% | **+0.95%** | +0.95 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Aeroflex Industries, Entero Healthcare Solutions, L. T. Elevators, Macpower CNC Machines, Venus Remedies).

## Cohort: 2026-W37 (standard)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 22 days live. Invested Rs 82,850.92 / cash Rs 17,149.08.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,646.70 | 6 | 9,880.20 | 1,971.40 | 2026-09-24* | +0.00% | +19.72% | +1.95 |
| Yash Highvoltage | 9 | 950.65 | 9 | 8,555.85 | 1,056.40 | 2026-09-24* | -5.93% | +11.12% | +0.95 |
| Macpower CNC Machines | 8 | 1,904.90 | 4 | 7,619.60 | 2,061.10 | 2026-09-24* | +0.00% | +8.20% | +0.62 |
| Asahi Songwon Colors | 10 | 372.65 | 26 | 9,688.90 | 388.00 | 2026-09-24* | +1.33% | +4.12% | +0.40 |
| Dynamic Cables | 12 | 146.30 | 82 | 11,996.60 | 149.00 | 2026-09-24* | +0.91% | +1.85% | +0.22 |
| GPT Healthcare | 9 | 158.17 | 56 | 8,857.52 | 161.73 | 2026-09-24* | -0.00% | +2.25% | +0.20 |
| Bansal Roofing Products | 4 | 157.05 | 25 | 3,926.25 | 160.00 | 2026-09-24* | +1.04% | +1.88% | +0.07 |
| Haldyn Glass | 6 | 146.40 | 40 | 5,856.00 | 145.30 | 2026-09-24* | -1.26% | -0.75% | -0.04 |
| Thyrocare Technologies | 5 | 576.15 | 8 | 4,609.20 | 566.75 | 2026-09-24* | +0.00% | -1.63% | -0.08 |
| Venus Remedies | 12 | 1,694.40 | 7 | 11,860.80 | 1,624.80 | 2026-09-24* | +0.00% | -4.11% | -0.49 |
| **Cash** | | | | 17,149.08 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.37% | **+3.81%** | +3.81 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, Thyrocare Technologies, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W37 (concentrated)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 22 days live. Invested Rs 91,727.25 / cash Rs 8,272.75.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Yash Highvoltage | 17 | 950.65 | 17 | 16,161.05 | 1,056.40 | 2026-09-24* | -5.93% | +11.12% | +1.80 |
| Macpower CNC Machines | 20 | 1,904.90 | 10 | 19,049.00 | 2,061.10 | 2026-09-24* | +0.00% | +8.20% | +1.56 |
| Dynamic Cables | 20 | 146.30 | 136 | 19,896.80 | 149.00 | 2026-09-24* | +0.91% | +1.85% | +0.37 |
| Aeroflex Industries | 13 | 537.45 | 24 | 12,898.80 | 525.70 | 2026-09-25* | -0.28% | -2.19% | -0.28 |
| Venus Remedies | 25 | 1,694.40 | 14 | 23,721.60 | 1,624.80 | 2026-09-24* | +0.00% | -4.11% | -0.97 |
| **Cash** | | | | 8,272.75 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.95% | **+2.47%** | +2.47 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Aeroflex Industries, Dynamic Cables, Macpower CNC Machines, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W39 (standard)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 8 days live. Invested Rs 81,052.54 / cash Rs 18,947.46.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Dynamic Cables | 12 | 142.60 | 84 | 11,978.40 | 149.00 | 2026-09-24* | +0.91% | +4.49% | +0.54 |
| Asahi Songwon Colors | 10 | 372.80 | 26 | 9,692.80 | 388.00 | 2026-09-24* | +1.33% | +4.08% | +0.40 |
| Venus Remedies | 12 | 1,582.20 | 7 | 11,075.40 | 1,624.80 | 2026-09-24* | +0.00% | +2.69% | +0.30 |
| Haldyn Glass | 6 | 141.80 | 42 | 5,955.60 | 145.30 | 2026-09-24* | -1.26% | +2.47% | +0.15 |
| Thyrocare Technologies | 5 | 555.80 | 8 | 4,446.40 | 566.75 | 2026-09-24* | +0.00% | +1.97% | +0.09 |
| Bansal Roofing Products | 4 | 156.30 | 25 | 3,907.50 | 160.00 | 2026-09-24* | +1.04% | +2.37% | +0.09 |
| Yash Highvoltage | 9 | 1,059.20 | 8 | 8,473.60 | 1,056.40 | 2026-09-24* | -5.93% | -0.26% | -0.02 |
| Macpower CNC Machines | 8 | 2,104.50 | 3 | 6,313.50 | 2,061.10 | 2026-09-24* | +0.00% | -2.06% | -0.13 |
| GPT Healthcare | 9 | 166.21 | 54 | 8,975.34 | 161.73 | 2026-09-24* | -0.00% | -2.70% | -0.24 |
| Novartis India | 11 | 2,046.80 | 5 | 10,234.00 | 1,971.40 | 2026-09-24* | +0.00% | -3.68% | -0.38 |
| **Cash** | | | | 18,947.46 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.32% | **+0.79%** | +0.79 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, Thyrocare Technologies, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W39 (concentrated)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 8 days live. Invested Rs 93,431.00 / cash Rs 6,569.00.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Dynamic Cables | 20 | 142.60 | 140 | 19,964.00 | 149.00 | 2026-09-24* | +0.91% | +4.49% | +0.90 |
| Venus Remedies | 25 | 1,582.20 | 15 | 23,733.00 | 1,624.80 | 2026-09-24* | +0.00% | +2.69% | +0.64 |
| Aeroflex Industries | 20 | 510.90 | 39 | 19,925.10 | 525.70 | 2026-09-25* | -0.28% | +2.90% | +0.58 |
| Bansal Roofing Products | 13 | 156.30 | 83 | 12,972.90 | 160.00 | 2026-09-24* | +1.04% | +2.37% | +0.31 |
| Macpower CNC Machines | 17 | 2,104.50 | 8 | 16,836.00 | 2,061.10 | 2026-09-24* | +0.00% | -2.06% | -0.35 |
| **Cash** | | | | 6,569.00 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.26% | **+2.07%** | +2.07 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Aeroflex Industries, Bansal Roofing Products, Dynamic Cables, Macpower CNC Machines, Venus Remedies).

---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
