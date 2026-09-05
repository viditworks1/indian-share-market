#!/usr/bin/env python3
"""
Prints only the analysis.md entries dated on/after a cutoff date, so the
conviction-rerank job never has to load the entire (ever-growing) file into
context. Entries are demarcated by "### YYYY-MM-DD" lines under "## Stock Name"
headings.

Usage: python3 extract_recent.py <cutoff-date YYYY-MM-DD>
If no cutoff is given, uses state.json's last_ranking_date; if that's also
null, prints everything (first-ever run).
"""
import sys
import os
import re
import json
import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS_PATH = os.path.join(BASE, "analysis.md")
STATE_PATH = os.path.join(BASE, "state.json")


def get_cutoff():
    if len(sys.argv) > 1:
        return datetime.date.fromisoformat(sys.argv[1])
    with open(STATE_PATH) as f:
        state = json.load(f)
    d = state.get("meta", {}).get("last_ranking_date")
    return datetime.date.fromisoformat(d) if d else None


def main():
    cutoff = get_cutoff()
    with open(ANALYSIS_PATH) as f:
        lines = f.readlines()

    out = []
    current_stock_heading = None
    current_entry_date = None
    current_entry_lines = []
    stock_has_output = False

    def flush_entry():
        nonlocal current_entry_lines, current_entry_date, stock_has_output
        if current_entry_lines and (cutoff is None or (current_entry_date and current_entry_date >= cutoff)):
            if current_stock_heading and not stock_has_output:
                out.append(current_stock_heading)
                stock_has_output = True
            out.extend(current_entry_lines)
        current_entry_lines = []

    # Two entry-boundary formats are in use:
    #   (a) "## Stock Name" followed by a nested "### YYYY-MM-DD" sub-heading
    #   (b) "## Stock Name ... [YYYY-MM-DD]" as a single heading (no nested date line)
    # Format (b) used to be silently dropped because only (a)'s date line was matched.
    inline_date_re = re.compile(r"\[(\d{4}-\d{2}-\d{2})\]\s*$")
    for line in lines:
        stock_match = re.match(r"^##\s+(.+)$", line)
        date_match = re.match(r"^###\s+(\d{4}-\d{2}-\d{2})", line)
        if stock_match:
            flush_entry()
            current_stock_heading = line
            stock_has_output = False
            inline_match = inline_date_re.search(line)
            if inline_match:
                current_entry_date = datetime.date.fromisoformat(inline_match.group(1))
                current_entry_lines = [line]
                stock_has_output = True  # heading line already captured in current_entry_lines
            continue
        if date_match:
            flush_entry()
            current_entry_date = datetime.date.fromisoformat(date_match.group(1))
            current_entry_lines = [line]
            continue
        if current_entry_lines is not None and current_stock_heading:
            current_entry_lines.append(line)
    flush_entry()

    if not out:
        print(f"(no analysis.md entries on/after {cutoff.isoformat() if cutoff else 'the beginning'})")
    else:
        sys.stdout.writelines(out)


if __name__ == "__main__":
    main()
