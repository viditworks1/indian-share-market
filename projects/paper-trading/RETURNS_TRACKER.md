# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only). Two sibling books are tracked separately and folded into the same dashboard: the continuously-rebalanced `live-recommendation/` tracker (own `TRACKER.md`) and the weekly frozen `swing-6m/cohorts.json` series (own `TRACKER.md`) — see those files, not this one, for their detail.

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-09-22 (generated 2026-09-22 21:29). Daily history: 15 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 32 | 108,550.71 | +0.39% | **+8.55%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 25 | 105,863.68 | -0.01% | **+5.86%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 25 | 100,759.20 | +1.56% | **+0.76%** |
| 2026-W37 | standard | 2026-09-07 | 2026-09-04 | 18 | 103,272.77 | +0.11% | **+3.27%** |
| 2026-W37 | concentrated | 2026-09-07 | 2026-09-04 | 18 | 102,314.40 | +1.59% | **+2.31%** |
| 2026-W39 | standard | 2026-09-21 | 2026-09-18 | 4 | 100,120.02 | -0.01% | **+0.12%** |
| 2026-W39 | concentrated | 2026-09-21 | 2026-09-18 | 4 | 100,143.30 | +1.11% | **+0.14%** |

*Concentrated series: 3 cohort(s), average return **+1.07%**.*
*Standard series: 4 cohort(s), average return **+4.45%**.*

**Age-matched:** ~0wk old: standard +0.12% vs concentrated +0.14%; ~2wk old: standard +3.27% vs concentrated +2.31%; ~3wk old: standard +5.86% vs concentrated +0.76%.

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | Conv-only rank | Δ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 ★ | Venus Remedies | **80.0** | 77 | 91 | 70 | 90 | 90/90 | +13.5% | +24.7% | 1 | 0 |
| 2 ★ | Macpower CNC Machines | **63.0** | 65 | 81 | 30 | 90 | 50/67 | +35.7% | +48.2% | 3 | ▲1 |
| 3 ★ | Aeroflex Industries | **58.0** | 52 | 85 | 0 | 90 | 70/82 | +24.6% | +32.9% | 2 | ▼1 |
| 4 ★ | Bansal Roofing Products | **56.8** | 46 | 53 | 6 | 88 | 81/97 | +18.5% | +18.1% | 5 | ▲1 |
| 5 ★ | Yash Highvoltage | **53.0** | 50 | 49 | 37 | 70 | 50/77 | +36.1% | +37.9% | 6 | ▲1 |
| 6 | Entero Healthcare Solutions | **45.9** | 37 | 61 | 33 | 90 | 60/89 | +30.3% | +26.0% | 4 | ▼2 |
| 7 | GPT Healthcare | **36.6** | 16 | 3 | 45 | 88 | 98/100 | +9.4% | +10.3% | 10 | ▲3 |
| 8 | L. T. Elevators | **36.3** | 35 | 36 | 24 | 70 | 58/15 | +31.1% | — | 7 | ▼1 |
| 9 | Haldyn Glass | **24.6** | 4 | 3 | 45 | 88 | 81/94 | +18.4% | +20.8% | 11 | ▲2 |
| 10 | Asahi Songwon Colors | **23.0** | 3 | 3 | 45 | 88 | 72/100 | +23.6% | +19.0% | 9 | ▼1 |
| 11 | Novartis India | **19.8** | 10 | 20 | 45 | 88 | 41/62 | +41.0% | +53.4% | 8 | ▼3 |

*Out of pool:* Dynamic Cables (below 30W EMA -0.3%)

★ = would be in next Monday's concentrated cohort at 25/20/20/17/13% by rank.

---

## Cohort: 2026-W35-inaugural (standard)

Decided 2026-08-25, entry-priced off 2026-08-21 close. 32 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 1,973.30 | 2026-09-22 | -1.54% | +39.07% | +3.88 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 1,123.65 | 2026-09-22 | +1.50% | +23.18% | +1.90 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 2,096.50 | 2026-09-22 | +7.22% | +11.83% | +1.11 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 155.50 | 2026-09-22 | +0.29% | +13.88% | +0.81 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 162.79 | 2026-09-22 | -1.53% | +8.07% | +0.64 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 144.15 | 2026-09-22 | +0.70% | +9.00% | +0.54 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 95.63 | 2026-09-22 | +5.00% | +9.10% | +0.45 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 371.20 | 2026-09-22 | -2.76% | +0.87% | +0.09 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 139.80 | 2026-09-21* | -1.96% | -0.99% | -0.12 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,611.50 | 2026-09-22 | +1.15% | -7.28% | -0.76 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.39% | **+8.55%** | +8.55 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 25 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 1,973.30 | 2026-09-22 | -1.54% | +32.77% | +3.41 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 1,123.65 | 2026-09-22 | +1.50% | +13.95% | +1.24 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 162.79 | 2026-09-22 | -1.53% | +7.30% | +0.65 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 2,096.50 | 2026-09-22 | +7.22% | +4.45% | +0.27 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 144.15 | 2026-09-22 | +0.70% | +3.82% | +0.23 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 371.20 | 2026-09-22 | -2.76% | +1.23% | +0.12 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 139.80 | 2026-09-21* | -1.96% | +1.30% | +0.08 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 155.50 | 2026-09-22 | +0.29% | -0.64% | -0.03 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,611.50 | 2026-09-22 | +1.15% | -0.93% | -0.11 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.01% | **+5.86%** | +5.86 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 25 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 344.00 | 2026-09-22 | -1.09% | +4.85% | +0.95 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 2,096.50 | 2026-09-22 | +7.22% | +4.45% | +0.72 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,841.80 | 2026-09-22 | +2.58% | +1.84% | +0.23 |
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,611.50 | 2026-09-22 | +1.15% | -0.93% | -0.23 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 516.70 | 2026-09-22 | +0.23% | -4.69% | -0.91 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.56% | **+0.76%** | +0.76 |


## Cohort: 2026-W37 (standard)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 18 days live. Invested Rs 82,850.92 / cash Rs 17,149.08.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,646.70 | 6 | 9,880.20 | 1,973.30 | 2026-09-22 | -1.54% | +19.83% | +1.96 |
| Yash Highvoltage | 9 | 950.65 | 9 | 8,555.85 | 1,123.65 | 2026-09-22 | +1.50% | +18.20% | +1.56 |
| Macpower CNC Machines | 8 | 1,904.90 | 4 | 7,619.60 | 2,096.50 | 2026-09-22 | +7.22% | +10.06% | +0.77 |
| GPT Healthcare | 9 | 158.17 | 56 | 8,857.52 | 162.79 | 2026-09-22 | -1.53% | +2.92% | +0.26 |
| Thyrocare Technologies | 5 | 576.15 | 8 | 4,609.20 | 577.50 | 2026-09-22 | +1.06% | +0.23% | +0.01 |
| Asahi Songwon Colors | 10 | 372.65 | 26 | 9,688.90 | 371.20 | 2026-09-22 | -2.76% | -0.39% | -0.04 |
| Bansal Roofing Products | 4 | 157.05 | 25 | 3,926.25 | 155.50 | 2026-09-22 | +0.29% | -0.99% | -0.04 |
| Haldyn Glass | 6 | 146.40 | 40 | 5,856.00 | 144.15 | 2026-09-22 | +0.70% | -1.54% | -0.09 |
| Dynamic Cables | 12 | 146.30 | 82 | 11,996.60 | 139.80 | 2026-09-21* | -1.96% | -4.44% | -0.53 |
| Venus Remedies | 12 | 1,694.40 | 7 | 11,860.80 | 1,611.50 | 2026-09-22 | +1.15% | -4.89% | -0.58 |
| **Cash** | | | | 17,149.08 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.11% | **+3.27%** | +3.27 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

## Cohort: 2026-W37 (concentrated)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 18 days live. Invested Rs 91,727.25 / cash Rs 8,272.75.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Yash Highvoltage | 17 | 950.65 | 17 | 16,161.05 | 1,123.65 | 2026-09-22 | +1.50% | +18.20% | +2.94 |
| Macpower CNC Machines | 20 | 1,904.90 | 10 | 19,049.00 | 2,096.50 | 2026-09-22 | +7.22% | +10.06% | +1.92 |
| Aeroflex Industries | 13 | 537.45 | 24 | 12,898.80 | 516.70 | 2026-09-22 | +0.23% | -3.86% | -0.50 |
| Dynamic Cables | 20 | 146.30 | 136 | 19,896.80 | 139.80 | 2026-09-21* | -1.96% | -4.44% | -0.88 |
| Venus Remedies | 25 | 1,694.40 | 14 | 23,721.60 | 1,611.50 | 2026-09-22 | +1.15% | -4.89% | -1.16 |
| **Cash** | | | | 8,272.75 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.59% | **+2.31%** | +2.31 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

## Cohort: 2026-W39 (standard)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 4 days live. Invested Rs 81,052.54 / cash Rs 18,947.46.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Yash Highvoltage | 9 | 1,059.20 | 8 | 8,473.60 | 1,123.65 | 2026-09-22 | +1.50% | +6.08% | +0.52 |
| Venus Remedies | 12 | 1,582.20 | 7 | 11,075.40 | 1,611.50 | 2026-09-22 | +1.15% | +1.85% | +0.21 |
| Thyrocare Technologies | 5 | 555.80 | 8 | 4,446.40 | 577.50 | 2026-09-22 | +1.06% | +3.90% | +0.17 |
| Haldyn Glass | 6 | 141.80 | 42 | 5,955.60 | 144.15 | 2026-09-22 | +0.70% | +1.66% | +0.10 |
| Macpower CNC Machines | 8 | 2,104.50 | 3 | 6,313.50 | 2,096.50 | 2026-09-22 | +7.22% | -0.38% | -0.02 |
| Bansal Roofing Products | 4 | 156.30 | 25 | 3,907.50 | 155.50 | 2026-09-22 | +0.29% | -0.51% | -0.02 |
| Asahi Songwon Colors | 10 | 372.80 | 26 | 9,692.80 | 371.20 | 2026-09-22 | -2.76% | -0.43% | -0.04 |
| GPT Healthcare | 9 | 166.21 | 54 | 8,975.34 | 162.79 | 2026-09-22 | -1.53% | -2.06% | -0.18 |
| Dynamic Cables | 12 | 142.60 | 84 | 11,978.40 | 139.80 | 2026-09-21* | -1.96% | -1.96% | -0.24 |
| Novartis India | 11 | 2,046.80 | 5 | 10,234.00 | 1,973.30 | 2026-09-22 | -1.54% | -3.59% | -0.37 |
| **Cash** | | | | 18,947.46 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.01% | **+0.12%** | +0.12 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

## Cohort: 2026-W39 (concentrated)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 4 days live. Invested Rs 93,431.00 / cash Rs 6,569.00.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,582.20 | 15 | 23,733.00 | 1,611.50 | 2026-09-22 | +1.15% | +1.85% | +0.44 |
| Aeroflex Industries | 20 | 510.90 | 39 | 19,925.10 | 516.70 | 2026-09-22 | +0.23% | +1.14% | +0.23 |
| Macpower CNC Machines | 17 | 2,104.50 | 8 | 16,836.00 | 2,096.50 | 2026-09-22 | +7.22% | -0.38% | -0.06 |
| Bansal Roofing Products | 13 | 156.30 | 83 | 12,972.90 | 155.50 | 2026-09-22 | +0.29% | -0.51% | -0.07 |
| Dynamic Cables | 20 | 142.60 | 140 | 19,964.00 | 139.80 | 2026-09-21* | -1.96% | -1.96% | -0.39 |
| **Cash** | | | | 6,569.00 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.11% | **+0.14%** | +0.14 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
