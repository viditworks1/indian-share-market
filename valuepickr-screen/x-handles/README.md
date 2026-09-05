# X-handles pipeline (new, 2026-09-02)

Purpose: work through the user's full X (Twitter) finance following list
(`Vidit_Finance_Following_List.xlsx`, 297 accounts), find the ones that actually
make **India-listed single-stock calls**, do a deep 6-month read of each, score
them against our own independent research, and grow the trusted X cluster
(`../x_cluster.json`) on evidence — feeding new names into the ValuePickr open
screen for scanning + deep-dive along the way.

This is the "untrusted funnel" that sits *upstream* of `x-trusted-cluster`
(that daily task only reads handles already promoted into `../x_cluster.json`).

## Files
- `x_handle_registry.json` — every account, classified. Buckets:
  - **A1** (48) — high-signal single-name caller → deep pass
  - **A2** (55) — probable / lower-volume / more thematic → deep pass
  - **B** (100) — equities-adjacent but rarely names actionable stocks → no deep pass
  - **X** (65) — not India stock-picking (US, VC/startup, PF, fintech founders, RE, tax, macro) → excluded
  - **CC** (22) — credit-cards category → ignored per user instruction
  - **cluster** (8) — already in `../x_cluster.json`, covered by `x-trusted-cluster`
  - 103 deep-pass handles total.
- `dossiers/<handle>.md` — per-handle deep-pass output. First ```json block is the
  machine-readable front-matter (contract in `../scripts/regen_x_scoreboard.py`);
  prose below it is the human read.
- `dossiers/_archived/` — dossiers of handles dropped from re-scoring.
- `x-handle-scoreboard.md` — mechanical ranking (regen script), promotion / drop lists.
- `x-handle-triage-log.md`, `x-handle-ranking-log.md` — dated run logs.
- `TRIAGE_STATUS.md` — one line: `IN PROGRESS` / `SCOPE COMPLETE <date>`. `vpscreen-audit`
  watches this to know when `x-handle-triage` can be deleted.

## Routines
| Task | Cadence | Scope |
|---|---|---|
| `x-handle-triage` | 2×/day (10:00, 20:00) | **Finite backlog.** 5 deep-pass handles/run, A1 first, oldest xlsx_row first. One Apify run/day, 183-day window. Writes dossier; seeds genuinely new conviction-bearing names into `state.json` as `source:"external-lead"`, `x_untrusted:true` (no floor). Self-retires at SCOPE COMPLETE. |
| `x-handle-ranking` | weekly (Sat 15:00), → monthly after ~8 weeks | Fills `our_verdict` / `since_call_pct` per call in each dossier (≤3 WebSearch price checks/run, rotated), regenerates the scoreboard, emits promotion/drop candidates. |
| `x-cluster-promotion` | monthly (1st, 11:00) | Reads the scoreboard, writes a dated **proposal** block (ADD/DROP/PRIMARY) to `../x-cluster-log.md`. Never edits `../x_cluster.json` — that stays a human action. |

## Cleanups (planned)
1. `x-handle-triage` writes `SCOPE COMPLETE` to `TRIAGE_STATUS.md` when the pending
   backlog hits 0. `vpscreen-audit` then flags it in `../audit-log.md` for the user
   to **delete the `x-handle-triage` task**. Its SKILL.md is left on disk.
2. After triage completes: promoted handles live in `x_cluster.json` (daily
   `x-trusted-cluster` covers them forever); their registry `tier` → `cluster`.
3. `x-handle-ranking` steps down weekly → monthly once scores stabilise
   (user changes the cron), and stops re-scoring `tier:"rejected"` handles
   (dossier moved to `dossiers/_archived/`).
4. Registry-shape + stale-`pending` hygiene folded into `vpscreen-audit`.
