#!/usr/bin/env python3
"""
Recency weighting for trusted-user conviction signals.

Why this exists: forum posts get read months to over a year after they were
written (a trusted user's own journal thread can span years). A conviction
call from a year ago - possibly since exited - should NOT be treated the
same as a fresh one. This module turns a signal's "date" field into a
0.0-1.0 weight that downstream scoring/filtering logic can multiply in.

This is a pure decay-by-age function. It does NOT know about explicit
"I sold/exited" statements - that's a separate, stronger signal, captured
by the `superseded` boolean field on high_conviction_calls / trusted_signals
entries (see audit_recency.py and the trust_tier docs in trusted_users.json).
A superseded=true entry should always be treated as weight 0.0 regardless
of what weight_for_date() returns, because "sold" is an explicit statement,
not a staleness inference.

Buckets (age = today - date_str, in days):
    <= 60 days   : 1.0   ("current")
    61-180 days  : 0.6   (~2-6 months)
    181-365 days : 0.25  (~6-12 months)
    > 365 days   : 0.05  (stale - kept for historical record, not "current")

Usage as a module:
    from recency_weight import weight_for_date
    w = weight_for_date("2026-07-14")

Usage standalone (for testing / spot-checks):
    python3 recency_weight.py 2026-07-14 [YYYY-MM-DD-as-"today", optional]
    python3 recency_weight.py --selftest
"""
import sys
import re
from datetime import date, datetime

# Age-in-days upper bounds -> weight. Checked in order; the first bound the
# age is <= wins. None as the bound means "no upper limit" (the catch-all).
_BUCKETS = [
    (60, 1.0),
    (180, 0.6),
    (365, 0.25),
    (None, 0.05),
]

_FULL_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_YEAR_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
_YEAR_ONLY_RE = re.compile(r"^\d{4}$")


def _parse_date_str(date_str: str):
    """
    Best-effort parse of the date fields actually found in this project's
    JSON (users.json high_conviction_calls / data/<slug>.json trusted_signals).
    Most are clean "YYYY-MM-DD", but some legacy/backfilled entries are
    "YYYY-MM" or a freeform string like "2025-ish (pre Sept-2025 accounting
    controversy)". Returns a `date` object, or None if unparseable.

    Partial dates are anchored to the START of the period (month/year),
    which is the conservative choice for a recency check - it never makes
    a fuzzy date look fresher than it might be.
    """
    if not date_str:
        return None
    s = date_str.strip()

    if _FULL_DATE_RE.match(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            return None

    if _YEAR_MONTH_RE.match(s):
        try:
            return datetime.strptime(s + "-01", "%Y-%m-%d").date()
        except ValueError:
            return None

    if _YEAR_ONLY_RE.match(s):
        try:
            return date(int(s), 1, 1)
        except ValueError:
            return None

    # Freeform strings like "2025-ish (pre Sept-2025 accounting controversy)":
    # try to salvage a leading 4-digit year.
    m = re.match(r"^(\d{4})", s)
    if m:
        try:
            return date(int(m.group(1)), 1, 1)
        except ValueError:
            return None

    return None


def weight_for_date(date_str: str, today: date = None) -> float:
    """
    Return a recency weight in [0.0, 1.0] for a signal dated `date_str`.

    date_str: "YYYY-MM-DD" (preferred). "YYYY-MM" and "YYYY" are accepted
        and anchored to the start of the period. Anything else that isn't
        parseable at all is treated conservatively as stale (0.05) rather
        than erroring, so a batch audit over messy historical data doesn't
        crash - callers that want to know about unparseable dates should
        use _parse_date_str directly or check the printed warnings from
        audit_recency.py.
    today: override "now" for testing / reproducible batch runs. Defaults
        to date.today().
    """
    if today is None:
        today = date.today()

    parsed = _parse_date_str(date_str)
    if parsed is None:
        return 0.05

    age_days = (today - parsed).days
    if age_days < 0:
        # Future-dated entry (clock skew, typo, or a placeholder date like
        # "today" used as a last-touched marker) - treat as fully current
        # rather than penalizing it.
        return 1.0

    for bound, weight in _BUCKETS:
        if bound is None or age_days <= bound:
            return weight
    return 0.05  # unreachable given the None catch-all above, kept for safety


def _selftest():
    today = date(2026, 8, 22)
    cases = [
        ("2026-08-22", 1.0),    # 0 days
        ("2026-07-14", 1.0),    # ~39 days
        ("2026-06-23", 1.0),    # 60 days exactly
        ("2026-06-22", 0.6),    # 61 days
        ("2026-02-23", 0.6),    # ~180 days
        ("2026-02-22", 0.25),   # 181 days
        ("2025-08-22", 0.25),   # 365 days exactly
        ("2025-08-21", 0.05),   # 366 days
        ("2024-01", 0.05),
        ("2023-06", 0.05),
        ("2025-ish (pre Sept-2025 accounting controversy)", 0.05),
        ("", 0.05),
        ("not-a-date", 0.05),
        ("2026-09-01", 1.0),    # future-dated -> current
    ]
    failures = 0
    for date_str, expected in cases:
        got = weight_for_date(date_str, today=today)
        ok = abs(got - expected) < 1e-9
        status = "OK" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"[{status}] weight_for_date({date_str!r}, today={today}) = {got} (expected {expected})")
    print(f"\n{len(cases) - failures}/{len(cases)} passed")
    return failures == 0


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    if args[0] == "--selftest":
        ok = _selftest()
        sys.exit(0 if ok else 1)

    date_str = args[0]
    today = None
    if len(args) > 1:
        today = datetime.strptime(args[1], "%Y-%m-%d").date()
    w = weight_for_date(date_str, today=today)
    print(w)


if __name__ == "__main__":
    main()
