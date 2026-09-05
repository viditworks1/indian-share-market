#!/usr/bin/env python3
"""
write_four_box.py - atomically add/overwrite the four_box block on ONE
data/<slug>.json (schema: DEEPDIVE_QUICKREF.md). Score is computed from the
box values here, not trusted from the caller, so a typo can't silently write
a wrong score.

Never touches thesis_fit or any other field - if the computed score
contradicts the existing thesis_fit per the decision table, that's for
audit_state.py's four-box check (run daily by vpscreen-audit) to catch and
reconcile, not this script.

USAGE
  write_four_box.py <slug> --tailwind yes --tam weak --moat weak --valuation no \
      --note "one line naming the weak/no boxes and why"
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_data_file import resolve_data_path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")

BOX_VALUES = {"yes": 1.0, "weak": 0.5, "no": 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--tailwind", choices=BOX_VALUES, required=True)
    ap.add_argument("--tam", choices=BOX_VALUES, required=True)
    ap.add_argument("--moat", choices=BOX_VALUES, required=True)
    ap.add_argument("--valuation", choices=BOX_VALUES, required=True)
    ap.add_argument("--note", required=True)
    args = ap.parse_args()

    fp = resolve_data_path(BASE, DATA_DIR, args.slug)
    if not os.path.exists(fp):
        print(f"error: no data file for slug {args.slug!r} (looked at {fp})", file=sys.stderr)
        sys.exit(1)

    with open(fp) as f:
        d = json.load(f)

    score = sum(BOX_VALUES[v] for v in (args.tailwind, args.tam, args.moat, args.valuation))
    d["four_box"] = {
        "tailwind": args.tailwind,
        "tam": args.tam,
        "moat": args.moat,
        "valuation": args.valuation,
        "score": score,
        "note": args.note,
    }

    tmp = fp + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    os.replace(tmp, fp)
    print(f"{args.slug}: four_box score {score}")


if __name__ == "__main__":
    main()
