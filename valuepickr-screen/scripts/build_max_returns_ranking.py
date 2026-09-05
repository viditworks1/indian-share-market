#!/usr/bin/env python3
"""
Builds a SECOND, criteria-free ranking from state.json - every researched stock,
ranked by conviction alone, with NO thesis_fit gate (10x-in-2-3-years /
100x-in-10-years). This exists as a hedge: if that return-magnitude bar is too
strict and excluding genuinely good opportunities, this view surfaces them
anyway. Fully mechanical - conviction and the one-line rationale (`notes_short`)
are already set by the scan task, so this needs zero LLM judgment or tool calls.

Red-flagged stocks (AVOID/HIGH CAUTION/EXCLUDE) are kept in a separate, clearly
labeled section rather than mixed into the ranked list - even a "no investment
criteria" view shouldn't present a going-concern-doubt stock alongside a clean
high-conviction one without a warning label.

Usage: python3 build_max_returns_ranking.py
Writes: data/max-returns-ranking.json (consumed by make_max_returns_ranking.js)
"""
import json
import os
import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")
OUT_PATH = os.path.join(BASE, "data", "max-returns-ranking.json")

CONVICTION_RANK = {
    "High": 5, "Medium-High": 4, "Medium": 3, "Low-Medium": 2, "Low": 1,
}


def conv_score(c):
    return CONVICTION_RANK.get(c, 0)


def main():
    with open(STATE_PATH) as f:
        state = json.load(f)
    stocks = state["stocks"]

    ranked, flagged = [], []
    for slug, e in stocks.items():
        if e.get("status") not in ("researched", "excluded", "avoid"):
            continue
        entry = {
            "name": e.get("name", slug),
            "conviction": e.get("conviction") or "Unrated",
            "thesis_fit": e.get("thesis_fit"),
            "market_cap_tier": e.get("market_cap_tier") or "",
            "reason": e.get("notes_short") or "",
        }
        if e.get("red_flag_tier"):
            entry["red_flag_tier"] = e["red_flag_tier"]
            flagged.append(entry)
        else:
            ranked.append(entry)

    ranked.sort(key=lambda x: -conv_score(x["conviction"]))
    flagged.sort(key=lambda x: x["red_flag_tier"])

    out = {
        "date_compiled": datetime.date.today().isoformat(),
        "total_researched": len(ranked) + len(flagged),
        "intro": (
            "This is a SECOND, criteria-free ranking of every researched stock - it does NOT "
            "apply the main screen's 10x-in-2-3-years / 100x-in-10-years thesis-fit gate. It "
            "exists as a hedge in case that return-magnitude bar is too strict and is excluding "
            "genuinely good opportunities (e.g. a high-quality large-cap with a real catalyst "
            "that just can't mathematically 10x). Ranked purely by conviction - the same "
            "fundamentals/technicals/community assessment used everywhere else in this project, "
            "just without the extreme-return filter. Cross-check against "
            "docs/00_SCREEN_RANKING.docx (the thesis-gated view) before acting - a stock ranked "
            "highly here but absent there is exactly the case this document is meant to catch."
        ),
        "ranked": ranked,
        "flagged_intro": (
            "Red-flagged (AVOID/HIGH CAUTION/EXCLUDE) stocks are kept separate even in this "
            "criteria-free view - a solvency or regulatory red flag isn't a return-potential "
            "debate, it's a capital-loss risk."
        ),
        "flagged": flagged,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)

    print(f"max-returns-ranking.json: {len(ranked)} ranked, {len(flagged)} flagged separately "
          f"(of {len(ranked) + len(flagged)} total researched)")


if __name__ == "__main__":
    main()
