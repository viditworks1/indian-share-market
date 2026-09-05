# Paper-Trading Front-Test Tracker

This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to market **every weekday** by `paper-trading/scripts/refresh.py`; this file and `paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` (append-only). Daily snapshots: `daily_history.json` (append-only).

**Two parallel series per week, same Rs 1,00,000, different sizing:**
- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).
- **concentrated** — top-5 of the candidate universe by a **2-factor composite** (`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), sized 25/20/20/17/13. `master_score` (valuepickr-screen, built from studying real high-return investors' documented methods) is itself a renormalized blend of conviction + quality + expectation-gap + consistency + asymmetry — see `valuepickr-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a 4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/fundamental-tier are still shown per-name for context, just no longer weighted separately into the composite (they'd double-count against `master_score`).

**Last updated:** 2026-09-05 (generated 2026-09-05 11:31). Daily history: 5 day(s) recorded.

---

## Summary — all cohorts

| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |
|---|---|---|---|---:|---:|---:|---:|
| 2026-W35-inaugural | standard | 2026-08-25 | 2026-08-21 | 15 | 104,488.25 | +2.20% | **+4.49%** |
| 2026-W36 | standard | 2026-08-31 | 2026-08-28 | 8 | 102,020.45 | +1.70% | **+2.02%** |
| 2026-W36 | concentrated | 2026-08-31 | 2026-08-28 | 8 | 99,613.40 | +0.54% | **-0.39%** |

*Concentrated series: 1 cohort(s), average return **-0.39%**.*
*Standard series: 2 cohort(s), average return **+3.25%**.*

*Age-matched standard-vs-concentrated comparison appears once both series have ≥2 cohort-weeks.*

---

## Concentrated candidate universe — composite ranking (for the next Monday cohort)

Scored fresh each run from live weekly + monthly technicals + the current `master_score` (all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational context only — they feed `master_score` upstream, not this composite directly.

| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | Conv-only rank | Δ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 ★ | Venus Remedies | **81.1** | 83 | 80 | 70 | 90 | 70/83 | +24.9% | +31.9% | 1 | 0 |
| 2 ★ | Dynamic Cables | **69.5** | 59 | 52 | 65 | 88 | 100/100 | +1.3% | +0.5% | 6 | ▲4 |
| 3 ★ | Macpower CNC Machines | **55.8** | 62 | 66 | 30 | 90 | 10/75 | +46.6% | +39.7% | 3 | 0 |
| 4 ★ | Yash Highvoltage | **53.1** | 46 | 54 | 37 | 70 | 66/86 | +26.9% | +29.0% | 5 | ▲1 |
| 5 ★ | Aeroflex Industries | **48.6** | 46 | 80 | 0 | 90 | 45/76 | +38.5% | +39.0% | 2 | ▼3 |
| 6 | Entero Healthcare Solutions | **46.1** | 43 | 58 | 33 | 70 | 36/83 | +43.3% | +32.4% | 4 | ▼2 |
| 7 | L. T. Elevators | **40.0** | 38 | 47 | 24 | 70 | 67/15 | +26.2% | — | 7 | 0 |
| 8 | GPT Healthcare | **38.9** | 18 | 8 | 45 | 88 | 100/100 | +6.6% | +3.5% | 11 | ▲3 |
| 9 | Bansal Roofing Products | **37.7** | 24 | 30 | 45 | 88 | 68/95 | +25.8% | +19.6% | 8 | ▼1 |
| 10 | Novartis India | **27.2** | 12 | 24 | 45 | 88 | 64/86 | +28.1% | +28.5% | 9 | ▼1 |
| 11 | Asahi Songwon Colors | **24.4** | 6 | 8 | 45 | 88 | 69/100 | +25.3% | +18.0% | 10 | ▼1 |
| 12 | Haldyn Glass | **24.3** | 6 | 8 | 45 | 88 | 68/92 | +25.7% | +23.2% | 12 | 0 |

★ = would be in next Monday's concentrated cohort at 25/20/20/17/13% by rank.

---

## Cohort: 2026-W35-inaugural (standard)

Decided 2026-08-25, entry-priced off 2026-08-21 close. 15 days live. Invested Rs 84,544.37 / cash Rs 15,455.63.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,418.90 | 7 | 9,932.30 | 1,614.10 | 2026-09-03* | +0.79% | +13.76% | +1.37 |
| Bansal Roofing Products | 6 | 136.55 | 43 | 5,871.65 | 158.80 | 2026-09-03* | +4.89% | +16.29% | +0.96 |
| Haldyn Glass | 6 | 132.25 | 45 | 5,951.25 | 145.35 | 2026-09-03* | +2.47% | +9.91% | +0.59 |
| Yash Highvoltage | 9 | 912.20 | 9 | 8,209.80 | 970.00 | 2026-09-03* | -0.37% | +6.34% | +0.52 |
| RNIT AI Solutions | 5 | 87.65 | 57 | 4,996.05 | 95.78 | 2026-09-03* | +5.00% | +9.28% | +0.46 |
| GPT Healthcare | 8 | 150.64 | 53 | 7,983.92 | 158.17 | 2026-09-04* | +4.87% | +5.00% | +0.40 |
| Macpower CNC Machines | 11 | 1,874.80 | 5 | 9,374.00 | 1,944.10 | 2026-09-03* | -0.00% | +3.70% | +0.35 |
| Dynamic Cables | 12 | 141.20 | 84 | 11,860.80 | 141.70 | 2026-09-03* | +4.92% | +0.35% | +0.04 |
| Asahi Songwon Colors | 10 | 368.00 | 27 | 9,936.00 | 368.80 | 2026-09-03* | +0.24% | +0.22% | +0.02 |
| Venus Remedies | 12 | 1,738.10 | 6 | 10,428.60 | 1,701.90 | 2026-09-03* | +5.00% | -2.08% | -0.22 |
| **Cash** | | | | 15,455.63 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +2.20% | **+4.49%** | +4.49 |

\* price carried forward — data source has not yet posted a 2026-09-05 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, RNIT AI Solutions, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W36 (standard)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 8 days live. Invested Rs 71,356.63 / cash Rs 28,643.37.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Novartis India | 11 | 1,486.30 | 7 | 10,404.10 | 1,614.10 | 2026-09-03* | +0.79% | +8.60% | +0.89 |
| Venus Remedies | 12 | 1,626.70 | 7 | 11,386.90 | 1,701.90 | 2026-09-03* | +5.00% | +4.62% | +0.53 |
| GPT Healthcare | 9 | 151.72 | 59 | 8,951.48 | 158.17 | 2026-09-04* | +4.87% | +4.25% | +0.38 |
| Haldyn Glass | 6 | 138.85 | 43 | 5,970.55 | 145.35 | 2026-09-03* | +2.47% | +4.68% | +0.28 |
| Dynamic Cables | 6 | 138.00 | 43 | 5,934.00 | 141.70 | 2026-09-03* | +4.92% | +2.68% | +0.16 |
| Asahi Songwon Colors | 10 | 366.70 | 27 | 9,900.90 | 368.80 | 2026-09-03* | +0.24% | +0.57% | +0.06 |
| Bansal Roofing Products | 4 | 156.50 | 25 | 3,912.50 | 158.80 | 2026-09-03* | +4.89% | +1.47% | +0.06 |
| Yash Highvoltage | 9 | 986.10 | 9 | 8,874.90 | 970.00 | 2026-09-03* | -0.37% | -1.63% | -0.14 |
| Macpower CNC Machines | 8 | 2,007.10 | 3 | 6,021.30 | 1,944.10 | 2026-09-03* | -0.00% | -3.14% | -0.19 |
| **Cash** | | | | 28,643.37 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +1.70% | **+2.02%** | +2.02 |

\* price carried forward — data source has not yet posted a 2026-09-05 close (Asahi Songwon Colors, Bansal Roofing Products, Dynamic Cables, GPT Healthcare, Haldyn Glass, Macpower CNC Machines, Novartis India, Venus Remedies, Yash Highvoltage).

## Cohort: 2026-W36 (concentrated)

Decided 2026-08-31, entry-priced off 2026-08-28 close. 8 days live. Invested Rs 92,319.10 / cash Rs 7,680.90.

| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Venus Remedies | 25 | 1,626.70 | 15 | 24,400.50 | 1,701.90 | 2026-09-03* | +5.00% | +4.62% | +1.13 |
| Entero Healthcare Solutions | 13 | 1,808.60 | 7 | 12,660.20 | 1,848.00 | 2026-09-03* | +0.00% | +2.18% | +0.28 |
| Aeroflex Industries | 20 | 542.10 | 36 | 19,515.60 | 537.45 | 2026-09-04* | -0.87% | -0.86% | -0.17 |
| Macpower CNC Machines | 17 | 2,007.10 | 8 | 16,056.80 | 1,944.10 | 2026-09-03* | -0.00% | -3.14% | -0.50 |
| L. T. Elevators | 20 | 328.10 | 60 | 19,686.00 | 309.45 | 2026-09-03* | -2.69% | -5.68% | -1.12 |
| **Cash** | | | | 7,680.90 | | | | — | 0.00 |
| **Total** | | | | **100,000.00** | | | +0.54% | **-0.39%** | -0.39 |

\* price carried forward — data source has not yet posted a 2026-09-05 close (Aeroflex Industries, Entero Healthcare Solutions, L. T. Elevators, Macpower CNC Machines, Venus Remedies).

---

*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. Narrative commentary, when added, goes in the cohort sections above and survives regen only if the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*
