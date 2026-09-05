# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only).

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-09-05 (generated 2026-09-05 19:46). Daily history: 5 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 15 | 104,995.07 | +2.70% | **+5.00%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 8 | 102,207.55 | +1.88% | **+2.21%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 8 | 99,257.50 | +0.18% | **-0.74%** |

*Concentrated series: 1 cohort(s), average return **-0.74%**.*
*Standard series: 2 cohort(s), average return **+3.60%**.*

*Age-matched standard-vs-concentrated comparison appears once both series have ≥2 cohort-weeks.*

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | Conv-only rank | Δ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 ★ | Venus Remedies | **81.3** | 83 | 80 | 70 | 90 | 70/83 | +24.4% | +31.9% | 1 | 0 |
| 2 ★ | Dynamic Cables | **69.5** | 59 | 52 | 65 | 88 | 100/100 | +4.4% | +0.5% | 6 | ▲4 |
| 3 ★ | Macpower CNC Machines | **59.5** | 62 | 66 | 30 | 90 | 35/75 | +43.9% | +39.7% | 3 | 0 |
| 4 ★ | Yash Highvoltage | **53.7** | 46 | 54 | 37 | 70 | 70/86 | +24.6% | +29.0% | 5 | ▲1 |
| 5 ★ | Aeroflex Industries | **48.7** | 46 | 80 | 0 | 90 | 45/77 | +38.5% | +38.1% | 2 | ▼3 |
| 6 | Entero Healthcare Solutions | **46.5** | 43 | 58 | 33 | 70 | 39/83 | +41.8% | +32.4% | 4 | ▼2 |
| 7 | L. T. Elevators | **39.7** | 38 | 47 | 24 | 70 | 65/15 | +27.5% | — | 7 | 0 |
| 8 | GPT Healthcare | **38.9** | 18 | 8 | 45 | 88 | 100/100 | +6.6% | +6.0% | 11 | ▲3 |
| 9 | Bansal Roofing Products | **38.1** | 24 | 30 | 45 | 88 | 70/95 | +24.5% | +19.6% | 8 | ▼1 |
| 10 | Novartis India | **26.6** | 12 | 24 | 45 | 88 | 60/86 | +30.4% | +28.5% | 9 | ▼1 |
| 11 | Asahi Songwon Colors | **24.1** | 6 | 8 | 45 | 88 | 67/100 | +26.5% | +18.0% | 10 | ▼1 |
| 12 | Haldyn Glass | **24.1** | 6 | 8 | 45 | 88 | 67/92 | +26.5% | +23.2% | 12 | 0 |

★ = would be in next Monday's concentrated cohort at 25/20/20/17/13% by rank.

---

## Cohort: 2026-W35-inaugural (standard)

Decided 2026-08-25, entry-priced off 2026-08-21 close. 15 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 1,646.70 | 2026-09-04* | +2.82% | +16.05% | +1.59 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 157.05 | 2026-09-04* | +3.73% | +15.01% | +0.88 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 99.84 | 2026-09-04* | +9.45% | +13.91% | +0.69 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 146.40 | 2026-09-04* | +3.21% | +10.70% | +0.64 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 146.30 | 2026-09-04* | +8.33% | +3.61% | +0.43 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 158.17 | 2026-09-04* | +4.87% | +5.00% | +0.40 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 950.65 | 2026-09-04* | -2.36% | +4.22% | +0.35 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 1,904.90 | 2026-09-04* | -2.02% | +1.61% | +0.15 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 372.65 | 2026-09-04* | +1.29% | +1.26% | +0.13 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,694.40 | 2026-09-04* | +4.53% | -2.51% | -0.26 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +2.70% | **+5.00%** | +5.00 |

\* price carried forward — data source has not yet posted a 2026-09-05 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, RNIT AI Solutions, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 8 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 1,646.70 | 2026-09-04* | +2.82% | +10.79% | +1.12 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,694.40 | 2026-09-04* | +4.53% | +4.16% | +0.47 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 158.17 | 2026-09-04* | +4.87% | +4.25% | +0.38 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 146.30 | 2026-09-04* | +8.33% | +6.01% | +0.36 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 146.40 | 2026-09-04* | +3.21% | +5.44% | +0.32 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 372.65 | 2026-09-04* | +1.29% | +1.62% | +0.16 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 157.05 | 2026-09-04* | +3.73% | +0.35% | +0.01 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 1,904.90 | 2026-09-04* | -2.02% | -5.09% | -0.31 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 950.65 | 2026-09-04* | -2.36% | -3.59% | -0.32 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.88% | **+2.21%** | +2.21 |

\* price carried forward — data source has not yet posted a 2026-09-05 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 8 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,694.40 | 2026-09-04* | +4.53% | +4.16% | +1.02 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,827.60 | 2026-09-04* | -1.10% | +1.05% | +0.13 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 537.45 | 2026-09-04* | -0.87% | -0.86% | -0.17 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 1,904.90 | 2026-09-04* | -2.02% | -5.09% | -0.82 |
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 313.00 | 2026-09-04* | -1.57% | -4.60% | -0.91 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.18% | **-0.74%** | -0.74 |

\* price carried forward — data source has not yet posted a 2026-09-05 close (Aeroflex Industries, Entero Healthcare Solutions, L. T. Elevators, Macpower CNC Machines, Venus Remedies).

---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
