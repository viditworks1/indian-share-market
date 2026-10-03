# x-cluster-promotion proposal — 2026-10-03

Monthly review. **Not yet applied — `x_cluster.json` is a human-edited file; this is a proposal only.**

**Date: 2026-10-03 (generated from scoreboard dated 2026-09-26, full triage at 103/103 depth-pass dossiers as of 2026-09-13).**

## Mechanical scoreboard status: full triage, zero resolved verdicts

The x-handles deep-pass triage is complete (103/103), with dossiers built for all. However:

- `x-handle-ranking` has **not yet run** to fill in `calls[].our_verdict` fields in any dossier (still all `null`).
- `regen_x_scoreboard.py` only scores calls with a resolved verdict, correctly returning 0 resolved calls across all 103 handles.
- **Result: the scoreboard remains empty (all scores at baseline 40.0 for unscored handles), yielding no promotion candidates per the ≥6-resolved-calls rule.**

No candidates to propose for ADD until `x-handle-ranking` executes its first real run and resolves dossier verdicts.

## Propose ADD to `x_cluster.json` (tier: cluster)

_(none — see status above)_

## Propose DROP

Evidence from `x-cluster-log.md` run history (2026-08-30 through 2026-09-28, ~4 weeks since prior proposal):

| Handle | Tier | Added | Evidence for drop |
|---|---|---|---|
| @persistencecap | cluster | 2026-08-30 | Lowest volume from day one (6 tweets in the initial 30-day backfill) and zero posts returned in every single subsequent run (08-31, 09-01, 09-02, 09-04, 09-05, 09-07, 09-08, 09-09, 09-10, 09-12, 09-22, 09-24, 09-26, 09-28). Zero usable signals, zero even attempted content. |
| @srisiv1 | cluster | 2026-08-30 | 3 tweets in the initial backfill, one macro/directional note on PSU + private banks (08-30, logged, not a stock call). Zero new posts in every run since 09-01 through 09-28; one isolated post on 09-26 was insurance-sector bearish (no single stock named). No named-stock signal ever. |
| @dhruvbajaj184 | cluster | 2026-08-30 | 29 tweets in the initial backfill (highest volume of this group) bucketed as "mostly macro/psychology/framework" from the start. Zero new posts in every single subsequent run (09-01 → 09-26). 09-28 produced 4 posts (GRT Jewellers/TBZ acquisition threads, portfolio-construction musings) — all already-researched or non-stock context; no business content or conviction views ever produced. |
| @prabhakarkudva | cluster | 2026-08-30 | 20 tweets in the initial backfill. Every run since (notably ~10 new posts on 09-07, 1 post on 09-24 that was structure commentary, 1 blocked post on 09-28) has been pure portfolio-construction/regime-awareness philosophy with zero named stocks. The PEAD/earnings-surprise content that motivated adding this handle has not materialized in 4+ weeks. |
| @Anand_shah07 | cluster | 2026-08-30 | Steady posting volume (30, then 1-8 new tweets most runs, 12 on 09-22, 9 on 09-24, 2 on 09-26, 4 on 09-28) but every single logged post has been emoji replies / behavioural reflection, never a named stock or thesis. Zero usable signals in 4+ weeks despite active posting. |

**To apply:** remove the corresponding entry from `x_cluster.json.handles` for any of the above.

## No change (current cluster members with activity or recent adds)

- **@saket1974** (cluster; added 2026-08-31) — ~5 months of history now. Low-volume (5/30 initially, zero new posts in all runs 09-01 through 09-28). No signals. Worth dropping next review if the pattern holds.
- **@Finstor85** (cluster; added 2026-08-31, Ameya) — low posting frequency. Produced 2 watch-list contributions (09-02 and 09-08) plus contributed to refreshed watch entry (09-08). 09-24 added Midhani as new conviction candidate. Not a drop, but tracking below conviction floor.
- **@itsTarH** (cluster; added 2026-08-30) — thin throughout (one conviction candidate, bliss-gvs-pharma, on 08-30; only already-researched touches since). Recent runs (09-22, 09-24, 09-26, 09-28) show zero new posts or only out-of-scope content (AMD, Saudi crude, #TheWrap plugs). Below conviction grade but not yet a clear "0 usable" drop.

---

Note: `x-handles/x-handle-ranking-log.md` remains header-only. The promotion candidate pipeline is complete in scope but awaiting verdict-resolution to generate scores above baseline.
