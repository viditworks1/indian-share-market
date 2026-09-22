# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only). Two sibling books are tracked separately and folded into the same dashboard: the continuously-rebalanced `live-recommendation/` tracker (own `TRACKER.md`) and the weekly frozen `swing-6m/cohorts.json` series (own `TRACKER.md`) — see those files, not this one, for their detail.

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-09-22 (generated 2026-09-22 09:37). Daily history: 15 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 32 | 109,426.95 | +1.20% | **+9.43%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 25 | 106,982.63 | +1.04% | **+6.98%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 25 | 99,302.40 | +0.09% | **-0.70%** |
| 2026-W37 | standard | 2026-09-07 | 2026-09-04 | 18 | 104,319.82 | +1.12% | **+4.32%** |
| 2026-W37 | concentrated | 2026-09-07 | 2026-09-04 | 18 | 102,056.80 | +1.33% | **+2.06%** |
| 2026-W39 | standard | 2026-09-21 | 2026-09-18 | 4 | 101,192.27 | +1.06% | **+1.19%** |
| 2026-W39 | concentrated | 2026-09-21 | 2026-09-18 | 4 | 99,772.60 | +0.73% | **-0.23%** |

*Concentrated series: 3 cohort(s), average return **+0.38%**.*
*Standard series: 4 cohort(s), average return **+5.48%**.*

**Age-matched:** ~0wk old: standard +1.19% vs concentrated -0.23%; ~2wk old: standard +4.32% vs concentrated +2.06%; ~3wk old: standard +6.98% vs concentrated -0.70%.

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | Conv-only rank | Δ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 ★ | Venus Remedies | **79.9** | 77 | 91 | 70 | 90 | 90/90 | +13.7% | +24.7% | 1 | 0 |
| 2 ★ | Dynamic Cables | **75.6** | 68 | 60 | 65 | 90 | 100/100 | +1.7% | +1.1% | 5 | ▲3 |
| 3 ★ | Aeroflex Industries | **57.7** | 52 | 85 | 0 | 90 | 68/82 | +25.7% | +32.9% | 2 | ▼1 |
| 4 ★ | Macpower CNC Machines | **56.2** | 65 | 81 | 30 | 90 | 5/67 | +49.8% | +48.2% | 3 | ▼1 |
| 5 ★ | Bansal Roofing Products | **56.1** | 46 | 53 | 6 | 88 | 77/97 | +20.9% | +18.1% | 6 | ▲1 |
| 6 | Yash Highvoltage | **53.7** | 50 | 49 | 37 | 70 | 54/77 | +33.5% | +37.9% | 7 | ▲1 |
| 7 | Entero Healthcare Solutions | **46.4** | 37 | 61 | 33 | 90 | 63/89 | +28.4% | +26.0% | 4 | ▼3 |
| 8 | GPT Healthcare | **36.3** | 16 | 3 | 45 | 88 | 95/100 | +10.7% | +10.3% | 11 | ▲3 |
| 9 | L. T. Elevators | **36.2** | 35 | 36 | 24 | 70 | 58/15 | +31.3% | — | 8 | ▼1 |
| 10 | Haldyn Glass | **24.5** | 4 | 3 | 45 | 88 | 80/94 | +18.8% | +20.8% | 12 | ▲2 |
| 11 | Asahi Songwon Colors | **23.3** | 3 | 3 | 45 | 88 | 74/100 | +22.7% | +19.0% | 10 | ▼1 |
| 12 | Novartis India | **14.8** | 10 | 20 | 45 | 88 | 8/62 | +48.2% | +53.4% | 9 | ▼3 |

★ = would be in next Monday's concentrated cohort at 25/20/20/17/13% by rank.

---

## Cohort: 2026-W35-inaugural (standard)

Decided 2026-08-25, entry-priced off 2026-08-21 close. 32 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 2,029.50 | 2026-09-22 | +1.27% | +43.03% | +4.27 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 1,150.25 | 2026-09-22 | +3.90% | +26.10% | +2.14 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 157.05 | 2026-09-22 | +1.29% | +15.01% | +0.88 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 166.34 | 2026-09-22 | +0.62% | +10.42% | +0.83 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 146.50 | 2026-09-22 | +2.34% | +10.78% | +0.64 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 1,991.70 | 2026-09-22 | +1.86% | +6.24% | +0.58 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 384.00 | 2026-09-22 | +0.59% | +4.35% | +0.43 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 92.80 | 2026-09-22 | +1.89% | +5.88% | +0.29 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 142.60 | 2026-09-18* | +0.00% | +0.99% | +0.12 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,609.40 | 2026-09-22 | +1.02% | -7.40% | -0.77 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.20% | **+9.43%** | +9.43 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 25 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 2,029.50 | 2026-09-22 | +1.27% | +36.55% | +3.80 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 1,150.25 | 2026-09-22 | +3.90% | +16.65% | +1.48 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 166.34 | 2026-09-22 | +0.62% | +9.64% | +0.86 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 384.00 | 2026-09-22 | +0.59% | +4.72% | +0.47 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 146.50 | 2026-09-22 | +2.34% | +5.51% | +0.33 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 142.60 | 2026-09-18* | +0.00% | +3.33% | +0.20 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 157.05 | 2026-09-22 | +1.29% | +0.35% | +0.01 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 1,991.70 | 2026-09-22 | +1.86% | -0.77% | -0.05 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,609.40 | 2026-09-22 | +1.02% | -1.06% | -0.12 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.04% | **+6.98%** | +6.98 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 25 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 341.00 | 2026-09-18* | -1.96% | +3.93% | +0.77 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 1,991.70 | 2026-09-22 | +1.86% | -0.77% | -0.12 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,786.50 | 2026-09-22 | -0.50% | -1.22% | -0.15 |
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,609.40 | 2026-09-22 | +1.02% | -1.06% | -0.26 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 516.15 | 2026-09-22 | +0.13% | -4.79% | -0.93 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.09% | **-0.70%** | -0.70 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (L. T. Elevators).

## Cohort: 2026-W37 (standard)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 18 days live. Invested Rs 82,850.92 / cash Rs 17,149.08.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,646.70 | 6 | 9,880.20 | 2,029.50 | 2026-09-22 | +1.27% | +23.25% | +2.30 |
| Yash Highvoltage | 9 | 950.65 | 9 | 8,555.85 | 1,150.25 | 2026-09-22 | +3.90% | +21.00% | +1.80 |
| GPT Healthcare | 9 | 158.17 | 56 | 8,857.52 | 166.34 | 2026-09-22 | +0.62% | +5.17% | +0.46 |
| Macpower CNC Machines | 8 | 1,904.90 | 4 | 7,619.60 | 1,991.70 | 2026-09-22 | +1.86% | +4.56% | +0.35 |
| Asahi Songwon Colors | 10 | 372.65 | 26 | 9,688.90 | 384.00 | 2026-09-22 | +0.59% | +3.05% | +0.30 |
| Thyrocare Technologies | 5 | 576.15 | 8 | 4,609.20 | 578.80 | 2026-09-22 | +1.29% | +0.46% | +0.02 |
| Haldyn Glass | 6 | 146.40 | 40 | 5,856.00 | 146.50 | 2026-09-22 | +2.34% | +0.07% | +0.00 |
| Bansal Roofing Products | 4 | 157.05 | 25 | 3,926.25 | 157.05 | 2026-09-22 | +1.29% | +0.00% | +0.00 |
| Dynamic Cables | 12 | 146.30 | 82 | 11,996.60 | 142.60 | 2026-09-18* | +0.00% | -2.53% | -0.30 |
| Venus Remedies | 12 | 1,694.40 | 7 | 11,860.80 | 1,609.40 | 2026-09-22 | +1.02% | -5.02% | -0.59 |
| **Cash** | | | | 17,149.08 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.12% | **+4.32%** | +4.32 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

## Cohort: 2026-W37 (concentrated)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 18 days live. Invested Rs 91,727.25 / cash Rs 8,272.75.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Yash Highvoltage | 17 | 950.65 | 17 | 16,161.05 | 1,150.25 | 2026-09-22 | +3.90% | +21.00% | +3.39 |
| Macpower CNC Machines | 20 | 1,904.90 | 10 | 19,049.00 | 1,991.70 | 2026-09-22 | +1.86% | +4.56% | +0.87 |
| Dynamic Cables | 20 | 146.30 | 136 | 19,896.80 | 142.60 | 2026-09-18* | +0.00% | -2.53% | -0.50 |
| Aeroflex Industries | 13 | 537.45 | 24 | 12,898.80 | 516.15 | 2026-09-22 | +0.13% | -3.96% | -0.51 |
| Venus Remedies | 25 | 1,694.40 | 14 | 23,721.60 | 1,609.40 | 2026-09-22 | +1.02% | -5.02% | -1.19 |
| **Cash** | | | | 8,272.75 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.33% | **+2.06%** | +2.06 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

## Cohort: 2026-W39 (standard)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 4 days live. Invested Rs 81,052.54 / cash Rs 18,947.46.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Yash Highvoltage | 9 | 1,059.20 | 8 | 8,473.60 | 1,150.25 | 2026-09-22 | +3.90% | +8.60% | +0.73 |
| Asahi Songwon Colors | 10 | 372.80 | 26 | 9,692.80 | 384.00 | 2026-09-22 | +0.59% | +3.00% | +0.29 |
| Haldyn Glass | 6 | 141.80 | 42 | 5,955.60 | 146.50 | 2026-09-22 | +2.34% | +3.31% | +0.20 |
| Venus Remedies | 12 | 1,582.20 | 7 | 11,075.40 | 1,609.40 | 2026-09-22 | +1.02% | +1.72% | +0.19 |
| Thyrocare Technologies | 5 | 555.80 | 8 | 4,446.40 | 578.80 | 2026-09-22 | +1.29% | +4.14% | +0.18 |
| Bansal Roofing Products | 4 | 156.30 | 25 | 3,907.50 | 157.05 | 2026-09-22 | +1.29% | +0.48% | +0.02 |
| GPT Healthcare | 9 | 166.21 | 54 | 8,975.34 | 166.34 | 2026-09-22 | +0.62% | +0.08% | +0.01 |
| Dynamic Cables | 12 | 142.60 | 84 | 11,978.40 | 142.60 | 2026-09-18* | +0.00% | +0.00% | +0.00 |
| Novartis India | 11 | 2,046.80 | 5 | 10,234.00 | 2,029.50 | 2026-09-22 | +1.27% | -0.85% | -0.09 |
| Macpower CNC Machines | 8 | 2,104.50 | 3 | 6,313.50 | 1,991.70 | 2026-09-22 | +1.86% | -5.36% | -0.34 |
| **Cash** | | | | 18,947.46 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.06% | **+1.19%** | +1.19 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

## Cohort: 2026-W39 (concentrated)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 4 days live. Invested Rs 93,431.00 / cash Rs 6,569.00.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,582.20 | 15 | 23,733.00 | 1,609.40 | 2026-09-22 | +1.02% | +1.72% | +0.41 |
| Aeroflex Industries | 20 | 510.90 | 39 | 19,925.10 | 516.15 | 2026-09-22 | +0.13% | +1.03% | +0.20 |
| Bansal Roofing Products | 13 | 156.30 | 83 | 12,972.90 | 157.05 | 2026-09-22 | +1.29% | +0.48% | +0.06 |
| Dynamic Cables | 20 | 142.60 | 140 | 19,964.00 | 142.60 | 2026-09-18* | +0.00% | +0.00% | +0.00 |
| Macpower CNC Machines | 17 | 2,104.50 | 8 | 16,836.00 | 1,991.70 | 2026-09-22 | +1.86% | -5.36% | -0.90 |
| **Cash** | | | | 6,569.00 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.73% | **-0.23%** | -0.23 |

\* price carried forward — data source has not yet posted a 2026-09-22 close (Dynamic Cables).

---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
