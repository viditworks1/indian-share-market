#!/usr/bin/env python3
"""
refresh_derived.py - one call for the "after the batch" script salvo that almost
every scheduled task was running as 3-5 separate shell invocations.

Wraps the deterministic, no-LLM regen/score scripts:
  --scores   compute_conviction_score.py
  --gap      compute_expectation_gap_score.py
  --quality  compute_quality_score.py
  --master   compute_master_score.py (runs AFTER scores/gap/quality -- depends on all three)
  --users    regen_user_ranking.py + promote_trusted_users.py
  --lists    regen_lists.py
  --all      all of the above (default if no flag given)

Nothing here touches the network or an LLM, and each wrapped script is a pure
function of state.json / users.json / data/*.json, so running the wrong subset is
harmless - it just recomputes the same numbers.

FAST-EXIT: with --if-stale, the whole run is skipped (exit 0, one line) unless
state.json, users.json or analysis.md has an mtime newer than this script's last
successful run (tracked in data/.refresh_derived.stamp). Tasks that always mutate
state before calling this should NOT pass --if-stale; a read-mostly cadence task
(e.g. a rerun that found nothing) can.

Usage:
  refresh_derived.py --all
  refresh_derived.py --scores --lists
  refresh_derived.py --all --if-stale
"""
import argparse
import json
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
STAMP = os.path.join(BASE, "data", ".refresh_derived.stamp")
WATCH = [os.path.join(BASE, f) for f in ("state.json", "users.json", "analysis.md")]

STEPS = {
    "scores": ["compute_conviction_score.py"],
    "gap": ["compute_expectation_gap_score.py"],
    "quality": ["compute_quality_score.py"],
    "master": ["compute_master_score.py"],
    "users": ["regen_user_ranking.py", "promote_trusted_users.py"],
    "lists": ["regen_lists.py"],
}
ORDER = ["scores", "gap", "quality", "master", "users", "lists"]


def is_stale():
    try:
        last = os.path.getmtime(STAMP)
    except OSError:
        return True
    return any(os.path.exists(p) and os.path.getmtime(p) > last for p in WATCH)


def run(script):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)],
                       capture_output=True, text=True)
    tail = (p.stdout or p.stderr).strip().splitlines()
    tail = tail[-1] if tail else ""
    mark = "ok " if p.returncode == 0 else "FAIL"
    print(f"  [{mark}] {script}: {tail}")
    return p.returncode == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ORDER:
        ap.add_argument(f"--{k}", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--if-stale", action="store_true",
                    help="no-op unless state.json/users.json/analysis.md changed since last run")
    args = ap.parse_args()

    if args.if_stale and not is_stale():
        print("refresh_derived: nothing changed since last run - skipped")
        return

    want = ORDER if (args.all or not any(getattr(args, k) for k in ORDER)) \
        else [k for k in ORDER if getattr(args, k)]

    print(f"refresh_derived: {', '.join(want)}")
    ok = True
    for group in want:
        for script in STEPS[group]:
            ok = run(script) and ok

    if ok:
        os.makedirs(os.path.dirname(STAMP), exist_ok=True)
        with open(STAMP, "w") as f:
            json.dump({"ran": want, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f)
    else:
        sys.exit("refresh_derived: one or more steps FAILED (see above)")


if __name__ == "__main__":
    main()
