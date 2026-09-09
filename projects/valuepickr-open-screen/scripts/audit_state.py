#!/usr/bin/env python3
"""
Mechanical hygiene sweep over state.json + screen-ranking.json - deterministic
checks only, no LLM judgment. Auto-fixes what has one unambiguous correct value;
reports (never guesses) anything else. Meant to be run by the vpscreen-audit
scheduled task, but safe to run by hand any time.

Usage: python3 audit_state.py [--fix]   (default is --fix; pass --dry-run to only report)
"""
import argparse
import json
import os
import re
import sys

from recency_weight import weight_for_date
from resolve_data_file import resolve_data_path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")
RANKING_PATH = os.path.join(BASE, "data", "screen-ranking.json")
USERS_PATH = os.path.join(BASE, "users.json")
TRUSTED_USERS_PATH = os.path.join(BASE, "trusted_users.json")
DATA_DIR = os.path.join(BASE, "data")

VALID_STATUS = {"candidate", "researched", "excluded", "avoid", "not-a-stock"}
VALID_THESIS = {None, "10x-in-2-3-years", "100x-in-10-years", "neither"}
RETURN_LABELS = {"10x-in-2-3-years", "100x-in-10-years"}
FOUR_BOX_ENUM = {"yes": 1.0, "weak": 0.5, "no": 0.0}
STATUS_ALIASES = {"analyzed": "researched", "done": "researched", "complete": "researched"}

# Fields treated as a "trusted-thread signal" - preserved across a merge regardless of which
# entry wins, so they're excluded from the completeness tiebreak (that logic is separate, below).
SIGNAL_FIELDS = ("source", "source_detail", "trusted_conviction_strength")
STATUS_TIER = {"researched": 1, "excluded": 1, "avoid": 1, "candidate": 0}


def _norm_name(x):
    """Loose normalisation so a screen-ranking.json display name ('Syngene International')
    lines up with a state.json entry name ('Syngene International Ltd')."""
    x = (x or "").lower()
    for w in (" ltd", " limited", " corporation", " (india)", "(india)", " india",
              " technologies", " industries", ".", ",", "-", "'"):
        x = x.replace(w, "")
    return " ".join(x.split())


def _completeness_score(e):
    """Count non-null, non-empty-string fields, excluding SIGNAL_FIELDS (those are copied
    over separately and shouldn't bias which entry is picked as canonical)."""
    score = 0
    for k, v in e.items():
        if k in SIGNAL_FIELDS:
            continue
        if v is None or v == "":
            continue
        score += 1
    return score


def _choose_canonical(slug_a, slug_b, stocks):
    """Return (winner_slug, loser_slug) between two entries sharing a topic_id."""
    e_a, e_b = stocks[slug_a], stocks[slug_b]
    ta = STATUS_TIER.get(e_a.get("status"), 0)
    tb = STATUS_TIER.get(e_b.get("status"), 0)
    if ta != tb:
        return (slug_a, slug_b) if ta > tb else (slug_b, slug_a)
    ca = _completeness_score(e_a)
    cb = _completeness_score(e_b)
    if ca != cb:
        return (slug_a, slug_b) if ca > cb else (slug_b, slug_a)
    # final deterministic tiebreak: earlier first_seen_date, then slug alphabetically
    fa = e_a.get("first_seen_date") or ""
    fb = e_b.get("first_seen_date") or ""
    if fa != fb:
        return (slug_a, slug_b) if fa < fb else (slug_b, slug_a)
    return (slug_a, slug_b) if slug_a < slug_b else (slug_b, slug_a)


_STOPWORDS_RE = re.compile(r"\b(ltd\.?|limited|pvt\.?|private|india|the|co\.?|company)\b")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _norm_stock_name(s):
    """Loose normalization so 'MTAR Technologies Ltd' (state.json name) and
    'Mtar Technologies Ltd' (users.json high_conviction_calls stock) compare equal."""
    s = (s or "").lower()
    s = _STOPWORDS_RE.sub(" ", s)
    s = _NON_ALNUM_RE.sub(" ", s).strip()
    return s


def _names_match(a, b):
    na, nb = _norm_stock_name(a), _norm_stock_name(b)
    if not na or not nb:
        return False
    return na == nb or na in nb or nb in na


def _resolve_source_user(entry, trusted_names, data_signals):
    """
    Best-effort parse of WHICH trusted username a very-high trusted_conviction_strength
    tag is attributed to, from existing free-text fields - no live forum research here.

    Priority:
    1. If phreakv6 (the project's one 'core'-tier user) is named anywhere in this stock's
       data/<slug>.json trusted_signals, source_detail, or notes_short - credit phreakv6.
       This matters because he's the only user whose tier can keep the floor active, and
       several very-high tags are joint phreakv6-original / elevated-user-corroboration
       calls where phreakv6 is the substantive original source even if a later corroborating
       post is what's recorded in the structured source_detail field (e.g. venus-remedies).
    2. Otherwise, the first trusted username in source_detail explicitly marked
       "(user-trusted" (the project's own convention for citing the driving signal).
    3. Otherwise, the first trusted username mentioned anywhere in source_detail.
    4. Otherwise, "<name> (trusted)" in notes_short.
    5. Otherwise, the first trusted username mentioned anywhere in notes_short.
    Returns None if nothing resolvable.
    """
    source_detail = entry.get("source_detail") or ""
    notes_short = entry.get("notes_short") or ""

    if data_signals:
        for sig in data_signals:
            if "phreakv6" in (sig.get("username") or ""):
                return "phreakv6"
    if re.search(r"(?<![A-Za-z0-9_.])phreakv6(?![A-Za-z0-9_.])", source_detail + " " + notes_short):
        return "phreakv6"

    name_alt = "|".join(re.escape(n) for n in trusted_names)
    if not name_alt:
        return None

    m = re.search(r"(?<![A-Za-z0-9_.])(" + name_alt + r")\s*\(user-trusted", source_detail)
    if m:
        return m.group(1)

    def first_mention(text):
        best, best_pos = None, None
        for name in trusted_names:
            mm = re.search(r"(?<![A-Za-z0-9_.])" + re.escape(name) + r"(?![A-Za-z0-9_.])", text)
            if mm and (best_pos is None or mm.start() < best_pos):
                best, best_pos = name, mm.start()
        return best

    u = first_mention(source_detail)
    if u:
        return u

    m = re.search(r"(?<![A-Za-z0-9_.])(" + name_alt + r")\s*\(trusted\)", notes_short)
    if m:
        return m.group(1)

    return first_mention(notes_short)


def _best_recency_weight(entry, slug, source_user, users_index, data_signals, today=None):
    """
    Find the LATEST relevant date we have on record for this stock's trusted signal and
    return its recency weight (see recency_weight.weight_for_date). Since weight is
    monotonically non-increasing with age, "latest date" == "max weight across every
    date candidate we can find" - so we just compute weight for every candidate and
    take the max, rather than needing to parse-and-compare dates ourselves.

    Deliberately does NOT fall back to last_analyzed_date/first_seen_date: those record
    when THIS PROJECT last scanned the thread, not when the trusted user actually posted
    the conviction - using them would make a 2021 backfilled call look "fresh" just
    because the thread was (re-)scanned this week. If no real signal date is found,
    weight defaults conservatively to 0.05 (stale), same as an unparseable date.
    """
    candidates = []

    # 1. users.json high_conviction_calls: the structured, purpose-built date field for
    #    exactly this (username, stock) pairing.
    if source_user and source_user in users_index:
        for call in users_index[source_user]:
            if _names_match(call.get("stock", ""), entry.get("name", "")):
                candidates.append(call.get("date", ""))

    # 2. data/<slug>.json trusted_signals dates (filtered to source_user when we can).
    for sig in data_signals or []:
        uname_field = sig.get("username") or ""
        if not source_user or source_user in uname_field:
            candidates.append(sig.get("date", ""))

    # 3. Any explicit YYYY-MM-DD dates embedded in source_detail / notes_short prose.
    text = (entry.get("source_detail") or "") + " " + (entry.get("notes_short") or "")
    candidates.extend(_ISO_DATE_RE.findall(text))

    if not candidates:
        return 0.05

    return max(weight_for_date(c, today=today) for c in candidates)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    fix = not args.dry_run

    report = []
    fixed = 0

    with open(STATE_PATH) as f:
        state = json.load(f)
    stocks = state["stocks"]

    # screen-dimensions lookup: display-name -> primary_screen_reason, from
    # data/screen-ranking.json (see scripts/SCREEN_DIMENSIONS_SCHEMA.md). Used by the
    # revisit_after_30d carve-out (section 3) and the dimension check (section 5).
    screen_prr = {}
    if os.path.exists(RANKING_PATH):
        with open(RANKING_PATH) as f:
            _rk_early = json.load(f)
        for _b in ("screenedOut", "tierC", "highCaution", "avoid", "tierB", "tierA"):
            for _it in _rk_early.get(_b, []):
                if _it.get("primary_screen_reason"):
                    screen_prr[_norm_name(_it.get("name", ""))] = _it["primary_screen_reason"]

    # --- 1. status normalization ---
    for slug, e in stocks.items():
        s = e.get("status")
        if s in STATUS_ALIASES:
            report.append(f"status: {slug} had '{s}', {'fixed to' if fix else 'should be'} '{STATUS_ALIASES[s]}'")
            if fix:
                e["status"] = STATUS_ALIASES[s]
                fixed += 1
        elif s not in VALID_STATUS:
            report.append(f"status: {slug} has unrecognized value '{s}' - NOT auto-fixed, needs a look")

    # --- 2. thesis_fit validity (report only, don't guess) ---
    for slug, e in stocks.items():
        t = e.get("thesis_fit")
        if e.get("status") in ("researched", "excluded", "avoid") and t not in VALID_THESIS:
            report.append(f"thesis_fit: {slug} has unrecognized value '{t}' - NOT auto-fixed, needs a look")

    # --- 2b. four_box gate vs thesis_fit consistency (report only; see DEEPDIVE_QUICKREF.md).
    #     four_box lives in data/<slug>.json only. Grandfathered: a researched name with no
    #     block yet is skipped (deepdive-top100's rotation backfills it). ---
    fb_missing = 0
    fb_checked = 0
    fb_override_kept = 0
    for slug, e in stocks.items():
        if e.get("status") != "researched" or e.get("red_flag_tier"):
            continue
        data_fp = resolve_data_path(BASE, DATA_DIR, slug)
        if not os.path.exists(data_fp):
            continue
        try:
            with open(data_fp) as f:
                fb = json.load(f).get("four_box")
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(fb, dict):
            fb_missing += 1
            continue
        fb_checked += 1
        boxes = {k: fb.get(k) for k in ("tailwind", "tam", "moat", "valuation")}
        bad = [f"{k}={v!r}" for k, v in boxes.items() if v not in FOUR_BOX_ENUM]
        if bad:
            report.append(f"four_box: {slug} has non-enum box value(s) {', '.join(bad)} "
                          f"(want yes/weak/no) - needs a look")
            continue
        want_score = sum(FOUR_BOX_ENUM[v] for v in boxes.values())
        have_score = fb.get("score")
        if not isinstance(have_score, (int, float)) or abs(have_score - want_score) > 0.01:
            report.append(f"four_box: {slug} score is {have_score!r} but the boxes sum to "
                          f"{want_score} - needs a look")
            have_score = want_score  # judge the mismatch below on the true sum
        t = e.get("thesis_fit")
        if have_score >= 3.0 and t == "neither":
            # score >= 3.0 only PERMITS a return label (DEEPDIVE_QUICKREF decision table),
            # it does not require one. A deliberate 'neither' with a written rationale in the
            # four_box note / verdict_reasoning carries analyst_override:true and is not a defect
            # (size / return-magnitude / capital-intensity calls the mechanical boxes can't see -
            # the "Nesco logic"). Count them so the suppression stays visible.
            if fb.get("analyst_override"):
                fb_override_kept += 1
            else:
                report.append(f"FOUR-BOX MISMATCH (thesis understated): {slug} four_box.score "
                              f"{have_score} >= 3.0 but thesis_fit == 'neither'. Re-check against "
                              f"analysis.md; if the boxes are right, thesis_fit should be a return "
                              f"label (conviction unchanged). If the 'neither' is deliberate, add "
                              f"four_box.analyst_override=true with the reason in the note.")
        elif have_score <= 1.5 and t in RETURN_LABELS:
            report.append(f"FOUR-BOX MISMATCH (thesis overstated): {slug} four_box.score "
                          f"{have_score} <= 1.5 but thesis_fit == '{t}'. That range is 'neither' "
                          f"with no exception - re-check.")
    if fb_missing:
        report.append(f"four_box coverage: {fb_checked} researched non-red-flag names have a "
                      f"block, {fb_missing} still missing (deepdive-top100 backfills these; a "
                      f"rising count means it isn't).")
    if fb_override_kept:
        report.append(f"four_box: {fb_override_kept} name(s) keep thesis_fit='neither' at "
                      f"score>=3.0 via analyst_override (deliberate size/return-magnitude calls) "
                      f"- suppressed from the understated-mismatch list, not a defect.")

    # --- 3. revisit_after_30d 3-part rule (mechanical, safe to auto-fix) ---
    for slug, e in stocks.items():
        if not e.get("revisit_after_30d"):
            continue
        conv = e.get("conviction") or ""
        ok_conviction = conv in ("Medium-High", "High")
        ok_redflag = not e.get("red_flag_tier")
        ok_thesis = e.get("thesis_fit") != "neither"
        # Carve-out: a screen-out driven purely by technicals or valuation is NOT durable -
        # "the move already happened" / "trades at 75x" can look completely different a
        # quarter later. Keep revisit_after_30d eligible for those even below the
        # Medium-High conviction bar, as long as the thesis still fits and there's no red
        # flag. (see scripts/SCREEN_DIMENSIONS_SCHEMA.md)
        prr = screen_prr.get(_norm_name(e.get("name", "")))
        if prr in ("technicals", "valuation") and ok_redflag and ok_thesis:
            continue
        if not (ok_conviction and ok_redflag and ok_thesis):
            reasons = []
            if not ok_conviction:
                reasons.append(f"conviction={conv!r} (needs Medium-High/High)")
            if not ok_redflag:
                reasons.append(f"red_flag_tier={e.get('red_flag_tier')!r}")
            if not ok_thesis:
                reasons.append("thesis_fit=neither")
            report.append(f"revisit_after_30d: {slug} was true but fails rule ({', '.join(reasons)}), "
                           f"{'fixed to' if fix else 'should be'} false")
            if fix:
                e["revisit_after_30d"] = False
                fixed += 1

    # --- 3.5 very-high trusted conviction floor (mechanical, safe to auto-fix) ---
    # Rule agreed 2026-08-22: a very-high-strength trusted-thread candidate with no red
    # flag must have conviction >= Medium-High. Found violated in practice (td-power-systems,
    # mtar-technologies both sat at "Medium") within the same session the rule was written -
    # confirms LLM-only enforcement of scoring rules is fragile; this closes the gap for good.
    #
    # Rule tightened 2026-08-22 (later same day): the floor should only bind when the
    # very-high tag both (a) traces back to a "core"-tier trusted user (trusted_users.json;
    # currently only phreakv6 - "elevated" tier is the ~400-user mechanically-promoted bulk
    # and was never meant to carry conviction-floor weight on its own) and (b) is still recent
    # (recency_weight.weight_for_date >= 0.6, i.e. the underlying signal is within ~6 months).
    # A trusted user's conviction from a year ago (possibly since exited) isn't "current"
    # conviction - see recency_weight.py. When either condition fails we do NOT erase the
    # very-high tag (it's a real historical record) - instead trusted_conviction_floor_active
    # is set to false so the floor stops being enforced for that entry.
    CONVICTION_RANK = {"Low": 1, "Low-Medium": 2, "Medium": 3, "Medium-High": 4, "High": 5}

    trusted_names = []
    trust_tier_by_user = {}
    if os.path.exists(TRUSTED_USERS_PATH):
        with open(TRUSTED_USERS_PATH) as f:
            _tu = json.load(f)
        for uname, u in _tu.get("users", {}).items():
            trusted_names.append(uname)
            trust_tier_by_user[uname] = u.get("trust_tier")

    users_index = {}
    if os.path.exists(USERS_PATH):
        with open(USERS_PATH) as f:
            _users = json.load(f).get("users", {})
        for uname, u in _users.items():
            users_index[uname] = u.get("high_conviction_calls", [])

    for slug, e in stocks.items():
        if e.get("trusted_conviction_strength") != "very-high":
            continue

        data_fp = resolve_data_path(BASE, DATA_DIR, slug)
        data_signals = None
        if os.path.exists(data_fp):
            with open(data_fp) as f:
                data_signals = json.load(f).get("trusted_signals")

        if not e.get("trusted_conviction_source_user"):
            resolved = _resolve_source_user(e, trusted_names, data_signals)
            if resolved:
                report.append(f"trusted_conviction_source_user: {slug} {'set to' if fix else 'should be set to'} "
                               f"'{resolved}' (parsed from source_detail/notes_short/trusted_signals)")
                if fix:
                    e["trusted_conviction_source_user"] = resolved
                    fixed += 1

        source_user = e.get("trusted_conviction_source_user")
        is_core = bool(source_user) and trust_tier_by_user.get(source_user) == "core"
        weight = _best_recency_weight(e, slug, source_user, users_index, data_signals)
        should_be_active = is_core and weight >= 0.6

        current_active = e.get("trusted_conviction_floor_active", True)
        if current_active is not should_be_active:
            reasons = []
            if not is_core:
                reasons.append(f"source_user={source_user!r} is not core-tier "
                                f"(trust_tier={trust_tier_by_user.get(source_user)!r})")
            if not (weight >= 0.6):
                reasons.append(f"signal recency weight={weight} < 0.6 (stale, >~6 months old)")
            reason_txt = "; ".join(reasons) if reasons else "now core-tier and recent"
            report.append(f"trusted_conviction_floor_active: {slug} {'set to' if fix else 'should be'} "
                           f"{should_be_active} ({reason_txt})")
            if fix:
                e["trusted_conviction_floor_active"] = should_be_active
                fixed += 1

        if e.get("status") not in ("researched", "excluded", "avoid"):
            continue
        if e.get("red_flag_tier"):
            continue
        if e.get("trusted_conviction_floor_active", True) is False:
            continue
        conv = e.get("conviction")
        if CONVICTION_RANK.get(conv, 0) < CONVICTION_RANK["Medium-High"]:
            report.append(f"conviction floor: {slug} is very-high-trusted (core-tier, recent) with no red flag but "
                           f"conviction={conv!r} (needs >= Medium-High), {'fixed to' if fix else 'should be'} Medium-High")
            if fix:
                e["conviction"] = "Medium-High"
                fixed += 1

    # --- 3.6 last_post_number_analyzed sanity (added 2026-08-23) ---
    # This field is the per-stock incremental-read checkpoint: vpscreen-scan uses it to
    # fetch only NEW posts on a re-verification pass instead of blindly re-pulling "most
    # recent 50" (which both wastes tokens re-reading old posts AND can silently skip a
    # thread's middle section if it grew a lot between visits). Report only, never guess a
    # value - a wrong checkpoint could cause a real coverage gap, worse than a missing one
    # (missing just falls back to the safe first-time-read behavior).
    for slug, e in stocks.items():
        if e.get("status") not in ("researched", "excluded", "avoid"):
            continue
        if "last_post_number_analyzed" not in e:
            report.append(f"last_post_number_analyzed: {slug} is {e.get('status')} but field is missing entirely "
                           f"- NOT auto-fixed, vpscreen-scan will fall back to first-time-read behavior")
            continue
        val = e.get("last_post_number_analyzed")
        if val is not None and not isinstance(val, int):
            report.append(f"last_post_number_analyzed: {slug} has non-int value {val!r} - needs a look")
            continue
        hpn = e.get("highest_post_number")
        if val is not None and isinstance(hpn, int) and val > hpn:
            # highest_post_number is a discover.py-time cached thread-length count that
            # nothing downstream reads - it goes stale the moment the thread grows. The
            # checkpoint is written by vpscreen-scan after an actual read, so it's the
            # authoritative number here: you cannot have read past post N if the thread's
            # highest post is below N. Raise the stale ceiling to match rather than re-flag
            # it every run. (Still safe - never lowers the ceiling, never touches the
            # checkpoint, which is the field a wrong value would actually hurt.)
            report.append(f"last_post_number_analyzed: {slug} checkpoint ({val}) exceeded stale "
                           f"highest_post_number ({hpn}) - {'raised ceiling to' if fix else 'ceiling should be'} {val}")
            if fix:
                e["highest_post_number"] = val
                fixed += 1

    # --- 4. duplicate topic_id auto-merge (same VP thread registered under 2+ slugs) ---
    # Same forum thread sometimes gets registered under two different slugs via different
    # discovery paths. Keep whichever entry has more complete data as canonical (prefer
    # researched/excluded/avoid over candidate; tiebreak on non-null field count), delete the
    # other, but first copy over any trusted-thread signal (source/source_detail/
    # trusted_conviction_strength) the removed entry has that the survivor lacks.
    by_topic = {}
    for slug, e in stocks.items():
        tid = e.get("topic_id")
        if tid:
            by_topic.setdefault(tid, []).append(slug)
    for tid, slugs in sorted(by_topic.items()):
        if len(slugs) <= 1:
            continue
        canonical_slug = slugs[0]
        for other in slugs[1:]:
            canonical_slug, _ = _choose_canonical(canonical_slug, other, stocks)
        canonical = stocks[canonical_slug]
        for slug in slugs:
            if slug == canonical_slug:
                continue
            e = stocks[slug]
            copied = []
            for field in SIGNAL_FIELDS:
                if e.get(field) not in (None, "") and canonical.get(field) in (None, ""):
                    copied.append(field)
                    if fix:
                        canonical[field] = e[field]
            msg = f"duplicate topic_id {tid}: {'merged' if fix else 'would merge'} '{slug}' into canonical '{canonical_slug}'"
            if copied:
                msg += f", copied {copied} from '{slug}' (would otherwise be lost)"
            report.append(msg)
            if fix:
                del stocks[slug]
                fixed += 1

    if fix:
        with open(STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)

    # --- 5. screen-ranking.json: a name shouldn't appear in a tier AND screenedOut ---
    if os.path.exists(RANKING_PATH):
        with open(RANKING_PATH) as f:
            ranking = json.load(f)
        tiered_names = set()
        for tier in ("tierA", "tierB", "tierC", "highCaution", "avoid", "exclude"):
            for item in ranking.get(tier, []):
                tiered_names.add(item["name"])
        screened_names = {item["name"] for item in ranking.get("screenedOut", [])}
        overlap = tiered_names & screened_names
        if overlap:
            report.append(f"screen-ranking.json: names in BOTH a tier and screenedOut (contradiction): {sorted(overlap)} - NOT auto-fixed, needs a look")
        note = ranking.get("methodology_note", "")
        if len(note) > 800:
            report.append(f"screen-ranking.json: methodology_note is {len(note)} chars - likely has names creeping back into prose instead of the screenedOut array, worth a look")

        # --- screen-dimension check (replaces the 2026-08-22 keyword past-performance spot-check) ---
        # Each screenedOut entry now carries a {dimensions, primary_screen_reason} block
        # (authored by vpscreen-rerank, mechanically backstopped by
        # scripts/classify_screen_dimensions.py). See scripts/SCREEN_DIMENSIONS_SCHEMA.md.
        # The old block keyword-scanned the free-text reason and flagged ~70 entries/run,
        # none actionable, because almost every deliberate screen-out mentions a catalyst
        # while explaining why it doesn't count. Now: three precise reads.
        #
        #  (1) MIS-SCREEN - the 2026-08-22 bug: screened primarily on a weak multi-year
        #      average while the recent quarters have actually turned, thesis still fits and
        #      governance isn't red. Should be 0-3; every one is worth a look -> move to Tier C.
        #  (2) unclassified count - screen-outs whose dimensions block the mechanical pass
        #      couldn't read; vpscreen-rerank must author these.
        #  (3) legacy keyword fallback - only for entries with NO block yet, and tightened to
        #      require BOTH a trailing-weakness cue AND a recent-strength cue (the actual
        #      mis-screen signature), not merely "a catalyst is mentioned".
        prr_dist = {}
        unclassified = []
        TRAIL_WEAK_CUE = ["weak trailing", "trailing roe", "trailing average", "weak 5yr",
                           "weak 5-yr", "flat 5-yr", "flat 5 yr", "5yr cagr ~-", "5-yr cagr ~-",
                           "revenue cagr ~-", "sales cagr ~-", "3yr roe ~-", "negative 3yr roe",
                           "negative roe"]
        RECENT_STRONG_CUE = ["recent-quarter inflection", "confirmed inflection", "cfo inflection",
                              "earnings inflection", "margin turn", "turned the corner",
                              "recent quarters have turned", "q1 fy27 revenue +5",
                              "q1 fy27 revenue +6", "q1 fy27 revenue +7", "q1 fy27 revenue +8"]
        for item in ranking.get("screenedOut", []):
            name = item["name"]
            dims = item.get("dimensions")
            prr = item.get("primary_screen_reason")
            if dims and prr:
                prr_dist[prr] = prr_dist.get(prr, 0) + 1
                if prr == "unclassified":
                    unclassified.append(name)
                elif (prr == "long_term_fundamentals"
                      and dims.get("recent_fundamentals") == "strong"
                      and dims.get("thesis") != "neither"
                      and dims.get("governance") != "red"):
                    report.append(f"MIS-SCREEN (past-performance bias): screenedOut '{name}' is screened "
                                   f"primarily on weak long-term fundamentals while "
                                   f"dimensions.recent_fundamentals=='strong', the thesis fits and governance "
                                   f"isn't red - the 2026-08-22 pattern. Move to Tier C with 'unconfirmed, "
                                   f"watch' framing. Reason: {item.get('reason', '')!r}")
            else:
                r = item.get("reason", "").lower()
                if any(c in r for c in TRAIL_WEAK_CUE) and any(c in r for c in RECENT_STRONG_CUE):
                    report.append(f"POSSIBLE PAST-PERFORMANCE BIAS (no dimensions block yet): screenedOut "
                                   f"'{name}' pairs a trailing-weakness cue with a recent-strength cue - author "
                                   f"a dimensions block and re-check against analysis.md. Reason: "
                                   f"{item.get('reason', '')!r}")
        if prr_dist:
            report.append("screen dimensions: primary_screen_reason across screenedOut - "
                           + ", ".join(f"{k}={v}" for k, v in sorted(prr_dist.items(), key=lambda kv: -kv[1])))
        if unclassified:
            report.append(f"screen dimensions: {len(unclassified)} screenedOut entries still have "
                           f"primary_screen_reason=='unclassified' - vpscreen-rerank should author real blocks "
                           f"(scripts/classify_screen_dimensions.py is the stopgap). First few: {unclassified[:8]}")

    # --- 6. trusted_threads.json sanity + backlog check ---
    TRUSTED_PATH = os.path.join(BASE, "trusted_threads.json")
    if os.path.exists(TRUSTED_PATH):
        with open(TRUSTED_PATH) as f:
            trusted = json.load(f)
        for name, t in trusted.get("threads", {}).items():
            if not isinstance(t.get("topic_id"), int) or t.get("last_post_number_seen", 0) < 0:
                report.append(f"trusted_threads.json: '{name}' has malformed topic_id/last_post_number_seen - needs a look")
        backlog = [(slug, e) for slug, e in stocks.items()
                   if e.get("source") == "trusted-thread" and e.get("status") == "candidate"]
        very_high_backlog = [slug for slug, e in backlog if e.get("trusted_conviction_strength") == "very-high"]
        # vpscreen-scan's Step 0.5 is uncapped for trusted-thread candidates (drains the whole
        # queue every run, very-high first), so this should rarely build up - if it does, that's
        # a real signal something's wrong (Step 0.5 not running, or being skipped), not just
        # "needs more time" the way it might have under the old 5/run cap.
        if very_high_backlog:
            report.append(f"URGENT: {len(very_high_backlog)} very-high-conviction trusted-thread candidates still "
                           f"unresearched - Step 0.5 is supposed to be uncapped for these, this should not "
                           f"persist across runs: {very_high_backlog}")
        elif len(backlog) > 15:
            report.append(f"trusted_threads.json backlog: {len(backlog)} trusted-thread-sourced candidates still "
                           f"unresearched (all 'high' tier, none 'very-high') - Step 0.5 takes up to 15/run so this "
                           f"should drain within a run or two; worth a look if it keeps growing: "
                           f"{[s for s,_ in backlog[:10]]}")
        for slug, e in backlog:
            strength = e.get("trusted_conviction_strength")
            if strength not in (None, "very-high", "high"):
                report.append(f"trusted_conviction_strength: {slug} has unrecognized value '{strength}' - needs a look")

    # --- 6.5. sovrenn-news seed backlog (report-only) ---
    # Seeded 2026-09-02. vpscreen-scan Step 0.5 tier 4.65 is uncapped within the 10/run batch,
    # so a large candidate backlog persisting many runs means Step 0.5 isn't draining it.
    sov_backlog = [slug for slug, e in stocks.items()
                   if e.get("source") in ("sovrenn-news", "sovrenn-discovery") and e.get("status") == "candidate"]
    if len(sov_backlog) > 30:
        report.append(f"sovrenn-news backlog: {len(sov_backlog)} sovrenn-news candidates still unresearched - "
                       f"tier 4.65 is uncapped, should drain in ~3 runs; worth a look if it isn't shrinking: "
                       f"{sov_backlog[:10]}")

    # --- 7. trusted_users.json sanity ---
    if os.path.exists(TRUSTED_USERS_PATH):
        with open(TRUSTED_USERS_PATH) as f:
            tu = json.load(f)
        crit = tu.get("promotion_criteria", {})
        if "min_total_love" not in crit or "min_posts_seen" not in crit:
            report.append("trusted_users.json: promotion_criteria missing expected keys - needs a look")
        for uname, e in tu.get("users", {}).items():
            if e.get("source") not in ("user-named", "auto-promoted"):
                report.append(f"trusted_users.json: '{uname}' has unrecognized source '{e.get('source')}' - needs a look")
            tier = e.get("trust_tier")
            if tier not in ("core", "elevated"):
                report.append(f"trusted_users.json: '{uname}' has unrecognized/missing trust_tier {tier!r} - needs a look")
            elif tier == "core" and e.get("source") != "user-named":
                # "core" is reserved for a human explicitly naming a user as heavily trusted -
                # promote_trusted_users.py never auto-assigns it. If this ever fires, something
                # hand-edited the file inconsistently (or the auto-promotion script regressed).
                report.append(f"trusted_users.json: '{uname}' has trust_tier='core' but source={e.get('source')!r} "
                               f"(expected 'user-named') - core should only ever be hand-assigned, needs a look")

    print(f"=== audit_state.py report ({'fix applied' if fix else 'dry-run'}) ===")
    print(f"registry size: {len(stocks)} | issues found: {len(report)} | auto-fixed: {fixed}")
    for line in report:
        print(f"- {line}")
    if not report:
        print("(clean - no issues found)")


if __name__ == "__main__":
    main()
