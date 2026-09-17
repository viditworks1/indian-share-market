```json
{
  "handle": "pgodhani",
  "scraped_date": "2026-09-12",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 0,
  "cadence": "dormant",
  "discloses_names": false,
  "disclaimer_pattern": "none",
  "calls": [],
  "watch_only_names": []
}
```

No tweets recovered for this handle. Two independent Apify (kaitoeasyapi Twitter/X scraper) runs against `from:pgodhani since:2026-03-13 until:2026-09-12` — one inside a 6-handle batch, one solo re-run targeting this handle specifically — both returned exactly 0 dataset items with no error, i.e. the search genuinely produced nothing. The browser path (x.com live search and the raw profile page) was also attempted but the whole Chrome session was rate-limited/erroring ("Something went wrong. Try reloading.") for the entire duration of this run, likely due to the very high number of concurrent parallel-worker tabs hitting X simultaneously as part of this bulk sweep — so the browser could not independently confirm whether the account is empty, protected, suspended, or simply inactive in-window. Given two consistent zero-result signals from the working scrape path, this is reported as a genuine empty result rather than fabricated, but the account-status ambiguity (does it exist / is it protected) should be treated as an open capability-failure note rather than a confirmed "dormant" account — flagged here as dormant/zero-activity for pipeline purposes, pending a future manual spot-check.
