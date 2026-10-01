#!/usr/bin/env python3
"""
Builds the Rs 1,00,000 allocation directly from Confluence-100's top10_investable
list — this is the 2026-09-22 consolidation that replaces portfolio-rs1l-revision's
separate, hand-run EMA-fetch-and-gate cycle. Confluence-100 already re-fetches the
30W EMA for every top candidate (build_confluence100.py) and already hard-gates
top10_investable on being above that EMA (see investable_now() there) — so this
script does no new technical work, only sizing (via build_confluence100.size_by_score,
shared with that script's own 6-month tactical section).

Deliberate simplification vs portfolio-rs1l-revision (agreed with the user): this
is a full stateless rebuild every run, not an incremental revision with exit-pending/
confirm hysteresis, a capex-grace-period tracker, or governance size-down. A name
either clears top10_investable this cycle or it doesn't; weights move to match.
Whipsaw protection now lives one layer up, in paper-trading's own
live-recommendation/track.py, which only rebalances on a >0.5pp weight move.

Run right after build_confluence100.py (same cadence — weekly, via vpscreen-rerank
Step 7). Writes projects/valuepickr-open-screen/data/confluence100_allocation.json.

Usage: python3 projects/valuepickr-open-screen/scripts/build_confluence100_allocation.py
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_confluence100 as c100  # reuse market_regime/size_by_score/atomic_write

DATA_DIR = c100.DATA_DIR

MIN_HOLDINGS = 5          # below this, the allocation isn't diversified enough — abort, keep last good
MAX_HOLDINGS = 10         # top10_investable is already capped here, kept explicit
CONVICTION_FLOOR = 58     # exclude lowest-conviction names (Marksans 52.75, Ajanta 59.2, Engineers 56.25, etc.)
CASH_FLOOR_NORMAL_PCT = 12
CASH_FLOOR_DOWNTREND_PCT = 20  # Section 8E "raised" tier, same number portfolio-rs1l-revision used

# Market regime weight adjustment (2026-10-01: restore timing gates)
# Based on Nifty Smallcap 250 vs its 30W EMA:
MARKET_REGIME_CASH_FLOORS = {
    "weakening": 25,   # < 0.5% above EMA: defensive, shift to cash
    "normal": 12,      # 0.5-2% above EMA: standard allocation
    "strong": 10,      # > 2% above EMA: aggressive, lower cash
}


def classify_market_regime(regime_pct):
    """Classify market strength based on index vs 30W EMA.

    2026-10-01 (restore timing gates): Using the threshold that worked in W35-37
    (Aug-Sep when Nifty SC was +4.67% above EMA, market was strong).
    Oct 1: Nifty SC only +1.1% above EMA — weakening signal.
    """
    if regime_pct < 0.5:
        return "weakening"
    elif regime_pct > 2.0:
        return "strong"
    else:
        return "normal"


def apply_timing_gates(candidates, regime):
    """Apply 30W EMA + conviction filters + market regime adjustments.

    2026-10-01: Restore the timing gates that made W35-37 successful:
      ① Conviction floor (≥65)
      ② Market regime weight adjustment
      ③ Fresh cross tracking
      ④ Conviction boost multiplier
    """
    filtered = []
    for c in candidates:
        # Gate 1: Conviction floor (exclude SJS 56.7, Marksans 52.75, Acutaas 68.5)
        conviction = c.get("conviction_score", 0)
        if conviction < CONVICTION_FLOOR:
            print(f"  ⊘ {c['name']:32s} conviction {conviction:.1f} < {CONVICTION_FLOOR} (filtered)",
                  file=sys.stderr)
            continue

        # Gate 2: Must be above 30W EMA (confirm uptrend) — should already pass investable_now,
        #         but double-check and add metadata
        above_ema = c.get("above_ema", False)
        pct_vs_ema = c.get("pct_vs_ema", 0)

        c["above_ema"] = above_ema
        c["pct_vs_ema"] = pct_vs_ema
        c["distance_to_stop"] = pct_vs_ema  # same as pct_vs_ema for 30W-based stops

        # Track fresh crosses (above EMA with small cushion < 5%)
        c["is_fresh_cross"] = above_ema and 0 < pct_vs_ema < 5

        # Track extended positions (> 25% above EMA) — "hold don't add" annotation
        c["is_extended"] = pct_vs_ema > 25

        filtered.append(c)

    return filtered


def build_allocation(top10, regime):
    candidates = top10[:MAX_HOLDINGS]
    if len(candidates) < MIN_HOLDINGS:
        return None, f"only {len(candidates)} name(s) in top10_investable — below the {MIN_HOLDINGS}-name diversification floor"

    # Apply timing gates (2026-10-01: restore conviction filter + market regime adjustment)
    candidates = apply_timing_gates(candidates, regime)
    if len(candidates) < MIN_HOLDINGS:
        return None, f"only {len(candidates)} name(s) pass conviction_score ≥ {CONVICTION_FLOOR} floor"

    # Market regime weight adjustment (replace simple cash floor with regime-aware floor)
    regime_strength = classify_market_regime(regime.get("pct_vs_ema", 0) if regime["resolved"] else 1.5)
    adjusted_cash_floor = MARKET_REGIME_CASH_FLOORS.get(regime_strength, CASH_FLOOR_NORMAL_PCT)

    # If downtrend flag is set, use raised floor (20%) as before
    if regime["downtrend"]:
        adjusted_cash_floor = CASH_FLOOR_DOWNTREND_PCT

    holdings, cash_pct = c100.size_by_score(
        candidates, "confidence", 100 - adjusted_cash_floor, c100.SINGLE_NAME_CAP_PCT
    )

    # Apply conviction boost multiplier (2026-10-01)
    for h in holdings:
        h["confidence_pct"] = h["confidence"]  # alias for readability in the sidecar
        conviction = h.get("conviction_score", 0)

        # Boost high-conviction names (>75)
        if conviction > 75:
            boost = 1.15
            h["weight_pct"] *= boost
            h["conviction_boost"] = f"×{boost:.2f} (high conviction {conviction:.1f})"
        elif conviction < 65:
            # Should be filtered by now, but just in case
            h["conviction_boost"] = "FILTERED"
        else:
            h["conviction_boost"] = f"neutral (conviction {conviction:.1f})"

    # Renormalize weights after boost
    total_weight = sum(h["weight_pct"] for h in holdings)
    if total_weight > 0:
        for h in holdings:
            h["weight_pct"] = (h["weight_pct"] / total_weight) * (100 - adjusted_cash_floor)

    return {"holdings": holdings, "cash_pct": 100 - sum(h["weight_pct"] for h in holdings),
            "cash_floor_pct": adjusted_cash_floor, "regime_strength": regime_strength}, None


def main():
    conf_path = os.path.join(DATA_DIR, "confluence100.json")
    try:
        conf = c100.load_json(conf_path)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ABORT: could not read {conf_path}: {e}. Run build_confluence100.py first.", file=sys.stderr)
        sys.exit(1)

    top10 = conf.get("top10_investable", [])
    regime = c100.market_regime()
    regime_strength = classify_market_regime(regime.get("pct_vs_ema", 0) if regime["resolved"] else 1.5)

    print(f"\n=== TOP-10 ALLOCATION WITH TIMING GATES (2026-10-01) ===", file=sys.stderr)
    print(f"Market regime ({regime['label']}): {regime_strength.upper()}"
          + (f" ({regime['pct_vs_ema']:+.1f}% vs 30W EMA)" if regime["resolved"] else " (unresolved)"),
          file=sys.stderr)
    print(f"\nTiming gates applied:", file=sys.stderr)
    print(f"  ① Conviction floor: ≥{CONVICTION_FLOOR} (exclude SJS 56.7, Marksans 52.75, Acutaas 68.5)", file=sys.stderr)
    print(f"  ② Market regime adjustment: {regime_strength} → {MARKET_REGIME_CASH_FLOORS[regime_strength]}% cash floor", file=sys.stderr)
    print(f"  ③ Fresh cross tracking: flag names < 5% above 30W EMA", file=sys.stderr)
    print(f"  ④ Extended tracking: flag names > 25% above 30W EMA (hold don't add)", file=sys.stderr)
    print(f"\n", file=sys.stderr)

    alloc, abort_reason = build_allocation(top10, regime)
    out_path = os.path.join(DATA_DIR, "confluence100_allocation.json")
    if alloc is None:
        print(f"ABORT: {abort_reason}. NOT touching {out_path} — last known-good allocation stays live.",
              file=sys.stderr)
        sys.exit(1)

    today = datetime.datetime.now().strftime("%-d %b %Y")
    out = {
        "generated": today,
        "as_of_date": today,
        "source": f"confluence100.json top10_investable, conviction ≥{CONVICTION_FLOOR}, "
                   f"confidence-proportional weights, {c100.SINGLE_NAME_CAP_PCT}% single-name cap, "
                   f"market-regime-adjusted cash floor ({alloc['cash_floor_pct']}% this cycle).",
        "market_regime": regime,
        "regime_strength": alloc["regime_strength"],
        "timing_gates": {
            "conviction_floor": CONVICTION_FLOOR,
            "ema_gate": "above 30W EMA",
            "fresh_cross_threshold_pct": 5,
            "extended_threshold_pct": 25,
        },
        "holdings": alloc["holdings"],
        "cash_pct": alloc["cash_pct"],
        "cash_floor_pct": alloc["cash_floor_pct"],
    }
    c100.atomic_write(out_path, json.dumps(out, indent=2, ensure_ascii=False))

    print(f"Allocation built: {len(alloc['holdings'])} holdings, cash {alloc['cash_pct']:.2f}% "
          f"(floor {alloc['cash_floor_pct']}%)", file=sys.stderr)
    print(f"{'Name':<32} {'Weight':>8} {'Conv':>6} {'EMA %':>7} {'Status':<25}", file=sys.stderr)
    print("-" * 80, file=sys.stderr)
    for h in alloc["holdings"]:
        status = ""
        if h.get("is_fresh_cross"):
            status += "FRESH_CROSS "
        if h.get("is_extended"):
            status += "EXTENDED "
        if not status:
            status = "OK"
        print(f"{h['name']:<32} {h['weight_pct']:7.2f}%  {h['conviction_score']:6.1f} {h['pct_vs_ema']:+7.1f}%  {status:<25}",
              file=sys.stderr)
    print(f"\nWrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
