# Progress Log

## 2026-08-09 (live session, manual "Run now" — not the scheduled task)
Ran Batch 1 (13 stocks) live in-session since there's no programmatic way to force-fire the scheduled task, and the user asked to run it now.

**Completed (9 full deep-dives):**
- Rapicut Carbides — speculative tungsten-supercycle microcap, related-party flag
- Aarti Surfactants — early-stage margin turnaround, unproven
- Unihealth Hospitals — Africa hospital platform, strong but SME-liquidity + concentration risk
- Asahi Songwon Colors — margin-driven profit inflection, moderate uptrend
- Gujarat Containers — cheap but unconfirmed, weak technicals, no VP thread found
- Novartis India — ChrysCapital PE buyout special situation, already re-rated 87%
- High Energy Batteries — lumpy defence order book, just posted a loss, avoid for now
- Fluidomat — high-quality compounder hitting a working-capital air pocket
- Trejhara Solutions — high growth, low ROE/ROCE, overbought weekly

**Excluded (4, short notes only):**
- Apar Industries — large-cap (Rs 66,830 Cr)
- Oracle Financial Services Software — large-cap (Rs 1,02,793 Cr)
- BlackBerry — foreign, out of scope
- Nokia — foreign, out of scope

**Pace vs. deadline:** Batch 1 of 8 complete on day 1 of the 7-day (2026-08-16 IST) window — on pace. 8 batches remain (~88 stocks) for the scheduled nightly job to continue with, following the same batch order in manifest.json.

**Methodology notes for future runs:**
- TradingView's interactive chart canvas does not render reliably for automated screenshots — use the `/technicals/` summary tab instead (Weekly/Monthly MACD + Moving Averages + oscillators), reached via the 10-tab timeframe selector (refs 9 and 10 in the interactive list = Weekly, Monthly). Exact Bollinger Band values aren't exposed there — RSI/CCI/Williams %R extremity is used as a documented proxy for "stretched vs. band" positioning.
- The reusable `research/scripts/make_stock_doc.js` + per-stock JSON data file pipeline works well and is much faster than building each docx from scratch.
- Several names had no dedicated ValuePickr thread found (Gujarat Containers, High Energy Batteries, Trejhara) — noted honestly rather than fabricated.

## 2026-08-14 (live session, lean method)
Batches 2-3 complete (26 stocks) using the lean 2-search/no-browser/short-writeup method adopted mid-session for ~80%+ token reduction per stock. Scheduled task fired once (2026-08-13) but produced no output - likely stuck on an unattended permission prompt; not relying on it going forward given the 2026-08-16 deadline. Key findings: Darjeeling Industries has a CONFIRMED active SEBI order (excluded); AVI Polymers flagged HIGH CAUTION (promoter stake 25%->1.1% in one quarter); JITF Infra Logistics flagged AVOID (negative net worth, going-concern audit warnings); NDL Ventures excluded as a large-NBFC reverse-merger vehicle, not a growth microcap. Totals: 28 done, 14 excluded, 74 pending.

## 2026-08-14 (live session, lean method, continued)
Batches 4-6 complete (37 more stocks). Totals: 43 done, 43 excluded, 30 pending (batches 7-8 remain). Notable: Kerala Ayurveda flagged AVOID (severe distress: ROE -117%, interest coverage 0.07x, debt/EBITDA >15x). Confirmed the vast majority of names mentioned by curators for their historical multi-bagger returns (Laurus Labs, Azad Engineering, RR Kabel, Sansera, Anthem Biosciences, MTAR, etc.) are now already large-cap and structurally excluded from a fresh 10x-in-2-3-years thesis - the sheet's "returns already achieved" framing was itself the tell.
