#!/usr/bin/env python3
"""
Builds the 1-month tactical (short-momentum) list from Confluence-100,
distinct from the 6-month tactical list.

Philosophy: For 1-month horizon, we want stocks in UPTRENDS with strong
short-term momentum, filtered to exclude decline-phase positions. This
captures early momentum before it stales, with tighter stops to match
the shorter horizon.

Hard filters:
  - Price ABOVE both 30D EMA and 10D EMA (no below-EMA decline plays)
  - Both 30D and 10D EMAs MUST be rising (confirmed uptrend)
  - 1-month momentum (5D/10D/20D) all positive
  - tactical_1m_score ≥ 65 (higher bar than 6m tactical's ≥70, due to
    decay risk in short-term momentum)

Scoring: 25% 5D ret + 25% 10D ret + 20% 20D ret + 15% EMA trend +
         10% posture + 5% nearhi (distance from 52w high)

Writes projects/valuepickr-open-screen/data/confluence100_tactical1m.json

Usage: python3 projects/valuepickr-open-screen/scripts/build_confluence100_tactical1m.py
"""
import datetime
import json
import os
import sys
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_confluence100 as c100

# Import the daily-series fetching infrastructure from paper-trading refresh
PAPER_TRADING_DIR = os.path.join(c100.ROOT, "projects", "paper-trading")
spec = importlib.util.spec_from_file_location(
    "refresh", os.path.join(PAPER_TRADING_DIR, "scripts/refresh.py")
)
rf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rf)

DATA_DIR = c100.DATA_DIR
MIN_HOLDINGS = 3


def simple_ema(closes, period):
    """Compute simple EMA over closes (list of prices)."""
    if not closes or len(closes) < period:
        return []
    ema_vals = []
    k = 2.0 / (period + 1)
    ema = closes[0]
    for i in range(len(closes)):
        if i == 0:
            ema = closes[0]
        else:
            ema = closes[i] * k + ema * (1 - k)
        ema_vals.append(ema)
    return ema_vals


def ret_pct(series, days):
    """Return % over last N days. series = [(date, price), ...]"""
    if not series or len(series) < 2:
        return None
    last_p = series[-1][1]
    tgt_date = series[-1][0] - datetime.timedelta(days=days)
    prior_price = None
    for d, p in series:
        if d <= tgt_date:
            prior_price = p
    if prior_price is None:
        prior_price = series[0][1]
    return ((last_p / prior_price) - 1) * 100 if prior_price else None


def ema_above(series, ema_vals, idx=-1):
    """True if price is above EMA at index."""
    if not series or not ema_vals or abs(idx) > len(series):
        return None
    price = series[idx][1]
    ema = ema_vals[idx]
    return price > ema if ema > 0 else None


def ema_slope(ema_vals, n=8):
    """EMA slope over last N bars (% change)."""
    if not ema_vals or len(ema_vals) < n + 1:
        return None
    return ((ema_vals[-1] / ema_vals[-1 - n]) - 1) * 100


def sc(x, lo, hi):
    """Clamp & normalize x to [0, 1]."""
    if x is None:
        return 0.0
    return max(0.0, min(1.0, (x - lo) / (hi - lo)))


def tactical_1m_score_one(stock_data, daily_series, ema30_vals, ema10_vals):
    """
    Compute 1-month tactical score for one stock.

    Factors: 25% 5D + 25% 10D + 20% 20D + 15% EMA trend + 10% posture + 5% nearhi
    Returns: (score 0-100, metadata dict) or (None, reason_str)
    """
    if not daily_series or len(daily_series) < 30:
        return None, "insufficient daily data"

    # Hard filters
    price_above_30d = ema_above(daily_series, ema30_vals, -1)
    price_above_10d = ema_above(daily_series, ema10_vals, -1)
    if not (price_above_30d and price_above_10d):
        return None, "price below 30D or 10D EMA (decline filter)"

    # EMA trend: both must be rising
    slope_30d = ema_slope(ema30_vals, n=8)
    slope_10d = ema_slope(ema10_vals, n=8)
    if not (slope_30d and slope_30d > 0.5 and slope_10d and slope_10d > 0.5):
        return None, "EMA(s) not rising"

    # Momentum: 5D, 10D, 20D returns
    r5 = ret_pct(daily_series, 5)
    r10 = ret_pct(daily_series, 10)
    r20 = ret_pct(daily_series, 20)

    if not (r5 is not None and r10 is not None and r20 is not None):
        return None, "missing momentum data"

    if not (r5 > 0 and r10 > 0 and r20 > 0):
        return None, f"negative momentum (5D={r5:.1f}%, 10D={r10:.1f}%, 20D={r20:.1f}%)"

    # Scoring components (each 0-100)
    # Momentum: normalize to 0-100 (assume 0-20% is "very good" for 1 month)
    r5_score = sc(r5, 0, 15) * 100
    r10_score = sc(r10, 0, 12) * 100
    r20_score = sc(r20, 0, 10) * 100

    # EMA trend: normalize slope to 0-5% = excellent
    ema_trend_score = sc(min(slope_30d, slope_10d), 0, 3) * 100

    # Posture (extension vs 10D EMA): sweet spot 5-15%
    if ema10_vals[-1] > 0:
        ext_10d = ((daily_series[-1][1] / ema10_vals[-1]) - 1) * 100
        if ext_10d <= 0:
            posture_score = 0
        elif ext_10d < 2:
            posture_score = 40 * (ext_10d / 2)
        elif ext_10d <= 5:
            posture_score = 40 + 40 * sc(ext_10d, 2, 5)
        elif ext_10d <= 15:
            posture_score = 80 + 20 * sc(ext_10d, 5, 15)
        elif ext_10d <= 30:
            posture_score = 100
        else:
            posture_score = max(50, 100 - sc(ext_10d, 30, 50) * 50)
    else:
        posture_score = 0

    # Nearhi: distance from 52w high
    last_d = daily_series[-1][0]
    lo52 = min(p for d, p in daily_series if d >= last_d - datetime.timedelta(days=365))
    hi52 = max(p for d, p in daily_series if d >= last_d - datetime.timedelta(days=365))
    nearhi_score = 0
    if hi52 > 0:
        pct_from_hi = ((daily_series[-1][1] / hi52) - 1) * 100
        # Sweet spot: within 5% of 52w high
        if pct_from_hi > -5:
            nearhi_score = 100
        elif pct_from_hi > -15:
            nearhi_score = 70
        elif pct_from_hi > -25:
            nearhi_score = 40

    # Weighted composite
    score = (0.25 * r5_score + 0.25 * r10_score + 0.20 * r20_score +
             0.15 * ema_trend_score + 0.10 * posture_score + 0.05 * nearhi_score)

    return score, {
        "r5_pct": round(r5, 1),
        "r10_pct": round(r10, 1),
        "r20_pct": round(r20, 1),
        "ema_trend": round(min(slope_30d, slope_10d), 2),
        "posture": round(posture_score, 1),
        "ext_10d_pct": round(ext_10d, 1) if 'ext_10d' in locals() else None,
        "nearhi_pct": round(pct_from_hi, 1) if 'pct_from_hi' in locals() else None,
    }


def build_tactical1m_list(all_stocks):
    """Build 1-month tactical list with daily-data scoring."""
    candidates = []

    for stock in all_stocks:
        # Start with top-100 pool; only fetch daily data if above 30W EMA
        if not stock.get("above_ema", False):
            continue

        sym = stock.get("symbol")
        if not sym:
            continue

        try:
            daily_series = rf.daily_series(sym)
        except Exception as e:
            continue

        if not daily_series:
            continue

        # Calculate 10D and 30D EMAs from daily series
        closes = [p for d, p in daily_series]
        if len(closes) < 30:
            continue

        ema30_vals = c100.ema30(closes)  # Reuse from confluence100
        ema10_vals = simple_ema(closes, 10)

        score, meta = tactical_1m_score_one(stock, daily_series, ema30_vals, ema10_vals)

        if score is None:
            continue

        candidate = dict(stock)
        candidate["tactical_1m_score"] = round(score, 1)
        candidate.update(meta)
        candidates.append(candidate)

    if len(candidates) < MIN_HOLDINGS:
        return None, f"only {len(candidates)} stocks pass 1m tactical filters"

    # Sort by 1m tactical score
    candidates.sort(key=lambda x: x.get("tactical_1m_score", 0), reverse=True)

    # Market regime sizing (same as 6m tactical)
    regime = c100.market_regime()
    regime_pct = regime.get("pct_vs_ema", 0) if regime["resolved"] else 1.0

    if regime_pct < 0.5:
        regime_strength = "weakening"
        target_holdings = 5
    elif regime_pct > 1.0:
        regime_strength = "strong"
        target_holdings = 8
    else:
        regime_strength = "normal"
        target_holdings = 6

    selected = candidates[:min(target_holdings, len(candidates))]

    # Size by tactical_1m_score
    holdings, cash_pct = c100.size_by_score(
        selected, "tactical_1m_score", 100, 12  # 12.5% single-name cap
    )

    return {"holdings": holdings, "cash_pct": cash_pct, "regime_strength": regime_strength,
            "target_holdings": target_holdings}, None


def main():
    conf_path = os.path.join(DATA_DIR, "confluence100.json")
    try:
        conf = c100.load_json(conf_path)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ABORT: could not read {conf_path}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n=== TACTICAL1M LIST (1-month momentum) ===\n", file=sys.stderr)

    all_rows = conf.get("rows", [])
    alloc, abort_reason = build_tactical1m_list(all_rows)
    out_path = os.path.join(DATA_DIR, "confluence100_tactical1m.json")

    if alloc is None:
        print(f"ABORT: {abort_reason}. NOT touching {out_path}", file=sys.stderr)
        sys.exit(1)

    today = datetime.datetime.now().strftime("%-d %b %Y")
    regime = c100.market_regime()

    out = {
        "generated": today,
        "as_of_date": today,
        "horizon": "1 month",
        "source": "confluence100.json, 1-month momentum + EMA trend scoring",
        "hard_filters": {
            "price_above_ema": "price > both 30D and 10D EMAs",
            "ema_trend": "both 30D and 10D EMAs rising",
            "momentum": "5D/10D/20D returns all positive",
        },
        "market_regime": regime,
        "regime_strength": alloc["regime_strength"],
        "target_holdings": alloc["target_holdings"],
        "holdings": alloc["holdings"],
        "cash_pct": alloc["cash_pct"],
    }

    c100.atomic_write(out_path, json.dumps(out, indent=2, ensure_ascii=False))

    print(f"1-month tactical list built: {len(alloc['holdings'])} holdings "
          f"(target {alloc['target_holdings']}), cash {alloc['cash_pct']:.1f}%\n",
          file=sys.stderr)
    print(f"{'Name':<32} {'Score':>8} {'5D%':>7} {'10D%':>7} {'20D%':>7}",
          file=sys.stderr)
    print("-" * 65, file=sys.stderr)
    for h in sorted(alloc['holdings'], key=lambda x: x['tactical_1m_score'], reverse=True):
        r5 = h.get('r5_pct', '—')
        r10 = h.get('r10_pct', '—')
        r20 = h.get('r20_pct', '—')
        print(f"{h['name']:<32} {h['tactical_1m_score']:7.1f}  {r5:>6} {r10:>6} {r20:>6}",
              file=sys.stderr)
    print(f"\nWrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
