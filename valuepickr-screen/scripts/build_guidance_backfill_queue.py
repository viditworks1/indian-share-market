#!/usr/bin/env python3
"""
build_guidance_backfill_queue.py
================================

Builds / refreshes the queue for the ``guidance-backfill`` scheduled task:
researched stocks that DESERVE a guidance / expectation-gap assessment (see
``GUIDANCE_EXPECTATION_SCHEMA.md``) but do not have a ``market_expectation``
block on their ``data/<slug>.json`` yet.

WHY A SEPARATE QUEUE FROM deepdive-queue.json
--------------------------------------------
``deepdive-top100`` only covers the top 100 of ``max-returns-ranking.json`` and
crawls them ~9/day, so:
  * names ranked 101+ would never get the guidance blocks, and
  * even top-100 names wait ~10 days for their first pass (and the ones already
    ``done`` at pass 1 ran under the pre-guidance prompt).
``guidance-backfill`` does a LIGHTER, guidance-only pass (latest 1-2 concalls +
current multiple + a forward estimate — not the full 3-year annual-report read)
to close that gap fast, in ``conviction_score`` order. When ``deepdive-top100``
later reaches a name it replaces the light blocks with its deeper version
(blocks are replaced wholesale each pass) — no conflict.

SELECTION RULE (all must hold)
------------------------------
  * status == "researched"
  * red_flag_tier not set  (a red flag isn't a guidance-gap question)
  * thesis_fit != "neither" (screened-out names aren't portfolio candidates)
  * conviction_score >= MIN_CONVICTION_SCORE  (tier-B threshold — focus effort
    on names that could actually enter the portfolio)
  * data/<slug>.json exists and has NO ``market_expectation`` block yet

Sorted by conviction_score desc (highest-conviction gaps assessed first).
Entries already carrying a ``market_expectation`` block — from a prior backfill
run OR from a deepdive-top100 pass — drop off automatically on the next rebuild.

Usage:  python3 build_guidance_backfill_queue.py       (from scripts/ or repo root)
Writes: data/guidance-backfill-queue.json
"""
import datetime
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")
DATA_DIR = os.path.join(BASE, "data")
OUT_PATH = os.path.join(BASE, "data", "guidance-backfill-queue.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_data_file import resolve_data_path  # noqa: E402

MIN_CONVICTION_SCORE = 35          # tier-B threshold in vpscreen-rerank


def load(p, default=None):
    if not os.path.exists(p):
        return default
    with open(p) as f:
        return json.load(f)


def main():
    state = load(STATE_PATH)
    stocks = state["stocks"]

    prev = load(OUT_PATH, default={}) or {}
    prev_status = {e["slug"]: e for e in prev.get("queue", [])}

    queue = []
    for slug, e in stocks.items():
        if e.get("status") != "researched":
            continue
        if e.get("red_flag_tier"):
            continue
        if e.get("thesis_fit") == "neither":
            continue
        score = e.get("conviction_score")
        if not isinstance(score, (int, float)) or score < MIN_CONVICTION_SCORE:
            continue
        data_path = resolve_data_path(BASE, DATA_DIR, slug)
        data = load(data_path)
        if not isinstance(data, dict):
            continue
        if isinstance(data.get("market_expectation"), dict):
            continue                        # already assessed — off the queue

        p = prev_status.get(slug, {})
        queue.append({
            "slug": slug,
            "state_key": slug,
            "name": e.get("name", slug),
            "data_file": os.path.relpath(data_path, BASE),
            "conviction_score": score,
            "conviction": e.get("conviction"),
            "thesis_fit": e.get("thesis_fit"),
            "market_cap_tier": e.get("market_cap_tier"),
            "backfill_status": p.get("backfill_status", "pending"),
            "backfill_date": p.get("backfill_date"),
            "attempts": p.get("attempts", 0),
        })

    queue.sort(key=lambda x: (-(x["conviction_score"] or 0), x["slug"]))
    for i, e in enumerate(queue, 1):
        e["rank"] = i

    pending = sum(1 for e in queue if e["backfill_status"] == "pending")
    out = {
        "generated": datetime.date.today().isoformat(),
        "selection": (
            f"status=researched, no red flag, thesis_fit!=neither, conviction_score>="
            f"{MIN_CONVICTION_SCORE}, no market_expectation block yet. Sorted by "
            f"conviction_score desc. guidance-backfill drains this; entries drop off "
            f"automatically once a market_expectation block exists (from here or "
            f"deepdive-top100)."
        ),
        "total": len(queue),
        "pending": pending,
        "queue": queue,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"guidance-backfill-queue.json: {len(queue)} names ({pending} pending, "
          f"{len(queue) - pending} already done but still missing the block — will retry)")
    for e in queue[:12]:
        print(f"  {e['rank']:>3}  {e['conviction_score']:5.1f}  {e['slug']:<44s}  {e['backfill_status']}")


if __name__ == "__main__":
    main()
