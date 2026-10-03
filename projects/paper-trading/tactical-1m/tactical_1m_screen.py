#!/usr/bin/env python3
"""1-month tactical screen: pure momentum + technical posture for 1-month horizon.
Reuses paper-trading/scripts/refresh.py fetch/EMA helpers.

Filter: price ABOVE rising 30D EMA and 10D EMA (no decline-phase stocks).
Score on: 1-month momentum (5D/10D/20D returns), trend confirmation, relative strength.
"""
import sys, os, datetime, importlib.util

PAPER_TRADING_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("refresh", os.path.join(PAPER_TRADING_DIR, "scripts/refresh.py"))
rf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rf)

# Candidate universe: Confluence-100 + recent high-conviction names
# Will be called with a candidate list from upstream (e.g., Confluence-100 technical, vpscreen-scan tier 4+)
# For this first run, use a subset of strong recent performers that are still in uptrends
CANDS = {}  # Will be filled by caller or from Confluence-100; for now empty placeholder

def ret(series, days):
    """Return % over last N days."""
    if not series or len(series) < 2:
        return None
    last_d, last_p = series[-1]
    tgt = last_d - datetime.timedelta(days=days)
    prior = None
    for d, pnew in series:
        if d <= tgt:
            prior = pnew
    if prior is None:
        prior = series[0][1]
    return (last_p / prior - 1) * 100 if prior else None

def slope_pct(evals, n=8):
    """EMA slope over last N bars (as % change)."""
    if not evals or len(evals) < n + 1:
        return None
    return (evals[-1] / evals[-1 - n] - 1) * 100

def ema_above(series, ema_vals, idx=-1):
    """True if price is above EMA at index (default: latest)."""
    if not series or not ema_vals or abs(idx) > len(series):
        return None
    price = series[idx][1]
    ema = ema_vals[idx]
    return price > ema if ema > 0 else None

_TCFG = rf.CFG["technical"]
THIN_PCT, KNEE_PCT = _TCFG["thin_cushion_pct"], _TCFG["ext_cushion_knee_pct"]

def sc(x, lo, hi):
    """Clamp & normalize x to [0, 1]."""
    if x is None:
        return 0.0
    return max(0.0, min(1.0, (x - lo) / (hi - lo)))

def posture_score_1m(ext10d):
    """For 1-month: looser on extension (momentum plays), but not paper-thin.
    Sweet spot: 5-15% above 10D EMA."""
    if ext10d is None or ext10d <= 0:
        return 0.0
    if ext10d < 2:
        return 0.4 * (ext10d / 2)        # too thin
    if ext10d <= 5:
        return 0.4 + 0.4 * sc(ext10d, 2, 5)   # building cushion
    if ext10d <= 15:
        return 0.8 + 0.2 * sc(ext10d, 5, 15)  # sweet spot
    if ext10d <= 30:
        return 1.0                       # extended but still acceptable for 1m
    return max(0.5, 1.0 - sc(ext10d, 30, 50))  # very extended, some penalty


rows = []
candidates = CANDS if CANDS else {}  # Allow external injection or CLI usage

if not candidates:
    print("Usage: python tactical_1m_screen.py <symbol1> <symbol2> ... OR inject CANDS dict", file=sys.stderr)
    print("or run from upstream (vpscreen-scan tier 4+, Confluence-100, etc.)", file=sys.stderr)
    sys.exit(1)

for name, (sym, note) in candidates.items():
    try:
        dseries = rf.daily_series(sym)
    except Exception as e:
        dseries = None
    if not dseries:
        print(f"{name:<24} {sym:<15} !! no data")
        continue

    last_d, last_p = dseries[-1]
    r5 = ret(dseries, 5)
    r10 = ret(dseries, 10)
    r20 = ret(dseries, 20)
    r30 = ret(dseries, 30)

    # relative strength vs Nifty 500 (broader index, less small-cap specific)
    rs30 = rf.relative_strength_pct(sym, lookback_days=30)

    # 52w high distance
    lo52 = min(p for d, p in dseries if d >= last_d - datetime.timedelta(days=365))
    hi52 = max(p for d, p in dseries if d >= last_d - datetime.timedelta(days=365))
    from_hi = (last_p / hi52 - 1) * 100

    # Daily 30D EMA
    dv = [p for d, p in dseries]
    e30 = rf.ema(dv, 30) if len(dv) > 35 else None
    ext30 = (dv[-1] - e30[-1]) / e30[-1] * 100 if e30 else None
    ema30_slope = slope_pct(e30, 8) if e30 else None
    above_ema30 = ema_above(dseries, e30) if e30 else None

    # Daily 10D EMA
    e10 = rf.ema(dv, 10) if len(dv) > 15 else None
    ext10 = (dv[-1] - e10[-1]) / e10[-1] * 100 if e10 else None
    ema10_slope = slope_pct(e10, 5) if e10 else None
    above_ema10 = ema_above(dseries, e10) if e10 else None

    rows.append(dict(
        name=name, sym=sym, note=note, last=last_p, last_d=last_d,
        r5=r5, r10=r10, r20=r20, r30=r30, from_hi=from_hi,
        ext30=ext30, s30=ema30_slope, above_ema30=above_ema30,
        ext10=ext10, s10=ema10_slope, above_ema10=above_ema10,
        rs30=rs30
    ))

print(f"\n{'name':<24}{'last':>9}{'5d%':>7}{'10d%':>7}{'20d%':>7}{'30d%':>7}{'<hi%':>7}{'ext30':>7}{'s30':>6}{'ext10':>7}{'s10':>6}{'rs30':>8}{'Above30D':>8}{'Above10D':>8}{'SCORE':>7}")
scored = []

for r in rows:
    # Hard filter: must be above BOTH 30D and 10D EMA (no decline-phase stocks)
    if not (r['above_ema30'] and r['above_ema10']):
        print(f"SKIP {r['name']:<20} {r['sym']:<14} - below 30D or 10D EMA")
        continue

    # Hard filter: both EMAs must be rising
    if not (r['s30'] and r['s30'] > 0 and r['s10'] and r['s10'] > 0):
        print(f"SKIP {r['name']:<20} {r['sym']:<14} - EMA(s) not rising")
        continue

    # Scoring for 1-month momentum
    mom5 = sc(r['r5'], 0, 20)         # 5-day sweet spot: 0-20%
    mom10 = sc(r['r10'], 0, 25)       # 10-day sweet spot: 0-25%
    mom20 = sc(r['r20'], 2, 35)       # 20-day: 2-35% (slight positive bias)
    trend = 0.6 * sc(r['s30'], 2, 15) + 0.4 * sc(r['s10'], 3, 20)  # rising EMAs
    posture = posture_score_1m(r['ext10'])
    nearhi = sc(r['from_hi'], -10, -1)  # closer to 52w high = more bullish
    leadership = sc(r['rs30'], -5, 40)  # beating Nifty 500 over 1m

    # Composite: emphasize recent momentum + trend confirmation
    score = (0.25*mom5 + 0.25*mom10 + 0.20*mom20 + 0.15*trend + 0.10*posture + 0.05*nearhi) * 100
    # bonus for leadership
    if r['rs30'] is not None and r['rs30'] > 15:
        score += 5

    r['score'] = score
    scored.append(r)

for r in sorted(scored, key=lambda z: -z['score']):
    f = lambda v, w=7, p=1: (f"{v:>{w}.{p}f}" if v is not None else " " * (w-1) + "-")
    above_e30_str = "✓" if r['above_ema30'] else "✗"
    above_e10_str = "✓" if r['above_ema10'] else "✗"
    print(f"{r['name']:<24}{f(r['last'],9,1)}{f(r['r5'])}{f(r['r10'])}{f(r['r20'])}{f(r['r30'])}{f(r['from_hi'])}{f(r['ext30'])}{f(r['s30'],6)}{f(r['ext10'])}{f(r['s10'],6)}{f(r['rs30'],8)}{above_e30_str:>8}{above_e10_str:>8}{f(r['score'],7,1)}")
    print(f"    {r['sym']:<14} {r['note']}")
