# 1-Month Tactical Portfolio — Methodology & Rules

**Created:** 2026-10-02  
**Machine-readable holdings:** `paper-trading/tactical-1m/cohorts.json` (append-only, one cohort per week)  
**Status:** Active weekly cohort series (started 2026-10-07 target)  
**Distinct from:** `swing-6m/` (6-month momentum) and `live-recommendation/` (fundamentals auto-rebalancing)

---

## 1. Purpose — Pure Short-Term Momentum

The existing swing-6m portfolio targets 6-month horizons with dated catalysts. **This portfolio focuses on 1-month pure technical/momentum moves**, solving the core issue: **stocks like Dhabria Plywood and Dynamic Cables in decline phases get caught by broader technical scoring but are deteriorating on shorter timeframes.**

**1-month tactical filters ruthlessly for:**
- Price ABOVE BOTH 30D EMA and 10D EMA (no decline-phase, oversold, or below-EMA stocks)
- Both EMAs must be RISING (confirmed uptrend, not bounce-only)
- 1-month momentum (5D, 10D, 20D returns positive)
- Relative strength beating Nifty 500 over the same 1-month window

**Result:** A purely tactical portfolio that rides 1-month momentum waves, exits them in a week or two if the technicals roll over (EMA break, stop hit), and redeploys to the next strong name.

---

## 2. Factor Thesis — What Drives 1-Month Returns

| Factor | Weight | Rationale |
|---|---|---|
| **5-day momentum** | 25% | Most recent price action; sweet spot 0–20% |
| **10-day momentum** | 25% | Early sustained move confirmation |
| **20-day momentum** | 20% | Mid-term trend; sweet spot 2–35% (positive bias) |
| **EMA trend** | 15% | 30D + 10D slopes rising (uptrend confirmation) |
| **Posture (extension)** | 10% | 5–15% above 10D EMA (momentum sweet spot) |
| **Relative strength** | 5% | Beating Nifty 500 over 1 month (leadership) |

**Explicitly NOT needed:**
- Dated catalysts (1-month horizon too short)
- Fundamental quality (momentum screams about what's hot NOW)
- Earnings revisions (pure price momentum proxies it)

---

## 3. Screen Design

**Hard filters (ALL must pass):**

1. **Price above BOTH 30D and 10D EMA** — no below-EMA stocks (decline phase, oversold bounces rejected)
2. **Both 30D and 10D EMAs rising** — confirmed uptrend, not a false reversal
3. **Positive 1-month momentum** — 5D, 10D, 20D returns all ≥ 0 (preferably +5% or more on 5D)
4. **Relative strength ≥ 0 vs Nifty 500 / 1m** — not lagging the broad index
5. **Liquidity** — enough traded value, Yahoo history available, NSE/BSE traded

**Scoring formula:**

```
score = (0.25·mom5 + 0.25·mom10 + 0.20·mom20 + 0.15·trend + 0.10·posture + 0.05·nearhi) × 100
bonus = +5 if relative_strength_30d > 15 (significant leadership)
```

**Data sources:**
- Yahoo Finance daily closes (via `refresh.py` helpers)
- 30D EMA = k=2/31, 10D EMA = k=2/11 (exponential smoothing)
- Relative strength vs Nifty 500 over rolling 30 days

---

## 4. Portfolio Construction Rules

- **Capital:** Rs 1,00,000 per cohort
- **Sizing:** Score-tiered, single-name cap 12%, 10% cash buffer
- **Hard stop:** **−10%** from entry (tighter than swing's −16%; short horizon can't afford big drawdowns)
- **Thesis-break exit:** Price closes below BOTH 30D EMA and 10D EMA on 2 consecutive days → exit next session
- **Trim on over-extension:** If price hits +25% above 10D EMA, trim by 30% (lock in early gains in a hot stock)
- **Review:** **Weekly** (vs monthly for swing) — re-run the screen, exit any holding that fell below EMAs, redeploy freed cash
- **Rebalance:** None between cohort creation and week-end review (frozen cohort, like swing-6m)
- **Benchmark:** Nifty 500 (broad index, less small-cap skew than Nifty Smallcap 250)

---

## 5. Cohort Lifecycle

1. **Decision date (Monday close):** Run screen on Confluence-100 technical tier 1–3 names + recent high-conviction winners still in uptrends
2. **Entry price date (Monday close):** Hand-curate top 8–10 names that pass all hard filters
3. **Horizon end date:** +30 calendar days (4-5 weeks)
4. **Weekly review:** Every Monday, check for thesis breaks, trim over-extended names, redeploy
5. **Close out:** At horizon end date OR when thesis breaks (early exit), whichever first
6. **Success criterion:** Beat Nifty 500 by ≥ 3 pp (shorter horizon, higher execution risk, so lower bar than swing's 5pp)

---

## 6. vs. Other Portfolios — Where This Fits

| Portfolio | Horizon | Factors | Rebalance | Hard Stop | Best For |
|---|---|---|---|---|---|
| **Standard/Concentrated** | 2–3 years | Fundamentals (quality, growth) | Ad-hoc (annual/event-driven) | None | Core holdings |
| **6M Swing** | 6 months | Earnings + momentum + catalyst | Monthly review, no rebalance | −16% | Catalyst/earnings plays |
| **1M Tactical** | 1 month | Pure momentum + technicals | Weekly review, no rebalance | −10% | Trend-following, tactical rotation |
| **Live-recommendation** | Ongoing | Fundamentals + technical filter | Continuous (auto-rebalance) | None | Auto-pilot fundamentals |

**1M Tactical's edge:** Catches fast 1–2 month momentum runs BEFORE they've bled into swing cohorts; exits ruthlessly if technicals roll (stops swing downside). Complements swing (captures earlier, faster exits).

---

## 7. Known Limitations & Risks

1. **No fundamental quality gate.** A cash-burner or scam can score high on momentum. Mitigated by: (a) sourcing from Confluence-100 / vpscreen-scan tier 4+ (already pre-filtered for quality floor), (b) tight −10% stops catch deterioration early.

2. **Momentum-reversal regime risk.** Strong momentum can evaporate in 1–2 days, especially in illiquid small-caps. Tight stops are the only defence; Friday close → Monday entry can gap-down over weekend.

3. **Extension creep.** Momentum plays build extension fast (+25% vs EMA in 5 days is common). The trim rule (reduce by 30% on +25% ext) is manual; if not executed in time, a sharp reversal wipes the gain. Weekly review catches this, but Friday-to-Monday gap risk remains.

4. **Weekly review execution.** Requires active decision-making every Monday. If missed, a thesis-break EMA cross can cost −5–10% before the next review.

5. **Liquidity on forced exit.** A stop-hit can occur on illiquid names (SME). Real-world fill could be worse than paper model.

6. **Overlap with other books.** Some names may be held in 6M swing, fundamentals, or live-rec simultaneously (correlated draw-down risk).

---

## 8. Tracking & Success Criteria

- **`paper-trading/tactical-1m/track.py`** marks every cohort MTM every trading day. Invoked by the `paper-trading-weekly` scheduled task. Appends to `history.json`, regenerates `TRACKER.md`.
- **Hosted dashboard:** `refresh.py` folds cohorts into `dashboard_data.json` as `tactical_1m_cohorts` list; the Front-Test Ledger artifact renders a panel per cohort (summary, holdings, flags).
- **Per-cohort checks:** Nifty 500 return over the same entry→horizon window (no TRI; dividend yield immaterial over 1m).
- **Success:** Beat Nifty 500 by ≥ 3 pp, max drawdown ≤ benchmark's.
- **Evaluation:** Individual data points per cohort; method earns confidence as weekly cohorts accumulate.

---

## 9. Integration with Refresh Pipeline

`paper-trading/scripts/refresh.py`'s main loop invokes:
1. `swing-6m/track.py` (marks swing cohorts)
2. `live-recommendation/track.py` (marks auto-rebalancing fundamentals)
3. **`tactical-1m/track.py`** (marks 1M tactical cohorts) ← NEW

All three fold into a single `dashboard_data.json`; the Front-Test Ledger artifact renders three separate sections (standard cohorts, swing cohorts, 1M tactical cohorts).

Weekly cohort creation (Monday) happens in the `paper-trading-weekly` scheduled task's Step 2:
- Step 2a: Screen fundamentals (if applicable)
- Step 2b: Screen 6M swing (if applicable)
- **Step 2c: Screen 1M tactical** ← NEW (run `tactical_1m_screen.py` on Confluence-100 tier 1–3, hand-curate, append to `tactical-1m/cohorts.json`)

---

## 10. Changelog

- **2026-10-02 — Methodology designed & scripts created.** `tactical_1m_screen.py` (1m momentum screen, hard filters for price above EMAs), `track.py` (daily MTM), `cohorts.json` (append-only structure). Ready for first cohort entry (target: 2026-10-07, a Monday).
- **2026-10-07 — First cohort (2026-W41-inaugural) created.** Hand-curated 8 names from Confluence-100 tier 1–3 + strong recent momentum winners. Priced at Monday 2026-10-07 close. Horizon 2026-11-06.

---

## Appendix: Example Cohort Structure

```json
{
  "week_id": "2026-W41-inaugural",
  "series": "tactical-1m",
  "decided_date": "2026-10-07",
  "entry_price_date": "2026-10-07",
  "horizon_end_date": "2026-11-06",
  "capital": 100000,
  "benchmark": "Nifty 500",
  "rules": {
    "composite": "0.25*mom5 + 0.25*mom10 + 0.20*mom20 + 0.15*trend + 0.10*posture + 0.05*nearhi",
    "hard_stop_pct": -10,
    "review_cadence": "weekly",
    "cash_band_pct": [10]
  },
  "holdings": [
    {
      "name": "Stock A",
      "symbol": "SYMA.NS",
      "weight_pct": 12.0,
      "entry_price": 500.0,
      "shares": 20,
      "invested": 10000.0,
      "hard_stop": 450.0
    }
  ],
  "cash": 10000.0
}
```
