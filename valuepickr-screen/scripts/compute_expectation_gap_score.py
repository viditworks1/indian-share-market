#!/usr/bin/env python3
"""
compute_expectation_gap_score.py
================================

Computes a mechanical, deterministic 0-100 ``expectation_gap_score`` for every
researched stock that has been through the guidance / expectation-gap deep-dive
(i.e. whose ``data/<slug>.json`` carries a ``market_expectation`` block, written
by the ``deepdive-top100`` task per ``scripts/GUIDANCE_EXPECTATION_SCHEMA.md``).

WHY THIS EXISTS (see playbook/guidance-and-expectation-gap.md for the method)
---------------------------------------------------------------------------
``conviction_score`` answers "is this a good business that trusted people back?"
It deliberately has NO price-vs-expectation input. This score is the orthogonal
half: "is it mispriced, with a catalyst, on acceptable risk?" — the Orbit
Research Step-8 rubric of  Gap x Evidence x Catalyst x Timing x Risk, ranked by
the *quality* of the opportunity rather than the size of the numerical gap.

A portfolio candidate should clear a bar on BOTH scores. ``portfolio-rs1l-
revision`` treats a high-``conviction_score`` name whose ``gap_direction`` is
``priced-in``/``over-optimistic`` (flags ``priced-in`` / ``no-edge`` below) as a
watchlist name, not an add.

PURELY MECHANICAL
-----------------
Like ``compute_conviction_score.py``: a pure function of fields already in
``data/<slug>.json`` + ``state.json``. No LLM, no network. Given the same files
it always produces the same number. It does NOT mutate ``data/<slug>.json`` — a
catalyst whose window has elapsed is treated as ``lapsed`` *for scoring only*;
the next ``deepdive-top100`` pass refreshes the real block.

FORMULA
-------
    gap_frac = gap_points / 40        gap_points (0-40) from gap_direction + |gap_magnitude_pct|

    quality  = 0.35 * evidence_q      each _q normalised to [0,1] (see tables below)
             + 0.30 * catalyst_q
             + 0.20 * timing_q
             + 0.15 * risk_q

    expectation_gap_score = clamp(gap_frac * quality * 100, 0, 100)
                            * 0.5   if red_flag_tier == "HIGH CAUTION"
                            = 0     if red_flag_tier in {AVOID, EXCLUDE}
                            = 0     if gap_direction == "over-optimistic"
                            * 0.7   if earnings_quality.peak_margin_risk and gap in
                                    {underestimated, partially-priced}   (flag "peak-margin-risk")
                            * 0.6   if growth_trajectory.yoy_trend == "decelerating" and gap in
                                    {priced-in, partially-priced}        (flag "growth-decelerating")

The last two ("Ishmohit-lens") haircuts read OPTIONAL blocks on data/<slug>.json
(scripts/ISHMOHIT_SIGNALS_SCHEMA.md). They are strict no-ops when the block is absent, so a
data file without them scores exactly as it did before 2026-08-30.

A weighted-average quality multiplier (not a product of four sub-1.0 factors) so
the 0-100 range is actually used: a genuinely strong setup
(underestimated + strong evidence + dated high-confidence catalyst + <=6M + no
open SPOF) approaches 100; a weak one (priced-in + weak + no catalyst + >18M +
3 SPOFs) lands near 0. Same "relative ordering matters more than absolute
calibration" rationale as conviction_score.

USAGE
-----
    python3 compute_expectation_gap_score.py      (from scripts/ or project root)

Writes:
  - state.json:  adds/overwrites ``expectation_gap_score`` on every researched
    stock that has a ``market_expectation`` block. Researched stocks WITHOUT one
    are left without the key (nothing to score yet) and counted as
    "not_assessed".
  - data/expectation-gap-scores.json:  ranked report consumed by
    make_expectation_gap_ranking.js — {ranked, no_edge, not_assessed}.
"""
import datetime
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")
DATA_DIR = os.path.join(BASE, "data")
OUT_PATH = os.path.join(BASE, "data", "expectation-gap-scores.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_data_file import resolve_data_path  # noqa: E402

RESEARCHED_STATUSES = ("researched", "excluded", "avoid")
RED_FLAG_ZERO = {"AVOID", "EXCLUDE"}

# --- component 1: gap_points (0-40) -----------------------------------------
GAP_DIRECTION_BASE = {
    "underestimated": 28,
    "partially-priced": 18,
    "priced-in": 4,
    "over-optimistic": 0,
}
GAP_MAGNITUDE_ADDER_CAP = 12          # +0.5 pt per 1% gap, capped
GAP_POINTS_CAP = 40

# --- quality multiplier weights (sum to 1.0) ----------------------------
W_EVIDENCE = 0.35
W_CATALYST = 0.30
W_TIMING = 0.20
W_RISK = 0.15

# --- component: evidence_q [0,1] from market_expectation.evidence_quality
EVIDENCE_Q = {
    "strong": 1.00,
    "moderate": 0.75,
    "monitor": 0.50,
    "weak": 0.25,
    "none": 0.05,
}
EVIDENCE_Q_UNKNOWN = 0.05            # conservative default + warn

# --- component: catalyst_q [0,1] --------------------------------------
CATALYST_EVIDENCE_Q = {"high": 1.00, "med": 0.65, "low": 0.35}
CATALYST_EVIDENCE_Q_UNKNOWN = 0.35
CATALYST_UNDATED_MULT = 0.60        # applied to catalyst_q when no date/quarter on record
CATALYST_NONE_Q = 0.15             # no identifiable catalyst — heavily discounted, not zero
CATALYST_STATUS_MULT = {
    "pending": 1.00,
    "in-progress": 1.00,
    "hit": 1.00,                     # the re-rate may still be playing out
    "missed": 0.30,
    "lapsed": 0.00,
}

# --- component: timing_q [0,1] from catalyst.expected_window_months ---
def timing_q_for_window(months):
    if months is None:
        return 0.40                  # unknown timing -> below middling
    if months <= 6:
        return 1.00
    if months <= 12:
        return 0.75
    if months <= 18:
        return 0.45
    return 0.25

# --- component: risk_q [0,1] from thesis-critical single-point-of-failure count
RISK_Q_BY_OPEN_SPOF = {0: 1.00, 1: 0.65, 2: 0.40}   # >=3 -> 0.20
RISK_Q_MIN = 0.20
DIVERSIFICATION_BUMP = 0.15         # >=2 independent evidenced chain links AND <=1 open SPOF
RISK_Q_CAP = 1.00

HIGH_CAUTION_MULT = 0.5

# --- ISHMOHIT-LENS HAIRCUTS (optional data/<slug>.json blocks, no-op when absent) ---
# playbook/ishmohit-soic-style.md + scripts/ISHMOHIT_SIGNALS_SCHEMA.md
PEAK_MARGIN_MULT = 0.70    # earnings_quality.peak_margin_risk on an underestimated/partially-priced gap
GROWTH_DECEL_MULT = 0.60   # growth_trajectory.yoy_trend == "decelerating" on a priced-in/partially-priced gap


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def _parse_date(s):
    if not s or not isinstance(s, str):
        return None
    try:
        return datetime.date.fromisoformat(s.strip()[:10])
    except ValueError:
        return None


def effective_catalyst_status(cat, market_expectation, today):
    """A pending/in-progress catalyst whose window has elapsed is 'lapsed' for
    scoring purposes (we do not write this back to the data file)."""
    if not isinstance(cat, dict):
        return None
    status = cat.get("status") or "pending"
    if status not in ("pending", "in-progress"):
        return status
    months = cat.get("expected_window_months")
    if not isinstance(months, (int, float)):
        return status
    start = _parse_date(cat.get("window_start")) or _parse_date(
        (market_expectation or {}).get("as_of")
    )
    if start is None:
        return status
    # ~30.44 days/month; add the window then compare
    elapsed_deadline = start + datetime.timedelta(days=round(months * 30.44))
    if today > elapsed_deadline:
        return "lapsed"
    return status


def compute_gap_points(me, warnings, slug):
    direction = (me or {}).get("gap_direction")
    if direction not in GAP_DIRECTION_BASE:
        warnings.append((slug, f"unrecognized gap_direction {direction!r} -> treated as priced-in"))
        direction = "priced-in"
    base = GAP_DIRECTION_BASE[direction]
    adder = 0.0
    if direction in ("underestimated", "partially-priced"):
        mag = me.get("gap_magnitude_pct")
        if isinstance(mag, (int, float)):
            adder = min(GAP_MAGNITUDE_ADDER_CAP, abs(mag) * 0.5)
    return min(GAP_POINTS_CAP, base + adder), direction


def compute_evidence_q(me, warnings, slug):
    eq = (me or {}).get("evidence_quality")
    if eq in EVIDENCE_Q:
        return EVIDENCE_Q[eq], eq
    warnings.append((slug, f"unrecognized evidence_quality {eq!r} -> {EVIDENCE_Q_UNKNOWN}"))
    return EVIDENCE_Q_UNKNOWN, eq


def compute_catalyst_q(cat, eff_status, warnings, slug):
    if not isinstance(cat, dict) or not (cat.get("event") or cat.get("expected_window_months") is not None):
        return CATALYST_NONE_Q
    ev = cat.get("evidence_quality")
    base = CATALYST_EVIDENCE_Q.get(ev)
    if base is None:
        warnings.append((slug, f"unrecognized catalyst.evidence_quality {ev!r} -> {CATALYST_EVIDENCE_Q_UNKNOWN}"))
        base = CATALYST_EVIDENCE_Q_UNKNOWN
    if not cat.get("is_dated"):
        base *= CATALYST_UNDATED_MULT
    status_mult = CATALYST_STATUS_MULT.get(eff_status, 1.0)
    return clamp(base * status_mult, 0.0, 1.0)


def compute_risk_q(commits, chain, warnings, slug):
    open_spofs = []
    if isinstance(commits, list):
        for c in commits:
            if not isinstance(c, dict) or not c.get("thesis_critical"):
                continue
            spof = (c.get("single_point_of_failure") or "").strip()
            if spof:
                open_spofs.append(spof.lower())
    n_open = len(set(open_spofs))
    risk = RISK_Q_BY_OPEN_SPOF.get(n_open, RISK_Q_MIN)

    evidenced = []
    if isinstance(chain, dict):
        evidenced = [x for x in (chain.get("evidenced_links") or []) if x]
    if len(evidenced) >= 2 and n_open <= 1:
        risk = min(RISK_Q_CAP, risk + DIVERSIFICATION_BUMP)
    return risk, n_open, sorted(set(open_spofs))


def compute_score_for_stock(slug, entry, today, warnings):
    """Returns (score_or_None, detail_dict). None => not guidance-assessed yet."""
    data_path = resolve_data_path(BASE, DATA_DIR, slug)
    data = load_json(data_path)
    if not isinstance(data, dict):
        return None, {"reason": "no data file"}

    me = data.get("market_expectation")
    if not isinstance(me, dict):
        return None, {"reason": "no market_expectation block"}

    commits = data.get("commitments")
    chain = data.get("earnings_chain")
    cat = data.get("catalyst")

    red_flag = entry.get("red_flag_tier")
    eff_status = effective_catalyst_status(cat, me, today)

    gap_points, direction = compute_gap_points(me, warnings, slug)
    evidence_q, evidence_quality = compute_evidence_q(me, warnings, slug)
    catalyst_q = compute_catalyst_q(cat, eff_status, warnings, slug)
    timing_months = cat.get("expected_window_months") if isinstance(cat, dict) else None
    if not isinstance(timing_months, (int, float)):
        timing_months = None
    timing_q = timing_q_for_window(timing_months)
    risk_q, n_open_spof, open_spofs = compute_risk_q(commits, chain, warnings, slug)

    gap_frac = gap_points / GAP_POINTS_CAP
    quality = (W_EVIDENCE * evidence_q + W_CATALYST * catalyst_q
               + W_TIMING * timing_q + W_RISK * risk_q)
    score = gap_frac * quality * 100

    flags = []
    if red_flag in RED_FLAG_ZERO:
        score = 0.0
        flags.append("red-flag-zeroed")
    elif red_flag == "HIGH CAUTION":
        score *= HIGH_CAUTION_MULT
        flags.append("high-caution")

    if direction == "over-optimistic":
        score = 0.0
        flags.append("no-edge")
    elif direction == "priced-in":
        flags.append("priced-in")

    # --- Ishmohit-lens haircuts (optional blocks; only cut a still-positive score) ---
    eq_block = data.get("earnings_quality")
    if (score > 0 and isinstance(eq_block, dict) and eq_block.get("peak_margin_risk") is True
            and direction in ("underestimated", "partially-priced")):
        score *= PEAK_MARGIN_MULT
        flags.append("peak-margin-risk")
    gt_block = data.get("growth_trajectory")
    if (score > 0 and isinstance(gt_block, dict)
            and gt_block.get("yoy_trend") == "decelerating"
            and direction in ("priced-in", "partially-priced")):
        score *= GROWTH_DECEL_MULT
        flags.append("growth-decelerating")

    if eff_status == "lapsed":
        flags.append("catalyst-lapsed")
    elif not isinstance(cat, dict) or not (cat.get("event") or cat.get("expected_window_months") is not None):
        flags.append("no-catalyst")

    if evidence_quality == "none":
        flags.append("thin-evidence")

    score = clamp(round(score, 2), 0, 100)

    detail = {
        "slug": slug,
        "name": entry.get("name", slug),
        "expectation_gap_score": score,
        "conviction_score": entry.get("conviction_score"),
        "conviction": entry.get("conviction"),
        "thesis_fit": entry.get("thesis_fit"),
        "red_flag_tier": red_flag,
        "market_cap_tier": entry.get("market_cap_tier"),
        "gap_direction": direction,
        "gap_type": me.get("gap_type"),
        "gap_magnitude_pct": me.get("gap_magnitude_pct"),
        "evidence_quality": evidence_quality,
        "catalyst_event": (cat or {}).get("event") if isinstance(cat, dict) else None,
        "catalyst_window_months": timing_months,
        "catalyst_window_start": (cat.get("window_start") if isinstance(cat, dict) else None)
        or me.get("as_of"),
        "catalyst_status_effective": eff_status,
        "catalyst_is_dated": bool(cat.get("is_dated")) if isinstance(cat, dict) else False,
        "risk_open_spof_count": n_open_spof,
        "risk_open_spofs": open_spofs,
        "flags": flags,
        "score_breakdown": {
            "gap_points": round(gap_points, 2),
            "gap_frac": round(gap_frac, 3),
            "evidence_q": evidence_q,
            "catalyst_q": round(catalyst_q, 3),
            "timing_q": timing_q,
            "risk_q": round(risk_q, 3),
            "quality": round(quality, 3),
        },
    }
    return score, detail


def main():
    state = load_json(STATE_PATH)
    if state is None:
        print(f"ERROR: {STATE_PATH} not found", file=sys.stderr)
        sys.exit(1)
    stocks = state.get("stocks", {})
    today = datetime.date.today()

    warnings = []
    ranked, no_edge, not_assessed = [], [], []

    for slug, entry in stocks.items():
        if entry.get("status") not in RESEARCHED_STATUSES:
            continue
        score, detail = compute_score_for_stock(slug, entry, today, warnings)
        if score is None:
            entry.pop("expectation_gap_score", None)
            not_assessed.append({
                "slug": slug,
                "name": entry.get("name", slug),
                "conviction_score": entry.get("conviction_score"),
                "conviction": entry.get("conviction"),
                "thesis_fit": entry.get("thesis_fit"),
            })
            continue
        entry["expectation_gap_score"] = score
        if score <= 0.0 or "no-edge" in detail["flags"] or "red-flag-zeroed" in detail["flags"]:
            no_edge.append(detail)
        else:
            ranked.append(detail)

    ranked.sort(key=lambda r: r["expectation_gap_score"], reverse=True)
    no_edge.sort(key=lambda r: (r.get("conviction_score") or 0), reverse=True)
    not_assessed.sort(key=lambda r: (r.get("conviction_score") or 0), reverse=True)

    # --- catalyst calendar: dated re-rating events, soonest first ----------
    calendar = []
    for r in ranked + no_edge:
        if not r.get("catalyst_event"):
            continue
        months = r.get("catalyst_window_months")
        start = _parse_date(r.get("catalyst_window_start"))
        target = None
        if start is not None and isinstance(months, (int, float)):
            target = (start + datetime.timedelta(days=round(months * 30.44))).isoformat()
        calendar.append({
            "slug": r["slug"],
            "name": r["name"],
            "event": r["catalyst_event"],
            "target_date": target,
            "window_months": months,
            "is_dated": r.get("catalyst_is_dated", False),
            "status_effective": r.get("catalyst_status_effective"),
            "expectation_gap_score": r["expectation_gap_score"],
            "conviction_score": r.get("conviction_score"),
        })
    calendar.sort(key=lambda c: (c["target_date"] is None, c["target_date"] or ""))

    out = {
        "date_compiled": today.isoformat(),
        "method": "playbook/guidance-and-expectation-gap.md · formula in this script's docstring "
                  "and scripts/GUIDANCE_EXPECTATION_SCHEMA.md",
        "scored_count": len(ranked) + len(no_edge),
        "not_assessed_count": len(not_assessed),
        "ranked": ranked,
        "no_edge": no_edge,
        "not_assessed": not_assessed,
        "catalyst_calendar": calendar,
    }

    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)

    print("=== compute_expectation_gap_score.py ===")
    print(f"scored {len(ranked) + len(no_edge)} stocks with a market_expectation block "
          f"({len(ranked)} ranked, {len(no_edge)} no-edge/zeroed); "
          f"{len(not_assessed)} researched stocks not yet guidance-assessed")
    if warnings:
        print(f"WARNING: {len(warnings)} field warnings:")
        for slug, msg in warnings[:20]:
            print(f"  {slug}: {msg}")
    print(f"wrote expectation_gap_score into {STATE_PATH}")
    print(f"wrote ranked report to {OUT_PATH}")
    if ranked:
        print("\nTop 10 by expectation gap:")
        for r in ranked[:10]:
            print(f"  {r['expectation_gap_score']:6.2f}  {r['slug']:44s} "
                  f"[{r['gap_direction']}/{r['gap_type']}] conv={r['conviction_score']} "
                  f"flags={','.join(r['flags']) or '-'}")
    if no_edge:
        print("\nNo-edge (good business, gap already priced / over-optimistic / red-flag):")
        for r in no_edge[:10]:
            print(f"  conv={r['conviction_score']}  {r['slug']:44s} [{r['gap_direction']}] "
                  f"flags={','.join(r['flags'])}")


if __name__ == "__main__":
    main()
