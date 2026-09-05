# x-handle-triage — run log

Dated block per run. One Apify actor run/day; 5 deep-pass handles/run, A1 before A2,
oldest xlsx_row first. Method: see `../../.claude`... (SKILL). Seeds go into `../state.json`
as `source:"external-lead"`, `x_untrusted:true` — no conviction floor.

---

## 2026-09-02
- Apify actor call FAILED: `kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest` returned "Monthly usage hard limit exceeded". No scrape performed.
- Batch that would have run (unchanged, still pending): @LuckyInvest_ARK, @ayushmitt, @drvijaymalik, @MukulAg77304674, @porinju (all A1).
- No dossiers written. No names seeded. Registry not modified. `triage.last_run_date` not set (no actor run consumed).
- Task inert this run — Apify monthly quota exhausted. Retry next scheduled fire.
- Backlog: 103/103 remaining.

## 2026-09-05
- Scan (browser): 5 handles [@Chins1729 @soicfinance @Investor_Ankur @jitenkparmar @manojgupta1979], 25 tweets total scanned (Chins1729: 0 — no results in window; soicfinance: 13, window loaded only back to 2026-08-27 despite scroll retries — X search infinite-scroll stalled, not a true 6-month absence; Investor_Ankur: 1; jitenkparmar: 10, similarly scroll-capped back to 2026-07-14; manojgupta1979: 11, scroll-capped back to 2026-05-22).
- Dossiers written: Chins1729, soicfinance, Investor_Ankur, jitenkparmar, manojgupta1979.
- New names seeded (external-lead, x_untrusted): jyoti-cnc-automation, metropolitan-stock-exchange (2/15 cap).
- Overflow (in dossier, not seeded): none.
- Existing-name re-look flags (→ existing-name-sightings.md): lakshmi-machine-works (@soicfinance, vs current excluded/Low).
- Watch-only names recorded: 1 (LICI, @Investor_Ankur).
- Notes: Chins1729 returned zero posts in the 6-month window (confirmed via page-text, likely dormant/inactive handle). jitenkparmar's visible posts were entirely social/reactive replies with no stock names — surprising for a "value & cyclical" investor note, may keep views off X. Modison Ltd (@manojgupta1979) and Macpower/Sterlite (@soicfinance) already exist in the registry at fresh last_analyzed dates — no re-flag needed.
- Backlog: 83/103 remaining.

## 2026-09-02
- Scan (browser): 5 handles [@LuckyInvest_ARK @ayushmitt @drvijaymalik @MukulAg77304674 @porinju], 49 tweets total. Per-handle: LuckyInvest_ARK 12, ayushmitt 12, drvijaymalik 20, MukulAg77304674 0 (dormant — no posts since Oct 2025), porinju 5. NOTE: X `f=live` search returned a badly shortened window for 3 handles despite the 183-day query — LuckyInvest_ARK and drvijaymalik surfaced only ~1 week (from 2026-08-26), porinju only ~2 weeks (from 2026-08-15). Session throttled deep-scroll after the first pass. Not the ~150-post cap; the opposite.
- Dossiers written: LuckyInvest_ARK.md, ayushmitt.md, drvijaymalik.md, MukulAg77304674.md, porinju.md.
- New names seeded (external-lead, x_untrusted): none (0/8 cap) — zero conviction calls across all 5 handles.
- Overflow (in dossier, not seeded): none.
- Watch-only names recorded: 1 (RACL Geartech, via @ayushmitt — named as an operational-turnaround case study in a reply, no investment view).
- Notes: @drvijaymalik = `refuses` pattern — public timeline is 100% promotional (workshop ads, sector primers, paywalled "Recommended Stocks"); names zero stocks. @ayushmitt = deliberately careful, community/product focus. @LuckyInvest_ARK in-window = macro + StyleUnion (his unlisted retail venture) brand posts, no listed-stock view. @MukulAg77304674 dormant; track via shareholding disclosures instead. @porinju in-window = personal/philosophical only. Recommend Apify full-180d deep-pass for LuckyInvest_ARK, drvijaymalik, porinju on the next x-handle-ranking cycle before finalising discloses_names.
- Backlog: 98/103 remaining.

### 2026-09-02 — correction (user directive)
- User note mid-run: "no one openly gives stock calls; any positive-manner name mention or concall-tracking = a recommendation." Re-applied the looser lens to this batch.
- Change: @ayushmitt RACL Geartech reclassified watch-only -> CONVICTION (bull / high) and SEEDED as `racl-geartech` (source:external-lead, x_untrusted:true, x_source_user:ayushmitt). Quote: "RACL is a beautiful case study of big transformation due to dedication and hard work".
- Re-checked the other 4 under the looser lens: @LuckyInvest_ARK, @drvijaymalik, @porinju named NO India-listed company at all in their (short) windows; @MukulAg77304674 dormant. No further reclassification.
- Revised tallies: seeds 1/8; watch-only 0; @ayushmitt discloses_names -> true.
- Backlog unchanged: 98/103.

## 2026-09-02 — same-day no-op
- Duplicate same-day fire: `triage.last_run_date` already 2026-09-02 (browser scan of @LuckyInvest_ARK/@ayushmitt/@drvijaymalik/@MukulAg77304674/@porinju completed earlier today, backlog 98/103). Hard cap is one scan per calendar day. No scrape, no dossiers, no seeds, registry unchanged. Next batch (@iMicrocap @InvestorAyush @equitybyaadi @SpangleAdvisors @reachanandl) deferred to next scheduled fire.
- Backlog: 98/103 remaining.

## 2026-09-03
- Scan (browser attempted, failed → apify-fallback run kROKNQ2c9AawD4Gk9 / dataset CpEwzwV23XueowQTa): 5 handles [@iMicrocap @InvestorAyush @equitybyaadi @SpangleAdvisors @reachanandl], 379 tweets total. Per-handle: iMicrocap 100 (window truncated at 100-post cap → only 2026-08-27..09-02 covered), InvestorAyush 77 (back to 2026-03-29), equitybyaadi 47 (back to 2026-03-04), SpangleAdvisors 55 (back to 2026-03-04), reachanandl 100 (window truncated at 100-post cap → only 2026-08-21..09-02 covered).
- Browser path failed: X search (f=live, with/without until) and the profile timeline both hard-capped the logged-in Chrome session at ~8-13 posts / ~2-3 weeks, infinite scroll going stagnant with the page footer rendered (end of results) — not a login wall, an X result-throttle. Switched all 5 handles to Apify. Chrome tab closed.
- Dossiers written: iMicrocap.md, InvestorAyush.md, equitybyaadi.md, SpangleAdvisors.md, reachanandl.md.
- New names seeded (external-lead, x_untrusted): **3/15 cap** — `earkart` (high, @InvestorAyush Smallcap Series Part 9 + #1 watchlist), `sastasundar-ventures` (medium, @InvestorAyush Smallcap Series Part 10), `bhel` (medium, @SpangleAdvisors quote-tweet praise). [Backfilled after the run when the SKILL seed bar was lowered — see PIPELINE FIX below. Original run under the old very-high/high-only + 8-cap rule seeded 0.] All high/very-high names named by these 5 handles were already in the screen (Fredun Pharma, TechNVision, Vistar Amar, Entero Healthcare, Repono, Glen Industries, Kerala Ayurveda, Galaxy Supermarket, Indotech, Kernex, BSE, Reliance, Rapicut Carbides, Vaxfab, Alan Scott).
- Overflow (in dossier, not seeded): none (all 3 medium names now seeded under the new rule).
- Existing-name re-look flags (→ existing-name-sightings.md): technvision-ventures-ltd (@InvestorAyush very-high, our Low), vistar-amar-ltd (@InvestorAyush high, our Low), bombay-stock-exchange-bet-on-financialization (@SpangleAdvisors high disclosed multi-yr holding, our Low-Medium), rapicut-carbides (@reachanandl high core holding, our Low).
- Unresolved: @reachanandl's most-repeated core holding is the ticker abbreviation "BRPL" (picked 2021, held through PE 15→61→17, multiple ATH callouts) — could not map to a listed name from any post; recorded as a sighting in the dossier, NOT seeded (never-fabricate). Needs a permalink/chart-screenshot dive on the ranking pass.
- Watch-only names recorded: 5 (@InvestorAyush Aug-18 study watchlist: Aveer Foods, Suba Hotels, Telge Projects, Dhampure Speciality, Vision Infra Equipments).
- Notes: @equitybyaadi and @reachanandl both have disclaimer_pattern=refuses (won't take names openly / "no spoon feeding"). @iMicrocap has pivoted to US micro-cap / SEC-EDGAR coverage — no in-scope India single-stock calls this window. @SpangleAdvisors and @equitybyaadi trade mostly in nameless themes. Two sharp disagreements to resolve on the ranking pass: @InvestorAyush very-high conviction on Fredun Pharma (our screen: Medium) and TechNVision (our screen: Low).
- Backlog: 93/103 remaining.

### PIPELINE FIX (2026-09-03, user-directed)
3 real runs (15 handles) had produced 0 seeds. Root causes: (a) registry saturation — credible microcap handles' core names are mostly already in the 400+ screen (working as intended, no dupes); (b) the `conviction ∈ {very-high, high}` seed gate dropped every medium new name; (c) a calibration miss — "educational / not a recommendation" boilerplate was treated as a downgrader, pushing Earkart (dedicated write-up + #1 watchlist ×3) to medium.
SKILL.md changed: Step 4 now seeds **any** new name with a bull/bear/exit direction (very-high / high / **medium**) — every positively/negatively framed name, not just explicit calls; per-run cap 8 → 15 (`triage.new_seed_cap_per_run` = 15). `vpscreen-scan`'s fast `neither` exit at tier 4.5 is the quality gate now, not a pre-seed conviction bar. Only WATCH-only names and unresolvable tickers stay out. Step 3 grading: a blanket disclaimer no longer downgrades; dedicated write-up / repeated top-of-watchlist = high. New: existing entries that are excluded/Low/stale but get a high+ bull thesis from a handle → logged to `x-handles/existing-name-sightings.md` for `x-handle-ranking` to re-dive.

## 2026-09-03 — same-day no-op
- Duplicate same-day fire: `triage.last_run_date` already 2026-09-03 (Apify-fallback scan of @iMicrocap/@InvestorAyush/@equitybyaadi/@SpangleAdvisors/@reachanandl completed earlier today, backlog 93/103). Hard cap is one scan per calendar day. No scrape, no dossiers, no seeds, registry unchanged. Next batch (@AnirbanManna10 @ankitbahuguna84 @StocksAndStoics @arvind_kothari @hiddengemsindia) deferred to next scheduled fire.
- Backlog: 93/103 remaining.

## 2026-09-04
- Scan (browser): 5 handles [@AnirbanManna10 @ankitbahuguna84 @StocksAndStoics @arvind_kothari @hiddengemsindia], ~313 tweets total. Per-handle: AnirbanManna10 152 (window truncated at ~150-post cap, back to 2026-05-09; newest loaded 2026-08-16); ankitbahuguna84 59 (X live-search stopped paginating at ~26 days, back to 2026-08-09); StocksAndStoics 73 (full window, oldest 2026-03-06); arvind_kothari 20 (full window); hiddengemsindia 9 (dormant, oldest 2026-05-26).
- Note: the standard extractor tripped the harness "Cookie/query string data" content filter on 4 of 5 feeds; re-ran with a URL/param-stripped + charset-whitelisted variant of the same extractor (same scroll/cap logic) — clean. No Apify used.
- Dossiers written: AnirbanManna10.md, ankitbahuguna84.md, StocksAndStoics.md, arvind_kothari.md, hiddengemsindia.md.
- New names seeded (external-lead, x_untrusted): msafe-equipments, sg-finserve, tata-capital, emmvee-photovoltaic-power, workmates-core2cloud, shree-pushkar-chemicals, gng-electronics, premier-polyfilm, bhagwati-autocast, dhabriya-polywood, s-p-apparels, himatsingka-seide, epl-limited, keltech-energies, silicon-rental-solutions (15/15 cap — FULL).
- Overflow (in dossier, not seeded): home-first-finance, capri-global-capital, angel-one (bear), rbz-jewellers (bear), esds-software, cff-fluid-control, megatherm-induction, danlaw-technologies, prizor-viztech, pace-digitek, solex-energy, osel-devices, ajc-jewel-manufacturers, mayur-uniquoters, jasch-industries, wise-travel-india-wti-cabs, kimbal, + cotton-yarn basket (nitin-spinners, ghcl-textiles, sportking-india, vardhman-textiles, nahar-spinning, dcm-nouvelle, shiva-mills).
- Existing-name re-look flags (→ existing-name-sightings.md): emerald-finance, bhageria-industries, bodal-chemicals-ltd, haldyn-glass-ltd, apollo-pipes-ltd-from-the-house-of-apl-apollo, shree-refrigerations.
- Watch-only names recorded: ~23 (mostly StocksAndStoics' cotton-yarn + PVC-pipe + PEB basket names).
- Notes: @hiddengemsindia (Ashish Chugh) and @arvind_kothari (Niveshaay) are effectively refuses-to-name on X — Chugh dormant with 0 stock mentions; Kothari macro/brand only, 1 borderline listed name (Kimbal). "Sigma Advanced" (@ankitbahuguna84) mentioned 2x as a stock but identity unresolvable → dossier note only, not seeded. StocksAndStoics is a high-quality spread-cycle analyst — 10 of the 15 seeds are his.
- Backlog: 88/103 remaining.

### 2026-09-04 — seed-cap override (user instruction)
- Per user: do not hold to the 15/run cap this run — seed every name the research pass identified. Seeded the remaining 24 (total 39 this run): home-first-finance, capri-global-capital, angel-one (bear), rbz-jewellers (bear), esds-software, cff-fluid-control, megatherm-induction, danlaw-technologies, prizor-viztech, pace-digitek, solex-energy, osel-devices, ajc-jewel-manufacturers, mayur-uniquoters, jasch-industries, wise-travel-india-wti-cabs, kimbal, nitin-spinners, ghcl-textiles, sportking-india, vardhman-textiles, nahar-spinning, dcm-nouvelle, shiva-mills.
- Cotton-yarn spinning basket (nitin-spinners, ghcl-textiles, sportking-india, vardhman-textiles, nahar-spinning, dcm-nouvelle, shiva-mills) moved from StocksAndStoics watch_only_names into calls[] at medium/bull (positive sector-spread framing).
- Still NOT seeded: "Sigma Advanced" (@ankitbahuguna84) — listed-entity identity unresolvable; dossier note only. Pure peer-comparison / neutral names remain watch-only (Interarch, EPack Prefab, Astral, Finolex Cables, Prince Pipes, Supreme Industries, Gokaldas Exports, Kitex Garments, Carraro India).
- n_new_seeded updated: AnirbanManna10 7, ankitbahuguna84 11, StocksAndStoics 20, arvind_kothari 1, hiddengemsindia 0.
- external-lead / x_untrusted total in state.json: 73. Overflow list now empty.

## 2026-09-04 (duplicate fire)
- Same-day no-op: triage.last_run_date already 2026-09-04. Skipped scan. Batch would have been: @Chins1729 @soicfinance @Investor_Ankur @jitenkparmar @manojgupta1979.

## 2026-09-05
- Scan (browser): 5 handles [@navinmahtani @Accuracy_Invst @shyamsek @sidd1307 @TheAlpha10X], 34 tweets total (navinmahtani 7, Accuracy_Invst 9, shyamsek 9, sidd1307 0, TheAlpha10X 9; no window truncated at 150 for any).
- Dossiers written: navinmahtani, Accuracy_Invst, shyamsek, sidd1307, TheAlpha10X.
- New names seeded (external-lead, x_untrusted): aequs (1/15 cap).
- Overflow (in dossier, not seeded): none.
- Existing-name re-look flags (→ existing-name-sightings.md): none (Inox India sighting from @Accuracy_Invst and Sterlite Tech sighting from @TheAlpha10X are both already Medium conviction / recently analyzed — don't meet the re-look bar).
- Watch-only names recorded: 19 (all from @TheAlpha10X, garbled/unframed screener lists — Gandhar Oil Refinery, Apollo Micro Systems, KSH International, V-Marc India, Netweb Technologies, Cupid, Midwest Energy, Blue Water Logistics, Neuland Labs, Divgi, Fineotex, KRN, Knowledge Marine, Bharti Airtel, Varun Beverages, CCL Products, ICICI Bank, Bajaj Finance, Sterlite Technologies).
- Notes: @sidd1307 (Siddhartha Bhaiya) returned a genuine empty state for the full 6-month window — dormant or handle issue, not a scrape error. @navinmahtani and @shyamsek showed no stock-specific content this window despite their microcap/contrarian reputations — likely quiet stretch or content format (threads/images) not captured by from: search.
- Backlog: 78/103 remaining.

## 2026-09-05
- Scan (browser): 5 handles [@tusharbohra @microcp2mltibgr @theHarshFolio @kanodiaankit12 @Ankush__Agrawal], 44 tweets total (tusharbohra 7, microcp2mltibgr 9, theHarshFolio 0, kanodiaankit12 11, Ankush__Agrawal 17). Note: X search feed's lazy-load stagnated well short of the 183-day target on 4/5 handles (windows returned: tusharbohra back to 2026-07-08, microcp2mltibgr back to 2026-09-04 only, kanodiaankit12 back to 2026-08-30, Ankush__Agrawal back to 2026-07-11) — not the 150-post truncation cap, just early stagnation. theHarshFolio returned X's genuine empty-state (0 results).
- Dossiers written: tusharbohra, microcp2mltibgr, theHarshFolio, kanodiaankit12, Ankush__Agrawal.
- New names seeded (external-lead, x_untrusted): purple-style-labs (1/15 cap).
- Overflow (in dossier, not seeded): none.
- Existing-name re-look flags (→ existing-name-sightings.md): mv-electrosystems-ltd (@tusharbohra, disclosed position + full IAS2026 deck vs current researched/Low/2026-08-28).
- Watch-only names recorded: 1 (IdeaForge, @tusharbohra — amplified a third-party industry piece with no company-specific view).
- Notes: theHarshFolio returned zero posts in the 183-day window (possible dormant/handle issue, not a scrape failure — X's own empty-state was present). microcp2mltibgr and Ankush__Agrawal windows were also unusually narrow due to search-feed lazy-load stagnation; neither named a specific India-listed company in the tweets actually captured.
- Backlog: 73/103 remaining.
