#!/usr/bin/env python3
"""
Resolves the on-disk data/<...>.json path for a stock from its state.json key
(the "slug").

Usually this is simply data/<slug>.json. But state.json keys are derived from
a stock's forum topic_slug, which for long/awkward thread titles gets recorded
verbatim (e.g. "hbl-engineering-booting" from
"hbl-engineering-booting-up-for-the-race-of-the-century"), while the actual
research data file uses a shorter, cleaner basename (data/hbl-engineering.json).
data/deepdive-queue.json's `data_file` field is the established source of truth
for this mapping (13 stocks currently differ from the naive data/<slug>.json
guess) - scripts that skip it will silently treat those stocks' data as absent
rather than erroring, since a missing file and an "unassessed" stock look the
same to a naive DATA_DIR/f"{slug}.json" open.

Usage:
    from resolve_data_file import resolve_data_path
    data_path = resolve_data_path(BASE, DATA_DIR, slug)
"""
import json
import os

_cache = {}  # data_dir -> {state_key: data_file}


def _load_map(data_dir):
    if data_dir in _cache:
        return _cache[data_dir]
    mapping = {}
    queue_path = os.path.join(data_dir, "deepdive-queue.json")
    try:
        with open(queue_path) as f:
            q = json.load(f)
        for entry in q.get("queue", []):
            state_key = entry.get("state_key")
            data_file = entry.get("data_file")
            if state_key and data_file:
                mapping[state_key] = data_file
    except (OSError, json.JSONDecodeError):
        pass
    _cache[data_dir] = mapping
    return mapping


def resolve_data_path(base, data_dir, slug):
    """Absolute path to `slug`'s data file, honoring deepdive-queue.json's
    explicit data_file override when the slug differs from its filename."""
    override = _load_map(data_dir).get(slug)
    if override:
        return os.path.join(base, override)
    return os.path.join(data_dir, f"{slug}.json")
