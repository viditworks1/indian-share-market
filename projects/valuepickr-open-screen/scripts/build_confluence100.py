#!/usr/bin/env python3
"""
Builds the Confluence 100 artifact: the top 100 ValuePickr-screen stocks by a
confidence-adjusted blend of master_score (conviction/quality/expectation-gap/
asymmetry) and a live 30-week EMA technical read.

Run as a weekly side job of vpscreen-rerank (see that task's SKILL.md Step 7).
Writes projects/valuepickr-open-screen/artifacts/confluence100.artifact.html —
the scheduled task then publishes that file with the Artifact tool using the
fixed URL recorded in vpscreen-rerank/SKILL.md.

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

ELIGIBLE_THESIS = ("10x-in-2-3-years", "100x-in-10-years")


def load_json(path):
    with open(path) as f:
        return json.load(f)


def build_universe():
    d = load_json(os.path.join(DATA_DIR, "master-scores.json"))
    ranked = d["ranked"]
    elig = [
        x for x in ranked
        if x.get("thesis_fit") in ELIGIBLE_THESIS and x.get("red_flag_tier") in (None, "")
    ]
    out = []
    for x in elig:
        slug = x["slug"]
        path = resolve_data_path(BASE, DATA_DIR, slug)
        rec = {
            "slug": slug,
            "name": x["name"],
            "master_score": x["master_score"],
            "conviction_label": x["conviction"],
            "thesis_fit": x["thesis_fit"],
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
    return out, len(ranked)


def blend_fundamental(x):
    cov = x["sb"]["weight_coverage"]
    fb = x.get("four_box_score")
    fb_pct = (fb / 5 * 100) if fb is not None else x["master_score"]
    w_master = 0.4 + 0.6 * cov
    return round(w_master * x["master_score"] + (1 - w_master) * fb_pct, 2)


def clean_name(name):
    n = re.split(r"[:(–—-]", name)[0].strip()
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


def technical_read(name):
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
    closes = [c for t, c in pairs]
    emas = ema30(closes)
    last_close, last_ema = closes[-1], emas[-1]
    pct = (last_close / last_ema - 1) * 100
    cross_weeks_ago = None
    for j in range(len(closes) - 1, max(len(closes) - 13, 0), -1):
        if (closes[j - 1] > emas[j - 1]) != (closes[j] > emas[j]):
            cross_weeks_ago = len(closes) - 1 - j
            break
    return {
        "status": "ok", "symbol": sym, "pct_vs_ema": round(pct, 1),
        "above": last_close > last_ema, "cross_weeks_ago": cross_weeks_ago,
    }


def tech_adjustment(t):
    if t.get("status") != "ok":
        return -2
    pct = t["pct_vs_ema"]
    cwa = t.get("cross_weeks_ago")
    if not t["above"]:
        return -18
    if cwa is not None and cwa <= 3:
        return 10
    if pct <= 15:
        return 8
    if pct <= 30:
        return 4
    if pct <= 45:
        return 0
    return -6


def tech_str(t):
    if t.get("status") == "ok":
        s = f"{'Above' if t['above'] else 'Below'} 30W-EMA {t['pct_vs_ema']:+.1f}%"
        if t.get("cross_weeks_ago") is not None:
            s += f" (cross {t['cross_weeks_ago']}w ago)"
        return s
    return "Not resolved"


def current_holdings():
    """Best-effort parse of portfolio/FINAL_PORTFOLIO_RECOMMENDATION.md Section 3
    allocation table for the HOLD badge. Falls back to an empty set on any
    parse failure rather than erroring the whole build."""
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


def main():
    universe, total_deepdived = build_universe()
    for x in universe:
        x["blended_fundamental"] = blend_fundamental(x)
    universe.sort(key=lambda x: -x["blended_fundamental"])

    full_coverage_count = sum(1 for x in universe if x["sb"]["weight_coverage"] >= 0.85)

    top = universe[:TECH_SCAN_BUFFER]
    print(f"Running live technical scan for {len(top)} candidates...", file=sys.stderr)
    for i, x in enumerate(top):
        x["tech"] = technical_read(x["name"])
        if i % 20 == 0:
            print(f"  ...{i}/{len(top)}", file=sys.stderr)

    for x in top:
        adj = tech_adjustment(x["tech"])
        x["tech_adj"] = adj
        x["confidence_pct"] = round(max(5, min(96, x["blended_fundamental"] + adj)))

    top.sort(key=lambda x: (-x["confidence_pct"], -x["blended_fundamental"]))
    final = top[:TOP_N]

    holdings = current_holdings()

    rows = []
    for i, x in enumerate(final):
        sb = x["sb"]
        name = clean_name(x["name"])
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
            "tagline": (x.get("tagline") or "")[:160],
            "technical": tech_str(x["tech"]),
            "in_current_portfolio": name in holdings,
        })

    stats = {
        "total_deepdived": total_deepdived,
        "eligible_count": len(universe),
        "full_coverage_count": full_coverage_count,
        "asof_date": datetime.datetime.now().strftime("%-d %b %Y"),
    }

    template_path = os.path.join(ARTIFACTS_DIR, "confluence100_template.html")
    html = open(template_path).read()
    html = html.replace("__ROWS_JSON__", json.dumps(rows, ensure_ascii=False))
    html = html.replace("__STATS_JSON__", json.dumps(stats, ensure_ascii=False))
    html = html.replace("__ASOF_DATE__", stats["asof_date"])

    out_path = os.path.join(ARTIFACTS_DIR, "confluence100.artifact.html")
    with open(out_path, "w") as f:
        f.write(html)

    # Machine-readable sidecar (slugs + ranks) — consumed by build_deepdive_queue.py
    # to prioritize deep-dive coverage of the current Confluence 100 membership.
    json_path = os.path.join(DATA_DIR, "confluence100.json")
    with open(json_path, "w") as f:
        json.dump({"generated": stats["asof_date"], "rows": rows}, f, indent=2, ensure_ascii=False)

    resolved = sum(1 for x in final if x["tech"].get("status") == "ok")
    print(f"Wrote {out_path}")
    print(f"Wrote {json_path}")
    print(f"Universe: {total_deepdived} deepdived, {len(universe)} eligible, "
          f"{full_coverage_count} fully cross-scored.")
    print(f"Top {TOP_N}: {resolved}/{TOP_N} technicals resolved, "
          f"{sum(1 for r in rows if r['in_current_portfolio'])} flagged as current holdings.")


if __name__ == "__main__":
    main()
