```json
{
  "handle": "AimInvestments",
  "scraped_date": "2026-09-13",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 11,
  "cadence": "medium",
  "discloses_names": true,
  "disclaimer_pattern": "none",
  "calls": [
    {
      "stock": "HDFC Bank",
      "slug": "hdfc-bank",
      "date": "2026-09-11",
      "direction": "bull",
      "conviction": "medium",
      "quote": "Thumbs up for HDFC Bank",
      "new_to_screen": false,
      "our_verdict": null,
      "since_call_pct": null
    }
  ],
  "watch_only_names": ["Deccan Gold Mines", "OBSC Perfection", "Cupid Ltd", "Milky Mist Dairy Food"]
}
```

AimInvestments (also runs two branded smallcase portfolios — Divitiae Healthcare Compounder and Divitiae Value Advantage) posts at a medium, mostly daily-news-digest cadence: a stream of terse market-news one-liners (macro commentary on GDP data, crude-oil moves, SIP flows) interleaved with bare company-news headlines paraphrased with no added opinion. The one clear exception in-window is a plain approving one-liner on HDFC Bank ("Thumbs up for HDFC Bank," 2026-09-11) — no elaboration, but a genuine positive-manner mention, so it clears the low bar as a medium-conviction bull call.

Everything else naming a specific company reads as unframed news relay rather than a view: Deccan Gold Mines (gold production starting soon), OBSC Perfection (an MoU with Aethrone Aerospace for a US manufacturing facility), Cupid Ltd (a promoter share purchase disclosure, stated purely factually with percentages), and Milky Mist Dairy Food (a new production-facility commissioning) are all reported as headlines with zero reaction/lean attached, so they're recorded as watch-only rather than calls. A question about listed beneficiaries of the India iPhone Fold launch names no specific company and was excluded. No disclaimer language ("not a recommendation," SEBI-registration note, etc.) appears anywhere in the scanned tweets, and the account otherwise reads as a small-cap/SME-oriented news aggregator with occasional light commentary rather than a deep-conviction stock-picker.

Capability note: the scroll loop stopped on three-stagnant-scrolls with the oldest captured tweet dated 2026-09-09 — the window returned only a tight two-day cluster (09-09 to 09-11) before X's live search ran dry, so this pass captured a much narrower slice than the full 2026-03-13 to 2026-09-12 window; a large portion of this handle's six-month history was not observed.
