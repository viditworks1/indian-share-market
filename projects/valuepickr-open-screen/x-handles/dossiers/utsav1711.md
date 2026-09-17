```json
{
  "handle": "utsav1711",
  "scraped_date": "2026-09-12",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 0,
  "cadence": "dormant",
  "discloses_names": false,
  "disclaimer_pattern": "none",
  "calls": [],
  "watch_only_names": [],
  "note": "Account is dormant for the entire 183-day scan window. Confirmed via a follow-up unwindowed Apify search (from:utsav1711, no date filter) that the account's most recent tweet is dated 2025-06-15 — over a year before the window opens. Not a scraping failure: account exists, was previously active on market topics (see prior content below), simply stopped posting."
}
```

Account character: prior to going dormant, this was a stock-commentary account with a distinctive philosophical/quippy style ("The only true gift u can leave your next generation is shares in your demat", "Mcap/vision" jokes about SME IPO valuations, a 4-stage "life cycle of a SME stock" thread). No tweets exist inside the 2026-03-13 to 2026-09-12 window — the account has been silent since mid-June 2025, well over a year. Confirmed genuine dormancy (not a rate-limit or scrape failure): the browser path returned "Something went wrong" on the search URL (later diagnosed as browser overload from many concurrent parallel scrapers, not this account specifically), so this was cross-checked with Apify twice — once with the date-bounded query (returned only KaitoEasyAPI mock/placeholder rows, i.e. zero real matches) and once with an unbounded from:utsav1711 query (returned 20 real historical tweets, newest dated 2025-06-15). This confirms the account is real, has tweets, but none in-window. No calls or watch names to report. No capability failure — this is a clean "nothing to scan" result.
