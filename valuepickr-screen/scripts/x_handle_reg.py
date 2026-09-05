#!/usr/bin/env python3
"""
Helper for x-handles/x_handle_registry.json — the X-account triage/ranking registry.
Mirrors get_stock.py / patch_stock.py in spirit so the scheduled tasks never read
the whole registry into context.

Usage:
  x_handle_reg.py --summary
  x_handle_reg.py --next-batch 5            # next N pending deep_pass handles, A1 before A2, oldest xlsx_row first
  x_handle_reg.py --pending-count
  x_handle_reg.py get <handle>
  x_handle_reg.py patch <handle> --set k=v --set k2=v2 --set-json k='<json>' --delete k
  x_handle_reg.py --scoreboard-input        # JSON blob feeding regen_x_scoreboard.py
"""
import argparse, json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(BASE, "x-handles", "x_handle_registry.json")


def load():
    with open(REG) as f:
        return json.load(f)


def save(d):
    with open(REG, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def find(d, handle):
    h = handle.strip().lstrip("@").lower()
    for row in d["handles"]:
        if row["handle"].lower() == h:
            return row
    return None


def coerce(v):
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if v.lower() in ("null", "none"):
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def next_batch(d, n):
    pend = [r for r in d["handles"] if r.get("deep_pass") and r.get("triage_status") == "pending"]
    pend.sort(key=lambda r: (0 if r["bucket"] == "A1" else 1, r["xlsx_row"]))
    return pend[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["get", "patch"])
    ap.add_argument("handle", nargs="?")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--next-batch", type=int, metavar="N")
    ap.add_argument("--pending-count", action="store_true")
    ap.add_argument("--scoreboard-input", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="k=v")
    ap.add_argument("--set-json", action="append", default=[], metavar="k=json")
    ap.add_argument("--delete", action="append", default=[], metavar="k")
    a = ap.parse_args()
    d = load()

    if a.summary:
        from collections import Counter
        b = Counter(r["bucket"] for r in d["handles"])
        t = Counter(r["triage_status"] for r in d["handles"])
        print("generated:", d.get("generated"))
        print("buckets:", dict(b))
        print("triage_status:", dict(t))
        dp = [r for r in d["handles"] if r.get("deep_pass")]
        done = [r for r in dp if r["triage_status"] == "done"]
        print(f"deep_pass: {len(done)}/{len(dp)} triaged")
        return

    if a.pending_count:
        print(len([r for r in d["handles"] if r.get("deep_pass") and r.get("triage_status") == "pending"]))
        return

    if a.next_batch is not None:
        rows = next_batch(d, a.next_batch)
        print(json.dumps([{k: r[k] for k in ("handle", "name", "bucket", "xlsx_row", "note",
                                             "last_tweet_id_seen")} for r in rows], indent=2, ensure_ascii=False))
        return

    if a.scoreboard_input:
        print(json.dumps({"handles": [r for r in d["handles"] if r.get("deep_pass")]}, indent=2, ensure_ascii=False))
        return

    if a.cmd == "get":
        r = find(d, a.handle)
        print(json.dumps(r, indent=2, ensure_ascii=False) if r else f"(not found: {a.handle})")
        return

    if a.cmd == "patch":
        r = find(d, a.handle)
        if not r:
            sys.exit(f"not found: {a.handle}")
        for kv in a.set:
            k, _, v = kv.partition("=")
            r[k.strip()] = coerce(v)
        for kv in a.set_json:
            k, _, v = kv.partition("=")
            r[k.strip()] = json.loads(v)
        for k in a.delete:
            r.pop(k.strip(), None)
        save(d)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return

    ap.print_help()


if __name__ == "__main__":
    main()
