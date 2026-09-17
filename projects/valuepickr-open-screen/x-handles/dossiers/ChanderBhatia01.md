```json
{
  "handle": "ChanderBhatia01",
  "scraped_date": "2026-09-13",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 8,
  "cadence": "low",
  "discloses_names": false,
  "disclaimer_pattern": "none",
  "calls": [],
  "watch_only_names": []
}
```

Account is low-cadence and, in the visible window, entirely off-topic for stock triage: posts are a mix of generic investing aphorisms ("never sell in panic and never buy in FOMO"), a eulogy-style note about a fund manager (Siddhartha Bhaiya, no specific fund/stock named), and a run of personal-health/fitness content (diet, protein intake, homocysteine/B12 supplementation) plus one civic complaint about Delhi waterlogging. One tweet gestures at a general strategy ("buy quality small caps and mid caps at 40-50% discount, allocate 5%... give companies multiple years") but names no specific company, so it doesn't seed anything under this pass's rules.

Search returned only 8 tweets spanning 2026-09-05 to 2026-09-11 before the scroll loop went stagnant (three consecutive scrolls with no new tweets loading) — X's live-search endpoint appears to have exhausted its index for this query well short of the full 2026-03-13 window, rather than the account being dormant for six months. This is a normal live-search truncation behavior, not a rate-limit/login-wall (page did not show an empty-state or block message; posts loaded and rendered normally). No capability failure to report beyond that partial-window caveat. No conviction or watch-only names to report for this handle in this pass.
