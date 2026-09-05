# Screen dimensions — why a stock is where it is, split into independent axes

**Problem this solves.** Every `screenedOut` / tier entry in `data/screen-ranking.json` used to
carry a single free-text `reason` blob that mixed together *unrelated* judgments — "the thesis
doesn't fit", "the chart already ran", "promoters pledge stock", "trailing ROE is weak". The
`vpscreen-audit` past-performance-bias check then keyword-scanned that blob and flagged ~70
entries/run, none actionable, because almost every deliberate screen-out *mentions* a catalyst
while explaining why it doesn't count. Signal drowned in noise, and the one pattern the check
exists to catch — **a real recent inflection buried under a weak multi-year average** (the
2026-08-22 Ujjivan / Deep Industries bug) — was indistinguishable from the 69 non-issues.

**Fix.** Decompose the call into 5 independent dimensions plus one `primary_screen_reason`.
Each is a small closed vocabulary. The `reason` prose stays (humans read it); the structured
block is what the audit and the revisit logic key off.

Some dimensions are **durable** (a mega-cap stays too big to 10x; a pledging promoter stays a
pledging promoter). One is **not**: `technicals`. A name screened out purely because the price
already re-rated or sits at a 52-week high is a *revisit candidate*, not a permanent exclusion —
the setup can look completely different in a quarter. The schema makes that explicit so those
names don't get buried forever.

---

## The block

Written on each entry in `data/screen-ranking.json`'s `screenedOut`, `tierC`, `highCaution`,
and `avoid` arrays (tierA/tierB entries may carry it too, but it mainly matters for the
screened / borderline ones):

```json
"dimensions": {
  "thesis":                 "fit" | "borderline" | "neither",
  "recent_fundamentals":    "strong" | "neutral" | "weak" | "unknown",
  "long_term_fundamentals": "strong" | "neutral" | "weak" | "unknown",
  "technicals":             "supportive" | "neutral" | "stretched" | "unknown",
  "governance":             "clean" | "watch" | "red" | "unknown"
},
"primary_screen_reason": "thesis" | "long_term_fundamentals" | "recent_fundamentals"
                       | "technicals" | "valuation" | "governance" | "size"
                       | "no_thread" | "unclassified"
```

### Dimension definitions

| dimension | what it measures | `strong` / `fit` / `clean` | `weak` / `neither` / `red` |
|---|---|---|---|
| **thesis** | does a 10x-in-2-3y or 100x-in-10y outcome *structurally* fit — TAM, business model, and above all **size** (a ~Rs 30,000 Cr co cannot 10x in 3y regardless of execution) | a credible path to the return magnitude exists | too large / too slow-scaling / commodity with no re-rating path |
| **recent_fundamentals** | the **last 1-2 quarters**: revenue & margin trajectory, a named catalyst that has *started* to show in the numbers, an earnings inflection | latest Q accelerating / margin turn visible / catalyst landing | latest Q de-growth, margin miss, decelerating, profit slump |
| **long_term_fundamentals** | the **trailing 3-5 yr** record: ROE/ROCE level, revenue & PAT CAGR, through-cycle consistency | sustained high ROCE/ROE, steady compounding | low/negative trailing returns, flat-to-negative CAGR, mature single-digit growth |
| **technicals** | price action & valuation-vs-own-history: how much has *already* re-rated, distance from 52-wk high, momentum, multiple vs its band | pulled back / cheap vs history / base building | already +80-100%+ in a year, re-rated 2-3x, at/near 52-wk high, peak-multiple |
| **governance** | promoter & disclosure *habits*: pledging, related-party dealings, auditor exits, SEBI matters, guidance withdrawn, capital-allocation history, promoter selling/exiting | clean record, aligned promoter | material pledge, RPT concerns, auditor resignation, withdrawn guidance, trusted holder exited on trust grounds |

`unknown` = not assessed this pass (don't guess). `unclassified` `primary_screen_reason` = the
mechanical backfill couldn't read it confidently and the rerank task should author it.

### `primary_screen_reason` — the single axis that actually drove the screen-out

Pick the **one** dimension that, if it flipped, would most change the verdict. Priority when
several are bad: `governance` (red) > `thesis` (neither) > `size` > `long_term_fundamentals` >
`valuation` / `technicals` > `recent_fundamentals` > `no_thread`.

- `size` is called out separately from `thesis` for the common "great business, just too big" case.
- `valuation` vs `technicals`: use `valuation` when it's an absolute multiple objection
  (~75x earnings), `technicals` when it's "the move already happened" (re-rated, at highs).
  Both are **non-durable** — see below.

---

## How the audit and revisit logic use this

**`vpscreen-audit` / `audit_state.py`** replaces the keyword spot-check with three precise reads:

1. **MIS-SCREEN (the real bug).** Flag when
   `primary_screen_reason == "long_term_fundamentals"` **and**
   `dimensions.recent_fundamentals == "strong"` **and**
   `dimensions.thesis != "neither"` **and**
   `dimensions.governance != "red"`.
   That is exactly "screened out on a weak trailing average while the recent quarters have
   turned and nothing else disqualifies it" — move to Tier C with "unconfirmed, watch" framing.
   Should be 0-3 entries, every one worth a look.

2. **SOFT SCREEN-OUT (revisit-eligible).** Report — not a defect — every entry whose
   `primary_screen_reason in ("technicals", "valuation")` and `thesis != "neither"`.
   These failed on something that **can easily change later**. They stay eligible for
   `revisit_after_30d` even at merely-`Medium` conviction (the normal rule needs Medium-High+).

3. **`unclassified` count.** How many screened entries still need a real `dimensions` block
   authored by the rerank task. A growing count means the rerank task isn't writing them.

**`revisit_after_30d` rule (§3).** The normal 3-part gate (conviction ≥ Medium-High, thesis ≠
neither, no red flag) gets one carve-out: if `primary_screen_reason in ("technicals",
"valuation")` and `thesis_fit != "neither"`, `revisit_after_30d = true` is allowed to stand
regardless of conviction level — the whole point is to re-check it once the technical setup
resets.

---

## Who writes it

- **`vpscreen-rerank`** (Step 3): authors `dimensions` + `primary_screen_reason` on every
  `screenedOut` / `tierC` / `highCaution` / `avoid` entry as it writes the `reason`, from the
  same `analysis.md` / `conviction-scores.json` read it already does. Carries unchanged entries
  forward with their block intact.
- **`scripts/classify_screen_dimensions.py`** (mechanical backstop): run after the rerank
  rebuild. Fills a conservative block on any entry missing one by parsing its `reason` prose;
  anything it can't read confidently gets `primary_screen_reason: "unclassified"`. Idempotent;
  never overwrites an existing block unless `--force`.
