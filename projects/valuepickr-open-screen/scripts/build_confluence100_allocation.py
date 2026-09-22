#!/usr/bin/env python3
"""
Builds the Rs 1,00,000 allocation directly from Confluence-100's top10_investable
list — this is the 2026-09-22 consolidation that replaces portfolio-rs1l-revision's
separate, hand-run EMA-fetch-and-gate cycle. Confluence-100 already re-fetches the
30W EMA for every top candidate (build_confluence100.py) and already hard-gates
top10_investable on being above that EMA (see investable_now() there) — so this
script does no new technical work, only sizing.

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
import build_confluence100 as c100  # reuse yahoo_chart/ema30/trailing_return_pct

ROOT = c100.ROOT
DATA_DIR = c100.DATA_DIR

MIN_HOLDINGS = 5          # below this, the allocation isn't diversified enough — abort, keep last good
MAX_HOLDINGS = 10         # top10_investable is already capped here, kept explicit
SINGLE_NAME_CAP_PCT = 12.5
CASH_FLOOR_NORMAL_PCT = 12
CASH_FLOOR_DOWNTREND_PCT = 20  # Section 8E "raised" tier, same number portfolio-rs1l-revision used

REGIME_BENCHMARK_SYMBOL = "NIFTYSMLCAP250.NS"
REGIME_BENCHMARK_LABEL = "Nifty Smallcap 250"


def market_regime():
    """Mirrors portfolio-rs1l-revision Step 3.5: is the benchmark's last completed
    weekly close below its own 30W EMA for 2+ consecutive weeks ("broad downtrend
    confirmed")? Falls back to 'no override' (not downtrend) if the fetch fails —
    the same fail-open behavior the rest of this pipeline uses elsewhere, since a
    data gap here shouldn't itself force the raised cash floor."""
    pairs = c100.yahoo_chart(REGIME_BENCHMARK_SYMBOL)
    if not pairs or len(pairs) < 32:
        return {"resolved": False, "downtrend": False, "label": REGIME_BENCHMARK_LABEL}
    closes = [c for _, c in pairs]
    emas = c100.ema30(closes)
    below_last = closes[-1] < emas[-1]
    below_prev = closes[-2] < emas[-2]
    downtrend = below_last and below_prev
    pct = (closes[-1] / emas[-1] - 1) * 100
    return {
        "resolved": True,
        "downtrend": downtrend,
        "label": REGIME_BENCHMARK_LABEL,
        "pct_vs_ema": round(pct, 1),
        "above_ema": not below_last,
    }


def build_allocation(top10, regime):
    candidates = top10[:MAX_HOLDINGS]
    if len(candidates) < MIN_HOLDINGS:
        return None, f"only {len(candidates)} name(s) in top10_investable — below the {MIN_HOLDINGS}-name diversification floor"

    cash_floor = CASH_FLOOR_DOWNTREND_PCT if regime["downtrend"] else CASH_FLOOR_NORMAL_PCT
    invested_target = 100 - cash_floor

    total_conf = sum(r["confidence"] for r in candidates)
    weights = {r["slug"]: (r["confidence"] / total_conf) * invested_target for r in candidates}

    # Cap-and-redistribute: repeatedly clamp anything over the single-name cap and
    # spread the excess proportionally across the still-uncapped names, until stable.
    for _ in range(len(candidates) + 2):
        capped = {s: w for s, w in weights.items() if w > SINGLE_NAME_CAP_PCT}
        if not capped:
            break
        excess = sum(w - SINGLE_NAME_CAP_PCT for w in capped.values())
        for s in capped:
            weights[s] = SINGLE_NAME_CAP_PCT
        uncapped = {s: w for s, w in weights.items() if s not in capped}
        uncapped_total = sum(uncapped.values())
        if uncapped_total <= 0:
            break
        for s in uncapped:
            weights[s] += excess * (uncapped[s] / uncapped_total)

    holdings = []
    invested_sum = 0.0
    for r in candidates:
        w = round(weights[r["slug"]], 2)
        invested_sum += w
        holdings.append({
            "name": r["name"],
            "slug": r["slug"],
            "symbol": r["symbol"],
            "weight_pct": w,
            "confidence_pct": r["confidence"],
            "fundamental_score": r["fundamental_score"],
            "technical_score": r["technical_score"],
            "momentum_score": r["momentum_score"],
            "thesis_fit": r["thesis_fit"],
            "tagline": r["tagline"],
        })
    cash_pct = round(100 - invested_sum, 2)
    return {"holdings": holdings, "cash_pct": cash_pct, "cash_floor_pct": cash_floor}, None


def main():
    conf_path = os.path.join(DATA_DIR, "confluence100.json")
    try:
        conf = c100.load_json(conf_path)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ABORT: could not read {conf_path}: {e}. Run build_confluence100.py first.", file=sys.stderr)
        sys.exit(1)

    top10 = conf.get("top10_investable", [])
    regime = market_regime()
    print(f"Market regime ({regime['label']}): "
          + (f"{'DOWNTREND' if regime['downtrend'] else 'ok'}"
             + (f" ({regime['pct_vs_ema']:+.1f}% vs 30W EMA)" if regime["resolved"] else "")
             if regime["resolved"] else "not resolved — fail-open, normal cash floor"),
          file=sys.stderr)

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
        "source": "confluence100.json top10_investable, confidence-proportional weights, "
                   f"{SINGLE_NAME_CAP_PCT}% single-name cap, cash floor "
                   f"{CASH_FLOOR_DOWNTREND_PCT}% in a confirmed broad downtrend else {CASH_FLOOR_NORMAL_PCT}%.",
        "market_regime": regime,
        "holdings": alloc["holdings"],
        "cash_pct": alloc["cash_pct"],
        "cash_floor_pct": alloc["cash_floor_pct"],
    }
    c100.atomic_write(out_path, json.dumps(out, indent=2, ensure_ascii=False))

    print(f"\nAllocation built: {len(alloc['holdings'])} holdings, cash {alloc['cash_pct']}% "
          f"(floor {alloc['cash_floor_pct']}%)", file=sys.stderr)
    for h in alloc["holdings"]:
        print(f"  {h['weight_pct']:5.2f}%  {h['name']:<32} conf {h['confidence_pct']}", file=sys.stderr)
    print(f"\nWrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
