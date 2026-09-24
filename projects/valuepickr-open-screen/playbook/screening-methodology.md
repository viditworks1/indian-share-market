# Screening Methodology

Concrete, checkable technical/quantitative screening rules pulled from trusted threads.
These are candidate inputs for a possible `technical_health` signal on researched stocks —
kept separate from the fundamentals-driven `conviction_score`, not blended into it, since they
answer a different question (is this a good *entry point*, not is this a good *business*).
See project note: not automatically "adopt the picks" — see the sourcing caveat on each rule.

## Where the pieces sit in sequence

```
trusted signal / 52W-high breakout   →  DISCOVERY
ROCE / growth / debt / red-flag gate →  QUALITY GATE      (conviction_score — "good business?")
commitment chain + expectation gap   →  EDGE TEST         (expectation_gap_score — "mispriced, with a catalyst?")
                                                           see guidance-and-expectation-gap.md
30-week EMA weekly cross              →  ENTRY TIMING
```

The breakout / stage-2 rules below and the technofunda pullback rules are the ENTRY-TIMING
layer. The EDGE TEST is a separate step: a name can pass the quality gate, be endorsed by a
trusted user, and sit above its 30W EMA, and still be a poor buy because its guidance is
already fully in the price. `guidance-and-expectation-gap.md` is the method for catching that;
`../scripts/GUIDANCE_EXPECTATION_SCHEMA.md` is the data it produces.

## Momentum/trend screening universe (Mudit.Kushalvardhan, rank #16)

*Mudit's Portfolio*, post #283 (2024-09-25): his stated screening criteria for the
rank-based-momentum phase of his approach —
- Universe: Smallcap 250 and Microcap 250 (two separate universes, top 10 ranked from each)
- Within 20% of all-time high AND within 20% of 52-week high
- Minimum daily volume: ₹1 crore
- Price above both the 100-day EMA and the 200-day EMA
- Momentum score/ranking sourced from a paid screener (momoindiascreener.com), re-ranked periodically

**Sourcing caveat:** by his own later account (see `investor-psychology.md`, post #332), this
exact strategy phase "mostly all stocks have underperformed nifty in a big way" over ~2 years
4 months. The screening mechanics are recorded as *interesting/checkable*, not as validated —
see the revised approach below, which he adopted after this admitted failure.

## Automatic exit tied to the same criteria as entry (Mudit.Kushalvardhan)

Post #287 (2024-09-27) and #289 (2024-09-27): "If the stock price falls more than 20% from its
52W high" or "the stock falls below the worst rank during rebalance" — both are just the entry
screen (within 20% of 52W high; top-N by rank) applied in reverse, so there's no separate
discretionary exit judgment.

## Revised approach: technical entry first, fundamental gate second (Mudit.Kushalvardhan)

Post #368 (2026-07-10), describing the strategy adopted *after* the rank-momentum failure:
"I watch chart and enter when chart is in stage 2 and for fundamental factors, I check
marketsmithindia to check EPS ranking, RoE, ROCE, quarterly sales and quarterly profit and
mostly CANSLIM criteria… But more focus is on Charts… I would categorise myself as a
Positional Trader." Sequencing is explicit: technical/stage screen narrows the universe first,
fundamentals are then used to *reject* candidates rather than to originate them. Self-reported
result (post #371, unverified, no disclosed comparison methodology): "outperformed Nifty 50 by
around 15%... Compared to Smallcap 250 universe, 8% to 10% outperformance," holding period
"around 3-4 months, and sometimes 6 months."

## Timeframe consistency matters for breakout reads (Mudit.Kushalvardhan)

Post #327/#328 (2025-01-06), a self-caught mistake: "A stock which is looking like it's
breaking out on daily time frame, may be the extended one on weekly chart... by looking at
daily chart, I got wrong perspective and my entry got wrong." Practical rule extracted: check
the higher timeframe (weekly) before acting on a daily-chart breakout signal, especially for
longer-hold positional entries.

## Valuation is a durability/growth question, not a TTM P/E snapshot — and P/E can be the wrong tool for the business entirely (phreakv6, rank #2, core-tier)

*Phreak's Thoughts, Ideas and Opinions*, post #221 (2026-03-27): "valuation is not always just
the TTM P/E. Doing so ends up in a lot of value traps. The differential insight can only come
from looking at capabilities that aren't captured in the balance sheet as intangibles... its
the growth and longevity that are primary drivers of valuation." Stated track record backing
the claim: buying "50 P/E+ consistently" over the prior period (Wockhardt, Shaily, Axiscades
cited) with "2x-4x in few of these even when market did nothing." Companion point from post
#308 (2026-08-05), on choosing which valuation tool to apply at all: "Picking the right
valuation tool to use is the first skill - knowing the nature of business (is it cyclical...?
growing cash flow...? stable business without growth?)... Its important not to make big
blunders like valuing businesses on P/E which should be valued by P/B (most common error that
keeps recurring)." Caveat stated in his own words in post #221: "This strategy will not work
as well in a roaring bull market... We are nowhere close to a roaring bull market at present"
— the high-P/E-for-durability approach is explicitly conditioned on the market regime, not
presented as a universal rule.

## Breakout-of-highs as a discovery filter, fundamentals as the confirmation that separates it from a pump (hitesh2710, rank #1, elevated-tier)

*Hitesh portfolio*, post #8043 (2025-10-28) and post #8056 (2025-10-31): his stated screening
method, credited to the books *How to Make Money in Stocks* (O'Neil) and *The Next Apple*
(Ivanov) — "if a stock starts trading at 52 week highs, or multi year highs, or all time
highs, then it usually does so for a reason... Amongst all the 52 week, or multi year or all
time high breakouts, the most suitable for investment are those where fundamentals support the
charts." He's explicit that the breakout alone isn't sufficient: "Many a times when a stock
clears all time highs, after many years, it only does so based on promises of a bright future.
Current numbers may not be too exciting... Those are the situations when we need to dig deeper
and try to figure out the investment triggers." Worked example (HBL Engineering): price hit an
all-time high of 76.50 in Jan 2018, crashed to 9.30 in the Mar 2020 Covid low, then broke back
above the 76.50 all-time high in Feb 2022 "in the process forming a nice multi month rounding
structure" before its strong uptrend began in June 2023 — the breakout was the trigger to look
closely, the annual report and thread research were what confirmed it wasn't a false one.
Explicit warning against the shortcut version of this method: "rather than ask for spoon
feeding with questions like 'what do you think about so and so company'... We need to learn the
method rather than ask for spoonfeeding."

## Bear-market resilience as a leading screen for the next rally's winners (hitesh2710, rank #1, elevated-tier)

*Hitesh portfolio*, post #8083 (2026-01-03) and post #8089 (2026-01-22, near-identical restatement
in response to a member's question about "how to catch the cycle"): the checkable criteria he
gives for building a watchlist *during* a correction, before the next leg is confirmed —
stocks "holding key levels, say staying above 200 dema," or that "have corrected not more than
20-25% from their swing highs even during strong market declines," or that "break out first
when markets show signs of reversal." Sequencing stated explicitly (post #8089): compile the
resilience-based list first using technicals, then "don the fundamental lens and look closely
at stocks showing resilience... and find out if there are any discernible triggers" — technical
screen narrows the universe, fundamentals decide which of the survivors to act on. He dates his
own use of the method to finding HBL Engineering in May 2022, when it was attempting a 4-year
high in the middle of a broader market correction. Caveat, his own words: "this approach also
may fail during highly turbulent markets which remain volatile for long."

## A capex-driven thesis earns a fixed grace period before being recalibrated, not indefinite patience

hitesh2710 (rank #1, elevated-tier) — *Hitesh portfolio*, post #7731 (2024-05-09), using Usha
Martin as the live example: "In case of fundamental bets, the basic premise is you have a rough
idea how things are going to pan out. There can be a delay of a quarter or two, but if company
is on a growth trajectory, then it will deliver in due course... In these kind of situations I am
not too perturbed by flat results because there is promise of good numbers a quarter or two down
the line. Even after that kind of wait the numbers do not come around I would recalibrate my
thesis." The management had guided that capex-driven results would show "from Q1 FY 25 onwards";
he treats a quarter-or-two slip against a specific guided milestone as normal noise, but sets an
explicit outer bound (two quarters past the guided date) beyond which continued underperformance
converts from "wait" to "recalibrate the thesis" — a checkable trigger rather than open-ended
conviction-holding.

## Narrative-driven and numbers-driven multibaggers are different animals, and most narrative stories don't deliver (hitesh2710, rank #1, elevated-tier)

*Hitesh portfolio*, post #8123 (2026-08-19), titled by him "NARRATIVE VERSUS NUMBERS": he splits
multibagger candidates into two categories. Narrative-driven — "talk about a particular sector
or market segment being too exciting for the future... stock price starts rising and keeps
going up and up. Earnings growth are still a few quarters away... by the time earnings start...
most of the juice is out of the stock" — with an explicit, stated base rate: "Maybe one or two
out of ten companies can get into this category" of actually delivering enough growth for
valuations to sustain or expand; the rest "fizzle out... or go sideways for prolonged periods."
Numbers-driven — "very strong growth in numbers, and often they keep showing up better than
expected... a good scope of a head cocktail of growth plus PE rerating" — durable until growth
stops keeping pace with valuation. Practical use stated in the same post: "while evaluating any
investing opportunity these days, its important to slot what kind of investing landscape the
particular company fits into" before deciding how much conviction the current price action
deserves. A useful companion filter for the same purpose, post #8122 (2026-08-19), on a stock
he was asked about but hadn't researched: a quick market-cap-to-sales and TTM-PE sanity check —
"if the valuations are totally out of whack, I dont even bother to look at the company."

## Technofunda pullback rule: buy dips to the 50-DMA/20-WMA only in names already validated by fundamentals (phreakv6, rank #2, core-tier)

*Phreak's Thoughts, Ideas and Opinions*, post #268 (2026-07-08): "I use technicals to instruct
my buy/sell decisions too but never without support from fundamentals... Technofunda approach
works great if followed with equal importance to both." The checkable entry rule: "look to buy
pullbacks to 50-dma in strong trending stocks or 20-WMA which usually gives a nice 20%
discount." His stated complaint is about doing it backwards — treating a stage-2 chart as
sufficient justification on its own, then abandoning the fundamental narrative the moment
price retraces: "All the gung-ho fundamentals that make their way out when stock is in stage-2
are nowhere to be found all of a sudden... Usually nothing changes in fundamentals in a month
in most businesses." The rule is an entry-timing tool for a name already judged worth owning
(see the sector-commitment sequencing in `reading-a-sector.md`), not a screen for finding
names in the first place.

## Treat an IPO's holding horizon as conditioned on the market regime it listed into (Vivek_6954, rank #4, elevated-tier)

*Vivek Gautam Portfolio*, post #1219 (2025-01-18), responding to a question about whether he
still held an IPO that had round-tripped back to its issue price: "IPOS are mostly trades
specially if they r bull mkt ipos n held with a strict stop loss. Bear mkt IPos come at good
valuation n create good wealth." A checkable, binary sorting rule: an IPO priced into a hot bull
market is treated as a trade with a hard stop, not a holding, on the reasoning that bull-market
issue pricing has little valuation margin baked in; an IPO priced during weak/bear conditions is
treated as a candidate for genuine long-term holding, on the reasoning that issuers and their
bankers can't demand the same premium when sentiment is poor. Distinct from a stock-specific
call — the rule sorts *how* to hold an IPO, not *which* one to buy.

## Cap the holding period at entry, and let target-reached or thesis-timeline slippage trigger the exit (vikas_sinha, rank #6, elevated-tier)

*The Anti-Portfolio*, posts #695/#699/#705 (2024-11-01/09/13, backfill) and later confirmed at
post #829 (2026-08-19, forward-check): "My setup is looking for 1-2 years timeline, structural
uplifts since I don't have preference/bandwidth to do much market tracking/trading." In the
earlier "Diwali cleaning" batch he applied this mechanically across six simultaneous exits, each
with a one-line stated reason tied to the same clock — "Indraprastha medical had crossed my
target, further return is expected to be muted due to lack of expansion plans"; "Time techno had
increased quite a bit and further growth can be slow" (exited two weeks later, post #699:
"already quite close to my target, further growth plans can take a decent amount of time, hence
I exited"); and, on a name whose story kept extending, post #705: "Looks like have to become a
long term investor here, which I wouldn't like to be, hence likely exit." The checkable rule:
decide the expected holding horizon (here, explicitly 1-2 years) before buying, and treat a
thesis that would require holding *longer* than that horizon as a sell signal in itself,
independent of whether the position is at a profit or loss. Distinct from the IPO-specific
holding-horizon rule below — this one applies the same logic to any position, sized around the
investor's own stated bandwidth constraint rather than the market regime at entry.

## Don't extend patience to the next capacity tranche when the current one isn't being monetised (vikas_sinha, rank #6, elevated-tier)

*The Anti-Portfolio*, post #836 (2026-08-28, forward-check): asked why he exited Shilchar
Technologies rather than waiting for the Apr-2027 capacity expansion to come on stream —
"Shilchar is facing issues monetising even the previous tranche of the expansion, so I wasn't
willing to wait for more." The checkable rule: when a capex-cycle company adds capacity,
require evidence that the *prior* expansion is being converted into revenue/utilisation before
underwriting the *next* one. A pipeline of announced capacity is a bear point, not a bull
point, until the last block is filled — extending the holding period to wait for tranche N+1
while tranche N sits underutilised is how a growth thesis quietly becomes a value trap.

## The 4-box filter (tailwind + TAM + moat + valuation), and the clustered-tailwind corollary (phreakv6, rank #3, core-tier)

*Phreak's Thoughts, Ideas and Opinions*, post #330 (2026-09-01, love=83), answering how he
picks: "I try to see if tailwind+tam+moat+valuation is satisfied (at least two or three). Very
rarely all 4 click, especially in today's market where everyone is using similar filters and
are all having access to powerful AI models." The checkable rule is the explicit hurdle —
score an idea on four independent boxes and require **at least 2-3 of 4**, treating all-4 as a
rare event rather than the target. The corollary he draws in the same post: "Sometimes
tailwinds are clustered, so that helps in looking at other plays for same tailwind - classic
example recently is AI/data centers." Once one play on a tailwind clears the filter,
deliberately enumerate the adjacent plays on the *same* tailwind rather than treating each as
an unrelated idea — he went from Aeroflex and Mtar (two AI/DC ideas from friends) to studying
"memory, power, cooling etc." as one cluster, using sector-specific resources (semianalysis)
to build the tailwind/moat understanding that the filter depends on. He is explicit that a
filter everyone else also runs (now amplified by common AI tooling) erodes the valuation edge,
so the differentiated work is the depth on tailwind and moat, not the screen itself.

## Not all single-customer/single-product concentration is the same risk (phreakv6, rank #3, core-tier)

*Phreak's Thoughts, Ideas and Opinions*, post #333 (2026-09-03, love=39), replying to a
comparison between BlueJet's single-molecule CDMO exposure and Mtar (single client Bloom) /
Yash Highvoltage (single product, bushings): "I don't think its an equivalent comparison."
For a single-molecule CDMO the risk is compounding — de-stocking even in a blockbuster molecule
(cites bempedoic acid), NDAs and CMO opacity hiding whether the molecule has peaked, innovators
deliberately diversifying to a second/third source once reliable, and separately the molecule
itself losing share to a competing innovator drug or going off-patent to generics (rimegepant
losing to atogepant; baxdrostat vs lorundrostat; enzalutamide generic vs darolutamide) — "moat
is strong but not impenetrable." The checkable counter-test for whether a concentration is
actually low-risk: (1) how many qualified competitors exist worldwide (Mtar's SOFC hotbox has
one, Kaori Heat; bushings has only 9 global makers); (2) how long and how switching-costly is
the incumbent relationship (Mtar-Bloom traces back 15-20 years and the product isn't easy to
requalify elsewhere); (3) is there a near-term de-stocking/peak-sales ceiling, or is the
tailwind structural for several years (no de-stocking risk in Mtar's SOFC ramp for 2-3 years);
and (4) is the company adding a further moat layer that competitors can't easily replicate
(Yash backward-integrating into transformer cores, which "no one else is" doing, pushing
margins to 30-35% in 3 years). A dependency clears as durable only when most of these four
check out — a single molecule facing de-stocking, generic-cliff and multi-source risk
simultaneously fails all four and is a materially different risk than a single customer/product
with few qualified competitors and long switching costs.

## Rank-and-yank your idea pipeline under a hard cap, even a self-imposed one (phreakv6, rank #3, core-tier)

*Phreak's Thoughts, Ideas and Opinions*, post #330 (2026-09-01): "because my capital is small
and I want it to perform the best, I am extremely picky ... even if several ideas seem very
interesting, I make it a point to rank and yank (look up stack-ranking if not familiar) - we
work best when working under such constraints even if they are made up." The habit: force every
interesting idea into a single ordered list and cut below a fixed line, and if you don't have a
real capital constraint doing that job, impose an artificial one — the ranking discipline is
the point, not the size of the account. He pairs it with an observed emotional payoff that acts
as a check that the process is working: "I have almost no fomo when I reject something
consciously." A conscious, ranked rejection that leaves no FOMO is the signal the filter is
calibrated; a rejection that keeps nagging is worth revisiting (see the asymmetric-regret entry
in `investor-psychology.md`).

## Watch for "peak margin" quarters — a great print can still mark the top if the market reads it as unsustainable (Vivek_6954, rank #5, elevated-tier)

*Vivek Gautam Portfolio*, post #1245 (2026-09-02, love=26) names it as one of two recurring
mistakes in his 14-year record: "delay in understanding the peak margin cases cos." Post #1254
(2026-09-03) gives the concrete mechanism with Kernex as the example: "Watch peak margin cases
closely. Eg kernex came with great nos this qtr yet stock fell from 2500 to 1600 odd in matter
of days." The lesson isn't "sell on good results" — it's that a screening/monitoring process
needs to actively ask, on every beat-and-raise quarter, whether the margin print looks durable
or looks like a peak that the market will fade even as the headline number impresses. He later
disclosed exiting Kernex (post #1245) after this pattern played out.
