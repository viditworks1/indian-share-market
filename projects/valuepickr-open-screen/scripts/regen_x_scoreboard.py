#!/usr/bin/env python3
"""
Mechanically regenerates x-handles/x-handle-scoreboard.md from the per-handle
dossiers (x-handles/dossiers/<handle>.md, JSON front-matter block) + the registry.
Pure aggregation — no network, no LLM judgment. The x-handle-ranking task fills the
per-call `our_verdict` / `since_call_pct` fields in each dossier and the
`promotion_state` in the registry; this script only scores and renders.

Dossier front-matter contract (first ```json fenced block in the file):
{
  "handle": str, "scraped_date": "YYYY-MM-DD", "window": "start..end",
  "n_tweets_scanned": int, "cadence": "high|medium|low|dormant",
  "discloses_names": bool, "disclaimer_pattern": "none|light|heavy|refuses",
  "calls": [ { "stock": str, "slug": str, "date": "YYYY-MM-DD",
              "direction": "bull|bear|exit", "conviction": "very-high|high|medium|watch",
              "quote": str, "new_to_screen": bool,
              "our_verdict": null|"agree-strong"|"agree"|"mixed"|"disagree"|"red-flag"|"unverified",
              "since_call_pct": null|number } ],
  "watch_only_names": [str]
}
"""
import json, os, re, datetime
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSS = os.path.join(BASE, "x-handles", "dossiers")
REG = os.path.join(BASE, "x-handles", "x_handle_registry.json")
OUT = os.path.join(BASE, "x-handles", "x-handle-scoreboard.md")

VERDICT_PTS = {"agree-strong": 6, "agree": 3, "mixed": 0, "unverified": 0,
               "disagree": -4, "red-flag": -8}

# promotion bar (advisory only — x-cluster-promotion task proposes, human edits x_cluster.json)
PROMO = dict(min_resolved_calls=6, min_corroboration_rate=0.55, min_original=2)
DROP = dict(max_usable_calls=1, min_disagree_rate=0.70)


def parse_front_matter(path):
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def score(fm):
    calls = fm.get("calls", [])
    resolved = [c for c in calls if c.get("our_verdict") in VERDICT_PTS]
    n = len(resolved)
    s = 40.0
    comp = {}
    if n:
        avg_v = sum(VERDICT_PTS[c["our_verdict"]] for c in resolved) / n
        corr = round(avg_v / 6 * 25, 1)          # -33..+25 -> effectively clamp below
        corr = max(-25.0, min(25.0, corr))
        s += corr
        comp["corroboration"] = corr
    orig = sum(1 for c in resolved
               if c.get("new_to_screen") and c.get("direction") == "bull"
               and c.get("our_verdict") in ("agree", "agree-strong"))
    comp["originality"] = min(orig * 4, 16)
    s += comp["originality"]
    pcts = [c["since_call_pct"] for c in resolved if isinstance(c.get("since_call_pct"), (int, float))]
    if pcts:
        mean_pct = sum(pcts) / len(pcts)
        sc = max(-15.0, min(15.0, mean_pct / 4))   # +60% avg -> +15
        comp["since_call"] = round(sc, 1)
        s += sc
    comp["volume"] = min(n, 10)
    s += comp["volume"]
    dp = fm.get("disclaimer_pattern", "none")
    if dp == "heavy":
        s -= 5; comp["disclaimer"] = -5
    if fm.get("cadence") == "dormant":
        s -= 10; comp["cadence"] = -10
    s = max(0.0, min(100.0, s))
    if dp == "refuses":
        s = min(s, 45.0); comp["refuses_names_cap"] = 45
    disagree_rate = (sum(1 for c in resolved if c["our_verdict"] in ("disagree", "red-flag")) / n) if n else 0.0
    corr_rate = (sum(1 for c in resolved if c["our_verdict"] in ("agree", "agree-strong")) / n) if n else 0.0
    promo = (n >= PROMO["min_resolved_calls"] and corr_rate >= PROMO["min_corroboration_rate"]
             and orig >= PROMO["min_original"])
    drop = (len([c for c in calls if c.get("our_verdict") not in (None, "unverified")]) <= DROP["max_usable_calls"]
            or (n >= 4 and disagree_rate >= DROP["min_disagree_rate"]))
    return round(s, 1), comp, dict(n_resolved=n, corr_rate=round(corr_rate, 2),
                                   disagree_rate=round(disagree_rate, 2), original=orig,
                                   promo=promo, drop=drop)


def main():
    reg = json.load(open(REG))
    by_handle = {r["handle"].lower(): r for r in reg["handles"]}
    rows = []
    for fn in sorted(os.listdir(DOSS)):
        if not fn.endswith(".md"):
            continue
        fm = parse_front_matter(os.path.join(DOSS, fn))
        if not fm:
            continue
        sc, comp, meta = score(fm)
        h = fm.get("handle", fn[:-3])
        rr = by_handle.get(h.lower())
        if rr:
            rr["x_handle_score"] = sc
            rr["score_components"] = comp
            rr["last_scored_date"] = datetime.date.today().isoformat()
            rr["promotion_state"] = ("promote-candidate" if meta["promo"]
                                     else "drop-candidate" if meta["drop"] else "hold")
        rows.append((sc, h, fm, meta, comp))
    rows.sort(key=lambda x: -x[0])
    json.dump(reg, open(REG, "w"), indent=2, ensure_ascii=False)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# X-handle Scoreboard (mechanical — regenerated by regen_x_scoreboard.py)\n\n")
        f.write(f"Generated: {datetime.date.today().isoformat()} · {len(rows)} handles with a dossier.\n\n")
        f.write("Score 0-100 from resolved calls in each dossier: corroboration with our own "
                "research (±25), originality/early calls (+16), since-call price move (±15), "
                "call volume (+10), base 40; penalties for heavy disclaimers / dormancy / "
                "refusing to name. Advisory only — promotion into `x_cluster.json` stays a human edit.\n\n")
        f.write("| # | Handle | Score | Resolved | Corrob. | Disagree | Original | State |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for i, (sc, h, fm, meta, comp) in enumerate(rows, 1):
            f.write(f"| {i} | @{h} | {sc} | {meta['n_resolved']} | {meta['corr_rate']} | "
                    f"{meta['disagree_rate']} | {meta['original']} | {'**PROMOTE?**' if meta['promo'] else 'drop?' if meta['drop'] else ''} |\n")

        proms = [r for r in rows if r[3]["promo"]]
        drops = [r for r in rows if r[3]["drop"]]
        f.write("\n## Promotion candidates (>= {min_resolved_calls} resolved calls, corrob >= {min_corroboration_rate}, >= {min_original} original)\n\n".format(**PROMO))
        if proms:
            for sc, h, fm, meta, comp in proms:
                f.write(f"- **@{h}** — score {sc}, {meta['n_resolved']} resolved, corrob {meta['corr_rate']}, "
                        f"{meta['original']} original. Propose → `x_cluster.json` cluster-tier.\n")
        else:
            f.write("_(none this cycle)_\n")
        f.write("\n## Drop candidates (<= 1 usable call, or >=70% disagree over >=4 calls)\n\n")
        if drops:
            for sc, h, fm, meta, comp in drops:
                f.write(f"- **@{h}** — score {sc}, {meta['n_resolved']} resolved, disagree {meta['disagree_rate']}. "
                        f"Propose → stop re-scoring (tier: rejected), archive dossier.\n")
        else:
            f.write("_(none this cycle)_\n")

        f.write("\n## Corroborated original calls (early names our research later agreed with)\n\n")
        any_c = False
        for sc, h, fm, meta, comp in rows:
            for c in fm.get("calls", []):
                if c.get("new_to_screen") and c.get("direction") == "bull" and c.get("our_verdict") in ("agree", "agree-strong"):
                    any_c = True
                    f.write(f"- `{c.get('slug')}` — @{h} ({c.get('date')}): {c.get('quote','')[:120]}\n")
        if not any_c:
            f.write("_(none yet)_\n")

    print(f"x-handle-scoreboard.md: {len(rows)} handles ranked")


if __name__ == "__main__":
    main()
