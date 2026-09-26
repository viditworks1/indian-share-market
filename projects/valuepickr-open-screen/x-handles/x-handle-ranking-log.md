# x-handle-ranking — run log

Dated block per run. Fills per-call `our_verdict` / `since_call_pct` in the dossiers
(<=3 rotated WebSearch price checks/run), regenerates `x-handle-scoreboard.md`.

---

## 2026-09-12
- First-ever run of this task (no prior log block, 153 unresolved calls across 21 of 50 dossiers).
- Dossiers processed: 8 (ayushmitt, InvestorAyush, SpangleAdvisors, equitybyaadi, reachanandl, AnirbanManna10, arvind_kothari, ankitbahuguna84 — oldest `scraped_date` first, packed to the 60-call cap). Calls resolved this run: 60 (agree-strong 2, agree 12, mixed 21, disagree 12, red-flag 9, unverified 4).
- Carried over (not yet touched, oldest-first): StocksAndStoics (30), Accuracy_Invst (2), kanodiaankit12 (1), manojgupta1979 (2), soicfinance (4), tusharbohra (2), CongruenceA (1), MashraniVivek (2), Rahul_Invest (1), nareshbahrain (2), niveshaay (2), vbomkara (1), BeatTheStreet10 (43) — 93 calls remaining, next run should pick these up first.
- Catch-up seeds: none (no unregistered call this run had conviction very-high/high — all were medium or below).
- Price checks (3/3 used): Capri Global Capital ~+70% since 2026-06-23 call (₹222→₹274); CFF Fluid Control ~-2% since 2026-08-26 call (₹1039→~₹1010); Repono left null (July call price found but no confident September "now" price in search results).
- Scoreboard top 5: @AnirbanManna10 68.6, @ankitbahuguna84 49.1, @SpangleAdvisors 43.0, @arvind_kothari 41.0, @ayushmitt 41.0.
- Promotion candidates: none (no row flagged; scoreboard only has blank/`drop?` states this run). Drop candidates (49, ALL first-cycle — none archived per the 2-consecutive-cycle rule, this list is the baseline for next run's comparison): @arvind_kothari, @ayushmitt, @1shankarsharma, @Accuracy_Invst, @AdityaKhemka5, @Amit_Jeswani1, @Ankush__Agrawal, @BeatTheStreet10, @CongruenceA, @DesaiAmeet, @LuckyInvest_ARK, @MarcellusInvest, @MashraniVivek, @MunkThePunk, @NeilBahal, @Rahul_Invest, @SamitVartak, @Sanjay__Bakshi, @StocksAndStoics, @TheAlpha10X, @VijayKedia1, @bharatbetpf, @drvijaymalik, @iMicrocap, @jitenkparmar, @kanodiaankit12, @manojgupta1979, @microcp2mltibgr, @nareshbahrain, @navinmahtani, @nbalajiv, @porinju, @rohitchauhan, @shyamsek, @soicfinance, @thesanjaydutt, @tusharbohra, @vbomkara, @virajmehta16, @Rishikesh_ADX, @niveshaay, @Chins1729, @Investor_Ankur, @MukulAg77304674, @UditSharma_IH, @hiddengemsindia, @sidd1307, @theHarshFolio, @thenamanchandak. Archived this run: none.
- Notes: many drop candidates show "Resolved: 0" only because their dossiers weren't reached this run (60-call cap), not because they lack signal — don't archive @StocksAndStoics/@Accuracy_Invst/etc. next cycle purely off this baseline until their carried-over calls are actually resolved. `@1shankarsharma`, `@DesaiAmeet`, `@MunkThePunk`, `@VijayKedia1`, `@thesanjaydutt` appear on the scoreboard with 0 resolved but have no dossier file with unresolved calls found in this run's scan — likely dossiers with an empty `calls: []` array; worth a human check on whether triage produced anything for them at all.

---

## 2026-09-26
- Dossiers processed: 13 (StocksAndStoics, Accuracy_Invst, kanodiaankit12, manojgupta1979, soicfinance, tusharbohra, CongruenceA, MashraniVivek, Rahul_Invest, nareshbahrain, niveshaay, vbomkara, BeatTheStreet10 — oldest-first; 60 calls total, cap reached). Calls resolved this run: 60 (agree-strong 1, agree 8, mixed 37, disagree 2, red-flag 2, unverified 10).
- Carried over: 513 calls remaining in 90 dossiers (oldest dossiers: ChintanParikh10, DEBU_NEOGI, DesaiAmeet, Disciplined_Inv, JakeraChoudhury, MarketSmithIND, MunkThePunk, PRATIKBULANI555, ParthaAwe, Prashanth_Krish, RupakRoyC, SanaSecurities, StocksResearch, SureshKBN, aditya_kondawar, ashwinidamani, bastionresearch, investor_vineet, mayank66333, mohan_koushik1, mystockedge, nathanit2014, nid_rockz, r_laroia, rajuidesai, rdkriplani, rishithegreat41, sab_maya_hai__, saditya10p, sudhir_bheda, AimInvestments, VineetGala, jeevanpatwa — next run).
- Catch-up seeds: none (no call in this batch was unregistered + bull/very-high/high + new_to_screen).
- Price checks (3/3 used): Apollo Pipes ~+50% since 2026-03-11; Reliance Industries ~-5% since 2026-03-05; Earkart ~-54% since 2026-03-16 (only Apollo Pipes update to dossier, others in untouched handles).
- Scoreboard top 5: @StocksAndStoics 57.2, @AnirbanManna10 68.6, @ankitbahuguna84 49.1, @SpangleAdvisors 43.0, @arvind_kothari 41.0.
- Promotion candidates: none (scoreboard has no state promotions). Drop candidates (~45, all first-cycle): many with 0 resolved calls in this run; none archived per 2-consecutive-cycle rule.
- Notes: many drop? flags have 0 calls resolved this cycle because their dossiers weren't reached (60-call cap + oldest-first ordering). Do not archive until call-resolution backlog narrows and the drop flag persists across 2 runs. Next batch should handle ~70 calls from ChintanParikh10 et al.

