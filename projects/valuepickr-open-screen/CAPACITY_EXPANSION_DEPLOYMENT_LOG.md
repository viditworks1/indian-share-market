# Capacity Expansion Screen — Pipeline Deployment Log

**Date:** 2026-10-02  
**Status:** ✅ DEEPDIVE INTEGRATION COMPLETE | ⏳ VPSCREEN-SCAN PENDING REVIEW

---

## Summary

Successfully integrated **116 new stock candidates** from Screener.in's "Capacity Expansion" screen:

✅ **16 candidates** → Deepdive queue (ranks 897-912, LIVE)  
⏳ **100 candidates** → VPscreen-scan pending batch (ready)

---

## Deepdive Queue Integration ✅ LIVE

**File:** `deepdive-queue.json`  
**Change:** 896 → 912 entries (+16)  
**Ranks:** 897-912  
**Commit:** `27cb50b` (2026-10-02)

### Top 5 Candidates
1. **Ksolves India** (103.34) — IT services; ROCE 127%, P/E 16.37, CMP 241
2. **ENS Enterprises** (95.92) — ROCE 115%, P/E 16.38, CMP 101
3. **Infrax Renewable** (90.40) — Clean energy; ROCE 105%, P/E 15.98, CMP 114
4. **Simca Advertis.** (89.19) — Media; ROCE 110%, P/E 20.78, CMP 290
5. **Adon Agro** (83.26) — **Lowest P/E (8.92)**; ROCE 84%, CMP 90

### Full List (Ranks 897-912)
All 16 candidates now in active deepdive rotation. Next deepdive-top100 run will begin processing based on pool priority and rotation rules.

---

## VPscreen-Scan Batch ⏳ READY

**Count:** 100 candidates (rows 17-116)  
**Tier:** 3.5 (new discovery)  
**File:** `vpscreen_pending_candidates.json`  
**Status:** Ready for manual integration

### Processing Plan
- Max 5/week
- Total clearance: ~20 weeks
- Gate: Sector identification required before conviction scoring

---

## Quality Metrics

| Metric | Value |
|--------|-------|
| Source | Screener.in Capacity Expansion (1,161 total) |
| Filtered (deepdive) | 16 (1.4% pass rate) |
| Filtered (vpscreen) | 100 (8.6% of 1,161) |
| Avg ROCE | 84.4% |
| Avg P/E | 18.07x |
| Portfolio overlap | 0 (100% new) |
| New sectors | 7+ (Renewables, Agro, IT, Media, Chemicals, Textiles) |

---

## Processing Status

**Deepdive Queue**
- ✅ 16 candidates merged
- ✅ Ranked by analysis score (897-912)
- ✅ Ready for next rotation
- ⏳ Processing begins next deepdive-top100 run

**VPscreen-Scan**
- ✅ 100 candidates staged
- ⏳ Manual state.json integration pending
- ⏳ Processing begins tier 3.5 queue

---

## Commit History

```
27cb50b Add 16 Capacity Expansion candidates to deepdive queue (ranks 897-912)
```

---

*Deployment by Claude Code | 2026-10-02*
