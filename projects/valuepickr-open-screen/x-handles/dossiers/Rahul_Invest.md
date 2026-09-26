```json
{
  "handle": "Rahul_Invest",
  "scraped_date": "2026-09-07",
  "window": "2026-03-08..2026-09-07",
  "n_tweets_scanned": 17,
  "cadence": "high",
  "discloses_names": true,
  "disclaimer_pattern": "light",
  "calls": [
    {
      "stock": "Beezaasan Explotech",
      "slug": "beezaasan-explotech",
      "date": "2026-08-20",
      "direction": "bull",
      "conviction": "high",
      "quote": "Beezaasan ATH - Recommended Beezaasan at Rs225/-, up 85% in less than 6 months",
      "new_to_screen": true,
      "our_verdict": "mixed",
      "since_call_pct": null
    }
  ],
  "watch_only_names": [
    "National Fittings",
    "unresolved promoter-buying teaser (mcap ~Rs174 Cr, Anil Kumar Agarwal buying)",
    "unresolved promoter-buying teaser (mcap ~Rs1014 Cr, down 40% from top)",
    "unresolved promoter-buying teaser (Rs182 Cr promoter block Sep25, stock -41% to Rs108)"
  ]
}
```

## Account character
Raahul Kumar Das / LnprCapital (SEBI RA), small/microcap focus. Signature format is the anonymised "Promoter Buying Decode" teaser — market cap, % promoter-holding jump, rupee value of open-market purchases, "just for educational purposes" — with the company name usually withheld from the main post. Also posts multibagger/microcap philosophy and market-flow snippets. Names are disclosed selectively (in replies, or when celebrating a past pick).

## Notable calls
- **Beezaasan Explotech (bull, high)** — quote-tweeted his own earlier "Recommended Beezaasan at Rs225/-" post to mark a new all-time high, "up 85% in less than 6 months". Explicit disclosed recommendation with performance boast → `high`. New to screen → **seeded** as `beezaasan-explotech` (external-lead, x_untrusted).
- Multiple "Promoter Buying Decode" teasers (promoter stake 52.62%→62.28% in 2 quarters via Mayadevi Polycot + NCVI Enterprises Rs17.8 Cr; a Rs182 Cr block with stock -41%; a Rs1014 Cr mcap name -40% from top; a Rs174 Cr mcap with Anil Kumar Agarwal accumulating). None name the listed company in the visible text → cannot resolve, watch-only, dossier note only.
- "National fitting" appears only as a bare two-word reply (likely answering one of the teasers, plausibly National Fittings Ltd) with no view attached from the handle → watch-only, not seeded.

## Anything odd
X live-search returned ~2.5 weeks of posts (oldest 2026-08-20). Deliberate name-withholding is this account's whole shtick, so seed yield will stay low unless we resolve the teasers via holdings-disclosure cross-checks — a job for `x-handle-ranking`, not this pass.
