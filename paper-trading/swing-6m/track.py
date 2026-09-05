#!/usr/bin/env python3
"""
paper-trading/swing-6m/track.py -- daily mark-to-market for the 6-MONTH SWING portfolio.

Run any weekday, alongside paper-trading/scripts/refresh.py. It:
  1. loads the active portfolio (highest portfolio-v*.json in this folder),
  2. marks every holding to market (latest Yahoo daily close),
  3. computes value / 1-day / return-since-inception, distance-to-stop, and 30W EMA posture,
  4. raises rule flags: STOP HIT, NEAR STOP (<=3%), EMA BREAK (2 weekly closes below 30W EMA),
  5. compares to a small-cap benchmark over the identical window,
  6. appends today's snapshot to history.json (one per date, latest write wins),
  7. regenerates TRACKER.md and prints a summary.

This is an ACTIVELY-MANAGED book: this script does NOT sell anything. It surfaces when a
rule has triggered so the monthly review (or an ad-hoc call) can act. Methodology +
reasoning: docs/SWING_6M_PORTFOLIO.md. Reuses fetch/EMA helpers from ../scripts/refresh.py.
No third-party deps.
"""

import json, os, sys, glob, datetime, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
_spec = importlib.util.spec_from_file_location("refresh", os.path.join(ROOT, "paper-trading/scripts/refresh.py"))
rf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rf)

CAPITAL_INCEPTION = 100000
NEAR_STOP_PCT = 3.0
BENCHMARKS = [
    ("Nifty Smallcap 250", "NIFTYSMLCAP250.NS"),
    ("Nifty Smallcap 100", "^CNXSC"),
    ("BSE SmallCap", "BSE-SMLCAP.BO"),
]


def latest_daily(sym):
    rows = rf._yahoo(sym, "1y", "1d")
    return rows or []


def close_asof(rows, d):
    prior = [r for r in rows if r[0] <= d]
    return prior[-1] if prior else (rows[0] if rows else (None, None))


def weekly_ema_posture(sym, span=30):
    rows = rf.weekly_closes(sym)
    if len(rows) < span + 5:
        return None
    iso_now = datetime.date.today().isocalendar()
    closed = [r for r in rows if r[0].isocalendar()[:2] != iso_now[:2]] or rows[:-1]
    vals = [r[1] for r in closed]
    e = rf.ema(vals, span)
    ext = (vals[-1] - e[-1]) / e[-1] * 100.0
    below2 = len(vals) >= 2 and vals[-1] < e[-1] and vals[-2] < e[-2]
    return {"ext_pct": round(ext, 1), "ema": round(e[-1], 2), "below_2_weeks": below2, "as_of": closed[-1][0].isoformat()}


def active_portfolio_file():
    cands = sorted(glob.glob(os.path.join(HERE, "portfolio-v*.json")))
    if not cands:
        sys.exit("no portfolio-v*.json in " + HERE)
    return cands[-1]


def main():
    pf_path = active_portfolio_file()
    P = json.load(open(pf_path))
    start_date = datetime.date.fromisoformat(P.get("entry_price_date", P["decided_date"]))
    horizon_end = P.get("horizon_end_date")
    cap_start = P.get("capital", CAPITAL_INCEPTION)
    cash = P["cash"]
    today = datetime.date.today()

    hist_path = os.path.join(HERE, "history.json")
    hist = json.load(open(hist_path)) if os.path.exists(hist_path) else {
        "_readme": "Append-only daily snapshots for the 6-month swing portfolio. One per date, latest write wins. Script-owned (track.py).",
        "snapshots": [],
    }
    prev = [s for s in hist["snapshots"] if s["date"] < today.isoformat()]
    prev_snap = prev[-1] if prev else None

    rows, total_val, fetch_fail = [], 0.0, []
    for h in P["holdings"]:
        sym = h["symbol"]
        dseries = latest_daily(sym)
        if not dseries:
            fetch_fail.append(sym)
            price, pdate = h["entry_price"], None
            stale = True
        else:
            price, pdate = dseries[-1][1], dseries[-1][0]
            stale = pdate < today
        value = h["shares"] * price
        total_val += value
        ret_pct = (price / h["entry_price"] - 1) * 100
        # 1-day
        if dseries and len(dseries) >= 2:
            day_pct = (dseries[-1][1] / dseries[-2][1] - 1) * 100
        else:
            day_pct = None
        dist_stop = (price / h["hard_stop"] - 1) * 100  # +% = cushion above stop
        post = weekly_ema_posture(sym)
        flags = []
        if price <= h["hard_stop"]:
            flags.append("STOP HIT")
        elif dist_stop <= NEAR_STOP_PCT:
            flags.append(f"NEAR STOP ({dist_stop:+.1f}%)")
        if post and post["below_2_weeks"]:
            flags.append("EMA BREAK (2 wk < 30W EMA)")
        if post and post["ext_pct"] is not None and post["ext_pct"] > 45:
            flags.append(f"EXTENDED (+{post['ext_pct']:.0f}% vs 30W EMA)")
        rows.append({
            "name": h["name"], "symbol": sym, "weight_pct": h["weight_pct"],
            "entry_price": h["entry_price"], "price": round(price, 2), "as_of": pdate.isoformat() if pdate else None,
            "stale": stale, "shares": h["shares"], "invested": round(h["invested"], 2), "value": round(value, 2),
            "return_pct": round(ret_pct, 2), "day_change_pct": None if day_pct is None else round(day_pct, 2),
            "hard_stop": h["hard_stop"], "dist_to_stop_pct": round(dist_stop, 1),
            "ext_vs_30w_ema_pct": post["ext_pct"] if post else None,
            "catalyst": h.get("catalyst", ""), "flags": flags,
        })

    port_value = round(total_val + cash, 2)
    port_ret = round((port_value / CAPITAL_INCEPTION - 1) * 100, 2)
    day_change_pct = None
    if prev_snap:
        day_change_pct = round((port_value / prev_snap["port_value"] - 1) * 100, 2)

    # benchmark since start_date
    bench = None
    for label, sym in BENCHMARKS:
        b = latest_daily(sym)
        if not b:
            continue
        _, p0 = close_asof(b, start_date)
        p1 = b[-1][1]
        if p0:
            bench = {"label": label, "symbol": sym, "start": round(p0, 2), "now": round(p1, 2),
                     "return_pct": round((p1 / p0 - 1) * 100, 2), "as_of": b[-1][0].isoformat()}
            break

    alpha = None if bench is None else round(port_ret - bench["return_pct"], 2)
    all_flags = sorted({f for r in rows for f in r["flags"]})

    snap = {
        "date": today.isoformat(), "portfolio_version": P.get("version", os.path.basename(pf_path)),
        "port_value": port_value, "port_return_pct": port_ret, "day_change_pct": day_change_pct,
        "invested_value": round(total_val, 2), "cash": cash,
        "benchmark": bench, "alpha_pct": alpha,
        "flags": all_flags, "holdings": rows,
    }
    hist["snapshots"] = [s for s in hist["snapshots"] if s["date"] != today.isoformat()] + [snap]
    hist["snapshots"].sort(key=lambda s: s["date"])
    json.dump(hist, open(hist_path, "w"), indent=2)

    write_tracker(P, snap, hist, pf_path, horizon_end)

    # ---- console summary ----
    print(f"swing-6m track -- {today} ({datetime.datetime.now():%Y-%m-%d %H:%M})  [{P.get('version','?')}]")
    print("-" * 64)
    for r in sorted(rows, key=lambda z: z["return_pct"]):
        d = "" if r["day_change_pct"] is None else f"{r['day_change_pct']:+.2f}%"
        star = "  <<< " + ", ".join(r["flags"]) if r["flags"] else ""
        print(f"  {r['name']:<24} {r['return_pct']:+6.2f}%  (1d {d:>7})  stop {r['dist_to_stop_pct']:+5.1f}%  ema {r['ext_vs_30w_ema_pct']}{star}")
    print("-" * 64)
    d = "" if day_change_pct is None else f"{day_change_pct:+.2f}%"
    print(f"  PORTFOLIO  Rs {port_value:,.2f}   total {port_ret:+.2f}%   1d {d}")
    if bench:
        print(f"  BENCHMARK  {bench['label']}: {bench['return_pct']:+.2f}%   ALPHA {alpha:+.2f} pp   (since {start_date})")
    else:
        print("  BENCHMARK  !! no benchmark series fetched")
    if fetch_fail:
        print(f"  !! fetch failed (carried entry price): {', '.join(fetch_fail)}")
    if all_flags:
        print("  !! RULE FLAGS: " + " | ".join(all_flags))
    else:
        print("  no rule flags")


def write_tracker(P, snap, hist, pf_path, horizon_end):
    L = []
    a = L.append
    a(f"# 6-Month Swing Portfolio -- Returns Tracker\n")
    a(f"_Regenerated by `paper-trading/swing-6m/track.py` on {snap['date']}. Do not hand-edit._\n")
    a(f"- Active portfolio: `{os.path.basename(pf_path)}` ({P.get('version','?')}), started {P.get('entry_price_date')}, horizon ends {horizon_end}")
    a(f"- Reference doc: `docs/SWING_6M_PORTFOLIO.md`")
    b = snap["benchmark"]
    if b:
        a(f"- Benchmark: {b['label']} ({b['symbol']}) -- proxy for {P.get('benchmark','')}\n")
    a(f"\n## Mark-to-market -- {snap['date']}\n")
    d = "" if snap["day_change_pct"] is None else f"{snap['day_change_pct']:+.2f}%"
    a(f"| Portfolio value | Total return | 1-day |")
    a(f"|---|---|---|")
    a(f"| **Rs {snap['port_value']:,.2f}** | **{snap['port_return_pct']:+.2f}%** | {d} |")
    if b:
        a(f"\n| {b['label']} since start | Alpha |")
        a(f"|---|---|")
        a(f"| {b['return_pct']:+.2f}% | **{snap['alpha_pct']:+.2f} pp** |")
    a(f"\n## Holdings\n")
    a(f"| Name | Wt% | Entry | Price | Return | 1-Day | Value | Dist to stop | vs 30W EMA | Flags |")
    a(f"|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(snap["holdings"], key=lambda z: -z["return_pct"]):
        dd = "" if r["day_change_pct"] is None else f"{r['day_change_pct']:+.2f}%"
        st = " *" if r["stale"] else ""
        a(f"| {r['name']}{st} | {r['weight_pct']} | {r['entry_price']:.2f} | {r['price']:.2f} | {r['return_pct']:+.2f}% | {dd} | {r['value']:,.0f} | {r['dist_to_stop_pct']:+.1f}% | {r['ext_vs_30w_ema_pct']} | {', '.join(r['flags']) or '-'} |")
    a(f"| **Total** | | | | **{snap['port_return_pct']:+.2f}%** | | **{snap['invested_value']:,.0f}** + {snap['cash']:,.0f} cash | | | |")
    if snap["flags"]:
        a(f"\n## ⚠ Rule flags active\n")
        for f in snap["flags"]:
            a(f"- **{f}**")
        a(f"\n_This script does not trade. Act on flags at the monthly review or ad hoc._")
    a(f"\n## Value history\n")
    a(f"| Date | Value | Total return | 1-day | Benchmark | Alpha | Flags |")
    a(f"|---|---|---|---|---|---|---|")
    for s in hist["snapshots"][-40:]:
        bb = s.get("benchmark") or {}
        dd = "" if s.get("day_change_pct") is None else f"{s['day_change_pct']:+.2f}%"
        a(f"| {s['date']} | {s['port_value']:,.0f} | {s['port_return_pct']:+.2f}% | {dd} | {bb.get('return_pct','-') if bb else '-'}{'%' if bb else ''} | {s.get('alpha_pct','-')}{' pp' if s.get('alpha_pct') is not None else ''} | {', '.join(s.get('flags',[])) or '-'} |")
    open(os.path.join(HERE, "TRACKER.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
