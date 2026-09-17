```json
{
  "handle": "Priyaanshu06",
  "scraped_date": "2026-09-12",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 1,
  "cadence": "dormant",
  "discloses_names": false,
  "disclaimer_pattern": "none",
  "calls": [],
  "watch_only_names": []
}
```

Only a single tweet was recovered for this handle across the full 6-month window via Apify (kaitoeasyapi Twitter/X scraper); the browser path was unavailable for the entire run (X search was erroring/rate-limited across the whole Chrome session throughout this sweep, likely from the volume of concurrent parallel-worker tabs). The one tweet found (28 Jul 2026) is a macro newsletter-promo post about India's and the US's Buffett Indicator level and what it means for markets/investing broadly — not a mention of any specific India-listed company, so no conviction or watch-only calls were seeded. Given only one data point, this account reads as either extremely low-cadence or largely non-market content the rest of the time; treat n_tweets_scanned=1 as a genuine but likely incomplete result rather than proof of true dormancy, given the browser fallback could not be used to cross-check.
