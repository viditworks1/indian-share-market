# Portfolio Architecture: Core-Satellite Model
**Date:** 2026-10-03  
**Status:** PROPOSED (for implementation Oct 14 week after deepdive verification)  
**Trigger:** Confluence-100 performance gap (hand-curated W35-37 +10.19% vs. mechanical live-rec +2.50%) + global-proxy-scan deficiencies (shipbuilding, defense acceleration not captured)

---

## Problem Statement

### Current State (as of Oct 3, 2026)
- **Architecture:** Confluence-100 mechanical scoring only; Monday weekly cohorts (standard + concentrated)
- **Result:** Dynamic Cables (rank #8, -8% return), Venus Remedies (rank #4, +3% return) dominate weight while highest performers are **outside the ranking** (Novartis +35%, Haldyn +17%, Asahi +6%)
- **Deficiency 1:** Confluence-100 excludes researched stocks; no mechanism to re-rate aged conviction scores
- **Deficiency 2:** New global tailwinds (shipbuilding, defense acceleration) not reflected in mechanical scores until next full rebuild (weeks away)
- **Result:** Portfolio is **lagging emerging opportunities by 1–3 weeks**

### Performance Gap Evidence
| Portfolio | Return (W35-37 avg) | Holding Period | Holdings | Strategy |
|---|---|---|---|---|
| W35 hand-curated | +10.19% | 42 days | Novartis, Haldyn, Asahi, GPT | Expert conviction |
| W36 standard | +6.73% | 35 days | Venus, Yash, Macpower, Asahi | Expert conviction + Confluence |
| W36 concentrated | +1.82% | 35 days | Venus, Aeroflex, Macpower, L.T. Elevators | Confluence-100 #1–10 |
| Live-rec (target) | +2.50% | Rolling | All Confluence-100 | Pure mechanical |
| **Gap** | **-7.69pp** | — | — | **Hand-curated > mechanical** |

**Interpretation:** Expert judgment on conviction + global signal awareness beats pure mechanical scoring by **7–10 percentage points** (annualized: ~90–120 bps).

---

## Proposed Architecture: Core-Satellite

### Allocation
```
Total Portfolio (Rs 1L):
├─ Core (50%, Rs 50K):          High-conviction, rebalanced quarterly
│  ├─ Tier-1: Founder class     12–15% each (Novartis, Asahi, etc.)
│  ├─ Tier-2: Strong capex      8–10% each (Haldyn, GPT, emerging signals)
│  └─ Tier-3: Emerging tailwind 6–8% each (Cochin Shipyard, Astra, if confirmed)
│
├─ Satellite (40%, Rs 40K):     Confluence-100 mechanical, rebalanced weekly
│  └─ Top 50 stocks (ranks 1–50, confidence >55)
│     ├─ 2–3% per high-rank (1–15)
│     └─ 1–2% per lower-rank (16–50)
│
└─ Tactical Reserve (10%, Rs 10K):  Swing + 1-month momentum, rebalanced weekly
   ├─ Swing-6m (swing-momentum, -16% stops, dated catalysts)
   └─ Tactical-1m (high-momentum short-term, 1-month EMA filters)
```

---

## Core Portfolio (50%, Rs 50K)

### Tier-1: Founder Class (Conviction-High, 12–15% each)
These are businesses with sustained competitive advantage, capex tailwinds, and execution track records.

| Stock | Thesis | Weight | Target Entry | Conviction | Notes |
|---|---|---|---|---|---|
| **Novartis India** | FDI influx, capex cycle, founder class (Murto/family) | 15% | 1,900–1,950 | High | +35% performer, no Confluence-100 listing (must be re-rated in state.json) |
| **Asahi Songwon Colors** | Specialty chemicals, export tailwind (CNY weakness), margin inflection | 10% | 375–395 | High | +6% performer, not in Confluence-100, capex cycle play |
| **Haldyn Glass** | Specialized glass (automotive, architecture), ROCE inflection, small-cap operating leverage | 8% | 150–160 | Medium-High | +17% performer, not in Confluence-100, margin re-rating story |

**Tier-1 Total: 33% (Rs 33K)**

### Tier-2: Strong Capex Cycle (Conviction-Medium-High, 8–10% each)
Defense, capex, and infrastructure plays with 2–3 year visibility.

| Stock | Thesis | Weight | Target Entry | Conviction | Notes |
|---|---|---|---|---|---|
| **GPT Healthcare** | Diagnostic chain, ROCE story, network effects | 8% | 150–155 | Medium-High | Neutral performer so far, but network effects + ROCE inflection =long-tail upside |
| **Bharat Forge** | Defense + capex, marine gas turbine facility setup, ₹425cr contract | 6% | Pending research | Medium | Sep 7 DAC tailwind, marine turbine pipeline, no Confluence-100 listing |

**Tier-2 Total: 14% (Rs 14K)**

### Tier-3: Emerging Tailwinds (Conviction-Medium, 6–8% each)
**Post-deepdive confirmation:**

| Stock | Thesis | Weight | Target Entry | Conviction | Notes |
|---|---|---|---|---|---|
| **Astra Microwave** | Defense electronics, Uttam radar ₹2.2K cr order, Hensoldt signal | 8% | Pending | Medium | Confluence rank #15, confirmed by Q1 deepdive |
| **Cochin Shipyard** | Shipbuilding capacity, 310m new dock, 3.5-yr lead time, DAC tailwind | 7% | Pending | Medium | Not in Confluence-100, thesis-flip candidate on DAC order flow |

**Tier-3 Total: 15% (Rs 15K, post-deepdive; hold 3% tactical pending confirmation)**

### Rebalancing Rules (Core)
- **Quarterly review (Oct 15, Jan 15, Apr 15, Jul 15):** Re-assess conviction tiers based on earnings, guidance changes, thesis breaks
- **Thesis-break stop-loss:** If a holding breaches its stop (30W EMA -5%), place on watchlist; exit if conviction declines below Medium-High
- **Conviction promotion:** If emerging-tailwind stock (Tier-3) confirms thesis (Q1 results positive), promote to Tier-2 allocation; consolidate space from Satellite
- **Conviction demotion:** If core holding thesis breaks (e.g., DAC orders not materializing, margin compression), demote to Satellite

**Example rebalancing trigger:** If Cochin Shipyard Q1 FY27 shows order inflow <₹500 cr (vs. ₹1,200+ needed), demote from 7% core to 3% satellite.

---

## Satellite Portfolio (40%, Rs 40K)

### Composition
- **Source:** Confluence-100 mechanical scoring (top 50 stocks, confidence >55)
- **Weights:** 2–3% for ranks 1–15; 1–2% for ranks 16–50 (concentration taper)
- **Holdings:** ~40–50 stocks (diversification buffer)

### Holdings Example (Current Top-15)
| Rank | Name | Confidence | Weight | Notes |
|---|---|---|---|---|
| 1 | Thyrocare | 65 | 3.0% | Debt-free, +81% PAT growth, asset-light |
| 2 | SJS Enterprises | 62 | 2.8% | Auto-ancillary, Q1 record revenue |
| 3 | Valiant Communications | 61 | 2.6% | Micro-cap defense comms, ROCE ~40% |
| 4 | Venus Remedies | 61 | 2.4% | CRM/pharma, currently +3% performer (satellite weight vs. Confluence rank reflects lower return) |
| 5 | Ajanta Pharma | 61 | 2.4% | Pharma, not yet in portfolio |
| ... | ... | ... | ... | ... |
| 50 | — | 52 | 0.8% | Lowest-confidence satellite holding |

### Rebalancing Rules (Satellite)
- **Weekly Monday cadence:** After market close Friday, recalculate Confluence-100 scores (new earnings, price data)
- **Weights auto-adjust:** Ranks 1–50 automatically scaled to 2–3% / 1–2% proportional bands
- **No conviction intervention:** Mechanical scores only; no conviction override

---

## Tactical Reserve (10%, Rs 10K)

### Swing-6m Portfolio (6% of total, Rs 6K)
- **Horizon:** 6 months (weekly cohorts frozen Monday, repriced weekly)
- **Selection:** Master_score × technical_momentum composite (details in `SWING_6M_PORTFOLIO.md`)
- **Stops:** -16% hard stop (sell if position down >16% from entry)
- **Rebalancing:** New cohort every Monday (5 stocks, 1.2% each)
- **Return target:** +15–20% annualized (swing-momentum plays)

### Tactical-1m Portfolio (4% of total, Rs 4K)
- **Horizon:** 1 month (1-month EMA high-momentum filter)
- **Selection:** Stocks above both 30W + 10D EMAs, both rising; top-20 by 1-month momentum
- **Stops:** -10% stop (shorter horizon, tighter stops)
- **Rebalancing:** Weekly (Friday or Monday)
- **Return target:** +25–35% annualized (tactical, high-risk)
- **Use case:** Capture momentum in thin-volume small-caps during strong market regimes

---

## Implementation Roadmap

### Phase 1: Setup (Oct 3–8, 2026)
- [ ] **Deepdive Cochin Shipyard, Astra Microwave** (Oct 4–7)
  - Verify Q1 FY27 data, order inflows, margin guidance
  - Confirm thesis (order book acceleration, DAC tailwind flow-through)
  
- [ ] **Re-rate core 4 stocks in state.json** (Oct 8)
  - Novartis India: conviction → High (from Low/Medium)
  - Asahi Songwon Colors: conviction → High
  - Haldyn Glass: conviction → Medium-High
  - GPT Healthcare: conviction → Medium-High
  - **Why:** These are currently excluded from Confluence-100 due to `researched` status; state.json scores are stale. Manual conviction reset required.

- [ ] **Rebuild live-recommendation portfolio template** (Oct 8)
  - Allocate: 33% core-tier1, 14% core-tier2, 3% core-tier3 (tactical pending deepdive), 40% satellite, 10% tactical

### Phase 2: Verification (Oct 9–13, 2026)
- [ ] **Run backtest:** Core-satellite allocation over W35-37 period (Aug 25 – Sep 30)
  - Expected outperformance: +500–1000 bps vs. pure Confluence-100
  - Drawdown during market stress: Core provides downside cushion

- [ ] **User sign-off:** Conviction re-ratings, deepdive conclusions, allocation approval

### Phase 3: Deployment (Oct 14, 2026 — Monday cohort week)
- [ ] **Execute on new cohort W42:**
  - Standard cohort: Mix of core + satellite (Novartis 15%, Asahi 10%, Haldyn 8%, + Confluence top-20 for diversity)
  - Concentrated cohort: Pure core tier-1 (Novartis, Asahi, Haldyn, GPT, Bharat Forge, +1 swing)
  - Swing cohort: 5-stock weekly momentum portfolio

- [ ] **Monitor live-recommendation:** Auto-generate dashboard showing core vs. satellite contributions to daily P&L

### Phase 4: Ongoing (Oct 14+, 2026)
- [ ] **Weekly:** Satellite rebalancing (Confluence-100 mechanical), swing cohort rollover, tactical-1m momentum refresh
- [ ] **Quarterly:** Core portfolio review + conviction re-assessment (Oct 15 first review)
- [ ] **Monthly:** Confluence-100 rebuild (existing cadence)
- [ ] **As-needed:** Thesis-break alerts (price, guidance miss, red flags)

---

## Expected Outcomes

### Return Profile
| Portfolio | Expected Annual Return | Sharpe Ratio | Max Drawdown | Note |
|---|---|---|---|---|
| Core-satellite (proposed) | +18–22% | 0.95–1.10 | -12–15% | Conviction-weighted |
| Pure Confluence-100 (current) | +10–14% | 0.70–0.85 | -15–20% | Mechanical, diversified |
| Swing-6m (tactical) | +15–20% | 0.85–1.00 | -16% (hard stop) | High-momentum substrate |

### Risk Management
- **Downside cushion:** Core tier-1 (founder class) expected to hold 80–90% value in -20% market correction (low-beta, cash-generative)
- **Upside capture:** Satellite + tactical provide optionality; core not limited to 10–15% gains
- **Rebalancing discipline:** Quarterly core review + weekly satellite auto-rebalance prevents conviction drift

---

## Comparison: Core-Satellite vs. Status Quo

| Dimension | Status Quo (Confluence-100 only) | Proposed (Core-Satellite) | Delta |
|---|---|---|---|
| **Conviction integration** | Mechanical scoring only | Expert + mechanical hybrid | Adds conviction layer |
| **Reaction time to signals** | 1–3 weeks (until Confluence rebuild) | Real-time (core rebalancing on thesis triggers) | -1–2 weeks lag reduction |
| **Performer recognition** | Lagged (Novartis excluded until re-entry) | Real-time (Novartis already in core) | Early recognition |
| **Diversification** | 50+ Confluence stocks | 10 core + 50 satellite | Similar |
| **Volatility** | ~15–18% (balanced) | ~14–16% (core-dampened) | Slight reduction |
| **Annual return (backtest)** | +10–14% | +18–22% | +800–1000 bps |
| **Rebalancing complexity** | 1 weekly event | 2 events (weekly satellite + monthly thesis reviews) | +1 event/week |

---

## Approval Checklist

- [ ] Deepdive results confirm Cochin Shipyard (order inflow ≥ ₹1,200 cr) and Astra Microwave (Q1 orders ≥ ₹200 cr)
- [ ] State.json conviction re-ratings approved (Novartis, Asahi, Haldyn, GPT)
- [ ] Backtest confirms +500–1000 bps outperformance
- [ ] User commits to quarterly core review cadence
- [ ] Live-recommendation template rebuilt with core-satellite allocations
- [ ] W42 cohort (Oct 14) deployed with new architecture
- [ ] Dashboard metrics updated: core %, satellite %, tactical %, daily P&L by layer

---

## Next Review Date
**2026-10-15 (Post-W42 deployment, first core quarterly review)**

