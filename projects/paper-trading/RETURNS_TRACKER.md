# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only). Two sibling books are tracked separately and folded into the same dashboard: the continuously-rebalanced `live-recommendation/` tracker (own `TRACKER.md`) and the weekly frozen `swing-6m/cohorts.json` series (own `TRACKER.md`) — see those files, not this one, for their detail.

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-09-26 (generated 2026-09-26 16:24). Daily history: 18 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 36 | 110,346.03 | +0.42% | **+10.35%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 29 | 106,936.95 | +0.30% | **+6.94%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 29 | 100,996.70 | -0.42% | **+1.00%** |
| 2026-W37 | standard | 2026-09-07 | 2026-09-04 | 22 | 104,205.90 | +0.01% | **+4.21%** |
| 2026-W37 | concentrated | 2026-09-07 | 2026-09-04 | 22 | 102,374.15 | -1.04% | **+2.37%** |
| 2026-W39 | standard | 2026-09-21 | 2026-09-18 | 8 | 101,140.44 | +0.03% | **+1.14%** |
| 2026-W39 | concentrated | 2026-09-21 | 2026-09-18 | 8 | 102,059.60 | +0.25% | **+2.06%** |

*Concentrated series: 3 cohort(s), average return **+1.81%**.*
*Standard series: 4 cohort(s), average return **+5.66%**.*

**Age-matched:** ~1wk old: standard +1.14% vs concentrated +2.06%; ~3wk old: standard +4.21% vs concentrated +2.37%; ~4wk old: standard +6.94% vs concentrated +1.00%.

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | Conv-only rank | Δ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 ★ | Venus Remedies | **78.4** | 77 | 91 | 70 | 90 | 81/88 | +18.4% | +27.3% | 1 | 0 |
| 2 ★ | Macpower CNC Machines | **61.4** | 65 | 81 | 30 | 90 | 38/69 | +42.5% | +45.9% | 3 | ▲1 |
| 3 ★ | Aeroflex Industries | **57.1** | 52 | 85 | 0 | 90 | 66/79 | +26.9% | +36.1% | 2 | ▼1 |
| 4 ★ | Bansal Roofing Products | **54.2** | 46 | 53 | 6 | 88 | 66/95 | +26.9% | +20.3% | 5 | ▲1 |
| 5 ★ | Yash Highvoltage | **53.6** | 50 | 49 | 37 | 70 | 54/77 | +33.8% | +37.7% | 6 | ▲1 |
| 6 | Entero Healthcare Solutions | **44.8** | 37 | 61 | 33 | 90 | 57/82 | +32.1% | +32.6% | 4 | ▼2 |
| 7 | L. T. Elevators | **37.5** | 35 | 36 | 24 | 70 | 66/15 | +26.7% | — | 7 | 0 |
| 8 | GPT Healthcare | **37.0** | 16 | 3 | 45 | 88 | 100/100 | +6.9% | +7.9% | 10 | ▲2 |
| 9 | Haldyn Glass | **23.6** | 4 | 3 | 45 | 88 | 76/92 | +21.1% | +23.1% | 11 | ▲2 |
| 10 | Asahi Songwon Colors | **21.3** | 3 | 3 | 45 | 88 | 61/100 | +29.9% | +22.8% | 9 | ▼1 |
| 11 | Novartis India | **20.8** | 10 | 20 | 45 | 88 | 45/66 | +38.5% | +49.3% | 8 | ▼3 |

*Out of pool:* Dynamic Cables (below 30W EMA -0.2%)

★ = would be in next Monday's concentrated cohort at 25/20/20/17/13% by rank.

---

## Cohort: 2026-W35-inaugural (standard)

Decided 2026-08-25, entry-priced off 2026-08-21 close. 36 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 1,965.60 | 2026-09-25* | -0.29% | +38.53% | +3.83 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 1,086.40 | 2026-09-25* | -3.25% | +19.10% | +1.57 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 167.10 | 2026-09-25* | +5.53% | +22.37% | +1.31 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 106.47 | 2026-09-25* | +6.04% | +21.47% | +1.07 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 2,062.50 | 2026-09-25* | +0.07% | +10.01% | +0.94 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 402.75 | 2026-09-25* | +5.18% | +9.44% | +0.94 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 146.65 | 2026-09-25* | -0.34% | +10.89% | +0.65 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 161.27 | 2026-09-25* | -0.28% | +7.06% | +0.56 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 139.95 | 2026-09-25* | -5.22% | -0.89% | -0.11 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,668.40 | 2026-09-25* | +2.68% | -4.01% | -0.42 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.42% | **+10.35%** | +10.35 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, RNIT AI Solutions, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 29 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 1,965.60 | 2026-09-25* | -0.29% | +32.25% | +3.36 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 402.75 | 2026-09-25* | +5.18% | +9.83% | +0.97 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 1,086.40 | 2026-09-25* | -3.25% | +10.17% | +0.90 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 161.27 | 2026-09-25* | -0.28% | +6.29% | +0.56 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 146.65 | 2026-09-25* | -0.34% | +5.62% | +0.34 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,668.40 | 2026-09-25* | +2.68% | +2.56% | +0.29 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 167.10 | 2026-09-25* | +5.53% | +6.77% | +0.27 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 2,062.50 | 2026-09-25* | +0.07% | +2.76% | +0.17 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 139.95 | 2026-09-25* | -5.22% | +1.41% | +0.08 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.30% | **+6.94%** | +6.94 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 29 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,668.40 | 2026-09-25* | +2.68% | +2.56% | +0.63 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 2,062.50 | 2026-09-25* | +0.07% | +2.76% | +0.44 |
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 335.20 | 2026-09-25* | -3.94% | +2.16% | +0.43 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,821.80 | 2026-09-25* | -1.64% | +0.73% | +0.09 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 525.70 | 2026-09-25* | -0.28% | -3.03% | -0.59 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -0.42% | **+1.00%** | +1.00 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Aeroflex Industries, Entero Healthcare Solutions, L. T. Elevators, Macpower CNC Machines, Venus Remedies).

## Cohort: 2026-W37 (standard)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 22 days live. Invested Rs 82,850.92 / cash Rs 17,149.08.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,646.70 | 6 | 9,880.20 | 1,965.60 | 2026-09-25* | -0.29% | +19.37% | +1.91 |
| Yash Highvoltage | 9 | 950.65 | 9 | 8,555.85 | 1,086.40 | 2026-09-25* | -3.25% | +14.28% | +1.22 |
| Asahi Songwon Colors | 10 | 372.65 | 26 | 9,688.90 | 402.75 | 2026-09-25* | +5.18% | +8.08% | +0.78 |
| Macpower CNC Machines | 8 | 1,904.90 | 4 | 7,619.60 | 2,062.50 | 2026-09-25* | +0.07% | +8.27% | +0.63 |
| Bansal Roofing Products | 4 | 157.05 | 25 | 3,926.25 | 167.10 | 2026-09-25* | +5.53% | +6.40% | +0.25 |
| GPT Healthcare | 9 | 158.17 | 56 | 8,857.52 | 161.27 | 2026-09-25* | -0.28% | +1.96% | +0.17 |
| Haldyn Glass | 6 | 146.40 | 40 | 5,856.00 | 146.65 | 2026-09-25* | -0.34% | +0.17% | +0.01 |
| Thyrocare Technologies | 5 | 576.15 | 8 | 4,609.20 | 566.85 | 2026-09-25* | +0.02% | -1.61% | -0.07 |
| Venus Remedies | 12 | 1,694.40 | 7 | 11,860.80 | 1,668.40 | 2026-09-25* | +2.68% | -1.53% | -0.18 |
| Dynamic Cables | 12 | 146.30 | 82 | 11,996.60 | 139.95 | 2026-09-25* | -5.22% | -4.34% | -0.52 |
| **Cash** | | | | 17,149.08 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.01% | **+4.21%** | +4.21 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, Thyrocare Technologies, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W37 (concentrated)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 22 days live. Invested Rs 91,727.25 / cash Rs 8,272.75.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Yash Highvoltage | 17 | 950.65 | 17 | 16,161.05 | 1,086.40 | 2026-09-25* | -3.25% | +14.28% | +2.31 |
| Macpower CNC Machines | 20 | 1,904.90 | 10 | 19,049.00 | 2,062.50 | 2026-09-25* | +0.07% | +8.27% | +1.58 |
| Aeroflex Industries | 13 | 537.45 | 24 | 12,898.80 | 525.70 | 2026-09-25* | -0.28% | -2.19% | -0.28 |
| Venus Remedies | 25 | 1,694.40 | 14 | 23,721.60 | 1,668.40 | 2026-09-25* | +2.68% | -1.53% | -0.36 |
| Dynamic Cables | 20 | 146.30 | 136 | 19,896.80 | 139.95 | 2026-09-25* | -5.22% | -4.34% | -0.86 |
| **Cash** | | | | 8,272.75 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -1.04% | **+2.37%** | +2.37 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Aeroflex Industries, Dynamic Cables, Macpower CNC Machines, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W39 (standard)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 8 days live. Invested Rs 81,052.54 / cash Rs 18,947.46.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Asahi Songwon Colors | 10 | 372.80 | 26 | 9,692.80 | 402.75 | 2026-09-25* | +5.18% | +8.03% | +0.78 |
| Venus Remedies | 12 | 1,582.20 | 7 | 11,075.40 | 1,668.40 | 2026-09-25* | +2.68% | +5.45% | +0.60 |
| Bansal Roofing Products | 4 | 156.30 | 25 | 3,907.50 | 167.10 | 2026-09-25* | +5.53% | +6.91% | +0.27 |
| Yash Highvoltage | 9 | 1,059.20 | 8 | 8,473.60 | 1,086.40 | 2026-09-25* | -3.25% | +2.57% | +0.22 |
| Haldyn Glass | 6 | 141.80 | 42 | 5,955.60 | 146.65 | 2026-09-25* | -0.34% | +3.42% | +0.20 |
| Thyrocare Technologies | 5 | 555.80 | 8 | 4,446.40 | 566.85 | 2026-09-25* | +0.02% | +1.99% | +0.09 |
| Macpower CNC Machines | 8 | 2,104.50 | 3 | 6,313.50 | 2,062.50 | 2026-09-25* | +0.07% | -2.00% | -0.13 |
| Dynamic Cables | 12 | 142.60 | 84 | 11,978.40 | 139.95 | 2026-09-25* | -5.22% | -1.86% | -0.22 |
| GPT Healthcare | 9 | 166.21 | 54 | 8,975.34 | 161.27 | 2026-09-25* | -0.28% | -2.97% | -0.27 |
| Novartis India | 11 | 2,046.80 | 5 | 10,234.00 | 1,965.60 | 2026-09-25* | -0.29% | -3.97% | -0.41 |
| **Cash** | | | | 18,947.46 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.03% | **+1.14%** | +1.14 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, Thyrocare Technologies, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W39 (concentrated)

Decided 2026-09-21, entry-priced off 2026-09-18 close. 8 days live. Invested Rs 93,431.00 / cash Rs 6,569.00.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,582.20 | 15 | 23,733.00 | 1,668.40 | 2026-09-25* | +2.68% | +5.45% | +1.29 |
| Bansal Roofing Products | 13 | 156.30 | 83 | 12,972.90 | 167.10 | 2026-09-25* | +5.53% | +6.91% | +0.90 |
| Aeroflex Industries | 20 | 510.90 | 39 | 19,925.10 | 525.70 | 2026-09-25* | -0.28% | +2.90% | +0.58 |
| Macpower CNC Machines | 17 | 2,104.50 | 8 | 16,836.00 | 2,062.50 | 2026-09-25* | +0.07% | -2.00% | -0.34 |
| Dynamic Cables | 20 | 142.60 | 140 | 19,964.00 | 139.95 | 2026-09-25* | -5.22% | -1.86% | -0.37 |
| **Cash** | | | | 6,569.00 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.25% | **+2.06%** | +2.06 |

\* price carried forward — data source has not yet posted a 2026-09-26 close (Aeroflex Industries, Bansal Roofing Products, Dynamic Cables, Macpower CNC Machines, Venus Remedies).

---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
