#!/usr/bin/env python3
"""6-month swing screen: momentum + technical posture for a candidate list.
Reuses paper-trading/scripts/refresh.py fetch/EMA helpers."""
import sys, os, datetime, importlib.util

PAPER_TRADING_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("refresh", os.path.join(PAPER_TRADING_DIR, "scripts/refresh.py"))
rf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rf)

# candidate -> (yahoo symbol, bucket, note)
CANDS = {
    "Venus Remedies":        ("VENUSREM.NS",  "A/catalyst", "print confirms ~19-20% OPM base"),
    "Macpower CNC Machines":  ("MACPOWER.NS",  "A/earnings", "4 straight Q inflection, Q1FY27 rev +56%"),
    "Dynamic Cables":         ("DYNAMIC.NS",   "catalyst",   "greenfield trial Sep26 -> Q4FY27 commercial"),
    "Yash Highvoltage":       ("YASHHV.BO",    "catalyst",   "Vadodara commissioning H1FY27, RIP from Oct"),
    "L. T. Elevators":        ("LTELEVATOR.BO","catalyst",   "H1FY27 print ~Nov + DYPC close 30Sep26"),
    "Neetu Yoshi":            ("NEETUYOSHI.BO","catalyst",   "capacity doubling Sep26, H1FY27 ramp"),
    "Vivid Electromech":      ("VIVIDMECH.BO", "catalyst",   "Ambernath Ph1 commercial Aug26 -> Oct26"),
    "Stylam Industries":      ("STYLAMIND.NS", "catalyst",   "AICA Kogyo 40% stake, Rs2300 open offer"),
    "SML Isuzu":              ("SMLISUZU.NS",  "catalyst",   "M&M promoter-stake acquisition, CCI-approved"),
    "Apcotex Industries":     ("APCOTEXIND.NS","earnings",   "Record Q1FY27 rev +40% PAT +311%"),
    "Electronics Mart India": ("EMIL.NS",      "earnings",   "Q1FY27 PAT +458% blockbuster"),
    "Surya Roshni":           ("SURYAROSNI.NS","earnings",   "Q1FY27 PAT +113% turnaround"),
    "Aimtron Electronics":    ("AIMTRON.NS",   "earnings",   "FY26 rev ~2x verified beat, PAT +77%"),
    "CSB Bank":               ("CSBBANK.NS",   "earnings",   "Q1FY27 PAT +27%, ROE up"),
    "Ujjivan SFB":            ("UJJIVANSFB.NS","earnings",   "record quarter, confirmed inflection"),
    "Privi Speciality":       ("PRIVISCL.NS",  "earnings",   "Q3FY26 PAT +76%, Givaudan JV ramping"),
    "Unimech Aerospace":      ("UNIMECHEM.NS", "earnings",   "Q1 rev +71%, ROE 22.6/ROCE 21.4"),
    "Vikram Thermo":          ("VIKRAMTH.BO",  "earnings",   "Q1FY27 margin expansion"),
    "Senores Pharma":         ("SENORES.NS",   "earnings",   "ANDA compounder beating own guidance"),
    "Thyrocare":              ("THYROCARE.NS", "catalyst",   "pledge released + radiology divestment"),
    "Apollo Micro Systems":   ("APOLLO.NS",    "earnings",   "Premier Explosives acq, defense backward-int"),
    "HBL Engineering":        ("HBLENGINE.NS", "earnings",   "Kavach order book, elevated-tier top holding"),
    "Sambhv Steel Tubes":     ("SAMBHV.NS",    "earnings",   "2 consec Q accelerating quality growth"),
    "Marine Electricals":     ("MARINEList.NS","catalyst",   "order book 2.4x YoY"),
    "Transrail Lighting":     ("TRANSRAILL.NS","earnings",   "strong T&D order book/execution"),
    "Bondada Engineering":    ("BONDADA.NS",   "earnings",   "FY26 rev +81%, order book ~2.5x"),
}

def ret(series, days):
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
    if not evals or len(evals) < n + 1:
        return None
    return (evals[-1] / evals[-1 - n] - 1) * 100

rows = []
for name, (sym, bucket, note) in CANDS.items():
    try:
        dseries = rf.daily_series(sym)
    except Exception as e:
        dseries = None
    if not dseries:
        print(f"{name:<24} {sym:<15} !! no data")
        continue
    last_d, last_p = dseries[-1]
    r1 = ret(dseries, 30); r3 = ret(dseries, 91); r6 = ret(dseries, 182); r12 = ret(dseries, 365)
    # 52w high distance
    lo52 = min(p for d, p in dseries if d >= last_d - datetime.timedelta(days=365))
    hi52 = max(p for d, p in dseries if d >= last_d - datetime.timedelta(days=365))
    from_hi = (last_p / hi52 - 1) * 100
    # weekly 30W EMA
    wk = rf.weekly_closes(sym)
    ext30 = ema30slope = None
    if wk and len(wk) > 32:
        wd = [d for d, c in wk]; wv = [c for d, c in wk]
        e30 = rf.ema(wv, 30)
        ext30 = (wv[-1] - e30[-1]) / e30[-1] * 100
        ema30slope = slope_pct(e30, 8)
    # daily 10W EMA (~50 trading days) via daily series
    dv = [p for d, p in dseries]
    e50 = rf.ema(dv, 50) if len(dv) > 55 else None
    ext10w = (dv[-1] / e50[-1] - 1) * 100 if e50 else None
    ema10wslope = slope_pct(e50, 20) if e50 else None
    rows.append(dict(name=name, sym=sym, bucket=bucket, note=note, last=last_p, last_d=last_d,
                     r1=r1, r3=r3, r6=r6, r12=r12, from_hi=from_hi, ext30=ext30, s30=ema30slope,
                     ext10w=ext10w, s10w=ema10wslope))

def sc(x, lo, hi):
    if x is None: return 0.0
    return max(0.0, min(1.0, (x - lo) / (hi - lo)))

print(f"\n{'name':<24}{'bkt':<11}{'last':>9}{'1m%':>7}{'3m%':>7}{'6m%':>7}{'12m%':>8}{'<hi%':>7}{'ext30':>7}{'s30':>6}{'ext10w':>8}{'s10w':>7}{'SCORE':>7}")
scored = []
for r in rows:
    # 6-month swing score: momentum sweet-spot + trend confirmation, penalise over-extension & far-from-high
    mom3 = sc(r['r3'], -5, 35)
    mom6 = sc(r['r6'], 0, 70)
    trend = 0.5 * sc(r['s30'], 0, 12) + 0.5 * sc(r['s10w'], 0, 15)      # rising EMAs
    posture = 1.0 - sc(r['ext30'], 25, 55)                              # not blown off
    nearhi = sc(r['from_hi'], -30, -2)                                  # close to 52w high
    notdump = 0.0 if (r['r3'] is not None and r['r3'] < -12) else 1.0   # exclude fresh breakdowns
    score = notdump * (0.28*mom3 + 0.22*mom6 + 0.25*trend + 0.15*posture + 0.10*nearhi) * 100
    r['score'] = score
    scored.append(r)

for r in sorted(scored, key=lambda z: -z['score']):
    f = lambda v, w=7, p=1: (f"{v:>{w}.{p}f}" if v is not None else " " * (w-1) + "-")
    print(f"{r['name']:<24}{r['bucket']:<11}{f(r['last'],9,1)}{f(r['r1'])}{f(r['r3'])}{f(r['r6'])}{f(r['r12'],8)}{f(r['from_hi'])}{f(r['ext30'])}{f(r['s30'],6)}{f(r['ext10w'],8)}{f(r['s10w'])}{f(r['score'],7,1)}")
    print(f"    {r['sym']:<14} {r['note']}")
