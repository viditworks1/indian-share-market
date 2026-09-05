#!/usr/bin/env python3
"""
get_stock.py - slice state.json instead of reading the whole 700KB+ file.

state.json is large enough that reading it in full just to look at a handful of
stock entries is the single biggest token sink across the scheduled tasks. This
script emits only what a task actually needs.

USAGE
  get_stock.py <slug> [<slug> ...]         -> JSON {slug: entry, ...} for those keys
  get_stock.py --fields name,status,conviction <slug> ...   -> project to those fields
  get_stock.py --status researched          -> all entries with that status (repeatable-ish: comma list)
  get_stock.py --status candidate --source trusted-thread,trusted-x   -> filter by status AND source
  get_stock.py --has conviction_needs_reverification   -> every entry where that key is present and truthy
  get_stock.py --index                      -> thin index: {slug: {status, conviction, conviction_score,
                                               thesis_fit, red_flag_tier, last_analyzed_date, source}}
  get_stock.py --meta                       -> just state.json["meta"]
  get_stock.py --count                      -> status histogram

Slugs are matched exactly first; if not found, a case-insensitive substring match
against slug and against entry["name"] is tried and the resolved key is used.
Unresolved slugs are reported on stderr and listed under a "_unresolved" key.
Output is compact-ish JSON (indent=2) on stdout.
"""
import argparse
import json
import os
import signal
import sys

try:  # don't traceback when piped into head/less
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")

INDEX_FIELDS = ["status", "conviction", "conviction_score", "thesis_fit",
                "red_flag_tier", "last_analyzed_date", "source"]


def load_state():
    with open(STATE_PATH) as f:
        return json.load(f)


def resolve(stocks, want):
    """Return the real state.json key for `want`, or None."""
    if want in stocks:
        return want
    low = want.lower()
    # slug substring
    for k in stocks:
        if low in k.lower():
            return k
    # name substring
    for k, v in stocks.items():
        if low in str(v.get("name", "")).lower():
            return k
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*", help="state.json stock keys (or fuzzy name/slug fragments)")
    ap.add_argument("--fields", help="comma list of fields to project each entry down to")
    ap.add_argument("--status", help="comma list; return every entry whose status is in the list")
    ap.add_argument("--source", help="comma list; further filter --status results by source")
    ap.add_argument("--has", help="return every entry where this key is present and truthy")
    ap.add_argument("--index", action="store_true", help="thin index of every entry")
    ap.add_argument("--meta", action="store_true", help="just state.json meta")
    ap.add_argument("--count", action="store_true", help="status histogram")
    args = ap.parse_args()

    state = load_state()
    stocks = state["stocks"]

    if args.meta:
        print(json.dumps(state["meta"], indent=2, ensure_ascii=False))
        return

    if args.count:
        hist = {}
        for v in stocks.values():
            hist[v.get("status", "?")] = hist.get(v.get("status", "?"), 0) + 1
        print(json.dumps(hist, indent=2))
        return

    if args.index:
        idx = {k: {f: v.get(f) for f in INDEX_FIELDS} for k, v in stocks.items()}
        print(json.dumps(idx, indent=2, ensure_ascii=False))
        return

    fields = [f.strip() for f in args.fields.split(",")] if args.fields else None
    filter_mode = bool(args.status or args.has)

    def project(entry):
        if not fields:
            return entry
        return {f: entry.get(f) for f in fields}

    out = {}

    if args.status:
        wanted = {s.strip() for s in args.status.split(",")}
        srcs = {s.strip() for s in args.source.split(",")} if args.source else None
        for k, v in stocks.items():
            if v.get("status") in wanted and (srcs is None or v.get("source") in srcs):
                out[k] = project(v)

    if args.has:
        for k, v in stocks.items():
            if v.get(args.has):
                out[k] = project(v)

    unresolved = []
    for s in args.slugs:
        key = resolve(stocks, s)
        if key is None:
            unresolved.append(s)
        else:
            out[key] = project(stocks[key])

    resolved_any = bool(out)
    if unresolved:
        sys.stderr.write("unresolved: " + ", ".join(unresolved) + "\n")
        out["_unresolved"] = unresolved

    print(json.dumps(out, indent=2, ensure_ascii=False))

    if not resolved_any and not filter_mode:
        # explicit slug(s) asked for, none resolved -> hard error
        sys.stderr.write("no matching entries\n")
        sys.exit(1)
    if not resolved_any and filter_mode:
        sys.stderr.write("(filter matched nothing)\n")


if __name__ == "__main__":
    main()
