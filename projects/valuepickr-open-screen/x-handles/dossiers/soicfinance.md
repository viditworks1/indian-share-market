```json
{
  "handle": "soicfinance",
  "scraped_date": "2026-09-05",
  "window": "2026-03-06 to 2026-09-05",
  "n_tweets_scanned": 13,
  "cadence": "high",
  "discloses_names": true,
  "disclaimer_pattern": "light",
  "calls": [
    {
      "stock": "Lakshmi Machine Works Ltd",
      "slug": "lakshmi-machine-works",
      "date": "2026-08-29",
      "direction": "bull",
      "conviction": "high",
      "quote": "Recovery in TMD order book, MTD machining centre push, new facility for ATC, order book scale up there",
      "new_to_screen": false,
      "our_verdict": "unverified",
      "since_call_pct": null
    },
    {
      "stock": "Jyoti CNC Automation Ltd",
      "slug": "jyoti-cnc-automation",
      "date": "2026-08-29",
      "direction": "bull",
      "conviction": "high",
      "quote": "Capacity expansion to 16k machines, Doubling Huron Capacity, EMS ramp up, Export licence unlocking deferred revenue",
      "new_to_screen": true,
      "our_verdict": "red-flag",
      "since_call_pct": null
    },
    {
      "stock": "Macpower CNC Machines Ltd",
      "slug": "macpower-cnc-machines-manufacturing-a-strong-growth",
      "date": "2026-08-29",
      "direction": "bull",
      "conviction": "high",
      "quote": "30-acre defence land greenfield, backward integration, JV/Tech partnership with German partner, 2,500-machine capacity operational",
      "new_to_screen": false,
      "our_verdict": "agree-strong",
      "since_call_pct": null
    },
    {
      "stock": "Sterlite Technologies Ltd",
      "slug": "sterlite-technologies",
      "date": "2026-09-03",
      "direction": "bull",
      "conviction": "medium",
      "quote": "Sterlite strong guidance of 20,000 crores revenue with 27% ebitda margins by FY29",
      "new_to_screen": false,
      "our_verdict": "mixed",
      "since_call_pct": null
    }
  ],
  "watch_only_names": []
}
```

## Notes

@soicfinance is the SOIC (Intrinsic Compounding) org handle — already flagged cluster-adjacent in the registry note. Extractor only surfaced 13 tweets from 2026-08-27 to 2026-09-04 despite the 6-month search window; X's infinite-scroll on the Latest search feed stalled repeatedly (verified with manual scroll + longer waits, still capped at the same 13) rather than reaching further back — this is a scroll/lazy-load ceiling, not a true absence of older posts. Treat cadence/scope as a lower bound; a future re-run may need a narrower date-sliced search to get past this window.

Within the visible window: a dedicated reply-thread naming three CNC/machine-tool growth stories (Lakshmi Machine Works, Jyoti CNC Automation, Macpower CNC) with specific catalysts for each — genuine bullish thesis material, not a bare list. Also a factual/bullish note on Sterlite Technologies' FY29 revenue guidance (light "not a buy/sell reco" disclaimer attached, doesn't downgrade the substance). Two other posts (management-quality essay, Middle East capex/line-pipe commentary) were educational/thematic with no single company pinned down — ignored. A Peptide-sector Substack plug and a Janmashtami/Raksha Bandhan greeting were non-stock content.

Macpower and Sterlite are already in the registry at fresh `last_analyzed_date` (2026-08-22 and 2026-09-04) with conviction High/Medium respectively — no re-look flag needed. Lakshmi Machine Works is in the registry as `excluded/Low` (2026-08-24) — SOIC's specific bullish catalysts contradict that read, so it's logged to `existing-name-sightings.md` for `x-handle-ranking` to reconsider. Jyoti CNC Automation Ltd is genuinely new (distinct from the existing `jyoti-resins-adhesives` entry) — seeded as `external-lead`.
