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

SCOPE BROADENED 2026-09-09 — this is now a *coverage* backfill, not guidance-only.
The Confluence-100 dashboard's score grid was blank for most names because the
three deepdive blocks that feed the master-score sub-scores were missing:
  * ``market_expectation`` (+ the 3 other guidance blocks)  -> expectation_gap_score
  * ``quality_metrics``                                     -> quality_score
  * ``track_record``                                        -> consistency_score
                                     (quality + gap together -> asymmetry_score)
The light lane in deepdive-top100 now fills whichever of these three a queued
name is missing, off the SAME light filings read. Confluence-100 members sort
first so the visible dashboard fills in fastest.

SELECTION RULE (all must hold)
------------------------------
  * status == "researched"
  * red_flag_tier not set  (a red flag isn't a guidance-gap question)
  * thesis_fit != "neither" (screened-out names aren't portfolio candidates)
  * conviction_score >= MIN_CONVICTION_SCORE  (tier-B threshold — focus effort
    on names that could actually enter the portfolio)
  * data/<slug>.json exists and is MISSING at least one of the three blocks
    above (``market_expectation`` / ``quality_metrics`` / ``track_record``)

Sort order: Confluence-100 union membership first (data/confluence100.json), then
conviction_score desc. Each entry carries ``missing`` = the subset of the three
blocks still absent. Entries drop off automatically once all three exist — from
a backfill run OR a full deepdive-top100 pass.

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
COVERAGE_BLOCKS = ("market_expectation", "quality_metrics", "track_record")
CONFLUENCE_PATH = os.path.join(BASE, "data", "confluence100.json")


def load(p, default=None):
    if not os.path.exists(p):
        return default
    with open(p) as f:
        return json.load(f)


def confluence_slugs():
    d = load(CONFLUENCE_PATH, default={}) or {}
    return {r["slug"] for r in d.get("rows", []) if r.get("slug")}


def missing_blocks(data):
    # A block counts as covered if it's a dict, OR the writer set an explicit
    # `<block>_na: true` flag (deliberately not applicable — e.g. track_record for
    # a company with <3 fiscal years of history, which the schema says to leave
    # absent). Without the flag such names would re-queue forever.
    out = []
    for b in COVERAGE_BLOCKS:
        if isinstance(data.get(b), dict):
            continue
        if data.get(f"{b}_na") is True:
            continue
        out.append(b)
    return out


def main():
    state = load(STATE_PATH)
    stocks = state["stocks"]
    conf = confluence_slugs()

    prev = load(OUT_PATH, default={}) or {}
    prev_status = {e["slug"]: e for e in prev.get("queue", [])}

    queue = []
    for slug, e in stocks.items():
        if e.get("status") != "researched":
            continue
        if e.get("red_flag_tier"):
            continue
        in_conf = slug in conf
        # A name qualifies if it is on the Confluence-100 dashboard (fill it for
        # completeness regardless of thesis/conviction) OR it clears the normal
        # portfolio-relevance bar (thesis fits + tier-B conviction).
        score = e.get("conviction_score")
        portfolio_relevant = (
            e.get("thesis_fit") != "neither"
            and isinstance(score, (int, float)) and score >= MIN_CONVICTION_SCORE
        )
        if not (in_conf or portfolio_relevant):
            continue
        data_path = resolve_data_path(BASE, DATA_DIR, slug)
        data = load(data_path)
        if not isinstance(data, dict):
            continue
        miss = missing_blocks(data)
        if not miss:
            continue                        # all 3 blocks present — off the queue

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
            "in_confluence100": slug in conf,
            "missing": miss,
            "backfill_status": p.get("backfill_status", "pending"),
            "backfill_date": p.get("backfill_date"),
            "attempts": p.get("attempts", 0),
        })

    # Confluence-100 members first (visible on the dashboard), then conviction desc.
    queue.sort(key=lambda x: (not x["in_confluence100"], -(x["conviction_score"] or 0), x["slug"]))
    for i, e in enumerate(queue, 1):
        e["rank"] = i

    pending = sum(1 for e in queue if e["backfill_status"] == "pending")
    conf_pending = sum(1 for e in queue if e["in_confluence100"] and e["backfill_status"] == "pending")
    out = {
        "generated": datetime.date.today().isoformat(),
        "selection": (
            f"status=researched, no red flag, thesis_fit!=neither, conviction_score>="
            f"{MIN_CONVICTION_SCORE}, MISSING >=1 of {list(COVERAGE_BLOCKS)}. Sorted by "
            f"Confluence-100 membership, then conviction_score desc. deepdive-top100's "
            f"light lane drains this, writing only the blocks named in each entry's "
            f"`missing`; entries drop off once all three exist (here or a full deep pass)."
        ),
        "total": len(queue),
        "pending": pending,
        "confluence100_pending": conf_pending,
        "queue": queue,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"guidance-backfill-queue.json: {len(queue)} names ({pending} pending, "
          f"{conf_pending} of them Confluence-100; "
          f"{len(queue) - pending} done-but-still-incomplete — will retry)")
    for e in queue[:12]:
        tag = "C100" if e["in_confluence100"] else "    "
        print(f"  {e['rank']:>3}  {tag}  {e['conviction_score']:5.1f}  {e['slug']:<44s}  "
              f"miss={'+'.join(b.split('_')[0] for b in e['missing'])}  {e['backfill_status']}")


if __name__ == "__main__":
    main()
