#!/usr/bin/env python3
"""
paper-trading/swing-6m/track.py -- daily mark-to-market for ALL 6-month swing cohorts.

Since 2026-09-11 this is a WEEKLY, append-only cohort series (swing-6m/cohorts.json),
mirroring the pattern already used for the standard/concentrated paper-trading cohorts:
every Monday a NEW frozen Rs 1,00,000 swing portfolio is decided (picks from
swing_screen.py's momentum+catalyst score, sized by hand per the SKILL) and then left
untouched for its own 6-month horizon and per-holding -16% hard stops -- never
rebalanced, never replaced. (Before this, there was a single ongoing book,
portfolio-v1.json, re-screened monthly; that book is now cohort "2026-W36-inaugural"
in cohorts.json, migrated byte-for-byte, and keeps running to its original
2027-03-03 horizon under the same rules.)

Run any weekday, alongside ../scripts/refresh.py (which invokes this as a subprocess).
This is an ACTIVELY-MANAGED-PER-COHORT book: this script does NOT sell anything. It
surfaces when a rule has triggered so the monthly review (or an ad-hoc call) can act.
Methodology + reasoning: SWING_6M_PORTFOLIO.md. Reuses fetch/EMA helpers from
../scripts/refresh.py. No third-party deps.
"""

import json, os, sys, datetime, importlib.util

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
COHORTS_PATH = os.path.join(HERE, "cohorts.json")
HIST_PATH = os.path.join(HERE, "history.json")
TRACKER_PATH = os.path.join(HERE, "TRACKER.md")


def latest_daily(sym):
    return rf._yahoo(sym, "1y", "1d") or []


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


def market_regime():
    """Portfolio-level overlay (added 2026-09-12, user rule: "don't fight the market"): is the
    benchmark itself (Nifty Smallcap 250) below its own 30W EMA for 2+ consecutive weekly closes?
    Independent of any cohort's own entry date -- this is a market-wide signal, not per-cohort.
    Never force-exits a holding by itself; see SWING_6M_PORTFOLIO.md section 5."""
    label, sym = BENCHMARKS[0]
    post = weekly_ema_posture(sym)
    if post is None:
        return {"label": label, "symbol": sym, "available": False}
    return {"label": label, "symbol": sym, "available": True, "ext_pct": post["ext_pct"],
            "ema": post["ema"], "as_of": post["as_of"], "downtrend": post["below_2_weeks"]}


def benchmark_since(start_date):
    for label, sym in BENCHMARKS:
        b = latest_daily(sym)
        if not b:
            continue
        _, p0 = close_asof(b, start_date)
        p1 = b[-1][1]
        if p0:
            return {"label": label, "symbol": sym, "start": round(p0, 2), "now": round(p1, 2),
                    "return_pct": round((p1 / p0 - 1) * 100, 2), "as_of": b[-1][0].isoformat()}
    return None


def mark_cohort(c, prev_snap, today):
    start_date = datetime.date.fromisoformat(c.get("entry_price_date", c["decided_date"]))
    rows, total_val, fetch_fail = [], 0.0, []
    for h in c["holdings"]:
        sym = h["symbol"]
        dseries = latest_daily(sym)
        if not dseries:
            fetch_fail.append(sym)
            price, pdate, stale = h["entry_price"], None, True
        else:
            price, pdate = dseries[-1][1], dseries[-1][0]
            stale = pdate < today
        value = h["shares"] * price
        total_val += value
        ret_pct = (price / h["entry_price"] - 1) * 100
        day_pct = (dseries[-1][1] / dseries[-2][1] - 1) * 100 if dseries and len(dseries) >= 2 else None
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
    cash = c["cash"]
    port_value = round(total_val + cash, 2)
    port_ret = round((port_value / c.get("capital", CAPITAL_INCEPTION) - 1) * 100, 2)
    day_change_pct = round((port_value / prev_snap["port_value"] - 1) * 100, 2) if prev_snap else None
    bench = benchmark_since(start_date)
    alpha = None if bench is None else round(port_ret - bench["return_pct"], 2)
    all_flags = sorted({f for r in rows for f in r["flags"]})
    horizon_end = c.get("horizon_end_date")
    dte = (datetime.date.fromisoformat(horizon_end) - today).days if horizon_end else None
    snap = {
        "date": today.isoformat(), "week_id": c["week_id"], "series": "swing",
        "decided_date": c["decided_date"], "entry_price_date": c["entry_price_date"],
        "horizon_end_date": horizon_end, "days_to_horizon": dte,
        "port_value": port_value, "port_return_pct": port_ret, "day_change_pct": day_change_pct,
        "invested_value": round(total_val, 2), "cash": cash,
        "benchmark": bench, "alpha_pct": alpha, "flags": all_flags, "holdings": rows,
    }
    return snap, fetch_fail


def main():
    doc = json.load(open(COHORTS_PATH))
    cohorts = doc["cohorts"]
    today = datetime.date.today()

    hist = json.load(open(HIST_PATH)) if os.path.exists(HIST_PATH) else {
        "_readme": "Append-only daily snapshots for the swing-6m cohorts. One per (date, week_id). "
                   "Script-owned (track.py).",
        "snapshots": [],
    }
    prev_by_week = {}
    for s in sorted(hist["snapshots"], key=lambda s: s["date"]):
        if s["date"] < today.isoformat():
            prev_by_week[s["week_id"]] = s

    regime = market_regime()
    marked, all_fail = [], []
    for c in cohorts:
        snap, fail = mark_cohort(c, prev_by_week.get(c["week_id"]), today)
        if regime.get("downtrend"):
            snap["flags"] = sorted(set(snap["flags"]) | {"MARKET DOWNTREND"})
        snap["market_regime"] = regime
        marked.append(snap)
        all_fail.extend(fail)

    hist["snapshots"] = [s for s in hist["snapshots"] if s["date"] != today.isoformat()] + marked
    hist["snapshots"].sort(key=lambda s: (s["date"], s["week_id"]))
    with open(HIST_PATH, "w") as f:
        json.dump(hist, f, indent=2)
        f.write("\n")

    write_tracker(marked, hist)

    print(f"swing-6m track -- {today} ({datetime.datetime.now():%Y-%m-%d %H:%M})  [{len(marked)} cohort(s)]")
    if regime.get("available"):
        tag = "DOWNTREND" if regime["downtrend"] else "ok"
        print(f"  market regime [{tag}]: {regime['label']} {regime['ext_pct']:+.2f}% vs its own 30W EMA (as of {regime['as_of']})")
    else:
        print("  market regime: !! benchmark fetch unavailable, check skipped this run")
    print("-" * 64)
    for m in marked:
        d = "  n/a " if m["day_change_pct"] is None else f"{m['day_change_pct']:+6.2f}"
        dte = "" if m["days_to_horizon"] is None else f"  {m['days_to_horizon']}d to horizon"
        print(f"  {m['week_id']:<22} value {m['port_value']:>12,.2f}  1d {d}%  total {m['port_return_pct']:+7.2f}%{dte}")
        if m["flags"]:
            print(f"      !! RULE FLAGS: {' | '.join(m['flags'])}")
    if len(marked) >= 2:
        avg = sum(m["port_return_pct"] for m in marked) / len(marked)
        print(f"  [swing avg] {avg:+.2f}% over {len(marked)} cohort(s)")
    if all_fail:
        print(f"  !! fetch failed (carried entry price): {', '.join(sorted(set(all_fail)))}")
    print()


def write_tracker(marked, hist):
    L = []
    a = L.append
    a("# 6-Month Swing Portfolio -- Returns Tracker\n")
    a(f"_Regenerated by `paper-trading/swing-6m/track.py` on {datetime.date.today().isoformat()}. Do not hand-edit._\n")
    a("A NEW frozen Rs 1,00,000 swing cohort is decided every Monday (momentum + dated-catalyst screen, "
      "`swing_screen.py`), sized once and then never rebalanced -- same append-only pattern as "
      "`paper-trading/cohorts.json`'s standard/concentrated series, just for the swing methodology. Each "
      "cohort carries its own 6-month horizon and per-holding -16% hard stops; this script never trades, "
      "it only surfaces rule flags (STOP HIT / NEAR STOP / EMA BREAK / EXTENDED) for the monthly review or "
      "an ad-hoc call. Reference: `SWING_6M_PORTFOLIO.md`.\n")
    regime = marked[0].get("market_regime") if marked else None
    if regime and regime.get("available"):
        tag = "**DOWNTREND -- see section 5's market-regime overlay**" if regime["downtrend"] else "ok, no overlay"
        a(f"**Market regime check** ({regime['label']}): {regime['ext_pct']:+.2f}% vs its own 30W EMA "
          f"as of {regime['as_of']} -- {tag}.\n")
    a("---\n")
    a("## Summary -- all swing cohorts\n")
    a("| Cohort | Decided | Entry Basis | Horizon end | Value (Rs) | 1-Day | Return % | Flags |")
    a("|---|---|---|---|---:|---:|---:|---|")
    for m in marked:
        d = "" if m["day_change_pct"] is None else f"{m['day_change_pct']:+.2f}%"
        a(f"| {m['week_id']} | {m['decided_date']} | {m['entry_price_date']} | {m['horizon_end_date']} | "
          f"{m['port_value']:,.2f} | {d} | **{m['port_return_pct']:+.2f}%** | {', '.join(m['flags']) or '-'} |")
    if len(marked) >= 2:
        avg = sum(m["port_return_pct"] for m in marked) / len(marked)
        a(f"\n*Swing series: {len(marked)} cohort(s), average return **{avg:+.2f}%**.*")
    a("\n---\n")
    for m in marked:
        a(f"## Cohort: {m['week_id']}\n")
        a(f"Decided {m['decided_date']}, entry-priced off {m['entry_price_date']} close, horizon ends "
          f"{m['horizon_end_date']} ({m['days_to_horizon']}d left). Invested Rs {m['invested_value']:,.2f} / "
          f"cash Rs {m['cash']:,.2f}.\n")
        b = m["benchmark"]
        if b:
            a(f"Benchmark: {b['label']} ({b['symbol']}) {b['return_pct']:+.2f}% since entry -- "
              f"**alpha {m['alpha_pct']:+.2f} pp**.\n")
        a("| Holding | Wt% | Entry | Price | Return | 1-Day | Value | Dist to stop | vs 30W EMA | Flags |")
        a("|---|---|---|---|---|---|---|---|---|---|")
        for r in sorted(m["holdings"], key=lambda z: -z["return_pct"]):
            dd = "" if r["day_change_pct"] is None else f"{r['day_change_pct']:+.2f}%"
            st = " *" if r["stale"] else ""
            a(f"| {r['name']}{st} | {r['weight_pct']} | {r['entry_price']:.2f} | {r['price']:.2f} | "
              f"{r['return_pct']:+.2f}% | {dd} | {r['value']:,.0f} | {r['dist_to_stop_pct']:+.1f}% | "
              f"{r['ext_vs_30w_ema_pct']} | {', '.join(r['flags']) or '-'} |")
        a(f"| **Total** | | | | **{m['port_return_pct']:+.2f}%** | | **{m['invested_value']:,.0f}** + "
          f"{m['cash']:,.0f} cash | | | |")
        if m["flags"]:
            a("\n**Rule flags active:** " + ", ".join(m["flags"]) + " -- act at the monthly review or ad hoc.")
        a("")
    a("---\n")
    a("## Value history (all cohorts)\n")
    a("| Date | Cohort | Value | Total return | 1-day | Benchmark | Alpha | Flags |")
    a("|---|---|---|---|---|---|---|---|")
    for s in hist["snapshots"][-120:]:
        bb = s.get("benchmark") or {}
        dd = "" if s.get("day_change_pct") is None else f"{s['day_change_pct']:+.2f}%"
        a(f"| {s['date']} | {s['week_id']} | {s['port_value']:,.0f} | {s['port_return_pct']:+.2f}% | {dd} | "
          f"{bb.get('return_pct', '-') if bb else '-'}{'%' if bb else ''} | "
          f"{s.get('alpha_pct', '-')}{' pp' if s.get('alpha_pct') is not None else ''} | "
          f"{', '.join(s.get('flags', [])) or '-'} |")
    with open(TRACKER_PATH, "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
