```json
{
  "handle": "nathanit2014",
  "scraped_date": "2026-09-12",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 6,
  "cadence": "unknown (capability-limited, see note)",
  "discloses_names": true,
  "disclaimer_pattern": "none",
  "calls": [
    {
      "stock": "Raymond Realty",
      "slug": "raymond-realty-ltd-high-roce-demerger-play",
      "date": "2026-09-12",
      "direction": "bull",
      "conviction": "high",
      "quote": "Raymond realty; patience will pay off; promoter grp is investing (part of a 3-stock bullish-and-invested real estate list)",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "Bombay Dyeing",
      "slug": "bombay-dyeing",
      "date": "2026-09-12",
      "direction": "bull",
      "conviction": "high",
      "quote": "Real estate sector - bullish and invested - Bombay dye; Raymond realty; embassy development; all 3 hv HUGE LAND BANK; need patience (2 years mini)",
      "new_to_screen": true,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "Embassy Developments",
      "slug": "embassy-developments-ltd",
      "date": "2026-09-12",
      "direction": "bull",
      "conviction": "high",
      "quote": "Real estate sector - bullish and invested - ...embassy development; all 3 hv HUGE LAND BANK; need patience (2 years mini)",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "IOL Chemicals",
      "slug": "iol-chemicals",
      "date": "2026-09-12",
      "direction": "exit",
      "conviction": "medium",
      "quote": "Sold 70% yesterday; cash needed (re: IOL CHEM trading bet added at open, SL 140, tgt 240)",
      "new_to_screen": true,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "West Coast Paper Mills",
      "slug": "west-coast-paper-mills-ltd",
      "date": "2026-09-12",
      "direction": "bull",
      "conviction": "high",
      "quote": "Recalling; west coast is not only PAPER; hidden OPTIC FIBRE SEGMENT... significant bottom line contribution in q4; will add more on dips",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "Asahi Songwon Colors",
      "slug": "asahi-songwon-colors-ltd",
      "date": "2026-09-12",
      "direction": "bull",
      "conviction": "high",
      "quote": "Added asahi last week (re: Asahi song won - blockbuster no's; undervalued; micro cap)",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "Vindhya Telelinks",
      "slug": "vindhya-telelinks-ltd",
      "date": "2026-09-12",
      "direction": "bull",
      "conviction": "medium",
      "quote": "Recalling (endorsing prior thread: on HARDWARE - VINDHYA & TEJAS will play a big role... GETIN in parts in next 3 months)",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "Tejas Networks",
      "slug": "tejas-networks",
      "date": "2026-09-12",
      "direction": "bull",
      "conviction": "medium",
      "quote": "Recalling (endorsing prior thread: on HARDWARE - VINDHYA & TEJAS will play a big role... GETIN in parts in next 3 months)",
      "new_to_screen": true,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "Shilpa Medicare",
      "slug": "shilpa-medicare-racing-away-on-the-oncology-api-highway",
      "date": "2026-09-12",
      "direction": "bull",
      "conviction": "medium",
      "quote": "3 blockbuster results in 2 days; Shilpa; SOTL & Rain; well followed stocks; patience & be in MKT",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    },
    {
      "stock": "Rain Industries",
      "slug": "rain-industries-an-oversold-de-leveraging-play",
      "date": "2026-09-12",
      "direction": "bull",
      "conviction": "medium",
      "quote": "3 blockbuster results in 2 days; Shilpa; SOTL & Rain; well followed stocks; patience & be in MKT",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    }
  ],
  "watch_only_names": [
    "SOTL (unresolved ticker, could not map to a listed entity with confidence)",
    "Bharti Airtel (named as a 'keep a watch' name in the recalled data-centre thread, not an active call)"
  ]
}
```

CAPABILITY NOTE: the scroll-collection script for this handle returned only 6 tweets, all timestamped within minutes of each other on 2026-09-12 (the scrape date itself), despite two retries with longer waits. Given the account's evident posting density (6 substantive, name-dense tweets inside one ~4-minute window), this almost certainly reflects the live X search "Latest" tab only rendering the newest batch before the scroll-triggered pagination stalled (concurrent heavy browser load from parallel triage workers is the likely cause), not that the account only tweeted 6 times in 6 months. Treat `cadence` as unverified — this dossier covers only the most recent visible slice, not the full window. A re-scrape (ideally via Apify or a quieter browser session) would likely surface much more history.

Account character: a rapid-fire, disclosure-heavy retail trader/tracker who names specific tickers with explicit position status ("invested", "added", "sold 70%"), price levels, and holding-period guidance ("patience, 2 years mini" for real estate names; "will add more on dips" for West Coast Paper). Very little hedging or disclaimer language — reads as a genuine trading/investing journal rather than commentary. The real-estate trio (Bombay Dyeing, Raymond Realty, Embassy Developments) is presented as one coordinated "land bank" thesis with an explicit multi-year holding horizon. Embassy Developments is worth flagging: our own screen carries it at red-flag tier "HIGH CAUTION" (IRP proceedings, weekly-only trading surveillance) — this account's blanket-bullish framing does not appear to account for that overhang.
