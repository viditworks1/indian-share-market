#!/usr/bin/env python3
"""
patch_stock.py - mutate ONE stock entry in state.json without the model having to
re-serialise the whole 700KB+ file (which is slow, token-heavy, and risks key
reordering / accidental drops).

USAGE
  patch_stock.py <slug> --set status=researched --set conviction=Medium-High
  patch_stock.py <slug> --set-json trusted_signals='[{"date":"2026-09-01"}]'
  patch_stock.py <slug> --set-json revisit_after_30d=true
  patch_stock.py <slug> --delete conviction_needs_reverification
  patch_stock.py <slug> --set last_analyzed_date=2026-09-01 --delete legacy_verdict
  patch_stock.py --new <slug> --set-json '{"name":"X Ltd","status":"candidate","source":"trusted-x"}'
  patch_stock.py --meta --set last_ranking_date=2026-09-01 --set last_ranking_timestamp=2026-09-01T14:32:00Z

RULES
  * --set  key=value        : value is stored as a string, UNLESS it is exactly
                              true/false/null or looks like a number -> then typed.
  * --set-json key=<json>    : value parsed as JSON (use for arrays/objects/explicit types).
  * --set-json '<json obj>'  : with no key=, merge every top-level key of the object.
  * --delete key            : remove the key if present (no error if absent).
  * --new <slug>            : the slug must NOT already exist; creates it (needs at least
                              one --set/--set-json). Without --new the slug MUST exist.
  * Existing key order is preserved; new keys are appended. Atomic write (.tmp + os.replace).
  * meta.last_updated is bumped to today on every successful write.
Exit non-zero (and no write) on any validation failure.
"""
import argparse
import datetime
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")


def coerce(s):
    if s == "true":
        return True
    if s == "false":
        return False
    if s == "null":
        return None
    try:
        if s.strip().lstrip("-").isdigit():
            return int(s)
        return float(s)
    except (ValueError, AttributeError):
        return s


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", nargs="?", help="stock key; omit only with --meta")
    ap.add_argument("--new", action="store_true", help="create this slug (must not exist)")
    ap.add_argument("--meta", action="store_true", help="patch state.json['meta'] instead of a stock")
    ap.add_argument("--set", action="append", default=[], metavar="key=value",
                    help="set a string/auto-typed scalar")
    ap.add_argument("--set-json", action="append", default=[], metavar="key=<json> | <json-obj>",
                    help="set a JSON value, or merge a whole JSON object if no key=")
    ap.add_argument("--delete", action="append", default=[], metavar="key",
                    help="remove a key")
    args = ap.parse_args()

    with open(STATE_PATH) as f:
        state = json.load(f)
    stocks = state["stocks"]

    if args.meta:
        if args.slug:
            sys.exit("error: --meta takes no slug")
        entry = state.setdefault("meta", {})
        args.slug = "meta"  # for the print line
    else:
        if not args.slug:
            sys.exit("error: a slug is required (or use --meta)")
        exists = args.slug in stocks
        if args.new and exists:
            sys.exit(f"error: --new given but '{args.slug}' already exists")
        if not args.new and not exists:
            sys.exit(f"error: '{args.slug}' not found (use --new to create)")
        entry = stocks.get(args.slug, {})

    for item in args.set:
        if "=" not in item:
            sys.exit(f"error: --set expects key=value, got {item!r}")
        k, v = item.split("=", 1)
        entry[k] = coerce(v)

    for item in args.set_json:
        if "=" in item and not item.lstrip().startswith("{"):
            k, v = item.split("=", 1)
            try:
                entry[k] = json.loads(v)
            except json.JSONDecodeError as e:
                sys.exit(f"error: --set-json {k}: bad JSON ({e})")
        else:
            try:
                obj = json.loads(item)
            except json.JSONDecodeError as e:
                sys.exit(f"error: --set-json object: bad JSON ({e})")
            if not isinstance(obj, dict):
                sys.exit("error: --set-json without key= must be a JSON object")
            entry.update(obj)

    for k in args.delete:
        entry.pop(k, None)

    if args.new and not entry:
        sys.exit("error: --new needs at least one --set/--set-json")

    if not args.meta:
        stocks[args.slug] = entry
    state.setdefault("meta", {})["last_updated"] = datetime.date.today().isoformat()

    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    os.replace(tmp, STATE_PATH)

    print(f"patched {args.slug}: {json.dumps(entry, ensure_ascii=False)[:400]}")


if __name__ == "__main__":
    main()
