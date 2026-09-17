# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only). Two sibling books are tracked separately and folded into the same dashboard: the continuously-rebalanced `live-recommendation/` tracker (own `TRACKER.md`) and the weekly frozen `swing-6m/cohorts.json` series (own `TRACKER.md`) — see those files, not this one, for their detail.

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-09-17 (generated 2026-09-17 20:29). Daily history: 12 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 27 | 106,652.22 | +6.65% | **+6.65%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 20 | 104,778.61 | +4.78% | **+4.78%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 20 | 96,556.50 | -3.44% | **-3.44%** |
| 2026-W37 | standard | 2026-09-07 | 2026-09-04 | 13 | 101,515.94 | +1.52% | **+1.52%** |
| 2026-W37 | concentrated | 2026-09-07 | 2026-09-04 | 13 | 97,638.40 | -2.36% | **-2.36%** |

*Concentrated series: 2 cohort(s), average return **-2.90%**.*
*Standard series: 3 cohort(s), average return **+4.32%**.*

**Age-matched:** ~1wk old: standard +1.52% vs concentrated -2.36%; ~2wk old: standard +4.78% vs concentrated -3.44%.

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | Conv-only rank | Δ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 ★ | Venus Remedies | **81.1** | 77 | 91 | 70 | 90 | 95/93 | +10.6% | +21.8% | 1 | 0 |
| 2 ★ | Macpower CNC Machines | **64.1** | 65 | 81 | 30 | 90 | 50/78 | +35.8% | +36.8% | 3 | ▲1 |
| 3 ★ | Aeroflex Industries | **60.2** | 52 | 85 | 0 | 90 | 80/88 | +18.9% | +26.9% | 2 | ▼1 |
| 4 ★ | Bansal Roofing Products | **57.2** | 46 | 53 | 6 | 88 | 82/100 | +17.7% | +15.4% | 5 | ▲1 |
| 5 ★ | Yash Highvoltage | **57.1** | 50 | 49 | 37 | 70 | 72/85 | +23.9% | +29.6% | 6 | ▲1 |
| 6 | Entero Healthcare Solutions | **46.4** | 37 | 61 | 33 | 90 | 63/89 | +28.4% | +26.0% | 4 | ▼2 |
| 7 | GPT Healthcare | **36.8** | 16 | 3 | 45 | 88 | 98/100 | +8.9% | +8.7% | 10 | ▲3 |
| 8 | L. T. Elevators | **35.2** | 35 | 36 | 24 | 70 | 51/15 | +35.0% | — | 7 | ▼1 |
| 9 | Asahi Songwon Colors | **25.3** | 3 | 3 | 45 | 88 | 87/100 | +15.2% | +12.7% | 9 | 0 |
| 10 | Haldyn Glass | **24.3** | 4 | 3 | 45 | 88 | 80/94 | +19.3% | +21.3% | 11 | ▲1 |
| 11 | Novartis India | **19.0** | 10 | 20 | 45 | 88 | 34/64 | +44.8% | +50.6% | 8 | ▼3 |

*Out of pool:* Dynamic Cables (below 30W EMA -4.5%)

★ = would be in next Monday's concentrated cohort at 25/20/20/17/13% by rank.

---

## Cohort: 2026-W35-inaugural (standard)

Decided 2026-08-25, entry-priced off 2026-08-21 close. 27 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 2,082.20 | 2026-09-17 | +46.75% | +46.75% | +4.64 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 1,080.45 | 2026-09-17 | +18.44% | +18.44% | +1.51 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 153.35 | 2026-09-17 | +12.30% | +12.30% | +0.72 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 163.61 | 2026-09-17 | +8.61% | +8.61% | +0.69 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 142.80 | 2026-09-17 | +7.98% | +7.98% | +0.47 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 91.83 | 2026-09-17 | +4.77% | +4.77% | +0.24 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 1,921.60 | 2026-09-17 | +2.50% | +2.50% | +0.23 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 365.15 | 2026-09-17 | -0.77% | -0.77% | -0.08 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 133.40 | 2026-09-16* | -5.52% | -5.52% | -0.66 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,549.80 | 2026-09-17 | -10.83% | -10.83% | -1.13 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +6.65% | **+6.65%** | +6.65 |

\* price carried forward — data source has not yet posted a 2026-09-17 close (Dynamic Cables).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 20 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 2,082.20 | 2026-09-17 | +40.09% | +40.09% | +4.17 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 1,080.45 | 2026-09-17 | +9.57% | +9.57% | +0.85 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 163.61 | 2026-09-17 | +7.84% | +7.84% | +0.70 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 142.80 | 2026-09-17 | +2.84% | +2.84% | +0.17 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 365.15 | 2026-09-17 | -0.42% | -0.42% | -0.04 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 153.35 | 2026-09-17 | -2.01% | -2.01% | -0.08 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 133.40 | 2026-09-16* | -3.33% | -3.33% | -0.20 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 1,921.60 | 2026-09-17 | -4.26% | -4.26% | -0.26 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,549.80 | 2026-09-17 | -4.73% | -4.73% | -0.54 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +4.78% | **+4.78%** | +4.78 |

\* price carried forward — data source has not yet posted a 2026-09-17 close (Dynamic Cables).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 20 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 344.60 | 2026-09-17 | +5.03% | +5.03% | +0.99 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 1,921.60 | 2026-09-17 | -4.26% | -4.26% | -0.68 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,666.60 | 2026-09-17 | -7.85% | -7.85% | -0.99 |
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,549.80 | 2026-09-17 | -4.73% | -4.73% | -1.15 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 497.60 | 2026-09-17 | -8.21% | -8.21% | -1.60 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -3.44% | **-3.44%** | -3.44 |


## Cohort: 2026-W37 (standard)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 13 days live. Invested Rs 82,850.92 / cash Rs 17,149.08.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,646.70 | 6 | 9,880.20 | 2,082.20 | 2026-09-17 | +26.45% | +26.45% | +2.61 |
| Yash Highvoltage | 9 | 950.65 | 9 | 8,555.85 | 1,080.45 | 2026-09-17 | +13.65% | +13.65% | +1.17 |
| GPT Healthcare | 9 | 158.17 | 56 | 8,857.52 | 163.61 | 2026-09-17 | +3.44% | +3.44% | +0.30 |
| Macpower CNC Machines | 8 | 1,904.90 | 4 | 7,619.60 | 1,921.60 | 2026-09-17 | +0.88% | +0.88% | +0.07 |
| Bansal Roofing Products | 4 | 157.05 | 25 | 3,926.25 | 153.35 | 2026-09-17 | -2.36% | -2.36% | -0.09 |
| Haldyn Glass | 6 | 146.40 | 40 | 5,856.00 | 142.80 | 2026-09-17 | -2.46% | -2.46% | -0.14 |
| Thyrocare Technologies | 5 | 576.15 | 8 | 4,609.20 | 559.25 | 2026-09-17 | -2.93% | -2.93% | -0.14 |
| Asahi Songwon Colors | 10 | 372.65 | 26 | 9,688.90 | 365.15 | 2026-09-17 | -2.01% | -2.01% | -0.20 |
| Venus Remedies | 12 | 1,694.40 | 7 | 11,860.80 | 1,549.80 | 2026-09-17 | -8.53% | -8.53% | -1.01 |
| Dynamic Cables | 12 | 146.30 | 82 | 11,996.60 | 133.40 | 2026-09-16* | -8.82% | -8.82% | -1.06 |
| **Cash** | | | | 17,149.08 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.52% | **+1.52%** | +1.52 |

\* price carried forward — data source has not yet posted a 2026-09-17 close (Dynamic Cables).

## Cohort: 2026-W37 (concentrated)

Decided 2026-09-07, entry-priced off 2026-09-04 close. 13 days live. Invested Rs 91,727.25 / cash Rs 8,272.75.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Yash Highvoltage | 17 | 950.65 | 17 | 16,161.05 | 1,080.45 | 2026-09-17 | +13.65% | +13.65% | +2.21 |
| Macpower CNC Machines | 20 | 1,904.90 | 10 | 19,049.00 | 1,921.60 | 2026-09-17 | +0.88% | +0.88% | +0.17 |
| Aeroflex Industries | 13 | 537.45 | 24 | 12,898.80 | 497.60 | 2026-09-17 | -7.41% | -7.41% | -0.96 |
| Dynamic Cables | 20 | 146.30 | 136 | 19,896.80 | 133.40 | 2026-09-16* | -8.82% | -8.82% | -1.75 |
| Venus Remedies | 25 | 1,694.40 | 14 | 23,721.60 | 1,549.80 | 2026-09-17 | -8.53% | -8.53% | -2.02 |
| **Cash** | | | | 8,272.75 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | -2.36% | **-2.36%** | -2.36 |

\* price carried forward — data source has not yet posted a 2026-09-17 close (Dynamic Cables).

---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
