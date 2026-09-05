# Full Stock Research Queue

Extracted from the [source Google Sheet](https://docs.google.com/spreadsheets/d/1j3sUPLk0q6fahFzbNJyTUr51BK68fhXe96u2DpKOXPk/edit?gid=0#gid=0) (a compilation of ValuePickr forum + X posts from ~8 different curators). **101 distinct companies** were identified, deduplicated, and queued for nightly research.

This is the live queue driving the `stock-research-nightly` scheduled task (runs ~11 PM IST daily). Status updates automatically as each stock is researched — see `research/manifest.json` for the machine-readable version, and `docs/` for the finished per-stock Word docs. `⚠` marks a flag the research step needs to resolve (verify size/ticker, red flag, etc.) before treating a name as a serious candidate.

---

## Batch 1
1. Rapicut Carbide Ltd
2. Aarti Surfactants Ltd — highest VP engagement recently, strong results + valuation discussion
3. Apar Industries Ltd — positive EPS growth emphasis
4. Unihealth Hospitals Ltd
5. Oracle Financial Services Software Ltd ⚠ likely large-cap, probably excluded on size
6. Asahi Songwon Colors Ltd
7. Gujarat Containers Ltd
8. Novartis India Ltd ⚠ MNC subsidiary, verify size/liquidity
9. High Energy Batteries (India) Ltd
10. Fluidomat Ltd
11. Trejhara Solutions Ltd
12. ~~BlackBerry Ltd~~ — excluded, foreign mega-cap
13. ~~Nokia Corp~~ — excluded, foreign mega-cap

## Batch 2
14. Alan Scott Ltd — ~8X, 2023 management-change bet
15. Accel Ltd
16. Hitech Gear Ltd
17. Samkrg Pistons & Rings Ltd
18. Waaree Renewable Technologies Ltd — ~158X cited ⚠ verify current market cap
19. Stylam Industries Ltd — ~52X cited
20. Ritco Logistics Ltd — ~15X cited, near 52-week high
21. Bajaj Steel Industries Ltd — ~9.5X cited
22. JITF Infra Logistics Ltd — ~7.8X cited
23. BCL Industries Ltd — ~3.4X cited
24. Beardsell Ltd — ~2.7X cited
25. Darjeeling Industries ⚠ **regulatory red flag — SEBI order/manipulation allegations mentioned in source**
26. Transpek Industry Ltd

## Batch 3
27. Bansal Roofing Products Ltd
28. NDL Ventures Ltd
29. Ather Energy Ltd ⚠ large recent IPO, likely too large for thesis
30. Vaxfab Enterprises Ltd
31. AVI Polymers Ltd ⚠ verify exact listed entity
32. Sai Life Sciences Ltd — Tier 1 CRAMS/CDMO
33. Anthem Biosciences Ltd — Tier 1 list
34. Unimech Aerospace and Manufacturing Ltd
35. Intellect Design Arena Ltd
36. Eureka Forbes Ltd
37. Timken India Ltd ⚠ verify upper-bound size fit
38. Sansera Engineering Ltd
39. Praj Industries Ltd

## Batch 4
40. Cohance Lifesciences Ltd
41. Viyash Life Sciences ⚠ verify listed status
42. Tatva Chintan Pharma Chem Ltd — "Ghoomega + Machayega" setup
43. Sona BLW Precision Forgings Ltd (Sona Comstar) ⚠ verify size
44. Cemindia Projects Ltd (formerly ITD Cementation India) ⚠ ~₹22,800–23,500 Cr mcap, midcap upper range
45. MTAR Technologies Ltd
46. Devson Catalyst Ltd ⚠ SME platform, verify liquidity
47. Jupiter Wagons Ltd — past multi-bagger example
48. Yasho Industries Ltd — already a multi-bagger
49. Haldyn Glass Ltd
50. Balaji Amines Ltd
51. ADF Foods Ltd
52. Tips Music Ltd (Tips Industries)

## Batch 5
53. Saregama India Ltd
54. TPL Plastech Ltd
55. Laurus Labs Ltd ⚠ ~₹1 lakh cr mcap cited — likely large-cap territory
56. Azad Engineering Ltd — DRDO turbo-jet delivery, Mitsubishi contract
57. Axiscades Technologies Ltd
58. Sedemac Mechatronics Ltd — recent IPO, sensor-less ISG tech
59. Manorama Industries Ltd
60. RNIT AI Ltd ⚠ verify listed entity/ticker
61. Pricol Ltd — demerger catalyst
62. GPT Healthcare Ltd — "dark horse" hospitals name
63. Dynamic Cables Ltd
64. Schloss Bangalore Ltd (The Leela) ⚠ verify ticker/size, likely midcap+

## Batch 6
65. Ramkrishna Forgings Ltd
66. Shriram Pistons & Rings Ltd
67. TVS Holdings Ltd ⚠ large-cap holdco, likely excluded on size
68. Adani Ports and SEZ (APSEZ) ⚠ large-cap, **excluded on size**
69. JSW Infrastructure Ltd ⚠ large-cap, likely excluded
70. RR Kabel Ltd — strongest detailed thesis per source
71. Macpower CNC Machines Ltd
72. Selan Exploration Technology Ltd ⚠ verify vs "Antelopus Selan Energy" naming
73. Pyramid Technoplast Ltd — ultra-smallcap, higher risk
74. Shilpa Medicare Ltd — "very highly recommended"
75. Entero Healthcare Solutions Ltd
76. Kerala Ayurveda Ltd

## Batch 7
77. Fredun Pharmaceuticals Ltd ⚠ verify listed status — may be private/unlisted
78. Technvision Ventures Ltd ⚠ verify exact listed entity
79. Vistar Amar ⚠ verify listed status/ticker
80. Repono ⚠ likely unlisted/private
81. Glen Industries ⚠ verify listed status/ticker
82. Galaxy Supermarket ⚠ likely unlisted
83. PDS Limited
84. Sambhv Steel Tubes Ltd
85. Gravita India Ltd
86. Concord Biotech Ltd — curator's disclosed portfolio holding
87. Quality Power Electrical Equipments Ltd
88. NRB Bearings Ltd
89. Shivalik Bimetal Controls Ltd

## Batch 8 (overflow)
90. Capital Small Finance Bank Ltd
91. Gufic Biosciences Ltd
92. Repco Home Finance Ltd
93. Edelweiss Financial Services Ltd ⚠ verify which listed entity
94. Neogen Chemicals Ltd
95. Orchid Pharma Ltd
96. Go Fashion (India) Ltd
97. Raymond Lifestyle Ltd ⚠ verify size, may be midcap+
98. Jeena Sikho Lifecare Ltd
99. Technocraft Industries (India) Ltd
100. Thermax Ltd ⚠ verify upper-bound size fit
101. GMM Pfaudler Ltd
102. MV Electrosystems Ltd (MVEL) ⚠ verify listed status
103. Amrutanjan Health Care Ltd
104. Standard Glass Lining Technology Ltd — curator disclosed holding
105. Aether Industries Ltd
106. Triveni (entity unclear) ⚠ **must disambiguate** — two listed "Triveni" companies exist
107. India Glycols Ltd
108. Piccadily Agro Industries Ltd

---

## How this runs
- **Schedule:** nightly, ~11 PM IST, via the `stock-research-nightly` scheduled task (needs the Claude Code app open at that time; if closed, it runs on next launch instead).
- **Pace:** ~12–15 stocks fully researched per run — expect this queue to take roughly 7–9 nights depending on how much depth each name needs.
- **Per-stock output:** a `.docx` in `docs/` covering fundamentals (Screener.in), technicals (Weekly/Monthly MACD + Bollinger Bands — the CM_Ult_MacD_MTF indicator isn't available for unattended runs, so this is the automated fallback), ValuePickr + X sentiment, BSE corporate actions/red flags, bull/bear case, and a 10x-in-2-3-years plausibility verdict.
- **Final output:** once every name is done, `docs/00_FINAL_RANKING.docx` — the consolidated ranked list with the scoring framework applied.
- **This is research/analysis for informational purposes only — not personalized financial advice.**
