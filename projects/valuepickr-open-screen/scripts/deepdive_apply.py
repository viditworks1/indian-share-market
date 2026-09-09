#!/usr/bin/env python3
"""
deepdive_apply.py — persist ONE stock's deep-dive bookkeeping atomically.

The deepdive-top100 scheduled task calls this once per stock, immediately after it
finishes writing that stock's data/<slug>.json (the rich prose + `deep_dive` block
are written by the task directly; this script only moves the structured state so a
half-finished run never leaves the queue / state.json inconsistent).

It updates:
  * valuepickr-screen/state.json         — the stock's entry
  * valuepickr-screen/data/deepdive-queue.json — the stock's queue entry

Usage (run from repo root):
  python3 valuepickr-screen/scripts/deepdive_apply.py \
      --queue-name "<exact `name` from the queue entry>" \
      --pass 1 --pre "Medium-High" --post "High" \
      --thesis "10x-in-2-3-years" --mcap "Small-cap (~Rs 1,876 Cr)" \
      --redflag none --notes "<= ~25-word notes_short" \
      --summary "<one-line what-this-pass-found, for queue history>"

--pre / --post are the conviction label before and after this deep dive.
--redflag: one of  none | AVOID | "HIGH CAUTION" | EXCLUDE
--thesis:  one of  10x-in-2-3-years | 100x-in-10-years | neither
"""
import argparse, json, os, sys, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
VP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATE = os.path.join(VP, "state.json")
QUEUE = os.path.join(VP, "data", "deepdive-queue.json")
TODAY = datetime.date.today().isoformat()

VALID_CONV = {"High", "Medium-High", "Medium", "Low-Medium", "Low", "Unrated"}
VALID_THESIS = {"10x-in-2-3-years", "100x-in-10-years", "neither"}
VALID_REDFLAG = {"none", "AVOID", "HIGH CAUTION", "EXCLUDE"}


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
    ap.add_argument("--queue-name", required=True)
    ap.add_argument("--pass", dest="passno", type=int, required=True)
    ap.add_argument("--pre", required=True)
    ap.add_argument("--post", required=True)
    ap.add_argument("--thesis", required=True)
    ap.add_argument("--mcap", required=True)
    ap.add_argument("--redflag", default="none")
    ap.add_argument("--notes", required=True)
    ap.add_argument("--summary", required=True)
    a = ap.parse_args()

    if a.post not in VALID_CONV or a.pre not in VALID_CONV:
        sys.exit(f"bad conviction label (pre={a.pre} post={a.post}); valid: {sorted(VALID_CONV)}")
    if a.thesis not in VALID_THESIS:
        sys.exit(f"bad --thesis {a.thesis}; valid: {sorted(VALID_THESIS)}")
    if a.redflag not in VALID_REDFLAG:
        sys.exit(f"bad --redflag {a.redflag}; valid: {sorted(VALID_REDFLAG)}")

    q = load(QUEUE)
    entry = next((e for e in q["queue"] if e["name"] == a.queue_name), None)
    if entry is None:
        sys.exit(f"no queue entry named exactly: {a.queue_name!r}")
    state_key = entry.get("state_key")

    # ---- state.json ----
    st = load(STATE)
    if state_key and state_key in st["stocks"]:
        s = st["stocks"][state_key]
        s["conviction"] = a.post
        s["thesis_fit"] = a.thesis
        s["market_cap_tier"] = a.mcap
        s["notes_short"] = a.notes
        s["red_flag_tier"] = None if a.redflag == "none" else a.redflag
        s["deepdive_pass"] = a.passno
        s["deepdive_date"] = TODAY
        dump(STATE, st)
        state_msg = f"state.json[{state_key}] updated"
    else:
        state_msg = f"WARNING: state_key {state_key!r} not in state.json — skipped state update"

    # ---- deepdive-queue.json ----
    entry["deepdive_status"] = "done"
    entry["deepdive_pass"] = a.passno
    entry["deepdive_date"] = TODAY
    entry["pre_deepdive_conviction"] = a.pre
    entry["post_deepdive_conviction"] = a.post
    entry.setdefault("history", []).append({
        "pass": a.passno, "date": TODAY,
        "pre": a.pre, "post": a.post, "summary": a.summary,
    })
    dump(QUEUE, q)

    pool = [e for e in q["queue"] if e.get("in_active_pool")]
    done = sum(1 for e in pool if e["deepdive_status"] == "done"
               and e["deepdive_pass"] >= a.passno)
    total = len(pool) or len(q["queue"])  # fallback for a queue predating the active-pool rework
    print(f"OK  rank {entry['rank']:>3}  {a.queue_name[:50]}")
    print(f"    {state_msg}")
    print(f"    queue: pass {a.passno} progress {done}/{total} (active pool)"
          + ("  <-- PASS COMPLETE, run build_deepdive_queue.py to roll to next pass"
             if done == total else ""))


if __name__ == "__main__":
    main()
