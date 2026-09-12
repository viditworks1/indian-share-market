# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only). Two sibling books are tracked separately and folded into the same dashboard: the continuously-rebalanced `live-recommendation/` tracker (own `TRACKER.md`) and the weekly frozen `swing-6m/cohorts.json` series (own `TRACKER.md`) — see those files, not this one, for their detail.

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-09-12 (generated 2026-09-12 12:30). Daily history: 11 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 22 | 108,968.51 | +0.49% | **+8.97%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 15 | 106,556.88 | +0.46% | **+6.56%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 15 | 101,927.40 | -0.39% | **+1.93%** |
| 2026-W37 | standard | 2026-09-07 | 2026-09-04 | 8 | 103,253.87 | +0.54% | **+3.25%** |
| 2026-W37 | concentrated | 2026-09-07 | 2026-09-04 | 8 | 98,610.90 | +0.27% | **-1.39%** |

*Concentrated series: 2 cohort(s), average return **+0.27%**.*
*Standard series: 3 cohort(s), average return **+6.26%**.*

**Age-matched:** ~1wk old: standard +3.25% vs concentrated -1.39%; ~2wk old: standard +6.56% vs concentrated +1.93%.

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | Conv-only rank | Δ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 ★ | Venus Remedies | **78.6** | 77 | 91 | 70 | 90 | 82/88 | +17.8% | +27.2% | 1 | 0 |
| 2 ★ | Dynamic Cables | **75.6** | 68 | 60 | 65 | 90 | 100/100 | +1.7% | +1.1% | 5 | ▲3 |
| 3 ★ | Macpower CNC Machines | **64.4** | 65 | 81 | 30 | 90 | 50/81 | +35.8% | +34.2% | 3 | 0 |
| 4 ★ | Yash Highvoltage | **57.5** | 50 | 49 | 37 | 70 | 73/88 | +23.1% | +27.5% | 7 | ▲3 |
| 5 ★ | Bansal Roofing Products | **57.0** | 46 | 53 | 6 | 88 | 81/100 | +18.5% | +15.2% | 6 | ▲1 |
| 6 | Aeroflex Industries | **52.5** | 52 | 85 | 0 | 90 | 40/72 | +41.2% | +43.1% | 2 | ▼4 |
| 7 | Entero Healthcare Solutions | **44.1** | 37 | 61 | 33 | 90 | 50/86 | +35.7% | +29.4% | 4 | ▼3 |
| 8 | GPT Healthcare | **37.0** | 16 | 3 | 45 | 88 | 100/100 | +8.1% | +7.6% | 11 | ▲3 |
| 9 | L. T. Elevators | **29.1** | 35 | 36 | 24 | 70 | 11/15 | +46.4% | — | 8 | ▼1 |
| 10 | Haldyn Glass | **23.9** | 4 | 3 | 45 | 88 | 77/94 | +20.9% | +20.9% | 12 | ▲2 |
| 11 | Asahi Songwon Colors | **22.6** | 3 | 3 | 45 | 88 | 69/100 | +25.3% | +19.7% | 10 | ▼1 |
| 12 | Novartis India | **10.4** | 10 | 20 | 45 | 88 | 0/29 | +79.1% | +71.2% | 9 | ▼3 |

★ = would be in next Monday's concentrated cohort at 25/20/20/17/13% by rank.

---

## Cohort: 2026-W35-inaugural (standard)

Decided 2026-08-25, entry-priced off 2026-08-21 close. 22 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 2,391.30 | 2026-09-11* | +0.00% | +68.53% | +6.81 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 99.08 | 2026-09-10* | -0.85% | +13.04% | +0.65 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 151.40 | 2026-09-10* | +4.45% | +10.88% | +0.64 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 161.29 | 2026-09-10* | +1.20% | +7.07% | +0.56 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 141.95 | 2026-09-10* | -3.80% | +7.33% | +0.44 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 954.95 | 2026-09-10* | +0.99% | +4.69% | +0.38 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 375.65 | 2026-09-10* | +3.21% | +2.08% | +0.21 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 142.65 | 2026-09-10* | -0.00% | +1.03% | +0.12 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 1,843.00 | 2026-09-11* | +0.00% | -1.70% | -0.16 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,624.20 | 2026-09-10* | +0.49% | -6.55% | -0.68 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.49% | **+8.97%** | +8.97 |

\* price carried forward — data source has not yet posted a 2026-09-12 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, RNIT AI Solutions, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 15 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 2,391.30 | 2026-09-11* | +0.00% | +60.89% | +6.34 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 161.29 | 2026-09-10* | +1.20% | +6.31% | +0.56 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 375.65 | 2026-09-10* | +3.21% | +2.44% | +0.24 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 142.65 | 2026-09-10* | -0.00% | +3.37% | +0.20 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 141.95 | 2026-09-10* | -3.80% | +2.23% | +0.13 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,624.20 | 2026-09-10* | +0.49% | -0.15% | -0.02 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 151.40 | 2026-09-10* | +4.45% | -3.26% | -0.13 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 954.95 | 2026-09-10* | +0.99% | -3.16% | -0.28 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 1,843.00 | 2026-09-11* | +0.00% | -8.18% | -0.49 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.46% | **+6.56%** | +6.56 |

\* price carried forward — data source has not yet posted a 2026-09-12 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 15 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 371.45 | 2026-09-10* | -1.60% | +13.21% | +2.60 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 563.95 | 2026-09-11* | +0.00% | +4.03% | +0.79 |
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,624.20 | 2026-09-10* | +0.49% | -0.15% | -0.04 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,792.90 | 2026-09-10* | -1.24% | -0.87% | -0.11 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 1,843.00 | 2026-09-11* | +0.00% | -8.18% | -1.31 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.39% | **+1.93%** | +1.93 |

\* price carried forward — data source has not yet posted a 2026-09-12 close (Aeroflex Industries, Entero Healthcare Solutions, L. T. Elevators, Macpower CNC Machines, Venus Remedies).

## Cohort: 2026-W37 (standard)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 8 days live. Invested Rs 82,850.92 / cash Rs 17,149.08.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,646.70 | 6 | 9,880.20 | 2,391.30 | 2026-09-11* | +0.00% | +45.22% | +4.47 |
| GPT Healthcare | 9 | 158.17 | 56 | 8,857.52 | 161.29 | 2026-09-10* | +1.20% | +1.97% | +0.17 |
| Asahi Songwon Colors | 10 | 372.65 | 26 | 9,688.90 | 375.65 | 2026-09-10* | +3.21% | +0.81% | +0.08 |
| Yash Highvoltage | 9 | 950.65 | 9 | 8,555.85 | 954.95 | 2026-09-10* | +0.99% | +0.45% | +0.04 |
| Bansal Roofing Products | 4 | 157.05 | 25 | 3,926.25 | 151.40 | 2026-09-10* | +4.45% | -3.60% | -0.14 |
| Thyrocare Technologies | 5 | 576.15 | 8 | 4,609.20 | 557.70 | 2026-09-10* | +1.46% | -3.20% | -0.15 |
| Haldyn Glass | 6 | 146.40 | 40 | 5,856.00 | 141.95 | 2026-09-10* | -3.80% | -3.04% | -0.18 |
| Macpower CNC Machines | 8 | 1,904.90 | 4 | 7,619.60 | 1,843.00 | 2026-09-11* | +0.00% | -3.25% | -0.25 |
| Dynamic Cables | 12 | 146.30 | 82 | 11,996.60 | 142.65 | 2026-09-10* | -0.00% | -2.49% | -0.30 |
| Venus Remedies | 12 | 1,694.40 | 7 | 11,860.80 | 1,624.20 | 2026-09-10* | +0.49% | -4.14% | -0.49 |
| **Cash** | | | | 17,149.08 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.54% | **+3.25%** | +3.25 |

\* price carried forward — data source has not yet posted a 2026-09-12 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, Thyrocare Technologies, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W37 (concentrated)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 8 days live. Invested Rs 91,727.25 / cash Rs 8,272.75.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Aeroflex Industries | 13 | 537.45 | 24 | 12,898.80 | 563.95 | 2026-09-11* | +0.00% | +4.93% | +0.64 |
| Yash Highvoltage | 17 | 950.65 | 17 | 16,161.05 | 954.95 | 2026-09-10* | +0.99% | +0.45% | +0.07 |
| Dynamic Cables | 20 | 146.30 | 136 | 19,896.80 | 142.65 | 2026-09-10* | -0.00% | -2.49% | -0.50 |
| Macpower CNC Machines | 20 | 1,904.90 | 10 | 19,049.00 | 1,843.00 | 2026-09-11* | +0.00% | -3.25% | -0.62 |
| Venus Remedies | 25 | 1,694.40 | 14 | 23,721.60 | 1,624.20 | 2026-09-10* | +0.49% | -4.14% | -0.98 |
| **Cash** | | | | 8,272.75 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.27% | **-1.39%** | -1.39 |

\* price carried forward — data source has not yet posted a 2026-09-12 close (Aeroflex Industries, Dynamic Cables, Macpower CNC Machines, Venus Remedies, Yash Highvoltage).

---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
