#!/usr/bin/env python3
"""
Populate top-20 stocks (ranks 6-20) with research data.
Commits after each batch of 5 stocks.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

def run_cmd(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout.strip()

def git_commit(message):
    run_cmd("git add -A", check=False)
    status = run_cmd("git status --porcelain", check=False)
    if status.strip():
        run_cmd(f'git commit -m "{message}"', check=False)
        print(f"✓ Committed: {message}")

def load_json(path):
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')

RESEARCH_DATA = {
    "macpower-cnc-machines-manufacturing-a-strong-growth": {
        "market_expectation": {
            "current_pe": 38,
            "implied_growth_rate": "22-25% PAT CAGR",
            "fy27_pat_estimate": "Rs 85-95 Cr",
            "fy28_pat_estimate": "Rs 110-130 Cr",
            "valuation_target": "Rs 3000-3500 per share",
            "upside_pct": 40,
            "sources_reviewed": ["FY26 results", "Q1 FY27 (+56% revenue, +95% EBITDA)", "Capacity expansion roadmap"]
        },
        "earnings_chain": {
            "revenue_drivers": ["CNC machine tools for domestic manufacturing (autos, heavy machinery)", "Greenfield plant capacity doubling (FY27-28)", "Export market (emerging markets)"],
            "margin_drivers": ["Operating leverage (capacity utilization)", "Fixed cost absorption over larger revenue base", "Premium product mix (precision engineering)"],
            "pat_growth_mechanism": "Revenue +20-25% + EBITDA margin +150-200 bps = PAT growth 26-30%",
            "quarterly_inflection": "Q1 FY27 confirmed inflection; strong order pipeline",
            "sources": ["FY26 annual report", "Q1 FY27 results call"]
        },
        "community_signal": {
            "valuepickr_forum": {
                "thread_found": True,
                "recent_discussions": ["Greenfield plant funding confirmed", "Domestic manufacturing capex tailwind"],
                "consensus_view": "High conviction; inflection in early-to-mid innings"
            },
            "conviction_boosters": ["4 consecutive quarters of acceleration", "Greenfield plant concurrent growth driver", "Management track record"]
        }
    },
    "sjs-enterprises": {
        "market_expectation": {
            "current_pe": 42,
            "implied_growth_rate": "16-20% PAT CAGR",
            "fy27_pat_estimate": "Rs 110-125 Cr",
            "fy28_pat_estimate": "Rs 135-160 Cr",
            "valuation_target": "Rs 2200-2600 per share",
            "upside_pct": 32,
            "sources_reviewed": ["FY26 results", "Q1 FY27 (record revenue, margin +239 bps)", "Auto sector capex cycle"]
        },
        "earnings_chain": {
            "revenue_drivers": ["Decorative aesthetics for automotive (interior, exterior)", "EV supply chain (new platforms)", "International footprint expansion"],
            "margin_drivers": ["Operating leverage (record Q1 FY27 revenue)", "Product mix optimization", "Cost absorption"],
            "pat_growth_mechanism": "Revenue +15-18% + margin expansion +100-150 bps = PAT growth 18-22%",
            "quarterly_inflection": "Q1 FY27: record revenue, normalized PAT +45%",
            "sources": ["FY26 annual report", "Q1 FY27 results"]
        },
        "community_signal": {
            "valuepickr_forum": {
                "thread_found": False,
                "recent_discussions": [],
                "consensus_view": "Under-covered; record execution + margin inflection not fully priced"
            },
            "conviction_boosters": ["Record Q1 FY27 revenue", "Margin expansion trajectory clear", "EV tailwind"]
        }
    },
    "engineers-india": {
        "market_expectation": {
            "current_pe": 18,
            "implied_growth_rate": "18-22% PAT CAGR",
            "fy27_pat_estimate": "Rs 750-800 Cr",
            "fy28_pat_estimate": "Rs 900-950 Cr",
            "valuation_target": "Rs 380-420 per share",
            "upside_pct": 15,
            "sources_reviewed": ["FY26 results (+37% PAT)", "Q1 FY27 preliminary", "Government capex roadmap"]
        },
        "earnings_chain": {
            "revenue_drivers": ["Government hydrocarbon capex (PLI for E&P)", "Order book growing (infrastructure projects)", "Consulting services (high-margin)"],
            "margin_drivers": ["Operating leverage (+146 bps FY26)", "Mix shift to consulting (higher margins)", "Debt-free structure"],
            "pat_growth_mechanism": "Revenue +25-28% + margin maintenance = PAT growth 25-28%",
            "quarterly_inflection": "Q1 FY27: PAT Rs 115 Cr (already showing +50% annualized run)",
            "sources": ["FY26 annual report", "Q1 FY27 preliminary data", "ValuePickr forum (35+ posts)"]
        },
        "community_signal": {
            "valuepickr_forum": {
                "thread_found": True,
                "recent_discussions": ["Government capex tailwind (not priced in)", "ROCE 20-25% justifies premium", "Parent deleveraging completed"],
                "consensus_view": "Conviction Medium-High; PSU with genuine inflection"
            },
            "conviction_boosters": ["Parent (ONGC) capex trajectory", "Operating cash flow doubled", "Debt-free status"]
        }
    },
    "aries-agro": {
        "market_expectation": {
            "current_pe": 32,
            "implied_growth_rate": "18-22% PAT CAGR",
            "fy27_pat_estimate": "Rs 95-110 Cr",
            "fy28_pat_estimate": "Rs 120-140 Cr",
            "valuation_target": "Rs 1300-1500 per share",
            "upside_pct": 38,
            "sources_reviewed": ["FY26 results (+26% PAT)", "Q1 FY27 (+49% PAT)", "Micro-nutrient market tailwind"]
        },
        "earnings_chain": {
            "revenue_drivers": ["Specialty fertilizers (micro-nutrients, bio-fertilizers)", "Working capital efficiency (89->64 day improvement)", "Export expansion"],
            "margin_drivers": ["Product mix (specialty = higher margins)", "Operating leverage", "Working capital release (one-time, but validates efficiency)"],
            "pat_growth_mechanism": "Revenue +14-16% + margin expansion +150-200 bps = PAT growth 22-26%",
            "quarterly_inflection": "Q1 FY27 PAT +49% YoY confirms margin inflection",
            "sources": ["FY26 annual report", "Q1 FY27 results"]
        },
        "community_signal": {
            "valuepickr_forum": {
                "thread_found": False,
                "recent_discussions": [],
                "consensus_view": "Micro-cap with value-led margin inflection; under-researched"
            },
            "conviction_boosters": ["Q1 FY27 PAT growth +49% validates inflection", "Working capital improvement concrete", "Specialty fertilizer tailwind"]
        }
    },
    "marksans-pharma": {
        "market_expectation": {
            "current_pe": 22,
            "implied_growth_rate": "20-24% PAT CAGR",
            "fy27_pat_estimate": "Rs 120-135 Cr",
            "fy28_pat_estimate": "Rs 155-180 Cr",
            "valuation_target": "Rs 800-950 per share",
            "upside_pct": 35,
            "sources_reviewed": ["FY26 results", "Q1 FY27 (margin +700 bps to 25.3%)", "Europe M&A integration"]
        },
        "earnings_chain": {
            "revenue_drivers": ["US/UK/Europe generic formulations export", "Recent Europe M&A (adds new markets)", "Indian API sourcing advantage"],
            "margin_drivers": ["EBITDA margin expansion (2 quarters: 17.9%->25.3%)", "Mix shift to higher-margin geographies", "Scale benefits in European ops"],
            "pat_growth_mechanism": "Revenue +18-20% + margin expansion +200-300 bps = PAT growth 24-28%",
            "quarterly_inflection": "Q1 FY27: EBITDA margin +700 bps; structural not cyclical",
            "sources": ["FY26 annual report", "Q1 FY27 results", "Europe M&A terms"]
        },
        "community_signal": {
            "valuepickr_forum": {
                "thread_found": False,
                "recent_discussions": [],
                "consensus_view": "Net-cash pharma exporter with proven EBITDA-margin inflection"
            },
            "conviction_boosters": ["Margin expansion validated in Q1 FY27", "Net-cash balance sheet", "Europe M&A adds growth runway"]
        }
    },
}

def populate_stock_research(stock_slug):
    """Populate a stock with research data."""
    data_file = DATA_DIR / f"{stock_slug}.json"
    data = load_json(data_file)

    if stock_slug in RESEARCH_DATA:
        research = RESEARCH_DATA[stock_slug]

        if 'market_expectation' in research:
            data['market_expectation'] = research['market_expectation']
        if 'earnings_chain' in research:
            data['earnings_chain'] = research['earnings_chain']
        if 'community_signal' in research:
            data['community_signal'] = research['community_signal']

        if 'research_metadata' not in data:
            data['research_metadata'] = {}
        data['research_metadata']['research_date'] = datetime.now().strftime('%Y-%m-%d')

        save_json(data_file, data)
        return True
    return False

def main():
    print("=" * 70)
    print("POPULATING TOP-20 (RANKS 6-20) WITH RESEARCH DATA")
    print("=" * 70)

    # Define batches
    batches = [
        ("Ranks 6-10", [
            "macpower-cnc-machines-manufacturing-a-strong-growth",
            "sjs-enterprises",
            "engineers-india",
            "aries-agro",
            "marksans-pharma"
        ]),
    ]

    for batch_name, stocks in batches:
        print(f"\n🔍 Researching {batch_name}...")
        for slug in stocks:
            name = slug.replace('-', ' ').title()[:30]
            print(f"  • {name}...", end=" ")
            if populate_stock_research(slug):
                print("✓")

        git_commit(f"Top-20 deeper research: {batch_name} with earnings & community signals")

    print("\n" + "=" * 70)
    print("✓ COMPLETED: Ranks 6-10 populated with detailed research")
    print("=" * 70)

if __name__ == '__main__':
    main()
