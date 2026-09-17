# x-cluster-promotion proposal — 2026-09-12

Monthly review. **Not yet applied — `x_cluster.json` is a human-edited file; this is a proposal only.**

## Mechanical scoreboard: empty this cycle

`x-handles/x-handle-scoreboard.md` shows "0 handles with a dossier" (generated 2026-09-02), and `x-handle-ranking-log.md` has never recorded a real run — header only, no dated blocks. 42 per-handle dossiers now exist under `x-handles/dossiers/` (built by `x-handle-triage`'s deep pass), but every `calls[].our_verdict` field in them is still `null` — `regen_x_scoreboard.py` only scores calls with a resolved verdict, so it correctly returns 0 across the board. There is nothing to promote from that pipeline until `x-handle-ranking` actually runs and fills in verdicts.

**Result: no ADD proposals this cycle.**

## Propose ADD to `x_cluster.json` (tier: cluster)

_(none — see note above)_

## Propose DROP

Evidence from `x-cluster-log.md`'s full run history (2026-08-30 inception through 2026-09-10, ~6 weeks):

| Handle | Added | Reason for original add | Evidence for drop |
|---|---|---|---|
| @persistencecap | 2026-08-30 | "Signal & Noise" deck | Lowest volume from day one (6 tweets in initial backfill); zero posts in every run since (08-31 → 09-10). Zero usable signals. |
| @srisiv1 | 2026-08-30 | "prescient, never miss an interview" | 3 tweets in initial backfill, one macro banks note (not a stock call); zero new posts every run since. |
| @dhruvbajaj184 | 2026-08-30 | special-situations | 29 tweets in initial backfill (highest volume of this group), bucketed as macro/psychology from day one; zero new posts since, zero business content ever produced. |
| @prabhakarkudva | 2026-08-30 | PEAD/earnings-surprise commentary | 20 tweets initial + ~10 new on 09-07 — all portfolio-construction philosophy. The PEAD content that motivated the add never materialized. |
| @Anand_shah07 | 2026-08-30 | psychology + themes amplification | Active poster (30 initial, 1-8/run since) but every post is emoji replies / behavioural reflection — never a named stock in 6 weeks. |

**To apply:** remove the entry from `x_cluster.json.handles` for any of the above.

## No change (close to the bar, or too new to judge)

- **@saket1974** (added 2026-08-31) — only ~12 days of history vs. the ~8-week bar; flagged as low-volume at addition. Revisit next cycle.
- **@Finstor85** (added 2026-08-31) — no conviction-tier signal, but 2 watch-list contributions (chennai-petroleum-corporation, iifl-finance) + 1 refreshed watch entry. Not a drop.
- **@itsTarH** (added 2026-08-30) — one conviction candidate (bliss-gvs-pharma) on day one, only already-researched touches since. Falls inside the 6-week window so it doesn't clear the "0 usable calls" bar yet.

## Other note

`x-handles/TRIAGE_STATUS.md` still reads **IN PROGRESS** (50/103 deep-pass handles triaged as of 2026-09-11) — the promotion candidate pool isn't complete yet, and `x-handle-ranking` has not yet run to resolve any dossier calls into scores.

---
Full detail logged in `x-cluster-log.md` under the same date.
