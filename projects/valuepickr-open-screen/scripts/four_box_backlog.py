#!/usr/bin/env python3
"""
four_box_backlog.py - slice the four_box backfill backlog instead of scanning
state.json + every data/*.json file by hand each run.

A stock is "backfillable" when: status == researched, no red_flag_tier, its
data/<slug>.json file exists, it does NOT already carry a four_box block, and
it has at least one of the rich deep-dive fields (verdict_reasoning,
market_expectation, growth_trajectory, quality_metrics) a box score can
honestly be derived from without new research. Names without any of those
fields aren't skipped forever - deepdive-top100 will give them the fuller
research pass that produces both the fields and the block together.

Ordered by conviction_score (data/conviction-scores.json) descending, so the
highest-conviction names get the gate applied soonest. Missing/unscored slugs
sort last.

USAGE
  four_box_backlog.py --next-batch 40   -> JSON list of the next N candidates
                                           [{slug, name, conviction_score, thesis_fit}, ...]
  four_box_backlog.py --count           -> just the total remaining backlog count
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_data_file import resolve_data_path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")
DATA_DIR = os.path.join(BASE, "data")
CONVICTION_PATH = os.path.join(DATA_DIR, "conviction-scores.json")

RICH_FIELDS = ("verdict_reasoning", "market_expectation", "growth_trajectory", "quality_metrics")


def load_conviction_map():
    try:
        with open(CONVICTION_PATH) as f:
            rows = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    return {r.get("slug"): r.get("conviction_score") for r in rows if r.get("slug")}


def backlog():
    with open(STATE_PATH) as f:
        stocks = json.load(f)["stocks"]
    conv_map = load_conviction_map()

    candidates = []
    for slug, e in stocks.items():
        if e.get("status") != "researched" or e.get("red_flag_tier"):
            continue
        fp = resolve_data_path(BASE, DATA_DIR, slug)
        if not os.path.exists(fp):
            continue
        try:
            with open(fp) as f:
                d = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(d, dict):
            continue
        if isinstance(d.get("four_box"), dict):
            continue
        if not any(d.get(k) for k in RICH_FIELDS):
            continue
        candidates.append({
            "slug": slug,
            "name": e.get("name") or d.get("name") or slug,
            "conviction_score": conv_map.get(slug),
            "thesis_fit": e.get("thesis_fit"),
        })

    candidates.sort(key=lambda c: (c["conviction_score"] is None, -(c["conviction_score"] or 0)))
    return candidates


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--next-batch", type=int)
    g.add_argument("--count", action="store_true")
    args = ap.parse_args()

    b = backlog()
    if args.count:
        print(len(b))
    else:
        print(json.dumps(b[:args.next_batch], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
