# x-trusted-cluster — run log

Mechanical run log for the `x-trusted-cluster` scheduled task (weekly). One dated block per
run: which handles were read, how many tweets, what stock signals were extracted, what was
written to `state.json` (`source: "trusted-x"`) / `trusted_signals` / `analysis.md`.
Method + why: `playbook/ishmohit-soic-style.md`. State: `x_cluster.json`.

Not a place for methodology notes — those go in the playbook.

---

## 2026-08-30 (first run — manual execution in the setup session; Apify actor confirmed working)
Actor run YeVP69j7yYAe878eE (kaitoeasyapi/...): 10 handles, 30-day window (actor returned ~Aug 7-29 for the busy handles once each searchTerm hit its 100-item cap — daily runs fill forward from here).
Per-handle tweet counts: ishmohit1 68 · unseenvalue 100 · itsTarH 38 · persistencecap 6 · LearningEleven 115 · suru27 100 · srisiv1 3 · dhruvbajaj184 29 · prabhakarkudva 20 · Anand_shah07 30.

### New candidates (source: trusted-x)
- sudeep-pharma (Sudeep Pharma) — @unseenvalue, high — Substack presn on battery-materials optionality
- obsc-perfection (OBSC Perfection) — @LearningEleven, high — stated holding; "scale to scale", strong Q1FY27
- divgi-torqtransfer-systems (Divgi TorqTransfer) — @LearningEleven, high — Indonesia 4WD tender win, >50% recurring, India export springboard
- bliss-gvs-pharma (Bliss GVS Pharma) — @itsTarH, high — 2 quarters 30%+ growth, 11-qtr-high margins, "Anupam Rasayan turnaround"
- nephrocare-health (Nephrocare Health Services) — @unseenvalue, high — Dec-2025 CKD deep-dive, revisiting; dialysis-chain play
- sansera-engineering (Sansera Engineering) — @LearningEleven (holding) + @ishmohit1 (amplified ADS order-book jump), high — precision parts into wafer-fab/equipment + aero/defence

### trusted_signals appended (already-researched)
- td-power-systems, sai-life-sciences, shilpa-medicare-ias2026, entero-healthcare-solutions, laurus-labs, ramkrishna-forgings-ias2026
  (Laurus + RK Forgings noted as cluster-vs-screen divergences — Laurus flagged for a fresh look.)

### Skipped / not acted on
- @ishmohit1: no cleanly-named single-stock buy call this window — his posts were thematic (forgings/castings exporters to US, humanoids→bearings/forgings, CDMO+peptides, textile FY27, fintech operating leverage, DC buildout) + explicit "no reco". Themes flow into vpscreen-scan / global-proxy-scan, not here.
- @unseenvalue CDMO-universe list (Divis, Anthem Bio, Syngene, Neuland, Piramal Pharma, Aarti Pharma, DCAL, Hikal, Cohance) — a tracking list, not per-name conviction; not seeded.
- @LearningEleven concall-quote digests (Carysil, Speciality Restaurants, KSH Intl, Astra Microwave, Gland Pharma, Poly Medicure, PDS, Viyash, Skipper, Hind Rectifiers, Marksans, Steelcast, Standard Engineering) — quote compilations, not stated positions; not seeded (Steelcast + Standard Engineering worth a manual look later).
- @persistencecap / @srisiv1 / @dhruvbajaj184 / @prabhakarkudva / @Anand_shah07 / @suru27 — mostly macro/psychology/framework this window; srisiv1: structurally bearish large-cap private + PSU banks (macro view, noted).
- Notes: 6 new candidates < the ~15 cap, no overflow. Busy handles' 30-day windows were truncated by the 100-item/searchTerm cap; acceptable for a backfill run, daily cadence resolves it.

---

## 2026-08-30 (scheduled run — same-day duplicate of the first run above; skipped)
No Apify actor call made. The first/backfill run above executed earlier today in the setup session and already
processed a 30-day window for all 10 handles, setting `last_tweet_id_seen` per handle and `x_cluster.json.last_run_date`
to 2026-08-30. This scheduled invocation fired on the same calendar day. Firing another actor run now would (a) violate
the "one Apify actor run per week" hard cap in the SKILL, and (b) return nothing new — a 3-day window would yield only
tweets with ids <= the per-handle `last_tweet_id_seen` set hours ago. Nothing written to state.json / trusted_signals /
analysis.md. State files left unchanged (last_run_date already 2026-08-30). Next real scan on the next scheduled day.
- New candidates (source:trusted-x): none
- Refreshed candidates: none
- trusted_signals appended (already-researched): none
- Overflow / skipped: none
- Notes: same-day no-op; de-dupe/cadence working as designed.

## 2026-08-31
- Actor run 1GyfioKaomPWNsTpa (kaitoeasyapi/twitter-x-data-tweet-scraper): 10 handles queried, 112 tweets fetched, 44 newer than last_tweet_id_seen. Per-handle new: ishmohit1 2, unseenvalue 34, itsTarH 1, LearningEleven 5, suru27 1, Anand_shah07 1; persistencecap / srisiv1 / dhruvbajaj184 / prabhakarkudva returned 0 (normal — post rarely).
- New candidates (source:trusted-x): artemis-medicare-services — @suru27 (SEBI RIA, cluster) standalone analytical thread on Artemis Medicare scaling to ~2,000 beds via 30-yr operating agreements + purchased FAR, working around metro land scarcity. Constructive/discovery signal, x_conviction_strength=high, no floor.
- Refreshed candidates: none.
- trusted_signals appended (already-researched): rpg-life-sciences — @unseenvalue bullish "Santaap 2010 → Kantaap 2026" arc (2010 losses → 2026 high margins / CDMO traction / superior ROCE / lean B/S) + disclosed holding ("Mere paas Maa (RPG Life) hai"). Entry/holding. docx regenerated; analysis.md entry added.
- Overflow / skipped: none (well under ~15 cap).
- Notes:
  - @ishmohit1 (primary): 2 new posts, both non-stock (football; impersonation-account warning). No stock signal from the primary handle this run.
  - @LearningEleven "Timepass talk on Sunday" roundup covered Bodal Chemicals / Kiri Industries / Atul / Jaysynth Orgochem / Ultramarine & Pigments (dye-intermediate China supply shock), TD Power Systems, Centum Electronics, TVS Supply Chain Solutions, Travel Food Services — explicitly disclaimed ("None or buy or sell recommendations ... learning and education purposes"). Treated as pure education, no live call → no candidates, no trusted_signals write-back.
  - @unseenvalue: announced published/standalone "current views" on Jubilant Ingrevia + Alivus Life, and an upcoming view on Ather Energy — direction not stated in-tweet, so log-only (no directionless corroboration write-back). Syngene: soft bullish aspiration ("will change PFP if Syngene hits 2000 Cr EBITDA by FY30") — log-only. HDFC Bank: unpaywalled a skeptical piece ("When Reputation Speaks Louder Than Truth") — bearish/skeptical framing, not corroboration; log-only (name already researched via trusted-thread, left untouched).
  - Alivus Life: not in state; directionless mention only → no candidate.
  - regen_lists.py run after write-backs.

## 2026-08-31 (user-directed cluster expansion — manual, interactive session)
User asked to find new X users to trust, read their posts, extract new stocks/themes, research the themes and feed candidates into the scan pipeline.

### New handles added to x_cluster.json (all cluster-tier)
Cross-referenced `playbook/ishmohit-soic-style.md` §5 (the cluster @ishmohit1 engages with) against `x_cluster.json` — exactly 3 named handles were missing. All 3 added:
- **@saket1974** — pipe industry. Very low volume (5 tweets in 30d, all personal/macro, no stock signal).
- **@Finstor85** (Ameya) — very low volume (1 reply to @soicfinance in 30d, no stock signal).
- **@a_basumallick** (Abhishek Basumallick — Shree Rama PMS / Intelligent Investor advisory / CURIOSITY newsletter) — high volume (~100 posts/30d), mostly concall-snippet + macro/theme.

Actor run tJGwmzhh8drAFEZQ1, 30-day window (2026-08-01 → 08-31), 106 tweets. `last_tweet_id_seen` set per handle.

### New candidates
- **sasken-technologies** (Sasken Technologies) — `source: trusted-x`, @a_basumallick, `x_conviction_strength: high`. 3 posts: Sasken holds IP + reference design for 2W display modules currently imported via China's Quectel; indigenous module "ready, awaits China+1 tailwind to play out". Specific named import-substitution catalyst → seeded. No floor.
- **computer-age-management-services** (CAMS), **kfin-technologies** (KFin) — `source: external-lead`. MF RTA duopoly; absent from screen. Seeded from @a_basumallick's repeated "financialisation of savings" theme (see below), NOT a per-name call by him.
- **mazagon-dock-shipbuilders** (Mazagon Dock), **cochin-shipyard** (Cochin Shipyard) — `source: external-lead`. Defence + commercial shipyards; absent from screen. Seeded from @a_basumallick's stated year-long shipbuilding interest (theme below). Both large-cap — vpscreen-scan will apply the large-cap-inflection test.

### trusted_signals appended (already-researched)
- **welspun-corp** — @a_basumallick flagged a ~Rs 17,200 Cr US order (~1x FY26 revenue) + structural long-term Saudi line-pipe demand (#welcorp #manindustries). Bullish data point. docx regenerated. analysis.md entry added.

### New themes added to active_themes.json (both priority 2; a human/user-directed edit, per that file's own "a human can add/retire entries here directly")
- **Capital-markets financialisation** (exchanges, depositories, RTAs, brokers, AMCs, wealth managers). Validated by WebSearch: SIP flows +48% YoY (~Rs 310bn/mo May-26), 77% of equity+balanced net inflows; NSE unique PAN holders 31M (FY20) → 128M (Feb-26); wealth AUM ~30% CAGR FY21-26. SOIC also published "Beyond the Index" on this. Screen already covers BSE / CDSL / Nuvama / 360 One; RTA + AMC legs were thin → CAMS/KFin seeded.
- **Shipbuilding & maritime** (defence shipyards, commercial shipbuilding cluster, ship-repair). Validated: Govt cleared Rs 44,700 Cr of shipbuilding schemes (SBFAS + Shipbuilding Development Scheme); Maritime India Vision 2030 targets global share <1% → 5%; MDL order book ~Rs 27,000 Cr (~3yr visibility) + P75I ~Rs 43,000 Cr pipeline. Screen had only GRSE.

### Skipped / not acted on
- **@a_basumallick** posts on Welspun(done above), Man Industries (already `avoid` in state — bare #manindustries hashtag on a "Saudi pipe demand" post, not enough to revisit an avoid), Cyient, Walchandnagar, Hyundai, Lupin, Dixon, Zydus Life, BEML, CEM India, KSB, KSH Intl, GVT&D (he flagged order-inflow pressure — mild negative), Bluspring, BHEL, Delhivery, CONCOR, GEE Ltd, Vivid Electromech — all concall-snippet / news-highlight posts with a hashtag, not stated positions (same discipline as the 2026-08-30 not-seeding of @LearningEleven's quote digests). Sectors flow via the theme layer, not as per-name seeds.
- **@saket1974**, **@Finstor85** — no stock signal in the 30-day window.
- Regen: `regen_lists.py` run.

## 2026-08-31 (secondary watch list created — user-directed, interactive session)
User asked for a lower-priority scan tier for names that trusted X users are only *tracking* via concall/news snippets (not conviction calls), to be worked before any self/web-search forum discovery.

### Mechanism
- New `source: "trusted-x-watch"` on `status: "candidate"` entries in `state.json`. Fields: `x_source_user`, `x_watch_note`, `x_first_seen_date`.
- `scripts/regen_lists.py` extended → now also writes **`x-cluster-watch-list.md`** (Pending / Already-researched tables, oldest `first_seen_date` first).
- `vpscreen-scan/SKILL.md` — new Step 0.5 **tier 4.8**: worked AFTER every vetted tier (1–4.7), BEFORE any Step 1 web/forum discovery, **capped 2/run**, oldest first, rest carry over. Researched normally — Step 3 preliminary filter applies, no override, no conviction floor. Step 2 fill order + the "fall back to Step 1" gate + Step 5 verdict-line + Step 5.6 field-preservation all updated.
- `x-trusted-cluster/SKILL.md` — Step 3 now sorts each named company into a CONVICTION bucket (→ `trusted-x`) or a WATCH bucket (→ `trusted-x-watch`); Step 4 split into 4A/4B; ~10 watch-names/run cap; Step 6 log template + ground rules updated. Snippet mentions are no longer dropped.

### Retroactive seed (9 names, from this session's @a_basumallick 30-day scrape + one @LearningEleven pre-flag)
cyient, dixon-technologies, zydus-lifesciences, beml, ksb-ltd, bluspring-enterprises, ge-vernova-t-d-india, gee-ltd (all @a_basumallick concall/news snippets); steelcast (@LearningEleven digest, pre-flagged 2026-08-30 "worth a manual look").
- Already researched, so NOT seeded (already in pipeline with a last_analyzed_date): walchandnagar-industries, ksh-international, vivid-electromech.
- Dropped as ambiguous ticker: "Standard Engineering" (@LearningEleven digest) — no confidently-matched listed entity.
- Not added (too tangential / mega-cap OEM / explicit "insights only"): Hyundai, Lupin, BHEL, Delhivery, CONCOR, "Cemindia" (entity unresolved).

`regen_lists.py` run: x-cluster-watch-list.md = 9 pending, 0 researched.

## 2026-09-01
- Actor run OVVgxKGSN2oQeAUbG: 13 handles queried, 7 returned posts, 123 tweets total in the 3-day window (2026-08-29 → 09-01). Per-handle NEW (id > last_seen): ishmohit1 2, unseenvalue 17, LearningEleven 5, a_basumallick 8, Anand_shah07 1, itsTarH 0, suru27 0. No posts: persistencecap, srisiv1, dhruvbajaj184, prabhakarkudva, saket1974, Finstor85.
- New candidates (source:trusted-x): none
- Refreshed candidates: none
- New watch-list names (source:trusted-x-watch): none
- trusted_signals appended (already-researched): laurus-labs, shree-ganesh-remedies (both @unseenvalue, cluster-tier). docx regenerated for both; analysis.md entries added.
- Overflow / skipped: none (well under caps).
- Notes:
  - @ishmohit1 (primary): 2 new posts — GDP-beat "bottoms-up, companies telling the same story" + "real action lies beyond index". Macro/generic, no named stock. No signal from the primary handle this run.
  - @unseenvalue drove the run (17 new, mostly his usual behavioural/veiled-name style):
    - Laurus Labs → disclosed 2019 entry + 2023 double-down, "good decisions", equanimous on price → trusted_signals append (consistent with his prior 2026-08-27 Laurus signal; he is long).
    - #SGRL (Shree Ganesh Remedies) → cryptic bullish-contrarian pattern-match, likens current washout optics to Neuland Labs 2010, points to a concall slide at 48:39 → trusted_signals append with "cryptic, not an explicit buy" caveat.
    - Ather Energy → "only thing on my plate today" + a published paid "Five Fables, One Inflection Point" writeup; direction NOT stated in-tweet ("the gap is where the interesting story begins"). Already researched → log-only (do nothing), consistent with 2026-08-30 handling of his directionless "current views" announcements.
    - Syngene → jokey margin aspiration ("if Syngene hits Anthem Bio's FY26 EBITDA margin by FY36 I won't tweet for 3 months"). Not a real directional call → log-only (consistent with prior run).
    - HCLTech → cautionary/AI-cannibalisation framing, quote-tweeting someone's #HCLTech exit. Bearish lean, not corroboration → log-only.
    - HDFC Bank → pointer to his own March-2026 skeptical note. Bearish/skeptical → log-only (name already researched via trusted-thread, untouched).
    - Neuland Labs (historical example only), Solara (quiz-prompt only) → ignored, no view.
  - @a_basumallick: 8 new, all macro (USD reserve share, FII inflows) or bare-theme hashtag posts with NO named company (#water processing for data centers, EV 2W uptick, sugarcane/ethanol) + Messi retirement. No named-stock signal this run.
  - @LearningEleven (5), @Anand_shah07 (1): behavioural/meta posts, no stock.
  - refresh_derived.py --lists run after write-backs.

## 2026-09-02
**Mechanism change (user-directed, interactive session):** Apify actor `kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest` first attempt returned "Monthly usage hard limit exceeded". User directed that X scraping switch to the **logged-in Chrome browser** (`mcp__claude-in-chrome__*`, real X session as @Sattva_7) as the default for all Twitter runs going forward; Apify is now fallback-only. `x-trusted-cluster/SKILL.md` + `x-handle-triage/SKILL.md` Step 0 + Step 2 rewritten browser-first. This run then completed via the browser path.
- Scan (browser): 13 handles queried, 8 returned posts in the 3-day window (2026-08-30 → 09-02). Per-handle NEW (id > last_seen): ishmohit1 6, unseenvalue ~7 (newest visible; deep scroll capped by X virtualization), itsTarH 1, LearningEleven 5, suru27 ~3, dhruvbajaj184 ~2, Anand_shah07 1, Finstor85 2, a_basumallick ~6. No posts: persistencecap, srisiv1, prabhakarkudva, saket1974.
- New candidates (source:trusted-x): none
- Refreshed candidates: none
- New watch-list names (source:trusted-x-watch): **united-drilling-tools** (@a_basumallick weekly STOCK STORY writeup, explicit not-a-reco disclaimer); **chennai-petroleum-corporation** (@Finstor85 self-QT of May-2026 post, disclosed contra oil bet since 2021). Refreshed existing watch-tier candidate: **antelopus-selan-oil-exploration** (added x_source_user=Finstor85 + x_watch_note; source left as-is — same @Finstor85 self-QT naming "selan" as a disclosed contra oil bet since 2020).
- trusted_signals appended (already-researched): none.
- Overflow / skipped: none (3 watch names, under the ~10 cap).
- Notes:
  - @ishmohit1 (primary): 6 new posts, all CDMO/CMO-sector reply-thread commentary + an ADC-modality note + a CDMO YouTube-video announcement. The reply thread discusses an unnamed "second-source supplier for a blockbuster drug" CDMO with a cautious lean ("how sustainable that contract will be is the key Q") — company not named in his own tweets (parent thread not retrievable logged-out-of-thread). Windlas / Innova named only as "tier 6" CMO categorization (mild-negative, directionless) — Windlas already researched → log-only. **No actionable named-stock signal from the primary handle this run.**
  - @unseenvalue: only the directionless "Azad Engg vs Anthem Bio" comparison-essay promo (both already researched) → log-only, no trusted_signals (consistent with prior-run handling of his directionless writeup announcements). Rest = behavioural/meta + thank-you replies.
  - @Finstor85: self-quote-tweet of a May-2026 post reaffirming "selan, cpcl" as his best 2020-21 contra oil bets ("grown up so well in their ops"). New tweet text itself is a generic point about "market cycle experience"; the named-stock content is in the >90-day-old quoted tweet, positive but not a fresh call → both names to the WATCH list (selan refreshed on the existing candidate, cpcl new).
  - @a_basumallick: weekly STOCK STORY on United Drilling Tools (explicit NOT-A-RECOMMENDATION) → watch list. Rest = macro (US AI bubble), defence-manufacturing chart, auto-sales hashtag soup (#tatamotors #maruti #mahindra…) — no single-name view.
  - @itsTarH: #TheWrap newsletter promos (oil & gas "Samudra Manthan" scheme theme, no named co). @LearningEleven / @suru27 / @dhruvbajaj184 / @Anand_shah07: behavioural/meta/event-logistics replies, no stock. MCX quoted by @LearningEleven (Aug 30, likely already seen last run; MCX already researched) → log-only.
  - Browser-path limitation observed: X's virtualized search feed resists deep automated scroll — reliably yields the newest ~10-15 posts per handle, not always the full 3-day window for high-cadence accounts. Acceptable for a daily cadence (next run's 3-day window overlaps); noted in SKILL.
- refresh_derived.py --lists run after write-backs.

## 2026-09-02 (same-day no-op)
- Duplicate same-day fire: x_cluster.json.last_run_date already 2026-09-02 (full scan completed earlier today via browser path). Per SKILL same-day guard, no second scan. STOP.

## 2026-09-04
- Scan (browser): 13 handles queried, 11 returned posts, ~14 new tweets total. Per-handle new: ishmohit1 3 (rest padel/macro/meta), unseenvalue 6, itsTarH 3, persistencecap 1, LearningEleven 3, suru27 2, srisiv1 0 (empty), dhruvbajaj184 0 new (all <= last seen), prabhakarkudva 0 (empty), Anand_shah07 3, saket1974 1, Finstor85 0 new, a_basumallick 3.
- New candidates (source:trusted-x): none
- Refreshed candidates: none (conviction bucket)
- New watch-list names (source:trusted-x-watch): poly-medicure — @unseenvalue management trust/integrity case-study writeup, favorable framing, no explicit buy call.
- Watch-list refreshed: united-drilling-tools — @a_basumallick re-shared his weekly STOCK STORY (intelsense), same non-recommendation disclaimer; x_watch_note updated, source unchanged.
- trusted_signals appended (already-researched): shilpa-medicare-ias2026 — @LearningEleven (X) bullish FY28/FY29 earnings-triggers thread (oncology API ~30% global share + formulation scale-up). docx regenerated, analysis.md entry added.
- Overflow / skipped: none.
- Notes: mechanism = claude-in-chrome browser (1 browser connected), no Apify needed. Non-actioned mentions logged: (1) @ishmohit1 reply classifying Innova Captab / Windlas Biotech as CDMO "tier 6" and Concord Biotech as ~2-3% innovator sales — framework-tiering remark, mild-negative, no conviction call, all three already in registry; no write-back. (2) @suru27 one-line snark "FirstCry... should be AlwaysCry" — joke, no thesis; skipped. (3) @saket1974 reply fragment "Only Goodluck manufacturing and supplying as of now" — goodluck-india already researched; directionless snippet with mild positive lean, log-only per SKILL 4B. (4) @Finstor85 retrospective on Selan Exploration + CPCL as 2020/21 contra bets that worked — post id below last_seen, already processed. (5) @unseenvalue cryptic "keyword: peptide, it's 60 not 50" — no named company; skipped.

## 2026-09-05
- Scan (browser): 13 handles queried, 9 returned posts, ~23 new tweets total. Per-handle new: ishmohit1 3, unseenvalue 2, itsTarH 0, persistencecap 0, LearningEleven 6, suru27 3, srisiv1 0 (empty), dhruvbajaj184 0, prabhakarkudva 0 (empty), Anand_shah07 3, saket1974 0, Finstor85 0, a_basumallick 5.
- New candidates (source:trusted-x): none
- Refreshed candidates: none
- New watch-list names (source:trusted-x-watch): motherson (Samvardhana Motherson International) — @a_basumallick, capex-scale comparison (consumer-electronics capex commitment vs established players' gross block, "striking" as a scale indicator), explicitly "not an apples to apples comparison", no conviction stated.
- trusted_signals appended (already-researched): none.
- Overflow / skipped: none (1 watch name, well under the ~10 cap).
- Notes: mechanism = claude-in-chrome browser (1 browser connected), no Apify needed.
  - @LearningEleven: 6 new posts. Two touched named stocks but did not clear the bar: ESDS Software Solution mentioned only as banter about being "locked in UC" with others "disappointed and hurt" — no business content, ignored (passing-example rule); a "cables & wires... one Ultra new plant disrupted the whole thesis" post names no specific ticker (sector/corporate-house commentary), ignored. Rest = sector-disruption musings (paints/cables/toys), BlackRock-India macro thesis, generic pre-buy checklist — no named-stock signal.
  - @suru27: 3 new. Two named stocks but stayed too hedged/retrospective for either bucket: CMS (CMS Info Systems) — "may bottom... still no signals on system... still remains in watchlist" (explicitly uncertain, chart-hunch only, not a concall/news/writeup snippet); Pfaudler — retrospective price-move commentary (860→1148) mocking narrative-chasing, referencing that it was "discussed in concalls when prices were depressed" without summarizing that content — no fresh view. Both skipped as too ambiguous for either bucket (no conviction, doesn't fit the watch-bucket source shapes). Third post was AI/career reflection, no stock.
  - @ishmohit1: 3 new, all thematic reply/observation posts (conglomerate disruption economics, "three As" market-top joke, cables-and-wires-as-next-paints framing) — sector-level, no named company.
  - @unseenvalue: 2 new, both book/reading-habit posts, no stock.
  - @Anand_shah07: 3 new, all behavioural/psychology + personal replies, no stock.
  - @a_basumallick: 5 new; Motherson (above) is the only named-company post with business substance — rest are macro/theme hashtag posts (semiconductors, hybrid-car growth, defence manufacturing, US Fed) or newsletter-TOC/link posts with no single-name view.
  - No posts returned: itsTarH, persistencecap, srisiv1 (empty), dhruvbajaj184, prabhakarkudva (empty), saket1974, Finstor85 — all had a top result at or below their existing last_tweet_id_seen (i.e. nothing since 2026-09-04's run), consistent with a quiet day for those accounts.
- refresh_derived.py --lists run after write-backs.
