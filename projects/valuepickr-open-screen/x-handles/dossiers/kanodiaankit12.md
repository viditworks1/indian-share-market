```json
{
  "handle": "kanodiaankit12",
  "scraped_date": "2026-09-05",
  "window": "2026-03-06..2026-09-05",
  "n_tweets_scanned": 11,
  "cadence": "unknown-window-too-narrow",
  "discloses_names": true,
  "disclaimer_pattern": "none",
  "calls": [
    {
      "stock": "Purple Style Labs",
      "slug": "purple-style-labs",
      "date": "2026-08-30",
      "direction": "bull",
      "conviction": "medium",
      "quote": "Quote-tweeted a PSL DRHP-anomaly deep-dive with 'anomalies... contain the richest information' (Robert Greene).",
      "new_to_screen": true,
      "our_verdict": null,
      "since_call_pct": null
    }
  ],
  "watch_only_names": []
}
```

Scan surfaced only 11 tweets, all from 2026-08-30 to 2026-09-05 — well short of the 183-day target (search feed stopped lazy-loading early), so this is a thin, recency-biased sample. Ankit Kanodia (SEBI RIA, ZenNivesh) mostly posted DRHP/IPO teasers in this window ("2nd page of a DRHP", "Book Running Managers of an IPO... no points for guessing") that appear to build toward revealing an upcoming IPO name, plus one substantive item: he quote-tweeted a third-party deep-dive on Purple Style Labs' DRHP anomalies (no OFS, no PE/VC investors, high margins) and added a Robert Greene quote framing anomalies as the richest source of information — an implicit signal he finds the PSL story interesting/well-flagged rather than a stated bull/bear thesis of his own. Graded `medium` on that basis. Purple Style Labs is not in the registry (confirmed via `get_stock.py`) — seeded this run. The DRHP/IPO teaser tweets don't name a company explicitly enough to resolve, so left out.
