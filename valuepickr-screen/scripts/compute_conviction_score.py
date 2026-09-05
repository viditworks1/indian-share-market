#!/usr/bin/env python3
"""
Computes a mechanical, deterministic 0-100 "conviction_score" for every researched
stock in state.json, WITHOUT touching the existing categorical `conviction` field.

WHY THIS EXISTS
----------------
The categorical `conviction` field (Low/Low-Medium/Medium/Medium-High/High) is
pure per-stock LLM re-derivation every research run, with nothing mechanical to
check consistency against past calls. This has already caused two observed bugs:
(1) the same underlying situation - small-cap, weak trailing-average ROE, real
recent-quarter inflection - got classified differently across two different
stocks in two different runs; (2) an explicit "very-high trusted + no red flag
=> at least Medium-High" rule (see audit_state.py section 3.5) was violated
twice within the same session it was written, because there was no mechanical
scoring layer to check the LLM's output against.

`conviction_score` is a pure function of fields already sitting in state.json
(and trusted_users.json / a stock's own data/<slug>.json). It never calls an
LLM and never touches the network, so given the same state.json it always
produces the same number - useful as a cross-check against the categorical
field, and as a ranking signal that isn't subject to per-run drift.

FORMULA (weights chosen to sum sensibly to 0-100; see component docstrings below)
----------------------------------------------------------------------------------
  raw = base_anchor          (0-40,  from categorical `conviction`)
      + thesis_bonus         (0-20,  from `thesis_fit`)
      + trust_component      (0-25,  from trusted-thread sourcing)
      + corroboration_bonus  (0-15,  from distinct trusted-user count)
      + management_component  (-12..+12, from data/<slug>.json `management_quality`)
      - red_flag_penalty     (0 or 25, or forces the whole score to 0)

  conviction_score = clamp(raw, 0, 100)   [and forced to 0 for AVOID/EXCLUDE
                                            red_flag_tier regardless of the rest]

Max positive raw sum is 40+20+25+15+12 = 112, absorbed by the clamp to 100; a
stock needs to max out every component to hit the ceiling - intentional
headroom, not a bug. `management_component` is TVGP's "P" (promoter/management
quality as a POSITIVE attribute, not just red-flag absence - see
playbook/ishmohit-soic-style.md); it is GUARDED - exactly 0 whenever a stock's
data file has no `management_quality` block, so it is a strict no-op on the
whole registry until `deepdive-top100` starts populating that block. In
practice almost nothing hits the ceiling, which is fine for a ranking signal
(relative ordering matters more than absolute calibration).

USAGE
-----
    python3 compute_conviction_score.py        (from scripts/ or project root)

Writes:
  - state.json:  adds/overwrites `conviction_score` on every stock entry that
    has status in ("researched", "excluded", "avoid") - i.e. has actually been
    through research, not a bare "candidate". Leaves `conviction` untouched.
    Candidates (no research done yet) are left without a conviction_score key
    entirely, since there is nothing to score.
  - data/conviction-scores.json: sorted (descending) ranked report list.

NOTE ON A CONCURRENT AGENT'S WORK
----------------------------------
Another agent is (or may be, depending on timing) landing a shared
`scripts/recency_weight.py` module (function `weight_for_date(date_str,
today=None) -> float`) and a `trusted_conviction_floor_active` field on stock
entries, plus a `trust_tier` field ("core"/"elevated") on trusted_users.json
entries. This script:
  - imports `recency_weight.weight_for_date` if the module exists;
  - otherwise falls back to an inline implementation with the identical
    signature (see `_fallback_weight_for_date` below), which should be
    DELETED and replaced with the real import once scripts/recency_weight.py
    lands for real - it's a heuristic stand-in, not a permanent fixture.
  - already found `trust_tier` present on trusted_users.json (see component 4).
  - did NOT find `trusted_conviction_floor_active` or
    `trusted_conviction_source_user` present on any state.json stock entry as
    of this run - both are handled defensively (treated as absent -> neutral/
    full-weight default) so this script keeps working once they do land.
"""
import datetime
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")
TRUSTED_USERS_PATH = os.path.join(BASE, "trusted_users.json")
DATA_DIR = os.path.join(BASE, "data")
OUT_PATH = os.path.join(BASE, "data", "conviction-scores.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_data_file import resolve_data_path  # noqa: E402

RESEARCHED_STATUSES = ("researched", "excluded", "avoid")

# --- component 1: base conviction anchor (0-40) ------------------------------
CONVICTION_ANCHOR = {
    "Low": 8,
    "Low-Medium": 16,
    "Medium": 24,
    "Medium-High": 32,
    "High": 40,
}

# --- component 2: thesis-fit magnitude bonus (0-20) ---------------------------
THESIS_BONUS = {
    "100x-in-10-years": 20,
    "10x-in-2-3-years": 14,
    "neither": 0,
}

# --- component 3: red-flag penalty --------------------------------------------
RED_FLAG_PENALTY = 25           # "HIGH CAUTION" - positive magnitude, subtracted below
RED_FLAG_ZERO = {"AVOID", "EXCLUDE"}   # forces whole score to 0

# --- component 4: trust/community signal (0-25) -------------------------------
TRUST_STRENGTH_BASE = {"very-high": 18, "high": 8}
FLOOR_INACTIVE_MULTIPLIER = 0.4   # trusted_conviction_floor_active explicitly False
TRUST_TIER_MULTIPLIER = {"core": 1.0, "elevated": 0.6}
TRUST_COMPONENT_CAP = 25

# --- component 6: management quality (-12 .. +12) ----------------------------
# TVGP's "P" (playbook/ishmohit-soic-style.md) - promoter/management quality as a
# POSITIVE attribute. Read from data/<slug>.json's `management_quality` block
# (scripts/ISHMOHIT_SIGNALS_SCHEMA.md). GUARDED: returns exactly 0 when the block
# is absent, so this is a strict no-op on every stock until deepdive-top100
# populates the block. Widened 2026-09-04 (user-requested) to also score
# capital-allocation discipline, related-party-transaction trend, and
# dividend/buyback discipline - previously rpt_trend was collected on every
# block but never actually scored, and there was no field at all for capital
# allocation or shareholder returns. Each of the 5 sub-terms no-ops (0) on its
# own if missing/unclear, so a block with only the original 2 fields scores
# identically to before this widen - the new terms are additive.
MGMT_ASSESSMENT_PTS = {"positive": 6, "neutral": 0, "concern": -6}
MGMT_GUIDANCE_PTS = {
    "reliable": 2, "mixed": 0, "over-promises": -4,
    "no-track-record": 0, "unclear": 0,
}
MGMT_CAPITAL_ALLOC_PTS = {"disciplined": 3, "neutral": 0, "value-destructive": -4}
MGMT_RPT_PTS = {"clean": 2, "flat": 1, "rising": -2, "concerning": -5}
MGMT_SHAREHOLDER_RETURNS_PTS = {"consistent": 2, "initiated": 1, "none": 0, "erratic": -3}
MGMT_COMPONENT_CLAMP = 12

# --- component 5: multi-user corroboration bonus (0-15) ----------------------
CORROBORATION_BONUS = {2: 8, 3: 15}   # 2 distinct users -> 8, 3+ -> 15
# a signal counts toward corroboration only if it's not marked superseded and
# its recency weight clears this bar. trusted_signals[].date is free-text in
# practice ("recent (Q1 FY26 results period)", "backfill", "2026-08-15", etc)
# so this is deliberately a low bar - see _fallback_weight_for_date.
CORROBORATION_RECENCY_MIN_WEIGHT = 0.15


# ------------------------------------------------------------------------------
# recency_weight: prefer the shared module if the other concurrent agent's
# work has landed; otherwise fall back to an inline heuristic with the same
# signature. DELETE this fallback once scripts/recency_weight.py is real.
# ------------------------------------------------------------------------------
_recency_module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recency_weight.py")
if os.path.exists(_recency_module_path):
    sys.path.insert(0, os.path.dirname(_recency_module_path))
    from recency_weight import weight_for_date  # noqa: E402
    _USING_SHARED_RECENCY_MODULE = True
else:
    _USING_SHARED_RECENCY_MODULE = False

    def _fallback_weight_for_date(date_str, today=None):
        """
        Heuristic stand-in for the shared recency_weight.weight_for_date().
        trusted_signals[].date in this project is messy free text, not
        reliably ISO dates, so this does best-effort extraction:
          - explicit ISO date/month ("2026-08-15", "2026-08") -> real decay
            (~1-year half-life exponential decay from `today`)
          - text containing "recent"/"ongoing"/"current" (no explicit stale
            marker) -> high weight (0.85), it's asserted to be fresh
          - text containing "backfill" with no other recency marker -> lower
            weight (0.4), it's explicitly a retroactive/backfilled note
          - a bare 4-digit year found anywhere -> decay from Jan 1 of that year
          - empty/None/unparseable -> neutral default (0.5), conservative but
            not zero (we don't want to silently drop genuine signals just
            because the date field is messy prose)
        Returns a float in [0.0, 1.0].
        """
        if not date_str:
            return 0.5
        if today is None:
            today = datetime.date.today()
        s = date_str.strip().lower()

        iso_match = re.search(r"(\d{4})-(\d{2})(?:-(\d{2}))?", s)
        if iso_match:
            y, m, d = iso_match.groups()
            try:
                dt = datetime.date(int(y), int(m), int(d) if d else 1)
                age_days = max(0, (today - dt).days)
                return round(0.5 ** (age_days / 365.0), 4)
            except ValueError:
                pass

        if any(k in s for k in ("recent", "ongoing", "current")):
            return 0.85

        if "backfill" in s:
            return 0.4

        year_match = re.search(r"(20\d{2})", s)
        if year_match:
            try:
                dt = datetime.date(int(year_match.group(1)), 1, 1)
                age_days = max(0, (today - dt).days)
                return round(0.5 ** (age_days / 365.0), 4)
            except ValueError:
                pass

        return 0.5

    weight_for_date = _fallback_weight_for_date


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def compute_base_anchor(conviction):
    return CONVICTION_ANCHOR.get(conviction, 0)


def compute_thesis_bonus(thesis_fit):
    return THESIS_BONUS.get(thesis_fit, 0)


def compute_red_flag_penalty(red_flag_tier):
    """Returns (penalty_points, force_zero). penalty_points is a positive
    magnitude to be SUBTRACTED from the raw score (0 = no penalty)."""
    if not red_flag_tier:  # None or "" both mean "no red flag" in this data
        return 0, False
    if red_flag_tier in RED_FLAG_ZERO:
        return 0, True
    if red_flag_tier == "HIGH CAUTION":
        return RED_FLAG_PENALTY, False
    # Unrecognized non-empty value: treat conservatively as HIGH CAUTION-
    # equivalent rather than ignoring it silently, and flag it in the report.
    return RED_FLAG_PENALTY, False


def compute_trust_component(entry, trusted_users):
    if entry.get("source") != "trusted-thread":
        return 0.0

    strength = entry.get("trusted_conviction_strength")
    base = TRUST_STRENGTH_BASE.get(strength, 0)
    if base == 0:
        return 0.0

    floor_active = entry.get("trusted_conviction_floor_active")
    floor_multiplier = FLOOR_INACTIVE_MULTIPLIER if floor_active is False else 1.0

    tier_multiplier = 1.0  # neutral default when we can't determine the source user
    source_user = entry.get("trusted_conviction_source_user")
    if source_user and trusted_users:
        user_entry = trusted_users.get(source_user)
        if user_entry:
            tier = user_entry.get("trust_tier")
            tier_multiplier = TRUST_TIER_MULTIPLIER.get(tier, 1.0)

    return min(TRUST_COMPONENT_CAP, base * floor_multiplier * tier_multiplier)


def compute_corroboration_bonus(slug, today=None):
    data_path = resolve_data_path(BASE, DATA_DIR, slug)
    if not os.path.exists(data_path):
        return 0, 0  # (bonus, distinct_user_count)
    try:
        with open(data_path) as f:
            stock_data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return 0, 0

    signals = stock_data.get("trusted_signals")
    if not signals or not isinstance(signals, list):
        return 0, 0

    distinct_users = set()
    for sig in signals:
        if not isinstance(sig, dict):
            continue
        if sig.get("superseded"):
            continue
        username = sig.get("username")
        if not username:
            continue
        w = weight_for_date(sig.get("date"), today=today)
        if w < CORROBORATION_RECENCY_MIN_WEIGHT:
            continue
        distinct_users.add(username)

    count = len(distinct_users)
    if count >= 3:
        return CORROBORATION_BONUS[3], count
    if count == 2:
        return CORROBORATION_BONUS[2], count
    return 0, count


def compute_management_component(slug, warnings=None):
    """(-12..+12) from data/<slug>.json's `management_quality` block; 0 if the block
    is absent or the file is unreadable (the guard that makes this a no-op until
    deepdive-top100 populates it). 5 sub-terms (assessment, guidance_credibility,
    capital_allocation_track_record, rpt_trend, shareholder_returns), each an
    independent no-op (0) when its field is missing/unclear. Returns
    (component_float, detail_dict_or_None)."""
    data_path = resolve_data_path(BASE, DATA_DIR, slug)
    if not os.path.exists(data_path):
        return 0.0, None
    try:
        with open(data_path) as f:
            stock_data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return 0.0, None

    mq = stock_data.get("management_quality")
    if not isinstance(mq, dict):
        return 0.0, None

    assessment = mq.get("assessment")
    guidance = mq.get("guidance_credibility")
    capital_alloc = mq.get("capital_allocation_track_record")
    rpt = mq.get("rpt_trend")
    shareholder_returns = mq.get("shareholder_returns")

    a_pts = MGMT_ASSESSMENT_PTS.get(assessment)
    if a_pts is None:
        if warnings is not None and assessment is not None:
            warnings.append((slug, f"unrecognized management_quality.assessment {assessment!r} -> 0"))
        a_pts = 0
    g_pts = MGMT_GUIDANCE_PTS.get(guidance, 0)

    ca_pts = MGMT_CAPITAL_ALLOC_PTS.get(capital_alloc)
    if ca_pts is None:
        if warnings is not None and capital_alloc is not None and capital_alloc != "unclear":
            warnings.append((slug, f"unrecognized management_quality.capital_allocation_track_record {capital_alloc!r} -> 0"))
        ca_pts = 0

    rpt_pts = MGMT_RPT_PTS.get(rpt)
    if rpt_pts is None:
        if warnings is not None and rpt is not None and rpt != "unclear":
            warnings.append((slug, f"unrecognized management_quality.rpt_trend {rpt!r} -> 0"))
        rpt_pts = 0

    sr_pts = MGMT_SHAREHOLDER_RETURNS_PTS.get(shareholder_returns)
    if sr_pts is None:
        if warnings is not None and shareholder_returns is not None and shareholder_returns != "unclear":
            warnings.append((slug, f"unrecognized management_quality.shareholder_returns {shareholder_returns!r} -> 0"))
        sr_pts = 0

    comp = clamp(a_pts + g_pts + ca_pts + rpt_pts + sr_pts, -MGMT_COMPONENT_CLAMP, MGMT_COMPONENT_CLAMP)
    return float(comp), {
        "assessment": assessment,
        "guidance_credibility": guidance,
        "capital_allocation_track_record": capital_alloc,
        "rpt_trend": rpt,
        "shareholder_returns": shareholder_returns,
    }


def compute_score_for_entry(slug, entry, trusted_users, today=None, warnings=None):
    base_anchor = compute_base_anchor(entry.get("conviction"))
    thesis_bonus = compute_thesis_bonus(entry.get("thesis_fit"))
    red_flag_penalty, force_zero = compute_red_flag_penalty(entry.get("red_flag_tier"))
    trust_component = compute_trust_component(entry, trusted_users)
    corroboration_bonus, distinct_trusted_users = compute_corroboration_bonus(slug, today=today)
    management_component, management_detail = compute_management_component(slug, warnings=warnings)

    if force_zero:
        raw = 0
    else:
        # red_flag_penalty is a positive magnitude (0 or 25) - subtract it.
        raw = (base_anchor + thesis_bonus + trust_component + corroboration_bonus
               + management_component - red_flag_penalty)

    score = clamp(round(raw, 2), 0, 100)

    breakdown = {
        "base_anchor": base_anchor,
        "thesis_bonus": thesis_bonus,
        "red_flag_penalty": red_flag_penalty,
        "red_flag_forced_zero": force_zero,
        "trust_component": round(trust_component, 2),
        "corroboration_bonus": corroboration_bonus,
        "distinct_trusted_users": distinct_trusted_users,
        "management_component": round(management_component, 2),
        "management_quality": management_detail,
    }
    return score, breakdown


def main():
    state = load_json(STATE_PATH)
    if state is None:
        print(f"ERROR: {STATE_PATH} not found", file=sys.stderr)
        sys.exit(1)
    stocks = state.get("stocks", {})

    trusted_users_raw = load_json(TRUSTED_USERS_PATH, default={})
    trusted_users = trusted_users_raw.get("users", {}) if trusted_users_raw else {}

    today = datetime.date.today()

    unrecognized_red_flags = []
    mgmt_warnings = []
    scored = []
    skipped_not_researched = 0

    for slug, entry in stocks.items():
        if entry.get("status") not in RESEARCHED_STATUSES:
            skipped_not_researched += 1
            continue

        rft = entry.get("red_flag_tier")
        if rft and rft not in RED_FLAG_ZERO and rft != "HIGH CAUTION":
            unrecognized_red_flags.append((slug, rft))

        score, breakdown = compute_score_for_entry(
            slug, entry, trusted_users, today=today, warnings=mgmt_warnings
        )
        entry["conviction_score"] = score

        scored.append({
            "slug": slug,
            "name": entry.get("name"),
            "conviction_score": score,
            "conviction": entry.get("conviction"),
            "thesis_fit": entry.get("thesis_fit"),
            "market_cap_tier": entry.get("market_cap_tier"),
            "red_flag_tier": entry.get("red_flag_tier"),
            "source": entry.get("source"),
            "score_breakdown": breakdown,
        })

    scored.sort(key=lambda r: r["conviction_score"], reverse=True)

    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

    with open(OUT_PATH, "w") as f:
        json.dump(scored, f, indent=2)

    print(f"=== compute_conviction_score.py ===")
    print(f"recency_weight source: {'shared scripts/recency_weight.py' if _USING_SHARED_RECENCY_MODULE else 'inline fallback (swap for shared module once it lands)'}")
    print(f"scored {len(scored)} researched-status stocks ({skipped_not_researched} candidates skipped, no research yet)")
    if unrecognized_red_flags:
        print(f"WARNING: {len(unrecognized_red_flags)} unrecognized red_flag_tier values treated as HIGH CAUTION-equivalent (-25): {unrecognized_red_flags}")
    if mgmt_warnings:
        print(f"WARNING: {len(mgmt_warnings)} unrecognized management_quality.assessment values treated as 0:")
        for slug, msg in mgmt_warnings[:20]:
            print(f"  {slug}: {msg}")
    n_mgmt = sum(1 for r in scored if r["score_breakdown"].get("management_quality"))
    print(f"management_component active on {n_mgmt}/{len(scored)} scored stocks "
          f"(0 = block not yet populated by deepdive-top100; a no-op until then)")
    print(f"wrote conviction_score into {STATE_PATH}")
    print(f"wrote ranked report to {OUT_PATH}")
    print()
    print("Top 10:")
    for r in scored[:10]:
        print(f"  {r['conviction_score']:6.2f}  {r['slug']:50s} (categorical: {r['conviction']}, thesis: {r['thesis_fit']})")
    print("Bottom 5:")
    for r in scored[-5:]:
        print(f"  {r['conviction_score']:6.2f}  {r['slug']:50s} (categorical: {r['conviction']}, thesis: {r['thesis_fit']}, red_flag: {r['red_flag_tier']})")


if __name__ == "__main__":
    main()
