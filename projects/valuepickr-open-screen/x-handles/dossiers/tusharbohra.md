```json
{
  "handle": "tusharbohra",
  "scraped_date": "2026-09-05",
  "window": "2026-03-06..2026-09-05",
  "n_tweets_scanned": 7,
  "cadence": "low",
  "discloses_names": true,
  "disclaimer_pattern": "light",
  "calls": [
    {
      "stock": "MV Electrosystems",
      "slug": "mv-electrosystems-ltd",
      "date": "2026-08-10",
      "direction": "bull",
      "conviction": "high",
      "quote": "Presented MVEL at IAS2026 (8 Aug); disclosed 'we may have positions here' alongside a full deck.",
      "new_to_screen": false,
      "our_verdict": "disagree",
      "since_call_pct": null
    },
    {
      "stock": "Laurus Labs",
      "slug": "laurus-labs",
      "date": "2026-07-08",
      "direction": "bull",
      "conviction": "medium",
      "quote": "'Sajal bhai your conviction on Laurus is just so infectious and inspiring' (reply, not own thesis).",
      "new_to_screen": false,
      "our_verdict": "mixed",
      "since_call_pct": null
    }
  ],
  "watch_only_names": [
    "IdeaForge"
  ]
}
```

Only 7 tweets surfaced in the scan despite an 183-day target window — the search feed stopped lazy-loading new items after a handful of scrolls (stagnant cap hit) rather than the 150-post cap, so the account may post more than this captured; oldest post seen was 2026-07-08.

Tushar Bohra is an active conference presenter/investor (IAS2026 speaker) who discloses positions when sharing decks — the MV Electrosystems presentation carries a standard "does not constitute a recommendation" light disclaimer alongside an explicit "we may have positions here." That's the one substantive call in this window: a full IAS2026 deck on MVEL with disclosed position, which counts as `high` conviction. MVEL is already in the registry (`researched`, conviction `Low`, last analyzed 2026-08-28) — flagged in `existing-name-sightings.md` for a re-look since a trusted-adjacent presenter with a disclosed position rates it well above our current Low read.

The Laurus Labs mention is a reply praising someone else's (@Sajal) conviction, not his own stated thesis — kept as `medium` but it's thin; Laurus is already researched in the registry so no seed either way. An IdeaForge mention was purely amplifying a third-party industry deep-dive on drone-sector capital raises with no company-specific view of his own — logged as watch-only. Nothing new to seed from this account this run. Account also flagged an impersonator handle (@diptesh_rana) — no action needed, not stock-relevant.
