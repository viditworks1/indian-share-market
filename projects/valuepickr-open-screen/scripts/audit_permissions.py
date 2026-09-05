#!/usr/bin/env python3
"""
Removes permission-allow entries from .claude/settings.local.json that are
already fully covered by an existing wildcard entry in the SAME file - this is
a pure no-op cleanup (removing a rule that's redundant doesn't change what's
allowed, since the wildcard already covers it), never widens scope, never adds
a new wildcard on its own initiative. Keeps the file from growing without bound
as every new stock/URL/thread accumulates its own exact-match line.

A wildcard entry looks like "Bash(<prefix>*)" (trailing '*' inside the parens).
Any other entry "Bash(<literal>)" is redundant if <literal> starts with <prefix>
for some wildcard entry in the file.

Usage: python3 audit_permissions.py [--dry-run]
"""
import argparse
import json
import os
import re

SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    ".claude", "settings.local.json",
)


def extract_wildcard_prefixes(allow):
    prefixes = []
    for rule in allow:
        m = re.match(r"^Bash\((.*)\*\)$", rule)
        if m:
            prefixes.append(m.group(1))
    return prefixes


def is_redundant(rule, prefixes):
    m = re.match(r"^Bash\((.*)\)$", rule)
    if not m:
        return False
    literal = m.group(1)
    if literal.endswith("*"):
        return False  # it's itself a wildcard, never drop those
    return any(literal.startswith(p) for p in prefixes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(SETTINGS_PATH):
        print("no settings.local.json found, nothing to do")
        return

    with open(SETTINGS_PATH) as f:
        data = json.load(f)

    allow = data.get("permissions", {}).get("allow", [])
    prefixes = extract_wildcard_prefixes(allow)

    keep, dropped = [], []
    for rule in allow:
        if is_redundant(rule, prefixes):
            dropped.append(rule)
        else:
            keep.append(rule)

    print(f"=== audit_permissions.py report ({'dry-run' if args.dry_run else 'fix applied'}) ===")
    print(f"total rules: {len(allow)} | wildcard rules: {len(prefixes)} | redundant (removable): {len(dropped)}")
    for r in dropped:
        print(f"- REDUNDANT (covered by an existing wildcard): {r}")

    if dropped and not args.dry_run:
        data["permissions"]["allow"] = keep
        with open(SETTINGS_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print(f"removed {len(dropped)} redundant rules, {len(keep)} remain")
    elif not dropped:
        print("(clean - nothing redundant)")


if __name__ == "__main__":
    main()
