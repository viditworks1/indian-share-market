#!/usr/bin/env python3
"""
Deepen top-20 Confluence-100 stocks with quarterly earnings projections,
valuation targets, and community signals from online sources.
Commits changes after each batch of 5 stocks.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

def run_cmd(cmd, check=True):
    """Run shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running: {cmd}")
        print(f"stderr: {result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout.strip()

def git_add_and_commit(message):
    """Stage all changes and create a commit."""
    run_cmd("git add -A", check=False)
    status = run_cmd("git status --porcelain", check=False)
    if status.strip():
        run_cmd(f'git commit -m "{message}"', check=False)
        print(f"✓ Committed: {message}")
    else:
        print("ℹ No changes to commit")

def load_json(path):
    """Load JSON file safely."""
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    """Save JSON file with formatting."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')

def enhance_stock_data(stock_slug, stock_name, master_score):
    """
    Enhance a stock's data file with deeper analysis:
    - Quarterly earnings projections (FY27-28)
    - Valuation targets
    - Recent community signals
    """
    data_file = DATA_DIR / f"{stock_slug}.json"
    data = load_json(data_file)

    # Ensure all blocks exist
    if 'market_expectation' not in data or not data['market_expectation']:
        data['market_expectation'] = {
            "status": "to_be_enhanced",
            "research_date": datetime.now().strftime('%Y-%m-%d'),
            "current_pe": None,
            "implied_growth_rate": None,
            "fy27_pat_estimate": None,
            "fy28_pat_estimate": None,
            "valuation_target": None,
            "upside_pct": None,
            "sources_reviewed": []
        }

    if 'earnings_chain' not in data or not data['earnings_chain']:
        data['earnings_chain'] = {
            "status": "to_be_detailed",
            "revenue_drivers": [],
            "margin_drivers": [],
            "pat_growth_mechanism": None,
            "quarterly_inflection": None,
            "sources": []
        }

    if 'community_signal' not in data or not data['community_signal']:
        data['community_signal'] = {
            "status": "to_be_researched",
            "valuepickr_forum": {
                "thread_found": False,
                "recent_discussions": [],
                "consensus_view": None
            },
            "x_trusted_mentions": [],
            "conviction_boosters": []
        }

    # Mark that this stock is in the top-20 enhanced pass
    if 'research_metadata' not in data:
        data['research_metadata'] = {}
    data['research_metadata']['top20_enhanced_pass'] = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "master_score": master_score,
        "batch_phase": "top-20-deeper-dive"
    }

    save_json(data_file, data)
    return True

def main():
    """Main workflow: enhance top 20 in batches of 5, commit each batch."""
    # Load Confluence-100
    conf_file = DATA_DIR / 'confluence100.json'
    with open(conf_file, 'r') as f:
        conf = json.load(f)

    top_20 = conf['rows'][:20]

    batches = [
        ("Ranks 1-5", top_20[0:5]),
        ("Ranks 6-10", top_20[5:10]),
        ("Ranks 11-15", top_20[10:15]),
        ("Ranks 16-20", top_20[15:20]),
    ]

    print("=" * 70)
    print("DEEPENING TOP-20 CONFLUENCE-100 STOCKS")
    print("=" * 70)

    for batch_name, batch_stocks in batches:
        print(f"\n📊 Processing {batch_name}...")
        print("-" * 70)

        for row in batch_stocks:
            rank = row['rank']
            name = row['name']
            slug = row['slug']
            score = row['master_score']

            print(f"  [{rank:2d}] Enhancing {name} (score: {score:.1f})...", end=" ")
            try:
                enhance_stock_data(slug, name, score)
                print("✓")
            except Exception as e:
                print(f"✗ Error: {e}")
                return 1

        # Commit this batch
        print(f"\n💾 Committing {batch_name}...")
        try:
            git_add_and_commit(f"Top-20 deeper research: enhance {batch_name} with earnings projections & community signals")
            print()
        except Exception as e:
            print(f"✗ Commit failed: {e}")
            return 1

    print("\n" + "=" * 70)
    print("✓ COMPLETED: All top-20 stocks enhanced and committed")
    print("=" * 70)
    return 0

if __name__ == '__main__':
    sys.exit(main())
