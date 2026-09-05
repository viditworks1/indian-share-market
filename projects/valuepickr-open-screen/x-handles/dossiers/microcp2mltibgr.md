```json
{
  "handle": "microcp2mltibgr",
  "scraped_date": "2026-09-05",
  "window": "2026-03-06..2026-09-05",
  "n_tweets_scanned": 9,
  "cadence": "unknown-window-too-narrow",
  "discloses_names": false,
  "disclaimer_pattern": "none",
  "calls": [],
  "watch_only_names": []
}
```

The scan only surfaced 9 tweets, all from 2026-09-04/09-05 (a single day) — the search feed stopped lazy-loading after a handful of scrolls well short of the 183-day target, so this is a very partial sample and not representative of the account's actual cadence or naming behavior. Content in the captured window is entirely off-topic: replies, memes, a generic crude-oil macro musing, and a note about a hacked-account impersonator complaint. No India-listed company was named with any view, positive or negative. No conviction calls, no watch-only names, nothing to seed. `discloses_names` and `cadence` should be treated as unresolved rather than confirmed "no" given how thin this sample is — worth a re-scrape attempt (e.g. via a wider scroll or Apify) on a future pass if the account keeps surfacing.
