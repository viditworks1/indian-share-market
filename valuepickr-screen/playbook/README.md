# Playbook — Learnings from Trusted ValuePickr Investors

Separate from `analysis.md` (per-stock research) and `portfolio-threads-log.md` (mechanical
run log of what was read/tagged). This is a themed knowledge base of general, reusable
investing wisdom pulled from trusted portfolio/journal threads — position sizing, risk
management, how to read a sector, investor psychology, screening methodology.

**Scope discipline:** entries here are *methodology and mindset*, not stock calls. A post
that says "I hold X at Y% of portfolio" belongs in `analysis.md`/`state.json` via the normal
trusted-thread pipeline, not here. A post that explains *why* the person sizes positions the
way they do, or how they think about admitting a thesis was wrong, belongs here.

**Two deliberate exceptions to "trusted VP threads only":**
- `guidance-and-expectation-gap.md` — sourced from an external research report (Orbit
  Research, "Near 52W Highs & Guidance", Aug 2026). It is the method backing the
  commitment-chain / expectation-gap layer (data contract:
  `../scripts/GUIDANCE_EXPECTATION_SCHEMA.md`).
- `ishmohit-soic-style.md` — distilled from 6 months of @ishmohit1 (SOIC) posts on X, scraped
  2026-08-30 at the user's request. It backs the `value_chain` / `earnings_quality` /
  `growth_trajectory` / `management_quality` blocks (data contract:
  `../scripts/ISHMOHIT_SIGNALS_SCHEMA.md`), the speed-breaker and large-cap-inflection rules
  in `vpscreen-scan`, the exit-confirmation rule in `portfolio-rs1l-revision`, and two
  scheduled tasks: `x-trusted-cluster` (weekly — @ishmohit1 + his X cluster) and
  `global-proxy-scan` (2×/week — bellwether global concalls → Indian proxies, config in
  `../global_bellwethers.json`).

Both files state the exception explicitly in their own header.

**Attribution discipline:** every entry cites `user (rank per top-contributors.md), thread,
post #, date`. No entry is written without a specific quoted or closely-paraphrased source —
this is a collection of falsifiable, attributed observations, not generic aphorisms. If a
"lesson" can't be traced to an actual post, it doesn't go in.

**Scope:** top-ranked users only (per `top-contributors.md`), since the premise is that
sustained community reputation is a signal the methodology is worth listening to — not proof
it's correct. Track record still matters more than eloquence; where a user's own words show a
strategy underperforming, that's noted alongside the technique, not filtered out.

## Files
- `position-sizing-and-risk.md` — allocation rules, stop-loss discipline, diversification philosophy
- `investor-psychology.md` — handling drawdowns, admitting mistakes, avoiding macro-driven panic
- `screening-methodology.md` — concrete, checkable screening/technical rules (momentum, stage analysis, fundamentals gates)
- `reading-a-sector.md` — sector-level pattern recognition and thesis-building approaches
- `guidance-and-expectation-gap.md` — the 8-step "decode guidance → build the commitment
  chain → grade its quality → compare to what the price assumes → rank the expectation gap"
  method (external source; see the exception note above). Data contract:
  `../scripts/GUIDANCE_EXPECTATION_SCHEMA.md`.
- `ishmohit-soic-style.md` — @ishmohit1 / SOIC investment & research style: TVGP, "unique
  businesses", value-chain PhD + supply-side, rate-of-change of growth, growth traps,
  peak-margin earnings quality, "speed breaker" buys, global-first → Indian proxy, index
  churn, plus his research inputs, themes, and temperament. Includes the full list of pipeline
  changes made from it (2026-08-30) and what's still only recommended. Data contract for the
  four signal blocks: `../scripts/ISHMOHIT_SIGNALS_SCHEMA.md`.

## Crawl state
`crawl_state.json` tracks which post range of each trusted thread has been mined for this
purpose specifically — independent of `../trusted_threads.json`'s `backfill_progress_post_number`,
which tracks the separate stock-signal-extraction pipeline. The two trackers intentionally do
not share state: a post can be relevant to one, both, or neither.
