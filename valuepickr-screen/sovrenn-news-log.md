# Sovrenn Daily News — pipeline seed log

Source: `~/Downloads/Sovrenn_Daily_News_Digest.docx` — a compiled digest of "SOVRENN DAILY
NEWS" posts from the Sovrenn Community 12 WhatsApp group. Period covered: Mar–Aug 2026;
9 dated posts (2 Apr – 25 Jun 2026), 47 company updates. Supplied by the user 2026-09-02
with the instruction: identify the stocks, add them to the research pipeline and all ongoing
routines, and — since these are mostly microcaps thin on ValuePickr — weight the research
toward quarterly / annual reports, exchange announcements and news over forum discussion.

## What was done (2026-09-02)

44 distinct companies in the digest. Classified against `state.json`:

### New candidates seeded — `source: "sovrenn-news"`, `status: "candidate"` (25)
Each carries `sovrenn_note` (digest datapoint + date). Picked up by `vpscreen-scan`
Step 0.5 **tier 4.65** (uncapped within the 10/run batch; ~3 runs to drain). Research
brief for the tier: resolve the VP topic if one exists (Step 3.05), then work off the
latest quarterly + concall, last 2–3 annual reports, and 6 months of BSE/NSE
announcements; forum deep-read is best-effort. `sovrenn_note` is an unverified lead —
confirm against the filing before it moves conviction.

| slug | digest hook |
|---|---|
| sathlokhar-synergys-ec-global | Apr: orders ₹125 Cr (Reliance Consumer ₹102 Cr); FY26 turnover >100% YoY; OB ₹991 Cr, pipeline ₹18,417 Cr |
| chamunda-electricals | Apr: LoA ₹63 Cr GETCO, 88 sub-stations O&M, 3 yr |
| solarium-green-energy | Apr: LoA ₹188 Cr solar EPC + 3 yr O&M, MAHAGENCO 50 MWac |
| eco-recycling | Q4FY26 sales +90%, PAT +250% (₹7 Cr); e-waste |
| kirloskar-pneumatic | Q4FY26 sales +20% ₹712 Cr, PAT +79% ₹144 Cr, OPM 19→26% |
| bondada-engineering | Q4FY26 sales +28% ₹914 Cr; Jun: NOA ₹1,338 Cr NTPC Renewable (250 MW solar + BESS) |
| servotech-renewable-power | Q4FY26 sales +49% ₹217 Cr, PAT +38%; EV chargers + solar |
| exhicon-events-media-solutions | ICICI Lombard tie-up; H2FY26 sales +23% ₹100 Cr, PAT +15% |
| kp-green-engineering | Orders ~₹507.9 Cr (solar structures, TL towers, PEB, isolators) |
| kp-energy | Q4FY26 sales +58% ₹632 Cr, PAT +72% ₹79 Cr; wind EPC/BOP + IPP |
| ceigall-india | Q4FY26 sales +37% ₹1,387 Cr, PAT +79% ₹129 Cr; roads EPC |
| safe-enterprises-retail-fixtures | H2FY26 sales +31% ₹106 Cr, PAT +41% ₹31 Cr; retail fixtures |
| kaka-industries | H2FY26 sales +35% ₹138 Cr, PAT +67% ₹10 Cr; PVC profiles |
| insolation-energy | Q4FY26 sales +100% ₹794 Cr, PAT +67% ₹70 Cr; solar modules |
| viviana-power-tech | H2FY26 sales +2.6x ₹441 Cr, PAT +2.9x; electrical EPC / EV infra |
| travel-food-services | Q4FY26 sales +26% ₹461 Cr, PAT +15% ₹123 Cr, OPM 37→40%; airport F&B |
| sat-kartar-life | NABH accreditation, Sanjeevan Hospital New Delhi; Ayurveda / D2C wellness |
| winsol-engineers | Order ₹49.80 Cr KPIG Energia, 400 kV EHV line, Gujarat |
| krm-ayurveda | NABH Bengaluru; new 23-bed hospital Pitampura, New Delhi |
| kilburn-engineering | First order ₹70.2 Cr Casale SA Switzerland (fertilizer process equipment) |
| arham-technologies | NSE Emerge → NSE Main Board migration approved |
| desco-infratech | Subsidiary commissioned Phase-1 5 TPD CBG plant, Bulandshahr |
| vinyas-innovative-technologies | POs ₹72.21 Cr PCBA, 3–6 mo; EMS / defence electronics |
| atmastco | Order ₹57.33 Cr L&T-MHI Power Boilers (ceiling girder, 4,368 MT) |
| shanti-gold-international | Board to consider fund raise (FPO/QIP/rights/...); gold jewellery mfr |

### Re-tagged (1)
- `marine-electricals-riding-the-waves-of-expansion` — was an untagged `candidate`;
  set `source: "sovrenn-news"` + `sovrenn_note` (Jun: orders ₹76.4 Cr from STT Global
  Data Centres + Deepak Chem Tech). Now enters via tier 4.65.

### Already researched — re-verification flagged (11)
`conviction_needs_reverification: true` + `reverification_reason`, `last_analyzed_date`
cleared → swept by `vpscreen-scan` Step 0.5 **tier 2**. Chosen where the digest datapoint
is a material earnings inflection (sales/PAT +>40% YoY) or a large order/rating/contract
vs size, and current conviction was not already High.

| slug | prior | digest datapoint |
|---|---|---|
| oriana-power | Low / 10x | SECI Green Ammonia agreement formalised — 60k TPA, ₹3,135 Cr / 10 yr |
| websol-energy-system-ltd | Low / 10x | Q4FY26 sales +132% ₹401 Cr, PAT +158% ₹125 Cr |
| cosmic-crf-limited | Low / 10x | H2FY26 sales +78% ₹412 Cr, PAT +2.4x |
| zaggle (…pain-points…) | Low / 10x | 5-yr Zaggle Save deal with Crompton Greaves Consumer |
| veefin-solutions | EXCLUDED | BSE SME → Main Board + NSE direct-listing move — re-check the exclusion |
| aimtron-electronics | Medium / 10x | H2FY26 sales +59% ₹162 Cr, PAT +71%; warrant conversion ₹15.8 Cr |
| acutaas-chemicals | Medium / neither | Q4FY26 sales +41% ₹433 Cr, PAT +2.1x, OPM 28→42% — re-test "neither" |
| cartrade-tech-ltd | Medium / neither | Q4FY26 sales +19%, PAT +54%, OPM 27→35% — re-test "neither" |
| abs-marine-services | Medium / 10x | CRISIL upgrade A-/A2+, facilities → ₹505.5 Cr, 31% rev CAGR, 55% OPM |
| epack-prefab-technologies | Low / neither | Mambattu plant +13,200 MT, commercial production from 29 Apr 2026 |
| apsis-aerocom | Low / neither | Defence supply order ₹7.24 Cr (small abs., material vs micro base) |

### Already researched — note only, no re-verification (7)
`sovrenn_news[]` entry appended; conviction/thesis untouched. Datapoint minor or merely
corroborates the existing view: `anant-raj` (promoter buying ₹2.5 Cr), `deep-industries`
(order ₹78 Cr Antelopus Selan), `cantabil-india` (Q4 sales +15%), `shivalik-bimetal-controls`
(Q4 sales +23%, steady), `fredun-pharmaceuticals` (Q4 sales +28%, PAT +57%),
`yatharth-hospital-trauma-care-services` (Q4 sales +47%), `krishna-defence-allied-industries`
(MoD order ₹45.6 Cr).

## Downstream routines
- **`deepdive-top100`** — no change needed; it auto-includes any `status:"researched"` name
  by `priority_score` (never-deep-dived → +55). Once tier 4.65 / tier 2 research completes,
  these flow into the deep primary-document crawl automatically — that crawl (3 yr annual
  reports + ~4 quarters concalls + 6 mo announcements) is exactly the "more energy on
  quarterly/annual reports" the user asked for.
- **`vpscreen-rerank`**, **`portfolio-rs1l-revision`**, **`paper-trading-weekly`** — no change;
  they consume `state.json` / the rankings and pick up any new researched name + conviction
  on their own cadence.
- **`vpscreen-audit`** — `audit_state.py` gained a report-only sovrenn-news backlog check
  (fires only if the tier-4.65 queue isn't draining, threshold 30).

## Provenance note
The digest is a third-party WhatsApp compilation, not a primary source and not a trusted-user
call — hence no conviction floor and no `trusted_signals` entries. Every datapoint is a lead
to verify against the company's own filings during research.

---

## 2026-09-02 — sovrenn.com/discovery page addendum

User asked to also check `https://www.sovrenn.com/discovery` for additional names.

**Finding: the Discovery buckets are paywalled.** Logged-out, every company is masked as
"Company A / Company B / …" (labels reset per page); only the market cap, TTM PE, date and
the financial-trigger remark are visible, not the identity. The `Analyse` button needs a
login. I did not sign up or log in. So the buckets can't be harvested wholesale from here.

**What the buckets are** (counts as of 2026-09-02): Functional triggers — Excellent Results
(Jun-26) 154, (Mar-26) 223; FY27 Revenue Guidance 182; Large Order Receipts 308; Order Book
194; Aggressive Growth >30% 202; Capacity Expansions / New Products 273; Promoter Buying 170;
JV/Partnerships/Acquisitions 274; Preferential Issuance 271; Credit Rating Updates 213; Bulk
Deals 234; plus ~30 Sectoral buckets and a monthly "First Time Covered" history. Same
per-quarter result-template phrasing as the WhatsApp digest — i.e. Discovery is the
structured superset; the digest was the small named slice of it.

**Reverse-identified from the visible remarks — round 1 (1):**

| slug | how identified | why it's a fit |
|---|---|---|
| `virtual-galaxy-infotech` — **Virtual Galaxy Infotech Ltd** | "Excellent Results (Jun-26)" p1: ₹383 Cr mcap, 8.3x TTM PE, Q1FY27 rev ₹40.4 Cr +60% YoY, order book ₹145.5 Cr (2x), **USD 1.1M software contract with Botswana Development Corporation** — the counterparty is a unique fingerprint → web search confirmed | Cheap (~8x TTM PE) BFSI core-banking software SME; FY26 rev ₹182 Cr (+52%), 25% PAT / 46% EBITDA margin, ~42% recurring revenue, ₹500 Cr FY29 revenue target, first international win. Seeded `source: "sovrenn-discovery"` with a `sovrenn_discovery_insights` block. |

### 2026-09-02 — round 2 (user asked to try more)

Captured the full "Excellent Results (Jun-26)" bucket text: page 1 (50 rows, Aug-dated),
page 2 (50 rows, Jul-dated), page 4 (4 rows, 1–3 Jul). Page 3 renders a duplicate of page 2
(Sovrenn pagination bug) so ~50 mid-July rows couldn't be captured. All rows name-masked;
identification is by fingerprint (2-decimal mcap / PE, exact quarterly revenue & PAT
transitions, named counterparties, "highest-ever" phrasings) + web search.

**Confirmed and seeded `source: "sovrenn-discovery"` (3):**

| slug | fingerprint used | note |
|---|---|---|
| `netweb-technologies` — **Netweb Technologies India Ltd** | p2: ₹29,196 Cr mcap, 111.9x PE, Q1FY27 rev ₹301→820 Cr (+172%), PAT ₹30→85 Cr (+183%) → "Q1FY27 172% revenue" web search | India full-stack AI/HPC/private-cloud server maker (Tyrone). AI ~62% of Q1FY27 rev (+484% YoY); order book+L1+pipeline ~₹4,400 Cr. **Large-cap at ~112x** — deep read must judge whether a multi-bagger is still on the table from here or it's a max-returns-ranking-only name. |
| `hi-tech-pipes` — **Hi-Tech Pipes Ltd** | p4: ₹1,619 Cr mcap, 21.3x PE, "highest-ever quarterly sales volume **1,56,136 MT** +26% YoY" → exact-tonnage web search | ERW steel pipes / structural steel. Q1FY27 rev ~₹1,413 Cr (+79%); crossed 1M TPA capacity (Sikandrabad Unit-III), roadmap 2M TPA by FY29, FY27 volume guide 6.5–7 lakh MT, next-1M-TPA capex ~₹650 Cr. Volume-led compounder — margin/tonne + leverage during capex are the swing factors. |
| `bhadora-industries` — **Bhadora Industries Ltd** | p2: ₹168 Cr mcap, 16.9x PE, cables, Q1FY27 net sales "+226% YoY to ₹45 Cr from ₹14 Cr", "integrated cable manufacturing facility" → phrase web search | Cable & wire manufacturing **microcap**. Q1FY27 net sales ₹13.9→45.3 Cr (+226%) on mix + realisations; expanding into value-added / specialised cables + integrated facility. Power-infra / renewables / DC / EV cable tailwind (matches an `active_themes.json` theme). Very small base — verify durability + capex funding. |

**Already researched — note only (1):** `pngs-gargi-fashion-jewellery` (p2: ₹577 Cr, 18.6x,
jewellery, Akshaya Tritiya + EBO) → `sovrenn_news[]` entry: Q1FY27 rev ₹30.48 Cr (+11.6%),
EBO sales +186% YoY (now ~22% of rev), Akshaya Tritiya rev +77%. Corroborates the existing
Low / 10x call; not a re-verification trigger.

**Already excluded — re-verification flagged (1):** `v-marc-india` (excluded, trusted-thread)
→ `conviction_needs_reverification: true`, `last_analyzed_date` cleared. Q1FY27 (Jul-2026):
revenue +102% YoY, PAT +163% YoY to ~₹28.5 Cr. Wire & cable maker (Uttarakhand, largely
DISCOM supply). Identified via a fuzzy web-search match rather than a clean masked-row map,
but the Q1FY27 beat is independently real and large vs the excluded / "neither" call, so the
tier-2 re-check is warranted regardless.

**Not identified:** the bulk of the bucket. Rows using the plain result template
("Sales up X% YoY from ₹A Cr to ₹B Cr…") with no unique counterparty / tonnage / "highest-ever"
hook are not safely resolvable by search, and a large share are mid/large caps (₹4,000–70,000 Cr)
outside the microcap intent anyway. Not seeding guesses.

Backup for this round: `state.json.bak-20260902-sovrenn-discovery`. Registry 599→604.

**Pipeline wiring:** tier 4.65 selector widened to `source:sovrenn-news OR source:sovrenn-discovery`;
SKILL.md tier note updated to mention `sovrenn_discovery_insights`; `audit_state.py` backlog
check widened to both sources. Everything else flows as for the sovrenn-news batch.

**If a Sovrenn login becomes available:** paste any bucket's company list as text (the way the
WhatsApp digest was supplied) and it can be processed the same way — cross-checked against
`state.json` and seeded under `source: "sovrenn-discovery"`.
