#!/usr/bin/env python3
"""
Mark one or more registry entries as status="not-a-stock" so discover.py stops
surfacing them as "actionable" every run.

Use for generic / sector / theme / book / methodology threads that never resolve
to a single company (e.g. "Logistics sector", "Sugar Cycles: ...", "Investing
Basics", "Reminiscences of a Stock Operator", "Companies with 20%+ guidance").

Usage:
  python3 mark_not_a_stock.py <slug> [<slug> ...]
  python3 mark_not_a_stock.py --list          # show current not-a-stock entries
  python3 mark_not_a_stock.py --undo <slug>   # revert to status="candidate"
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    with open(STATE_PATH) as f:
        state = json.load(f)
    stocks = state["stocks"]

    if args[0] == "--list":
        hits = [(s, e.get("raw_title", "")) for s, e in stocks.items()
                if e.get("status") == "not-a-stock"]
        print(f"{len(hits)} entries with status=not-a-stock:")
        for s, t in sorted(hits):
            print(f"  {s:50s} {t[:70]}")
        return

    undo = False
    if args[0] == "--undo":
        undo = True
        args = args[1:]

    changed = []
    missing = []
    for slug in args:
        e = stocks.get(slug)
        if e is None:
            missing.append(slug)
            continue
        if undo:
            e["status"] = "candidate"
        else:
            e["status"] = "not-a-stock"
            e.setdefault("first_seen_date", state["meta"].get("last_discover_run"))
            e["notes_short"] = (e.get("notes_short") or "") or \
                "generic/sector/theme/book/methodology thread - not a single company"
        changed.append(slug)

    if changed:
        with open(STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)
    verb = "reverted to candidate" if undo else "marked not-a-stock"
    print(f"{verb}: {', '.join(changed) if changed else '(none)'}")
    if missing:
        print(f"NOT FOUND in registry: {', '.join(missing)}")


if __name__ == "__main__":
    main()
