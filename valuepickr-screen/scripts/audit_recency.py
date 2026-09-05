#!/usr/bin/env python3
"""
Recency audit for trusted-user conviction signals.

Scans every entry in users.json's high_conviction_calls arrays (the raw,
per-user log of trusted conviction calls this project has recorded),
computes each entry's current recency weight via recency_weight.py, and
reports any entry that has now decayed below 0.25 (i.e. > ~6 months old)
that ISN'T already marked superseded: true.

This is a read-only report to stdout - it does not modify any file. The
point is to flag "this call is old enough that nobody has checked whether
the position is still current" so a human (or a future scheduled task that
does live forum research) knows what to go re-verify. A stale-but-not-yet-
checked call is exactly the gap this script exists to surface: date decay
alone doesn't tell you WHY a call went stale (still held quietly? exited
and never updated? just an old backfilled mention?) - only a fresh look at
the thread can resolve that, this script just points at where to look.

Usage: python3 audit_recency.py [--today YYYY-MM-DD] [--count]

--count prints only the summary header (total scanned / already-superseded /
stale-flagged / unparseable counts) and skips the per-entry listing. This is
all a routine that only logs a count (e.g. vpscreen-audit) actually needs -
the full per-row listing is for a human who intends to go re-verify calls.
"""
import argparse
import json
import os
from datetime import date

from recency_weight import weight_for_date, _parse_date_str

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_PATH = os.path.join(BASE, "users.json")

STALE_THRESHOLD = 0.25  # entries with weight strictly below this get flagged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default=None, help="Override today's date (YYYY-MM-DD), for reproducible runs")
    ap.add_argument("--count", action="store_true",
                    help="print only the summary counts, skip the per-entry listing")
    args = ap.parse_args()
    today = date.fromisoformat(args.today) if args.today else date.today()

    with open(USERS_PATH) as f:
        users = json.load(f).get("users", {})

    total = 0
    superseded_count = 0
    stale_flagged = []
    unparseable = []

    for uname, u in users.items():
        for c in u.get("high_conviction_calls", []):
            total += 1
            date_str = c.get("date", "")
            stock = c.get("stock", "<unknown stock>")
            superseded = bool(c.get("superseded", False))
            if superseded:
                superseded_count += 1
                continue  # explicit exit already recorded - not a decay question

            if _parse_date_str(date_str) is None:
                unparseable.append((uname, stock, date_str))

            w = weight_for_date(date_str, today=today)
            if w < STALE_THRESHOLD:
                stale_flagged.append((uname, stock, date_str, w))

    stale_flagged.sort(key=lambda x: x[3])  # oldest/lowest-weight first

    print(f"audit_recency.py - run as of {today.isoformat()}")
    print(f"total high_conviction_calls entries scanned: {total}")
    print(f"already marked superseded (skipped): {superseded_count}")
    print(f"stale, needs a status recheck (weight < {STALE_THRESHOLD}, not superseded): {len(stale_flagged)}")
    if unparseable:
        print(f"unparseable dates (treated conservatively as stale, weight 0.05): {len(unparseable)}")

    if args.count:
        return

    print()

    if unparseable:
        print(f"NOTE: {len(unparseable)} entries have a date field that couldn't be cleanly parsed "
              f"(treated conservatively as stale, weight 0.05):")
        for uname, stock, date_str in unparseable:
            print(f"  - {uname} | {stock} | date={date_str!r}")
        print()

    if not stale_flagged:
        print("No stale, non-superseded entries found. Nothing to flag.")
        return

    print(f"STALE, NEEDS A STATUS RECHECK ({len(stale_flagged)} entries, weight < {STALE_THRESHOLD}, not superseded):")
    print("These calls are old enough (>~6 months) that this project has no record of whether the")
    print("position is still current. Re-check the thread / user's recent posts and either mark")
    print("superseded: true (if they exited) or leave as-is with an updated date (if still held).\n")
    for uname, stock, date_str, w in stale_flagged:
        print(f"  weight={w:<5} | {uname:<25} | {stock:<45} | date={date_str}")


if __name__ == "__main__":
    main()
