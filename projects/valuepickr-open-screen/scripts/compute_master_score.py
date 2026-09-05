#!/usr/bin/env python3
"""
compute_master_score.py
========================

Computes `consistency_score`, `asymmetry_score`, and a composite `master_score`
(all 0-100) for every researched stock — see MASTER_SCORE_METHODOLOGY.md for the
full rationale (built 2026-09-05 from a research pass over real high-return
investors' documented methods: Jhunjhunwala, Kedia, Pabrai, Akre, Terry Smith,
Mukherjea, Sleep, Lynch, Porinju, Basant Maheshwari, Li Lu).

PURELY MECHANICAL, like every other score in this pipeline. No LLM, no network.

  consistency_score (Mukherjea's Coffee Can mechanism — persistence, not a
  point-in-time read): from data/<slug>.json's `track_record` block —
      consistency_score = round(100 * years_cleared / years_checked)   if years_checked >= 3
                         = not assessed                                 otherwise (too young)

  asymmetry_score (Pabrai's "heads I win, tails I don't lose much"): needs NO
  new data — purely a recombination of expectation_gap_score (the upside) and
  quality_score's own debt_component/fcf_component (the downside cushion):
      upside              = expectation_gap_score
      downside_protection = ((debt_component/20) + (fcf_component/25)) / 2 * 100
      asymmetry_score     = 0.5 * upside + 0.5 * downside_protection
                            not assessed if either input is missing

  master_score: weighted average, RENORMALIZED over whichever components are
  actually present (never fabricated, never zero-filled for a missing one):
      conviction_score        weight 0.25
      quality_score           weight 0.25
      expectation_gap_score   weight 0.20
      consistency_score       weight 0.15
      asymmetry_score         weight 0.15
      master_score = sum(weight_i * score_i for present i) / sum(weight_i for present i)
      requires conviction_score present, else not assessed (no research yet).

No red-flag multiplier is applied a second time here — conviction_score and
quality_score each already apply their own, and that propagates through the
weighted average.

USAGE
-----
    python3 compute_master_score.py      (from scripts/ or project root)

Writes:
  - state.json: adds/overwrites `consistency_score`, `asymmetry_score`,
    `master_score` (each independently, only where computable) on every
    researched-status stock entry.
  - data/master-scores.json: {ranked, not_assessed}, each with a
    score_breakdown per stock.
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "state.json")
DATA_DIR = os.path.join(BASE, "data")
QUALITY_SCORES_PATH = os.path.join(DATA_DIR, "quality-scores.json")
OUT_PATH = os.path.join(DATA_DIR, "master-scores.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_data_file import resolve_data_path  # noqa: E402

RESEARCHED_STATUSES = ("researched", "excluded", "avoid")
MIN_YEARS_FOR_CONSISTENCY = 3

MASTER_WEIGHTS = {
    "conviction_score": 0.25,
    "quality_score": 0.25,
    "expectation_gap_score": 0.20,
    "consistency_score": 0.15,
    "asymmetry_score": 0.15,
}


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def load_quality_breakdowns():
    """slug -> {debt_component, fcf_component} from data/quality-scores.json's
    ranked+weak lists (the aggregate quality_score alone, on state.json, doesn't
    carry the sub-terms asymmetry_score needs)."""
    out = {}
    qs = load_json(QUALITY_SCORES_PATH, default={})
    for r in (qs.get("ranked") or []) + (qs.get("weak") or []):
        slug = r.get("slug")
        bd = r.get("score_breakdown") or {}
        if slug:
            out[slug] = {
                "debt_component": bd.get("debt_component"),
                "fcf_component": bd.get("fcf_component"),
            }
    return out


def compute_consistency_score(slug, warnings):
    data_path = resolve_data_path(BASE, DATA_DIR, slug)
    data = load_json(data_path)
    if not isinstance(data, dict):
        return None, None
    tr = data.get("track_record")
    if not isinstance(tr, dict):
        return None, None
    years_checked = tr.get("years_checked")
    years_cleared = tr.get("years_cleared")
    if not isinstance(years_checked, int) or years_checked < MIN_YEARS_FOR_CONSISTENCY:
        return None, tr  # too young / not enough history -- not assessed, not penalized
    if not isinstance(years_cleared, int):
        warnings.append((slug, f"track_record.years_cleared missing/invalid ({years_cleared!r}) with years_checked={years_checked} -> not assessed"))
        return None, tr
    if years_cleared > years_checked:
        warnings.append((slug, f"track_record.years_cleared ({years_cleared}) > years_checked ({years_checked}) -> clamped"))
        years_cleared = years_checked
    score = clamp(round(100 * years_cleared / years_checked), 0, 100)
    return score, tr


def compute_asymmetry_score(expectation_gap_score, quality_breakdown):
    if not isinstance(expectation_gap_score, (int, float)):
        return None
    if not isinstance(quality_breakdown, dict):
        return None
    debt_c = quality_breakdown.get("debt_component")
    fcf_c = quality_breakdown.get("fcf_component")
    if not isinstance(debt_c, (int, float)) or not isinstance(fcf_c, (int, float)):
        return None
    downside_protection = ((debt_c / 20.0) + (fcf_c / 25.0)) / 2.0 * 100.0
    upside = expectation_gap_score
    return clamp(round(0.5 * upside + 0.5 * downside_protection, 2), 0, 100)


def compute_master_score(entry, consistency_score, asymmetry_score):
    conviction = entry.get("conviction_score")
    if not isinstance(conviction, (int, float)):
        return None, None  # no research signal at all -- not assessed

    candidates = {
        "conviction_score": conviction,
        "quality_score": entry.get("quality_score"),
        "expectation_gap_score": entry.get("expectation_gap_score"),
        "consistency_score": consistency_score,
        "asymmetry_score": asymmetry_score,
    }
    used = {k: v for k, v in candidates.items() if isinstance(v, (int, float))}
    total_weight = sum(MASTER_WEIGHTS[k] for k in used)
    weighted_sum = sum(MASTER_WEIGHTS[k] * v for k, v in used.items())
    master = clamp(round(weighted_sum / total_weight, 2), 0, 100)
    breakdown = {k: (used.get(k)) for k in MASTER_WEIGHTS}
    breakdown["components_used"] = sorted(used.keys())
    breakdown["weight_coverage"] = round(total_weight, 2)
    return master, breakdown


def main():
    state = load_json(STATE_PATH)
    if state is None:
        print(f"ERROR: {STATE_PATH} not found", file=sys.stderr)
        sys.exit(1)
    stocks = state.get("stocks", {})
    quality_breakdowns = load_quality_breakdowns()

    warnings = []
    ranked, not_assessed = [], []
    skipped_not_researched = 0
    n_consistency = 0
    n_asymmetry = 0

    for slug, entry in stocks.items():
        if entry.get("status") not in RESEARCHED_STATUSES:
            skipped_not_researched += 1
            continue

        consistency_score, track_record = compute_consistency_score(slug, warnings)
        asymmetry_score = compute_asymmetry_score(
            entry.get("expectation_gap_score"), quality_breakdowns.get(slug)
        )
        if consistency_score is not None:
            entry["consistency_score"] = consistency_score
            n_consistency += 1
        else:
            entry.pop("consistency_score", None)
        if asymmetry_score is not None:
            entry["asymmetry_score"] = asymmetry_score
            n_asymmetry += 1
        else:
            entry.pop("asymmetry_score", None)

        master, breakdown = compute_master_score(entry, consistency_score, asymmetry_score)
        if master is None:
            entry.pop("master_score", None)
            not_assessed.append({"slug": slug, "name": entry.get("name", slug)})
            continue
        entry["master_score"] = master
        ranked.append({
            "slug": slug,
            "name": entry.get("name", slug),
            "master_score": master,
            "red_flag_tier": entry.get("red_flag_tier"),
            "conviction": entry.get("conviction"),
            "thesis_fit": entry.get("thesis_fit"),
            "track_record": track_record,
            "score_breakdown": breakdown,
        })

    ranked.sort(key=lambda r: r["master_score"], reverse=True)

    out = {
        "method": "Composite of conviction_score/quality_score/expectation_gap_score/"
                  "consistency_score/asymmetry_score, weighted 0.25/0.25/0.20/0.15/0.15 and "
                  "renormalized over whichever are present. Formula + investor research in "
                  "MASTER_SCORE_METHODOLOGY.md.",
        "scored_count": len(ranked),
        "not_assessed_count": len(not_assessed),
        "consistency_score_coverage": n_consistency,
        "asymmetry_score_coverage": n_asymmetry,
        "ranked": ranked,
        "not_assessed": not_assessed,
    }

    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)

    print("=== compute_master_score.py ===")
    print(f"scored {len(ranked)} stocks with master_score "
          f"({n_consistency} with consistency_score, {n_asymmetry} with asymmetry_score); "
          f"{len(not_assessed)} not yet assessed (no conviction_score); "
          f"{skipped_not_researched} candidates skipped, no research yet")
    if warnings:
        print(f"WARNING: {len(warnings)} field warnings:")
        for slug, msg in warnings[:20]:
            print(f"  {slug}: {msg}")
    print(f"wrote scores into {STATE_PATH}")
    print(f"wrote ranked report to {OUT_PATH}")
    if ranked:
        print("\nTop 10 by master_score:")
        for r in ranked[:10]:
            print(f"  {r['master_score']:6.2f}  {r['slug']:44s} "
                  f"used={'+'.join(r['score_breakdown']['components_used'])}")


if __name__ == "__main__":
    main()
