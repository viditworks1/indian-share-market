#!/usr/bin/env python3
"""One-shot: seed Sovrenn Daily News Digest (Apr-Jun 2026) into state.json.

- 25 genuinely-absent names  -> new status:candidate, source:sovrenn-news
- 1 existing untagged candidate (marine-electricals) -> tag source:sovrenn-news
- 11 already-researched names with a material fresh datapoint -> conviction_needs_reverification
- 7 already-researched names, minor/corroborating datapoint -> sovrenn_news note only

Idempotent-ish: refuses to recreate a slug that already exists.
"""
import datetime
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(BASE, "state.json")
TODAY = "2026-09-02"

NEW = {
 "sathlokhar-synergys-ec-global": ("Sathlokhar Synergys E&C Global Ltd",
   "2026-04-02: New orders INR 125 Cr (Reliance Consumer Products INR 102 Cr, EDAC INR 17 Cr, Anabond INR 4 Cr); FY26 turnover >100% YoY; order book INR 991 Cr, project pipeline INR 18,417 Cr, YTD order inflow INR 1,097 Cr.",
   "SME civil/PEB/MEP EPC contractor; large stated order book + pipeline vs size."),
 "chamunda-electricals": ("Chamunda Electricals Ltd",
   "2026-04-02: Letter of Award INR 63 Cr from GETCO for O&M of 88 units of 66 KV sub-stations, 3-year contract.",
   "SME power-substation O&M; annuity-style 3yr contract large vs size."),
 "solarium-green-energy": ("Solarium Green Energy Ltd",
   "2026-04-02: Letter of Award INR 188 Cr as sub-contractor for EPC + 3yr O&M of a 50 MWac solar PV project under MAHAGENCO, Maharashtra.",
   "SME solar EPC (2025 SME IPO); single order ~large vs revenue base."),
 "eco-recycling": ("Eco Recycling Ltd (Ecoreco)",
   "2026-04-28: Q4FY26 sales +90% YoY to INR 18.6 Cr, net profit +250% YoY to INR 7 Cr, OPM ~69%; QoQ sales +215%, PAT +248%.",
   "E-waste recycling microcap; sharp Q4 inflection, high margins, small base."),
 "kirloskar-pneumatic": ("Kirloskar Pneumatic Co Ltd (KPCL)",
   "2026-04-28: Q4FY26 sales +20% YoY INR 712 Cr, net profit +79% YoY INR 144 Cr, OPM 19%->26%; QoQ PAT +246%.",
   "Air/gas compression systems, gas distribution, defence; margin step-up. Likely small/mid-cap, size the 10x bar."),
 "bondada-engineering": ("Bondada Engineering Ltd",
   "2026-04-28: Q4FY26 sales +28% YoY INR 914 Cr, PAT +13% YoY INR 63 Cr. 2026-06-17: NOA INR 1,338 Cr from NTPC Renewable Energy (250 MW solar PV + 50 MW/200 MWh BESS), 18 months; solar EPC order book 5.5 GWp, BESS 1.1 GWh.",
   "Telecom-infra + solar/BESS EPC; very large fresh order vs current revenue."),
 "servotech-renewable-power": ("Servotech Renewable Power Ltd (erst. Servotech Power Systems)",
   "2026-05-04: Q4FY26 sales +49% YoY INR 217 Cr, net profit +38% YoY INR 11 Cr, OPM 8%->10%; QoQ PAT -31%.",
   "EV chargers + solar products mfr; growth strong but thin/volatile margins."),
 "exhicon-events-media-solutions": ("Exhicon Events Media Solutions Ltd",
   "2026-05-04: Partnership with ICICI Lombard to promote exhibition insurance. 2026-05-19: H2FY26 sales +23% YoY INR 100 Cr, net profit +15% YoY INR 23 Cr, OPM ~28%.",
   "SME MICE / events & exhibitions services; steady growth, asset-light."),
 "kp-green-engineering": ("KP Green Engineering Ltd",
   "2026-05-04: New confirmed orders ~INR 507.9 Cr across solar structures, transmission towers, pre-engineered buildings, isolators and infra products.",
   "Fabrication for renewables/T&D/infra (KP group); large order intake vs size."),
 "kp-energy": ("KP Energy Ltd",
   "2026-05-08: Q4FY26 sales +58% YoY INR 632 Cr, net profit +72% YoY INR 79 Cr, OPM 18%->21%; QoQ sales +83%, PAT +93%.",
   "Wind EPC / balance-of-plant + IPP (KP group); strong Q4 inflection."),
 "ceigall-india": ("Ceigall India Ltd",
   "2026-05-08: Q4FY26 sales +37% YoY INR 1,387 Cr, net profit +79% YoY INR 129 Cr, OPM 13%->16%; QoQ sales +40%, PAT +79%.",
   "Roads/highways EPC (structures, elevated corridors, metro); recent IPO. Size the 10x bar."),
 "safe-enterprises-retail-fixtures": ("Safe Enterprises Retail Fixtures Ltd",
   "2026-05-19: H2FY26 sales +31% YoY INR 106 Cr, net profit +41% YoY INR 31 Cr; HoH sales -5%.",
   "SME retail-display fixtures / store fit-out; high PAT margin, lumpy HoH."),
 "kaka-industries": ("Kaka Industries Ltd",
   "2026-05-19: H2FY26 sales +35% YoY INR 138 Cr, net profit +67% YoY INR 10 Cr; HoH sales +10%.",
   "SME PVC profiles / building & furniture products; thin net margin (~7%)."),
 "insolation-energy": ("Insolation Energy Ltd",
   "2026-05-26: Q4FY26 sales +100% YoY INR 794 Cr, net profit +67% YoY INR 70 Cr, OPM ~14% flat; QoQ sales +38%, PAT +37%.",
   "Solar module/cell manufacturer; revenue doubling, commodity-margin watch."),
 "viviana-power-tech": ("Viviana Power Tech Ltd",
   "2026-05-26: H2FY26 sales +2.6x YoY INR 441 Cr, net profit +2.9x YoY INR 44 Cr; HoH sales +4.8x, PAT +4.9x.",
   "SME electrical EPC / EV-charging infra; very steep HoH ramp, check order-book durability."),
 "travel-food-services": ("Travel Food Services Ltd",
   "2026-05-26: Q4FY26 sales +26% YoY INR 461 Cr, net profit +15% YoY INR 123 Cr, OPM 37%->40%.",
   "Airport F&B outlets + lounges; high-margin, recent IPO. Size the 10x bar."),
 "sat-kartar-life": ("Sat Kartar Life Ltd",
   "2026-06-12: NABH accreditation for Sat Kartar Sanjeevan Hospital, Paschim Vihar Extn, New Delhi (Panchakarma / Shalya Tantra / Naturopathy / Yoga), valid to 18 May 2029.",
   "SME Ayurveda / D2C wellness + hospital; accreditation is a soft catalyst, verify financials."),
 "winsol-engineers": ("Winsol Engineers Ltd",
   "2026-06-12: Purchase & Service Order INR 49.80 Cr from KPIG Energia for supply + ETC works on a 400 kV EHV transmission line project in Gujarat (ex-GST).",
   "SME power T&D / EHV substation EPC; single order large vs size."),
 "krm-ayurveda": ("KRM Ayurveda Ltd",
   "2026-06-12: NABH accreditation for Panchakarma Day Care Centre, JP Nagar, Bengaluru. 2026-06-17: new 23-bed Ayurvedic hospital 'MSS Hospital', Pitampura, New Delhi (IPD + OPD).",
   "SME Ayurveda hospital chain in expansion; verify unit economics + funding."),
 "kilburn-engineering": ("Kilburn Engineering Ltd",
   "2026-06-17: First-ever order INR 70.2 Cr from Casale SA, Switzerland for design/engineering/manufacture of process equipment for fertilizer applications.",
   "Industrial drying / process-equipment maker; first export/MNC order = new vector."),
 "arham-technologies": ("Arham Technologies Ltd",
   "2026-06-17: Approved migration of listing from NSE Emerge (SME) to the NSE Main Board.",
   "SME; mainboard migration only - needs a full first-time fundamental read."),
 "desco-infratech": ("Desco Infratech Ltd",
   "2026-06-25: Subsidiary Shri Green Agro Energies commissioned Phase-1 of a 5 TPD CBG plant at Bulandshahr, UP (initial 1 TPD, commercial sales soon) - entry into bio-energy.",
   "SME city-gas / pipeline infra services; CBG is a new adjacency, small scale so far."),
 "vinyas-innovative-technologies": ("Vinyas Innovative Technologies Ltd",
   "2026-06-25: Purchase orders INR 72.21 Cr from domestic customers for manufacture/supply of PCBA, to be executed in 3-6 months.",
   "EMS / defence & aerospace electronics; order large vs size, defence-linked mix."),
 "atmastco": ("Atmastco Ltd",
   "2026-06-25: Domestic order INR 57.33 Cr from L&T-MHI Power Boilers for fabrication/supply of Ceiling Girder (ICB-Boiler Area, 4,368 MT); linked to Adani Korba/Raigarh/Anuppur units.",
   "SME heavy fabrication / steel trading / defence; project-linked large order."),
 "shanti-gold-international": ("Shanti Gold International Ltd",
   "2026-06-25: Board meeting 30 Jun 2026 to consider a fund raise (FPO / rights / ADR-GDR / FCCB / QIP / debt / preferential).",
   "Gold jewellery (22kt CZ) manufacturer, recent IPO; fund-raise intent = dilution/expansion signal, read financials fresh."),
}

# already-researched: material fresh datapoint -> re-verify
REVERIFY = {
 "oriana-power": "2026-04-02: Green Ammonia Purchase Agreement with SECI formalised - 60,000 TPA at INR 52/kg, total contract value INR 3,135 Cr over 10 years (Madhya Bharat Agro end off-taker). Materialises the Aug-2025 LoA.",
 "websol-energy-system-ltd": "2026-04-28: Q4FY26 sales +132% YoY INR 401 Cr, net profit +158% YoY INR 125 Cr; QoQ sales +54%, PAT +92%. OPM 45%->36%.",
 "cosmic-crf-limited": "2026-05-26: H2FY26 sales +78% YoY INR 412 Cr, net profit +2.4x YoY INR 26 Cr; HoH sales +36%. OPM ~10% flat.",
 "zaggle-a-platform-to-address-pain-points-for-enterprises": "2026-06-10: 5-year agreement with Crompton Greaves Consumer Electricals for Zaggle Save (employee expense/benefits SaaS); contract value MAU/spend-linked, not fixed.",
 "veefin-solutions": "2026-06-12: Board to consider migration BSE SME -> BSE Main Board + direct NSE Main Board listing + postal-ballot notice. (Currently EXCLUDED - re-check whether the exclusion still holds.)",
 "aimtron-electronics": "2026-04-28: H2FY26 sales +59% YoY INR 162 Cr, net profit +71% YoY INR 24 Cr; HoH sales +69%. Warrant conversion: 2.32 L shares at INR 680 (~INR 15.8 Cr), paid-up equity to INR 20.84 Cr.",
 "acutaas-chemicals": "2026-05-04: Q4FY26 sales +41% YoY INR 433 Cr, net profit +2.1x YoY INR 134 Cr, OPM 28%->42%; QoQ sales +10%, PAT +26%. Margin expansion + PAT doubling - re-test the 'neither' call vs trailing average.",
 "cartrade-tech-ltd": "2026-05-08: Q4FY26 sales +19% YoY INR 203 Cr, net profit +54% YoY INR 71 Cr, OPM 27%->35%; QoQ sales -3%, PAT +15%. Operating leverage playing out - re-test 'neither'.",
 "abs-marine-services": "2026-06-25: CRISIL upgrade to A-/Stable (from BBB+) and A2+ (from A2); rated facilities enhanced to INR 505.5 Cr (from INR 370.5 Cr). Cites 31% revenue CAGR, 55% operating margin, long-term ONGC/Schlumberger contracts.",
 "epack-prefab-technologies": "2026-05-04: Mambattu (AP) plant capacity expansion - +13,200 MT added to existing 68,112 MT, commercial production from 29 Apr 2026, current utilisation ~60%.",
 "apsis-aerocom": "2026-05-08: Defence-sector supply order ~INR 7.24 Cr from a domestic customer, execution within ~10 months. Small absolute value but material vs this microcap's base.",
}

# already-researched: minor / corroborating datapoint -> note only, no re-verify
NOTE_ONLY = {
 "anant-raj": "2026-04-02: Promoter bought 60,500 shares at avg INR 411 (~INR 2.5 Cr aggregate).",
 "deep-industries": "2026-05-08: Work order INR 78 Cr from Antelopus Selan Energy for integrated drilling services, to be completed within 30 months. (Corroborates existing 10x/Medium view.)",
 "cantabil-india": "2026-05-19: Q4FY26 sales +15% YoY INR 253 Cr, net profit +26% YoY INR 29 Cr, OPM 27%->31%; QoQ sales -4%, PAT -36% (seasonal).",
 "shivalik-bimetal-controls": "2026-05-19: Q4FY26 sales +23% YoY INR 163 Cr, net profit +24% YoY INR 26 Cr, OPM ~22% flat; QoQ sales +22%, PAT +18%. Steady, not an inflection.",
 "fredun-pharmaceuticals": "2026-05-26: Q4FY26 sales +28% YoY INR 213 Cr, net profit +57% YoY INR 11 Cr, OPM 10%->14%; QoQ sales +32%. (Corroborates existing Medium-High/10x view.)",
 "yatharth-hospital-trauma-care-services": "2026-05-26: Q4FY26 sales +47% YoY INR 342 Cr, net profit +15% YoY INR 45 Cr, OPM 25%->23%; QoQ sales +7%.",
 "krishna-defence-allied-industries": "2026-06-17: Order INR 45.6 Cr from Ministry of Defence for special steel products for a shipbuilding project, 8 months. (Corroborates existing Medium-High view; thesis_fit stays a size question.)",
}


def main():
    with open(STATE) as f:
        state = json.load(f)
    stocks = state["stocks"]
    log = []

    # 1. new candidates
    for slug, (name, note, short) in NEW.items():
        if slug in stocks:
            log.append(f"SKIP new {slug}: already exists ({stocks[slug].get('status')})")
            continue
        stocks[slug] = {
            "name": name,
            "status": "candidate",
            "source": "sovrenn-news",
            "sovrenn_note": note,
            "first_seen_date": TODAY,
            "topic_id": None,
            "last_analyzed_date": None,
            "conviction": None,
            "market_cap_tier": None,
            "thesis_fit": None,
            "red_flag_tier": None,
            "revisit_after_30d": False,
            "notes_short": f"Sovrenn Daily News seed ({TODAY}). {short} Microcap/SME, thin or absent VP thread expected — research off latest quarterly + last 2–3 annual reports + 6mo BSE/NSE announcements + news (Step 3.05 topic resolution first). Scan tier 4.65.",
        }
        log.append(f"NEW  {slug}")

    # 2. existing untagged candidate -> tag
    me = "marine-electricals-riding-the-waves-of-expansion"
    if me in stocks and stocks[me].get("status") == "candidate":
        stocks[me]["source"] = "sovrenn-news"
        stocks[me]["sovrenn_note"] = ("2026-06-17: Orders INR 76.4 Cr from STT Global Data Centres India and "
            "Deepak Chem Tech for supply of power distribution systems, 12–18 months.")
        stocks[me]["notes_short"] = (stocks[me].get("notes_short") or "").strip() + \
            " | Sovrenn Daily News (2026-06-17): DC + chem power-distribution orders INR 76.4 Cr. Scan tier 4.65."
        log.append(f"TAG  {me} -> source:sovrenn-news")
    else:
        log.append(f"WARN marine-electricals not a candidate as expected")

    # 3. re-verify
    for slug, reason in REVERIFY.items():
        if slug not in stocks:
            log.append(f"WARN reverify {slug}: not found")
            continue
        e = stocks[slug]
        e.setdefault("sovrenn_news", [])
        e["sovrenn_news"].append({"date": TODAY, "note": reason})
        e["conviction_needs_reverification"] = True
        e["reverification_reason"] = f"Sovrenn Daily News datapoint ({TODAY}): " + reason
        e["last_analyzed_date"] = None  # tier-2 convention: cooldown cleared
        log.append(f"RVRF {slug} (was conviction={e.get('conviction')}, thesis={e.get('thesis_fit')})")

    # 4. note only
    for slug, note in NOTE_ONLY.items():
        if slug not in stocks:
            log.append(f"WARN note {slug}: not found")
            continue
        e = stocks[slug]
        e.setdefault("sovrenn_news", [])
        e["sovrenn_news"].append({"date": TODAY, "note": note})
        log.append(f"NOTE {slug}")

    state.setdefault("meta", {})["last_updated"] = datetime.date.today().isoformat()

    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    os.replace(tmp, STATE)

    print("\n".join(log))
    print(f"\nregistry size now: {len(stocks)}")


if __name__ == "__main__":
    main()
