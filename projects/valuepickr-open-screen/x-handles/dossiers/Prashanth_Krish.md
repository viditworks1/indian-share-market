```json
{
  "handle": "Prashanth_Krish",
  "scraped_date": "2026-09-12",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 100,
  "cadence": "high",
  "discloses_names": false,
  "disclaimer_pattern": "none",
  "calls": [
    {
      "stock": "Vadilal Industries",
      "slug": "vadilal-industries",
      "date": "2026-07-29",
      "direction": "bull",
      "conviction": "medium",
      "quote": "what a ride the stock had haf since that terry [target] of mine. #vadilal",
      "new_to_screen": true,
      "our_verdict": null,
      "since_call_pct": null
    }
  ],
  "watch_only_names": ["TCS", "Infosys"]
}
```

Capability note: the browser scrape (x.com search, in-window) returned a persistent "Something went wrong" error page for this handle even after a retry with a longer wait — attributed to rate-limiting from the very high concurrent tab load across this multi-handle triage sweep, not a genuine empty result. Fell back to Apify (kaitoeasyapi/twitter-x-data-tweet-scraper), which returned 100 items successfully, spanning 2026-06-20 to 2026-09-11 (maxItems cap reached; earlier posts back to the 2026-03-13 window start were not retrieved, so this is a partial-window sample skewed toward the most recent ~3 months).

Account character: a prolific, mostly non-market account — dense reply activity on Indian politics, geography/geopolitics, travel/hotel-pricing comparisons, and general contrarian social commentary, interspersed with occasional investing-philosophy musings (momentum vs. multi-factor investing, DIY investing discipline, Zerodha/direct-MF commentary — Zerodha itself unlisted so out of scope). Investing content is mostly abstract/process-oriented rather than single-stock; he describes himself as "100% in Momentum" as a personal style but names no current holdings or calls in-window. The sole specific India-listed company reference is a callback quip to a past price target on Vadilal Industries ("what a ride the stock had... since that terry of mine #vadilal"), implying an earlier bullish target that played out — graded medium conviction, bull, new to the screen. A reply thread touches a quoted tweet arguing TCS & Infosys "will return with a vengeance" on AI-driven IT services strength, but Prashanth's own comment ("Tides can change pretty fast") does not clearly endorse or reject the thesis, so both names are logged watch-only per the no-added-reaction rule. Overall this handle reads as low-value for stock-specific conviction tracking; its rare stock content is Vadilal-adjacent and stale.
