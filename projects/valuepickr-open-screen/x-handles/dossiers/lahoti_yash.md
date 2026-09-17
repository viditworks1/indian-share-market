```json
{
  "handle": "lahoti_yash",
  "scraped_date": "2026-09-12",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 9,
  "cadence": "low",
  "discloses_names": false,
  "disclaimer_pattern": "none",
  "calls": [],
  "watch_only_names": []
}
```

Account character: very low-signal handle for this pipeline's purposes. Only 9 real tweets fell in the 6-month window (the Apify actor padded its response to 15 with generic billing-notice filler items, which were excluded from the count). Content is a thin mix of generic motivational one-liners ("धैर्यं सर्वस्य साधनम्" — patience is the means to everything, "a jack of all trades..."), a personal remark thanking a concall-scanning feature demo from @stockscansin, a note on Rapido visibly gaining market share from Ola at Hyderabad airport (an anecdotal observation about a private/unlisted-adjacent business, not an actionable India-listed single-stock call), and two approving reposts of long-form threads — one a sector-wide pharma value-chain breakdown from @soicfinance (no single company singled out), and one a business-quality writeup on ASML Holding from @ResearchSOIC (a US-listed name, explicitly out of scope).

No India-listed single-stock conviction — bullish, bearish, or otherwise — was found anywhere in the window. Nothing qualified even for the lighter watch-only bucket, since the pharma-sector repost names no specific company and the only named company (ASML) is a US listing excluded by the classification rules. Cadence reads as low and largely repost-driven rather than original single-name research; this handle currently contributes nothing actionable to the screen and may be worth deprioritizing in future triage passes unless its posting pattern changes.
