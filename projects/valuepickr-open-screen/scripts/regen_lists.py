#!/usr/bin/env python3
"""
Regenerates skip-list.md and revisit-list.md from state.json.
Purely mechanical (date math only) - no research judgment. Run after state.json
is updated by a scan, or at the start of the 2-day conviction rerank job.

Usage: python3 regen_lists.py
"""
import json
import datetime
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")
DATA_DIR = os.path.join(BASE, "data")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_data_file import resolve_data_path  # noqa: E402
SKIP_PATH = os.path.join(BASE, "skip-list.md")
REVISIT_PATH = os.path.join(BASE, "revisit-list.md")
XWATCH_PATH = os.path.join(BASE, "x-cluster-watch-list.md")
FOLLOWTHROUGH_PATH = os.path.join(BASE, "conviction-followthrough.md")
GAP_SCORES_PATH = os.path.join(BASE, "data", "expectation-gap-scores.json")

COOLDOWN_DAYS = 30

# --- "conviction without follow-through" thresholds (phreakv6 #330, the Aegis regret:
#     "did all the work in Feb, loved how cheap it was, never bought ... missed the May
#     switch"). A high-conviction call that is then left to age unrefreshed is this
#     project's analogue. Report-only, mechanical - no research judgment. ---
FT_STALE_REVISIT_GRACE_DAYS = 14   # revisit_after_30d flagged but overdue by more than this
FT_STALLED_DEEPDIVE_DAYS = 45      # High/Med-High but deepdive_pass <=1 and this old
FT_STALE_THESIS_DAYS = 60          # last substantive work older than this
FT_STALE_FLOOR_DAYS = 45           # trusted floor active but underlying signal this old


def parse_date(s):
    try:
        return datetime.date.fromisoformat(s) if s else None
    except (ValueError, TypeError):
        return None


def catalyst_calendar_section(today):
    """Returns the '## Catalyst calendar' markdown block, built from
    data/expectation-gap-scores.json's `catalyst_calendar` (written by
    compute_expectation_gap_score.py). Empty string if that file is absent."""
    if not os.path.exists(GAP_SCORES_PATH):
        return ""
    try:
        with open(GAP_SCORES_PATH) as f:
            cal = json.load(f).get("catalyst_calendar", [])
    except (json.JSONDecodeError, OSError):
        return ""

    lines = [
        "## Catalyst calendar\n",
        "Dated re-rating events behind the expectation-gap thesis for each guidance-assessed "
        "stock (from `data/expectation-gap-scores.json`, itself from each stock's `catalyst` "
        "block). `target_date` = `window_start` + `expected_window_months`. Rows past their "
        "date with status still pending are the ones to actively re-check — a lapsed catalyst "
        "zeroes that stock's catalyst term until the next deep-dive refreshes it. "
        "Regenerated mechanically - do not hand-edit.\n",
    ]
    if not cal:
        lines.append("_(none — no guidance-assessed stock has a dated catalyst yet)_\n")
        return "\n".join(lines) + "\n"

    overdue = [c for c in cal if c.get("target_date") and parse_date(c["target_date"]) and parse_date(c["target_date"]) <= today]
    upcoming = [c for c in cal if c.get("target_date") and parse_date(c["target_date"]) and parse_date(c["target_date"]) > today]
    undated = [c for c in cal if not c.get("target_date") or not parse_date(c.get("target_date"))]

    def rows(items):
        out = ["| Stock | Target date | Window | Status | Gap score | Event |",
               "|---|---|---|---|---|---|"]
        for c in items:
            ev = (c.get("event") or "").replace("|", "/").strip()
            if len(ev) > 160:
                ev = ev[:157] + "..."
            wm = c.get("window_months")
            out.append(
                f"| {c.get('name','?')} | {c.get('target_date') or '—'} | "
                f"{('~' + str(wm) + 'M') if wm is not None else '—'} | "
                f"{c.get('status_effective') or '—'} | "
                f"{c.get('expectation_gap_score', '—')} | {ev} |"
            )
        return "\n".join(out) + "\n"

    lines.append("### Overdue / due — re-check now\n")
    lines.append(rows(overdue) if overdue else "_(none)_\n")
    lines.append("### Upcoming\n")
    lines.append(rows(upcoming) if upcoming else "_(none)_\n")
    if undated:
        lines.append("### Undated (window given but no start date)\n")
        lines.append(rows(undated))
    return "\n".join(lines) + "\n"


def conviction_followthrough_rows(stocks, today):
    """High / Medium-High researched names whose conviction was asserted and then left
    to age without follow-through. Returns a list of dicts sorted most-stale first.
    Every reason is a pure date/field check - no research judgment."""
    rows = []
    for slug, e in stocks.items():
        if e.get("status") != "researched":
            continue
        if e.get("conviction") not in ("High", "Medium-High"):
            continue
        if e.get("red_flag_tier"):
            continue  # red-flagged names live in their own sections, not here

        # "did the work" timestamp: deep-dive beats the thread-scan cooldown date,
        # which in practice stays pinned to the initial screen date.
        work_date = (parse_date(e.get("deepdive_date"))
                     or parse_date(e.get("guidance_backfill_date"))
                     or parse_date(e.get("last_analyzed_date")))
        days_stale = (today - work_date).days if work_date else None

        reasons = []
        owned_here = False  # a reason that no other task is already working

        # (1) PRIMARY, non-redundant: a trusted-conviction floor whose underlying signal
        # has aged past the recency-weight cliff with no new forum post to re-touch it.
        # deepdive-top100 explicitly does NOT re-verify trusted_* fields, and this task
        # only re-checks a trusted name when its THREAD gets a new post - so nothing else
        # catches a floor that is quietly decaying.
        if e.get("trusted_conviction_floor_active"):
            # trusted_signals live in data/<slug>.json, not the state.json entry
            newest = None
            try:
                with open(resolve_data_path(BASE, DATA_DIR, slug)) as df:
                    sig_dates = [parse_date(x.get("date"))
                                 for x in json.load(df).get("trusted_signals", [])]
                sig_dates = [d for d in sig_dates if d]
                newest = max(sig_dates) if sig_dates else None
            except (OSError, json.JSONDecodeError):
                newest = None
            if newest is not None:
                floor_age = (today - newest).days
                if floor_age >= FT_STALE_FLOOR_DAYS:
                    src_user = e.get("trusted_conviction_source_user") or "?"
                    reasons.append(f"trusted floor ({src_user}) rests on a {floor_age}d-old signal")
                    owned_here = True

        # (2)(3) SECONDARY - also covered by deepdive-top100's staleness-weighted queue;
        # listed here only so this file is a complete picture of aged high-conviction names.
        if e.get("revisit_after_30d") and work_date:
            overdue_by = (today - (work_date + datetime.timedelta(days=COOLDOWN_DAYS))).days
            if overdue_by > FT_STALE_REVISIT_GRACE_DAYS:
                reasons.append(f"revisit overdue {overdue_by}d")

        if e.get("deepdive_pass") in (None, 0, 1) and days_stale is not None \
                and days_stale >= FT_STALLED_DEEPDIVE_DAYS:
            reasons.append(f"deep-dive stalled at pass {e.get('deepdive_pass') or 0} ({days_stale}d)")

        if days_stale is not None and days_stale >= FT_STALE_THESIS_DAYS:
            reasons.append(f"thesis unrefreshed {days_stale}d")

        if not reasons:
            continue
        rows.append({
            "name": e.get("name", slug),
            "slug": slug,
            "conviction": e.get("conviction"),
            "thesis_fit": e.get("thesis_fit") or "—",
            "work_date": work_date.isoformat() if work_date else "never",
            "days_stale": days_stale if days_stale is not None else 10 ** 6,
            "pass": e.get("deepdive_pass") or 0,
            "source": e.get("source") or "—",
            "owned_here": owned_here,
            "why": "; ".join(reasons),
        })
    # this-task-owned rows first (stale trusted floors), then by staleness
    rows.sort(key=lambda r: (not r["owned_here"], -r["days_stale"]))
    return rows


def write_conviction_followthrough(stocks, today):
    rows = conviction_followthrough_rows(stocks, today)
    with open(FOLLOWTHROUGH_PATH, "w") as f:
        f.write("# Conviction Without Follow-Through\n\n")
        f.write(
            "High / Medium-High researched names where a view was formed and then left to "
            "age without follow-through - the project's analogue of phreakv6's one stated "
            "regret (*Phreak's Thoughts* #330: \"I had done all the work in Feb and I loved "
            "how cheap it was but never bought ... in May, I had a good opp. to switch but I "
            "didn't\"). Not a re-research queue on its own - a prompt to advance the "
            "deep-dive, re-verify the trusted call, or consciously downgrade. Red-flagged "
            "names are excluded (own sections). Regenerated mechanically from `state.json` - "
            "do not hand-edit.\n\n"
        )
        f.write(f"Generated: {today.isoformat()}\n\n")
        f.write(
            f"**Rows marked ✚ are this task's (`vpscreen-portfolio-threads`) to work** - a "
            f"`trusted_conviction_floor_active` name whose newest `trusted_signals` entry is "
            f"≥{FT_STALE_FLOOR_DAYS}d old: the floor is decaying via `recency_weight` with no "
            "new forum post to re-touch it, and no other task re-verifies trusted fields. "
            "Handle per the SKILL's stale-floor step (re-open that user's thread / search "
            "their recent posts for a fresh mention even absent a new-post trigger; if none, "
            "note it so the floor can be reconsidered).\n\n"
        )
        f.write(
            f"Unmarked rows (`revisit overdue` >{FT_STALE_REVISIT_GRACE_DAYS}d; `deep-dive "
            f"stalled` at pass ≤1 for ≥{FT_STALLED_DEEPDIVE_DAYS}d; `thesis unrefreshed` "
            f"≥{FT_STALE_THESIS_DAYS}d) are **already on `deepdive-top100`'s staleness-weighted "
            "queue** - shown here only for a complete picture, no action needed from this task.\n\n"
        )
        if not rows:
            f.write("_(none — every High / Medium-High name is fresh, on a live revisit "
                    "schedule, past pass 1 recently, or has a current trusted signal)_\n")
        else:
            f.write("| | Stock | Conviction | Thesis fit | Last work | Days stale | Pass | Source | Why flagged |\n")
            f.write("|---|---|---|---|---|---|---|---|---|\n")
            for r in rows:
                ds = "never" if r["days_stale"] == 10 ** 6 else r["days_stale"]
                mark = "✚" if r["owned_here"] else ""
                f.write(f"| {mark} | {r['name']} | {r['conviction']} | {r['thesis_fit']} | "
                        f"{r['work_date']} | {ds} | {r['pass']} | {r['source']} | {r['why']} |\n")
    return rows


def main():
    with open(STATE_PATH) as f:
        state = json.load(f)

    today = datetime.date.today()
    stocks = state.get("stocks", {})

    # --- skip-list: analyzed within the cooldown window ---
    skip_rows = []
    for slug, s in stocks.items():
        d = parse_date(s.get("last_analyzed_date"))
        if d is None:
            continue
        eligible_again = d + datetime.timedelta(days=COOLDOWN_DAYS)
        if eligible_again > today:
            skip_rows.append((s["name"], slug, d, eligible_again, s.get("conviction", "?")))
    skip_rows.sort(key=lambda r: r[3])

    with open(SKIP_PATH, "w") as f:
        f.write("# Skip List (30-day cooldown)\n\n")
        f.write(
            "Stocks analyzed recently enough that their thread should NOT be re-opened by "
            "the scan job yet, regardless of new forum activity. Regenerated mechanically "
            "from `state.json` - do not hand-edit.\n\n"
        )
        f.write(f"Generated: {today.isoformat()}\n\n")
        if not skip_rows:
            f.write("_(empty — nothing currently on cooldown)_\n")
        else:
            f.write("| Stock | Last analyzed | Eligible again on | Conviction |\n")
            f.write("|---|---|---|---|\n")
            for name, slug, d, eligible, conv in skip_rows:
                f.write(f"| {name} | {d.isoformat()} | {eligible.isoformat()} | {conv} |\n")

    # --- revisit-list: moderate-high conviction names flagged for explicit 30-day follow-up ---
    due_now, scheduled = [], []
    for slug, s in stocks.items():
        if not s.get("revisit_after_30d"):
            continue
        d = parse_date(s.get("last_analyzed_date"))
        if d is None:
            due_now.append((s["name"], slug, "never analyzed", s.get("conviction", "?")))
            continue
        target = d + datetime.timedelta(days=COOLDOWN_DAYS)
        if target <= today:
            due_now.append((s["name"], slug, d.isoformat(), s.get("conviction", "?")))
        else:
            scheduled.append((s["name"], slug, target, s.get("conviction", "?")))
    scheduled.sort(key=lambda r: r[2])

    with open(REVISIT_PATH, "w") as f:
        f.write("# Revisit List (moderate-high conviction, explicit 30-day follow-up)\n\n")
        f.write(
            "Stocks worth actively re-checking once their cooldown lapses, even if the forum "
            "goes quiet on them - not just passively waiting for new posts. Regenerated "
            "mechanically from `state.json` - do not hand-edit.\n\n"
        )
        f.write(f"Generated: {today.isoformat()}\n\n")
        f.write("## Due now\n\n")
        if not due_now:
            f.write("_(none due)_\n\n")
        else:
            f.write("| Stock | Last analyzed | Conviction |\n|---|---|---|\n")
            for name, slug, last, conv in due_now:
                f.write(f"| {name} | {last} | {conv} |\n")
            f.write("\n")
        f.write("## Scheduled (not yet due)\n\n")
        if not scheduled:
            f.write("_(none scheduled)_\n")
        else:
            f.write("| Stock | Due on | Conviction |\n|---|---|---|\n")
            for name, slug, target, conv in scheduled:
                f.write(f"| {name} | {target.isoformat()} | {conv} |\n")

        cal_section = catalyst_calendar_section(today)
        if cal_section:
            f.write("\n---\n\n")
            f.write(cal_section)

    # --- x-cluster watch list: low-priority concall/news-snippet names tracked by trusted X users ---
    # source == "trusted-x-watch": a cluster handle NAMED the company in a concall digest /
    # news snippet / quote compilation / weekly business writeup, but WITHOUT a conviction-bearing
    # view. vpscreen-scan Step 0.5 tier 4.8 works this list AFTER every vetted tier (1-4.7) and
    # BEFORE any Step 1 web/forum discovery, capped 2/run, oldest first_seen_date first.
    watch_pending, watch_done = [], []
    for slug, s in stocks.items():
        if s.get("source") != "trusted-x-watch":
            continue
        fs = s.get("first_seen_date") or s.get("x_first_seen_date") or ""
        users = s.get("x_source_user") or "?"
        note = (s.get("x_watch_note") or s.get("notes_short") or "").replace("|", "/").strip()
        if len(note) > 200:
            note = note[:197] + "..."
        la = s.get("last_analyzed_date")
        row = (s.get("name", slug), slug, fs, users, note, la, s.get("status", "?"),
               s.get("conviction") or "—", s.get("thesis_fit") or "—")
        (watch_done if la else watch_pending).append(row)
    watch_pending.sort(key=lambda r: (r[2] or "9999", r[0]))
    watch_done.sort(key=lambda r: (r[5] or "", r[0]))

    with open(XWATCH_PATH, "w") as f:
        f.write("# X-cluster Watch List (low priority — snippet-tracked, not conviction calls)\n\n")
        f.write(
            "Names a trusted X-cluster handle (see `x_cluster.json`) *mentioned* in a concall "
            "digest, news snippet, quote compilation or weekly business writeup — WITHOUT a "
            "conviction-bearing view. Distinct from `source: \"trusted-x\"` (an actual stated "
            "position/thesis → Step 0.5 tier 4.55). This list is `vpscreen-scan` Step 0.5 "
            "**tier 4.8**: worked AFTER every vetted tier (1–4.7) and BEFORE any Step 1 "
            "web/forum discovery, **capped 2/run**, oldest `first_seen_date` first, the rest "
            "carry over. Researched normally (Step 3 preliminary filter applies, no override, "
            "no conviction floor). Regenerated mechanically from `state.json` — do not hand-edit.\n\n"
        )
        f.write(f"Generated: {today.isoformat()}\n\n")
        f.write("## Pending research (queue, oldest first)\n\n")
        if not watch_pending:
            f.write("_(none pending)_\n\n")
        else:
            f.write("| Stock | First seen | Trusted user(s) | Snippet / why tracked |\n")
            f.write("|---|---|---|---|\n")
            for name, slug, fs, users, note, la, st, conv, tf in watch_pending:
                f.write(f"| {name} | {fs or '—'} | {users} | {note} |\n")
            f.write("\n")
        f.write("## Already researched (exited the queue)\n\n")
        if not watch_done:
            f.write("_(none yet)_\n")
        else:
            f.write("| Stock | Last analyzed | Thesis fit | Conviction | Trusted user(s) |\n")
            f.write("|---|---|---|---|---|\n")
            for name, slug, fs, users, note, la, st, conv, tf in watch_done:
                f.write(f"| {name} | {la} | {tf} | {conv} | {users} |\n")

    ft_rows = write_conviction_followthrough(stocks, today)

    print(
        f"skip-list.md: {len(skip_rows)} rows; "
        f"revisit-list.md: {len(due_now)} due now, {len(scheduled)} scheduled; "
        f"x-cluster-watch-list.md: {len(watch_pending)} pending, {len(watch_done)} researched; "
        f"conviction-followthrough.md: {len(ft_rows)} flagged"
    )


if __name__ == "__main__":
    main()
