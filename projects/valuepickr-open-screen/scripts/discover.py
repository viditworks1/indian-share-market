#!/usr/bin/env python3
"""
Mechanical ValuePickr discovery + triage - does Phases 1-3 of the scan funnel
with ZERO LLM tool-call overhead (one Python process, N cheap HTTP calls via
urllib, no agent loop). The scheduled task / live session just runs this once
and reads the compact report; it only needs its own tool calls (WebSearch /
individual post fetch) for the small "go deeper" shortlist this prints.

What it does:
1. Pages through the given Discourse categories (default: Stock Opportunities
   id=11, Stock Analysis & Valuation id=14) via the public JSON API until
   topics cross the 30-day activity cutoff.
2. Filters out obviously non-single-company threads (portfolio-review threads,
   meta/FAQ, generic personal-finance Q&A) via a title blacklist.
3. Upserts every surviving topic into state.json's stock registry (by topic
   id - stable even if title changes), tracking last_forum_activity,
   reply_count, and a "flagged_material" bool from an excerpt keyword scan.
4. Applies the 30-day cooldown: a stock whose last_analyzed_date is within
   the cooldown is NOT included in the actionable report (skip logic).
5. Prints a compact, prioritized report (flagged-material first, then by
   reply_count) capped to --limit entries - this is what an agent should
   read, not the full state.json.

Usage:
  python3 discover.py                  # scan + upsert + print report
  python3 discover.py --limit 40       # cap the printed actionable list
  python3 discover.py --max-pages 15   # safety cap on pagination per category
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")

CATEGORIES = [
    (11, "stock-opportunities"),
    (14, "stock-analysis-valuation"),
    (17, "stock-screening"),
]
COOLDOWN_DAYS = 30
FORUM_ACTIVITY_WINDOW_DAYS = 30

# Statuses that permanently remove a thread from the actionable report. "not-a-stock"
# is the manual disposition for a generic / sector / theme / book / methodology
# thread that never resolves to a single company (set by the scan skill or by
# tools/mark_not_a_stock.py). Without this, such a thread reappears as "actionable"
# every run because a busy thread never leaves the 30-day window and a
# never-researched thread never gets a last_analyzed_date.
TERMINAL_SKIP_STATUSES = {"not-a-stock"}

# A candidate that has been in the registry this long without ever being analyzed
# is quarantined into a separate "stale - needs disposition" section instead of
# consuming a research slot in the main actionable list.
STALE_CANDIDATE_DAYS = 45

TITLE_BLACKLIST = [
    "about the", "faq", "guideline", "welcome to valuepickr", "portfolio review",
    "my portfolio", "our portfolio", "beginner", "which bank", "nri", "mutual fund",
    "ppf", "meetup", "meet up", "conference", "housekeeping", "forum abuse",
    "content suggestion", "job openings", "expert network", "annual vp",
    "city meets", "productivity", "tech requirement",
    # generic / sector / theme / book / methodology threads that never resolve to
    # one company - they otherwise resurface as "actionable" every run forever
    # because a busy thread never leaves the 30-day window and never gets a
    # last_analyzed_date (see also TITLE_BLACKLIST_REGEX and status=not-a-stock).
    "deep value portfolio", "reminiscences", "valuation of holdcos",
    "investing basics", "the gcc opportunity", "cpu/gpu",
]

# Higher-precision patterns for non-company threads. Kept deliberately tight
# (anchored / requires the non-company phrase to dominate the title) so a real
# company thread whose tagline merely contains "sector" or "cycle" is NOT caught
# - e.g. "Exicom Tele-Services: ... the Booming EV Sector" must pass through.
# The stale-candidate quarantine below is the backstop for anything that slips by.
TITLE_BLACKLIST_REGEX = [
    r"^(the\s+)?[a-z&/ .-]{2,28} sector( thread)?\s*$",  # "Logistics sector", "The auto sector"
    r"\bcycles?\s*[:\-]\s",                              # "Sugar Cycles: ...", "Commodity cycle - "
    r"\bcompanies\s+(with|which|that|having|where)\b",   # screener-list threads
    r"^\s*list of\b",                                    # "List of ..." index threads
    r"\b(19|20)\d0\b.*\b(compounder|structural|generation|vision|megatrend)\b",  # "India 2040 - ..."
]

MATERIAL_KEYWORDS = [
    "result", "earnings", "order win", "order book", "promoter", "pledge", "stake",
    "sebi", "downgrade", "upgrade", "buyback", "acquisition", "merger", "delist",
    "resign", "rights issue", "qip", "block deal", "guidance", "dividend", "bonus",
    "split", "litigation", "fraud", "credit rating", "raid", "scam", "insider",
]


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def slugify(name):
    n = re.sub(r"\s*\([^)]*\)", "", name)
    n = re.sub(r"[-–|].*$", "", n)  # keep only text before first separator
    n = re.sub(r"\b(Ltd|Limited|Pvt|Corporation|Corp)\.?$", "", n.strip())
    s = re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")
    return s or "unknown"


def is_blacklisted(title):
    t = title.lower()
    if any(b in t for b in TITLE_BLACKLIST):
        return True
    return any(re.search(rx, t) for rx in TITLE_BLACKLIST_REGEX)


def scan_excerpt(excerpt):
    if not excerpt:
        return False
    e = excerpt.lower()
    return any(k in e for k in MATERIAL_KEYWORDS)


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {
        "meta": {"categories_watched": [c for c, _ in CATEGORIES],
                  "cooldown_days": COOLDOWN_DAYS, "last_discover_run": None,
                  "last_ranking_date": None},
        "stocks": {},
    }


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--max-pages", type=int, default=15)
    args = ap.parse_args()

    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=FORUM_ACTIVITY_WINDOW_DAYS)
    state = load_state()
    stocks = state["stocks"]

    by_topic_id = {v.get("topic_id"): k for k, v in stocks.items() if v.get("topic_id")}

    total_seen, total_blacklisted, total_new, total_not_a_stock = 0, 0, 0, 0

    for cat_id, cat_slug in CATEGORIES:
        page = 0
        while page < args.max_pages:
            url = f"https://forum.valuepickr.com/c/{cat_slug}/{cat_id}.json?page={page}"
            try:
                d = fetch_json(url)
            except Exception as e:
                print(f"WARN: fetch failed for {url}: {e}", file=sys.stderr)
                break
            topics = d.get("topic_list", {}).get("topics", [])
            if not topics:
                break
            # Pinned topics (e.g. category "About" threads) can carry very old
            # last_posted_at while still sorting first on the page - only the
            # LAST topic on the page (the actual oldest by activity) should
            # decide whether we've paged past the 30-day window.
            last_on_page = datetime.datetime.fromisoformat(
                topics[-1]["last_posted_at"].replace("Z", "+00:00")
            ).date()
            crossed_cutoff = last_on_page < cutoff

            for t in topics:
                total_seen += 1
                last_posted = datetime.datetime.fromisoformat(
                    t["last_posted_at"].replace("Z", "+00:00")
                ).date()
                if last_posted < cutoff:
                    continue
                title = t["title"]
                if is_blacklisted(title):
                    total_blacklisted += 1
                    continue

                topic_id = t["id"]
                slug = by_topic_id.get(topic_id) or slugify(title)
                if slug in stocks and stocks[slug].get("status") in TERMINAL_SKIP_STATUSES:
                    total_not_a_stock += 1
                    continue  # permanently disposed - don't re-flag or re-surface
                is_new = slug not in stocks
                if is_new:
                    total_new += 1
                    stocks[slug] = {
                        "name": title.split(" - ")[0].split(" – ")[0].strip(),
                        "raw_title": title,
                        "topic_id": topic_id,
                        "topic_slug": t["slug"],
                        "category_id": cat_id,
                        "first_seen_date": today.isoformat(),
                        "last_analyzed_date": None,
                        "last_reply_count_analyzed": None,
                        "status": "candidate",
                        "conviction": None,
                        "market_cap_tier": None,
                        "notes_short": None,
                    }
                    by_topic_id[topic_id] = slug
                entry = stocks[slug]
                entry["last_forum_activity"] = last_posted.isoformat()
                entry["reply_count"] = t.get("reply_count", 0)
                entry["flagged_material"] = scan_excerpt(t.get("excerpt", ""))
                entry["excerpt"] = (t.get("excerpt") or "")[:280]
                entry["highest_post_number"] = t.get("highest_post_number")
                entry["topic_id"] = topic_id
                entry["topic_slug"] = t["slug"]
            page += 1
            time.sleep(1.5)
            if crossed_cutoff:
                break

    # Build the actionable report: cooldown-eligible, prioritized
    actionable = []
    stale_candidates = []
    on_cooldown = 0
    skipped_terminal = 0
    for slug, e in stocks.items():
        if e.get("status") in TERMINAL_SKIP_STATUSES:
            skipped_terminal += 1
            continue  # permanently disposed (e.g. not-a-stock)
        if e.get("last_forum_activity") and e["last_forum_activity"] < cutoff.isoformat():
            continue  # stale thread, not part of this run's active window
        last_analyzed = e.get("last_analyzed_date")
        if last_analyzed:
            days_since = (today - datetime.date.fromisoformat(last_analyzed)).days
            if days_since < COOLDOWN_DAYS:
                on_cooldown += 1
                continue
        # Never-analyzed candidate that has lingered in the registry too long:
        # quarantine it for one-time human/agent disposition instead of letting it
        # eat a research slot every run.
        first_seen = e.get("first_seen_date")
        if (not last_analyzed and e.get("status") == "candidate" and first_seen
                and (today - datetime.date.fromisoformat(first_seen)).days >= STALE_CANDIDATE_DAYS):
            stale_candidates.append((slug, e))
            continue
        actionable.append((slug, e))

    # Deliberately NOT sorted by reply_count - that structurally favors huge legacy
    # mega-threads (HDFC Bank, Laurus Labs, ...) over genuinely new/smaller names.
    # Material-news flag first, then most-recently-active as a neutral recency signal
    # that doesn't systematically bias toward already-popular companies. Two stable
    # sorts (Python's sort() is guaranteed stable): recency first, then material-flag
    # on top of it, so recency order is preserved within each flag group.
    actionable.sort(key=lambda item: item[1].get("last_forum_activity") or "", reverse=True)
    actionable.sort(key=lambda item: 0 if item[1].get("flagged_material") else 1)
    shortlist = actionable[: args.limit]

    state["meta"]["last_discover_run"] = today.isoformat()
    save_state(state)

    print(f"=== ValuePickr discover.py report ({today.isoformat()}) ===")
    print(f"Topics seen this run: {total_seen} | blacklisted: {total_blacklisted} | "
          f"not-a-stock (skipped): {total_not_a_stock} | "
          f"new to registry: {total_new} | total registry size: {len(stocks)}")
    print(f"On 30-day cooldown (skipped): {on_cooldown} | "
          f"terminal-status (skipped): {skipped_terminal} | "
          f"actionable now: {len(actionable)} | showing top {len(shortlist)}\n")
    for slug, e in shortlist:
        flag = "[MATERIAL]" if e.get("flagged_material") else "          "
        status = e.get("status", "candidate")
        print(f"{flag} {slug:35s} status={status:11s} replies={e.get('reply_count',0):4d} "
              f"last_activity={e.get('last_forum_activity')}")
        if e.get("excerpt"):
            print(f"           excerpt: {e['excerpt'][:160]}")
    if len(actionable) > len(shortlist):
        print(f"\n...and {len(actionable) - len(shortlist)} more actionable entries not shown "
              f"(raise --limit or let future runs work through the backlog).")

    if stale_candidates:
        print(f"\n--- STALE CANDIDATES: {len(stale_candidates)} never-analyzed threads "
              f">{STALE_CANDIDATE_DAYS}d old - triage once, then set status ---")
        print("    (research it, OR set status=not-a-stock if it is a generic/sector/"
              "theme/book/methodology thread with no single company)")
        for slug, e in sorted(stale_candidates, key=lambda x: x[1].get("first_seen_date") or ""):
            print(f"    {slug:45s} first_seen={e.get('first_seen_date')} "
                  f"replies={e.get('reply_count',0):4d}  {(e.get('raw_title') or '')[:70]}")


if __name__ == "__main__":
    main()
