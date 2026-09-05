#!/usr/bin/env python3
"""
migrate_legacy_verdicts.py - ONE-SHOT.

The 34 `source: "legacy-108-screen"` seed entries in state.json each carry a
verbose, FROZEN `legacy_verdict` block (bucket / headline / verdict_reasoning /
bear_case / old_json ...). Nothing mechanical reads it - only the vpscreen-scan
prompt did, during first research. Keeping ~34 multi-line frozen blocks in the
hot 700KB state.json inflates every full read of that file.

This moves each `legacy_verdict` block out to a single sidecar,
data/legacy-verdicts.json, keyed by state.json slug, and drops the block from
state.json. `source_detail` (which already carries a one-line summary of the old
verdict) is left untouched, so a task that never opens the sidecar still sees the
gist. vpscreen-scan's Step 3.05 is updated to read the sidecar instead.

Idempotent: re-running finds nothing to move and just reports the sidecar count.
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")
SIDECAR = os.path.join(BASE, "data", "legacy-verdicts.json")


def dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def main():
    with open(STATE_PATH) as f:
        state = json.load(f)

    sidecar = {}
    if os.path.exists(SIDECAR):
        with open(SIDECAR) as f:
            sidecar = json.load(f)

    moved = 0
    for slug, entry in state["stocks"].items():
        if "legacy_verdict" in entry:
            sidecar[slug] = entry.pop("legacy_verdict")
            moved += 1

    if moved == 0:
        real = len([k for k in sidecar if not k.startswith("_")])
        print(f"nothing to move. sidecar holds {real} legacy verdicts.")
        return

    sidecar["_readme"] = ("Frozen 2026-08-15 verdicts from the original 108-stock screen, "
                          "moved out of state.json by migrate_legacy_verdicts.py. Keyed by "
                          "state.json slug. Read-only reference for vpscreen-scan Step 3.05; "
                          "re-derive conviction fresh, never copy these.")
    dump(SIDECAR, sidecar)
    dump(STATE_PATH, state)
    print(f"moved {moved} legacy_verdict blocks -> {os.path.relpath(SIDECAR, BASE)} "
          f"({len(sidecar) - 1} total entries)")


if __name__ == "__main__":
    main()
