```json
{
  "handle": "gaurang_19",
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

Verified via two independent methods: browser live-search returned `n:0, empty:false` (retried), and a follow-up Apify scrape (kaitoeasyapi tweet scraper, same handle/date window) returned only mock-data placeholder rows — the actor's own signal for a genuinely empty real-data result. No tweets found in-window by either method. `last_tweet_id_seen`: null. This account is either dormant, private, suspended, or posts so rarely that nothing fell inside the 2026-03-13 to 2026-09-12 window. No calls, no watch-only names.
