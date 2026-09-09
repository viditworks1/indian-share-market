```json
{
  "handle": "nareshbahrain",
  "scraped_date": "2026-09-07",
  "window": "2026-03-08..2026-09-07",
  "n_tweets_scanned": 17,
  "cadence": "high",
  "discloses_names": true,
  "disclaimer_pattern": "light",
  "calls": [
    {
      "stock": "Jindal Saw",
      "slug": "jindal-saw",
      "date": "2026-09-07",
      "direction": "bull",
      "conviction": "medium",
      "quote": "\"153 to 319 in 8 months & 23 days\" JINDALSAW - Low 153 (09 Dec 25), High 319 (01 Sep 26)",
      "new_to_screen": true,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "HDFC Bank",
      "slug": "hdfc-bank",
      "date": "2026-09-04",
      "direction": "bull",
      "conviction": "medium",
      "quote": "Already gave the HDFCBANK valuation zone with chart end-March 2026. Those valuations given are still holding.",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    }
  ],
  "watch_only_names": ["Engineers India (ENGINERSIN)"]
}
```

## Account character
Naresh Nambisan / ValuationMantra (SEBI RA, INH000022215). Self-described "pure tape person" running a "valuation zone" method — marks buy zones on charts when negativity is priced in for foundationally strong companies, then publicises them retrospectively when they work. High cadence, heavy on process/philosophy one-liners ("no stock is sacrosanct", "buy low as a way of life"), free Substack/charts funnel, RA disclosure boilerplate.

## Notable calls
- **Jindal Saw (bull, medium)** — retrospective win showcase: "153 to 319 in 8 months & 23 days", low Rs153 on 09 Dec 25, high Rs319 on 01 Sep 26. Marketing post around a past valuation-zone entry rather than a fresh thesis, but a clear disclosed positive call → `medium`. New to screen → **seeded** as `jindal-saw` (external-lead, x_untrusted).
- **HDFC Bank (bull, medium)** — repeated references to a "HDFCBANK valuation zone" chart he published end-March 2026, noting "those valuations given are still holding". Mild positive, mega-cap, already in screen → not seeded.
- Another retrospective post (Rs130-142 zone marked Jan '25 as a stock crashed from Rs304, now ~Rs290) carried no ticker in the visible text — unresolved, ignored.

## Anything odd
X live-search returned only ~4 days of posts (oldest 2026-09-03) — very shallow; this is a high-cadence account so a deeper Apify scrape would likely surface several more named zones. `ENGINERSIN` appeared only as "Google for news wrt ENGINERSIN during that period" in a reply — no view, watch-only.
