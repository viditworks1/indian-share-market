#!/usr/bin/env python3
"""Daily MTM tracking for 1-month tactical cohorts (append-only to cohorts.json).
Mark-to-market every holding in every cohort, check stops & EMA crosses, regenerate TRACKER.md."""
import sys, os, json, datetime, importlib.util
from collections import defaultdict

PAPER_TRADING_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("refresh", os.path.join(PAPER_TRADING_DIR, "scripts/refresh.py"))
rf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rf)

TACTICAL_1M_DIR = os.path.dirname(os.path.abspath(__file__))
COHORTS_PATH = os.path.join(TACTICAL_1M_DIR, "cohorts.json")
HISTORY_PATH = os.path.join(TACTICAL_1M_DIR, "history.json")
TRACKER_MD_PATH = os.path.join(TACTICAL_1M_DIR, "TRACKER.md")

def load_cohorts():
    if not os.path.exists(COHORTS_PATH):
        return {"cohorts": []}
    with open(COHORTS_PATH) as f:
        return json.load(f)

def load_history():
    if not os.path.exists(HISTORY_PATH):
        return []
    with open(HISTORY_PATH) as f:
        return json.load(f)

def save_history(hist):
    with open(HISTORY_PATH, "w") as f:
        json.dump(hist, f, indent=2)

def get_price(sym):
    """Fetch latest price for symbol."""
    try:
        series = rf.daily_series(sym)
        if series and len(series) > 0:
            return series[-1][1]  # (date, price)
    except:
        pass
    return None

def get_ema_values(sym, ema_periods):
    """Fetch EMA for given periods (30, 10)."""
    try:
        series = rf.daily_series(sym)
        if not series or len(series) < ema_periods + 5:
            return {}
        prices = [p for d, p in series]
        result = {}
        for period in ema_periods:
            ema_vals = rf.ema(prices, period)
            if ema_vals:
                result[period] = ema_vals[-1]  # latest
        return result
    except:
        pass
    return {}

def get_benchmark_price(bench_sym="NIFTY500.NS"):
    """Fetch benchmark (Nifty 500) price."""
    return get_price(bench_sym)

def mark_to_market():
    cohorts_data = load_cohorts()
    hist = load_history()
    today = datetime.date.today().isoformat()

    # Skip if already marked today
    if hist and hist[-1].get("date") == today:
        print(f"Already marked {today}, skipping")
        return

    snapshot = {"date": today, "cohorts": {}}
    bench_price = get_benchmark_price()

    for cohort in cohorts_data.get("cohorts", []):
        week_id = cohort.get("week_id")
        entry_price_date = cohort.get("entry_price_date")
        horizon_end_date = cohort.get("horizon_end_date")

        # Skip if cohort already closed
        if today > horizon_end_date:
            continue

        cohort_data = {
            "week_id": week_id,
            "nav": 0,
            "return_pct": 0,
            "holdings": [],
            "benchmark_price": bench_price,
            "flags": []
        }

        total_value = 0
        total_invested = cohort.get("capital", 100000)
        total_initial_invested = 0

        for holding in cohort.get("holdings", []):
            sym = holding["symbol"]
            entry_price = holding["entry_price"]
            shares = holding["shares"]
            invested = holding["invested"]

            curr_price = get_price(sym)
            ema_vals = get_ema_values(sym, [30, 10])

            if not curr_price:
                curr_price = entry_price  # fallback

            curr_value = curr_price * shares
            pnl = curr_value - invested
            pnl_pct = (pnl / invested * 100) if invested > 0 else 0

            hard_stop = entry_price * (1 - 0.10)  # -10% for 1M tactical
            dist_to_stop_pct = ((curr_price - hard_stop) / hard_stop * 100) if hard_stop > 0 else 0

            ema30 = ema_vals.get(30, entry_price)
            ema10 = ema_vals.get(10, entry_price)
            above_ema30 = "✓" if curr_price > ema30 else "✗"
            above_ema10 = "✓" if curr_price > ema10 else "✗"

            ext10 = ((curr_price - ema10) / ema10 * 100) if ema10 > 0 else 0

            flags = []
            if curr_price <= hard_stop:
                flags.append("STOP HIT")
            elif dist_to_stop_pct < 3:
                flags.append(f"NEAR STOP ({dist_to_stop_pct:.1f}pp)")
            if curr_price < ema30:
                flags.append("BELOW 30D EMA")
            if curr_price < ema10:
                flags.append("BELOW 10D EMA")

            holding_rec = {
                "name": holding["name"],
                "symbol": sym,
                "entry_price": entry_price,
                "curr_price": curr_price,
                "shares": shares,
                "invested": invested,
                "curr_value": curr_value,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "ema30": ema30,
                "ema10": ema10,
                "ext10_pct": ext10,
                "above_ema30": above_ema30,
                "above_ema10": above_ema10,
                "dist_to_stop_pct": dist_to_stop_pct,
                "flags": flags
            }
            cohort_data["holdings"].append(holding_rec)
            total_value += curr_value
            total_initial_invested += invested

        # Calculate cohort-level return
        cohort_data["nav"] = total_value + cohort.get("cash", 0)
        if total_initial_invested > 0:
            cohort_data["return_pct"] = ((total_value - total_initial_invested) / total_initial_invested * 100)

        snapshot["cohorts"][week_id] = cohort_data

    # Save snapshot
    hist.append(snapshot)
    save_history(hist)

    # Regenerate TRACKER.md
    generate_tracker_md(cohorts_data, hist[-1])
    print(f"Marked to market: {today}, {len(snapshot['cohorts'])} cohorts tracked")

def generate_tracker_md(cohorts_data, latest_snapshot):
    """Regenerate TRACKER.md with all cohorts' status."""
    lines = ["# 1-Month Tactical Portfolio — Daily Tracker\n"]
    lines.append(f"**Last updated:** {latest_snapshot['date']}\n\n")

    for week_id, cohort_snap in sorted(latest_snapshot["cohorts"].items()):
        cohort = next((c for c in cohorts_data["cohorts"] if c["week_id"] == week_id), {})
        lines.append(f"## {week_id}\n")
        lines.append(f"- **NAV:** Rs {cohort_snap['nav']:,.0f}\n")
        lines.append(f"- **Return:** {cohort_snap['return_pct']:+.2f}%\n")
        lines.append(f"- **Horizon:** {cohort.get('decided_date')} → {cohort.get('horizon_end_date')}\n")

        if cohort_snap.get("flags"):
            lines.append(f"- **Flags:** {', '.join(cohort_snap['flags'])}\n")

        # Holdings table
        lines.append("\n| Name | Price | Shares | Invested | Current | P&L | P&L % | Dist Stop | Flags |\n")
        lines.append("|------|-------|--------|----------|---------|-----|-------|-----------|-------|\n")
        for h in cohort_snap["holdings"]:
            flags_str = ", ".join(h["flags"]) if h["flags"] else "—"
            lines.append(
                f"| {h['name']} | Rs {h['curr_price']:,.1f} | {h['shares']} | "
                f"Rs {h['invested']:,.0f} | Rs {h['curr_value']:,.0f} | "
                f"Rs {h['pnl']:+,.0f} | {h['pnl_pct']:+.1f}% | {h['dist_to_stop_pct']:+.1f}pp | {flags_str} |\n"
            )
        lines.append("\n")

    with open(TRACKER_MD_PATH, "w") as f:
        f.writelines(lines)

if __name__ == "__main__":
    mark_to_market()
