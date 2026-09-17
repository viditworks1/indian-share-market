```json
{
  "handle": "investor_vineet",
  "scraped_date": "2026-09-12",
  "window": "2026-03-13 to 2026-09-12",
  "n_tweets_scanned": 100,
  "cadence": "high",
  "discloses_names": true,
  "disclaimer_pattern": "none",
  "calls": [
    {
      "stock": "Equitas Small Finance Bank",
      "slug": "equitas-small-finance-bank",
      "date": "2026-08-29",
      "direction": "bull",
      "conviction": "very-high",
      "quote": "50% PPFAS / 30% equitas / 10% medi assist / 2% arman finance / 8% misc/sgb [disclosed portfolio allocation]; also: Equitas BV increases by 1.6 this quarter",
      "new_to_screen": true, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "Arman Financial Services",
      "slug": "arman-financial-services",
      "date": "2026-08-29",
      "direction": "bull",
      "conviction": "high",
      "quote": "2% arman finance [disclosed portfolio allocation]; Aisi hi kahaani Arman finance ki bhi hai [same BV-growth story as Equitas]",
      "new_to_screen": false, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "Medi Assist Healthcare Services",
      "slug": "medi-assist-healthcare-services-ltd",
      "date": "2026-08-29",
      "direction": "bull",
      "conviction": "medium",
      "quote": "10% medi assist [disclosed portfolio allocation]",
      "new_to_screen": false, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "IDFC First Bank",
      "slug": "idfc-first-bank",
      "date": "2026-07-25",
      "direction": "bull",
      "conviction": "high",
      "quote": "Idfc first posts an ROA above 1% for first time. Impressive profit numbers.(last quarter had 600cr impact of chandigarh branch issue). Good footing overall.",
      "new_to_screen": false, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "Alok Industries",
      "slug": "alok-industries",
      "date": "2026-09-01",
      "direction": "bear",
      "conviction": "medium",
      "quote": "Alok industries volumes suggest its going to be beaten down to nclt levels. Seems some bank has liquidated the security cover.",
      "new_to_screen": true, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "HDFC AMC",
      "slug": "hdfc-amc",
      "date": "2026-07-15",
      "direction": "bull",
      "conviction": "medium",
      "quote": "Hdfc AMC - wat an accreation quarter",
      "new_to_screen": true, "our_verdict": null, "since_call_pct": null
    },
    {
      "stock": "South Indian Bank",
      "slug": "south-indian-bank",
      "date": "2026-07-16",
      "direction": "bear",
      "conviction": "medium",
      "quote": "Despite NIM improvement - SIB posts a QoQ decline in profits due to higher c2I and higher qoq provisioning",
      "new_to_screen": true, "our_verdict": null, "since_call_pct": null
    }
  ],
  "watch_only_names": ["RBA Ltd", "Fedbank Financial", "MCX", "Piramal Finance", "ITC Infotech/Happiest Minds merger"]
}
```

Account character: a high-cadence account that is roughly 70% political/social commentary (reservation policy, protests, election takes, in a Hinglish register) and roughly 30% markets — mostly F&O/options-trading color (CAS auction mechanics, expiry-day war stories, index straddle commentary) plus periodic NBFC/bank-results tracking. Genuinely useful stock-specific content is concentrated in a handful of results-reaction and one explicit portfolio-disclosure tweet.

The single most valuable data point is a direct reply disclosing his live portfolio allocation: 50% PPFAS (a PMS/fund, excluded as not a single stock), 30% Equitas Small Finance Bank, 10% Medi Assist, 2% Arman Financial Services, 8% misc/SGB. Combined with a same-day standalone tweet on Equitas book-value growth ("BV increases by 1.6 this quarter") and a following tweet drawing the same book-value-compounding parallel to Arman Financial ("Aisi hi kahaani Arman finance ki bhi hai"), Equitas gets very-high conviction and Arman gets high. Medi Assist has the disclosed allocation but zero supporting commentary elsewhere in-window, so it's graded medium.

Beyond the portfolio reveal, he runs a recurring NBFC/bank-results beat: approving of IDFC First Bank's first sub-1% ROA quarter, and flagging South Indian Bank's cost-to-income-driven profit miss despite NIM improvement (his own results reactions, not third-party reposts). Alok Industries gets a standalone bearish volume/NCLT-risk observation. HDFC AMC gets a terse but clearly approving one-liner on an "accretion quarter."

RBA Ltd is discussed only via someone else's detailed thesis (quote-tweeted, hedged, "may become a lucrative buy... many levers"), and Piramal Finance/MCX/Fedbank/the ITC Infotech-Happiest Minds merger question are all either third-party data he's relaying for a macro point or genuinely non-committal — kept watch-only rather than promoted to calls.
