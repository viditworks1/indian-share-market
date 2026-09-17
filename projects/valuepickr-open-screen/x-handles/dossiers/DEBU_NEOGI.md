```json
{
  "handle": "DEBU_NEOGI",
  "scraped_date": "2026-09-12",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 100,
  "cadence": "high",
  "discloses_names": true,
  "disclaimer_pattern": "light",
  "calls": [
    {
      "stock": "Unicommerce eSolutions",
      "slug": "unicommerce-esolutions",
      "date": "2026-06-11",
      "direction": "bull",
      "conviction": "very-high",
      "quote": "Very good play for long term on quick commerce and e commerce... Discl: I am heavily invested in this company",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "Parag Milk Foods",
      "slug": "parag-milk-foods",
      "date": "2026-08-25",
      "direction": "bull",
      "conviction": "very-high",
      "quote": "Advantage Parag Milk. Discl: Heavily invested in Parag, please do your own due diligence",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "HBL Engineering",
      "slug": "hbl-engineering-booting",
      "date": "2026-08-26",
      "direction": "bull",
      "conviction": "high",
      "quote": "one man (HBL promoter) spends on R&D... someone who wants to own a slice of a business then HBL is almost a perfect choice",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "Grand Continent Hotels",
      "slug": "grand-continent-hotels",
      "date": "2026-08-31",
      "direction": "bear",
      "conviction": "medium",
      "quote": "high-risk, high-reward emerging hospitality bet, not a conviction core holding [lease-model risk, aggressive expansion, SME liquidity, modest ROE]",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    }
  ],
  "watch_only_names": []
}
```

Scraped via Apify after Chrome search hit a persistent X error page for this handle (retried once per protocol, still failing — see capability note in the run). 100 tweets pulled, very high cadence. This account (Debashish Neogi, MD of a luxury chocolate exporter, Abaan) is dominated by personal/entrepreneurial content — motivational "founder journey" threads, a public complaint to @AxisBank about corporate-banking service, macro/bond-yield explainers (US 10Y framework), a SEBI pump-and-dump enforcement recap (Mauria Udyog, Vishal Fabrics, 7NR Retail, GBL Industries, Darjeeling Ropeway — cited only as fraud-case examples, not investment views, so not counted as calls), and a Subhash Chandra/Zee NCLT debt-haircut news commentary (also not a call — no forward view on Zee itself given here). Genuine single-stock conviction is concentrated in four names: two very-high, disclosed "heavily invested" positions (Unicommerce, Parag Milk Foods) stated plainly with light DYOR-style disclaimers; a spirited defense of HBL Engineering's promoter/R&D philosophy in a reply thread (positive characterization of management quality, no explicit holding disclosed); and a genuinely balanced but net-cautious multi-tweet teardown of Grand Continent Hotels (lease-model risk, aggressive room expansion, SME illiquidity, still-modest ROE) that explicitly concludes it is "not a conviction core holding" despite listing real positives — graded bear/medium rather than a clean bull call. No watch-only names surfaced (every named company got at least a directional lean). Style note: heavy use of first-person aphorisms and career-story threads makes this a lower-density account for stock signal despite the high tweet volume — worth a lighter monitoring cadence going forward unless conviction posts cluster.
