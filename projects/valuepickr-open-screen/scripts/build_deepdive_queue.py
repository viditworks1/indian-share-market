#!/usr/bin/env python3
"""
build_deepdive_queue.py — (re)generate the deep-dive task's active pool + queue.

2026-09-05: reworked from a dynamic priority over the ENTIRE researched universe (572+
stocks, priority = conviction_score + staleness + thesis_bonus - redflag_penalty) back to
a fixed-size TOP-100 ACTIVE POOL, but selected and rotated on different signals than the
old static top-100-of-max-returns-ranking design ever used. See CHANGELOG.md.

2026-09-16 (user instruction — HARD eligibility gate, not just a priority bonus): the pool
is no longer drawn from the full researched universe. It is now restricted to stocks that
are BOTH (a) a current Confluence-100 member (data/confluence100.json) AND (b) not a
large/mega-cap (`market_cap_tier` containing "large" or "mega", case-insensitive). A
large-cap name almost always resolves `thesis_fit` to "neither" purely on size (per the
large-cap protocol in DEEPDIVE_QUICKREF.md) regardless of how strong its four_box/master
score is, so it can never "support the thesis" this project screens for — the user's
explicit instruction is to safely ignore such names from this pipeline entirely, even if
they'd otherwise score well enough to make a priority-based top-100. Small/mid-cap
Confluence-100 members are eligible regardless of thesis_fit (a name that doesn't yet
support the thesis is still worth deepening research on, per the user). A stock that is
NOT a current Confluence-100 member, or that IS large/mega-cap, is never in the pool no
matter its potential_score — see the `eligible_for_pool` gate below. Also added: a 60-day
per-stock cooldown (`COOLDOWN_DAYS`) — a pool member last deep-dived within the last 60
days is never selected for a fresh FULL primary-document dive; it still rotates into the
queue (as the lowest-priority `rerun_tier`) with `dive_mode:"technicals_only"`, signalling
the task to do a lightweight price/valuation-only refresh rather than a new dive to that
name. See CHANGELOG.md and deepdive-top100/SKILL.md Step 0 / Step 1.

Universe (unchanged): EVERY researched stock in state.json that
  * has status == "researched",
  * resolves to a data/<slug>.json file, and
  * is not a settled red flag (red_flag_tier not in {AVOID, EXCLUDE};
    HIGH CAUTION is kept but de-prioritised).

This full universe's queue entries (incl. `data_file`) are ALWAYS written, even for
names outside the active pool — resolve_data_file.py and other scripts depend on this
queue being the source of truth for the state_key -> data_file mapping for every
researched stock, not just the pool.

Stage 1 — POOL SELECTION.

  2026-09-16 (user instruction — HARD gate, supersedes the old "everyone eligible, just
  boosted" model): a stock is only `eligible_for_pool` if BOTH:
    (a) `in_confluence100` — a current Confluence-100 member (data/confluence100.json,
        built by vpscreen-rerank's Step 7 side job), AND
    (b) NOT `is_large_or_mega` — its `market_cap_tier` does not contain "large" or "mega"
        (case-insensitive). Large-caps are excluded outright, regardless of score: per the
        large-cap protocol, a large-cap's `thesis_fit` resolves to "neither" purely on size
        no matter how strong its four_box/master score is, so it structurally can never
        "support the thesis" this screen exists for. Small/mid-cap Confluence-100 members
        are eligible even when their OWN `thesis_fit` is currently "neither" — the point is
        Confluence-100 membership + being small/mid-cap enough to plausibly support the
        thesis with more work, not already having cleared it.
  A stock failing either test is never in the pool, however high its potential_score —
  see `other_rows` below, which is `ineligible_rows + (eligible_rows past the pool cutoff)`.

  Among ELIGIBLE rows only, priority is still four_box + master_score, boosted for low
  score-coverage (the Confluence-100 gate above already handles the old CONFLUENCE_BONUS
  role, so that bonus term is retired — see CHANGELOG.md):

  fb100    = four_box.score / 4 * 100   (four_box.score is 0-4; read from data/<slug>.json)
             falls back to master_score if a stock has no four_box block yet
  master   = state.json's master_score  (falls back to conviction_score, then 30.0 default)

  potential_score = round(0.5 * fb100 + 0.5 * master, 2)

  COVERAGE_BONUS   = (1 - weight_coverage) * 10.0   (weight_coverage defaults to 0.0,
                     i.e. the full +10 bonus, for a stock master-scores.json has no entry
                     for yet — consistent with "no coverage yet" deserving priority; low
                     coverage means quality_score/consistency_score/expectation_gap_score
                     etc. are still missing, i.e. this name needs more primary-document
                     work before it's fully cross-scored)

  pool_priority = round(potential_score + COVERAGE_BONUS, 2)

Sort ELIGIBLE rows by pool_priority desc (ties: master desc, then name). The ACTIVE POOL =
the top POOL_SIZE (100) of that sort — recomputed fresh every run, so membership can shift
as deep dives update four_box/master_score, as Confluence-100 membership changes week to
week (a name entering or leaving Confluence-100, or crossing the large-cap line, moves
straight in or out of eligibility), and as score coverage fills in. Because eligibility is
now a hard gate on Confluence-100 + non-large-cap rather than the full 570+-stock
universe, the pool can genuinely be SMALLER than 100 — `pool_size = min(POOL_SIZE,
len(eligible_rows))`, and it is normal/expected for this to print well under 100 (bounded
by however many small/mid-cap Confluence-100 members exist at any given time).

Stage 2 — ROTATION ORDER *within* the pool (this drives `rank` 1..pool_size and therefore
which 3 get picked next — see deepdive-top100/SKILL.md Step 0):

  2026-09-16 (user instruction): a 60-day per-stock cooldown was added as the new tier-0
  check, ABOVE high_caution — a pool member last deep-dived (`deepdive_date`) fewer than
  `COOLDOWN_DAYS` (60) ago is NEVER a candidate for a fresh full primary-document dive,
  full stop, regardless of how strong or stale its score is. It still appears in the queue
  (so it isn't silently forgotten) with `dive_mode:"technicals_only"` and sorts into the
  new lowest tier (4) — see deepdive-top100/SKILL.md Step 1 for what a technicals-only
  touch means (a lightweight price/valuation refresh, NOT a new research pass, and it must
  NOT update `deepdive_date`/`deepdive_pass`/history the way a full dive does, or the
  cooldown would never actually expire).

  2026-09-11 (user instruction): staleness (days-since-last-dive) no longer drives ordering
  at all among already-dived names — it used to push the longest-untouched name to the front
  regardless of whether it was ever worth re-diving. Replaced with a 5-level tier (0-3
  unchanged in spirit, 4 added 2026-09-16 for cooldown), each level ordered by
  `pool_priority` descending:

    tier 0 — never-deep-dived                       ("prioritize newer candidates" first)
    tier 1 — already dived, potential_score >= STALE_RERUN_FLOOR (30)   (worth a re-dive)
    tier 2 — already dived, potential_score <  STALE_RERUN_FLOOR       ("no need to rerun" —
             a stale call that never cleared the quality bar on raw four_box+master alone;
             floor checked on `potential_score`, i.e. BEFORE the low-coverage bonus, so a
             fundamentally weak name doesn't dodge the floor just for missing score
             coverage — that's a separate, visibility-driven reason to prioritize, not
             quality)
    tier 3 — high_caution                            (unchanged, de-prioritised near-last)
    tier 4 — in_cooldown (deep-dived <60 days ago)   (2026-09-16, ALWAYS absolute last —
             checked before high_caution, so even a high_caution name that was just dived
             sorts here, not tier 3; see `rerun_tier()`)

  sort key = ( tier (0/1/2/3/4 per the above),
               -pool_priority (ranking WITHIN a tier — same low-coverage-boosted score as
                 Stage 1),
               name )

Plainly: never-dived pool members go first (highest priority first among them); once every
pool member has had at least one dive in the current rotation, ordering is pool_priority
descending among names that cleared the floor, then pool_priority descending again among
names that didn't (so a weak, boosted-into-the-pool name only gets re-dived once nothing
better is pending), with high_caution names sorting near-last and in_cooldown names always
sorting dead last (a full dive should basically never reach tier 4 in normal operation —
by design, cooldown entries are meant to be picked up only via the technicals-only path
described in SKILL.md, once tiers 0-3 are exhausted). This replaces the old "restart basis
staleness and ranking" behaviour — staleness no longer decides order at all, only whether a
name is *stale enough to be a re-dive candidate in the first place* is now irrelevant to
this script (every already-dived, non-cooldown pool member is always a candidate once its
pass comes due; STALE_RERUN_FLOOR only affects how eagerly it's picked, not whether).

Rotation bookkeeping is scoped to the ACTIVE POOL only (not the full universe):
  * a pool entry is "done" once its deep dive for `current_pass` is finished, else "pending";
  * a non-pool entry's `deepdive_status` is set to "not_in_pool" (dormant — its own
    deepdive_pass/deepdive_date/history are preserved untouched, just not in rotation);
  * `current_pass` = the rotation now in progress, computed over pool entries only;
  * when every POOL entry is "done", `current_pass` rolls to N+1 and all pool entries
    reset to "pending" (history is always preserved). Because the pool is recomputed
    fresh each run, the pass that starts next may have slightly different membership
    than the one that just completed — that's intended, not a bug.

Idempotent: existing per-stock progress is matched by `state_key` (falling back to `name`)
and carried forward; entries that drop out of the universe are removed; new entries enter
as "pending" with deepdive_pass 0 if they land in the pool, "not_in_pool" otherwise.

Run from the repo root:  python3 valuepickr-screen/scripts/build_deepdive_queue.py
"""
import json, os, glob, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
VP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(VP, "data")
STATE = os.path.join(VP, "state.json")
QUEUE = os.path.join(DATA, "deepdive-queue.json")
RANKING = os.path.join(DATA, "max-returns-ranking.json")  # read-only, for the long title only
MASTER_SCORES = os.path.join(DATA, "master-scores.json")  # read-only, for weight_coverage
CONFLUENCE = os.path.join(DATA, "confluence100.json")     # read-only, weekly side job output

# ---- tunables ----
POOL_SIZE = 100                # the active deep-dive pool never exceeds this; since
                                # 2026-09-16 eligibility is a hard Confluence-100 +
                                # non-large-cap gate (see module docstring), the pool is
                                # routinely SMALLER than this — it is a ceiling, not a floor
DEFAULT_MASTER = 30.0          # fallback when master_score is absent (shouldn't happen
                                # for any "researched" stock, but stay defensive)
COVERAGE_BONUS_MAX = 10.0      # pool_priority nudge (scaled by 1-weight_coverage) for
                                # stocks whose master-score sub-components are incomplete
COOLDOWN_DAYS = 60             # 2026-09-16 (user instruction): a pool member last
                                # deep-dived fewer than this many days ago is never a
                                # candidate for a fresh FULL dive — see rerun_tier()
STALE_RERUN_FLOOR = 30.0       # Stage 2: an already-dived name with potential_score below
                                # this (pre-Confluence/coverage-bonus quality alone) sorts
                                # behind every name that cleared it — "no need to rerun" a
                                # stale call that never earned the budget (2026-09-11)

SKIP_STEMS = {"max-returns-ranking", "screen-ranking", "conviction-scores",
              "deepdive-queue", "expectation-gap-scores"}
SETTLED_REDFLAGS = {"AVOID", "EXCLUDE"}
TODAY = datetime.date.today()


def norm(s):
    return "".join(c.lower() for c in s if c.isalnum())


def days_since(iso):
    if not iso:
        return None
    try:
        d = datetime.date.fromisoformat(iso[:10])
    except Exception:
        return None
    return max(0, (TODAY - d).days)


def main():
    state = json.load(open(STATE))["stocks"]

    # index data/*.json by filename stem and by internal "name"; also grab four_box.score
    # while we're already opening every file (needed for potential_score anyway).
    datafiles, dataname, stem_internal_name, stem_fourbox = {}, {}, {}, {}
    for p in glob.glob(os.path.join(DATA, "*.json")):
        stem = os.path.splitext(os.path.basename(p))[0]
        if stem in SKIP_STEMS:
            continue
        datafiles[stem] = p
        try:
            doc = json.load(open(p))
        except Exception:
            doc = {}
        nm = doc.get("name")
        if nm:
            dataname[norm(nm)] = stem
            stem_internal_name[stem] = nm
        fb = doc.get("four_box")
        if isinstance(fb, dict) and isinstance(fb.get("score"), (int, float)):
            stem_fourbox[stem] = float(fb["score"])

    # rendered docs, for overwriting the right .docx
    docx_norm = {}
    for p in glob.glob(os.path.join(VP, "docs", "*.docx")):
        st = os.path.splitext(os.path.basename(p))[0]
        docx_norm[norm(st)] = f"docs/{st}.docx"

    def resolve_docx(internal_name, clean_name):
        for cand in (internal_name,
                     internal_name.split(":")[0],
                     internal_name.split("(")[0],
                     internal_name.replace(" Ltd", "").replace(" Limited", ""),
                     internal_name.split(":")[0].split("(")[0]
                         .replace(" Ltd", "").replace(" Limited", ""),
                     clean_name):
            k = norm(cand)
            if k and k in docx_norm:
                return docx_norm[k], True
        return f"docs/{clean_name}.docx", False

    def resolve_stem(key, nm):
        if key in datafiles:
            return key
        s = dataname.get(norm(nm))
        if s:
            return s
        head = norm((nm or "").split(":")[0].split("(")[0])
        if len(head) > 6:
            for dn, ds in dataname.items():
                if head in dn or dn in head:
                    return ds
        for st in datafiles:
            if key and (key.startswith(st) or st.startswith(key)):
                return st
        return None

    # long ValuePickr titles, for reference only (not the universe gate)
    long_title = {}
    try:
        for r in json.load(open(RANKING)).get("ranked", []):
            long_title[r["name"]] = r
    except Exception:
        pass

    # weight_coverage per stem, from the master-score composite's score_breakdown
    # (missing/never-scored -> None, treated as 0.0 coverage = max coverage bonus)
    stem_coverage = {}
    try:
        for r in json.load(open(MASTER_SCORES)).get("ranked", []):
            wc = (r.get("score_breakdown") or {}).get("weight_coverage")
            if isinstance(wc, (int, float)):
                stem_coverage[r["slug"]] = float(wc)
    except Exception:
        pass

    # current Confluence-100 membership, from vpscreen-rerank's weekly side job
    # (missing file, e.g. before the first weekly refresh -> empty set, degrades gracefully)
    confluence_slugs = set()
    try:
        for r in json.load(open(CONFLUENCE)).get("rows", []):
            if r.get("slug"):
                confluence_slugs.add(r["slug"])
    except Exception:
        pass

    # previous per-stock progress, keyed by state_key AND by name
    prev_by_key, prev_by_name = {}, {}
    if os.path.exists(QUEUE):
        for e in json.load(open(QUEUE)).get("queue", []):
            if e.get("state_key"):
                prev_by_key[e["state_key"]] = e
            prev_by_name[e["name"]] = e

    rows = []
    unresolved = []
    for key, s in state.items():
        if s.get("status") != "researched":
            continue
        rf = (s.get("red_flag_tier") or "").strip()
        if rf.upper() in SETTLED_REDFLAGS:
            continue
        nm = s.get("name") or key
        stem = resolve_stem(key, nm)
        if not stem:
            unresolved.append((key, nm))
            continue
        data_file = f"data/{stem}.json"
        internal_name = stem_internal_name.get(stem, nm)
        clean_name = nm.split(":")[0].split(" - ")[0].strip()[:80]
        docx_file, docx_existing = resolve_docx(internal_name, clean_name)

        p = prev_by_key.get(key) or prev_by_name.get(nm) or {}
        # deepdive_pass / date: queue entry wins, else fall back to state.json
        dd_pass = p.get("deepdive_pass", s.get("deepdive_pass", 0)) or 0
        dd_date = p.get("deepdive_date") or s.get("deepdive_date")
        history = p.get("history", [])

        master = s.get("master_score")
        master = float(master) if isinstance(master, (int, float)) else None
        cscore = s.get("conviction_score")
        cscore = float(cscore) if isinstance(cscore, (int, float)) else None
        master_used = master if master is not None else (cscore if cscore is not None else DEFAULT_MASTER)

        fb_score = stem_fourbox.get(stem)
        fb100 = (fb_score / 4.0 * 100.0) if fb_score is not None else master_used

        potential = round(0.5 * fb100 + 0.5 * master_used, 2)

        in_confluence100 = stem in confluence_slugs
        tier_str = (s.get("market_cap_tier") or "").lower()
        is_large_or_mega = ("large" in tier_str) or ("mega" in tier_str)
        eligible_for_pool = in_confluence100 and not is_large_or_mega
        weight_coverage = stem_coverage.get(stem)  # None if not yet in master-scores.json
        coverage_bonus = (1.0 - (weight_coverage if weight_coverage is not None else 0.0)) * COVERAGE_BONUS_MAX
        pool_priority = round(potential + coverage_bonus, 2)

        thesis = s.get("thesis_fit") or "neither"
        dsince = days_since(dd_date)
        never = dd_pass == 0 or dsince is None
        high_caution = bool(rf) and rf.upper() not in ("", "NONE")
        in_cooldown = (not never) and (dsince is not None) and (dsince < COOLDOWN_DAYS)

        rows.append({
            "state_key": key,
            "name": clean_name,
            "ranking_title": long_title.get(clean_name, {}).get("name")
                             or (nm if nm != clean_name else None),
            "data_file": data_file,
            "docx_file": docx_file,
            "docx_is_existing": docx_existing,
            "clean_name": clean_name,
            "market_cap_tier": s.get("market_cap_tier"),
            "ranking_conviction": s.get("conviction"),
            "ranking_thesis_fit": thesis,
            "conviction_score": cscore if cscore is not None else DEFAULT_MASTER,
            "master_score": round(master_used, 2),
            "four_box_score": fb_score,
            "potential_score": potential,
            "in_confluence100": in_confluence100,
            "is_large_or_mega": is_large_or_mega,
            "eligible_for_pool": eligible_for_pool,
            "weight_coverage": weight_coverage,
            "pool_priority": pool_priority,
            "high_caution": high_caution,
            "never_deepdived": never,
            "days_since_deepdive": dsince,
            "in_cooldown": in_cooldown,
            "deepdive_status": p.get("deepdive_status", "pending"),
            "deepdive_pass": dd_pass,
            "deepdive_date": dd_date,
            "pre_deepdive_conviction": p.get("pre_deepdive_conviction"),
            "post_deepdive_conviction": p.get("post_deepdive_conviction"),
            "history": history,
        })

    # ---- Stage 1: pool selection ----
    # 2026-09-16: HARD gate first (Confluence-100 member AND not large/mega-cap) — a row
    # failing this is never in the pool no matter its pool_priority. Only eligible rows
    # compete for the top-POOL_SIZE cut by pool_priority (potential_score, boosted for low
    # score-coverage).
    eligible_rows = [r for r in rows if r["eligible_for_pool"]]
    ineligible_rows = [r for r in rows if not r["eligible_for_pool"]]

    eligible_rows.sort(key=lambda r: (-r["pool_priority"], -r["potential_score"], -r["master_score"], r["name"].lower()))
    pool_size = min(POOL_SIZE, len(eligible_rows))
    for i, r in enumerate(eligible_rows):
        r["in_active_pool"] = i < pool_size
    for r in ineligible_rows:
        r["in_active_pool"] = False

    pool_rows = [r for r in eligible_rows if r["in_active_pool"]]
    other_rows = [r for r in eligible_rows if not r["in_active_pool"]] + ineligible_rows

    # ---- Stage 2: rotation order within the pool (tier, then pool_priority) ----
    # 2026-09-11: staleness no longer orders anything — see the module docstring. A name's
    # tier is (0) never-dived, (1) already-dived and worth a re-dive (potential_score >=
    # floor), (2) already-dived but never earned the budget (potential_score < floor,
    # "no need to rerun"), (3) high_caution, (4) in_cooldown (2026-09-16, checked FIRST so
    # it wins over every other tier including high_caution — see module docstring).
    def rerun_tier(r):
        if r["in_cooldown"]:
            return 4
        if r["high_caution"]:
            return 3
        if r["never_deepdived"]:
            return 0
        return 1 if r["potential_score"] >= STALE_RERUN_FLOOR else 2

    for r in pool_rows:
        r["rerun_tier"] = rerun_tier(r)
        # 2026-09-16: a technicals-only touch must NOT reset deepdive_date/pass/history —
        # see SKILL.md Step 1 and deepdive_apply.py's --mode flag.
        r["dive_mode"] = "technicals_only" if r["rerun_tier"] == 4 else "full"

    pool_rows.sort(key=lambda r: (r["rerun_tier"], -r["pool_priority"], r["name"].lower()))

    # --- pool rotation bookkeeping (current_pass computed over the pool only) ---
    passes = {r["deepdive_pass"] for r in pool_rows}
    if not pool_rows:
        current_pass = 1
    elif all(r["deepdive_status"] == "done" for r in pool_rows):
        current_pass = max(passes) + 1
        for r in pool_rows:
            r["deepdive_status"] = "pending"
    else:
        current_pass = min(passes) + 1
        for r in pool_rows:
            if r["deepdive_pass"] < current_pass and r["deepdive_status"] != "done":
                r["deepdive_status"] = "pending"

    # non-pool entries are dormant: preserve their history/pass/date, just mark status
    other_rows.sort(key=lambda r: (-r["pool_priority"], -r["potential_score"], -r["master_score"], r["name"].lower()))
    for r in other_rows:
        r["deepdive_status"] = "not_in_pool"
        r["rerun_tier"] = None  # rerun_tier only means something for in-pool rotation
        r["dive_mode"] = None

    ordered = pool_rows + other_rows
    for i, r in enumerate(ordered, 1):
        r["rank"] = i

    # reorder keys so `rank` leads each entry
    out = []
    for r in ordered:
        out.append({"rank": r.pop("rank"), **r})

    queue = {
        "generated": TODAY.isoformat(),
        "source": ("ACTIVE POOL (2026-09-16: hard-gated) — recomputed every run from "
                   "every researched state.json stock (status=researched, data file "
                   "resolvable, not AVOID/EXCLUDE), but only stocks that are BOTH a "
                   "current Confluence-100 member AND not large/mega-cap are "
                   "`eligible_for_pool` at all — a large-cap's thesis_fit resolves to "
                   "'neither' on size alone regardless of score, so it can never support "
                   "this screen's thesis and is excluded outright, not just de-prioritised. "
                   "Among eligible stocks, pool membership (top up to 100) is ranked by "
                   "pool_priority = potential_score (0.5*four_box_score(scaled 0-100) + "
                   "0.5*master_score) + up to +10 for low score-coverage "
                   "(weight_coverage). Rotation order *within* the pool is by rerun_tier "
                   "(0=never-dived, 1=already-dived & potential_score>=30, "
                   "2=already-dived & potential_score<30 i.e. 'no need to rerun', "
                   "3=high_caution, 4=in_cooldown i.e. deep-dived <60 days ago — always "
                   "absolute last, dive_mode='technicals_only' not a full dive) then "
                   "pool_priority desc — staleness no longer orders anything. See "
                   "build_deepdive_queue.py."),
        "universe_size": len(out),
        "pool_size": pool_size,
        "tunables": {"POOL_SIZE": POOL_SIZE, "DEFAULT_MASTER": DEFAULT_MASTER,
                     "COOLDOWN_DAYS": COOLDOWN_DAYS},
        "note": ("Active-pool queue for the deepdive-top100 task. The task rebuilds this "
                 "at Step 0 of EVERY run, then takes the first 3 'pending' entries by "
                 "`rank` (all pending entries are pool members — non-pool entries are "
                 "marked 'not_in_pool' and never selected). Pool eligibility (2026-09-16) "
                 "is a HARD gate: must be a current Confluence-100 member AND not "
                 "large/mega-cap, or the stock is never in the pool regardless of score "
                 "(`eligible_for_pool` on every queue entry records this). Among eligible "
                 "stocks, pool = top up to 100 by pool_priority (four_box + master_score, "
                 "boosted for low score-coverage), recomputed fresh each run — membership "
                 "can shift as Confluence-100 changes week to week or a name crosses the "
                 "large-cap line. Unlike the pre-2026-09-16 design, the pool can genuinely "
                 "run BELOW 100 (bounded by how many small/mid-cap Confluence-100 members "
                 "exist) — that is expected, not a bug. Once every pool entry is 'done' "
                 "for `current_pass`, it rolls to N+1 and all pool entries reset to "
                 "'pending' — rotation then resumes ordered by rerun_tier (never-dived, "
                 "then already-dived-above-floor, then already-dived-below-floor 'no need "
                 "to rerun', then high_caution, then in_cooldown — a pool member "
                 "deep-dived under 60 days ago, always absolute last and marked "
                 "`dive_mode:'technicals_only'`, never a candidate for a fresh full dive) "
                 "with pool_priority as the ranking key within each tier. Non-pool entries "
                 "are dormant (status 'not_in_pool') but keep their own data_file mapping "
                 "(other scripts, e.g. resolve_data_file.py, depend on the FULL universe "
                 "being listed here, not just the pool) and their full deepdive "
                 "history/pass/date, so they pick up right where they left off if they "
                 "re-enter the pool later. Do not hand-edit."),
        "current_pass": current_pass,
        "queue": out,
    }
    tmp = QUEUE + ".tmp"
    json.dump(queue, open(tmp, "w"), indent=2, ensure_ascii=False)
    os.replace(tmp, QUEUE)

    pool_pending = sum(1 for e in out if e["in_active_pool"] and e["deepdive_status"] == "pending")
    pool_done = sum(1 for e in out if e["in_active_pool"] and e["deepdive_status"] == "done")
    pool_never = sum(1 for e in out if e["in_active_pool"] and e["never_deepdived"])
    pool_confluence = sum(1 for e in out if e["in_active_pool"] and e["in_confluence100"])
    pool_no_rerun = sum(1 for e in out if e["in_active_pool"] and e["rerun_tier"] == 2)
    pool_cooldown = sum(1 for e in out if e["in_active_pool"] and e["in_cooldown"])
    eligible_count = sum(1 for e in out if e["eligible_for_pool"])
    excluded_large = sum(1 for e in out if e["in_confluence100"] and e["is_large_or_mega"])
    covered = [e["weight_coverage"] for e in out if e["in_active_pool"] and e["weight_coverage"] is not None]
    avg_coverage = round(sum(covered) / len(covered), 2) if covered else None
    print(f"Wrote {QUEUE}")
    print(f"  universe={len(out)}  pool_size={pool_size}  current_pass={current_pass}")
    print(f"  eligibility: confluence100-total={len(confluence_slugs)}  eligible(C100+non-large)={eligible_count}"
          f"  excluded-as-large/mega={excluded_large}")
    print(f"  pool: pending={pool_pending}  done={pool_done}  never-deep-dived-in-pool={pool_never}  in_cooldown(technicals-only)={pool_cooldown}")
    print(f"  pool: confluence100-members={pool_confluence}/{len(confluence_slugs)}  avg_weight_coverage={avg_coverage}")
    print(f"  pool: below-floor 'no need to rerun' (potential_score<{STALE_RERUN_FLOOR}, already dived)={pool_no_rerun}")
    if pool_rows:
        min_potential = min(r["potential_score"] for r in pool_rows)
        min_priority = min(r["pool_priority"] for r in pool_rows)
        print(f"  pool potential_score cutoff (min in pool): {min_potential}  (min pool_priority: {min_priority})")
        print("  top of pool rotation order this run:")
        tier_tag = {0: "NEVER", 1: "re-dive", 2: "no-rerun", 3: "caution", 4: "COOLDOWN"}
        for e in [r for r in out if r["in_active_pool"]][:5]:
            tag = tier_tag.get(e["rerun_tier"], "?")
            cf = "C100" if e["in_confluence100"] else "    "
            print(f"    #{e['rank']:>3} {e['name'][:38]:38} pri={e['pool_priority']:>6} pot={e['potential_score']:>6}"
                  f"  fb={e['four_box_score']}  master={e['master_score']:>5}  cov={e['weight_coverage']}  {cf}  {tag}  [{e['deepdive_status']}/{e['dive_mode']}]")
    if unresolved:
        print(f"  WARNING: {len(unresolved)} researched stocks could not resolve a data_file:")
        for key, nm in unresolved[:20]:
            print(f"    {key}  ({nm[:50]})")


if __name__ == "__main__":
    main()
