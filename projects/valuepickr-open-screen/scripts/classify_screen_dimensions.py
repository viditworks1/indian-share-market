#!/usr/bin/env python3
"""
Mechanical backstop for the screen-dimensions block (see SCREEN_DIMENSIONS_SCHEMA.md).

Reads data/screen-ranking.json and, for every entry in screenedOut / tierC / highCaution /
avoid that is MISSING a `dimensions` block, parses its free-text `reason` into a conservative
structured block:

    entry["dimensions"] = {thesis, recent_fundamentals, long_term_fundamentals,
                           technicals, governance}
    entry["primary_screen_reason"] = <one axis>

It is deliberately cautious: a phrase has to be fairly unambiguous to move a dimension off
"unknown", and if the dominant driver can't be read it sets primary_screen_reason to
"unclassified" so vpscreen-rerank authors it properly. Existing blocks are left alone unless
--force. Idempotent.

Usage:
  python3 classify_screen_dimensions.py                # apply, fill only missing blocks
  python3 classify_screen_dimensions.py --dry-run      # report the distribution, write nothing
  python3 classify_screen_dimensions.py --force        # re-derive every block from prose
"""
import argparse
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RANKING_PATH = os.path.join(BASE, "data", "screen-ranking.json")
BUCKETS = ("screenedOut", "tierC", "highCaution", "avoid")

# --- phrase -> verdict cues. Lowercase substring match against the reason text. -------------

THESIS_NEITHER = [
    "thesis 'neither'", 'thesis "neither"', "thesis_fit 'neither'", "thesis fit: neither",
    "thesis neither", "thesis re-assessed to 'neither'", "thesis reassessed to 'neither'",
    "10x math", "no 10x", "for 10x/100x", "10x/100x math", "return magnitude",
    "not a 2-3-year", "not a 2-3 year", "not a fast-return",
]
THESIS_SIZE = [
    "mega-cap", "already large", "already-large", "too large", "far too large",
    "large-cap", "already mid-cap", "size math", "size makes", "at this size",
    "too big", "scaled to rs", "already up ~", "modest for 10x", "too modest for 10x",
]
THESIS_FIT = ["thesis fits", "thesis fit: 10x", "10x-in-2-3-years", "100x-in-10-years"]

GOV_RED = [
    "auditor resign", "auditor exit", "sebi ", "fraud", "siphon", "round-trip",
    "guidance withdrawn", "withdrew its", "withdrew guidance", "pledge", "pledged",
    "promoter selling", "promoter sold", "promoter exit", "falling promoter holding",
    "declining promoter", "reduced stake", "cut its stake", "ofs", "trusted tracker",
    "trusted tracker exited", "fully exited", "exited over", "exited at a", "governance",
    "related-party", "related party", "rpt", "capital-allocation critique", "opacity",
    "management opacity", "trust concern", "trust grounds", "corporate governance",
]
GOV_WATCH = [
    "concentration risk", "key-management attrition", "management overhaul", "family feud",
    "promoter dispute", "succession", "disclosure", "cut segment disclosure", "lumpy",
    "government-dependent", "%-government", "government-scheme", "contingent",
]

TECH_STRETCHED = [
    "already re-rated", "re-rated ~", "re-rating already", "re-rating largely done",
    "already largely done", "already priced", "priced-in", "priced in", "already-priced",
    "52-week high", "52-wk high", "multi-year high", "all-time high", "near a 52",
    "already up", "already +", "up ~", "breakout already", "1yr breakout",
    "confirmed +", "doubled", "nearly doubled", "already re-rated hard", "peak-cycle valuation",
    "peak multiple", "~75x", "~80x", "~90x", "200x+", "expensive", "rich multiple",
]

LTF_WEAK = [
    "weak trailing", "trailing roe", "trailing average", "5yr", "5-yr", "5 yr",
    "3yr roe", "3-yr roe", "revenue cagr ~-", "sales cagr ~-", "negative roe",
    "near-zero roe", "low-quality", "mature ", "decelerating", "flat yoy", "flat-to",
    "single-digit growth", "~5% and decelerating", "de-growth", "5-year revenue growth negative",
    "5yr cagr", "5-yr cagr", "5-yr sales cagr", "mid-teens trailing", "no growth",
]
LTF_STRONG = [
    "strong roce", "excellent roce", "high-quality", "debt-free compounder",
    "quality compounder", "sustained", "strong roce/roe", "roe ~2", "roce ~2", "roce ~3",
    "near debt-free", "best business quality", "strongest fundamentals",
]

# recent_fundamentals is intentionally NOT inferred as "strong" from prose. Deciding whether a
# recent-quarter move is a real inflection or a cosmetic bounce the analyst already dismissed
# ("Q1 +45% YoY but net profit ~Rs 15 lakh - cosmetic, not an earnings inflection") needs a
# read of analysis.md, not a keyword. That's the rerank task's job. The mechanical pass only
# recognises the unambiguously *negative* recent signals below, and otherwise leaves it
# "unknown". This keeps the classifier from re-introducing the very bias bug it exists to kill.
RF_NEGATION = [
    "not an earnings inflection", "not an inflection", "cosmetic", "declined further",
    "both declined", "flattish", "one good year", "not good results next quarter",
]
RF_WEAK = [
    "profit slump", "opm collapsed", "margin miss", "q1 fy27 growth deceleration",
    "growth decelerat", "de-growth", "declined yoy", "pat only", "loss quarter",
    "q4 fy26 revenue -", "washout", "widening q1 loss", "widening loss",
] + RF_NEGATION

NO_THREAD = ["no dedicated valuepickr thread", "no vp thread", "no valuepickr thread",
             "no dedicated thread", "thread dormant", "no thread to cross-check"]


def _hit(text, cues):
    return any(c in text for c in cues)


def classify(reason):
    t = (reason or "").lower()
    d = {
        "thesis": "unknown",
        "recent_fundamentals": "unknown",
        "long_term_fundamentals": "unknown",
        "technicals": "unknown",
        "governance": "unknown",
    }

    if _hit(t, THESIS_NEITHER) or _hit(t, THESIS_SIZE):
        d["thesis"] = "neither"
    elif _hit(t, THESIS_FIT):
        d["thesis"] = "fit"

    if _hit(t, GOV_RED):
        d["governance"] = "red"
    elif _hit(t, GOV_WATCH):
        d["governance"] = "watch"

    if _hit(t, TECH_STRETCHED):
        d["technicals"] = "stretched"

    if _hit(t, LTF_WEAK):
        d["long_term_fundamentals"] = "weak"
    elif _hit(t, LTF_STRONG):
        d["long_term_fundamentals"] = "strong"

    if _hit(t, RF_WEAK):
        d["recent_fundamentals"] = "weak"

    # --- primary_screen_reason: the one axis that drove the call -------------------------
    # priority: governance(red) > thesis(neither via size) > thesis(neither) >
    #           long_term_fundamentals > valuation/technicals > recent_fundamentals > no_thread
    prr = "unclassified"
    if d["governance"] == "red":
        prr = "governance"
    elif d["thesis"] == "neither" and _hit(t, THESIS_SIZE) and not _hit(t, THESIS_NEITHER):
        prr = "size"
    elif d["thesis"] == "neither":
        prr = "thesis"
    elif d["long_term_fundamentals"] == "weak":
        prr = "long_term_fundamentals"
    elif d["technicals"] == "stretched":
        prr = "valuation" if _hit(t, ["~75x", "~80x", "~90x", "200x+", "expensive",
                                      "rich multiple", "peak multiple", "peak-cycle valuation"]) \
              else "technicals"
    elif d["recent_fundamentals"] == "weak":
        prr = "recent_fundamentals"
    elif _hit(t, NO_THREAD):
        prr = "no_thread"

    return d, prr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-derive every block, not just missing")
    args = ap.parse_args()

    with open(RANKING_PATH) as f:
        ranking = json.load(f)

    from collections import Counter
    filled = 0
    prr_dist = Counter()
    mis_screen = []
    soft = []

    for bucket in BUCKETS:
        for e in ranking.get(bucket, []):
            if "dimensions" in e and not args.force:
                prr_dist[e.get("primary_screen_reason", "unclassified")] += 1
                continue
            d, prr = classify(e.get("reason", ""))
            prr_dist[prr] += 1
            if not args.dry_run:
                e["dimensions"] = d
                e["primary_screen_reason"] = prr
            filled += 1
            if bucket == "screenedOut":
                # MIS-SCREEN can only be asserted off an LLM-authored recent_fundamentals=="strong";
                # the mechanical pass never sets that, so this stays empty unless --force is run
                # after vpscreen-rerank has authored real blocks.
                if (prr == "long_term_fundamentals" and d["recent_fundamentals"] == "strong"
                        and d["thesis"] != "neither" and d["governance"] != "red"):
                    mis_screen.append(e["name"])
                if prr in ("technicals", "valuation") and d["thesis"] != "neither":
                    soft.append(e["name"])

    if not args.dry_run:
        with open(RANKING_PATH, "w") as f:
            json.dump(ranking, f, indent=2, ensure_ascii=False)
            f.write("\n")

    verb = "would fill" if args.dry_run else "filled"
    print(f"screen dimensions: {verb} {filled} block(s) across {BUCKETS}")
    print("primary_screen_reason distribution:")
    for k, v in prr_dist.most_common():
        print(f"  {k:26s} {v}")
    print(f"\nMIS-SCREEN candidates (long-term-only weakness, recent strong): {len(mis_screen)}")
    for n in mis_screen:
        print(f"  - {n}")
    print(f"SOFT screen-outs (technicals/valuation, thesis still fits): {len(soft)}")


if __name__ == "__main__":
    main()
