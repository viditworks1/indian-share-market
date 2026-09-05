#!/usr/bin/env python3
"""
guidance_backfill_apply.py — persist ONE stock's guidance-backfill bookkeeping atomically.

The guidance-backfill task calls this once per stock, immediately after it writes
that stock's four guidance blocks into data/<slug>.json (the blocks themselves are
written by the task directly, exactly like deepdive-top100 writes its deep_dive
block; this script only moves the structured state so a half-finished run never
leaves the queue / state.json inconsistent — same lesson as deepdive_apply.py).

Updates:
  * valuepickr-screen/data/guidance-backfill-queue.json — the stock's queue entry
  * valuepickr-screen/state.json                        — a guidance_backfill_date stamp

Usage (from repo root):
  python3 valuepickr-screen/scripts/guidance_backfill_apply.py \
      --slug "<exact slug / state_key from the queue entry>" \
      --result done \
      --summary "<one-line: gap_direction / gap_type / catalyst, for the queue history>"

--result:  done | skipped | no-data
  done    -> a full market_expectation block was written
  skipped -> deliberately skipped (e.g. deepdive-top100 is about to deepen it)
  no-data -> genuinely nothing findable (thin SME); blocks set to []/null with an
             open_questions note. Still counts as processed so the queue moves on.
"""
import argparse
import datetime
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VP = os.path.join(ROOT, "valuepickr-screen")
STATE = os.path.join(VP, "state.json")
QUEUE = os.path.join(VP, "data", "guidance-backfill-queue.json")
DATA_DIR = os.path.join(VP, "data")
TODAY = datetime.date.today().isoformat()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_data_file import resolve_data_path  # noqa: E402

VALID_RESULT = {"done", "skipped", "no-data"}


def load(p):
    with open(p) as f:
        return json.load(f)


def dump(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--result", required=True, choices=sorted(VALID_RESULT))
    ap.add_argument("--summary", required=True)
    a = ap.parse_args()

    q = load(QUEUE)
    entry = next((e for e in q["queue"] if e["slug"] == a.slug), None)
    if entry is None:
        sys.exit(f"no guidance-backfill queue entry with slug: {a.slug!r}")

    # sanity: if result=done, the data file really should carry the block now
    if a.result == "done":
        dpath = resolve_data_path(VP, DATA_DIR, a.slug)
        try:
            d = load(dpath)
            if not isinstance(d.get("market_expectation"), dict):
                sys.exit(f"--result done but {dpath} has no market_expectation block; "
                         f"write the blocks first, then call this.")
        except OSError:
            sys.exit(f"--result done but cannot read {dpath}")

    entry["backfill_status"] = "done" if a.result in ("done", "no-data") else "skipped"
    entry["backfill_result"] = a.result
    entry["backfill_date"] = TODAY
    entry["attempts"] = entry.get("attempts", 0) + 1
    entry.setdefault("history", []).append({"date": TODAY, "result": a.result, "summary": a.summary})
    dump(QUEUE, q)

    st = load(STATE)
    s = st["stocks"].get(entry.get("state_key"))
    state_msg = "state_key not in state.json — skipped stamp"
    if s is not None:
        s["guidance_backfill_date"] = TODAY
        s["guidance_backfill_result"] = a.result
        dump(STATE, st)
        state_msg = f"state.json[{entry.get('state_key')}] stamped"

    done = sum(1 for e in q["queue"] if e["backfill_status"] in ("done",))
    skipped = sum(1 for e in q["queue"] if e["backfill_status"] == "skipped")
    total = len(q["queue"])
    print(f"OK  {a.slug}  -> {a.result}")
    print(f"    {state_msg}")
    print(f"    queue: {done} done, {skipped} skipped, {total - done - skipped} pending "
          f"(of {total})")


if __name__ == "__main__":
    main()
