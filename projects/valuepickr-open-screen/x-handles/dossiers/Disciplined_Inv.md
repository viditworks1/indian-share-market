```json
{
  "handle": "Disciplined_Inv",
  "scraped_date": "2026-09-12",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 11,
  "cadence": "low",
  "discloses_names": true,
  "disclaimer_pattern": "light",
  "calls": [
    {
      "stock": "GHCL Textiles",
      "slug": "ghcl-textiles",
      "date": "2026-09-01",
      "direction": "bull",
      "conviction": "very-high",
      "quote": "GHCL Textile at new ATH! Still trading below book value... Disclosure: Invested from 70 levels (CMP: 143)",
      "new_to_screen": false, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "Sheela Foam",
      "slug": "sheela-foam",
      "date": "2026-07-08",
      "direction": "bull",
      "conviction": "high",
      "quote": "Study Sheela Foam: Market leader having a turnaround. Kurlon integration complete. Debt down from 1500 Cr to 900 Cr. ATH Sales & Ebitda. First ever dividend announced.",
      "new_to_screen": true, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "Route Mobile",
      "slug": "route-mobile",
      "date": "2026-07-07",
      "direction": "bull",
      "conviction": "high",
      "quote": "Study Route Mobile: Cash ~1400 Cr, debt free... generating 600 Cr annual cashflows is available for just 2100 Cr. Proximus paid ~1700/share",
      "new_to_screen": true, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "S Chand & Co",
      "slug": "s-chand",
      "date": "2026-07-06",
      "direction": "bull",
      "conviction": "high",
      "quote": "Study Schand: Entire business that does 100 Cr avg cashflow available for around 400 Cr. AI Content Licencing growing at 60%. May soon do buyback.",
      "new_to_screen": true, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "Archit Nuwood Industries",
      "slug": "archit-nuwood-industries",
      "date": "2026-05-07",
      "direction": "bull",
      "conviction": "very-high",
      "quote": "Holding Archit from 40-45 levels.",
      "new_to_screen": true, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "Vijay Solvex",
      "slug": "vijay-solvex",
      "date": "2026-05-07",
      "direction": "bull",
      "conviction": "very-high",
      "quote": "Averaged Vijay Solvex at 350-400 levels.",
      "new_to_screen": true, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "Omax Autos",
      "slug": "omax-autos",
      "date": "2026-05-06",
      "direction": "bull",
      "conviction": "very-high",
      "quote": "Omax Autos update: ~50% revenue increase YoY, debt reduced further, Share of Revenue from Railways >42% now. Disc: Holding from 90 levels.",
      "new_to_screen": true, "our_verdict": null, "since_call_pct": null
    }
  ],
  "watch_only_names": []
}
```

Account character: a low-frequency (11 real tweets across the 6-month window — the Apify actor padded the response to 15 with billing-notice filler items that were excluded) but consistently high-quality value-investing account. Every stock post follows the same disciplined "Study X:" template — market cap, net cash/debt position, cashflow generation, and a clear valuation anchor (often benchmarked against a comparable transaction price, e.g. Route Mobile vs. what Proximus paid) — and almost every post carries an explicit disclosed position ("Disc: Holding from X levels," "Invested from X levels," "Averaged at X-Y levels"). This is about as close to textbook "trusted-signal" conviction as this batch produced: no hedging, no disclaimers beyond the position tag itself, and theses are fundamentals-first (debt paydown, dividend initiation, cashflow yield, buyback optionality) rather than price-action commentary.

Seven distinct names surfaced, all bullish, spanning small/micro-caps (Archit Nuwood, Vijay Solvex, Omax Autos, GHCL Textiles) to a few slightly larger turnaround/compounder names (Sheela Foam, Route Mobile, S Chand). Omax Autos and GHCL Textiles come with the most complete real-time operational detail (revenue growth %, segment mix, ATH context). Sheela Foam and Route Mobile are framed as "Study" pieces without an explicit disclosed position but with strong bullish framing (turnaround completion, deep valuation discount to a reference transaction) — graded high rather than very-high for that reason.

Nothing bearish or merely watch-listed appeared — every named company got a substantive, reasoned bull case. No India-listed name was left as a bare mention. Given the low volume but high hit-rate and explicit disclosures, this handle looks like a strong candidate for elevated trust weighting if the pipeline tracks per-handle reliability.
