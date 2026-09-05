# ValuePickr Open Screen (new project, 2026-08-21)

Separate from, and does not read/write/overwrite, the original 108-stock project
(`../research/`, `../docs/00_FINAL_RANKING.docx`, `../docs/00b_PORTFOLIO_Rs1L_Allocation.docx`).
That project screened a pre-curated ~108-name list. This one screens broadly across
India-listed companies, with ValuePickr used as a secondary, confirming data source rather
than the discovery mechanism (see "Discovery" below — this changed on 2026-08-21).

## Thesis (differs from the old project — read carefully)
- **No market-cap ceiling.** Any company is eligible as long as there's a plausible case for
  **10x in 2-3 years OR 100x in 10 years**. The larger the company, the higher the bar for
  that claim — a mega-cap needs an extraordinary, specific catalyst, not just "good business."
- **India-listed only** (foreign names like BlackBerry/Nokia are out of scope).
- **Quality gate:** ROCE/ROE strength, real (not cosmetic) revenue/profit growth, manageable debt.
- **Red-flag tiers** (explicit, not silently dropped): **AVOID** (negative net worth /
  going-concern doubts), **HIGH CAUTION** (sharp unexplained promoter-holding collapse),
  **EXCLUDE** (active SEBI/regulatory action).
- **Technicals:** weekly/monthly MACD + Bollinger Bands where obtainable; RSI/CCI/Williams %R
  extremity as a documented proxy otherwise, via TradingView's `/technicals/` tab — but this
  is now a rare escalation path (capped 2 browser sessions/run), not a default step; most
  stocks get their trend read cheaply from the fundamentals WebSearch snippet.
- **ValuePickr community conviction** is a qualitative signal, never the sole basis. Tracks
  which forum users get the most love/like reactions (Discourse action id=2, the heart icon)
  in `users.json` / `top-contributors.md`. A high-conviction call from a ranked contributor is
  noted (`community_signal` field), but fundamentals still decide the tier.

## Past-performance bias found and fixed (2026-08-22)
An audit found a systematic bias: stocks with a real, specific catalyst and a confirmed or
plausible RECENT-QUARTER inflection were being marked `thesis_fit: "neither"` purely because
a TRAILING 3-5yr average metric looked weak — which is definitionally true of any inflection
story, since the average is diluted by the pre-inflection period. Smoking-gun example:
Ujjivan Small Finance Bank (PAT +207% YoY, current ROE/ROCE already healthy at 14.35%/13.89%,
near 52-week high) was sitting in `screenedOut` rather than even Tier C, while Rain
Industries — a near-identical setup, also weak on trailing average — had correctly landed in
Tier C. The methodology could handle it right, just wasn't applied consistently.

Fixed: 6 stocks (Ujjivan SFB, Deep Industries, Ugro Capital, Borosil Renewables, Satin
Creditcare, Arman Financial) moved from `screenedOut` to Tier C with explicit "unconfirmed,
watch for 1-2 more quarters" framing — NOT upgraded to high conviction, this is about
visibility for monitoring, not premature confidence. Genuinely large-cap `"neither"` calls
(HDFC Bank, Manappuram Finance, etc.) are unaffected — a catalyst doesn't change that an
already-too-large company stays too large; that's legitimate size math, not a
trailing-average artifact. `vpscreen-scan`'s thesis-fit rule now explicitly requires judging
small/mid-cap names on recent-quarter trend + catalyst credibility, not the trailing average
alone. `audit_state.py` now has a mechanical (heuristic, report-only) spot-check for
`screenedOut` entries whose own reason names a catalyst without being size-gated, so this
doesn't silently recur.

## Discovery + filter funnel (current design, finalized 2026-08-22)
Went through two iterations before landing here:
1. Original: paged ValuePickr's forum categories, prioritized by reply count. Structurally
   favored already-huge, already-priced legacy threads (HDFC Bank, Laurus Labs, IDFC First
   Bank all have thousands of replies and correctly came back "neither") — high research
   cost, low hit rate for genuinely new names. User rejected this.
2. Web/news-first: discovery moved to rotating WebSearch themes, VP checked per-candidate
   only afterward. Worked, but the user then asked to flip discovery back to VP while
   keeping the reply-count fix.
3. **Current**: **discovery is ValuePickr-forum-first again** (`scripts/discover.py`), but
   its priority sort no longer uses reply count — material-news-flag first, then plain
   *recency* (most-recently-active thread first), a neutral signal that doesn't
   systematically favor big legacy threads. Then **web/news is a cheap preliminary filter**:
   one fundamentals WebSearch per candidate decides whether it's worth going further. Only
   survivors (AVOID/EXCLUDE-free, and not obviously failing the quality gate on weak
   fundamentals) get the expensive adaptive deep ValuePickr-thread read (see below).
   HIGH CAUTION stocks are a deliberate exception — they still get the deep read, since
   community discussion is specifically useful for understanding what's driving a
   promoter-holding concern. The 8-theme web-search rotation from iteration 2 is retired.

## The 30-day gate
A stock already analyzed within the last 30 days isn't re-analyzed (cooldown), tracked via
`state.json`'s `last_analyzed_date` and enforced by the scan task itself each run (previously
enforced by `discover.py`; same rule, now checked at candidate-selection time since discovery
no longer flows through that script).

## Files
- `state.json` — the stock registry: slug → name, VP topic id (if a thread was found),
  `status`, `conviction`, `red_flag_tier`, `thesis_fit`, `market_cap_tier`, `notes_short`,
  `revisit_after_30d`, `last_analyzed_date`. Also `meta.discovery_theme_index` (rotation
  state) and `meta.last_ranking_date` (rerank gate).
- `users.json` — community reputation registry (love/like counts per username), built
  incrementally from posts actually read during research.
- `analysis.md` — append-only per-stock findings log.
- `audit-log.md` — append-only daily self-audit log (see "Automated audit" below).
- `top-contributors.md`, `skip-list.md`, `revisit-list.md` — mechanically regenerated views,
  never hand-edited.
- `data/*.json` — per-stock structured data feeding the docx generator, plus
  `data/screen-ranking.json` (tiers + structured `screenedOut` list), `data/portfolio.json`
  (created once the first real allocation is built), and `data/max-returns-ranking.json`
  (see "Two rankings" below).
- `docs/*.docx` — per-stock docs, `00_SCREEN_RANKING.docx` (thesis-gated),
  `00c_MAX_RETURNS_RANKING.docx` (criteria-free hedge — see below), `00b_PORTFOLIO.docx`,
  `00d_EXPECTATION_GAP_RANKING.docx` (guidance-gap ranking — see "Expectation-gap layer" below).

## Two rankings, on purpose (added 2026-08-21)
The main screen gates on a strict thesis: 10x in 2-3 years OR 100x in 10 years. The user
explicitly asked for a hedge against that bar being too strict and quietly excluding real
opportunities — so `vpscreen-rerank` now maintains a SECOND, criteria-free ranking every run:
**`docs/00c_MAX_RETURNS_RANKING.docx`** — every researched stock, ranked by conviction alone,
no thesis-fit filter. Fully mechanical (`scripts/build_max_returns_ranking.py` +
`scripts/make_max_returns_ranking.js`, zero LLM judgment needed — `state.json` already has
everything required). Red-flagged stocks (AVOID/HIGH CAUTION/EXCLUDE) are still kept in a
separate, clearly labeled section even here — a solvency/regulatory red flag isn't a
return-potential debate. Cross-check this against the main ranking: a stock ranked highly
here but absent from `00_SCREEN_RANKING.docx`'s tiers is exactly the case this doc exists
to catch (e.g. Manappuram Finance, Natco Pharma — solid "Medium" conviction, but "neither"
thesis fit since they're too large to plausibly 10x).

## Expectation-gap layer (added 2026-08-30)
A third axis alongside the two rankings above, from the Orbit Research "Near 52W Highs &
Guidance" method — full doctrine in `playbook/guidance-and-expectation-gap.md`, data contract
in `scripts/GUIDANCE_EXPECTATION_SCHEMA.md`. `conviction_score` answers "good business, backed
by trusted people?"; this answers "mispriced, with a catalyst, on acceptable risk?" — the two
are kept as separate numbers, never blended.
- `deepdive-top100` (deep) and `guidance-backfill` (light, 2×/day, 4/run, conviction order
  — covers tier-A/B names the deep crawl won't reach for weeks) write four optional blocks
  onto `data/<slug>.json` — `commitments[]` (guidance decoded + graded on an
  expectation→action→operational→commercial→financial ladder), `earnings_chain`,
  `market_expectation` (what the price implies vs. our path, via reverse-P/E — no broker
  consensus), `catalyst`. Old files without them stay valid.
  Backfill queue: `scripts/build_guidance_backfill_queue.py` → `data/guidance-backfill-queue.json`;
  bookkeeping: `scripts/guidance_backfill_apply.py`.
- `scripts/compute_expectation_gap_score.py` — mechanical 0-100 `expectation_gap_score`
  (`gap_frac × quality`, where quality = weighted avg of evidence/catalyst/timing/risk).
  Writes `state.json` + `data/expectation-gap-scores.json` (`ranked` / `no_edge` /
  `not_assessed` / `catalyst_calendar`). Deterministic, no network; a catalyst window can
  lapse with time alone.
- `scripts/make_expectation_gap_ranking.js` → `docs/00d_EXPECTATION_GAP_RANKING.docx`. The
  "no current edge" section is the systematic version of "great business, already priced" —
  the Aeroflex/Novartis case. `vpscreen-rerank` runs both every cycle (Steps 2 + 5.5).
- `regen_lists.py` appends a dated **"## Catalyst calendar"** section (Overdue / Upcoming) to
  `revisit-list.md` from `catalyst_calendar`.
- `portfolio-rs1l-revision` gates new HOLDINGS adds on BOTH `conviction_score ≥ 60` and
  `expectation_gap_score ≥ 30` (no `no-edge`/`priced-in`/`over-optimistic`/`catalyst-lapsed`
  flag); conviction-only names go to the watchlist. Never a sell trigger.

## Scripts
- `scripts/discover.py` — the original VP-category-pager, kept but not currently called by
  `vpscreen-scan` (see "Discovery" above).
- `scripts/regen_lists.py`, `scripts/extract_recent.py`, `scripts/regen_user_ranking.py` —
  mechanical regenerators.
- `scripts/audit_state.py [--dry-run]` — mechanical `state.json` hygiene: normalizes stray
  `status` values, auto-fixes `revisit_after_30d` violations (exact 3-part rule), flags
  (never guesses) bad `thesis_fit` values and duplicate `topic_id` registrations, flags
  `screen-ranking.json` structural contradictions.
- `scripts/audit_permissions.py [--dry-run]` — removes `.claude/settings.local.json` allow
  rules already fully covered by an existing wildcard in the same file. Pure cleanup, never
  widens what's actually permitted.
- `scripts/make_stock_doc.js <data.json> <out.docx>`, `make_final_ranking.js`,
  `make_portfolio.js`, `make_max_returns_ranking.js`, `make_expectation_gap_ranking.js` —
  docx generators (reuse the `docx` npm package via a read-only relative `require` into the
  original project's `node_modules`).
- `scripts/compute_conviction_score.py`, `scripts/compute_expectation_gap_score.py` —
  the two mechanical 0-100 scores; both pure functions of `state.json` + `data/<slug>.json`,
  no LLM, no network. See `CONVICTION_SCORE_METHODOLOGY.md` / `GUIDANCE_EXPECTATION_SCHEMA.md`.

## Automated audit (new 2026-08-21)
`vpscreen-audit` runs daily (11pm), after that day's scan/rerank activity: runs both audit
scripts, does a few judgment-only checks scripts can't do (rate-limit-pacing compliance
spot-check, a small cross-project-duplicate spot-check), and appends a short entry to
`audit-log.md`. It's scoped to data hygiene only — it never edits another scheduled task's
prompt; that stays a human-reviewed change.

## Deep thread reads, adaptive depth (redesigned 2026-08-22)
Per-stock community context used to be a single most-recent post. Now `vpscreen-scan` reads
a thread's MOST RECENT posts (the post-ID stream is chronological, so the tail = most
recent — explicitly verified, not just assumed) starting with a base batch of 50 — but
efficiently: 1 request for the topic JSON (gets the post-ID stream) + 1 bulk request
(`/t/<id>/posts.json?post_ids[]=...`, all IDs at once) = 2 requests for 50 full posts, not
50 separate rate-limited calls.

50 is a floor, not a ceiling. After the base batch, the task judges whether the discussion
shows BUILDING conviction (converging posters, rising reactions, a live unresolved debate,
a trusted-user post referencing context not yet read) — if so, it fetches the next older
50-post batch the same way, and can keep escalating while the signal justifies it, up to a
firm ceiling of 200 posts (4 batches) per stock. Most stocks won't escalate past the base
batch; this is specifically for threads where something is visibly, actively developing.

`vpscreen-portfolio-threads` uses the same bulk-fetch pattern for its incremental thread
reads. This depth is what actually makes the trusted-user system below viable — with
1-post sampling almost nobody was ever seen twice; deeper reads naturally re-encounter the
same posters across threads.

## Trusted users, not just trusted threads (generalized 2026-08-22)
Phreak (`phreakv6`) was the seed, explicitly named by the user. `trusted_users.json` is now
the general roster — anyone on it gets the conviction-bump privilege wherever they post
(their own thread, a company thread, anywhere), not just a specific named thread.
`scripts/promote_trusted_users.py` mechanically promotes anyone in `users.json` who clears
`total_love >= 15` AND `posts_seen >= 3` (both scan and portfolio-threads tasks run this
after gathering new data). When someone is newly promoted, `vpscreen-portfolio-threads`
looks for their own portfolio thread (`search.json?q=<username>`, cap 2/run) and starts
tracking it incrementally if substantial (`reply_count >= 20`) — this is the "find similar
users and threads" mechanism, distinct from and complementary to the title-pattern thread
discovery that already existed.

## Conviction STRENGTH tiers + guaranteed evaluation (2026-08-22)
Not every trusted mention is equal — "primary holding" is a different signal than "small
position I'm tracking." Added `trusted_conviction_strength` (`"very-high"` or `"high"`) to
the per-stock schema, classified when `vpscreen-portfolio-threads` finds a mention:
- **`very-high`**: explicit primacy language ("primary/core holding", "highest conviction",
  "largest position"), a stated portfolio % ≥20%, OR the same user naming the same stock
  with qualifying language for the 2nd+ time (sustained conviction across posts).
- **`high`** (default): any other qualifying mention — single, smaller, "tracking," a
  trading bet.

What each tier gets:
- **Queue priority**: `vpscreen-scan`'s Step 0.5 is now UNCAPPED for trusted-thread
  candidates (was capped at 5/run) — it takes ALL of them into the batch, `very-high` first,
  up to the full 15-stock cap, before falling back to web discovery. This is the literal
  mechanism for "every name a trusted user recommends gets evaluated," not just a sample.
- **Filter override**: a `very-high` candidate proceeds to the deep VP-thread read
  UNCONDITIONALLY (skips the usual weak-fundamentals filter) — a red flag still disqualifies
  it, but a mediocre trailing average doesn't, since the trusted signal IS the reason to look
  deeper.
- **Deeper read by default**: a `very-high` candidate escalates to at least 100 posts (Batch
  2) without waiting for the normal "is conviction building" heuristic to justify it.
- **Conviction floor**: a `very-high` candidate with no red flag gets conviction set to AT
  LEAST `"Medium-High"` regardless of what a fundamentals-only read would suggest — the
  sustained trusted endorsement is a real input, not a tiebreaker. Only genuine research
  quality pushes it higher, to `"High"`. `high`-tier candidates get no floor, assessed
  normally.
- `audit_state.py` flags any `very-high` candidate still unresearched as URGENT (this
  shouldn't persist, given the uncapped queue) and `vpscreen-audit` checks whether
  `vpscreen-scan` has actually run recently if it does.

Retroactively applied to the stocks found in the thread-history-backfill above: Sai Life
Sciences, Aeroflex Industries, Mtar Technologies, TD Power Systems tagged `very-high`
(sustained core-holding language across many posts); Yash Highvoltage, Kitex Garments,
Aimtron Electronics tagged `high` (single, smaller-position mentions).

## We weren't reading thread HISTORY — found and fixed (2026-08-22)
A direct, full read of Phreak's entire 298-post thread (not the usual incremental slice)
found his real sustained core holdings — Sai Life Sciences, Aeroflex Industries, Mtar
Technologies, TD Power Systems, named repeatedly across dozens of posts — were almost
entirely missing from `state.json`. Root cause: the incremental design only ever reads NEW
posts going forward from whenever tracking starts; it never backfills the history that
came before. Fixed:
- Manually backfilled the immediate gap: 3 new candidates added (Sai Life Sciences, Yash
  Highvoltage, Kitex Garments), 3 existing-but-untagged candidates retagged (Mtar
  Technologies, TD Power Systems, Aimtron Electronics), 4 missed high-conviction calls
  logged for phreakv6.
- Added a real historical backfill mechanism: `trusted_threads.json` entries now track
  `backfill_complete` + `backfill_progress_post_number`. A new Step 1 in
  `vpscreen-portfolio-threads` works backward in 100-post bulk-fetch batches (cap 2
  threads/run) until reaching post #1 or a 300-post depth cap (bounded — an 8,000+ post
  thread's full history isn't practical, but 300 back is real progress over 17). Phreak's
  thread is fully backfilled; the other 6 tracked threads are queued for upcoming runs.
- Made multi-stock extraction explicit — a single disclosure line often names several
  companies at once, and the prompt now says to extract every one, not just the first.

## Portfolio-thread pipeline hardened (2026-08-22)
- **Frequency raised 1x/day → 4x/day** (`0 7,11,15,19 * * *`).
- **Anti-repetition flag, made explicit and cheap**: at 4x/day, most checks on a given thread
  find nothing new. Step 1 now does a lightweight `search.json` check (just to read
  `highest_post_number`) BEFORE any heavy fetch; if nothing's new since
  `last_post_number_seen`, the thread costs exactly one small request and the run moves on —
  the full topic JSON + bulk post-fetch only happens when there's genuinely something to read.
- **Continuous updates, not one-time**: every trusted-conviction sighting appends a fresh
  `analysis.md` entry, even for a stock with prior entries — this is a running log, not a
  snapshot.
- **Individual stock docs now updated too, not just the running log**: when a trusted user's
  conviction lands on a stock that already has its own `data/<slug>.json` (i.e. already been
  through the main pipeline), that stock's `trusted_signals` array gets a new entry and its
  `.docx` is regenerated — the signal is visible in the stock's own document, in a dedicated
  "Trusted-User Signals (Ongoing)" section, not just buried in `analysis.md`. `vpscreen-scan`
  seeds this same array on first research if a trusted-user post turns up during the initial
  deep read, so it's one continuous record across both tasks.
- **Trust levels get revisited, not just assigned once**: `promote_trusted_users.py` now also
  syncs `trusted_threads.json` — an `"auto-discovered"` thread gets upgraded to
  `"user-trusted"` if its author has independently earned trust since. `vpscreen-audit` (see
  below) retries the "find their own thread" search for already-trusted users who came up
  empty the first time, capped 2/run, oldest-promoted first.

## Trusted portfolio/journal threads (added 2026-08-22)
Separate from company-thread analysis: ValuePickr has individual investors' running
"portfolio/journal" threads (e.g. "Phreak's Thoughts, Ideas and Opinions" — 298 posts, 6,542
likes, 139 participants) where the same small group of engaged, often highly-regarded
posters discuss many stocks over time. `vpscreen-portfolio-threads` reads these
incrementally (tracked via `trusted_threads.json`'s `last_post_number_seen`, up to 15 new
posts/thread/run), building real repeat-sighting user reputation data (the main pipeline's
one-post-per-company-thread sampling rarely sees the same poster twice). When the explicitly
user-trusted author (`phreakv6`, seeded from the user's own request) expresses clear
conviction on a stock, that stock's `conviction` gets bumped one notch (capped at High,
never for other posters, never more than one notch) and the call is logged in `users.json`
immediately (bypassing the normal 2-sightings gate for that one trusted author). New stocks
mentioned this way are queued into `state.json` with `source: "trusted-thread"`, which
`vpscreen-scan`'s Step 0.5 now drains first (up to 5/run) before its usual web-discovery
batch. The task also auto-discovers similar threads via title-pattern search, gated on the
candidate thread clearing `like_count >= 500` and `participant_count >= 20` before being
added at the lighter `"auto-discovered"` trust level (no conviction-bump privilege until a
human promotes it). Log: `portfolio-threads-log.md`.

## Scheduled tasks (all enabled and running)
- `vpscreen-scan` — 3x/day (`0 8,13,18 * * *`), up to 15 stocks/run (~45/day), trusted-thread
  candidates prioritized first.
- `vpscreen-rerank` — daily, updates both rankings + portfolio (once Tier A has ≥5 names).
- `vpscreen-audit` — daily (11pm), self-check and cleanup.
- `vpscreen-portfolio-threads` — daily (10:30am), reads trusted portfolio/journal threads.

Pace was increased 2026-08-21 (was 2x/day, 8/run) specifically to reach the portfolio's
≥5-Tier-A gate faster — at the prior ~1-Tier-A-per-16-researched hit rate that was going to
take close to a week; the web-first discovery redesign should also help by reducing how much
research budget goes to already-priced mega-caps.

## History
- 2026-08-21, first pass: bootstrapped via VP-category paging, ~335 candidates registered.
- 2026-08-21, second pass: rate-limit hardening + permission-wildcard fixes after the first
  live runs (see `audit-log.md` and memory for detail).
- 2026-08-21, third pass: full audit found and fixed several issues (empty contributor
  leaderboard, `revisit_after_30d` drift, prose-based screened-out list, a duplicate-research
  spend on Laurus Labs already covered by the old project).
- 2026-08-21, fourth pass (this one): discovery redesigned web/news-first per explicit user
  request, pace increased, automated daily audit job added.
- 2026-09-02: seeded the "Sovrenn Daily News" digest (Apr–Jun 2026 WhatsApp compilation the
  user supplied) — 25 new microcap/SME candidates `source: "sovrenn-news"` (new `vpscreen-scan`
  Step 0.5 tier 4.65: thin-thread names, research off quarterly/annual reports + exchange
  filings + news), 11 already-researched names re-flagged for re-verification, 7 note-only.
  Also checked sovrenn.com/discovery (paywalled — company names masked when logged out);
  reverse-identified 1 name from a unique remark fingerprint — Virtual Galaxy Infotech Ltd,
  `source: "sovrenn-discovery"` (tier 4.65). Full detail: `sovrenn-news-log.md`.
