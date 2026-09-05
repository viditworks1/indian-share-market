#!/usr/bin/env python3
"""
forum_fetch.py - token-lean ValuePickr forum fetch helpers for vpscreen-scan /
vpscreen-portfolio-threads' deep-thread-read steps.

Why this exists: the raw Discourse `t/<topic_id>.json` and
`t/<topic_id>/posts.json` endpoints return ~70 fields per post
(avatar_template, flair_*, moderator/admin/staff flags, badges_granted,
can_edit/delete/recover, reads/readers_count, trust_level, quote_count, ...)
and the topic endpoint additionally embeds the first ~20 posts IN FULL even
when a caller only wants `post_stream.stream` + `highest_post_number`.
Measured on a real ~1000-post VP thread: the topic.json call alone is ~80KB
for two scalars, and each bulk-fetched post is ~60% metadata a stock-research
task never uses. A bare `curl -s "<url>"` with no post-processing puts all of
that raw JSON directly into the calling model's context. These two
subcommands do the fetch AND the field-trim server-side, so only what the
task actually reads (the stream-math result, or post text/author/date/love)
reaches the model.

Built-in 1.5s rate-limit sleep before every request happens inside this
script - a caller using `probe`/`posts` does not need its own
`sleep 1.5 &&` prefix for these two calls (still use it for any OTHER
forum.valuepickr.com curl the task makes directly, e.g. search.json).

Usage:
  forum_fetch.py probe <topic_id> [--checkpoint N] [--batch B] [--first-time-limit 50] [--recheck-cap 200]
      -> {highest_post_number, mode, new_count, post_ids_to_fetch, has_more, note}
      mode: "first-time" | "no-new" | "bulk" | "partial-catchup"
      Replaces: curl the topic.json, eyeball post_stream.stream, do the
      checkpoint math by hand. checkpoint = the stock's last_post_number_analyzed
      (omit for a first-time read). post_ids_to_fetch is what to pass to `posts`.
      For a first-time read's 4-batch escalation ladder: --batch 1 (default) is
      the most recent 50 posts, --batch 2 the 50 before that, --batch 3/4
      likewise -- each call is a fresh, cheap topic.json fetch (the same one
      probe always makes), just sliced to a different non-overlapping window.
      `has_more: false` means batch reached post #1 (nothing earlier to escalate to).

  forum_fetch.py probe <topic_id> --before N [--limit 100]
      -> {highest_post_number, mode:"backfill", post_ids_to_fetch,
          lowest_post_number_in_batch, highest_post_number_in_batch,
          reached_start, note}
      vpscreen-portfolio-threads Step 1's historical-backfill pattern: fetch
      up to --limit posts immediately OLDER than post_number --before (pass
      `last_post_number_seen` or `backfill_progress_post_number`, whichever is
      the thread's current backfill checkpoint). `reached_start: true` means
      the batch hit post #1 - set `backfill_complete: true` per that step's rule.

  forum_fetch.py posts <topic_id> --ids 123,456,789
      -> [{"post_number", "id", "username", "created_at", "love_count", "text"}, ...]
      text = the post's `cooked` HTML with tags stripped, entities unescaped,
      whitespace collapsed - the same substance a model would extract from
      the raw HTML anyway, just done once here instead of the model re-reading
      markup on every post.
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.request

BASE_URL = "https://forum.valuepickr.com"
RATE_LIMIT_SECONDS = 1.5


def _fetch(url):
    time.sleep(RATE_LIMIT_SECONDS)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _strip_html(cooked):
    if not cooked:
        return ""
    text = re.sub(r"<[^>]+>", " ", cooked)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def cmd_probe(args):
    data = _fetch(f"{BASE_URL}/t/{args.topic_id}.json")
    stream = data.get("post_stream", {}).get("stream", [])
    highest = data.get("highest_post_number", len(stream))

    if args.before is not None:
        # Backfill mode (vpscreen-portfolio-threads Step 1): fetch up to --limit
        # posts immediately OLDER than post_number --before (already-seen point).
        end_idx = args.before - 1  # exclusive; post_number P is at index P-1
        start_idx = max(0, end_idx - args.limit)
        ids = stream[start_idx:end_idx]
        out = {
            "highest_post_number": highest,
            "mode": "backfill",
            "post_ids_to_fetch": ids,
            "lowest_post_number_in_batch": start_idx + 1 if ids else None,
            "highest_post_number_in_batch": end_idx if ids else None,
            "reached_start": start_idx == 0,
            "note": (f"backfill batch: post_numbers {start_idx+1}-{end_idx} ({len(ids)} posts)"
                     + (", reached post #1" if start_idx == 0 else "")) if ids
                    else "nothing before this point (already at post #1)",
        }
    elif args.checkpoint is None:
        # First-time read, in non-overlapping 50-post windows counting backward
        # from the most recent post: --batch 1 = last 50, --batch 2 = the 50
        # before that, etc. -- this is what the 4-batch escalation ladder reads.
        window = args.first_time_limit
        end = max(0, len(stream) - (args.batch - 1) * window)
        start = max(0, end - window)
        ids = stream[start:end]
        out = {
            "highest_post_number": highest,
            "mode": "first-time",
            "new_count": None,
            "post_ids_to_fetch": ids,
            "has_more": start > 0,
            "note": f"first-time read, batch {args.batch} ({len(ids)} posts, "
                    f"positions {start+1}-{end} of {len(stream)}"
                    + (", more available" if start > 0 else ", reached the start of the thread") + ")",
        }
    else:
        # NOTE: positional slicing assumes stream position i <-> post_number i+1,
        # which can drift if posts were deleted earlier in the thread (stream/
        # posts_count can then run behind highest_post_number). This is the same
        # assumption the pre-existing manual "stream entries with post_number >
        # checkpoint" process made - mechanized here, not newly introduced.
        new_ids = stream[args.checkpoint:]
        new_count = len(new_ids)
        if new_count == 0:
            out = {
                "highest_post_number": highest,
                "mode": "no-new",
                "new_count": 0,
                "post_ids_to_fetch": [],
                "note": "no new forum activity since the checkpoint",
            }
        elif new_count <= args.recheck_cap:
            out = {
                "highest_post_number": highest,
                "mode": "bulk",
                "new_count": new_count,
                "post_ids_to_fetch": new_ids,
                "note": f"{new_count} new posts since checkpoint",
            }
        else:
            out = {
                "highest_post_number": highest,
                "mode": "partial-catchup",
                "new_count": new_count,
                "post_ids_to_fetch": new_ids[-args.recheck_cap:],
                "note": f"{new_count} new posts since checkpoint - fetching most recent {args.recheck_cap} only",
            }
    print(json.dumps(out))


def cmd_posts(args):
    ids = [i.strip() for i in args.ids.split(",") if i.strip()]
    if not ids:
        print(json.dumps([]))
        return
    qs = "&".join(f"post_ids[]={i}" for i in ids)
    data = _fetch(f"{BASE_URL}/t/{args.topic_id}/posts.json?{qs}")
    posts = data.get("post_stream", {}).get("posts", data.get("posts", []))
    out = []
    for p in posts:
        love = 0
        for a in (p.get("actions_summary") or []):
            if a.get("id") == 2:
                love = a.get("count", 0)
                break
        out.append({
            "post_number": p.get("post_number"),
            "id": p.get("id"),
            "username": p.get("username"),
            "created_at": p.get("created_at"),
            "love_count": love,
            "text": _strip_html(p.get("cooked", "")),
        })
    print(json.dumps(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_probe = sub.add_parser("probe")
    p_probe.add_argument("topic_id")
    p_probe.add_argument("--checkpoint", type=int, default=None,
                          help="last_post_number_analyzed; omit for a first-time read")
    p_probe.add_argument("--batch", type=int, default=1,
                          help="first-time mode only: which 50-post window back from the most recent post (1-4)")
    p_probe.add_argument("--first-time-limit", type=int, default=50,
                          help="first-time mode only: window size per batch")
    p_probe.add_argument("--recheck-cap", type=int, default=200)
    p_probe.add_argument("--before", type=int, default=None,
                          help="backfill mode: fetch posts immediately older than this post_number")
    p_probe.add_argument("--limit", type=int, default=100,
                          help="backfill mode only: max posts per batch")
    p_probe.set_defaults(func=cmd_probe)

    p_posts = sub.add_parser("posts")
    p_posts.add_argument("topic_id")
    p_posts.add_argument("--ids", required=True, help="comma-separated post ids")
    p_posts.set_defaults(func=cmd_posts)

    args = ap.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
