#!/usr/bin/env python3
"""
Builds the Confluence 100 artifact: a confidence-adjusted blend of master_score
(conviction/quality/expectation-gap/asymmetry) with two live technical reads —
a 30-week EMA trend read and a relative-strength read vs the Nifty 500 — over
the ValuePickr open-screen deepdive universe. Philosophy: strong business +
reasonable valuation + rising 30W trend + relative strength (beating the
market, not just trending up in isolation).

Two rankings are produced, each 100 names, switchable in the artifact:
  - "Overall"     — every deepdived stock with no red flag, ANY thesis_fit
                    (a 10x thesis is NOT required; a great business that only
                    clears the return bar at 3-4x still belongs on a
                    confidence-ranked shortlist).
  - "Thesis only" — the stricter historical list: thesis_fit is
                    10x-in-2-3-years or 100x-in-10-years, no red flag.
Thesis-only is a subset of Overall.

SME/Emerge exclusion (2026-09-18, at the user's explicit request): a stock
tagged `is_sme_emerge: true` on its state.json entry is hard-excluded from
both rankings in build_universe() below — it never enters `universe` at all,
so it can't appear in either list regardless of score. See build_universe()'s
docstring for how the tag is set/maintained.

Run as a side job of vpscreen-rerank (see that task's SKILL.md Step 7). It is
UNCONDITIONAL now — every rerank cycle rebuilds this, no weekly gate — because
a tier move, a new placement, or a score shift in Steps 3-6 can change either
list. Writes projects/valuepickr-open-screen/artifacts/confluence100.artifact.html;
the scheduled task then publishes that file with the Artifact tool using the
fixed URL recorded in vpscreen-rerank/SKILL.md.

Cost control: a live Yahoo Finance pull for every candidate every run is wasteful
(150-250 network calls per run). Only the top TOP_FRESH_N candidates by fundamental
score get a live pull every run; everyone else is served from data/technical_cache.json
and only refetched once it's older than CACHE_TTL_DAYS. See load/save_cache() and the
scan loop in main().

Data-loss safeguard: if live Yahoo access is broadly failing this run (network outage,
rate-limit), a stale cached read is used in preference to a blank "Not resolved" — and
if too few candidates resolve either way (MIN_RESOLVED_FRACTION), the run aborts BEFORE
touching the artifact/sidecar files, so a bad run can't clobber the last known-good
published build. This is exactly the failure mode that once silently overwrote a good
build with an all-unresolved one — see MEMORY project_confluence_100.md, 2026-09-16.

Usage: python3 projects/valuepickr-open-screen/scripts/build_confluence100.py  (from Stock Market root)
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
VP = os.path.join(ROOT, "projects", "valuepickr-open-screen")
BASE = VP
DATA_DIR = os.path.join(VP, "data")
ARTIFACTS_DIR = os.path.join(VP, "artifacts")
sys.path.insert(0, os.path.join(VP, "scripts"))
from resolve_data_file import resolve_data_path  # noqa: E402

TOP_N = 100
TECH_SCAN_BUFFER = 135  # scan more than TOP_N since some won't resolve / will lose to tech penalty

# "Investable now" gate (2026-09-18): a stock only counts toward the Top-10
# actionable cut if its confidence_pct is backed by real, complete inputs —
# not a score propped up on 1-2 present components, and not a stale/missing
# technical read. This is deliberately independent of confidence_pct itself
# (which already soft-discounts thin coverage via blend_fundamental's cov
# weighting) — soft-discounting can still leave an incomplete name ranked
# ahead of a complete one on a lucky component; the gate makes "complete
# enough to act on" an explicit yes/no instead of an implicit side-effect
# of the score. INVESTABLE_COV_THRESHOLD matches full_coverage_count's own
# bar for "fully cross-scored" so the two stats stay consistent.
INVESTABLE_COV_THRESHOLD = 0.85
INVESTABLE_TECH_STATUSES = ("ok",)
TOP10_N = 10

TOP_FRESH_N = 20         # always live-fetched every run, regardless of cache age
CACHE_TTL_DAYS = 7       # everyone else: reuse a cached read until it's this old
MIN_RESOLVED_FRACTION = 0.3  # abort (don't touch outputs) if fewer than this fraction resolves

ELIGIBLE_THESIS = ("10x-in-2-3-years", "100x-in-10-years")

# slug -> verified Yahoo symbol, consulted BEFORE the live name search.
# A null value = "confirmed no usable Yahoo weekly series" (NSE-Emerge / BSE-SME
# names return a single bar) — skip the search and mark the read unavailable
# cleanly instead of retrying every run. Maintained by hand + topped up from the
# "resolved by search this run" list this script prints at the end.
SYMBOL_MAP_PATH = os.path.join(DATA_DIR, "yahoo_symbol_map.json")


_SYMBOL_MAP_META_KEYS = {"_readme", "_verified"}


def load_symbol_map():
    """Flat slug -> symbol (or null) map at the top level of the JSON file,
    minus the leading '_'-prefixed metadata keys. (2026-09-18: fixed a bug
    where this read a nested "map" sub-key that no longer matched the file's
    actual flat structure, silently ignoring ~140 curated entries and forcing
    a live re-search for names that already had a verified symbol on file.)"""
    try:
        with open(SYMBOL_MAP_PATH) as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    return {k: v for k, v in raw.items() if k not in _SYMBOL_MAP_META_KEYS}


SYMBOL_MAP = load_symbol_map()
_RESOLVED_BY_SEARCH = {}  # slug -> symbol, for names not in SYMBOL_MAP that the search found

# Relative strength: is the stock beating the broad market, not just its own
# trend? Benchmarked against the Nifty 500 (^CRSLDX) — the universe here spans
# large- to micro-cap, so a broad index is the fairer bar than Nifty 50.
BENCHMARK_SYMBOL = "^CRSLDX"
BENCHMARK_LABEL = "Nifty 500"
RS_LOOKBACK_WEEKS = 13  # ~1 quarter, standard relative-strength window
MOMENTUM_LOOKBACK_WEEKS_LONG = 26  # ~2 quarters, the second leg of the momentum blend
_BENCHMARK_RETURN_PCT = None  # populated once in main(), read by _read_from_pairs

# 2026-09-22 (user request): confidence used to be blended_fundamental(0-100) plus
# two small additive deltas (tech_adjustment -18..+10, rs_adjustment -6..+6) — fundamentals
# dominated by construction but the split was never explicit. Replaced with a plain weighted
# composite of three 0-100 sub-scores so the "lean fundamentals, but also have momentum"
# balance is a literal, documented number rather than an emergent property of delta sizes.
FUND_WEIGHT = 0.70
TECH_WEIGHT = 0.18
MOMENTUM_WEIGHT = 0.12

# Technical-read cache: {"benchmark": {...} | None, "stocks": {slug: {...}}}.
# Keeps last-known-good 30W-EMA + RS reads so (a) most candidates only need a
# live Yahoo pull once a week instead of every run, and (b) a run where Yahoo
# access is broadly broken still has real data to fall back on instead of
# publishing a wall of "Not resolved".
CACHE_PATH = os.path.join(DATA_DIR, "technical_cache.json")


def load_cache():
    try:
        with open(CACHE_PATH) as f:
            c = json.load(f)
    except (OSError, json.JSONDecodeError):
        c = {}
    c.setdefault("benchmark", None)
    c.setdefault("stocks", {})
    return c


def save_cache(cache):
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    os.replace(tmp, CACHE_PATH)


def days_since(date_str, today):
    try:
        return (today - datetime.date.fromisoformat(date_str)).days
    except (TypeError, ValueError):
        return None


def tech_to_cache_entry(tech, today_iso):
    entry = dict(tech)
    entry["fetched_at"] = today_iso
    return entry


def cache_entry_to_tech(entry):
    return {k: v for k, v in entry.items() if k != "fetched_at"}


def atomic_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def build_universe():
    """Every deepdived stock with a clear red_flag_tier (HIGH CAUTION / AVOID /
    EXCLUDE are hard-dropped from a confidence ranking regardless of score).
    thesis_fit is NOT filtered here — each row carries `thesis_eligible` so the
    two rankings can be sliced downstream.

    SME/Emerge exclusion (2026-09-18, at the user's explicit request): a stock
    tagged `is_sme_emerge: true` on its state.json entry (see
    scripts/patch_stock.py) is hard-dropped here, before ranking — not merely
    penalized via the tech_adjustment -2 / investable_now gate it used to fall
    through. These names have no usable Yahoo weekly series by construction
    (single-bar illiquid boards), so they could never pass investable_now
    anyway; excluding them outright keeps Confluence-100 to names on the main
    board. The tag is maintained by hand (or by any task's research) via
    `patch_stock.py <slug> --set-json is_sme_emerge=true` the moment a listing
    platform is confirmed — do not infer it from `market_cap_tier` text here,
    that field is free-text and unreliable for a hard filter."""
    d = load_json(os.path.join(DATA_DIR, "master-scores.json"))
    state = load_json(os.path.join(BASE, "state.json"))["stocks"]
    ranked = d["ranked"]
    elig = [
        x for x in ranked
        if x.get("red_flag_tier") in (None, "")
        and not state.get(x["slug"], {}).get("is_sme_emerge")
    ]
    excluded_sme_emerge = sum(
        1 for x in ranked
        if x.get("red_flag_tier") in (None, "") and state.get(x["slug"], {}).get("is_sme_emerge")
    )
    out = []
    for x in elig:
        slug = x["slug"]
        path = resolve_data_path(BASE, DATA_DIR, slug)
        rec = {
            "slug": slug,
            "name": x["name"],
            "master_score": x["master_score"],
            "conviction_label": x["conviction"],
            "thesis_fit": x.get("thesis_fit"),
            "thesis_eligible": x.get("thesis_fit") in ELIGIBLE_THESIS,
            "sb": x["score_breakdown"],
        }
        if os.path.exists(path):
            try:
                sd = load_json(path)
                rec["tagline"] = sd.get("tagline")
                rec["market_cap_tier"] = sd.get("market_cap_tier")
                fb = sd.get("four_box") or {}
                rec["four_box_score"] = fb.get("score")
            except Exception:
                pass
        out.append(rec)
    return out, len(ranked), excluded_sme_emerge


def blend_fundamental(x):
    cov = x["sb"]["weight_coverage"]
    fb = x.get("four_box_score")
    fb_pct = (fb / 5 * 100) if fb is not None else x["master_score"]
    w_master = 0.4 + 0.6 * cov
    return round(w_master * x["master_score"] + (1 - w_master) * fb_pct, 2)


def clean_name(name):
    n = re.split(r"[:(~–—-]", name)[0].strip()
    n = re.sub(r"\bLtd\.?\b|\bLimited\b", "", n, flags=re.I).strip()
    return n or name.strip()


def yahoo_search(q, retries=2):
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for _ in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.load(r)
        except Exception:
            time.sleep(0.5)
    return None


def yahoo_chart(sym, retries=2):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=3y&interval=1wk"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for _ in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.load(r)
            result = data["chart"]["result"][0]
            ts = result["timestamp"]
            closes = result["indicators"]["quote"][0]["close"]
            pairs = [(t, c) for t, c in zip(ts, closes) if c is not None]
            if len(pairs) < 35:
                return None
            return pairs
        except Exception:
            time.sleep(0.4)
    return None


def ema30(closes):
    k = 2 / 31
    e = closes[0]
    vals = [e]
    for c in closes[1:]:
        e = c * k + e * (1 - k)
        vals.append(e)
    return vals


def trailing_return_pct(closes, weeks):
    if len(closes) <= weeks:
        return None
    base = closes[-1 - weeks]
    if not base:
        return None
    return (closes[-1] / base - 1) * 100


def fetch_benchmark_return():
    """Nifty 500's own trailing RS_LOOKBACK_WEEKS return, fetched once per run."""
    pairs = yahoo_chart(BENCHMARK_SYMBOL)
    if not pairs:
        return None
    closes = [c for t, c in pairs]
    return trailing_return_pct(closes, RS_LOOKBACK_WEEKS)


def technical_read(name, slug=None):
    # 1. verified symbol map wins — skips the fragile name search entirely.
    if slug is not None and slug in SYMBOL_MAP:
        mapped = SYMBOL_MAP[slug]
        if mapped is None:
            return {"status": "no_history_sme"}  # known: no Yahoo weekly series
        pairs = yahoo_chart(mapped)
        if not pairs:
            return {"status": "no_data", "symbol": mapped}
        return _read_from_pairs(mapped, pairs)

    # 2. fall back to the live name search.
    sd = yahoo_search(clean_name(name))
    sym = None
    if sd and sd.get("quotes"):
        for q in sd["quotes"]:
            if q.get("symbol", "").endswith(".NS"):
                sym = q["symbol"]
                break
        if not sym:
            for q in sd["quotes"]:
                if q.get("symbol", "").endswith(".BO"):
                    sym = q["symbol"]
                    break
    if not sym:
        return {"status": "no_symbol"}
    pairs = yahoo_chart(sym)
    if not pairs:
        return {"status": "no_data", "symbol": sym}
    if slug is not None:
        _RESOLVED_BY_SEARCH[slug] = sym  # candidate to promote into SYMBOL_MAP
    return _read_from_pairs(sym, pairs)


def _read_from_pairs(sym, pairs):
    closes = [c for t, c in pairs]
    emas = ema30(closes)
    last_close, last_ema = closes[-1], emas[-1]
    pct = (last_close / last_ema - 1) * 100
    cross_weeks_ago = None
    for j in range(len(closes) - 1, max(len(closes) - 13, 0), -1):
        if (closes[j - 1] > emas[j - 1]) != (closes[j] > emas[j]):
            cross_weeks_ago = len(closes) - 1 - j
            break
    out = {
        "status": "ok", "symbol": sym, "pct_vs_ema": round(pct, 1),
        "above": last_close > last_ema, "cross_weeks_ago": cross_weeks_ago,
    }
    stock_ret_13w = trailing_return_pct(closes, RS_LOOKBACK_WEEKS)
    if stock_ret_13w is not None:
        out["ret_13w_pct"] = round(stock_ret_13w, 1)
        if _BENCHMARK_RETURN_PCT is not None:
            out["rs_pct"] = round(stock_ret_13w - _BENCHMARK_RETURN_PCT, 1)
    stock_ret_26w = trailing_return_pct(closes, MOMENTUM_LOOKBACK_WEEKS_LONG)
    if stock_ret_26w is not None:
        out["ret_26w_pct"] = round(stock_ret_26w, 1)
    return out


def technical_score(t):
    """0-100 read of 30W-EMA trend quality — replaces the old small additive
    tech_adjustment delta with a real sub-score so FUND/TECH/MOMENTUM_WEIGHT are a
    literal blend, not fundamentals-plus-a-nudge. Unresolved reads get a neutral-low
    40 (not a harsh penalty) since a data gap isn't evidence of a bad trend."""
    if t.get("status") != "ok":
        return 40
    pct = t["pct_vs_ema"]
    cwa = t.get("cross_weeks_ago")
    if not t["above"]:
        return 15
    if cwa is not None and cwa <= 3:
        return 90  # fresh bullish cross
    if pct <= 15:
        return 82  # tight cushion on an established uptrend
    if pct <= 30:
        return 68
    if pct <= 45:
        return 52
    return 30  # very extended (>45%) — poor risk-reward to buy into, not a red flag


def tech_str(t):
    if t.get("status") == "ok":
        s = f"{'Above' if t['above'] else 'Below'} 30W-EMA {t['pct_vs_ema']:+.1f}%"
        if t.get("cross_weeks_ago") is not None:
            s += f" (cross {t['cross_weeks_ago']}w ago)"
        if t.get("stale_days") is not None:
            s += f" [cached, {t['stale_days']}d old — live refetch failed this run]"
        return s
    if t.get("status") == "no_history_sme":
        return "No weekly series (SME listing)"
    return "Not resolved"


def momentum_score(t):
    """0-100 momentum read (2026-09-22, new factor): blends absolute trailing price
    return (13w + 26w, the same two windows swing_screen.py uses) with relative
    strength vs the Nifty 500 — orthogonal to technical_score, which reads trend
    *quality* (distance/freshness vs the 30W EMA) rather than raw return magnitude.
    A stock can be a fresh EMA cross with modest absolute momentum, or a strong
    absolute-momentum name that's simply always traded above its EMA; this catches
    the latter. Missing data reads neutral (50), never penalized."""
    r13, r26 = t.get("ret_13w_pct"), t.get("ret_26w_pct")
    abs_vals = [v for v in (r13, r26) if v is not None]
    abs_component = _return_ladder(sum(abs_vals) / len(abs_vals)) if abs_vals else 50
    rs_component = _rs_ladder(t.get("rs_pct"))
    return round(0.65 * abs_component + 0.35 * rs_component)


def _return_ladder(pct):
    if pct >= 60:
        return 95
    if pct >= 30:
        return 85
    if pct >= 15:
        return 72
    if pct >= 0:
        return 58
    if pct >= -15:
        return 40
    if pct >= -30:
        return 22
    return 10


def _rs_ladder(rs):
    if rs is None:
        return 50
    if rs >= 15:
        return 90
    if rs > 0:
        return 68
    if rs > -10:
        return 45
    return 20


def rs_str(t):
    rs = t.get("rs_pct")
    if rs is None:
        return "RS not resolved"
    return f"RS {rs:+.1f}pp vs {BENCHMARK_LABEL} ({RS_LOOKBACK_WEEKS}w)"


def momentum_str(t):
    r13, r26 = t.get("ret_13w_pct"), t.get("ret_26w_pct")
    if r13 is None and r26 is None:
        return "Momentum not resolved"
    parts = []
    if r13 is not None:
        parts.append(f"{r13:+.1f}% (13w)")
    if r26 is not None:
        parts.append(f"{r26:+.1f}% (26w)")
    return " / ".join(parts)


def current_holdings():
    """Names in the live Rs 1L allocation, for the HOLD badge. Falls back to an
    empty set on any read/parse failure rather than erroring the whole build.

    2026-09-22: the allocation's source of truth moved to
    data/confluence100_allocation.json (build_confluence100_allocation.py, run
    right after this script by vpscreen-rerank) — Confluence-100 now drives the
    portfolio instead of merely cross-referencing it. Falls back to the legacy
    portfolio/FINAL_PORTFOLIO_RECOMMENDATION.md doc (written by the
    portfolio-rs1l-revision job, which is being retired) only until the new
    allocation file exists for the first time."""
    alloc_path = os.path.join(DATA_DIR, "confluence100_allocation.json")
    try:
        alloc = load_json(alloc_path)
        return {h["name"] for h in alloc.get("holdings", [])}
    except (OSError, json.JSONDecodeError, KeyError):
        pass

    path = os.path.join(ROOT, "portfolio", "FINAL_PORTFOLIO_RECOMMENDATION.md")
    try:
        text = open(path).read()
    except OSError:
        return set()
    m = re.search(r"## 3\. Final Rs 1,00,000 allocation(.*?)\n---", text, re.S)
    if not m:
        return set()
    names = set()
    for line in m.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        first = cells[0].replace("*", "").strip()
        if not first or first.lower().startswith(("stock", "---", "cash buffer", "total")):
            continue
        if first.startswith("~~"):  # exited, struck through
            continue
        names.add(clean_name(first))
    return names


def investable_now(x):
    """Hard data-completeness AND entry-timing gate, independent of confidence_pct
    — see INVESTABLE_COV_THRESHOLD above. Returns (bool, reason_if_not).

    2026-09-22: also requires the name to currently sit above its own 30W EMA —
    "ready to invest today" now means the same thing the standing per-name EMA
    discipline always has: never buy into a name below its own trend line, no
    matter how strong the fundamentals. This is what lets the Rs 1L allocation
    (build_confluence100_allocation.py) consume top10_investable directly without
    a second, separate technical filter."""
    cov = x["sb"].get("weight_coverage") or 0.0
    tech_status = x["tech"].get("status")
    if cov < INVESTABLE_COV_THRESHOLD and tech_status not in INVESTABLE_TECH_STATUSES:
        return False, "needs quality/consistency data + a resolved technical read"
    if cov < INVESTABLE_COV_THRESHOLD:
        return False, "needs quality/consistency data (thin master-score coverage)"
    if tech_status == "no_history_sme":
        # Confirmed SME/Emerge names are excluded in build_universe() before
        # reaching here (see is_sme_emerge), so this status now only fires for
        # a genuine main-board stock too recently listed for 35+ weekly bars.
        return False, "no technical read possible (too-recent a listing for 35+ weekly bars)"
    if tech_status not in INVESTABLE_TECH_STATUSES:
        return False, "technical not resolved (needs a verified Yahoo symbol)"
    if tech_status == "ok" and not x["tech"].get("above"):
        return False, "below its own 30W EMA — fails entry-timing discipline regardless of score"
    return True, ""


def make_rows(ordered, holdings):
    rows = []
    for i, x in enumerate(ordered):
        sb = x["sb"]
        name = clean_name(x["name"])
        ready, not_ready_reason = investable_now(x)
        rows.append({
            "rank": i + 1,
            "name": name,
            "slug": x["slug"],
            "confidence": x["confidence_pct"],
            "master_score": round(x["master_score"], 1),
            "conviction_score": sb.get("conviction_score"),
            "quality_score": sb.get("quality_score"),
            "expectation_gap_score": sb.get("expectation_gap_score"),
            "asymmetry_score": sb.get("asymmetry_score"),
            "four_box_score": x.get("four_box_score"),
            "weight_coverage": sb.get("weight_coverage"),
            "conviction_label": x.get("conviction_label"),
            "market_cap_tier": x.get("market_cap_tier"),
            "thesis_fit": x.get("thesis_fit") or "neither",
            "thesis_eligible": bool(x.get("thesis_eligible")),
            "tagline": (x.get("tagline") or "")[:160],
            "symbol": x["tech"].get("symbol"),
            "technical": tech_str(x["tech"]),
            "relative_strength": rs_str(x["tech"]),
            "rs_pct": x["tech"].get("rs_pct"),
            "momentum": momentum_str(x["tech"]),
            "ret_13w_pct": x["tech"].get("ret_13w_pct"),
            "ret_26w_pct": x["tech"].get("ret_26w_pct"),
            "fundamental_score": round(x["blended_fundamental"], 1),
            "technical_score": x["technical_score_val"],
            "momentum_score": x["momentum_score_val"],
            "above_ema": x["tech"].get("above"),
            "pct_vs_ema": x["tech"].get("pct_vs_ema"),
            "investable_now": ready,
            "not_ready_reason": not_ready_reason,
            "in_current_portfolio": name in holdings,
        })
    return rows


def main():
    universe, total_deepdived, excluded_sme_emerge = build_universe()
    for x in universe:
        x["blended_fundamental"] = blend_fundamental(x)
    universe.sort(key=lambda x: -x["blended_fundamental"])

    full_coverage_count = sum(1 for x in universe if x["sb"]["weight_coverage"] >= 0.85)
    thesis_universe_count = sum(1 for x in universe if x["thesis_eligible"])

    # Scan the union of (overall top buffer) and (thesis-eligible top buffer) so
    # both rankings have live technicals for every name that could land in their
    # top 100. Thesis-eligible is a subset, but its members can rank lower on the
    # blended fundamental than the overall cut, so scan them explicitly.
    overall_head = universe[:TECH_SCAN_BUFFER]
    thesis_head = [x for x in universe if x["thesis_eligible"]][:TECH_SCAN_BUFFER]
    scan = list({id(x): x for x in overall_head + thesis_head}.values())

    today = datetime.date.today()
    today_iso = today.isoformat()
    cache = load_cache()

    # Only the top TOP_FRESH_N by fundamental score get a mandatory live pull
    # every run — everyone else rides the cache until it's CACHE_TTL_DAYS old.
    top_fresh_slugs = {x["slug"] for x in universe[:TOP_FRESH_N]}

    global _BENCHMARK_RETURN_PCT
    _BENCHMARK_RETURN_PCT = fetch_benchmark_return()
    if _BENCHMARK_RETURN_PCT is not None:
        cache["benchmark"] = {"return_pct": _BENCHMARK_RETURN_PCT, "fetched_at": today_iso}
        print(f"{BENCHMARK_LABEL} trailing {RS_LOOKBACK_WEEKS}w return: "
              f"{_BENCHMARK_RETURN_PCT:+.1f}% (live)", file=sys.stderr)
    elif cache.get("benchmark"):
        _BENCHMARK_RETURN_PCT = cache["benchmark"]["return_pct"]
        age = days_since(cache["benchmark"]["fetched_at"], today)
        print(f"WARNING: live {BENCHMARK_LABEL} pull failed — using cached return "
              f"{_BENCHMARK_RETURN_PCT:+.1f}% from {age if age is not None else '?'}d ago.",
              file=sys.stderr)
    else:
        print(f"WARNING: could not fetch {BENCHMARK_SYMBOL} ({BENCHMARK_LABEL}) and no cached "
              f"fallback exists — relative-strength adjustment will be skipped this run.",
              file=sys.stderr)

    print(f"Technical scan for {len(scan)} candidates "
          f"({len(overall_head)} overall-head + {len(thesis_head)} thesis-head, deduped): "
          f"top {min(TOP_FRESH_N, len(scan))} by fundamentals always live, rest cached "
          f"up to {CACHE_TTL_DAYS}d old...", file=sys.stderr)

    live_n = cache_hit_n = stale_fallback_n = 0
    for i, x in enumerate(scan):
        slug = x["slug"]
        cached = cache["stocks"].get(slug)
        cache_age = days_since(cached["fetched_at"], today) if cached else None
        need_live = slug in top_fresh_slugs or cached is None or (
            cache_age is not None and cache_age >= CACHE_TTL_DAYS)

        if need_live:
            tech = technical_read(x["name"], slug)
            live_n += 1
            if tech.get("status") == "ok":
                cache["stocks"][slug] = tech_to_cache_entry(tech, today_iso)
            elif cached and cached.get("status") == "ok":
                # Live fetch failed (network/rate-limit/renamed ticker) — a stale
                # known-good read beats a blank one. Cache itself is left untouched
                # so a transient failure doesn't erase the last good fetch date.
                tech = cache_entry_to_tech(cached)
                tech["stale_days"] = cache_age
                stale_fallback_n += 1
        else:
            tech = cache_entry_to_tech(cached)
            cache_hit_n += 1

        x["tech"] = tech
        if i % 20 == 0:
            print(f"  ...{i}/{len(scan)}", file=sys.stderr)

    print(f"Technical scan done: {live_n} live fetch(es), {cache_hit_n} cache hit(s) "
          f"(<{CACHE_TTL_DAYS}d old), {stale_fallback_n} fell back to a stale cached read "
          f"after a failed live refetch.", file=sys.stderr)

    # Save whatever resolved, before the quality gate — a partially-successful run
    # (e.g. half the top-20 pulled fine before a rate-limit kicked in) shouldn't
    # lose the reads it did get, even if the run aborts below.
    save_cache(cache)

    resolved_n = sum(1 for x in scan if x["tech"].get("status") in ("ok", "no_history_sme"))
    resolved_frac = resolved_n / len(scan) if scan else 1.0
    if resolved_frac < MIN_RESOLVED_FRACTION:
        print(f"\nABORT: only {resolved_n}/{len(scan)} ({resolved_frac:.0%}) candidates resolved "
              f"(live or cached) — below the {MIN_RESOLVED_FRACTION:.0%} safety floor. This "
              f"usually means Yahoo Finance access is broadly broken in this environment "
              f"(network/rate-limit), not that 100+ tickers all vanished at once. NOT touching "
              f"artifacts/confluence100.artifact.html or data/confluence100.json — the last "
              f"known-good build stays live. (Cache was still saved with anything that did "
              f"resolve, so the next run starts from a better position.)", file=sys.stderr)
        sys.exit(1)

    for x in scan:
        x["technical_score_val"] = technical_score(x["tech"])
        x["momentum_score_val"] = momentum_score(x["tech"])
        x["confidence_pct"] = round(max(5, min(96,
            FUND_WEIGHT * x["blended_fundamental"]
            + TECH_WEIGHT * x["technical_score_val"]
            + MOMENTUM_WEIGHT * x["momentum_score_val"]
        )))

    holdings = current_holdings()

    overall_sorted = sorted(scan, key=lambda x: (-x["confidence_pct"], -x["blended_fundamental"]))
    rows_overall = make_rows(overall_sorted[:TOP_N], holdings)

    thesis_sorted = sorted(
        [x for x in scan if x["thesis_eligible"]],
        key=lambda x: (-x["confidence_pct"], -x["blended_fundamental"]),
    )
    rows_thesis = make_rows(thesis_sorted[:TOP_N], holdings)

    # The single actionable cut: "if I bought today, what would I actually
    # buy" — confidence-ranked, but ONLY from names that pass the investable_now
    # data-completeness gate (see investable_now() above). Drawn from the Overall
    # ranking (any thesis_fit) since a fairly-priced, rising, high-quality
    # non-thesis name is a legitimate buy today even if it'll never be a 10x.
    top10_investable = [r for r in rows_overall if r["investable_now"]][:TOP10_N]
    # Near-misses: highest-confidence names the gate is currently excluding —
    # surfaced so it's visible what a coverage/technical backfill would unlock,
    # not just silently dropped from the actionable list.
    near_miss_investable = [
        r for r in rows_overall if not r["investable_now"]
    ][: max(0, TOP10_N)]

    stats = {
        "total_deepdived": total_deepdived,
        "excluded_sme_emerge": excluded_sme_emerge,
        "eligible_overall": len(universe),
        "eligible_thesis": thesis_universe_count,
        # kept for backward compat with older template copies
        "eligible_count": thesis_universe_count,
        "full_coverage_count": full_coverage_count,
        "investable_now_count": sum(1 for r in rows_overall if r["investable_now"]),
        "asof_date": datetime.datetime.now().strftime("%-d %b %Y"),
    }

    template_path = os.path.join(ARTIFACTS_DIR, "confluence100_template.html")
    html = open(template_path).read()
    html = html.replace("__ROWS_OVERALL_JSON__", json.dumps(rows_overall, ensure_ascii=False))
    html = html.replace("__ROWS_THESIS_JSON__", json.dumps(rows_thesis, ensure_ascii=False))
    html = html.replace("__TOP10_JSON__", json.dumps(top10_investable, ensure_ascii=False))
    html = html.replace("__NEARMISS_JSON__", json.dumps(near_miss_investable, ensure_ascii=False))
    html = html.replace("__STATS_JSON__", json.dumps(stats, ensure_ascii=False))
    html = html.replace("__ASOF_DATE__", stats["asof_date"])

    # Atomic writes (temp file + os.replace): the quality gate above already keeps
    # a bad run from reaching here, but this also protects against a crash or kill
    # mid-write leaving a truncated/corrupt file behind.
    out_path = os.path.join(ARTIFACTS_DIR, "confluence100.artifact.html")
    atomic_write(out_path, html)

    # Machine-readable sidecar — consumed by build_deepdive_queue.py to prioritize
    # deep-dive coverage of current Confluence-100 membership. `rows` keeps the
    # union of both lists (deduped by slug) so a name in either ranking counts.
    seen, union = set(), []
    for r in rows_overall + rows_thesis:
        if r["slug"] in seen:
            continue
        seen.add(r["slug"])
        union.append(r)
    json_path = os.path.join(DATA_DIR, "confluence100.json")
    atomic_write(json_path, json.dumps({
        "generated": stats["asof_date"],
        "rows": union,
        "rows_overall": rows_overall,
        "rows_thesis": rows_thesis,
        "top10_investable": top10_investable,
        "near_miss_investable": near_miss_investable,
        "investable_now_count": stats["investable_now_count"],
    }, indent=2, ensure_ascii=False))

    res_o = sum(1 for x in overall_sorted[:TOP_N] if x["tech"].get("status") == "ok")
    res_t = sum(1 for x in thesis_sorted[:TOP_N] if x["tech"].get("status") == "ok")
    if _RESOLVED_BY_SEARCH:
        print(f"\n{len(_RESOLVED_BY_SEARCH)} name(s) resolved by live search (not in "
              f"yahoo_symbol_map.json) — verify and promote the good ones into the map:")
        for slug, sym in sorted(_RESOLVED_BY_SEARCH.items()):
            print(f'    "{slug}": "{sym}",')
    unresolved = sorted(
        x["slug"] for x in scan
        if x["tech"].get("status") not in ("ok", "no_history_sme")
    )
    if unresolved:
        print(f"\n{len(unresolved)} name(s) still unresolved (no map entry, search failed) — "
              f"need a hand-checked symbol or a null map entry if genuinely SME/unlisted:")
        for slug in unresolved:
            print(f"    {slug}")
    print()
    print(f"Wrote {out_path}")
    print(f"Wrote {json_path}")
    print(f"Universe: {total_deepdived} deepdived, {excluded_sme_emerge} excluded as SME/Emerge "
          f"(is_sme_emerge tag), {len(universe)} no-red-flag "
          f"({thesis_universe_count} also thesis-eligible), {full_coverage_count} fully cross-scored.")
    print(f"Overall 100: {res_o}/{TOP_N} technicals resolved. "
          f"Thesis 100: {res_t}/{TOP_N} technicals resolved. "
          f"Union sidecar: {len(union)} unique names, "
          f"{sum(1 for r in union if r['in_current_portfolio'])} flagged as current holdings.")
    print(f"\nInvestable-now gate (cov>={INVESTABLE_COV_THRESHOLD}, resolved technical): "
          f"{stats['investable_now_count']}/{len(rows_overall)} of the Overall 100 pass. "
          f"Top {len(top10_investable)}:")
    for r in top10_investable:
        print(f"    {r['confidence']:3d}%  {r['name']}")
    if near_miss_investable[:5]:
        print(f"  Highest-confidence names the gate is currently excluding "
              f"(would need backfill to qualify):")
        for r in near_miss_investable[:5]:
            print(f"    {r['confidence']:3d}%  {r['name']:40s} — {r['not_ready_reason']}")
    print(f"Cache economics: {live_n} live Yahoo fetches this run "
          f"(top {TOP_FRESH_N} fundamentals + any cache miss/expiry), {cache_hit_n} served "
          f"from cache (<{CACHE_TTL_DAYS}d old), {stale_fallback_n} stale-fallback saves. "
          f"Cache: {CACHE_PATH}")


if __name__ == "__main__":
    main()
