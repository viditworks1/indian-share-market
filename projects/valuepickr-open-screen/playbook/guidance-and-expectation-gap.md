# Guidance → Commitment Chain → Expectation Gap

**Source (exception to the usual playbook attribution rule):** this entry is *not* pulled
from a trusted ValuePickr thread. It is the method laid out in the external research report
**"Near 52W Highs & Guidance"** by *Saurav | Orbit Research* (63 pp., circulated Aug 2026,
covering 60 India-listed mid/small caps near 52-week highs). It earns a place here because
it fills a real hole in our pipeline: we rank *business quality* and *who is bullish*, but we
have no structured way to ask **"what does the current price already assume, and is our
number materially different — with evidence?"** The 60-company stock list in the report is
mostly out of our size scope; the 8-step *method* is the value, and it is written up below as
house doctrine.

**One-line premise:** a good business is not automatically a good stock; strong guidance is
not automatically an earnings surprise; strong earnings growth is not automatically a good
investment. The opportunity is
`Gap × Evidence × Catalyst × Timing × Risk` — not the size of the guidance.

---

## Where this sits in our funnel

```
trusted signal / 52W-high breakout        →  DISCOVERY        (vpscreen-scan, vpscreen-portfolio-threads)
fundamentals quality gate (ROCE/growth/debt/red flags)  →  QUALITY GATE     (vpscreen-scan)
commitment chain + expectation gap        →  EDGE TEST        (deepdive-top100 → new schema blocks)   ← THIS DOC
30-week EMA weekly cross                   →  ENTRY TIMING     (portfolio-rs1l-revision)
```

`conviction_score` (0-100) answers *"is this a good business trusted people like?"* and is
deliberately left as-is. This method produces a second, orthogonal signal —
`expectation_gap_score` (0-100), built in Phase 3 — that answers *"is it mispriced, with a
catalyst?"* A portfolio add should score well on **both**. A quality name whose gap is
`priced-in` with no evidenced edge is a watchlist name, not a buy — the same treatment the
portfolio doc already gives a name >40% above its 30W EMA.

Note the method does not fight our technical discipline: "near 52W highs" is already
hitesh2710's breakout-discovery filter and is consistent with trading above the 30W EMA.
It slots in between the quality gate and the entry-timing check.

---

## The 8 steps

### Step 1 — Decode the commitments

Convert every management statement (concall, MD&A, exchange filing) from prose into a common
structure: **Company → Commitment → Specifics → Timeline**. Force nothing; capture only what
management actually said.

Classify each commitment into one of **8 buckets**:

| Bucket | Examples |
|---|---|
| `growth` | revenue / volume growth, order inflow, segment growth, market-share |
| `capacity` | new capacity, plant commissioning, debottlenecking, utilisation, ramp-up |
| `orders` | order book, new orders, customer qualification, new customer/product, commercial supply |
| `margin` | EBITDA margin, PAT, ROCE, cost reduction, operating leverage, breakeven |
| `capex` | new plant, capacity expansion, equipment, R&D, backward integration |
| `balance_sheet` | debt reduction, working capital, OCF/FCF, interest cost, fundraising |
| `strategy` | JV, M&A, demerger, new geography, new vertical, product-mix / business-model change |
| `new_business` | a distinct new revenue stream moving toward commercialisation |

Output in our system: the `commitments[]` array on `data/<slug>.json`
(see `scripts/GUIDANCE_EXPECTATION_SCHEMA.md`).

### Step 2 — Classify and connect into chains

Stop looking company-by-company. Look across the bucket, and connect commitments that belong
to the same **economic chain**. The canonical chains:

```
Demand:          orders → capacity expansion → higher utilisation → production → revenue
New product:     customer qualification → commercial supply → volume ramp → revenue → margin → PAT
Existing plant:  higher utilisation → operating leverage → EBITDA margin → PAT
Deleverage:      revenue growth → better cash generation → debt reduction → lower interest → higher PAT / FCF
```

A company where **multiple commitments are connected** (`orders → capacity → utilisation →
revenue → EBITDA`) is a stronger setup than one making a single isolated claim ("we expect
20% growth"). Also look for **clusters of change** — the same chain appearing across many
companies at once (e.g. data-centre demand showing up in Diamond Power, Inox India, Sterlite,
KRN Heat Exchanger simultaneously) — that is a theme, and corroboration across unrelated
concalls is a real signal (same logic as our multi-trusted-user corroboration bonus).

Output: `earnings_chain` on `data/<slug>.json` — the connected sequence plus the one link
that is the bottleneck.

### Step 3 — Grade commitment quality

The core discipline. Not every commitment carries equal weight. Move each one along a
**5-stage ladder** — the further right, the less you are relying on management's words:

| Stage | Ordinal | Meaning | Evidence in filings |
|---|---|---|---|
| `expectation` | 1 | management says it will happen | growth guidance, a target, an "aspiration" |
| `action` | 2 | capital / resources committed, a concrete step taken | capex raised, order placed, approval filed |
| `operational` | 3 | the capacity / process / product is becoming operational | plant commissioned on a dated schedule, line running |
| `commercial` | 4 | a customer / order / commercial activity validates demand | order booked, first shipment, programme won |
| `financial` | 5 | the change is already visible in revenue / EBITDA / PAT / cash | delivered in a reported quarter |

Two rules:
- **One company holds several stages at once.** ASK Automotive (the report's running
  example): revenue-growth guidance = `expectation`; ₹700cr FY27 capex = `action`; Karoli
  utilisation to ~80% = `operational`; Japan alloy-wheel orders ₹70-90cr = `commercial`;
  13.5-14% EBITDA target = `financial` (target). Tag the *thesis-critical* commitment, and
  note which parts are already proven vs. still to happen.
- **"Already delivered" beats "future financial target."** India Glycols having *already*
  booked ₹120cr of a >₹500cr FY27 Spirits-EBITDA aspiration in Q1 is stronger than a company
  merely guiding to a future margin.

Output: `quality_stage` on each `commitments[]` entry; `evidence_quality` on
`market_expectation` is derived from the furthest-right stage backing the thesis.

### Step 4 — Put it on a timeline

Bucket each commitment by when it can move the financials: `3M` / `6M` / `12M` / `FY27` /
`FY28`. The question is not "record dates" — it is **when does today's commitment become
tomorrow's earnings?**

The strongest setup is where **several milestones cluster in the same window** (order +
capacity + utilisation + revenue all landing within 6-12 months). Two companies can have the
same long-term opportunity and completely different stock setups: one inflects next quarter,
the other needs two years.

Output: `timeline_bucket` on each `commitments[]` entry; `catalyst.expected_window_months`
for the thesis-critical one.

### Step 5 — Bridge the commitment to earnings

Follow the money: **Revenue → EBITDA → PAT → FCF.** Do not stop at "capacity is increasing"
or "orders are strong."

- **Revenue:** which commitments create *incremental* revenue (new orders, new capacity,
  higher utilisation, new product, higher ₹-content)?
- **EBITDA:** how much of that revenue drops through? Look for **operating leverage** —
  EBITDA growing *faster* than revenue via utilisation, mix, premiumisation. A company
  growing revenue 20% with flat margins is a different animal from one growing 20% with
  margins expanding.
- **PAT:** does the EBITDA reach PAT, or is it eaten by interest / depreciation? This is
  where balance-sheet commitments (deleveraging → lower interest) matter.
- **FCF:** does PAT become cash, or does working capital / capex absorb it? `PAT growth ≠
  FCF growth` — a heavy-capex or working-capital-intensive ramp can grow PAT and consume
  cash.

Output: `earnings_chain` records which links are evidenced and which are assumed; the more
links backed by Step-3 `commercial`/`financial` evidence, the stronger the case.

### Step 6 — Find the single point of failure

Work backwards: **what has to go right for the earnings case to work, and where can the
chain break?** Structure: `Dependency → Bottleneck → Execution Risk`.

- **Dependency:** what does the commitment rely on? (capacity depends on customer approvals;
  orders depend on timely commissioning; new product depends on qualification)
- **Bottleneck:** what physically or commercially limits the growth? (capacity, qualification,
  raw materials, technology, people, working capital, order conversion, utilisation,
  regulatory approval, commissioning)
- **Execution risk:** even if the dependency is available, can management deliver on time and
  at the expected economics? (project delays, cost overruns, slow utilisation ramp, customer
  delays, lower-than-expected orders, margin pressure, working-capital build, integration
  problems, debt/capex pressure)

Then name the **one critical point of failure** per earnings driver — the single thing to
monitor. A large opportunity with a fragile chain does not automatically rank highly. A
company with **multiple independent growth drivers** (so one failure doesn't kill the thesis)
is more robust than one with a single point of failure.

Output: `dependency` and `single_point_of_failure` on each `commitments[]` entry; feeds the
`risk` term of `expectation_gap_score`.

### Step 7 — Compare with market expectation

The step our pipeline is completely missing. Before looking for an opportunity, understand
what the current valuation already assumes.

- Look at: current price, market cap, current earnings, current multiple (P/E, EV/EBITDA,
  P/B — **pick the right tool for the business**, per phreakv6 in `screening-methodology.md`),
  and any visible FY27/FY28 expectation.
- **Reverse-engineer the stock:** don't ask "will this company grow?" Ask "**how much growth
  is the current price already assuming?**" — i.e. what EPS CAGR / margin / duration does
  today's multiple require.
- Compare *our* earnings path (Steps 1-6) with that implied path, and classify:

| `gap_direction` | Meaning |
|---|---|
| `priced-in` | our path ≈ the implied path — business can perform well, stock may not |
| `partially-priced` | market sees part of it; our work suggests our earnings > market earnings — investigate |
| `underestimated` | our path is materially *better* than what the price appears to require |
| `over-optimistic` | our path is *below* what the price requires — the company can still grow and the stock still disappoints |

Three kinds of gap:
- **Timing gap** — both agree on the size, disagree on *when* (market says FY28 contribution,
  our evidence says FY27 commercialisation). Earnings arriving early can move estimates up
  before the long-term story changes.
- **Magnitude gap** — agree on timing, disagree on *size* (market FY28 PAT ₹100cr, our
  estimate ₹130cr) — must have a business reason and evidence behind it.
- **Duration gap** — market expects growth to slow (FY27 growth → FY28 normalisation), our
  evidence suggests another leg (FY27 growth → FY28 capacity ramp → FY29 second growth leg).

> **Our data constraint:** we have no broker consensus (Yahoo Finance + screener.in only).
> Approximate the implied path with a reverse-P/E ("what EPS CAGR justifies today's multiple
> at a normal exit multiple?"), screener.in's own forward figures where shown, and the VP
> thread's stated consensus. This is **directional, not precise** — and that is acceptable,
> because Step 8 ranks on evidence / catalyst / timing quality, not on the exact gap number.

Output: the `market_expectation` block on `data/<slug>.json`.

### Step 8 — Find and rank the expectation gap

`Our Earnings − Market Earnings = Expectation Gap`. But a number is not enough — classify
*why* the gap exists and *what evidence* supports it.

**Gap type** (`gap_type`): `volume` | `capacity` | `mix` | `margin` | `timing` | `duration`
| `new_business`.

**Is it a real gap or an assumption gap?** — evidence quality of the gap itself:

| What the gap rests on | `evidence_quality` | Read |
|---|---|---|
| management commitment + operational progress | `strong` | act on it |
| orders + capacity + customer validation | `strong` | act on it |
| capacity planned but not started | `monitor` | needs monitoring |
| new product without customer qualification | `weak` | higher uncertainty |
| management aspiration only | `weak` | weak |
| our assumption with no evidence | `none` | do not rely on it |

**Find the catalyst** — the specific event that makes the market re-recognise the gap
(order win, capacity commissioning, customer qualification, commercial production, utilisation
step-up, margin print, acquisition consolidation, product launch, debt reduction, a quarterly
earnings beat), with a time window.

**Rank by opportunity quality, not gap size:**

| | Earnings Gap | Evidence | Catalyst | Timing | Risk | Overall |
|---|---|---|---|---|---|---|
| A | Large | Strong | Clear | 6M | Low | **High** |
| B | Large | Medium | Clear | 12M | Medium | **High** |
| C | Medium | Strong | Very clear | 3-6M | Low | **High** |
| D | Large | Weak | Unclear | 12M+ | High | **Low** |

The largest theoretical earnings upside (row D) is *not* the pick. The pick is a meaningful
gap where the evidence is already visible, the catalyst is approaching, timing is 6-12
months, and the single point of failure is acceptable.

Output: `catalyst` block + the inputs to `expectation_gap_score` (Phase 3).

---

## How this changes our ranking (built)

`expectation_gap_score` (0-100) — mechanical, deterministic, recomputed every
`vpscreen-rerank` cycle by `scripts/compute_expectation_gap_score.py`:

```
gap_frac = gap_points/40   gap_points: underestimated 28 / partially-priced 18 / priced-in 4
                           / over-optimistic 0 ; + up to 12 for |gap_magnitude_pct|

quality  = 0.35·evidence_q + 0.30·catalyst_q + 0.20·timing_q + 0.15·risk_q   (each 0–1)
             evidence_q  strong 1 / moderate .75 / monitor .5 / weak .25 / none .05
             catalyst_q  high 1 / med .65 / low .35 ; ×0.6 if undated ; ×0 if lapsed ; .15 if none
             timing_q    ≤6M 1 / ≤12M .75 / ≤18M .45 / >18M .25
             risk_q      0 open SPOF 1 / 1 → .65 / 2 → .40 / 3+ → .20  (+.15 if ≥2 evidenced links & ≤1 SPOF)

expectation_gap_score = clamp(gap_frac · quality · 100, 0, 100)
                        ×0.5 if HIGH CAUTION ; 0 if AVOID/EXCLUDE ; 0 if over-optimistic
```

A weighted-average `quality` (not a product of sub-1.0 factors) so the range is genuinely
used — a strong setup approaches 100, a weak one sits near 0. Full detail:
`scripts/GUIDANCE_EXPECTATION_SCHEMA.md`.

`docs/00d_EXPECTATION_GAP_RANKING.docx` (rebuilt by `vpscreen-rerank` every cycle) has three
sections: **ranked** by score; **"no current edge"** — good businesses whose gap is
`priced-in` / `over-optimistic` / catalyst lapsed (the Aeroflex/Novartis case, now systematic
instead of ad hoc); and **"not yet guidance-assessed"** — researched names not yet covered,
ordered by `conviction_score`.

**Phase 4 (built):**
- **Coverage:** `deepdive-top100` writes the blocks for the top-100 max-returns names on its
  deep pass; the `guidance-backfill` task (2×/day, 4/run) does a *lighter* guidance-only pass
  for every other tier-A/B name (`conviction_score ≥ 35`, no red flag, thesis ≠ neither) so
  the portfolio-relevant universe gets an `expectation_gap_score` in ~10 days rather than
  waiting on the deep crawl. Deep pass overwrites light blocks when it catches up.
- **Portfolio gate:** `portfolio-rs1l-revision` adds a name to HOLDINGS only if it clears
  **both** `conviction_score ≥ 60` **and** `expectation_gap_score ≥ 30` with no
  `no-edge`/`priced-in`/`over-optimistic`/`catalyst-lapsed` flag. Clears conviction but not
  the gap → WATCHLIST, annotated "quality name, guidance already priced — no current edge".
  Never a sell trigger for an existing holding; a holding whose gap decays gets a "hold,
  don't add — edge has closed" note.
- **Catalyst calendar:** `compute_expectation_gap_score.py` emits `catalyst_calendar` and
  `regen_lists.py` renders it as a dated **"## Catalyst calendar"** section (Overdue / Upcoming)
  at the bottom of `revisit-list.md`. A holding past its catalyst date with status still
  `pending` is a re-underwrite prompt.

---

## Checklist (per deep-dived stock)

1. Every material guidance statement decoded into `commitments[]` with a bucket.
2. Commitments connected into `earnings_chain`; bottleneck link named.
3. Each commitment graded `expectation` → `financial`; thesis-critical one identified.
4. Each commitment given a `timeline_bucket`; milestone cluster window noted.
5. Revenue → EBITDA → PAT → FCF bridge written; operating-leverage check done.
6. `dependency` + `single_point_of_failure` named per driver.
7. `market_expectation`: implied path estimated, `gap_direction` + `gap_type` + magnitude set.
8. `catalyst`: event + window + evidence quality set.
