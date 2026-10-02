# Capacity Expansion Deepdive Staging Status

**Date:** 2026-10-02  
**Status:** 16 candidates staged, awaiting research

---

## Overview

The 16 highest-scoring candidates from Screener.in Capacity Expansion screen (ranks 897-912) have been staged in `state.json` with source `capacity-expansion-deepdive` for integration into the deepdive rotation.

**Current Blocker:** None of the 16 can enter the automated deepdive-queue.json due to Confluence-100 hard-gate (implemented 2026-09-16).

---

## 16 Deepdive Candidates (Ranks 897-912)

| Rank | Slug | Name | Screener Score | P/E | ROCE% | Status |
|------|------|------|-----------------|-----|-------|--------|
| 897 | ksolves-india | Ksolves India | 103.34 | 16.37 | 127.4 | ✅ Existing |
| 898 | ens-enterprises | ENS Enterprises | 95.92 | 16.38 | 115.0 | 📋 Staged |
| 899 | infrax-renewable | Infrax Renewable | 90.40 | 15.98 | 105.3 | 📋 Staged |
| 900 | simca-advertis | Simca Advertis. | 89.19 | 20.78 | 109.7 | 📋 Staged |
| 901 | adon-agro | Adon Agro | 83.26 | 8.92 | 84.0 | 📋 Staged |
| 902 | one-global-serv | One Global Serv | 81.10 | 13.89 | 87.0 | 📋 Staged |
| 903 | tips-music | Tips Music | 80.39 | 38.37 | 118.5 | 📋 Staged |
| 904 | waaree-renewab | Waaree Renewab. | 77.76 | 16.54 | 85.0 | 📋 Staged |
| 905 | icici-amc | ICICI AMC | 74.07 | 43.74 | 115.1 | 📋 Staged |
| 906 | websol-energy | Websol Energy | 70.31 | 9.50 | 63.2 | 📋 Staged |
| 907 | polychem | Polychem | 69.46 | 5.51 | 56.4 | 📋 Staged |
| 908 | fascinate-textiles | Fascinate Textiles | 67.55 | 6.74 | 54.9 | 📋 Staged |
| 909 | genxai-analytics | GenXAI Analytics | 67.38 | 11.20 | 60.6 | 📋 Staged |
| 910 | australian-prem | Australian Prem | 67.20 | 8.06 | 56.1 | 📋 Staged |
| 911 | crizac | Crizac | 60.80 | 13.25 | 52.3 | ✅ Existing |
| 912 | bse | BSE | 40.89 | 43.88 | 60.0 | 📋 Staged |

---

## Integration Workflow

### Current State (2026-10-02)
- ✅ 2/16 candidates existing in state.json (ksolves-india, crizac)
- 📋 14/16 staged as `candidate` status with `pending_deepdive: true`
- ⛔ 0/16 in Confluence-100 (hard-gate blocks automatic queue entry)
- ⛔ Cannot enter deepdive-queue.json until Confluence-100 membership is resolved

### Next Steps
1. **Research Phase:** Execute full deepdive research on the 14 staged candidates (Steps 1-8 of deepdive pipeline)
2. **Confluence Integration:** Once researched, candidates must be added to Confluence-100 ranking to pass hard-gate
3. **Automated Queue Entry:** After Confluence-100 membership, next `build_deepdive_queue.py` run will automatically add eligible entries to the rotation queue
4. **Deepdive Rotation:** Entries will then be included in `deepdive-top100` automated rotation (3 pending per run, prioritized by pool_priority score)

---

## Key Constraints

### Confluence-100 Hard-Gate (2026-09-16)
- Deepdive pool automatically filters to **only** Confluence-100 members
- Large-cap and mega-cap stocks auto-excluded by size filter
- Non-pool entries are inert (status 'not_in_pool') until criteria are met

### Action Required
To move candidates from staged to active deepdive rotation:
1. **Research all 14 pending candidates** (full deepdive, not vpscreen-scan)
2. **Compute master_score and four_box_score** for each
3. **Integrate into Confluence-100 ranking** (rank them among the 100-stock universe)
4. **Verify not large/mega-cap** (small/mid-cap only can stay in pool)

---

## Files
- **state.json:** Entries in `state['stocks']` with source `capacity-expansion-deepdive`
- **CAPACITY_EXPANSION_CANDIDATES.md:** Original 16-candidate list from Screener.in
- **data/deepdive-queue.json:** Active pool (auto-generated, do not hand-edit)

---

*Staging document | 2026-10-02 | Claude Haiku 4.5*
