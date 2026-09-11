#!/usr/bin/env python3
"""
stale_reverify.py — automatic, age-driven re-verification backlog for vpscreen-scan (tier 5).

Complements the existing MANUAL `conviction_needs_reverification` flag (tier 2 — set by a
human or another task when something specific happens: a bug fix, a material new datapoint,
a Q-beat) with an AGE-driven backstop, since this project is meant to run unattended for
months and an already-`researched` call can simply go stale with nobody noticing.

User instruction (2026-09-11): once a researched call goes stale, don't blindly re-run it —
skip it if it never earned the scan budget in the first place (both `conviction_score` and
`master_score` below a floor — most of this project's universe is a screened-out "neither"
call and doesn't deserve ongoing forum-check cycles), and for whatever DOES qualify, order
strictly by `pool_priority` (a 50/50 blend of conviction_score and master_score — the same
shape build_deepdive_queue.py uses for its own rotation, kept consistent across the project),
not by how long it's been sitting. "Prioritize newer candidates" (fresh discovery / Step 0.5
tiers 1-4.8) still comes first in vpscreen-scan's Step 2 fill order — this tier (5) only fills
whatever slots are left over.

Eligible = status "researched", red_flag_tier not a settled AVOID/EXCLUDE (a HIGH CAUTION call
is kept eligible — same convention as build_deepdive_queue.py), NOT already carrying
`conviction_needs_reverification: true` (that stays tier 2's own lane, so a stock is never
double-counted), and `last_analyzed_date` at least STALE_DAYS old (aligned with discover.py's
STALE_CANDIDATE_DAYS=45, so "stale" means the same thing everywhere in this project).

Cheap and read-only: one state.json read (same pattern discover.py already uses — this runs
as a script outside the agent's context window, so loading the full file here is fine per the
project's "don't read state.json whole" rule, which is about the AGENT's own reads via
get_stock.py). Does not open any data/<slug>.json file — conviction_score/master_score are
already mirrored onto the state.json entry by refresh_derived.py's compute_* scripts.

Usage:
  python3 stale_reverify.py                  # ranked report, default limit 10
  python3 stale_reverify.py --limit 5
  python3 stale_reverify.py --days 45         # override the staleness threshold
  python3 stale_reverify.py --floor 30        # override the skip-floor
  python3 stale_reverify.py --today YYYY-MM-DD
"""
import argparse
import datetime
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")

STALE_DAYS = 45          # aligned with discover.py's STALE_CANDIDATE_DAYS
RERUN_FLOOR = 30.0       # skip entirely if conviction_score AND master_score are both below this
SETTLED_REDFLAGS = {"AVOID", "EXCLUDE"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10, help="max rows to print (report is always fully computed)")
    ap.add_argument("--days", type=int, default=STALE_DAYS)
    ap.add_argument("--floor", type=float, default=RERUN_FLOOR)
    ap.add_argument("--today", default=None)
    args = ap.parse_args()

    today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    state = json.load(open(STATE_PATH))["stocks"]

    eligible = []
    skipped_low = 0
    skipped_unparseable = 0

    for slug, s in state.items():
        if s.get("status") != "researched":
            continue
        if s.get("conviction_needs_reverification"):
            continue  # already tier 2's lane — never double-count
        rf = (s.get("red_flag_tier") or "").strip().upper()
        if rf in SETTLED_REDFLAGS:
            continue
        last = s.get("last_analyzed_date")
        if not last:
            continue
        try:
            d = datetime.date.fromisoformat(str(last)[:10])
        except Exception:
            skipped_unparseable += 1
            continue
        days_stale = (today - d).days
        if days_stale < args.days:
            continue

        conviction = s.get("conviction_score")
        master = s.get("master_score")
        conviction = float(conviction) if isinstance(conviction, (int, float)) else 0.0
        master = float(master) if isinstance(master, (int, float)) else 0.0

        if conviction < args.floor and master < args.floor:
            skipped_low += 1
            continue

        pool_priority = round(0.5 * conviction + 0.5 * master, 2)
        eligible.append({
            "slug": slug,
            "name": s.get("name") or slug,
            "conviction_score": conviction,
            "master_score": master,
            "pool_priority": pool_priority,
            "days_stale": days_stale,
            "last_analyzed_date": last,
        })

    eligible.sort(key=lambda r: (-r["pool_priority"], -r["days_stale"], r["name"].lower()))

    print(f"stale_reverify.py — run as of {today.isoformat()} "
          f"(stale >= {args.days}d, skip-floor {args.floor} on BOTH scores)")
    print(f"eligible for tier-5 re-verification: {len(eligible)}   "
          f"skipped (stale, both scores below floor): {skipped_low}"
          + (f"   unparseable last_analyzed_date: {skipped_unparseable}" if skipped_unparseable else ""))
    if not eligible:
        print("Nothing eligible this run.")
        return
    print(f"showing top {min(args.limit, len(eligible))} by pool_priority "
          f"(= 0.5*conviction_score + 0.5*master_score):\n")
    for r in eligible[: args.limit]:
        print(f"  pri={r['pool_priority']:>6}  conv={r['conviction_score']:>5}  master={r['master_score']:>5}  "
              f"{r['days_stale']:>4}d-stale  {r['slug']:<45} {r['name'][:45]}")


if __name__ == "__main__":
    main()
