# Auto-discovery like-threshold: recalibration (2026-08-22)

## Who consumes this
`vpscreen-portfolio-threads` (a scheduled task, prompt not editable by this agent) uses a
title-pattern search to auto-discover new portfolio/journal threads on ValuePickr worth tracking.
It currently gates candidates on a cumulative absolute threshold. This note hands off a
recalibrated, rate-based replacement rule for a human/orchestrator to paste into that task's
prompt.

## The problem with the old rule
Old gate: `like_count >= 500 AND participant_count >= 20`

`like_count` and `participant_count` are cumulative totals that only grow with a thread's age and
post volume. This structurally favors old, long-running threads and would take a newer-but-
genuinely-good contributor years of steady posting to clear 500 total likes - missing them
entirely for that whole window, regardless of how good their per-post signal actually is.

## Calibration data
Pulled live via the Discourse API (`https://forum.valuepickr.com/t/<slug>/<id>.json`, which
exposes `like_count`, `posts_count`, `participant_count`) on 2026-08-22:

| Thread | likes/post | posts | participants | Verdict |
|---|---|---|---|---|
| Phreak's thread (reference "great" thread) | 21.88 | 300 | 140 | clearly good |
| "My portfolio updates and investment journey" | 3.71 | 268 | 72 | genuinely good, but wouldn't clear old 500-like rule until ~post #135 |
| "Malhar's Investing Thoughts" | 3.81 | 36 | 19 | good newer thread, only 137 total likes - **never** clears the old absolute rule |
| "Rahul Kumar's Portfolio Review" | 0.70 | - | - | noise |
| "Thoughts on my portfolio" (unnamed thread) | 0.33 | - | - | noise |
| noise cluster generally | < 1.2 | - | - | noise |

The gap between the genuinely-good threads (3.71-21.88 likes/post) and the noise cluster
(< 1.2 likes/post) is wide and clean - a rate-based cut sits comfortably in between with margin
on both sides. "Malhar's Investing Thoughts" is the key illustration: a good, newer thread that
the old absolute rule would miss forever (only 137 cumulative likes, nowhere near 500) despite a
per-post engagement rate roughly on par with the other confirmed-good thread.

## New rule

```
(like_count / posts_count) >= 3.0
AND participant_count >= 15
AND posts_count >= 20
```

- **`like_count / posts_count) >= 3.0`** - the core recalibration. Sits well below the confirmed-
  good range (3.71-21.88) and well above the noise cluster (<= 1.2), so it has margin in both
  directions rather than sitting right at the boundary of either group.
- **`participant_count >= 15`** - lowered from 20 to loosen the old rule's other cumulative-count
  bias (fewer total participants for a newer thread), while still requiring the discussion isn't
  just one or two people talking to themselves. All three "good" reference threads clear this
  comfortably (19, 72, 140).
- **`posts_count >= 20`** - new floor, not present in the old rule. Needed because a rate-based
  gate is vulnerable to a small-sample false positive - e.g. a thread with 3 posts and 10 likes
  would post a 3.33 likes/post rate and pass on rate alone despite having no track record at all.
  Requiring at least 20 posts before the rate is trusted gives statistical significance to the
  ratio. All three reference "good" threads clear this by a wide margin (36, 268, 300 posts).

## Status
Formula tested against the calibration data above (confirms all 3 known-good threads pass, all
known-noise threads fail). Not yet applied to the live `vpscreen-portfolio-threads` scheduled
task prompt - that edit is reserved for a human/orchestrator to avoid two agents racing to
overwrite the same task prompt concurrently.
