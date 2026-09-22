#!/usr/bin/env python3
"""
paper-trading/tactical6m/track.py -- daily mark-to-market AND auto-rebalance for the
6-MONTH TACTICAL tracker.

Same pattern as ../live-recommendation/track.py (a single, continuously-rebalanced
Rs 1,00,000 paper portfolio, not a frozen weekly cohort), but sourced from
valuepickr-open-screen/data/confluence100_tactical6m.json -- Confluence-100's SECOND
ranking over its Top-100 pool: purely technical/momentum (technical_score + momentum_score,
50/50, no master_score term at all), on the theory that every name in the Top-100 already
cleared the fundamentals bar and can be treated as equal on that dimension. Max-return-in-
6-months framing, not a 10x/100x thesis screen. Rebuilt weekly by vpscreen-rerank Step 7.1,
so this tracker rebalances at live prices whenever that list's holdings or weights change.

If the tactical6m pool was too small to build this cycle (<5 above-EMA names), the source
JSON has no holdings and parse_tactical6m_weights() returns an empty weight set -- this
tracker then simply holds all cash until the pool recovers, same as any other empty-target
cycle; not an error.

Run any weekday, alongside ../scripts/refresh.py (which invokes this as a subprocess
and folds its latest snapshot into dashboard_data.json). No third-party deps.
"""
import json, os, sys, math, datetime, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
PT_DIR = os.path.dirname(HERE)
_spec = importlib.util.spec_from_file_location("refresh", os.path.join(PT_DIR, "scripts/refresh.py"))
rf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rf)

CAPITAL = rf.CAP
REBALANCE_THRESHOLD_PP = 0.5  # a weight move smaller than this (pp) isn't worth a rebalance
PF_PATH = os.path.join(HERE, "portfolio.json")
HIST_PATH = os.path.join(HERE, "history.json")
TRACKER_PATH = os.path.join(HERE, "TRACKER.md")


def load_portfolio():
    return json.load(open(PF_PATH)) if os.path.exists(PF_PATH) else None


def save_portfolio(pf):
    with open(PF_PATH, "w") as f:
        json.dump(pf, f, indent=2)
        f.write("\n")


def price_lookup(names):
    """name -> (symbol, price, date) via config.json's symbol map."""
    out = {}
    for n in names:
        meta = rf.CFG["names"].get(n)
        sym = meta["symbol"] if meta else n
        price, d = rf.latest_close(sym)
        out[n] = (sym, price, d)
    return out


def build_holdings(target_weights, nav, prices):
    """floor()-share sizing at the given NAV -- same convention as the frozen cohorts.
    A name whose price couldn't be fetched is skipped (its weight becomes extra cash);
    logged by the caller. An empty target_weights simply yields all cash."""
    holdings, invested = [], 0.0
    for name, wt in sorted(target_weights.items(), key=lambda kv: -kv[1]):
        sym, price, d = prices[name]
        if price is None:
            continue
        shares = math.floor(wt / 100.0 * nav / price)
        inv = shares * price
        invested += inv
        holdings.append({"name": name, "symbol": sym, "weight_pct": wt,
                          "entry_price": round(price, 2), "shares": shares, "invested": round(inv, 2)})
    cash = round(nav - invested, 2)
    return holdings, cash


def main():
    today = datetime.date.today()
    target_weights, revision = rf.parse_tactical6m_weights()
    all_names = set(target_weights)
    pf = load_portfolio()
    bootstrapped = False

    if pf is None:
        prices = price_lookup(all_names)
        missing = [n for n, (s, pr, d) in prices.items() if pr is None]
        if missing:
            print(f"  !! fetch failed for {', '.join(missing)} -- excluded from inception sizing", file=sys.stderr)
        holdings, cash = build_holdings(target_weights, CAPITAL, prices)
        pf = {
            "_readme": "6-MONTH TACTICAL tracker. SEPARATE from paper-trading/cohorts.json (frozen weekly "
                       "cohorts), swing-6m/cohorts.json (hand-curated, fundamentally-informed swing cohorts), "
                       "and live-recommendation/ (the fundamentals-led Rs 1L allocation). This single book "
                       "always mirrors the CURRENT allocation in "
                       "valuepickr-open-screen/data/confluence100_tactical6m.json -- Confluence-100's purely "
                       "technical/momentum ranking (no master_score term), auto-rebalancing at live prices "
                       "whenever that list's holdings or weights change by more than a rounding amount. "
                       "Script-owned -- do not hand-edit holdings/cash; it picks up the next weekly "
                       "Confluence-100 rebuild automatically. An empty holdings list (insufficient pool) "
                       "means all-cash, not an error.",
            "inception_date": today.isoformat(), "inception_capital": CAPITAL,
            "version": 1, "effective_date": today.isoformat(), "source_revision": revision,
            "holdings": holdings, "cash": cash,
            "rebalance_log": [{"date": today.isoformat(), "version": 1, "reason": "inception",
                                "nav": CAPITAL, "target_weights": target_weights}],
        }
        save_portfolio(pf)
        bootstrapped = True
        rebalanced = False
    else:
        held_names = {h["name"] for h in pf["holdings"]}
        cur_weights = {h["name"]: h["weight_pct"] for h in pf["holdings"]}
        prices = price_lookup(held_names | all_names)
        changed = (held_names != all_names) or any(
            abs(cur_weights.get(n, 0) - target_weights.get(n, 0)) > REBALANCE_THRESHOLD_PP
            for n in (held_names | all_names)
        )
        rebalanced = changed
        if changed:
            nav = pf["cash"] + sum(
                h["shares"] * (prices[h["name"]][1] if prices[h["name"]][1] is not None else h["entry_price"])
                for h in pf["holdings"]
            )
            holdings, cash = build_holdings(target_weights, nav, prices)
            added = sorted(all_names - held_names)
            dropped = sorted(held_names - all_names)
            reweighted = sorted(n for n in (held_names & all_names)
                                 if abs(cur_weights.get(n, 0) - target_weights.get(n, 0)) > REBALANCE_THRESHOLD_PP)
            bits = []
            if added: bits.append(f"added {', '.join(added)}")
            if dropped: bits.append(f"dropped {', '.join(dropped)}")
            if reweighted: bits.append(f"reweighted {', '.join(reweighted)}")
            reason = "; ".join(bits) or "weights changed"
            pf["version"] += 1
            pf["effective_date"] = today.isoformat()
            pf["source_revision"] = revision
            pf["holdings"] = holdings
            pf["cash"] = cash
            pf.setdefault("rebalance_log", []).append({
                "date": today.isoformat(), "version": pf["version"], "reason": reason, "nav": round(nav, 2),
            })
            save_portfolio(pf)

    # ---- mark to market (post-rebalance-or-not holdings) ----
    prices = price_lookup([h["name"] for h in pf["holdings"]])
    rows, total_val, fetch_fail = [], 0.0, []
    for h in pf["holdings"]:
        sym, price, d = prices[h["name"]]
        if price is None:
            fetch_fail.append(sym)
            price, d, stale = h["entry_price"], None, True
        else:
            stale = d < today
        val = h["shares"] * price
        total_val += val
        rows.append({
            "name": h["name"], "symbol": sym, "weight_pct": h["weight_pct"],
            "entry_price": h["entry_price"], "shares": h["shares"], "invested": h["invested"],
            "price": round(price, 2), "as_of": d.isoformat() if d else None, "stale": stale,
            "value": round(val, 2), "return_pct": round((price / h["entry_price"] - 1) * 100, 2),
        })

    nav = round(total_val + pf["cash"], 2)
    total_return_pct = round((nav / pf["inception_capital"] - 1) * 100, 2)

    hist = json.load(open(HIST_PATH)) if os.path.exists(HIST_PATH) else {
        "_readme": "Append-only daily NAV snapshots for the 6-month tactical tracker. One per date, "
                   "latest write wins. Script-owned (track.py).",
        "snapshots": [],
    }
    prev = [s for s in hist["snapshots"] if s["date"] < today.isoformat()]
    prev_snap = prev[-1] if prev else None
    day_change_pct = round((nav / prev_snap["nav"] - 1) * 100, 2) if prev_snap else None

    snap = {
        "date": today.isoformat(), "version": pf["version"], "rebalanced_today": rebalanced,
        "nav": nav, "return_pct": total_return_pct, "day_change_pct": day_change_pct,
        "invested_value": round(total_val, 2), "cash": pf["cash"], "holdings": rows,
    }
    hist["snapshots"] = [s for s in hist["snapshots"] if s["date"] != today.isoformat()] + [snap]
    hist["snapshots"].sort(key=lambda s: s["date"])
    with open(HIST_PATH, "w") as f:
        json.dump(hist, f, indent=2)
        f.write("\n")

    write_tracker(pf, snap, hist)

    print(f"tactical6m track -- {today} ({datetime.datetime.now():%Y-%m-%d %H:%M})  [v{pf['version']}]")
    print("-" * 64)
    for r in sorted(rows, key=lambda z: z["return_pct"]):
        print(f"  {r['name']:<26} {r['return_pct']:+6.2f}%  wt {r['weight_pct']:>4}%")
    print("-" * 64)
    d = "" if day_change_pct is None else f"{day_change_pct:+.2f}%"
    print(f"  NAV  Rs {nav:,.2f}   total {total_return_pct:+.2f}%   1d {d}")
    if bootstrapped:
        print(f"  ** BOOTSTRAPPED at v1: inception, {pf['source_revision']}")
    elif rebalanced:
        print(f"  ** REBALANCED to v{pf['version']}: {pf['rebalance_log'][-1]['reason']}")
    if fetch_fail:
        print(f"  !! fetch failed (carried entry price): {', '.join(fetch_fail)}")


def write_tracker(pf, snap, hist):
    L = []
    a = L.append
    a("# 6-Month Tactical Tracker -- Returns\n")
    a(f"_Regenerated by `paper-trading/tactical6m/track.py` on {snap['date']}. Do not hand-edit._\n")
    a(f"- Single, continuously-rebalanced Rs {pf['inception_capital']:,.0f} book, inception {pf['inception_date']}, "
      f"currently at version v{pf['version']} ({pf['effective_date']}).")
    a(f"- Always mirrors `valuepickr-open-screen/data/confluence100_tactical6m.json` -- Confluence-100's "
      f"purely technical/momentum ranking over its Top-100 pool (no master_score term; every name treated "
      f"as equal on fundamentals). Rebalances at live prices whenever a holding is added/dropped or a "
      f"weight moves more than {REBALANCE_THRESHOLD_PP}pp. Source: {pf.get('source_revision', '?')}.")
    a("- SEPARATE from `paper-trading/cohorts.json` (frozen weekly cohorts), "
      "`paper-trading/swing-6m/cohorts.json` (hand-curated swing cohorts), and "
      "`paper-trading/live-recommendation/` (the fundamentals-led Rs 1L allocation).\n")
    a(f"## Mark-to-market -- {snap['date']}\n")
    d = "" if snap["day_change_pct"] is None else f"{snap['day_change_pct']:+.2f}%"
    a("| NAV | Total return | 1-day |")
    a("|---|---|---|")
    a(f"| **Rs {snap['nav']:,.2f}** | **{snap['return_pct']:+.2f}%** | {d} |")
    a("\n## Holdings\n")
    a("| Name | Wt% | Entry (this version) | Price | Return | Value | As of |")
    a("|---|---|---|---|---|---|---|")
    for r in sorted(snap["holdings"], key=lambda z: -z["return_pct"]):
        st = " *" if r["stale"] else ""
        a(f"| {r['name']}{st} | {r['weight_pct']} | {r['entry_price']:.2f} | {r['price']:.2f} | "
          f"{r['return_pct']:+.2f}% | {r['value']:,.0f} | {r['as_of']} |")
    a(f"| **Total** | | | | **{snap['return_pct']:+.2f}%** | **{snap['invested_value']:,.0f}** + {snap['cash']:,.0f} cash | |")
    a("\n## Rebalance log\n")
    a("| Date | Version | NAV at rebalance | Reason |")
    a("|---|---|---|---|")
    for e in reversed(pf.get("rebalance_log", [])):
        a(f"| {e['date']} | v{e['version']} | Rs {e['nav']:,.2f} | {e['reason']} |")
    a("\n## Value history\n")
    a("| Date | NAV | Total return | 1-day | Rebalanced |")
    a("|---|---|---|---|---|")
    for s in hist["snapshots"][-60:]:
        dd = "" if s.get("day_change_pct") is None else f"{s['day_change_pct']:+.2f}%"
        a(f"| {s['date']} | {s['nav']:,.0f} | {s['return_pct']:+.2f}% | {dd} | {'yes' if s.get('rebalanced_today') else ''} |")
    with open(TRACKER_PATH, "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
