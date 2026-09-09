#!/usr/bin/env python3
"""
build_deepdive_queue.py — (re)generate the deep-dive task's active-100 pool + queue.

2026-09-05: reworked from a dynamic priority over the ENTIRE researched universe (572+
stocks, priority = conviction_score + staleness + thesis_bonus - redflag_penalty) back to
a fixed-size TOP-100 ACTIVE POOL, but selected and rotated on different signals than the
old static top-100-of-max-returns-ranking design ever used. See CHANGELOG.md.

Universe (unchanged): EVERY researched stock in state.json that
  * has status == "researched",
  * resolves to a data/<slug>.json file, and
  * is not a settled red flag (red_flag_tier not in {AVOID, EXCLUDE};
    HIGH CAUTION is kept but de-prioritised).

This full universe's queue entries (incl. `data_file`) are ALWAYS written, even for
names outside the active pool — resolve_data_file.py and other scripts depend on this
queue being the source of truth for the state_key -> data_file mapping for every
researched stock, not just the pool.

Stage 1 — POOL SELECTION, by "priority" (four_box + master_score, boosted for
Confluence-100 membership and for low score-coverage), primarily:

  fb100    = four_box.score / 4 * 100   (four_box.score is 0-4; read from data/<slug>.json)
             falls back to master_score if a stock has no four_box block yet
  master   = state.json's master_score  (falls back to conviction_score, then 30.0 default)

  potential_score = round(0.5 * fb100 + 0.5 * master, 2)

  2026-09-05 (user instruction): pool selection AND rotation both additionally favour
  (a) stocks currently in the weekly Confluence-100 artifact (data/confluence100.json,
      built by vpscreen-rerank's Step 7 side job — the live, technically-confirmed,
      portfolio-actionable shortlist) and
  (b) stocks with low `weight_coverage` (data/master-scores.json's per-stock
      score_breakdown — the fraction of the 5 master-score sub-scores actually
      computable; low coverage means quality_score/consistency_score/expectation_gap_score
      etc. are still missing, i.e. this name needs more primary-document work before it's
      fully cross-scored), so the routine actively closes those gaps rather than only
      re-confirming already well-covered names.

  CONFLUENCE_BONUS = 20.0   if the stock is a current Confluence-100 member
  COVERAGE_BONUS   = (1 - weight_coverage) * 10.0   (weight_coverage defaults to 0.0,
                     i.e. the full +10 bonus, for a stock master-scores.json has no entry
                     for yet — consistent with "no coverage yet" deserving priority)

  pool_priority = round(potential_score + CONFLUENCE_BONUS + COVERAGE_BONUS, 2)

Sort the whole eligible universe by pool_priority desc (ties: master desc, then name).
The ACTIVE POOL = the top POOL_SIZE (100) of that sort — recomputed fresh every run, so
membership can shift as deep dives update four_box/master_score, as Confluence-100
membership changes week to week, and as score coverage fills in. This never shrinks below
min(POOL_SIZE, eligible_universe_size) — with 570+ eligible names today that floor is
always exactly 100; there is always a next-best name to pull in. The bonuses are additive
nudges (typically ~10-40 points against a potential_score range that runs from the pool
cutoff, currently ~mid-40s, up into the 80s-90s for the strongest names) — they pull
borderline Confluence-100/low-coverage names into contention, they do not hand them the
pool outright over names with a much stronger fundamental potential_score.

Stage 2 — ROTATION ORDER *within* the pool (this drives `rank` 1..100 and therefore which
3 get picked next — see deepdive-top100/SKILL.md Step 0):

  sort key = ( high_caution flag (0/1, de-prioritised last),
               never-deep-dived flag (0/1, never-dived sorts FIRST),
               -days_since_last_deepdive (more stale first, 0 for never-dived — already
                 sorted first by the flag above),
               -pool_priority (ranking tie-break / secondary ordering — same
                 Confluence-100 + low-coverage-boosted score as Stage 1, so those names
                 also sort earlier *within* whichever staleness/never-dived tier they land in),
               name )

Plainly: never-dived pool members go first (highest priority first among them), then
once every pool member has had at least one dive in the current rotation, ordering falls
back to staleness (longest-since-last-dive first), with pool_priority as the tie-break.
This is exactly "restart basis staleness and ranking" once a pass completes.

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
POOL_SIZE = 100                # the active deep-dive pool never exceeds (or, while the
                                # eligible universe is >= 100, ever falls below) this
DEFAULT_MASTER = 30.0          # fallback when master_score is absent (shouldn't happen
                                # for any "researched" stock, but stay defensive)
CONFLUENCE_BONUS = 20.0        # pool_priority nudge for current Confluence-100 members
COVERAGE_BONUS_MAX = 10.0      # pool_priority nudge (scaled by 1-weight_coverage) for
                                # stocks whose master-score sub-components are incomplete

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
        weight_coverage = stem_coverage.get(stem)  # None if not yet in master-scores.json
        coverage_bonus = (1.0 - (weight_coverage if weight_coverage is not None else 0.0)) * COVERAGE_BONUS_MAX
        pool_priority = round(potential + (CONFLUENCE_BONUS if in_confluence100 else 0.0) + coverage_bonus, 2)

        thesis = s.get("thesis_fit") or "neither"
        dsince = days_since(dd_date)
        never = dd_pass == 0 or dsince is None
        high_caution = bool(rf) and rf.upper() not in ("", "NONE")

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
            "weight_coverage": weight_coverage,
            "pool_priority": pool_priority,
            "high_caution": high_caution,
            "never_deepdived": never,
            "days_since_deepdive": dsince,
            "deepdive_status": p.get("deepdive_status", "pending"),
            "deepdive_pass": dd_pass,
            "deepdive_date": dd_date,
            "pre_deepdive_conviction": p.get("pre_deepdive_conviction"),
            "post_deepdive_conviction": p.get("post_deepdive_conviction"),
            "history": history,
        })

    # ---- Stage 1: pool selection by pool_priority (potential_score, boosted for ----
    # ---- Confluence-100 membership and low score-coverage) ----
    rows.sort(key=lambda r: (-r["pool_priority"], -r["potential_score"], -r["master_score"], r["name"].lower()))
    pool_size = min(POOL_SIZE, len(rows))
    for i, r in enumerate(rows):
        r["in_active_pool"] = i < pool_size

    pool_rows = [r for r in rows if r["in_active_pool"]]
    other_rows = [r for r in rows if not r["in_active_pool"]]

    # ---- Stage 2: rotation order within the pool (staleness, then ranking) ----
    pool_rows.sort(key=lambda r: (
        1 if r["high_caution"] else 0,
        0 if r["never_deepdived"] else 1,
        -(r["days_since_deepdive"] or 0) if not r["never_deepdived"] else 0,
        -r["pool_priority"],
        r["name"].lower(),
    ))

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

    ordered = pool_rows + other_rows
    for i, r in enumerate(ordered, 1):
        r["rank"] = i

    # reorder keys so `rank` leads each entry
    out = []
    for r in ordered:
        out.append({"rank": r.pop("rank"), **r})

    queue = {
        "generated": TODAY.isoformat(),
        "source": ("ACTIVE-100-POOL — recomputed every run from every researched "
                   "state.json stock (status=researched, data file resolvable, not "
                   "AVOID/EXCLUDE). Pool membership (top 100) is selected by "
                   "pool_priority = potential_score (0.5*four_box_score(scaled 0-100) + "
                   "0.5*master_score) + a +20 bonus for current Confluence-100 membership "
                   "+ up to +10 for low score-coverage (weight_coverage). Rotation order "
                   "*within* the pool is by staleness then pool_priority ranking. See "
                   "build_deepdive_queue.py."),
        "universe_size": len(out),
        "pool_size": pool_size,
        "tunables": {"POOL_SIZE": POOL_SIZE, "DEFAULT_MASTER": DEFAULT_MASTER},
        "note": ("Active-pool queue for the deepdive-top100 task. The task rebuilds this "
                 "at Step 0 of EVERY run, then takes the first 3 'pending' entries by "
                 "`rank` (all pending entries are pool members — non-pool entries are "
                 "marked 'not_in_pool' and never selected). Pool = top 100 by "
                 "pool_priority (four_box + master_score, boosted for current "
                 "Confluence-100 membership and for low score-coverage), recomputed fresh "
                 "each run — membership can shift. The pool never shrinks below "
                 "min(100, eligible_universe_size); with 570+ eligible names, that floor "
                 "is always exactly 100 — there is always a next-best name to backfill "
                 "with, even once every never-dived pool member has been covered. Once "
                 "every pool entry is 'done' for `current_pass`, it rolls to N+1 and all "
                 "pool entries reset to 'pending' — rotation then resumes ordered by "
                 "staleness (longest-since-last-dive first) with potential_score as the "
                 "ranking tie-break. Non-pool entries are dormant (status 'not_in_pool') "
                 "but keep their own data_file mapping (other scripts, e.g. "
                 "resolve_data_file.py, depend on the FULL universe being listed here, "
                 "not just the pool) and their full deepdive history/pass/date, so they "
                 "pick up right where they left off if they re-enter the pool later. "
                 "Do not hand-edit."),
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
    covered = [e["weight_coverage"] for e in out if e["in_active_pool"] and e["weight_coverage"] is not None]
    avg_coverage = round(sum(covered) / len(covered), 2) if covered else None
    print(f"Wrote {QUEUE}")
    print(f"  universe={len(out)}  pool_size={pool_size}  current_pass={current_pass}")
    print(f"  pool: pending={pool_pending}  done={pool_done}  never-deep-dived-in-pool={pool_never}")
    print(f"  pool: confluence100-members={pool_confluence}/{len(confluence_slugs)}  avg_weight_coverage={avg_coverage}")
    if pool_rows:
        min_potential = min(r["potential_score"] for r in pool_rows)
        min_priority = min(r["pool_priority"] for r in pool_rows)
        print(f"  pool potential_score cutoff (min in pool): {min_potential}  (min pool_priority: {min_priority})")
        print("  top of pool rotation order this run:")
        for e in [r for r in out if r["in_active_pool"]][:5]:
            tag = "NEVER" if e["never_deepdived"] else f"{e['days_since_deepdive']}d-stale"
            cf = "C100" if e["in_confluence100"] else "    "
            print(f"    #{e['rank']:>3} {e['name'][:38]:38} pri={e['pool_priority']:>6} pot={e['potential_score']:>6}"
                  f"  fb={e['four_box_score']}  master={e['master_score']:>5}  cov={e['weight_coverage']}  {cf}  {tag}  [{e['deepdive_status']}]")
    if unresolved:
        print(f"  WARNING: {len(unresolved)} researched stocks could not resolve a data_file:")
        for key, nm in unresolved[:20]:
            print(f"    {key}  ({nm[:50]})")


if __name__ == "__main__":
    main()
