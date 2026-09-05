#!/usr/bin/env python3
"""
archive_analysis.py - keep analysis.md from growing without bound.

analysis.md is append-only and read (sliced) by extract_recent.py. Once it is
large AND has entries older than the retention window, this moves the old
entries into analysis-archive/pre-<cutoff>.md and leaves the recent tail (plus
the file's header block) in place.

An "entry" starts at a line matching either:
    ## <heading>            (old per-stock format, dated by following ### lines)
    ## <heading> [<date>]    (newer flat dated-heading format)
Its date is the LATEST of: a "[YYYY-MM-DD]" in the heading, and every
"### YYYY-MM-DD" line before the next "## " heading - i.e. the most recent
activity in that entry. This matters for the old per-stock format, where one
"## Stock" block can carry many dated ### sub-entries spanning months; the block
is only archived if its NEWEST sub-entry is past the window. Undated entries are
treated as recent (never archived).

Everything before the first "## " heading is the header block and is always kept.

DEFAULTS: retention 120 days, and only acts if analysis.md > 900 KB (i.e. stays
dormant until the file is roughly double its 2026-09 size). Override:
  archive_analysis.py --days 90 --min-kb 300
  archive_analysis.py --dry-run
Report-only and exit 0 when nothing qualifies.
"""
import argparse
import datetime
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(BASE, "analysis.md")
ARCHIVE_DIR = os.path.join(BASE, "analysis-archive")

HEAD_RE = re.compile(r"^##\s+(.+?)\s*$")
DATE_IN_HEAD_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2})")
DATE_LINE_RE = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2})")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--min-kb", type=int, default=900)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    size_kb = os.path.getsize(ANALYSIS) / 1024
    if size_kb < args.min_kb:
        print(f"analysis.md is {size_kb:.0f} KB (< {args.min_kb} KB) - nothing to do")
        return

    cutoff = datetime.date.today() - datetime.timedelta(days=args.days)
    with open(ANALYSIS) as f:
        lines = f.readlines()

    # locate entry starts
    starts = [i for i, ln in enumerate(lines) if HEAD_RE.match(ln)]
    if not starts:
        print("no '## ' entries found - nothing to do")
        return
    header = lines[:starts[0]]
    bounds = starts + [len(lines)]

    def entry_date(a, b):
        found = []
        m = DATE_IN_HEAD_RE.search(lines[a])
        if m:
            found.append(datetime.date.fromisoformat(m.group(1)))
        for ln in lines[a:b]:
            m = DATE_LINE_RE.match(ln)
            if m:
                found.append(datetime.date.fromisoformat(m.group(1)))
        return max(found) if found else None

    archive, keep = [], []
    for a, b in zip(bounds, bounds[1:]):
        d = entry_date(a, b)
        (archive if (d is not None and d < cutoff) else keep).extend(lines[a:b])

    if not archive:
        print(f"analysis.md is {size_kb:.0f} KB but no entries are older than "
              f"{cutoff.isoformat()} - nothing archived")
        return

    n_arch = sum(1 for ln in archive if HEAD_RE.match(ln))
    n_keep = sum(1 for ln in keep if HEAD_RE.match(ln))
    dest = os.path.join(ARCHIVE_DIR, f"pre-{cutoff.isoformat()}.md")

    if args.dry_run:
        print(f"[dry-run] would move {n_arch} entries ({len(''.join(archive))//1024} KB) "
              f"to {os.path.relpath(dest, BASE)}; {n_keep} entries stay")
        return

    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    mode = "a" if os.path.exists(dest) else "w"
    with open(dest, mode) as f:
        if mode == "w":
            f.write(f"# analysis.md archive - entries dated before {cutoff.isoformat()}\n\n")
        f.writelines(archive)

    tmp = ANALYSIS + ".tmp"
    with open(tmp, "w") as f:
        f.writelines(header)
        f.writelines(keep)
    os.replace(tmp, ANALYSIS)

    print(f"archived {n_arch} entries -> {os.path.relpath(dest, BASE)}; "
          f"{n_keep} entries + header remain ({os.path.getsize(ANALYSIS)//1024} KB)")


if __name__ == "__main__":
    main()
