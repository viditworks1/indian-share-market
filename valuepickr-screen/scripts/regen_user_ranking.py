#!/usr/bin/env python3
"""
Mechanically regenerates top-contributors.md from users.json - pure sort/
aggregation, no judgment calls. Run after the scan task has logged new posts,
or at the start of a rerank run.

A user needs MIN_POSTS_SEEN logged posts before ranking, so a single post that
happened to get a lot of loves doesn't create a misleading "top contributor"
out of one data point.
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_PATH = os.path.join(BASE, "users.json")
OUT_PATH = os.path.join(BASE, "top-contributors.md")

MIN_POSTS_SEEN = 1  # with ~1 post sampled per researched stock across a 335-name universe,
# requiring 2+ sightings before a user ever appears left this permanently empty in practice -
# show everyone, but the table's "Posts seen" column makes low-confidence (single-sighting)
# entries visible so they can be judged accordingly, rather than hiding them silently.


def main():
    with open(USERS_PATH) as f:
        data = json.load(f)
    users = data.get("users", {})

    ranked = [
        (uname, u) for uname, u in users.items()
        if u.get("posts_seen", 0) >= MIN_POSTS_SEEN
    ]
    ranked.sort(key=lambda x: (-(x[1].get("total_love") or 0), -(x[1].get("posts_seen") or 0)))

    with open(OUT_PATH, "w") as f:
        f.write("# ValuePickr Top Contributors (by love/like count)\n\n")
        f.write(
            "Built incrementally from posts actually read during scanning - not an "
            "exhaustive forum crawl, so most entries are a single sighting. The 'Posts "
            "seen' column is the confidence signal - treat a rank backed by only 1 post "
            "as provisional, not a verified pattern. Their high-conviction calls (logged "
            "under `high_conviction_calls`, which requires 2+ sightings) are treated as a "
            "qualitative signal in the screen, never a standalone reason to include or "
            "exclude a stock.\n\n"
        )
        if not ranked:
            f.write("_(empty — no posts logged yet)_\n")
        else:
            f.write("| Rank | Username | Total love | Posts seen | Avg love/post |\n")
            f.write("|---|---|---|---|---|\n")
            for i, (uname, u) in enumerate(ranked, 1):
                total = u.get("total_love", 0)
                seen = u.get("posts_seen", 0)
                avg = round(total / seen, 1) if seen else 0
                f.write(f"| {i} | {uname} | {total} | {seen} | {avg} |\n")
            f.write("\n## High-conviction calls logged\n\n")
            any_calls = False
            for uname, u in ranked:
                calls = u.get("high_conviction_calls", [])
                for c in calls:
                    any_calls = True
                    f.write(f"- **{uname}** on `{c.get('stock_slug')}` ({c.get('date')}): {c.get('note')}\n")
            if not any_calls:
                f.write("_(none logged yet)_\n")

    print(f"top-contributors.md: {len(ranked)} ranked users (of {len(users)} tracked)")


if __name__ == "__main__":
    main()
