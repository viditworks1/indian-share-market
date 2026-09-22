#!/usr/bin/env python3
"""
paper-trading/scripts/refresh.py  --  the daily engine for the front-test journal.

Run any weekday. It:
  1. marks every cohort in cohorts.json to market (latest available close per holding),
  2. appends / refreshes today's snapshot in daily_history.json (one per date, latest write wins),
  3. scores the concentrated-cohort candidate universe on a 2-factor composite
     (valuepickr-open-screen's master_score + a weekly/monthly technical blend),
  4. writes dashboard_data.json, dashboard.html and RETURNS_TRACKER.md.

It does NOT create new cohorts -- that stays a Monday-only step done from the SKILL,
using the composite ranking this script prints and stores.

No third-party deps (urllib + json + math + datetime only).
"""

import json, math, sys, time, urllib.request, datetime, os, re, subprocess, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO_ROOT = os.path.dirname(ROOT)  # one level above projects/ -- where portfolio/ lives
PT   = os.path.join(ROOT, "paper-trading")
SWING_DIR = os.path.join(PT, "swing-6m")
LIVE_DIR = os.path.join(PT, "live-recommendation")
# 2026-09-22: the standard cohort's and the live-recommendation tracker's weight source
# moved from portfolio/FINAL_PORTFOLIO_RECOMMENDATION.md (written by the now-legacy,
# pending-retirement portfolio-rs1l-revision job) to Confluence-100's own allocation,
# built weekly by vpscreen-rerank Step 7.2 directly from top10_investable. See
# parse_recommendation_weights() below.
CONFLUENCE100_ALLOCATION = os.path.join(ROOT, "valuepickr-open-screen", "data", "confluence100_allocation.json")

def p(*a):  # projects/-relative path
    return os.path.join(ROOT, *a)

def load(path):
    with open(path) as f:
        return json.load(f)

CFG = load(os.path.join(PT, "config.json"))
CAP = CFG["capital"]
TODAY = datetime.date.today()

# --------------------------------------------------------------------------- #
# Yahoo Finance fetch                                                          #
# --------------------------------------------------------------------------- #
_CACHE = {}

def _yahoo(symbol, rng, interval):
    key = (symbol, rng, interval)
    if key in _CACHE:
        return _CACHE[key]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={rng}&interval={interval}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    last_err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
            res = d["chart"]["result"][0]
            ts = res.get("timestamp") or []
            cl = res["indicators"]["quote"][0].get("close") or []
            rows = [(datetime.datetime.fromtimestamp(t, datetime.timezone.utc).date(), c)
                    for t, c in zip(ts, cl) if c is not None]
            _CACHE[key] = rows
            return rows
        except Exception as e:  # noqa
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    print(f"  !! fetch failed for {symbol} ({rng}/{interval}): {last_err}", file=sys.stderr)
    _CACHE[key] = []
    return []

def daily_series(symbol):
    return _yahoo(symbol, "3mo", "1d")

def latest_close(symbol):
    """(price, date) of the most recent available daily close, or (None, None)."""
    rows = daily_series(symbol)
    return (rows[-1][1], rows[-1][0]) if rows else (None, None)

def close_on_or_before(symbol, d):
    rows = daily_series(symbol)
    prior = [r for r in rows if r[0] <= d]
    return prior[-1] if prior else (rows[0] if rows else (None, None))

def weekly_closes(symbol):
    return _yahoo(symbol, "5y", "1wk")

def monthly_closes(symbol):
    return _yahoo(symbol, "15y", "1mo")

# --------------------------------------------------------------------------- #
# Technical: 30-week EMA (hard gate) + 10-month EMA (soft regime overlay)     #
# --------------------------------------------------------------------------- #
def ema(vals, span):
    k = 2 / (span + 1)
    e = vals[0]
    out = [e]
    for v in vals[1:]:
        e = v * k + e * (1 - k)
        out.append(e)
    return out

def _drop_in_progress_period(rows, period):
    """period: 'week' or 'month'. Drops the last row if it falls in the still-open
    current calendar period, so the EMA is only ever computed on completed bars."""
    if period == "week":
        cur = TODAY.isocalendar()[:2]
        keyfn = lambda d: d.isocalendar()[:2]
    else:
        cur = (TODAY.year, TODAY.month)
        keyfn = lambda d: (d.year, d.month)
    closed = [r for r in rows if keyfn(r[0]) != cur]
    return closed if closed else rows[:-1]

def weekly_technical(symbol):
    """Last completed weekly close vs the 30-week EMA. HARD GATE: ext_pct <= 0
    (close at/below the EMA) disqualifies the name from the concentrated pool
    entirely -- unchanged from the original single-timeframe design; this is the
    discipline the user had prior success with, so it keeps its primacy."""
    tcfg = CFG["technical"]
    span = CFG["ema_weeks"]
    rows = weekly_closes(symbol)
    if len(rows) < span + 5:
        return {"ext_pct": None, "fresh_cross": False, "score": None, "ema": None, "close": None, "note": "insufficient weekly history"}
    closed = _drop_in_progress_period(rows, "week")
    if len(closed) < span + 5:
        closed = rows[:-1]
    dates = [r[0] for r in closed]
    vals = [r[1] for r in closed]
    e = ema(vals, span)
    last_close, last_ema = vals[-1], e[-1]
    ext = (last_close - last_ema) / last_ema * 100.0
    look = tcfg["fresh_cross_lookback_weeks"]
    fresh = False
    for i in range(max(1, len(vals) - look), len(vals)):
        if vals[i - 1] <= e[i - 1] and vals[i] > e[i]:
            fresh = True
            break
    if ext <= 0:
        score = None  # disqualified from the candidate pool
    else:
        base = 100 - max(0.0, ext - tcfg["ext_cushion_knee_pct"]) * tcfg["ext_decay_per_pct"]
        base = max(tcfg["base_floor"], min(100.0, base))
        if fresh:
            base += tcfg["fresh_cross_bonus"]
        if ext > tcfg["overextended_pct"]:
            base -= tcfg["overextended_penalty"]
        score = max(0.0, min(100.0, base))
    return {"ext_pct": round(ext, 1), "fresh_cross": fresh, "score": None if score is None else round(score, 1),
            "ema": round(last_ema, 2), "close": round(last_close, 2), "as_of": dates[-1].isoformat(), "note": ""}

def monthly_technical(symbol):
    """Last completed monthly close vs the 10-month EMA -- a slower regime filter
    (Faber/GTAA-style), not a trade trigger. NEVER disqualifies from the pool
    (unlike weekly): a name below its monthly EMA just scores near base_floor,
    since a weekly pullback inside a longer monthly uptrend is normal and the
    weekly gate above already handles the hard exit discipline."""
    tcfg = CFG["technical_monthly"]
    span = CFG["ema_months"]
    rows = monthly_closes(symbol)
    if len(rows) < span + 5:
        return {"ext_pct": None, "fresh_cross": False, "score": tcfg["base_floor"], "ema": None, "close": None, "note": "insufficient monthly history"}
    closed = _drop_in_progress_period(rows, "month")
    if len(closed) < span + 5:
        closed = rows[:-1]
    dates = [r[0] for r in closed]
    vals = [r[1] for r in closed]
    e = ema(vals, span)
    last_close, last_ema = vals[-1], e[-1]
    ext = (last_close - last_ema) / last_ema * 100.0
    look = tcfg["fresh_cross_lookback_months"]
    fresh = False
    for i in range(max(1, len(vals) - look), len(vals)):
        if vals[i - 1] <= e[i - 1] and vals[i] > e[i]:
            fresh = True
            break
    if ext <= 0:
        score = tcfg["base_floor"]  # below the monthly regime line -- soft floor, not a gate
    else:
        base = 100 - max(0.0, ext - tcfg["ext_cushion_knee_pct"]) * tcfg["ext_decay_per_pct"]
        base = max(tcfg["base_floor"], min(100.0, base))
        if fresh:
            base += tcfg["fresh_cross_bonus"]
        if ext > tcfg["overextended_pct"]:
            base -= tcfg["overextended_penalty"]
        score = max(0.0, min(100.0, base))
    return {"ext_pct": round(ext, 1), "fresh_cross": fresh, "score": round(max(0.0, min(100.0, score)), 1),
            "ema": round(last_ema, 2), "close": round(last_close, 2), "as_of": dates[-1].isoformat(), "note": ""}

# --------------------------------------------------------------------------- #
# Fundamental screen-tier sub-score                                          #
# --------------------------------------------------------------------------- #
def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def build_tier_lookup():
    fs = CFG["fundamental_tier_scores"]
    out = {}  # normalised-name -> (score, label)
    try:
        vp = load(p(*CFG["data_files"]["vp_open_screen_ranking"].split("/")))
        for tier, sc in fs["vp_open_screen"].items():
            for x in vp.get(tier, []):
                out.setdefault(_norm(x.get("name")), []).append((sc, f"VP-open {tier}"))
    except Exception as e:  # noqa
        print(f"  !! vp screen tiers unavailable: {e}", file=sys.stderr)
    try:
        cu = load(p(*CFG["data_files"]["curated_108_ranking"].split("/")))
        for tier, sc in fs["curated_108_screen"].items():
            for x in cu.get(tier, []):
                out.setdefault(_norm(x.get("name")), []).append((sc, f"108-screen {tier}"))
    except Exception as e:  # noqa
        print(f"  !! 108 screen tiers unavailable: {e}", file=sys.stderr)
    return out

TIER_LOOKUP = build_tier_lookup()

def fundamental(name, slug, red_flag_tier):
    fs = CFG["fundamental_tier_scores"]
    keys = {_norm(name), _norm(slug), _norm(slug.replace("-ltd", "")), _norm(name + " ltd")}
    hits = []
    for k, lst in TIER_LOOKUP.items():
        if k in keys or any(k.startswith(x) or x.startswith(k) for x in keys if len(x) > 6):
            hits.extend(lst)
    if hits:
        score, why = max(hits, key=lambda t: t[0])
    else:
        score, why = fs["unlisted"], "not on either screen tier list"
    pen = CFG["red_flag_penalty"].get((red_flag_tier or "").upper(), 0)
    final = max(0.0, min(100.0, score - pen))
    return {"score": round(final, 1), "basis": why, "red_flag_tier": red_flag_tier, "red_flag_penalty": pen}

# --------------------------------------------------------------------------- #
# Conviction + expectation-gap                                               #
# --------------------------------------------------------------------------- #
CONV = {e["slug"]: e for e in load(p(*CFG["data_files"]["conviction"].split("/")))}
_GAP_RAW = load(p(*CFG["data_files"]["expectation_gap"].split("/")))
GAP_RANKED  = {e["slug"]: e.get("expectation_gap_score") for e in _GAP_RAW.get("ranked", [])}
GAP_NOEDGE  = {e["slug"] for e in _GAP_RAW.get("no_edge", [])}
GAP_NA      = {e["slug"] for e in _GAP_RAW.get("not_assessed", [])}
try:
    _MASTER_RAW = load(p(*CFG["data_files"]["master"].split("/")))
    MASTER = {e["slug"]: e for e in _MASTER_RAW.get("ranked", [])}
except Exception as e:  # noqa
    print(f"  !! master-scores.json unavailable: {e}", file=sys.stderr)
    MASTER = {}

LABEL_MAP = {"high": 100, "medium-high": 80, "medium": 60, "low-medium": 40, "low": 20}

def conviction(slug):
    e = CONV.get(slug)
    if e and isinstance(e.get("conviction_score"), (int, float)):
        return round(float(e["conviction_score"]), 1), "numeric", e.get("red_flag_tier")
    lab = (e or {}).get("conviction", "")
    return float(LABEL_MAP.get(lab.lower(), 50)), f"label:{lab or 'unknown'}", (e or {}).get("red_flag_tier")

def gap(slug):
    if slug in GAP_RANKED and GAP_RANKED[slug] is not None:
        return round(float(GAP_RANKED[slug]), 1), "ranked"
    if slug in GAP_NOEDGE:
        return 0.0, "no-edge flag"
    if slug in GAP_NA:
        return float(CFG["gap_not_assessed_score"]), "not_assessed (neutral)"
    return float(CFG["gap_not_assessed_score"]), "absent (neutral)"

def master_score(slug):
    """master_score (valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md) -- already
    a renormalized blend of conviction/quality/gap/consistency/asymmetry. Falls back to
    a neutral score, same convention as gap()'s not-assessed handling, for a name the
    registry hasn't scored yet (shouldn't happen for anything with a conviction_score,
    which is everything in composite_universe, but guarded anyway)."""
    e = MASTER.get(slug)
    if e and isinstance(e.get("master_score"), (int, float)):
        return round(float(e["master_score"]), 1), "ranked"
    return float(CFG["master_not_assessed_score"]), "not_assessed (neutral)"

# --------------------------------------------------------------------------- #
# Composite scoring for the candidate universe                               #
# --------------------------------------------------------------------------- #
def score_universe():
    w = CFG["composite_weights"]
    tw = CFG["technical_weights"]
    rows = []
    for name in CFG["composite_universe"]:
        meta = CFG["names"][name]
        slug, sym = meta["slug"], meta["symbol"]
        conv, conv_basis, rft = conviction(slug)
        g, g_basis = gap(slug)
        m, m_basis = master_score(slug)
        wk = weekly_technical(sym)
        mo = monthly_technical(sym)
        fund = fundamental(name, slug, rft)
        excluded = name in CFG["hard_excluded"]
        # the weekly EMA break remains the ONLY technical pool gate -- monthly is a
        # regime overlay on the score, never a disqualifier (see monthly_technical docstring)
        in_pool = (wk["score"] is not None) and not excluded
        wk_for_blend = wk["score"] if wk["score"] is not None else 0.0
        mo_for_blend = mo["score"] if mo["score"] is not None else 0.0
        tech_blend = tw["weekly"] * wk_for_blend + tw["monthly"] * mo_for_blend
        composite = w["master"] * m + w["technical"] * tech_blend
        rows.append({
            "name": name, "symbol": sym, "slug": slug,
            "master": m, "master_basis": m_basis,
            "conviction": conv, "conviction_basis": conv_basis,
            "gap": g, "gap_basis": g_basis,
            "fundamental": fund["score"], "fundamental_basis": fund["basis"],
            "red_flag_tier": rft, "red_flag_penalty": fund["red_flag_penalty"],
            "technical": round(tech_blend, 1),
            "weekly_technical": wk["score"], "ext_pct": wk["ext_pct"], "fresh_cross": wk["fresh_cross"],
            "ema": wk["ema"], "weekly_close": wk["close"], "tech_as_of": wk.get("as_of"),
            "monthly_technical": mo["score"], "ext_pct_monthly": mo["ext_pct"], "fresh_cross_monthly": mo["fresh_cross"],
            "ema_monthly": mo["ema"], "monthly_close": mo["close"], "tech_as_of_monthly": mo.get("as_of"),
            "composite": round(composite, 2),
            "in_pool": in_pool, "excluded": excluded,
            "contrib": {
                "master": round(w["master"] * m, 2),
                "technical": round(w["technical"] * tech_blend, 2),
            },
        })
    # ranks
    pool = [r for r in rows if r["in_pool"]]
    for i, r in enumerate(sorted(pool, key=lambda r: -r["composite"]), 1):
        r["composite_rank"] = i
    for i, r in enumerate(sorted(pool, key=lambda r: -r["conviction"]), 1):
        r["conviction_rank"] = i
    for r in rows:
        r.setdefault("composite_rank", None)
        r.setdefault("conviction_rank", None)
        if r["composite_rank"] and r["conviction_rank"]:
            r["rank_delta"] = r["conviction_rank"] - r["composite_rank"]  # +ve = composite likes it more
        else:
            r["rank_delta"] = None
    slots = CFG["concentrated_rank_weights_by_slot"]
    picks = sorted(pool, key=lambda r: -r["composite"])[:len(slots)]
    concentrated_next = [{"name": r["name"], "symbol": r["symbol"], "weight_pct": slots[i],
                          "composite": r["composite"], "master": r["master"], "conviction": r["conviction"],
                          "gap": r["gap"], "fundamental": r["fundamental"], "technical": r["technical"],
                          "weekly_technical": r["weekly_technical"], "monthly_technical": r["monthly_technical"]}
                         for i, r in enumerate(picks)]
    return rows, concentrated_next

# --------------------------------------------------------------------------- #
# Mark cohorts to market                                                     #
# --------------------------------------------------------------------------- #
def days_live(entry_date_iso):
    return (TODAY - datetime.date.fromisoformat(entry_date_iso)).days

def mark_cohorts(cohorts, prev_snap_by_key):
    out = []
    for c in cohorts:
        key = (c["week_id"], c["series"])
        hs = []
        cur_total = 0.0
        for h in c["holdings"]:
            price, asof = latest_close(h["symbol"])
            if price is None:
                price, asof = h["entry_price"], c["entry_price_date"]
                stale = True
            else:
                stale = asof < TODAY
            val = price * h["shares"]
            cur_total += val
            prev = None
            ps = prev_snap_by_key.get(key)
            if ps:
                pm = next((x for x in ps["holdings"] if x["name"] == h["name"]), None)
                if pm:
                    prev = pm["price"]
            hs.append({
                "name": h["name"], "symbol": h["symbol"],
                "weight_pct": h.get("weight_pct"),
                "conviction_score": h.get("conviction_score"),
                "entry_price": h["entry_price"], "shares": h["shares"], "invested": round(h["shares"] * h["entry_price"], 2),
                "price": round(price, 2), "as_of": asof.isoformat() if hasattr(asof, "isoformat") else str(asof),
                "stale": stale,
                "value": round(val, 2),
                "return_pct": round((price / h["entry_price"] - 1) * 100, 2),
                "day_change_pct": round((price / prev - 1) * 100, 2) if prev else None,
                "contribution_pct": round((val - h["shares"] * h["entry_price"]) / CAP * 100, 2),
            })
        cash = c["cash"]
        total = cur_total + cash
        ps = prev_snap_by_key.get(key)
        if ps:
            prev_total = ps["current_value"]
            day_val = round(total - prev_total, 2)
            day_pct = round((total / prev_total - 1) * 100, 2)
        else:
            day_val = day_pct = None  # first snapshot for this cohort -> no prior day to diff
        out.append({
            "week_id": c["week_id"], "series": c["series"],
            "decided_date": c["decided_date"], "entry_price_date": c["entry_price_date"],
            "days_live": days_live(c["entry_price_date"]),
            "invested": round(sum(h["shares"] * h["entry_price"] for h in c["holdings"]), 2),
            "cash": cash,
            "current_value": round(total, 2),
            "return_pct": round((total / CAP - 1) * 100, 2),
            "day_change_value": day_val,
            "day_change_pct": day_pct,
            "prev_snapshot_date": ps["date"] if ps else None,
            "holdings": hs,
        })
    return out

# --------------------------------------------------------------------------- #
# 6-month swing book (separate, actively-managed) -- run its tracker, fold in  #
# --------------------------------------------------------------------------- #
def run_swing_tracker():
    """Invoke paper-trading/swing-6m/track.py (its own multi-cohort MTM engine) so the
    dashboard folds in fresh data, then load each cohort's latest snapshot into a list of
    dashboard-ready dicts. Returns [] if the swing book isn't set up. Since 2026-09-11 this
    is a WEEKLY, append-only cohort series (swing-6m/cohorts.json) -- never merged into
    paper-trading/cohorts.json (fundamentals-driven) or live-recommendation/ (continuously
    rebalanced)."""
    track = os.path.join(SWING_DIR, "track.py")
    hist_p = os.path.join(SWING_DIR, "history.json")
    cohorts_p = os.path.join(SWING_DIR, "cohorts.json")
    if os.path.exists(track):
        try:
            r = subprocess.run([sys.executable, track], capture_output=True, text=True, timeout=180)
            if r.stdout:
                print(r.stdout, end="" if r.stdout.endswith("\n") else "\n")
            if r.returncode != 0:
                print(f"  !! swing track.py exited {r.returncode}: {r.stderr.strip()[:300]}", file=sys.stderr)
        except Exception as e:  # noqa
            print(f"  !! could not run swing track.py: {e}", file=sys.stderr)
    if not os.path.exists(hist_p):
        return []
    try:
        snaps = load(hist_p).get("snapshots", [])
    except Exception:
        return []
    if not snaps:
        return []
    rules_by_week = {}
    if os.path.exists(cohorts_p):
        try:
            for c in load(cohorts_p).get("cohorts", []):
                r = c.get("rules") or {}
                rules_by_week[c["week_id"]] = {"hard_stop_pct": r.get("hard_stop_pct"),
                                                "review_dates": r.get("review_cadence_monthly", [])}
        except Exception:
            pass
    by_week = {}
    for s in snaps:
        by_week.setdefault(s["week_id"], []).append(s)
    out = []
    for wk, arr in by_week.items():
        arr.sort(key=lambda x: x["date"])
        last = arr[-1]
        vh = [{"date": x["date"], "indexed": round(x["port_value"] / CAP * 100, 3),
               "value": x["port_value"], "return_pct": x["port_return_pct"],
               "benchmark_return_pct": (x.get("benchmark") or {}).get("return_pct")} for x in arr]
        start_date = last.get("entry_price_date")
        if start_date and (not vh or vh[0]["date"] != start_date):
            vh.insert(0, {"date": start_date, "indexed": 100.0, "value": CAP, "return_pct": 0.0, "benchmark_return_pct": 0.0})
        out.append({
            "week_id": wk, "decided_date": last.get("decided_date"),
            "start_date": start_date, "horizon_end_date": last.get("horizon_end_date"),
            "days_to_horizon": last.get("days_to_horizon"),
            "as_of": last["date"], "port_value": last["port_value"], "port_return_pct": last["port_return_pct"],
            "day_change_pct": last.get("day_change_pct"), "invested_value": last.get("invested_value"),
            "cash": last.get("cash"), "benchmark": last.get("benchmark"), "alpha_pct": last.get("alpha_pct"),
            "flags": last.get("flags", []), "holdings": last.get("holdings", []), "value_history": vh,
            "market_regime": last.get("market_regime"),
            "rules": rules_by_week.get(wk, {}),
        })
    out.sort(key=lambda c: c["decided_date"])
    return out


# --------------------------------------------------------------------------- #
# Live recommendation tracker (separate, continuously-rebalanced book) --      #
# reads valuepickr-open-screen/data/confluence100_allocation.json directly,   #
# runs its own tracker, folds into dashboard_data.json.                       #
# --------------------------------------------------------------------------- #
def parse_recommendation_weights(alloc_path=None):
    """Extract {name: weight_pct} from Confluence-100's Rs 1L allocation (2026-09-22,
    replaces the old portfolio/FINAL_PORTFOLIO_RECOMMENDATION.md Section 3 markdown
    parse -- that doc's source job, portfolio-rs1l-revision, is pending retirement and
    nothing here reads it anymore). Also returns a short revision label for logging,
    and merges each holding's resolved symbol into CFG["names"] in-memory so
    price_lookup() (in live-recommendation/track.py) finds it without a config.json
    edit -- Confluence-100 has already verified the ticker, no need to duplicate it."""
    alloc_path = alloc_path or CONFLUENCE100_ALLOCATION
    alloc = load(alloc_path)
    weights = {}
    for h in alloc.get("holdings", []):
        name, wt = h["name"], h["weight_pct"]
        if wt <= 0:
            continue
        weights[name] = wt
        if h.get("symbol") and name not in CFG["names"]:
            CFG["names"][name] = {"symbol": h["symbol"], "slug": h.get("slug")}
    revision = f"Confluence-100 allocation ({alloc.get('as_of_date', '?')}, cash {alloc.get('cash_pct', '?')}%)"
    return weights, revision


def run_live_recommendation_tracker():
    """Invoke paper-trading/live-recommendation/track.py (its own MTM + auto-rebalance
    engine) so the dashboard folds in fresh data, then load its latest snapshot into a
    dashboard-ready dict. Returns None if that book isn't set up yet."""
    track = os.path.join(LIVE_DIR, "track.py")
    hist_p = os.path.join(LIVE_DIR, "history.json")
    if os.path.exists(track):
        try:
            r = subprocess.run([sys.executable, track], capture_output=True, text=True, timeout=180)
            if r.stdout:
                print(r.stdout, end="" if r.stdout.endswith("\n") else "\n")
            if r.returncode != 0:
                print(f"  !! live-recommendation track.py exited {r.returncode}: {r.stderr.strip()[:300]}", file=sys.stderr)
        except Exception as e:  # noqa
            print(f"  !! could not run live-recommendation track.py: {e}", file=sys.stderr)
    if not os.path.exists(hist_p):
        return None
    try:
        snaps = load(hist_p).get("snapshots", [])
    except Exception:
        return None
    if not snaps:
        return None
    last = snaps[-1]
    pf_p = os.path.join(LIVE_DIR, "portfolio.json")
    meta = load(pf_p) if os.path.exists(pf_p) else {}
    vh = [{"date": s["date"], "indexed": round(s["nav"] / CAP * 100, 3),
           "value": s["nav"], "return_pct": s["return_pct"]} for s in snaps]
    inception = meta.get("inception_date")
    if inception and (not vh or vh[0]["date"] != inception):
        vh.insert(0, {"date": inception, "indexed": 100.0, "value": CAP, "return_pct": 0.0})
    return {
        "inception_date": inception, "version": meta.get("version"),
        "source_revision": meta.get("source_revision"),
        "as_of": last["date"], "nav": last["nav"], "return_pct": last["return_pct"],
        "day_change_pct": last.get("day_change_pct"), "invested_value": last.get("invested_value"),
        "cash": last.get("cash"), "holdings": last.get("holdings", []),
        "rebalance_log": meta.get("rebalance_log", []), "value_history": vh,
    }


# --------------------------------------------------------------------------- #
# Monday helper: closing prices as of a given date (for cohort creation)      #
# --------------------------------------------------------------------------- #
def cmd_prices_asof(date_iso, names_or_symbols):
    """Print the close on-or-before date_iso for each name/symbol. Used by the SKILL on Mondays."""
    want = datetime.date.fromisoformat(date_iso)
    name2sym = {k: v["symbol"] for k, v in CFG["names"].items()}
    print(f"# closes on-or-before {date_iso}")
    for tok in names_or_symbols:
        sym = name2sym.get(tok, tok)
        d, price = close_on_or_before(sym, want)
        print(f"{tok}\t{sym}\t{'' if price is None else round(price,2)}\t{d}")


# --------------------------------------------------------------------------- #
# main                                                                        #
# --------------------------------------------------------------------------- #
def main():
    cohorts_doc = load(os.path.join(PT, "cohorts.json"))
    cohorts = cohorts_doc["cohorts"]

    hist_path = os.path.join(PT, "daily_history.json")
    if os.path.exists(hist_path):
        hist = load(hist_path)
    else:
        hist = {"_readme": "Append-only daily mark-to-market snapshots, one per (date, week_id, series). "
                           "Written by paper-trading/scripts/refresh.py. Never hand-edit past snapshots.",
                "snapshots": []}

    # most-recent PRIOR snapshot per cohort (strictly before today)
    prev_by_key = {}
    for s in sorted(hist["snapshots"], key=lambda s: s["date"]):
        if s["date"] < TODAY.isoformat():
            prev_by_key[(s["week_id"], s["series"])] = s

    marked = mark_cohorts(cohorts, prev_by_key)

    # upsert today's snapshots
    hist["snapshots"] = [s for s in hist["snapshots"] if s["date"] != TODAY.isoformat()]
    for m in marked:
        hist["snapshots"].append({
            "date": TODAY.isoformat(), "week_id": m["week_id"], "series": m["series"],
            "days_live": m["days_live"], "current_value": m["current_value"], "return_pct": m["return_pct"],
            "day_change_value": m["day_change_value"], "day_change_pct": m["day_change_pct"],
            "cash": m["cash"],
            "holdings": [{"name": h["name"], "price": h["price"], "as_of": h["as_of"],
                         "value": h["value"], "return_pct": h["return_pct"], "stale": h["stale"]}
                        for h in m["holdings"]],
        })
    hist["snapshots"].sort(key=lambda s: (s["date"], s["series"], s["week_id"]))
    with open(hist_path, "w") as f:
        json.dump(hist, f, indent=2)
        f.write("\n")

    swing_cohorts = run_swing_tracker()
    live_recommendation = run_live_recommendation_tracker()

    universe, concentrated_next = score_universe()

    # per-cohort value time series (base 100) from history
    series_ts = {}
    for s in hist["snapshots"]:
        k = f'{s["week_id"]} / {s["series"]}'
        series_ts.setdefault(k, []).append({"date": s["date"], "indexed": round(s["current_value"] / CAP * 100, 3),
                                            "value": s["current_value"], "return_pct": s["return_pct"]})
    for k, arr in series_ts.items():
        arr.sort(key=lambda x: x["date"])
        c = next(c for c in marked if f'{c["week_id"]} / {c["series"]}' == k)
        arr.insert(0, {"date": c["entry_price_date"], "indexed": 100.0, "value": CAP, "return_pct": 0.0})

    by_series = {}
    for m in marked:
        by_series.setdefault(m["series"], []).append(m["return_pct"])
    series_summary = {s: {"count": len(v), "avg_return_pct": round(sum(v) / len(v), 2)} for s, v in by_series.items()}

    # age-matched comparison (only when both series have >=2 cohorts)
    age_note = None
    if all(len(by_series.get(s, [])) >= 2 for s in ("standard", "concentrated")):
        buckets = {}
        for m in marked:
            wk = math.floor(m["days_live"] / 7)
            buckets.setdefault(wk, {}).setdefault(m["series"], []).append(m["return_pct"])
        parts = []
        for wk in sorted(buckets):
            b = buckets[wk]
            if "standard" in b and "concentrated" in b:
                sa = sum(b["standard"]) / len(b["standard"])
                ca = sum(b["concentrated"]) / len(b["concentrated"])
                parts.append(f"~{wk}wk old: standard {sa:+.2f}% vs concentrated {ca:+.2f}%")
        age_note = "; ".join(parts) if parts else None

    data = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "as_of_date": TODAY.isoformat(),
        "capital": CAP,
        "composite_weights": CFG["composite_weights"],
        "technical_weights": CFG["technical_weights"],
        "gap_not_assessed_score": CFG["gap_not_assessed_score"],
        "concentrated_slots": CFG["concentrated_rank_weights_by_slot"],
        "cohorts": marked,
        "series_summary": series_summary,
        "age_matched_note": age_note,
        "value_timeseries": series_ts,
        "universe": universe,
        "concentrated_next": concentrated_next,
        "history_points": len(set(s["date"] for s in hist["snapshots"])),
        "swing_cohorts": swing_cohorts,
        "live_recommendation": live_recommendation,
    }
    with open(os.path.join(PT, "dashboard_data.json"), "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    write_dashboard(data)
    write_tracker(data, cohorts_doc)
    print_summary(data)


# --------------------------------------------------------------------------- #
# RETURNS_TRACKER.md (mechanical regen)                                       #
# --------------------------------------------------------------------------- #
def _pct(x, plus=True):
    if x is None:
        return "—"
    return f"{x:+.2f}%" if plus else f"{x:.2f}%"

def write_tracker(data, cohorts_doc):
    L = []
    a = L.append
    a("# Paper-Trading Front-Test Tracker\n")
    a("This is a **forward-testing** journal, not a backtest. Every Monday a brand-new, independent "
      "Rs 1,00,000 paper portfolio is decided (from the then-current `docs/FINAL_PORTFOLIO_RECOMMENDATION.md`), "
      "priced at the **prior Friday's close**, and then left untouched forever. Every cohort is marked to "
      "market **every weekday** by `paper-trading/scripts/refresh.py`; this file and "
      "`paper-trading/dashboard.html` are regenerated on each run. Raw entry data: `cohorts.json` "
      "(append-only). Daily snapshots: `daily_history.json` (append-only). Two sibling books are "
      "tracked separately and folded into the same dashboard: the continuously-rebalanced "
      "`live-recommendation/` tracker (own `TRACKER.md`) and the weekly frozen `swing-6m/cohorts.json` "
      "series (own `TRACKER.md`) — see those files, not this one, for their detail.\n")
    a("**Two parallel series per week, same Rs 1,00,000, different sizing:**")
    a("- **standard** — mirrors the recommendation's current allocation as-is (~10 diversified positions).")
    a("- **concentrated** — top-5 of the candidate universe by a **2-factor composite** "
      "(`master_score` 75% + technical 25%, technical itself weekly EMA 60% / monthly EMA 40%), "
      "sized 25/20/20/17/13. `master_score` (valuepickr-open-screen, built from studying real "
      "high-return investors' documented methods) is itself a renormalized blend of "
      "conviction + quality + expectation-gap + consistency + asymmetry — see "
      "`valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md`. Before 2026-09-05 this was a "
      "4-factor composite (conviction 30% + gap 30% + fundamental screen-tier 25% + weekly "
      "technical 15%); before 2026-09-01 it ranked on conviction score alone. Conviction/gap/"
      "fundamental-tier are still shown per-name for context, just no longer weighted "
      "separately into the composite (they'd double-count against `master_score`).\n")
    a(f"**Last updated:** {data['as_of_date']} (generated {data['generated_at']}). "
      f"Daily history: {data['history_points']} day(s) recorded.\n")
    a("---\n")
    a("## Summary — all cohorts\n")
    a("| Cohort | Series | Decided | Entry Basis | Days Live | Current Value (Rs) | 1-Day | Return % |")
    a("|---|---|---|---|---:|---:|---:|---:|")
    for c in data["cohorts"]:
        a(f"| {c['week_id']} | {c['series']} | {c['decided_date']} | {c['entry_price_date']} | "
          f"{c['days_live']} | {c['current_value']:,.2f} | {_pct(c['day_change_pct'])} | **{_pct(c['return_pct'])}** |")
    a("")
    for s, v in sorted(data["series_summary"].items()):
        a(f"*{s.capitalize()} series: {v['count']} cohort(s), average return **{_pct(v['avg_return_pct'])}**.*")
    if data["age_matched_note"]:
        a(f"\n**Age-matched:** {data['age_matched_note']}.")
    else:
        a("\n*Age-matched standard-vs-concentrated comparison appears once both series have ≥2 cohort-weeks.*")
    a("\n---\n")
    a("## Concentrated candidate universe — composite ranking (for the next Monday cohort)\n")
    a("Scored fresh each run from live weekly + monthly technicals + the current `master_score` "
      "(all of which other scheduled tasks keep updating). Conv/Gap/Fund columns are informational "
      "context only — they feed `master_score` upstream, not this composite directly.\n")
    a("| # | Name | Composite | Master | Conv | Gap | Fund | Tech (wk/mo) | Ext vs 30W EMA | Ext vs 10M EMA | Conv-only rank | Δ |")
    a("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    pool = sorted([r for r in data["universe"] if r["in_pool"]], key=lambda r: r["composite_rank"])
    for r in pool:
        ext = "—" if r["ext_pct"] is None else f"{r['ext_pct']:+.1f}%"
        ext_mo = "—" if r["ext_pct_monthly"] is None else f"{r['ext_pct_monthly']:+.1f}%"
        wk_mo = f"{r['weekly_technical']:.0f}/{r['monthly_technical']:.0f}" if r["weekly_technical"] is not None else "—"
        dd = r["rank_delta"]
        darr = "—" if dd is None else (f"▲{dd}" if dd > 0 else (f"▼{-dd}" if dd < 0 else "0"))
        star = " ★" if r["composite_rank"] <= len(CFG["concentrated_rank_weights_by_slot"]) else ""
        a(f"| {r['composite_rank']}{star} | {r['name']} | **{r['composite']:.1f}** | {r['master']:.0f} | "
          f"{r['conviction']:.0f} | {r['gap']:.0f} | {r['fundamental']:.0f} | {wk_mo} | "
          f"{ext} | {ext_mo} | {r['conviction_rank']} | {darr} |")
    out = [r for r in data["universe"] if not r["in_pool"]]
    if out:
        a("")
        a("*Out of pool:* " + "; ".join(
            f"{r['name']} (" + ("hard-excluded" if r['excluded'] else f"below 30W EMA {r['ext_pct']:+.1f}%" if r['ext_pct'] is not None else "below 30W EMA —%") + ")"
            for r in out))
    a(f"\n★ = would be in next Monday's concentrated cohort at "
      f"{'/'.join(map(str, CFG['concentrated_rank_weights_by_slot']))}% by rank.\n")
    a("---\n")
    for c in data["cohorts"]:
        a(f"## Cohort: {c['week_id']} ({c['series']})\n")
        a(f"Decided {c['decided_date']}, entry-priced off {c['entry_price_date']} close. "
          f"{c['days_live']} days live. Invested Rs {c['invested']:,.2f} / cash Rs {c['cash']:,.2f}.\n")
        a("| Holding | Wt % | Entry | Shares | Invested | Price | As of | 1-Day | Return % | Contrib pp |")
        a("|---|---:|---:|---:|---:|---:|---|---:|---:|---:|")
        for h in sorted(c["holdings"], key=lambda h: -h["contribution_pct"]):
            asof = h["as_of"] + ("*" if h["stale"] else "")
            wt = "—" if h["weight_pct"] is None else f"{h['weight_pct']}"
            a(f"| {h['name']} | {wt} | {h['entry_price']:,.2f} | {h['shares']} | {h['invested']:,.2f} | "
              f"{h['price']:,.2f} | {asof} | {_pct(h['day_change_pct'])} | {_pct(h['return_pct'])} | {h['contribution_pct']:+.2f} |")
        a(f"| **Cash** | | | | {c['cash']:,.2f} | | | | — | 0.00 |")
        a(f"| **Total** | | | | **{CAP:,.2f}** | | | {_pct(c['day_change_pct'])} | **{_pct(c['return_pct'])}** | "
          f"{c['return_pct']:+.2f} |")
        a("")
        gs = [h for h in c["holdings"] if h["as_of"] < data["as_of_date"]]
        if gs:
            a(f"\\* price carried forward — data source has not yet posted a {data['as_of_date']} close "
              f"({', '.join(sorted(set(h['name'] for h in gs)))}).")
        a("")
    a("---\n")
    a("*Generated by `paper-trading/scripts/refresh.py`. Do not hand-edit — re-run the script. "
      "Narrative commentary, when added, goes in the cohort sections above and survives regen only if "
      "the script is taught to preserve it; treat this file as disposable and the JSON as the source of truth.*")
    with open(os.path.join(PT, "RETURNS_TRACKER.md"), "w") as f:
        f.write("\n".join(L) + "\n")


# --------------------------------------------------------------------------- #
# dashboard.html                                                              #
# --------------------------------------------------------------------------- #
def write_dashboard(data):
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")  # safe to embed in <script>
    html = DASHBOARD_TEMPLATE.replace("/*__DATA__*/", payload)
    with open(os.path.join(PT, "dashboard.html"), "w") as f:
        f.write(html)
    # skeleton-free fragment for `Artifact` publishing (no doctype/html/head/body of our own;
    # <title>/<link>/<style> are valid in the body flow and the tool scans the first 8KB for <title>)
    frag = html
    frag = frag[frag.index("<title>"):]
    frag = frag.replace("</head>\n<body>", "").replace("\n</body>\n</html>\n", "\n")
    with open(os.path.join(PT, "dashboard.artifact.html"), "w") as f:
        f.write(frag)


def print_summary(data):
    print(f"\npaper-trading refresh — as of {data['as_of_date']} ({data['generated_at']})")
    print("-" * 64)
    for c in data["cohorts"]:
        dc = "  n/a " if c["day_change_pct"] is None else f"{c['day_change_pct']:+6.2f}"
        print(f"  {c['week_id']:<20} {c['series']:<13} value {c['current_value']:>12,.2f}  "
              f"1d {dc}%  total {c['return_pct']:+7.2f}%")
    for s, v in sorted(data["series_summary"].items()):
        print(f"  [{s} avg] {v['avg_return_pct']:+.2f}% over {v['count']} cohort(s)")
    print("\n  Composite top-5 for next Monday's concentrated cohort:")
    for i, r in enumerate(data["concentrated_next"], 1):
        print(f"   {i}. {r['name']:<28} wt {r['weight_pct']:>2}%  composite {r['composite']:.1f} "
              f"(master {r['master']:.0f} / tech wk {r['weekly_technical'] if r['weekly_technical'] is not None else '—'}"
              f" mo {r['monthly_technical'] if r['monthly_technical'] is not None else '—'}"
              f" / conv {r['conviction']:.0f} / gap {r['gap']:.0f})")
    if data["age_matched_note"]:
        print(f"\n  Age-matched: {data['age_matched_note']}")
    lr = data.get("live_recommendation")
    if lr:
        d = "" if lr.get("day_change_pct") is None else f"{lr['day_change_pct']:+.2f}%"
        print(f"\n  [live recommendation] v{lr.get('version')}  Rs {lr['nav']:>12,.2f}  "
              f"1d {d}  total {lr['return_pct']:+.2f}%  ({lr.get('source_revision','?')})")
    print()


DASHBOARD_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Front-Test Ledger</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root{
  color-scheme: light;
  --paper:#f2efe9; --surface:#fbf9f5; --surface-2:#f6f3ec; --edge:#e0dbd0; --edge-strong:#cec7b7;
  --ink:#211d17; --ink-2:#5c564a; --ink-3:#8a8373;
  --accent:#39527e; --accent-soft:#e6ebf3;
  --gain:#1c7a44; --gain-soft:#e2efe5; --loss:#b23f2c; --loss-soft:#f3e3de; --warn:#8a6a1f;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100;
  --shadow:0 1px 2px rgba(33,29,23,.06),0 8px 24px rgba(33,29,23,.05);
  --radius:10px;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme: dark;
    --paper:#14130f; --surface:#1c1b16; --surface-2:#232219; --edge:#33312a; --edge-strong:#45423a;
    --ink:#ece7db; --ink-2:#b3ac9c; --ink-3:#7d7768;
    --accent:#8ea6d4; --accent-soft:#242b39;
    --gain:#5bb87e; --gain-soft:#1e2c22; --loss:#df8a76; --loss-soft:#2f221d; --warn:#d0a24e;
    --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px rgba(0,0,0,.35);
  }
}
:root[data-theme="dark"]{
  color-scheme: dark;
  --paper:#14130f; --surface:#1c1b16; --surface-2:#232219; --edge:#33312a; --edge-strong:#45423a;
  --ink:#ece7db; --ink-2:#b3ac9c; --ink-3:#7d7768;
  --accent:#8ea6d4; --accent-soft:#242b39;
  --gain:#5bb87e; --gain-soft:#1e2c22; --loss:#df8a76; --loss-soft:#2f221d; --warn:#d0a24e;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  font-size:15px; line-height:1.55; letter-spacing:.005em;
}
.wrap{max-width:1180px; margin:0 auto; padding:32px 22px 80px}
h1,h2,h3{font-family:"Spectral",Georgia,"Times New Roman",serif; font-weight:600; text-wrap:balance; margin:0}
h1{font-size:30px; letter-spacing:-.01em}
h2{font-size:20px; letter-spacing:-.005em}
.mono{font-family:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace; font-variant-numeric:tabular-nums}
.eyebrow{font-size:11.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--ink-3); font-weight:600}
a{color:var(--accent)}

header.masthead{border-bottom:2px solid var(--edge-strong); padding-bottom:20px; margin-bottom:26px}
.masthead .row{display:flex; flex-wrap:wrap; gap:18px 28px; align-items:baseline; justify-content:space-between}
.masthead p.lede{margin:10px 0 0; color:var(--ink-2); max-width:64ch; font-size:14.5px}
.stamp{font-size:12.5px; color:var(--ink-3)}
.stamp b{color:var(--ink-2); font-weight:600}
.theme-btn{font:inherit; font-size:12px; color:var(--ink-2); background:var(--surface); border:1px solid var(--edge);
  border-radius:999px; padding:5px 12px; cursor:pointer}
.theme-btn:hover{border-color:var(--edge-strong)}

section{margin:34px 0 0}
.sec-head{display:flex; align-items:baseline; gap:12px; margin-bottom:14px}
.sec-head .note{font-size:12.5px; color:var(--ink-3)}

.cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(268px,1fr)); gap:16px}
.card{background:var(--surface); border:1px solid var(--edge); border-radius:var(--radius); padding:18px 18px 16px; box-shadow:var(--shadow)}
.card .tag{display:inline-flex; align-items:center; gap:7px; font-size:11px; letter-spacing:.1em; text-transform:uppercase; font-weight:600; color:var(--ink-2)}
.dot{width:9px; height:9px; border-radius:3px; display:inline-block}
.card h3{font-size:15px; margin-top:9px; font-family:"IBM Plex Sans",sans-serif; font-weight:600}
.bignum{font-size:27px; margin-top:8px; letter-spacing:-.01em}
.subline{display:flex; gap:10px; align-items:baseline; margin-top:3px; font-size:13px; color:var(--ink-2)}
.pill{font-size:11.5px; font-weight:600; padding:2px 8px; border-radius:999px; display:inline-flex; gap:5px; align-items:center}
.pill.up{background:var(--gain-soft); color:var(--gain)}
.pill.down{background:var(--loss-soft); color:var(--loss)}
.pill.flat{background:var(--surface-2); color:var(--ink-2)}
.meta{margin-top:13px; display:grid; grid-template-columns:1fr 1fr; gap:7px 14px; font-size:12.5px; color:var(--ink-2)}
.meta .k{color:var(--ink-3)}
.split{margin-top:13px}
.split-bar{height:7px; border-radius:4px; background:var(--accent); position:relative; overflow:hidden; border:1px solid var(--edge)}
.split-bar i{position:absolute; top:0; bottom:0; right:0; background:var(--surface-2); border-left:2px solid var(--surface)}
.split-lab{display:flex; justify-content:space-between; font-size:11.5px; color:var(--ink-3); margin-top:5px}
.chips{margin-top:12px; display:flex; flex-direction:column; gap:5px; font-size:12px}
.chip{display:flex; justify-content:space-between; gap:10px}
.chip .nm{color:var(--ink-2); overflow:hidden; text-overflow:ellipsis; white-space:nowrap}

.panel{background:var(--surface); border:1px solid var(--edge); border-radius:var(--radius); padding:20px; box-shadow:var(--shadow)}
.grid-2{display:grid; grid-template-columns:1.35fr 1fr; gap:18px}
@media (max-width:860px){ .grid-2{grid-template-columns:1fr} }

table{width:100%; border-collapse:collapse; font-size:13px}
.scroll{overflow-x:auto; -webkit-overflow-scrolling:touch}
th,td{padding:8px 10px; text-align:right; white-space:nowrap; border-bottom:1px solid var(--edge)}
th:first-child,td:first-child{text-align:left; white-space:normal}
thead th{font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-3); font-weight:600; border-bottom:1px solid var(--edge-strong)}
tbody tr:hover{background:var(--surface-2)}
tr.star td{background:var(--accent-soft)}
tr.star td:first-child{box-shadow:inset 3px 0 0 var(--accent)}
td.pos{color:var(--gain)} td.neg{color:var(--loss)}
.num{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace; font-variant-numeric:tabular-nums}
.sub{color:var(--ink-3); font-size:11.5px}

.legend{display:flex; flex-wrap:wrap; gap:14px; font-size:12px; color:var(--ink-2); margin:2px 0 12px}
.legend span{display:inline-flex; align-items:center; gap:6px}
.legend i{width:12px; height:3px; border-radius:2px; display:inline-block}

.factorbar{display:flex; height:16px; border-radius:4px; overflow:hidden; border:1px solid var(--edge); background:var(--surface-2)}
.factorbar i{display:block; border-right:2px solid var(--surface)}
.factorbar i:last-child{border-right:0}
.flabels{display:flex; flex-wrap:wrap; gap:10px; font-size:11px; color:var(--ink-3); margin-top:6px}
.flabels span{display:inline-flex; gap:5px; align-items:center}
.flabels i{width:9px; height:9px; border-radius:2px; display:inline-block}

.methods{font-size:12.5px; color:var(--ink-2); line-height:1.6}
.methods code{font-family:"IBM Plex Mono",monospace; font-size:11.5px; background:var(--surface-2); padding:1px 5px; border-radius:4px}
.foot{margin-top:40px; padding-top:18px; border-top:1px solid var(--edge); font-size:12px; color:var(--ink-3)}
svg text{font-family:"IBM Plex Mono",ui-monospace,monospace}
.ttip{position:fixed; pointer-events:none; z-index:50; background:var(--ink); color:var(--paper); font-size:11.5px;
  padding:6px 9px; border-radius:6px; opacity:0; transition:opacity .1s; font-family:"IBM Plex Mono",monospace; white-space:pre; box-shadow:var(--shadow)}
.barrow{display:grid; grid-template-columns:150px 1fr 62px; gap:10px; align-items:center; font-size:12px; margin:5px 0}
.barrow .track{position:relative; height:15px; background:var(--surface-2); border:1px solid var(--edge); border-radius:4px}
.barrow .fill{position:absolute; top:0; bottom:0; border-radius:3px}
.barrow .mid{position:absolute; top:-3px; bottom:-3px; width:1px; background:var(--edge-strong); left:50%}
.barrow .v{text-align:right; color:var(--ink-2)}
.barrow .nm{color:var(--ink-2); overflow:hidden; text-overflow:ellipsis; white-space:nowrap}

.flag{display:inline-block; font-size:10.5px; font-weight:600; letter-spacing:.05em; text-transform:uppercase;
  padding:3px 8px; border-radius:999px; background:var(--loss-soft); color:var(--loss); border:1px solid var(--loss); margin:2px 4px 2px 0}
.flag.warn{background:var(--surface-2); color:var(--warn); border-color:var(--warn)}
.kv{display:flex; flex-wrap:wrap; gap:6px 20px; font-size:12.5px; color:var(--ink-2); margin-top:12px}
.kv span .k{color:var(--ink-3); margin-right:5px}
.kv b{color:var(--ink); font-weight:600}
.swing-head{display:flex; flex-wrap:wrap; align-items:baseline; gap:8px 16px}

@media print{
  #themeBtn, #printBtn{display:none !important;}
  body{background:#fff; color:#111}
  .wrap{max-width:100%; padding:12px 0}
  .card, .panel, .cards, .top10, .tablewrap{box-shadow:none; break-inside:avoid}
  table{min-width:0}
  thead th{position:static; color:#333}
  tbody tr{break-inside:avoid}
  a{color:#111; text-decoration:none}
}
</style>
</head>
<body>
<div class="wrap">
  <header class="masthead">
    <div class="row">
      <div>
        <div class="eyebrow">Rs 1,00,000 forward test &middot; frozen weekly cohorts</div>
        <h1>Front-Test Ledger</h1>
      </div>
      <div style="text-align:right">
        <div class="stamp">as of <b id="asof"></b></div>
        <div class="stamp" id="gen"></div>
        <button class="theme-btn" id="themeBtn" type="button">theme</button>
        <button class="theme-btn" id="printBtn" type="button">print / PDF</button>
      </div>
    </div>
    <p class="lede">Every Monday a new Rs 1,00,000 paper portfolio is decided from the live recommendation,
      priced at the prior Friday's close, and then never touched again. Two sizing philosophies run in
      parallel &mdash; <b>standard</b> (diversified) and <b>concentrated</b> (top-5 by a two-factor composite).
      A separate <b>live recommendation tracker</b> stays continuously rebalanced to whatever the
      recommendation doc says right now, for contrast against the frozen cohorts. A weekly, frozen
      <b>6-month swing cohort series</b> (momentum + dated catalysts, hard stops) runs alongside for a
      third angle. Marked to market every weekday; nothing here is advice.</p>
  </header>

  <section id="s-cards">
    <div class="sec-head"><h2>Cohorts</h2><span class="note" id="cards-note"></span></div>
    <div class="cards" id="cards"></div>
  </section>

  <section id="s-live">
    <div class="sec-head"><h2>Live recommendation tracker</h2><span class="note">continuously rebalanced to the current doc &middot; not a frozen cohort</span></div>
    <div class="panel" id="live-panel"></div>
  </section>

  <section id="s-swing">
    <div class="sec-head"><h2>6-month swing cohorts</h2><span class="note">weekly, frozen at entry &middot; &minus;16% stops per cohort &middot; never rebalanced</span></div>
    <div id="swing-panels"></div>
  </section>

  <section id="s-series">
    <div class="sec-head"><h2>Standard vs concentrated</h2><span class="note">same data, same start, different sizing</span></div>
    <div class="panel" id="series-panel"></div>
  </section>

  <section id="s-chart">
    <div class="sec-head"><h2>Value since entry</h2><span class="note">indexed to 100 at each cohort's Friday entry &middot; history builds daily</span></div>
    <div class="panel">
      <div class="legend" id="chart-legend"></div>
      <div class="scroll"><div id="linechart"></div></div>
    </div>
  </section>

  <section id="s-contrib">
    <div class="sec-head"><h2>What's moving each cohort</h2><span class="note">contribution to cohort return, in percentage points of the Rs 1,00,000</span></div>
    <div id="contrib"></div>
  </section>

  <section id="s-detail">
    <div class="sec-head"><h2>Cohort detail</h2><span class="note">sorted by contribution &middot; * = price carried forward</span></div>
    <div id="detail"></div>
  </section>

  <section id="s-model">
    <div class="sec-head"><h2>Composite model &mdash; next concentrated cohort</h2><span class="note">recomputed live each run</span></div>
    <div class="grid-2">
      <div class="panel" id="model-table"></div>
      <div class="panel methods" id="model-methods"></div>
    </div>
  </section>

  <div class="foot" id="foot"></div>
</div>
<div class="ttip" id="tip"></div>

<script id="data" type="application/json">/*__DATA__*/</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const tip = document.getElementById('tip');
const fmt = (n,d=2)=> n==null? '—' : n.toLocaleString('en-IN',{minimumFractionDigits:d,maximumFractionDigits:d});
const pct = (n,d=2)=> n==null? '—' : (n>=0?'+':'') + n.toFixed(d) + '%';
const SCLR = {standard:'var(--s1)', concentrated:'var(--s2)'};
const FVAR = {master:'var(--s1)', technical:'var(--s4)'};
function showTip(html,x,y){ tip.innerHTML=html; tip.style.opacity='1'; tip.style.left=(x+14)+'px'; tip.style.top=(y+14)+'px'; }
function hideTip(){ tip.style.opacity='0'; }

document.getElementById('asof').textContent = D.as_of_date;
document.getElementById('gen').textContent = 'generated ' + D.generated_at + ' · ' + D.history_points + ' day(s) of history';

/* ---- theme toggle ---- */
const tb = document.getElementById('themeBtn');
tb.onclick = ()=>{
  const cur = document.documentElement.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : (cur === 'light' ? 'dark' : (matchMedia('(prefers-color-scheme: dark)').matches ? 'light' : 'dark'));
  document.documentElement.setAttribute('data-theme', next);
  try{ localStorage.setItem('ftl-theme', next); }catch(e){}
  draw();
};
try{ const t = localStorage.getItem('ftl-theme'); if(t) document.documentElement.setAttribute('data-theme', t); }catch(e){}

/* ---- print / save as PDF ---- */
document.getElementById('printBtn').addEventListener('click', ()=> window.print());

/* ---- cards ---- */
function cohortLabel(c){ return c.week_id + ' · ' + c.series; }
function card(c){
  const best = [...c.holdings].sort((a,b)=>b.return_pct-a.return_pct)[0];
  const worst = [...c.holdings].sort((a,b)=>a.return_pct-b.return_pct)[0];
  const dc = c.day_change_pct;
  const investedPct = c.invested / D.capital * 100;
  const retCls = c.return_pct>=0?'pos':'neg';
  let dayPill;
  if(dc==null){
    dayPill = `<span class="pill flat">first mark</span>`;
  }else{
    const cls = dc>0.005?'up':(dc<-0.005?'down':'flat');
    const arrow = dc>0.005?'▲':(dc<-0.005?'▼':'■');
    dayPill = `<span class="pill ${cls}">${arrow} ${pct(dc)} today</span>`
      + `<span class="sub mono">${c.day_change_value>=0?'+':''}${fmt(c.day_change_value,0)}</span>`;
  }
  return `<div class="card">
    <span class="tag"><i class="dot" style="background:${SCLR[c.series]||'var(--ink-3)'}"></i>${c.series}</span>
    <h3>${c.week_id}<span class="sub">&nbsp;· ${c.days_live}d live · from ${c.entry_price_date}</span></h3>
    <div class="bignum mono">Rs ${fmt(c.current_value)}</div>
    <div class="subline">
      <span class="${retCls}" style="font-weight:600">${pct(c.return_pct)}</span>
      ${dayPill}
    </div>
    <div class="split">
      <div class="split-bar"><i style="width:${(100-investedPct).toFixed(1)}%"></i></div>
      <div class="split-lab"><span>invested ${investedPct.toFixed(1)}%</span><span>cash ${(100-investedPct).toFixed(1)}%</span></div>
    </div>
    <div class="chips">
      <div class="chip"><span class="nm">▲ ${best.name}</span><span class="pos mono">${pct(best.return_pct)}</span></div>
      <div class="chip"><span class="nm">▼ ${worst.name}</span><span class="neg mono">${pct(worst.return_pct)}</span></div>
    </div>
  </div>`;
}
document.getElementById('cards').innerHTML = D.cohorts.map(card).join('');
document.getElementById('cards-note').textContent = D.cohorts.length + ' running · none ever rebalanced';

/* ---- live recommendation tracker (single, continuously rebalanced) ---- */
(function(){
  const lr = D.live_recommendation;
  const sec = document.getElementById('s-live');
  if(!lr){ if(sec) sec.hidden = true; return; }
  const retCls = lr.return_pct>=0?'pos':'neg';
  const dcTxt = lr.day_change_pct==null ? '—' : pct(lr.day_change_pct);
  const vh = lr.value_history||[];
  let spark = '';
  if(vh.length>=2){
    const W=300,H=56,pd=4, vals=vh.map(p=>p.indexed);
    const lo=Math.min(100,...vals), hi=Math.max(100,...vals), rng=(hi-lo)||1;
    const X=i=> pd + i/(vh.length-1)*(W-2*pd);
    const Y=v=> pd + (1-(v-lo)/rng)*(H-2*pd);
    const d=vals.map((v,i)=>(i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1)).join(' ');
    spark=`<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" style="margin-top:10px" aria-hidden="true">`
      +`<line x1="${pd}" y1="${Y(100).toFixed(1)}" x2="${W-pd}" y2="${Y(100).toFixed(1)}" stroke="var(--edge-strong)" stroke-dasharray="2 3"/>`
      +`<path d="${d}" fill="none" stroke="var(--s4)" stroke-width="2" stroke-linejoin="round"/></svg>`;
  }
  const hrows = [...lr.holdings].sort((a,b)=>b.return_pct-a.return_pct).map(h=>`<tr>
      <td>${h.name}${h.stale?' <span class="sub">*</span>':''}</td>
      <td class="num">${h.weight_pct}</td>
      <td class="num">${fmt(h.entry_price)}</td>
      <td class="num">${fmt(h.price)}</td>
      <td class="num ${h.return_pct>=0?'pos':'neg'}">${pct(h.return_pct)}</td>
      <td class="num">${fmt(h.value,0)}</td>
    </tr>`).join('');
  const rebal = (lr.rebalance_log||[]).slice().reverse().slice(0,8).map(e=>
    `<div class="chip"><span class="nm">${e.date} &middot; v${e.version}</span><span class="sub">${e.reason}</span></div>`).join('');
  document.getElementById('live-panel').innerHTML = `
    <div class="swing-head">
      <div class="bignum mono">Rs ${fmt(lr.nav)}</div>
      <div class="${retCls}" style="font-size:18px;font-weight:600">${pct(lr.return_pct)}</div>
      <div class="sub">1-day ${dcTxt} &nbsp;·&nbsp; v${lr.version} since ${lr.inception_date} &nbsp;·&nbsp; source ${lr.source_revision||'—'}</div>
    </div>
    ${spark}
    <div class="kv">
      <span><span class="k">invested / cash</span><b>${fmt(lr.invested_value,0)} / ${fmt(lr.cash,0)}</b></span>
      <span><span class="k">rebalances</span><b>${(lr.rebalance_log||[]).length}</b></span>
    </div>
    <div class="scroll" style="margin-top:14px"><table>
      <thead><tr><th>Holding</th><th>Wt%</th><th>Entry (v${lr.version})</th><th>Price</th><th>Return</th><th>Value</th></tr></thead>
      <tbody>${hrows}</tbody>
    </table></div>
    ${rebal?`<div class="chips" style="margin-top:12px">${rebal}</div>`:''}
    <p class="sub" style="margin-top:10px">Auto-rebalances at live prices whenever the recommendation doc's Section 3 changes a holding or a weight by more than 0.5pp. Entry price shown is this version's rebalance price, not the original inception price. * = price carried forward.</p>`;
})();

/* ---- 6-month swing cohorts (weekly, frozen) ---- */
(function(){
  const cohorts = D.swing_cohorts||[];
  const sec = document.getElementById('s-swing');
  if(!cohorts.length){ if(sec) sec.hidden = true; return; }
  const badge = f => `<span class="flag${/EXTENDED/.test(f)?' warn':''}">${f}</span>`;
  document.getElementById('swing-panels').innerHTML = cohorts.map(sw=>{
    const retCls = sw.port_return_pct>=0?'pos':'neg';
    const b = sw.benchmark;
    const alphaCls = (sw.alpha_pct||0)>=0?'pos':'neg';
    const dcTxt = sw.day_change_pct==null ? '—' : pct(sw.day_change_pct);
    const flagBadges = (sw.flags||[]).map(badge).join('');
    const vh = sw.value_history||[];
    let spark = '';
    if(vh.length>=2){
      const W=300,H=56,pd=4, vals=vh.map(p=>p.indexed);
      const lo=Math.min(100,...vals), hi=Math.max(100,...vals), rng=(hi-lo)||1;
      const X=i=> pd + i/(vh.length-1)*(W-2*pd);
      const Y=v=> pd + (1-(v-lo)/rng)*(H-2*pd);
      const d=vals.map((v,i)=>(i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1)).join(' ');
      spark=`<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" style="margin-top:10px" aria-hidden="true">`
        +`<line x1="${pd}" y1="${Y(100).toFixed(1)}" x2="${W-pd}" y2="${Y(100).toFixed(1)}" stroke="var(--edge-strong)" stroke-dasharray="2 3"/>`
        +`<path d="${d}" fill="none" stroke="var(--s3)" stroke-width="2" stroke-linejoin="round"/></svg>`;
    }
    const nextReview = (sw.rules&&sw.rules.review_dates||[]).filter(x=>x>=D.as_of_date)[0];
    const hrows = [...sw.holdings].sort((a,b)=>b.return_pct-a.return_pct).map(h=>{
      const fl = (h.flags||[]).join(', ');
      const near = h.dist_to_stop_pct!=null && h.dist_to_stop_pct<=3;
      return `<tr class="${fl?'star':''}">
        <td>${h.name}${h.stale?' <span class="sub">*</span>':''}${h.catalyst?`<div class="sub">${h.catalyst}</div>`:''}</td>
        <td class="num">${h.weight_pct}</td>
        <td class="num">${fmt(h.entry_price)}</td>
        <td class="num">${fmt(h.price)}</td>
        <td class="num ${h.day_change_pct>=0?'pos':'neg'}">${pct(h.day_change_pct)}</td>
        <td class="num ${h.return_pct>=0?'pos':'neg'}">${pct(h.return_pct)}</td>
        <td class="num ${near?'neg':''}">${h.dist_to_stop_pct==null?'—':(h.dist_to_stop_pct>=0?'+':'')+h.dist_to_stop_pct.toFixed(1)+'%'}</td>
        <td class="num">${h.ext_vs_30w_ema_pct==null?'—':(h.ext_vs_30w_ema_pct>=0?'+':'')+h.ext_vs_30w_ema_pct.toFixed(0)+'%'}</td>
        <td class="sub">${fl||'—'}</td>
      </tr>`;
    }).join('');
    return `<div class="panel" style="margin-bottom:14px">
      <div class="sec-head" style="margin-bottom:2px"><h3 style="font-family:'IBM Plex Sans',sans-serif;font-size:15px">${sw.week_id}</h3>
        <span class="note">decided ${sw.decided_date} &middot; entry ${sw.start_date}</span></div>
      <div class="swing-head">
        <div class="bignum mono">Rs ${fmt(sw.port_value)}</div>
        <div class="${retCls}" style="font-size:18px;font-weight:600">${pct(sw.port_return_pct)}</div>
        <div class="sub">1-day ${dcTxt}${b?` &nbsp;·&nbsp; ${b.label} ${pct(b.return_pct)} &nbsp;·&nbsp; <b class="${alphaCls}">alpha ${(sw.alpha_pct||0)>=0?'+':''}${sw.alpha_pct} pp</b>`:''}</div>
      </div>
      ${spark}
      <div class="kv">
        <span><span class="k">horizon</span><b>${sw.horizon_end_date||'—'}${sw.days_to_horizon!=null?` (${sw.days_to_horizon}d)`:''}</b></span>
        <span><span class="k">invested / cash</span><b>${fmt(sw.invested_value,0)} / ${fmt(sw.cash,0)}</b></span>
        <span><span class="k">next review</span><b>${nextReview||'—'}</b></span>
        <span><span class="k">hard stop</span><b>${sw.rules&&sw.rules.hard_stop_pct!=null?sw.rules.hard_stop_pct+'%':'—'}</b></span>
        ${sw.market_regime&&sw.market_regime.available?`<span><span class="k">market regime</span><b class="${sw.market_regime.downtrend?'neg':'pos'}">${sw.market_regime.label} ${pct(sw.market_regime.ext_pct)} vs 30W EMA</b></span>`:''}
      </div>
      <div style="margin-top:12px">${flagBadges||'<span class="sub">no rule flags active</span>'}</div>
      <div class="scroll" style="margin-top:14px"><table>
        <thead><tr><th>Holding</th><th>Wt%</th><th>Entry</th><th>Price</th><th>1-Day</th><th>Return</th><th>To stop</th><th>vs EMA</th><th>Flags</th></tr></thead>
        <tbody>${hrows}</tbody>
      </table></div>
    </div>`;
  }).join('') + `<p class="sub">Momentum + dated-catalyst screen. Each cohort is frozen at entry: &minus;16% hard stops per holding, never rebalanced. This script surfaces flags only -- act at the monthly review or ad hoc. Method: <code>SWING_6M_PORTFOLIO.md</code>. * = price carried forward.</p>`;
})();

/* ---- series comparison ---- */
(function(){
  const s = D.series_summary;
  const rows = Object.keys(s).sort().map(k=>{
    const v = s[k];
    const cls = v.avg_return_pct>=0?'pos':'neg';
    return `<tr><td><i class="dot" style="background:${SCLR[k]||'var(--ink-3)'}"></i> ${k}</td>
      <td class="num">${v.count}</td>
      <td class="num ${cls}">${pct(v.avg_return_pct)}</td></tr>`;
  }).join('');
  const note = D.age_matched_note
    ? `<p class="sub" style="margin:12px 0 0">Age-matched: ${D.age_matched_note}.</p>`
    : `<p class="sub" style="margin:12px 0 0">An age-matched comparison (same-age cohorts, standard vs concentrated) appears once both series have ≥2 cohort-weeks.</p>`;
  document.getElementById('series-panel').innerHTML =
    `<div class="scroll"><table><thead><tr><th>Series</th><th>Cohorts</th><th>Avg return</th></tr></thead><tbody>${rows}</tbody></table></div>${note}`;
})();

/* ---- line chart ---- */
function draw(){ lineChart(); }
function css(v){ return getComputedStyle(document.body).getPropertyValue(v).trim(); }
function lineChart(){
  const host = document.getElementById('linechart');
  const ts = D.value_timeseries;
  const keys = Object.keys(ts);
  const W = Math.max(680, host.clientWidth||900), H = 300, m = {t:16,r:64,b:34,l:46};
  const allDates = [...new Set([].concat(...keys.map(k=>ts[k].map(p=>p.date))))].sort();
  const x0 = new Date(allDates[0]), x1 = new Date(allDates[allDates.length-1]);
  const span = Math.max(1, x1-x0);
  let lo=100, hi=100;
  keys.forEach(k=>ts[k].forEach(p=>{ lo=Math.min(lo,p.indexed); hi=Math.max(hi,p.indexed); }));
  const pad = Math.max(0.6,(hi-lo)*0.18); lo-=pad; hi+=pad;
  const X = d => m.l + (new Date(d)-x0)/span * (W-m.l-m.r);
  const Y = v => m.t + (1-(v-lo)/(hi-lo)) * (H-m.t-m.b);
  const grid=[], ny=4;
  for(let i=0;i<=ny;i++){ const v=lo+(hi-lo)*i/ny; const y=Y(v);
    grid.push(`<line x1="${m.l}" y1="${y}" x2="${W-m.r}" y2="${y}" stroke="${css('--edge')}" stroke-width="1"/>`);
    grid.push(`<text x="${m.l-8}" y="${y+3}" text-anchor="end" font-size="10" fill="${css('--ink-3')}">${v.toFixed(1)}</text>`);
  }
  const base = Y(100);
  grid.push(`<line x1="${m.l}" y1="${base}" x2="${W-m.r}" y2="${base}" stroke="${css('--edge-strong')}" stroke-width="1" stroke-dasharray="2 3"/>`);
  const xt=[x0, new Date((+x0+ +x1)/2), x1].map(d=>{
    const s=d.toISOString().slice(0,10);
    return `<text x="${X(s)}" y="${H-12}" text-anchor="middle" font-size="10" fill="${css('--ink-3')}">${s.slice(5)}</text>`;
  }).join('');
  const seriesOf = k => k.includes('concentrated') ? 'concentrated' : (k.includes('standard') ? 'standard' : 'other');
  const colOf = s => s==='concentrated' ? '--s2' : (s==='standard' ? '--s1' : '--s3');
  const DASHES = ['', '7 4', '2 4', '10 3 2 3'];
  const seen = {};
  const dashIx = {};
  keys.forEach(k=>{ const s=seriesOf(k); dashIx[k] = (seen[s]=(seen[s]||0)+1) - 1; });
  const paths = keys.map((k)=>{
    const col = css(colOf(seriesOf(k)));
    const dash = DASHES[Math.min(dashIx[k], DASHES.length-1)];
    const pts = ts[k];
    const d = pts.map((p,j)=> (j?'L':'M') + X(p.date).toFixed(1) + ' ' + Y(p.indexed).toFixed(1)).join(' ');
    const dots = pts.map(p=>`<circle cx="${X(p.date).toFixed(1)}" cy="${Y(p.indexed).toFixed(1)}" r="${p===pts[pts.length-1]?3.6:2.4}" fill="${col}"/>`).join('');
    const last = pts[pts.length-1];
    const lab = `<text x="${X(last.date)+7}" y="${Y(last.indexed)+3}" font-size="10" fill="${col}">${pct(last.return_pct)}</text>`;
    return `<path d="${d}" fill="none" stroke="${col}" stroke-width="2" stroke-linejoin="round" stroke-dasharray="${dash}"/>${dots}${lab}`;
  }).join('');
  const cross = `<line id="xhair" x1="0" y1="${m.t}" x2="0" y2="${H-m.b}" stroke="${css('--edge-strong')}" stroke-width="1" opacity="0"/>`;
  host.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Indexed value since entry">${grid.join('')}${xt}${paths}${cross}`
    + `<rect x="${m.l}" y="${m.t}" width="${W-m.l-m.r}" height="${H-m.t-m.b}" fill="transparent" id="hit"/></svg>`;
  document.getElementById('chart-legend').innerHTML = keys.map(k=>{
    const col = `var(${colOf(seriesOf(k))})`;
    const di = Math.min(dashIx[k], DASHES.length-1);
    const swatch = di===0
      ? `background:${col}`
      : `background:repeating-linear-gradient(90deg,${col} 0 ${di===1?5:3}px,transparent ${di===1?5:3}px ${di===1?9:6}px)`;
    return `<span><i style="${swatch}"></i>${k}</span>`;
  }).join('') + `<span><i style="background:var(--edge-strong)"></i>break-even (100)</span>`;
  const svg = host.querySelector('svg'), hit = host.querySelector('#hit'), xh = host.querySelector('#xhair');
  hit.addEventListener('mousemove', ev=>{
    const r = svg.getBoundingClientRect(), sx = (ev.clientX-r.left)/r.width*W;
    const t = x0.getTime() + (sx-m.l)/(W-m.l-m.r)*span;
    let best=null;
    allDates.forEach(dd=>{ const dt=new Date(dd).getTime(); if(best==null||Math.abs(dt-t)<Math.abs(new Date(best).getTime()-t)) best=dd; });
    xh.setAttribute('x1',X(best)); xh.setAttribute('x2',X(best)); xh.setAttribute('opacity','1');
    let rows = keys.map(k=>{ const pt=ts[k].find(p=>p.date===best); if(!pt) return null;
      const col = k.includes('concentrated')?'var(--s2)':(k.includes('standard')?'var(--s1)':'var(--s3)');
      return `<span style="color:${col}">■</span> ${k}  ${pt.indexed.toFixed(2)}  (${pct(pt.return_pct)})`; }).filter(Boolean).join('\n');
    showTip(`${best}\n${rows}`, ev.clientX, ev.clientY);
  });
  hit.addEventListener('mouseleave', ()=>{ xh.setAttribute('opacity','0'); hideTip(); });
}
window.addEventListener('resize', ()=>{ clearTimeout(window._rz); window._rz=setTimeout(lineChart,150); });
lineChart();

/* ---- contribution diverging bars ---- */
(function(){
  const host = document.getElementById('contrib');
  host.innerHTML = D.cohorts.map(c=>{
    const hs = [...c.holdings].filter(h=>Math.abs(h.contribution_pct)>=0.005).sort((a,b)=>b.contribution_pct-a.contribution_pct);
    const mx = Math.max(0.5, ...hs.map(h=>Math.abs(h.contribution_pct)));
    const rows = hs.map(h=>{
      const w = Math.abs(h.contribution_pct)/mx*50;
      const pos = h.contribution_pct>=0;
      const col = pos?'var(--gain)':'var(--loss)';
      const left = pos?50:50-w;
      const ttl = `${h.name}: ${h.contribution_pct>=0?'+':''}${h.contribution_pct.toFixed(2)}pp of the Rs 1,00,000 · return ${pct(h.return_pct)} on Rs ${fmt(h.invested,0)} invested`;
      return `<div class="barrow" title="${ttl}">
        <span class="nm">${h.name}</span>
        <div class="track"><div class="mid"></div><div class="fill" style="left:${left}%;width:${w}%;background:${col}"></div></div>
        <span class="v mono">${h.contribution_pct>=0?'+':''}${h.contribution_pct.toFixed(2)}</span>
      </div>`;
    }).join('');
    return `<div class="panel" style="margin-bottom:14px">
      <div class="sec-head" style="margin-bottom:8px">
        <i class="dot" style="background:${SCLR[c.series]||'var(--ink-3)'}"></i>
        <h3 style="font-family:'IBM Plex Sans',sans-serif;font-size:14px">${cohortLabel(c)}</h3>
        <span class="note">net ${pct(c.return_pct)}</span>
      </div>${rows}</div>`;
  }).join('');
})();

/* ---- cohort detail tables ---- */
(function(){
  const host = document.getElementById('detail');
  host.innerHTML = D.cohorts.map(c=>{
    const rows = [...c.holdings].sort((a,b)=>b.contribution_pct-a.contribution_pct).map(h=>{
      const stale = h.as_of < D.as_of_date;
      return `<tr>
        <td>${h.name}${stale?' <span class="sub">*</span>':''}</td>
        <td class="num">${h.weight_pct==null?'—':h.weight_pct}</td>
        <td class="num">${fmt(h.entry_price)}</td>
        <td class="num">${h.shares}</td>
        <td class="num">${fmt(h.invested)}</td>
        <td class="num">${fmt(h.price)}</td>
        <td class="num ${h.day_change_pct>=0?'pos':'neg'}">${pct(h.day_change_pct)}</td>
        <td class="num ${h.return_pct>=0?'pos':'neg'}">${pct(h.return_pct)}</td>
        <td class="num ${h.contribution_pct>=0?'pos':'neg'}">${h.contribution_pct>=0?'+':''}${h.contribution_pct.toFixed(2)}</td>
      </tr>`;
    }).join('');
    return `<div class="panel" style="margin-bottom:14px">
      <div class="sec-head" style="margin-bottom:8px">
        <i class="dot" style="background:${SCLR[c.series]||'var(--ink-3)'}"></i>
        <h3 style="font-family:'IBM Plex Sans',sans-serif;font-size:14px">${cohortLabel(c)}</h3>
        <span class="note">Rs ${fmt(c.current_value)} &middot; ${pct(c.return_pct)} &middot; cash Rs ${fmt(c.cash)}</span>
      </div>
      <div class="scroll"><table>
        <thead><tr><th>Holding</th><th>Wt%</th><th>Entry</th><th>Sh</th><th>Invested</th><th>Price</th><th>1-Day</th><th>Return</th><th>Contrib pp</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>`;
  }).join('');
})();

/* ---- composite model table ---- */
(function(){
  const pool = D.universe.filter(r=>r.in_pool).sort((a,b)=>a.composite_rank-b.composite_rank);
  const outp = D.universe.filter(r=>!r.in_pool);
  const nslots = D.concentrated_next.length;
  const fkeys = ['master','technical'];
  const W = D.composite_weights;
  const maxComp = Math.max(...pool.map(r=>r.composite));
  const rows = pool.map(r=>{
    const seg = fkeys.map(k=>{
      const w = r.contrib[k]/maxComp*100;
      return `<i style="width:${w.toFixed(1)}%;background:${FVAR[k]}" title="${k}: ${r.contrib[k].toFixed(1)} of composite ${r.composite.toFixed(1)} (raw ${r[k]==null?'—':r[k].toFixed(0)} × ${D.composite_weights[k]})"></i>`;
    }).join('');
    const d = r.rank_delta;
    const darr = d==null?'—':(d>0?`<span class="pos">▲${d}</span>`:(d<0?`<span class="neg">▼${-d}</span>`:'0'));
    const star = r.composite_rank<=nslots;
    return `<tr class="${star?'star':''}">
      <td>${r.composite_rank}${star?' ★':''} &nbsp;${r.name}
        <div class="factorbar" style="margin-top:5px">${seg}</div></td>
      <td class="num"><b>${r.composite.toFixed(1)}</b></td>
      <td class="num">${r.master.toFixed(0)}</td>
      <td class="num">${r.conviction.toFixed(0)}</td>
      <td class="num">${r.gap.toFixed(0)}</td>
      <td class="num">${r.weekly_technical==null?'—':r.weekly_technical.toFixed(0)}</td>
      <td class="num">${r.monthly_technical==null?'—':r.monthly_technical.toFixed(0)}</td>
      <td class="num ${r.ext_pct>=0?'pos':'neg'}">${r.ext_pct==null?'—':(r.ext_pct>=0?'+':'')+r.ext_pct.toFixed(1)+'%'}</td>
      <td class="num ${r.ext_pct_monthly>=0?'pos':'neg'}">${r.ext_pct_monthly==null?'—':(r.ext_pct_monthly>=0?'+':'')+r.ext_pct_monthly.toFixed(1)+'%'}</td>
      <td class="num">${r.conviction_rank}</td>
      <td class="num">${darr}</td>
    </tr>`;
  }).join('');
  const outrow = outp.length? `<p class="sub" style="margin:10px 0 0">Out of pool: ` + outp.map(r=>
      `${r.name} (${r.excluded?'hard-excluded':'below 30W EMA '+(r.ext_pct>=0?'+':'')+ (r.ext_pct==null?'?':r.ext_pct.toFixed(1))+'%'})`).join('; ') + `.</p>` : '';
  document.getElementById('model-table').innerHTML = `
    <div class="flabels">
      <span><i style="background:var(--s1)"></i>master_score ×${W.master}</span>
      <span><i style="background:var(--s2)"></i>technical ×${W.technical} <span class="sub">(wk ${D.technical_weights?.weekly ?? '0.6'} / mo ${D.technical_weights?.monthly ?? '0.4'})</span></span>
    </div>
    <div class="scroll"><table>
      <thead><tr><th>Rank / name</th><th>Comp</th><th>Master</th><th>Conv</th><th>Gap</th><th>Tech-wk</th><th>Tech-mo</th><th>vs 30W EMA</th><th>vs 10M EMA</th><th>Conv-rk</th><th>Δ</th></tr></thead>
      <tbody>${rows}</tbody>
    </table></div>${outrow}`;
})();

/* ---- methodology ---- */
(function(){
  const W = D.composite_weights;
  const slots = D.concentrated_slots.join('/');
  const picks = D.concentrated_next.map((r,i)=>`${i+1}. <b>${r.name}</b> ${r.weight_pct}% <span class="sub">(composite ${r.composite.toFixed(1)})</span>`).join('<br>');
  document.getElementById('model-methods').innerHTML = `
    <h3 style="font-family:'IBM Plex Sans',sans-serif;font-size:14px;margin-bottom:8px">How the composite is built</h3>
    <p><b>composite</b> = ${W.master}·master_score + ${W.technical}·technical &nbsp;(each factor 0–100).</p>
    <p><b>Master score</b> — <code>master_score</code> from the ValuePickr screen (<code>valuepickr-open-screen/scripts/MASTER_SCORE_METHODOLOGY.md</code>): a renormalized blend of <code>conviction_score</code> (.25), <code>quality_score</code> (.25), <code>expectation_gap_score</code> (.20), <code>consistency_score</code> (.15, Mukherjea's Coffee Can persistence check) and <code>asymmetry_score</code> (.15, Pabrai's "heads I win, tails I don't lose much"), built from studying real high-return investors' documented methods. Conviction/Gap columns below are shown for context only — they already feed into Master upstream, so weighting them again here would double-count them.</p>
    <p><b>Technical</b> — now two timeframes, not one: <b>weekly</b> (60% of the technical weight) is the original discipline — last completed weekly close vs the 30-week EMA, full marks inside an 8% cushion, decays with extension, +12 for a fresh bullish cross, −20 past +45% extended, and a close below the EMA still drops the name from the pool entirely (this hard gate is unchanged). <b>Monthly</b> (40%) is new — last completed monthly close vs a 10-month EMA, a slower regime filter (Faber/GTAA-style) with wider thresholds (15% cushion, 70% overextended) that only ever shifts the score, never disqualifies — a weekly pullback inside a longer monthly uptrend is normal and shouldn't zero out the name.</p>
    <p style="margin-top:10px"><b>Next concentrated cohort</b> — Monday, top ${D.concentrated_next.length} sized ${slots}:<br>${picks}</p>
    <p class="sub" style="margin-top:10px">Weights live in <code>paper-trading/config.json</code>; <code>master_score</code> and the underlying conviction/quality/gap data are refreshed by other scheduled tasks and re-read here every run.</p>`;
})();

document.getElementById('foot').innerHTML =
  `Prices: Yahoo Finance daily/weekly closes. Standard/concentrated cohorts and swing cohorts are frozen at entry and never rebalanced — the recommendation doc evolves, these do not. ` +
  `The live recommendation tracker is the exception: it auto-rebalances to whatever the doc says right now. ` +
  `Swing cohorts carry their own hard stops and are benchmarked to the Nifty Smallcap 250. ` +
  `Generated by <code>paper-trading/scripts/refresh.py</code> on ${D.generated_at}. Research model only, not investment advice.`;
</script>
</body>
</html>
"""

if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "prices-asof":
        cmd_prices_asof(sys.argv[2], sys.argv[3].split(","))
    else:
        main()
