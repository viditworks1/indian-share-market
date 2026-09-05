#!/usr/bin/env python3
"""
compute_quality_score.py
=========================

Computes a mechanical, deterministic 0-100 ``quality_score`` for every researched
stock that has been through the balance-sheet / cash-generation deep-dive (i.e.
whose ``data/<slug>.json`` carries a ``quality_metrics`` block, written by
``deepdive-top100`` per ``scripts/ISHMOHIT_SIGNALS_SCHEMA.md`` §6).

WHY THIS EXISTS
---------------
The user's own stated stock-selection framework (2026-09-04): "growth + margins
+ ROCE + debt + capex + free cash flow + competitive advantage + management
quality." Four of those legs already had a home: growth (`growth_trajectory`),
competitive advantage (`value_chain`), management quality (`management_quality`
-> `conviction_score`'s management_component). Nothing scored ROCE, leverage,
free cash flow conversion, or capex efficiency -- a real gap, since these are
exactly the numbers that quietly diverge from a growth story before an EMA
break or a red flag ever shows up (working-capital bloat, a capex program that
never earns back its cost of capital, leverage creeping up to fund growth that
isn't converting to cash).

`quality_score` is a THIRD, orthogonal score alongside:
  - `conviction_score`   -- is this a good business trusted people back?
  - `expectation_gap_score` -- is it mispriced, with a catalyst, on acceptable risk?
  - `quality_score`      -- is the balance sheet / cash generation actually as
                            good as the growth story suggests?

PURELY MECHANICAL, like the other two -- no LLM, no network. A pure function of
fields already in data/<slug>.json (`quality_metrics`) + state.json
(`red_flag_tier`). Given the same files it always produces the same number.

FORMULA
-------
  roce_component    (0-25)  = roce_level_pts (0-18) + roce_trend_pts (0-7)
  debt_component     (0-20) = from net_debt_to_ebitda, or interest_coverage
                              as a fallback when leverage isn't a meaningful
                              number for this balance sheet
  fcf_component      (0-25) = from fcf_conversion_pct (CAN be negative)
  margin_component   (0-15) = from margin_trend
  capex_component    (0-15) = from capex_efficiency

  raw = roce_component + debt_component + fcf_component + margin_component + capex_component
                                                                     (0-100 already)
  quality_score = clamp(raw, 0, 100)
                  * 0.5  if red_flag_tier == "HIGH CAUTION"
                  = 0    if red_flag_tier in {AVOID, EXCLUDE}

Same missing-field discipline as compute_conviction_score.py /
compute_expectation_gap_score.py: a missing sub-field scores its most
conservative (lowest) value, not a guess; an unrecognised enum value is
treated the same way and logged as a warning. A stock whose data file has NO
`quality_metrics` block at all is NOT scored 0 -- it is left without a
`quality_score` key and reported under `not_assessed`, exactly like an
un-guidance-assessed stock in expectation-gap scoring. This is a strict no-op
on the whole registry until `deepdive-top100` starts populating the block.

USAGE
-----
    python3 compute_quality_score.py      (from scripts/ or project root)

Writes:
  - state.json: adds/overwrites `quality_score` on every stock entry with a
    `quality_metrics` block on its data/<slug>.json. Stocks without one are
    left without the key.
  - data/quality-scores.json: {ranked, weak, not_assessed}, each with a
    score_breakdown per stock -- same shape convention as
    expectation-gap-scores.json.
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")
DATA_DIR = os.path.join(BASE, "data")
OUT_PATH = os.path.join(BASE, "data", "quality-scores.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_data_file import resolve_data_path  # noqa: E402

RESEARCHED_STATUSES = ("researched", "excluded", "avoid")
RED_FLAG_ZERO = {"AVOID", "EXCLUDE"}
HIGH_CAUTION_MULT = 0.5

# --- component 1: ROCE (0-25 = level 0-18 + trend 0-7) -----------------------
def roce_level_pts(roce_pct):
    if not isinstance(roce_pct, (int, float)):
        return 0
    if roce_pct >= 25:
        return 18
    if roce_pct >= 20:
        return 14
    if roce_pct >= 15:
        return 10
    if roce_pct >= 10:
        return 5
    return 0

ROCE_TREND_PTS = {"improving": 7, "stable": 3, "declining": 0}
ROCE_COMPONENT_CAP = 25

# --- component 2: debt / leverage (0-20) -------------------------------------
def debt_component_from_leverage(net_debt_to_ebitda):
    if not isinstance(net_debt_to_ebitda, (int, float)):
        return None
    if net_debt_to_ebitda <= 0:
        return 20
    if net_debt_to_ebitda <= 1:
        return 16
    if net_debt_to_ebitda <= 2:
        return 10
    if net_debt_to_ebitda <= 3:
        return 4
    return 0

def debt_component_from_interest_coverage(interest_coverage):
    if not isinstance(interest_coverage, (int, float)):
        return None
    if interest_coverage >= 8:
        return 16
    if interest_coverage >= 4:
        return 10
    if interest_coverage >= 2:
        return 4
    return 0

DEBT_COMPONENT_CAP = 20

# --- component 3: free cash flow conversion (0-25) ---------------------------
def fcf_component_pts(fcf_conversion_pct):
    if not isinstance(fcf_conversion_pct, (int, float)):
        return 0
    if fcf_conversion_pct >= 80:
        return 25
    if fcf_conversion_pct >= 60:
        return 20
    if fcf_conversion_pct >= 40:
        return 14
    if fcf_conversion_pct >= 20:
        return 7
    if fcf_conversion_pct >= 0:
        return 2
    return 0  # negative conversion -- heavy investment phase or genuinely weak cash generation

FCF_COMPONENT_CAP = 25

# --- component 4: margin trend (0-15) ----------------------------------------
MARGIN_TREND_PTS = {"expanding": 15, "stable": 9, "contracting": 0}
MARGIN_COMPONENT_CAP = 15

# --- component 5: capex efficiency (0-15) -------------------------------------
CAPEX_EFFICIENCY_PTS = {"productive": 15, "neutral": 7, "value-destructive": 0}
CAPEX_COMPONENT_CAP = 15


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def compute_roce_component(qm, warnings, slug):
    level = roce_level_pts(qm.get("roce_pct"))
    trend = qm.get("roce_trend")
    trend_pts = ROCE_TREND_PTS.get(trend, 0)
    if trend is not None and trend not in ROCE_TREND_PTS and trend != "unclear":
        warnings.append((slug, f"unrecognized roce_trend {trend!r} -> 0"))
    return clamp(level + trend_pts, 0, ROCE_COMPONENT_CAP)


def compute_debt_component(qm, warnings, slug):
    ndte = qm.get("net_debt_to_ebitda")
    pts = debt_component_from_leverage(ndte)
    source = "net_debt_to_ebitda"
    if pts is None:
        ic = qm.get("interest_coverage")
        pts = debt_component_from_interest_coverage(ic)
        source = "interest_coverage"
        if pts is None:
            return 0, None  # neither field derivable -- most conservative
    return clamp(pts, 0, DEBT_COMPONENT_CAP), source


def compute_fcf_component(qm):
    return clamp(fcf_component_pts(qm.get("fcf_conversion_pct")), 0, FCF_COMPONENT_CAP)


def compute_margin_component(qm, warnings, slug):
    trend = qm.get("margin_trend")
    pts = MARGIN_TREND_PTS.get(trend, 0)
    if trend is not None and trend not in MARGIN_TREND_PTS and trend != "unclear":
        warnings.append((slug, f"unrecognized margin_trend {trend!r} -> 0"))
    return clamp(pts, 0, MARGIN_COMPONENT_CAP)


def compute_capex_component(qm, warnings, slug):
    eff = qm.get("capex_efficiency")
    pts = CAPEX_EFFICIENCY_PTS.get(eff, 0)
    if eff is not None and eff not in CAPEX_EFFICIENCY_PTS and eff != "unclear":
        warnings.append((slug, f"unrecognized capex_efficiency {eff!r} -> 0"))
    return clamp(pts, 0, CAPEX_COMPONENT_CAP)


def compute_red_flag_multiplier(red_flag_tier):
    """Returns (multiplier, force_zero) -- same convention as the other two scores."""
    if not red_flag_tier:
        return 1.0, False
    if red_flag_tier in RED_FLAG_ZERO:
        return 0.0, True
    if red_flag_tier == "HIGH CAUTION":
        return HIGH_CAUTION_MULT, False
    # Unrecognized non-empty value: treat conservatively as HIGH CAUTION-equivalent.
    return HIGH_CAUTION_MULT, False


def compute_score_for_stock(slug, entry, warnings):
    """Returns (score_or_None, detail_dict). None => no quality_metrics block yet."""
    data_path = resolve_data_path(BASE, DATA_DIR, slug)
    data = load_json(data_path)
    if not isinstance(data, dict):
        return None, {"reason": "no data file"}

    qm = data.get("quality_metrics")
    if not isinstance(qm, dict):
        return None, {"reason": "no quality_metrics block"}

    roce_component = compute_roce_component(qm, warnings, slug)
    debt_component, debt_source = compute_debt_component(qm, warnings, slug)
    fcf_component = compute_fcf_component(qm)
    margin_component = compute_margin_component(qm, warnings, slug)
    capex_component = compute_capex_component(qm, warnings, slug)

    raw = roce_component + debt_component + fcf_component + margin_component + capex_component

    red_flag = entry.get("red_flag_tier")
    mult, force_zero = compute_red_flag_multiplier(red_flag)
    score = 0.0 if force_zero else raw * mult
    score = clamp(round(score, 2), 0, 100)

    flags = []
    if force_zero:
        flags.append("red-flag-zeroed")
    elif red_flag == "HIGH CAUTION":
        flags.append("high-caution")
    if qm.get("roce_pct") is None:
        flags.append("no-roce-data")
    ndte = qm.get("net_debt_to_ebitda")
    if isinstance(ndte, (int, float)) and ndte > 3:
        flags.append("high-leverage")
    fcf = qm.get("fcf_conversion_pct")
    if isinstance(fcf, (int, float)) and fcf < 20:
        flags.append("weak-fcf")
    if qm.get("margin_trend") == "contracting":
        flags.append("margin-contracting")
    if qm.get("capex_efficiency") == "value-destructive":
        flags.append("value-destructive-capex")

    detail = {
        "slug": slug,
        "name": entry.get("name", slug),
        "quality_score": score,
        "conviction_score": entry.get("conviction_score"),
        "red_flag_tier": red_flag,
        "roce_pct": qm.get("roce_pct"),
        "roce_trend": qm.get("roce_trend"),
        "net_debt_to_ebitda": ndte,
        "interest_coverage": qm.get("interest_coverage"),
        "fcf_conversion_pct": fcf,
        "margin_trend": qm.get("margin_trend"),
        "capex_efficiency": qm.get("capex_efficiency"),
        "assessment": qm.get("assessment"),
        "flags": flags,
        "score_breakdown": {
            "roce_component": roce_component,
            "debt_component": debt_component,
            "debt_component_source": debt_source,
            "fcf_component": fcf_component,
            "margin_component": margin_component,
            "capex_component": capex_component,
            "raw": raw,
            "red_flag_multiplier": mult,
        },
    }
    return score, detail


def main():
    state = load_json(STATE_PATH)
    if state is None:
        print(f"ERROR: {STATE_PATH} not found", file=sys.stderr)
        sys.exit(1)
    stocks = state.get("stocks", {})

    warnings = []
    ranked, weak, not_assessed = [], [], []
    skipped_not_researched = 0

    for slug, entry in stocks.items():
        if entry.get("status") not in RESEARCHED_STATUSES:
            skipped_not_researched += 1
            continue

        score, detail = compute_score_for_stock(slug, entry, warnings)
        if score is None:
            entry.pop("quality_score", None)
            not_assessed.append({
                "slug": slug,
                "name": entry.get("name", slug),
                "conviction_score": entry.get("conviction_score"),
                "red_flag_tier": entry.get("red_flag_tier"),
            })
            continue
        entry["quality_score"] = score
        if score == 0.0 or "value-destructive-capex" in detail["flags"]:
            weak.append(detail)
        else:
            ranked.append(detail)

    ranked.sort(key=lambda r: r["quality_score"], reverse=True)
    weak.sort(key=lambda r: (r.get("conviction_score") or 0), reverse=True)
    not_assessed.sort(key=lambda r: (r.get("conviction_score") or 0), reverse=True)

    out = {
        "method": "the user's stated screening framework (2026-09-04): growth + margins + ROCE "
                  "+ debt + capex + free cash flow + competitive advantage + management quality. "
                  "This score covers the four legs (ROCE, debt, FCF, capex) that had no numeric "
                  "home before. Formula in this script's docstring and "
                  "scripts/QUALITY_SCORE_METHODOLOGY.md.",
        "scored_count": len(ranked) + len(weak),
        "not_assessed_count": len(not_assessed),
        "ranked": ranked,
        "weak": weak,
        "not_assessed": not_assessed,
    }

    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)

    print("=== compute_quality_score.py ===")
    print(f"scored {len(ranked) + len(weak)} stocks with a quality_metrics block "
          f"({len(ranked)} ranked, {len(weak)} weak/zeroed); "
          f"{len(not_assessed)} researched stocks not yet quality-assessed "
          f"({skipped_not_researched} candidates skipped, no research yet)")
    if warnings:
        print(f"WARNING: {len(warnings)} field warnings:")
        for slug, msg in warnings[:20]:
            print(f"  {slug}: {msg}")
    print(f"wrote quality_score into {STATE_PATH}")
    print(f"wrote ranked report to {OUT_PATH}")
    if ranked:
        print("\nTop 10 by quality_score:")
        for r in ranked[:10]:
            print(f"  {r['quality_score']:6.2f}  {r['slug']:44s} "
                  f"ROCE={r['roce_pct']} trend={r['roce_trend']} "
                  f"flags={','.join(r['flags']) or '-'}")
    if weak:
        print("\nWeak/zeroed:")
        for r in weak[:10]:
            print(f"  {r['quality_score']:6.2f}  {r['slug']:44s} flags={','.join(r['flags'])}")


if __name__ == "__main__":
    main()
