# 6-Month Swing Portfolio — Methodology & Reasoning Log

**Created:** 2026-09-03
**Machine-readable holdings:** `paper-trading/swing-6m/cohorts.json` (append-only, one cohort per week)
**Status:** Since 2026-09-11, a WEEKLY frozen cohort series (like the standard/concentrated series) —
a new Rs 1,00,000 swing cohort is decided every Monday and left untouched for its own 6-month horizon.
The original v1 book (created 2026-09-03) is now cohort `2026-W36-inaugural`, migrated byte-for-byte,
still running to its original 2027-03-03 horizon and first monthly review 2026-10-06.

This document is the permanent reference for *why* this portfolio exists, how names are
chosen, and the rules that govern it. Update the Changelog at the bottom on every revision.
The factor thesis, screen design, and construction rules below (sections 2–5, 7) describe the
**per-cohort methodology** — unchanged by the 2026-09-11 switch to weekly cohorts. Section 6's
worked example is specifically the inaugural cohort's construction.

---

## 1. Purpose — and how this differs from the frozen weekly cohorts

The existing `paper-trading/` journal runs **frozen weekly cohorts** off
`docs/FINAL_PORTFOLIO_RECOMMENDATION.md`: entered, priced at the prior Friday close, and
then never touched. Those are built on a **2–3 year** conviction / expectation-gap thesis.
When we scenario-modelled their 1-year returns, the base case only matched the small-cap
index — because most holdings were entered already 20–44 % extended above their 30-week EMA,
the cohorts carry 15–29 % cash, and the catalysts are mostly dated >12 months out. None of
that is wrong for a multi-year hold; it just means **year-one (and six-month) alpha is
structurally capped**.

This series is the deliberate opposite: a **6-month horizon** per cohort, chosen on the
factors that actually drive short-horizon returns, with hard stops and a monthly review of
live cohorts for thesis-break exits. Since 2026-09-11 it is structured the same way as the
frozen weekly cohorts — a NEW Rs 1,00,000 cohort every Monday, sized once and never
rebalanced — just with the swing factor thesis instead of the fundamentals one, and its own
`swing-6m/cohorts.json` (do **not** merge it into the main `paper-trading/cohorts.json` or
feed it to `refresh.py` directly — `refresh.py` invokes `swing-6m/track.py` as a subprocess
instead, same as it does for `live-recommendation/track.py`).

---

## 2. What drives 6-month alpha (the factor thesis)

Over a multi-year hold, business quality and reinvestment runway dominate. Over six months,
three different things dominate, in this order:

| Factor | 6-month weight | Rationale |
|---|---|---|
| **Earnings-revision momentum** | 35 % | Rising consensus / whisper estimates and *sequential* (QoQ) acceleration is the most robust short-horizon factor in Indian small-caps. Proxy used here: a **confirmed positive last-quarter surprise or explicit guidance raise** (not just YoY growth). |
| **Price momentum / relative strength** | 25 % | 3- and 6-month trailing return, position above a *rising* 30W and 10W EMA, proximity to the 52-week high. Extension that hurts a thesis-buy *helps* a momentum-buy — up to a point. |
| **Dated catalyst inside the window** | 25 % | Must be a datable event within ~6 months: a results date, an already-announced commissioning month, a demerger record date, an open-offer / acquisition close, an order-book conversion visible in the next 1–2 prints. "Greenfield sometime FY27" does **not** count. |
| **Quality floor** | 15 % | Just enough to exclude red-flag tiers, cash-burners, and governance-flagged names. Not a ranking driver. |

**Explicitly down-weighted to ~zero for this horizon:** deep-value / mean-reversion setups,
undated "optionality" theses, pre-inflection turnarounds, and anything held purely on
cheapness. In the `expectation-gap-scores.json` terms: `catalyst_is_dated = false` or
`catalyst_window_months > 6` → not eligible here.

---

## 3. Screen design

**Composite score**

```
swing_score = 0.35·earnings_revision + 0.25·price_momentum_6m
            + 0.25·dated_catalyst_within_6m + 0.15·quality_floor      (each sub-score 0–100)
```

The 2026-09-03 run implemented the momentum/technical half quantitatively (Yahoo daily +
weekly closes, 30W EMA k=2/31 reused from `refresh.py`) and the earnings/catalyst half from
the qualitative tags in `screen-ranking.json` and `expectation-gap-scores.json`. The exact
scoring used this run:

```
mom3     = clamp((r3m  − (−5)) / (35 − (−5)))          # 3-month return, sweet spot
mom6     = clamp((r6m  − 0)    / (70 − 0))             # 6-month return
trend    = 0.5·clamp(ema30_slope8w / 12) + 0.5·clamp(ema10w_slope20d / 15)
posture  = 1 − clamp((ext_vs_30w_ema − 25) / (55 − 25))   # penalise blow-off
nearhi   = clamp((pct_from_52w_high − (−30)) / (−2 − (−30)))
notdump  = 0 if r3m < −12 else 1                        # kill fresh breakdowns
swing_score = notdump · (0.28·mom3 + 0.22·mom6 + 0.25·trend + 0.15·posture + 0.10·nearhi) · 100
```

**Hard filters (all must pass):**

1. Last reported quarter: a **positive surprise or explicit guidance raise** — sequential
   acceleration, not just a YoY number.
2. Price **above a rising 30W EMA and a rising 10W EMA**.
3. **Not a vertical chase:** exclude if `ext_vs_30w_ema > 40 %` **or** 3-month return > 90 %.
4. A **dated catalyst with `window ≤ 6 months`** *or* a confirmed multi-quarter earnings
   inflection already in the tape.
5. **Liquidity:** enough traded value to model a fill. SME / BSE-only names are allowed but
   **capped at 10 %** position size. No Yahoo price history → ineligible (can't track it).
6. **No red-flag tier**, no `avoid` / `highCaution` classification, promoter pledge below
   threshold.

**Data sources:** `valuepickr-screen/data/screen-ranking.json` (quality tiers + Q1 FY27
inflection tags), `valuepickr-screen/data/expectation-gap-scores.json` (dated catalysts +
windows), `valuepickr-screen/data/conviction-scores.json`, Yahoo Finance via
`paper-trading/scripts/refresh.py` helpers. Screening script kept at
`paper-trading/swing-6m/` conventions / rerun from the scratchpad copy noted in the Changelog.

---

## 4. Screen run — 2026-09-03

Candidate universe: the ~7 names with a dated catalyst ≤6 months from
`expectation-gap-scores.json`, plus tier-A/tier-B names carrying an explicit confirmed
Q1 FY27 earnings inflection, plus the current paper-universe names for comparison. 26
screened, 21 priced (5 had no Yahoo history).

| Rank | Name | Bucket | Last | 3m % | 6m %* | vs 52w hi | ext 30W EMA | 30W slope | swing_score |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Vikram Thermo | earnings | 302.3 | +59.1 | +71.6 | −1.3 % | +34.9 % | +21.9 | **93.8** |
| 2 | Electronics Mart India | earnings | 176.2 | +60.5 | +58.2 | −9.0 % | +27.7 % | +18.7 | **92.4** |
| 3 | Macpower CNC | A/earnings | 1944 | +104.7 | +105 | −3.1 % | +42.7 % | +27.0 | 90.7 → **excluded (filter 3)** |
| 4 | Senores Pharma | earnings | 1430 | +37.0 | +36.9 | −7.8 % | +20.0 % | +16.4 | **81.5** |
| 5 | Yash Highvoltage | catalyst | 970 | +38.1 | +36.9 | −3.4 % | +24.7 % | +18.7 | **79.9** |
| — | Unimech Aerospace | earnings | 1465 | +33.8 | — | — | +22.7 % | — | ~80 (retry symbol) |
| 6 | L. T. Elevators | catalyst | 309 | +26.3 | +27.7 | −12.5 % | +23.8 % | +20.2 | **76.9** |
| 7 | Neetu Yoshi | catalyst | 178 | +21.9 | +46.3 | 0.0 % | +27.4 % | +15.2 | **73.7** |
| 8 | Aimtron Electronics | earnings | 1583 | +21.2 | — | −9.1 % | +26.6 % | +20.8 | 70.0 |
| 9 | Apcotex Industries | earnings | 650 | +20.8 | +30.5 | −4.6 % | +25.5 % | +15.6 | **69.7** |
| 10 | Sambhv Steel Tubes | earnings | 130 | +22.8 | +22.7 | −1.3 % | +12.7 % | +5.8 | 61.9 |
| 11 | Ujjivan SFB | earnings | 63 | +18.6 | +17.1 | −13.1 % | +2.3 % | +8.6 | 56.2 |
| 12 | Thyrocare | catalyst | 579 | +11.1 | +10.2 | −10.9 % | +13.2 % | +11.2 | 51.6 |
| 13 | Venus Remedies | A/catalyst | 1702 | +9.4 | +14.9 | −12.6 % | +23.4 % | +16.6 | 49.0 → excluded |
| 14 | Stylam Industries | catalyst | 3241 | +6.7 | +8.4 | −13.3 % | +9.4 % | +12.8 | 47.5 |
| 15+ | Privi Speciality, Apollo Micro, CSB Bank, Dynamic Cables, Surya Roshni, HBL Engineering, Transrail Lighting | — | — | ≤+3 or negative | — | — | at/below EMA | ≤ 3.8 | 0–33 → excluded (filter 2) |

\* Yahoo `daily_series` in `refresh.py` pulls a ~6-month range, so the "6m" and "12m"
columns collapse to the same value — treat "6m %" as "since ~start of window". 1- and
3-month figures are clean.

---

## 5. Portfolio construction rules

- **Sizing:** score-tiered, then capped. Single name ≤ 16 %; SME / thin-liquidity ≤ 10 %;
  per theme ≤ 25 %.
- **Cash:** hold 5–10 %. (Not 15–29 % like the frozen cohorts — over six months, a big cash
  pile is a ~1.5–2 pp drag in a rising tape and the horizon is too short to deploy it well.)
- **Hard stop:** −16 % from entry, per name. No averaging down.
- **Thesis-break exit:** guidance cut, a quarterly miss versus the tracked catalyst, or a
  close below the rising 30W EMA on two consecutive weekly closes → exit next session,
  regardless of price.
- **Market-regime overlay (added 2026-09-12, user rule: "don't fight the market — when index/
  sector/market is getting rough, it makes more sense to get out").** A portfolio-level check
  on top of the per-name rules above, not a replacement for them: `track.py` also checks whether
  the benchmark itself (Nifty Smallcap 250) has closed 2+ consecutive weekly closes below its
  own 30W EMA and raises a cohort-level `MARKET DOWNTREND` flag when it has (same mechanism as
  the per-holding `EMA BREAK` flag, just applied to the benchmark). This never force-exits a
  holding by itself — it's a review signal, same status as the other flags — but when active it
  should weigh toward completing pending thesis-break exits rather than granting benefit of the
  doubt, and toward NOT deploying freed cash into a fresh top-of-rank pick until the flag clears.
- **Trim on realisation:** once a tracked catalyst lands, if the stock makes no new 20-day
  high within ~3 weeks, cut the position by half (the drift has stalled).
- **Review:** monthly (2026-10-06, 11-03, 12-01, 2027-01-05, 02-02). Re-run the screen; cut
  anything that dropped out of the top decile or broke its EMA; redeploy freed cash into the
  current top of the ranked list.
- **Benchmark:** Nifty Microcap 250 TRI (primary), BSE Smallcap TRI (secondary).

---

## 6. The v1 portfolio (Rs 1,00,000, entry 2026-09-03 close)

| Weight | Name | Symbol | Entry | Shares | Invested | Hard stop | Catalyst tracked |
|---|---|---|---|---|---|---|---|
| 15 % | Electronics Mart India | EMIL.NS | 176.16 | 85 | 14,973.60 | 147.97 | Q2 FY27 print ~Nov 2026; Dec-qtr price-hike quarter |
| 13 % | Senores Pharmaceuticals | SENORES.NS | 1430.40 | 9 | 12,873.60 | 1201.54 | Rolling ANDA approvals + Q2 FY27 ~Nov 2026 |
| 12 % | Unimech Aerospace | UNIMECH.NS | 1465.30 | 8 | 11,722.40 | 1230.85 | Q2 FY27 results ~Oct–Nov 2026 |
| 12 % | Yash Highvoltage | YASHHV.BO | 970.00 | 12 | 11,640.00 | 814.80 | Vadodara commissioning H1 FY27; commercial RIP from Oct; H1 print ~Nov |
| 12 % | Vikram Thermo | VIKRAMTH.BO | 302.30 | 39 | 11,789.70 | 253.93 | Q2 FY27 margin trajectory ~Oct–Nov 2026 |
| 10 % | Apcotex Industries | APCOTEXIND.NS | 650.40 | 15 | 9,756.00 | 546.34 | Anti-dumping decision + Q2 FY27 ~Oct 2026 |
| 10 % | L. T. Elevators | LTELEVATOR.BO | 309.45 | 32 | 9,902.40 | 259.94 | DYPC close ~30 Sep 2026; H1 FY27 result ~Nov 2026 |
| 8 % | Neetu Yoshi | NEETUYOSHI.BO | 177.50 | 45 | 7,987.50 | 149.10 | Haridwar capacity doubling Sep 2026; H1 FY27 ~Nov 2026 |
| | **Invested** | | | | **90,645.20** | | |
| | **Cash (9.4 %)** | | | | **9,354.80** | | |

### Per-name reasoning

- **Electronics Mart India (15 %)** — Q1 FY27 PAT +458 % after two years of margin
  compression; consumer-durables retailer with operating leverage turning. Near 52-week
  high, rising 30W and 10W EMAs, extension healthy (+28 %). Given the biggest weight because
  it is the **most liquid** name in the book — the one position we could actually exit at
  size in a stress.
- **Senores Pharmaceuticals (13 %)** — consistent ANDA-approval compounder that has been
  beating its *own* aggressive guidance, which is the cleanest form of the earnings-revision
  signal. +37 % / 3m, extension moderate, EMAs rising.
- **Unimech Aerospace (12 %)** — Q1 revenue +71 %, ROE 22.6 % / ROCE 21.4 %, low debt.
  Momentum (3m +34 %) with genuine quality behind it. Symbol needed a retry
  (`UNIMECH.NS`, not `UNIMECHEM.NS`).
- **Yash Highvoltage (12 %)** — the strongest *dated* catalyst in the set: Vadodara
  greenfield commissioning in H1 FY27, first commercial RIP output from October 2026, and the
  H1 FY27 print on the Rs 360–400 Cr invoicing guide. Expectation-gap window 6 months,
  pending. Also sits in the frozen weekly cohorts — overlap accepted because the *reason* to
  own it here (a 6-month capacity catalyst) is distinct from the long thesis.
- **Vikram Thermo (12 %)** — highest raw swing score (93.8): strong existing fundamentals
  reinforced by Q1 FY27 margin expansion against rising input costs. Weight **held down to
  12 % despite the score** because it is BSE-only, thin, and the most extended name in the
  book (+35 % vs 30W EMA). Stop kept tight.
- **Apcotex Industries (10 %)** — record Q1 FY27 (revenue +40 %, PAT +311 %) on an
  anti-dumping filing plus capacity utilisation. The anti-dumping decision itself is a
  datable near-term event. Extension healthy.
- **L. T. Elevators (10 %)** — SME lift + parking maker doubling revenue, with a
  **3-month** dated catalyst window (DYPC acquisition close by ~30 Sep, H1 FY27 result
  ~Nov). Capped at 10 % because the conviction score fell 61 → 47 on a management-quality
  flag and it is SME-liquidity.
- **Neetu Yoshi (8 %)** — SME railway Class-A foundry, ROCE ~32 %, sitting at its
  52-week high, with a dated Sept-2026 capacity-doubling commissioning. Smallest weight
  purely for SME liquidity; tight stop.

### What was excluded, and why

- **Macpower CNC** — swing score 90.7 but fails filter 3 outright: +105 % in three months,
  +43 % above its 30W EMA. A textbook vertical chase; the risk/reward on a *fresh* 6-month
  entry is poor. Already held in all three frozen cohorts, so the research book is not
  under-exposed to it.
- **Venus Remedies** — momentum has stalled (3m +9 %, 10W EMA slope ≈ flat) and its
  catalyst window is 12 months and `catalyst_is_dated = false`. Fails the 6-month framework
  on both momentum and catalyst timing. Its place is the long thesis, held elsewhere.
- **Dynamic Cables, Surya Roshni, HBL Engineering, Transrail Lighting, CSB Bank** — real
  businesses / order books, but all below a *falling* 30W EMA with negative 3-month returns.
  Filter 2 excludes them. Revisit if any reclaims a rising EMA before a review date.
- **SML Isuzu, Marine Electricals, Vivid Electromech** — no usable Yahoo price history, so
  they cannot be priced or marked systematically. Ineligible until a data source exists.

---

## 7. Known limitations & risks

1. **No true estimate-revision feed.** The 35 %-weighted "earnings_revision" sub-score is
   proxied from qualitative last-quarter surprise tags, not a live consensus-revision
   dataset. This is the biggest methodological gap; a real revisions feed would materially
   sharpen the screen.
2. **Momentum-crash regime risk.** Every name here is, by construction, an up-trend with
   recent gains. A sharp factor rotation (momentum → value) can erase months of gains in
   weeks. The −16 % stops and the two-weekly-close EMA rule are the only defence.
3. **SME / thin liquidity.** Five of eight names are SME or BSE-only. Real-world fills would
   carry 1–3 % slippage each way that this paper model ignores; a forced exit in a drawdown
   could be worse. Hence the 10 % cap and tight stops on those.
4. **Extension already high.** Book-average extension vs 30W EMA is ~+26 %. Less blown-off
   than Macpower, but this is not a "buying the base" portfolio — it is buying confirmed
   trends and accepting mean-reversion risk if catalysts slip.
5. **Yahoo history depth.** `refresh.py`'s `daily_series` returns only ~6 months, so 6- and
   12-month momentum could not be separated this run. A deeper pull (range `2y`) is a
   cheap improvement for the next revision.
6. **Overlap with the frozen cohorts** (Yash Highvoltage, and the theme overlap in
   transmission/T&D capex). Correlated drawdowns across the research book are possible.
7. **Turnover cost.** Monthly rebalancing implies real slippage drag (~2–4 pp annualised in
   microcaps) that the paper model does not charge.

---

## 8. Tracking & success criteria

- **`paper-trading/swing-6m/track.py`** marks **every** cohort in `swing-6m/cohorts.json` to
  market **every weekday**. It is invoked automatically by
  `paper-trading/scripts/refresh.py` (which the `paper-trading-weekly` scheduled task runs),
  so the swing cohorts ride along with the frozen fundamentals cohorts on every run. It
  appends to `history.json` (one snapshot per date+week_id), regenerates `TRACKER.md` (one
  section per cohort), and prints per-cohort per-holding return / distance-to-stop / 30W-EMA
  extension, the portfolio total, the benchmark return since that cohort's own entry, the
  alpha, and any rule flags.
- **Hosted dashboard:** `refresh.py` folds every cohort's latest snapshot into
  `dashboard_data.json` as a `swing_cohorts` list and the **Front-Test Ledger** artifact
  renders a "6-month swing cohorts" section — one panel per cohort (summary, sparkline,
  per-holding table with distance-to-stop and EMA extension, and any active rule flags). Same
  URL as the cohort dashboard.
- Benchmark series used: **Nifty Smallcap 250** (`NIFTYSMLCAP250.NS`) as the Yahoo-available
  proxy for Nifty Microcap 250 TRI. Price index, not TRI — smallcap dividend yield ~1–1.5 %/yr,
  immaterial over six months.
- `track.py` **never trades.** When a flag fires (`STOP HIT`, `NEAR STOP`, `EMA BREAK`,
  `EXTENDED`) on a cohort's holding it is surfaced in the daily report; acting on it is the
  monthly review's job, or an explicit ad-hoc decision. This is now purely a **live-cohort
  monitoring** cadence — it does not replace or rebalance the book, since a fresh cohort is
  already created every Monday regardless.
- **New cohort every Monday** (added 2026-09-11, replacing the old single-book monthly
  re-screen): rerun `swing_screen.py`, hand-curate that week's names, append a new frozen
  cohort to `swing-6m/cohorts.json` per the `paper-trading-weekly` SKILL's Step 2c. Each
  cohort is judged independently against the benchmark over its own window from its own
  `entry_price_date` to its own `horizon_end_date`.
- Each cohort **judged at its own `horizon_end_date`** (6 months from its `decided_date`)
  against Nifty Microcap 250 TRI over the identical window.
- Success per cohort = **beat the benchmark by ≥ 5 pp** after modelled stops/exits, with a
  max drawdown no worse than the benchmark's. Matching the benchmark = the active machinery
  (stops, monthly monitoring) did not earn its complexity. A single 6-month cohort is one data
  point; the method earns confidence as more overlapping weekly cohorts complete their
  horizons and can be compared.

---

## 9. Changelog

- **2026-09-03 — v1 created.** 8 holdings, Rs 90,645 invested / Rs 9,355 cash. Screen run
  of 26 candidates (21 priced). Methodology as in sections 2–5 above.
- **2026-09-04 — tracking wired up.** `swing_screen.py` made permanent at
  `paper-trading/swing-6m/`. Added `track.py` (daily MTM engine) + `history.json` +
  `TRACKER.md`. First snapshot 2026-09-04: value Rs 99,985, −0.01 %, benchmark flat, no rule
  flags. (Some holdings showed a stale `*` price — Yahoo had not posted that day's close yet at
  run time; self-corrects next run.)
- **2026-09-04 — folded into the hosted dashboard.** `refresh.py` now invokes `track.py`
  itself and injects a `swing` block into `dashboard_data.json`; the Front-Test Ledger artifact
  renders a "6-month swing book" section. The separate SKILL Step 1b was removed — one entry
  point (`refresh.py`) drives both books. Artifact republished.
- **2026-09-11 — switched to a weekly, frozen cohort series** (user request: "every week,
  need a new swing portfolio"). Replaced the single ongoing book (`portfolio-v1.json`,
  monthly re-screen replacing the whole book) with `swing-6m/cohorts.json` — same
  append-only, never-rebalanced discipline as the standard/concentrated series, just for the
  swing methodology. The original v1 book was migrated byte-for-byte as cohort
  `2026-W36-inaugural` (no change to its holdings, prices, or dates) and keeps running to its
  original 2027-03-03 horizon. `track.py` rewritten to mark every cohort in the file, not just
  one active version; `history.json` snapshots now key on (date, week_id). Monthly review is
  now purely a monitoring/stop-triggered-exit cadence on already-decided cohorts — it no
  longer replaces the book, since Step 2c of the `paper-trading-weekly` SKILL creates a fresh
  cohort every Monday regardless. `refresh.py`'s dashboard fold-in changed from a single
  `swing` block to a `swing_cohorts` list, one artifact panel per cohort. See also
  [[project_swing_6m_portfolio]] in memory.
- **2026-09-12 — market-regime overlay added** (user rule, section 5). `track.py` now also
  checks the benchmark's (Nifty Smallcap 250) own weekly close vs its 30W EMA and raises a
  cohort-level `MARKET DOWNTREND` flag on 2+ consecutive closes below it, alongside the
  existing per-holding flags. First live read at today's run: benchmark +5.31% above its own
  30W EMA (close 18,339.90 vs EMA 17,415.22 as of the week of 2026-09-06) — flag does not fire.
  Same rule also added to `portfolio-rs1l-revision`'s SKILL.md (Step 3.5) and
  `FINAL_PORTFOLIO_RECOMMENDATION.md` (Section 8H) for the fundamentals-driven book.
