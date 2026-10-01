#!/usr/bin/env python3
"""
Builds the 6-month tactical (technical-only) allocation from Confluence-100,
separate from the fundamental Top-10 allocation.

2026-10-01: Restore timing gates that made W35-37 successful:
  ① Hard 30W EMA gate — only hold stocks ABOVE 30W EMA (confirmed uptrends)
  ② Technical floor ≥70 — only clear momentum signals
  ③ Market regime portfolio sizing (adaptive to market strength)
  ④ Stop rule — remove if closes below 30W EMA

Philosophy: Momentum + market regime = tactical 6-month hold.
Do NOT override with fundamental conviction; technical signals only.

Writes projects/valuepickr-open-screen/data/confluence100_tactical6m.json

Usage: python3 projects/valuepickr-open-screen/scripts/build_confluence100_tactical.py
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_confluence100 as c100

DATA_DIR = c100.DATA_DIR

# Market regime portfolio sizing (2026-10-01: restore timing gates)
MARKET_REGIME_HOLDINGS = {
    "strong":    10,   # Nifty SC > 1% above 30W EMA (growth mode)
    "normal":    7,    # 0.5-1% above EMA (neutral)
    "weakening": 5,    # < 0.5% above EMA (defensive, current as of Oct 1 +0.3%)
}

TECHNICAL_FLOOR = 70   # Only clear momentum signals (tactical_score ≥ 70)
MIN_HOLDINGS = 3       # Even in worst market, hold at least 3


def classify_market_regime_tactical(regime_pct):
    """Classify market for tactical sizing (different thresholds than fundamental)."""
    if regime_pct < 0.5:
        return "weakening"
    elif regime_pct > 1.0:
        return "strong"
    else:
        return "normal"


def build_tactical_allocation(all_stocks, regime):
    """Build tactical allocation with technical-only ranking + market regime gates."""

    # Filter 1: Above 30W EMA (hard gate — no exceptions)
    candidates = []
    for stock in all_stocks:
        if not stock.get("above_ema", False):
            continue
        if stock.get("tactical_score", 0) < TECHNICAL_FLOOR:
            continue
        candidates.append(stock)

    if len(candidates) < MIN_HOLDINGS:
        return None, f"only {len(candidates)} stocks pass technical floor ≥{TECHNICAL_FLOOR} AND above 30W EMA"

    # Sort by tactical_score (momentum preference)
    candidates.sort(key=lambda x: x.get("tactical_score", 0), reverse=True)

    # Filter 2: Market regime portfolio sizing
    regime_strength = classify_market_regime_tactical(regime.get("pct_vs_ema", 0) if regime["resolved"] else 1.0)
    target_holdings = MARKET_REGIME_HOLDINGS.get(regime_strength, 7)

    # Cap to available candidates
    selected = candidates[:min(target_holdings, len(candidates))]

    # Size by tactical_score (not confidence)
    holdings, cash_pct = c100.size_by_score(
        selected, "tactical_score", 100, 20  # 20% single-name cap for tactical
    )

    # Add tactical metadata
    for h in holdings:
        h["tactical_score"] = h.get("tactical_score", 0)
        h["distance_to_stop"] = h.get("pct_vs_ema", 0)
        h["is_above_ema"] = h.get("above_ema", True)

    return {"holdings": holdings, "cash_pct": cash_pct, "regime_strength": regime_strength,
            "target_holdings": target_holdings}, None


def main():
    conf_path = os.path.join(DATA_DIR, "confluence100.json")
    try:
        conf = c100.load_json(conf_path)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ABORT: could not read {conf_path}: {e}", file=sys.stderr)
        sys.exit(1)

    regime = c100.market_regime()
    regime_strength = classify_market_regime_tactical(regime.get("pct_vs_ema", 0) if regime["resolved"] else 1.0)
    target_holdings = MARKET_REGIME_HOLDINGS[regime_strength]

    print(f"\n=== TACTICAL6M ALLOCATION (2026-10-01) ===", file=sys.stderr)
    print(f"Market regime: {regime_strength.upper()} ({regime.get('pct_vs_ema', 0):+.1f}% vs 30W EMA)", file=sys.stderr)
    print(f"Target holdings: {target_holdings} (market regime sizing)\n", file=sys.stderr)

    # Get all candidates from confluence100
    all_rows = conf.get("rows", [])

    alloc, abort_reason = build_tactical_allocation(all_rows, regime)
    out_path = os.path.join(DATA_DIR, "confluence100_tactical6m.json")

    if alloc is None:
        print(f"ABORT: {abort_reason}. NOT touching {out_path}", file=sys.stderr)
        sys.exit(1)

    today = datetime.datetime.now().strftime("%-d %b %Y")
    out = {
        "generated": today,
        "as_of_date": today,
        "horizon": "6 months",
        "source": f"confluence100.json technical ranking, technical_score ≥{TECHNICAL_FLOOR}, "
                  f"above 30W EMA (hard gate), market-regime sizing ({target_holdings} holdings)",
        "market_regime": regime,
        "regime_strength": alloc["regime_strength"],
        "target_holdings": alloc["target_holdings"],
        "timing_gates": {
            "ema_gate": "above 30W EMA (hard gate)",
            "technical_floor": TECHNICAL_FLOOR,
            "market_regime_sizing": MARKET_REGIME_HOLDINGS,
            "stop_rule": "remove if closes below 30W EMA",
        },
        "holdings": alloc["holdings"],
        "cash_pct": alloc["cash_pct"],
    }

    c100.atomic_write(out_path, json.dumps(out, indent=2, ensure_ascii=False))

    print(f"Tactical allocation built: {len(alloc['holdings'])} holdings (target {target_holdings}), "
          f"cash {alloc['cash_pct']:.1f}%", file=sys.stderr)
    print(f"{'Name':<32} {'Weight':>8} {'Tech':>6} {'EMA %':>7}", file=sys.stderr)
    print("-" * 60, file=sys.stderr)
    for h in sorted(alloc['holdings'], key=lambda x: x['weight_pct'], reverse=True):
        print(f"{h['name']:<32} {h['weight_pct']:7.2f}%  {h['tactical_score']:6.1f} {h['pct_vs_ema']:+7.1f}%",
              file=sys.stderr)
    print(f"\nWrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
