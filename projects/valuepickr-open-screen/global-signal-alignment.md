# Global-signal alignment — Indian proxies checked against their bellwether tailwind

Maintained by the `global-proxy-scan` scheduled task (2×/week, Stage C + D). One row per
**already-researched** Indian proxy whose global theme is currently `accelerating` (or
`steady` with a tight bottleneck). Stage C checks the Indian company's **own** latest
order book / capacity / guidance / pricing / management commentary for the *same* signal the
global bellwether reported, and records a verdict:

| verdict | meaning | portfolio read |
|---|---|---|
| `confirmed` | the Indian name's own numbers show the same signal (order book, capacity adds, pricing, guidance) | eligible as a watchlist / allocation candidate for `portfolio-rs1l-revision` (still must clear its EMA + expectation-gap gates) |
| `partial` | some alignment, not full / not yet in the reported numbers | monitor; not yet an add |
| `not-yet-visible` | global tailwind real, but nothing in the Indian name's disclosures reflects it yet | monitor; re-checked on `stage_c_recheck_days` |
| `diverging` | the Indian name's own numbers **contradict** the global tailwind (flat/declining order book, margin give-back, lost customers) | caution — if held in the portfolio, a review trigger for `portfolio-rs1l-revision` (never an auto-cut; the EMA break / red flag / capex-grace miss remain the sell triggers) |

**This file is an INPUT to `portfolio-rs1l-revision`, not a trade instruction.** It does not
size positions, does not override the 30W-EMA discipline, and does not by itself add or remove
anything. `paper-trading-weekly` picks up any resulting change only after it lands in
`docs/FINAL_PORTFOLIO_RECOMMENDATION.md`.

Not a methodology doc — method lives in `playbook/ishmohit-soic-style.md` §6 and the task
SKILL. Config: `global_bellwethers.json`. Per-run narrative: `global-proxy-log.md`.

---

## Current alignment table

_As of: 2026-09-16_

| Indian name | slug | theme | tailwind | verdict | as-of | note | portfolio action |
|---|---|---|---|---|---|---|---|
| Transformer & Rectifier India | transformer-rectifier-india | Grid + transmission equipment | accelerating | confirmed | 2026-09-01 | Q1FY27 order inflows +218% YoY to ₹2,114cr; record order book ₹6,630cr (+26%); ₹23,000cr enquiry pipeline; plant under expansion = capacity-constrained | watchlist/allocation candidate — clears global-signal check; still gated on EMA + expectation-gap |
| Quality Power Electrical Equipments | quality-power-electrical-equipments | Grid + transmission (HVDC / FACTS) | accelerating | confirmed | 2026-09-01 | Q1FY27 rev +32%, PAT +47%, 28.3% EBITDA margin; book ₹1,945cr (1.9x FY26 rev); HV reactor orders for US hyperscale DCs + FACTS Japan + Abu Dhabi | watchlist/allocation candidate — clears global-signal check; still gated on EMA + expectation-gap |
| Cummins India | cummins-india | On-site DC prime power (gensets) | accelerating | confirmed | 2026-09-01 | Q1FY27 data centres = 40% of powergen revenue (from 23% YoY); customers preponing; "lead times & supply reliability more critical than price" | watchlist/allocation candidate — clears global-signal check; still gated on EMA + expectation-gap |
| Kirloskar Oil Engines | kirloskar-oil-engines | On-site DC prime power (gensets) | accelerating | partial | 2026-09-01 | Q1FY27 named 192 MW HyperNext DC genset order + 5-6yr O&M; PowerGen rev +18%; but consol PAT −20% YoY (margin give-back) | monitor — no add |
| Sansera Engineering | sansera-engineering | AI/semiconductor capex — EUV litho | accelerating | confirmed | 2026-09-01 | Q1FY27 ADS order backlog ~₹5,750cr (ADS sales 3x YoY); new ₹1,250cr / 5-yr order from a semicap-equipment customer; ₹3,500cr capacity plan; semicon rev ramps CY27 | watchlist/allocation candidate — clears global-signal check; still gated on EMA + expectation-gap |
| Aeroflex Industries | aeroflex-industries | Data-centre power & cooling (liquid cooling) | accelerating | confirmed | 2026-09-02 | Q1FY27 liquid-cooling skids = 22.2% of revenue (₹32.4cr, +71% QoQ); skid capacity +50% to 9,000/yr; multi-year LTA with a ~US$141bn US corporation for DC liquid-cooling components; FY27 guide 30-35% "led by data centers" | watchlist/allocation candidate — clears global-signal check; still gated on EMA + expectation-gap |
| Diamond Power Infrastructure | diamond-power-infrastructure | Copper + electrification metals | accelerating | confirmed | 2026-09-02 | Q1FY27 rev +128.6% YoY; commissioned 1,500 MT/mo copper wire-drawing & cable line; DC order book >₹575cr incl. ₹52.86cr Hyderabad hyperscale LOI; aggregate book ₹3,688cr (~2x FY26 rev) | watchlist/allocation candidate — clears global-signal check; still gated on EMA + expectation-gap |
| Rashi Peripherals | rashi-peripherals | Memory super-cycle (DRAM / HBM / NAND) | accelerating | partial | 2026-09-02 | Q1FY27 rev +61.9% YoY but 30-35% of growth = memory-price pass-through, 20-25% volume; EBITDA margin −24bps to 3.04%; mgmt "orange alert" on shortage capping volume — revenue leg of distributor thesis only, no margin benefit | monitor — no add |
| Ramkrishna Forgings | ramkrishna-forgings-ias2026 | Heavy industry / forgings — US reshoring | accelerating | partial | 2026-09-02 | Q1FY27 PAT +298% but margin-/diversification-led; exports GUIDED to ~35% of rev by FY27, not booked; Q1 new orders ₹293cr are 82% domestic auto, not US/Europe reshoring; state = excluded / HIGH CAUTION | monitor — no add (held: n/a) |
| Sai Life Sciences | sai-life-sciences | Life-sciences tools / bioprocessing recovery | accelerating | not-yet-visible | 2026-09-02 | Q1FY27 rev +12% YoY driven by CRO (+24%); CDMO (~60% of rev) only +6% YoY; 33 commercial + 14 late-phase molecules; no CDMO order-book inflection yet — Danaher orders turn not visible in Sai's own numbers | monitor — no add |
| Data Patterns (India) | data-patterns | Defence electronics / sensors (radar, EW, C4ISR) | accelerating | partial | 2026-09-04 | Q1FY27 rev +16.8% YoY, PAT −13.5% on margin compression; order book ₹2,654cr incl. negotiated, Q1 inflow only ~₹226cr; FY27 guide 20-25% + ₹2,000cr inflows; peer Astra Microwave record book incl. ₹2,205cr Uttam radar (largest ever) — backlog/guidance align, own quarter not yet inflecting | monitor — no add |

---

## Change log

- **2026-08-31** — file created with the `global-proxy-scan` v2 redesign (playbook §6). No
  Stage C pass yet; the first scheduled run under v2 fills the table above.
- **2026-09-01** — first v2 Stage C pass. 5 rows added: `transformer-rectifier-india`,
  `quality-power-electrical-equipments`, `cummins-india`, `sansera-engineering` →
  **confirmed** (all under accelerating grid / on-site-power / semicap tailwinds, each with a
  quoted Q1 FY27 order-book / capacity / pricing datapoint); `kirloskar-oil-engines` →
  **partial** (DC demand confirmed via a named 192 MW order, but consolidated PAT −20% YoY —
  pricing-power leg diverging). `revisit_after_30d` set on the four confirmed names. Stage C
  backlog carried to next run: `rashi-peripherals`, `aeroflex-industries`,
  `ramkrishna-forgings-ias2026`, plus newly-queued `sai-life-sciences`,
  `diamond-power-infrastructure`, `azad-engineering`, `unimech-aerospace`.
- **2026-09-02** — second v2 Stage C pass, clearing the carried backlog (5 names). 5 rows
  added: `aeroflex-industries` → **confirmed** (DC liquid-cooling = 22% of revenue, capacity
  +50%, named US LTA); `diamond-power-infrastructure` → **confirmed** (dedicated copper-cable
  line live, DC order book >₹575cr, book ~2x revenue) — `revisit_after_30d` set;
  `rashi-peripherals` → **partial** (revenue optically inflated by memory-price pass-through
  exactly as the distributor thesis predicts, but no margin benefit + shortage flagged as a
  volume headwind); `ramkrishna-forgings-ias2026` → **partial** (profit surge margin-led,
  export recovery guided-not-booked, Q1 orders are domestic auto — state stays excluded);
  `sai-life-sciences` → **not-yet-visible** (CRO carried the quarter, CDMO only +6% YoY, no
  order-book inflection). New theme added upstream (Stage A4): **defence electronics / sensors**
  (Hensoldt bellwether; Data Patterns / Astra Microwave / Paras Defence proxies) — enters the
  scan rotation next run, no alignment row yet.
- **2026-09-04** — third v2 Stage C pass. 1 row added: `data-patterns` → **partial**
  (Defence electronics / sensors — Hensoldt bellwether, first formal read this run =
  **accelerating**: H1-26 order intake doubled to €2.81bn, backlog €10.36bn first >€10bn,
  BtB 2.4x, PCB output ~3× since January). Data Patterns' own Q1FY27: revenue +16.8% YoY but
  PAT −13.5% on margin compression; order book ₹2,654cr incl. negotiated but Q1 inflow only
  ~₹226cr; FY27 guide reaffirmed (20-25% growth + ₹2,000cr expected inflows). Peer Astra
  Microwave carries a record book incl. the ₹2,205cr Uttam radar order from HAL ("largest in
  company history") and a lifted FY27 guide, but soft Q1 profitability on "temporary delays".
  Backlog + guidance align with the global signal; neither Indian name's reported quarter is
  yet inflecting at Hensoldt magnitude → **partial**, `revisit_after_30d` NOT set, re-check
  2026-10-04. No other Stage C names due (all next_check ~2026-10-01/02). No new global theme
  this run; Stage A rotating reads (TSMC, GE Vernova + Siemens Energy) both still
  **accelerating** (Siemens Energy transformer lead times now 3+ years; total backlog $186bn).
- **2026-09-12** — no Stage C rows due this run (all 11 tracked proxies' `next_check_date`
  fall 2026-10-01/02/04); table unchanged, `_As of:_` rolled forward. Stage A re-read 11 themes
  (14 bellwethers): ASML, Micron+SK Hynix, Vertiv, Salesforce, Caterpillar, Arista, Infineon,
  Rheinmetall, GE Aerospace, Cameco, Bloom Energy+ERock — all still **accelerating** except
  enterprise-saas (Salesforce cRPO growth held flat at +14% YoY vs Q1 → downgraded
  `accelerating` → **steady**, no re-rating impact, theme stays human-owned/priority 2). Stage B
  ran for 3 still-`hypothesis` accelerating themes: ai-networking-optics (still no genuine
  India-listed AI-cluster-optics pure-play — log-only), uranium-nuclear (still no direct
  mined-uranium/enrichment play — log-only), power-semiconductors → **new seed**
  `rir-power-electronics` (NSE-listed legacy power-semi maker building India's first SiC fab in
  Odisha, Rs618cr, FY2027 target; pre-commercial, no signal to verify yet). Stage B2
  (geopolitical) found nothing concrete enough to seed: a 2026-09-12 USTR Section 301
  forced-labor-import investigation naming India + many countries was too broad/no clear company
  link; an India-US Reciprocal Defense Procurement Agreement is "close to concluding" but not
  yet signed. Stage A4 found no genuinely new theme (Broadcom's 10GW/2029 OpenAI backlog and
  Ciena's 2028-29 backlog/LTAs both overlap existing semi-capex/ai-networking-optics themes).
- **2026-09-16** — no Stage C rows due this run (all 11 tracked proxies' `next_check_date`
  fall 2026-10-01/02/04); table unchanged, `_As of:_` rolled forward. Stage A re-read 9
  bellwethers: Eli Lilly, Danaher, BorgWarner, Freeport-McMoRan, Rockwell Automation and
  Hensoldt (all stale/cadence-due — all confirmed **unchanged** vs their last print, no new
  quarter yet) plus a rotating sample of TSMC, GE Vernova + Siemens Energy (all still
  **accelerating**, strengthening further: TSMC August monthly revenue +53.3% YoY record;
  GE Vernova total backlog $176bn; Siemens Energy Grid Technologies backlog a record €51bn).
  Stage A4 found one genuinely new dislocation — global shipyard capacity ("sold out well
  into 2030" per SFL's Q2-26 call) — added as theme `global-shipbuilding-capacity` (bellwether:
  HD Hyundai Heavy Industries), formalising the existing x-cluster-sourced "Shipbuilding &
  maritime" active_themes.json entry into the bellwether rotation; Stage B found all 4 obvious
  India shipbuilding names (Mazagon Dock, Cochin Shipyard, GRSE, Shipping Corp of India)
  already `researched` (thesis_fit=neither) — no new candidate, theme stays `unread` pending
  its first formal bellwether read next run. Stage B2 (geopolitical) found a real, dated
  ₹1.10 lakh crore DAC defence-procurement clearance (7-Sep-2026, 98% domestic) but it is only
  an in-principle approval (AoN) with vendor awards not yet made — too early-stage to tie to a
  specific company (Bharat Forge's related Rs425cr marine-gas-turbine contract predates and is
  unrelated to this specific clearance) — not seeded.
