#!/usr/bin/env python3
"""
Mechanical trust-level maintenance pass, run regularly ("revisit trust levels")
by multiple tasks. Two parts, both deterministic - no LLM judgment needed:

1. Promotion: promotes anyone in users.json clearing trusted_users.json's
   promotion_criteria (min_total_love AND min_posts_seen) who isn't already
   trusted. Prints newly-promoted usernames so the calling task can decide
   whether to go look for their own portfolio/journal thread (needs a tool
   call, not done here). Every auto-promotion gets trust_tier "elevated" -
   this script never assigns "core". "core" is reserved for users the human
   operator of this project has explicitly named as heavily trusted (e.g.
   phreakv6); only a human manually editing trusted_users.json to set
   source: "user-named" should ever create a "core" entry.

2. Thread trust-level sync: a thread in trusted_threads.json tracked at
   trust_level "auto-discovered" gets upgraded to "user-trusted" if its
   primary_author has since been promoted into trusted_users.json by other
   means (e.g. reputation earned in company threads, not just this one) -
   keeps the two registries consistent without needing a human to notice.

Usage: python3 promote_trusted_users.py
"""
import json
import os
import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_PATH = os.path.join(BASE, "users.json")
TRUSTED_PATH = os.path.join(BASE, "trusted_users.json")
THREADS_PATH = os.path.join(BASE, "trusted_threads.json")


def main():
    with open(USERS_PATH) as f:
        users = json.load(f).get("users", {})
    with open(TRUSTED_PATH) as f:
        trusted = json.load(f)

    crit = trusted.get("promotion_criteria", {"min_total_love": 15, "min_posts_seen": 3})
    min_love, min_seen = crit["min_total_love"], crit["min_posts_seen"]

    newly = []
    for uname, u in users.items():
        if uname in trusted["users"]:
            continue
        if (u.get("total_love", 0) >= min_love) and (u.get("posts_seen", 0) >= min_seen):
            trusted["users"][uname] = {
                "promoted_date": datetime.date.today().isoformat(),
                "promotion_reason": f"Auto-promoted: {u.get('total_love')} total love across {u.get('posts_seen')} sighted posts (threshold: {min_love}/{min_seen})",
                "source": "auto-promoted",
                # "core" tier is reserved for users the human operator explicitly names
                # (source: "user-named", set by hand). This script must never assign it -
                # every auto-promotion is "elevated" by construction.
                "trust_tier": "elevated",
                "own_thread_topic_id": None,
            }
            newly.append(uname)

    if newly:
        with open(TRUSTED_PATH, "w") as f:
            json.dump(trusted, f, indent=2)

    print(f"trusted users: {len(trusted['users'])} total | newly promoted this run: {len(newly)}")
    for u in newly:
        print(f"- {u}: {users[u].get('total_love')} love / {users[u].get('posts_seen')} posts seen")
    if not newly:
        print("(no new promotions - nobody new cleared the bar)")

    # --- thread trust-level sync ---
    if os.path.exists(THREADS_PATH):
        with open(THREADS_PATH) as f:
            threads_data = json.load(f)
        upgraded = []
        for name, t in threads_data.get("threads", {}).items():
            if t.get("trust_level") == "auto-discovered" and t.get("primary_author") in trusted["users"]:
                t["trust_level"] = "user-trusted"
                t["trust_level_note"] = (
                    f"Upgraded from auto-discovered: {t['primary_author']} independently cleared "
                    f"the trusted-user reputation bar (see trusted_users.json) as of "
                    f"{datetime.date.today().isoformat()}."
                )
                upgraded.append(name)
        if upgraded:
            with open(THREADS_PATH, "w") as f:
                json.dump(threads_data, f, indent=2)
            print(f"thread trust-level sync: upgraded {len(upgraded)} thread(s) to user-trusted: {upgraded}")
        else:
            print("thread trust-level sync: no upgrades this run")


if __name__ == "__main__":
    main()
