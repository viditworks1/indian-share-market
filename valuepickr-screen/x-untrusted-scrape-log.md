# Untrusted-X one-off scrape log

Manual, user-directed scrapes of X accounts that are **NOT** in the trusted cluster
(`x_cluster.json`). Names found here enter `state.json` as ordinary discovery
candidates — `source: "external-lead"`, `x_untrusted: true`, **no** conviction floor,
**no** `x_conviction_strength`, **no** `trusted_signals`, **no** corroboration-bonus
feed. They are researched by `vpscreen-scan` at tier 4.5 like any other user-vetted tip.
Distinct from `x-trusted-cluster` (that task is trusted handles only).

---

## 2026-09-02 — @Aditya_joshi12 (Aditya Joshi, Sovrenn research)

- **Requested by:** user ("find candidates for discovery from the posts of
  https://x.com/Aditya_joshi12 … not a trusted user yet, so any stock names identified
  has to be added to discovery pipeline").
- **Scrape:** Apify actor `kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest`,
  runs `UQTjPrx0qgUZ1gMTX` (90-day window, 5 real tweets) + `ptgR6OsvA5DQasZdT`
  (`from:Aditya_joshi12 since:2025-09-03 until:2026-09-02`, **60 tweets = his full ~1-year
  output**).
- **Account character:** low posting volume. Content is (a) macro / bull-bear-market
  timing commentary, (b) a numbered teaching-quiz series ("Padhega India, tabhi to aage
  badhega India") of investing-concept MCQs, (c) Sovrenn hiring / game-show promos. He
  states explicitly (2025-11-28): *"I don't take stock names on twitter … very important
  to not disclose stock names on twitter."* So there are **zero conviction calls** in the
  window — every company name appears only as a quiz option.

### Added to the pipeline (5) — all `source: external-lead`, `x_untrusted: true`, tier 4.5, no floor

| Slug | Name | Where it came from | Strength |
|---|---|---|---|
| `sonu-infratech` | Sonu Infratech Ltd | Quiz 2025-12-14, *answer* to "which delivered MORE than guidance last year" (FY25). NSE SME, civil/scaffolding EPC, heavy Reliance-Jamnagar exposure, ~Rs 66 Cr mcap / ~5x PE. | Mild positive datapoint (guidance beat) — verify against the actual FY25 result. |
| `maxvolt-energy-industries` | Maxvolt Energy Industries Ltd | Quiz 2025-11-28, option for "single-segment EV-sector proxy". NSE Emerge, listed Feb-2025, Li-ion battery packs. | Descriptive only. |
| `zelio-e-mobility` | Zelio E-Mobility Ltd | Quiz 2025-11-28, option for "single-segment EV-sector proxy". NSE/BSE (BSE 544563), electric 2W/3W maker. | Descriptive only. |
| `avg-logistics` | AVG Logistics Ltd | Quiz 2025-12-14, *distractor* in the "beat guidance" question → implied FY25 guidance **miss**. NSE, asset-light logistics / reefer & rail. | Weak / mildly negative — verify whether it actually missed. |
| `greenlam-industries` | Greenlam Industries Ltd | Quiz 2025-12-14, *distractor* in the "beat guidance" question → implied FY25 guidance **miss**. NSE/BSE mainboard laminates leader. | Weak / mildly negative — likely has a real VP thread (Step 3.05). |

### Named but NOT added

- **Ramkrishna Forgings ("RK Forging")** — quiz distractor 2025-12-14. Already in registry
  as `ramkrishna-forgings-ias2026` (excluded).
- **Amara Raja** — quiz 2025-11-28; he explicitly said it is **not** a pure EV play.
  Already in registry (`amara-raja-energy-mobility-limited-powering-ahead`).
- **"Supertech EV"** — quiz option 2025-11-28. Could not confirm any NSE/BSE listing;
  treated as a private brand / fabricated distractor. Not seeded.
- **Shree Ganesh Jewellery House** — quiz 2025-12-16, cited only as a delisted ~Rs 2,600 Cr
  CBI/ED scam. Not investable. (Note: unrelated to the listed `shree-ganesh-remedies`.)
- Distractor options that are not real companies (Sameer / Sameeksha / Samarkand Jewellery
  House; Zelio-style fake names) — ignored.

Backup: `state.json.bak-20260902-aditya-joshi-x`. Registry 604 → 609.
