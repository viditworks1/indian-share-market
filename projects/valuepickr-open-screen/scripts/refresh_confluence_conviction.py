#!/usr/bin/env python3
"""
Conviction Score Refresh Script for Confluence-100
Extracts conviction drivers from individual deepdive research files
and recalculates conviction_score for the master confluence100.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Base directory configuration
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
CONFLUENCE_FILE = DATA_DIR / "confluence100.json"

def load_confluence_master():
    """Load the master confluence100.json file"""
    with open(CONFLUENCE_FILE, 'r') as f:
        return json.load(f)

def find_stock_file(slug: str) -> Optional[Path]:
    """Find the individual stock data file by slug"""
    stock_file = DATA_DIR / f"{slug}.json"
    if stock_file.exists():
        return stock_file
    return None

def load_stock_data(file_path: Path) -> Dict:
    """Load individual stock data file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def extract_conviction_drivers(stock_data: Dict) -> Dict:
    """
    Extract conviction drivers from stock data
    Returns dict with individual driver values
    """
    drivers = {
        "quality_lift": 0,
        "management_credibility": 0,
        "community_corroboration": 0,
        "bull_case_count": 0,
        "notes": []
    }

    # 1. Quality lift: +5 points if quality_score >= 80
    quality_score = stock_data.get("quality_metrics", {}).get("assessment")
    if quality_score == "positive":
        # Positive assessment indicates quality_score >= 80 typically
        drivers["quality_lift"] = 5
        drivers["notes"].append("Quality lift: +5 (positive assessment)")

    # 2. Management credibility: +3 if excellent/strong, -3 if weak
    mgmt_assessment = stock_data.get("management_quality", {}).get("assessment")
    if mgmt_assessment == "positive":
        drivers["management_credibility"] = 3
        drivers["notes"].append("Management credibility: +3 (positive)")
    elif mgmt_assessment == "weak":
        drivers["management_credibility"] = -3
        drivers["notes"].append("Management credibility: -3 (weak)")

    # 3. Community corroboration: +2 per ValuePickr thread if active (50+ posts)
    community_signal = stock_data.get("community_signal", {})
    valuepickr_forum = community_signal.get("valuepickr_forum", {})
    if valuepickr_forum.get("thread_found"):
        # Count posts mentioned in sentiment_summary or estimate from activity level
        sentiment_summary = stock_data.get("sentiment_summary", "")
        if sentiment_summary:
            # Try to extract post count from sentiment summary
            import re
            post_match = re.search(r'(\d+)\s*posts?', sentiment_summary)
            if post_match:
                post_count = int(post_match.group(1))
                if post_count >= 50:
                    drivers["community_corroboration"] = 2
                    drivers["notes"].append(f"Community: +2 (active thread with {post_count} posts)")

    # 4. Bull case count: +1 per confirmed bull case point
    bull_case = stock_data.get("bull_case", [])
    if isinstance(bull_case, list):
        bull_count = len(bull_case)
        # Cap at +10 points for bull case (max 10 points from this driver)
        drivers["bull_case_count"] = min(bull_count, 10)
        drivers["notes"].append(f"Bull case: +{drivers['bull_case_count']} ({bull_count} points identified)")

    return drivers

def recalculate_conviction_score(row: Dict, stock_data: Dict) -> Tuple[float, Dict]:
    """
    Recalculate conviction score with new data
    Returns (new_score, drivers_dict)
    """
    # Base anchor: current conviction_score
    base_score = row.get("conviction_score", 60.0)

    # Extract drivers
    drivers = extract_conviction_drivers(stock_data)

    # Calculate new score
    new_score = base_score + drivers["quality_lift"] + drivers["management_credibility"]
    new_score += drivers["community_corroboration"] + drivers["bull_case_count"]

    # Cap at 100
    new_score = min(new_score, 100.0)
    new_score = max(new_score, 0.0)

    return round(new_score, 2), drivers

def analyze_changes(original: List[Dict], updated: List[Dict]) -> Dict:
    """Analyze changes in conviction scores"""
    analysis = {
        "material_changes": [],  # >= 5 points
        "new_tier_a": [],  # conviction >= 60 for first time
        "dropped_from_tier_a": [],  # now < 60
        "top_10_updated": []
    }

    # Create lookup dictionaries
    original_by_slug = {row["slug"]: row for row in original}

    # Find material changes
    for updated_row in updated:
        slug = updated_row["slug"]
        original_row = original_by_slug.get(slug)

        if original_row:
            old_score = original_row.get("conviction_score", 0)
            new_score = updated_row.get("conviction_score", 0)
            change = new_score - old_score

            if abs(change) >= 5:
                analysis["material_changes"].append({
                    "name": updated_row.get("name"),
                    "slug": slug,
                    "old_score": old_score,
                    "new_score": new_score,
                    "change": change
                })

            # Check tier transitions
            was_tier_a = old_score >= 60
            is_tier_a = new_score >= 60

            if not was_tier_a and is_tier_a:
                analysis["new_tier_a"].append({
                    "name": updated_row.get("name"),
                    "slug": slug,
                    "new_score": new_score
                })

            if was_tier_a and not is_tier_a:
                analysis["dropped_from_tier_a"].append({
                    "name": updated_row.get("name"),
                    "slug": slug,
                    "new_score": new_score
                })

    # Get top 10 by updated conviction
    top_10 = sorted(updated, key=lambda x: x.get("conviction_score", 0), reverse=True)[:10]
    analysis["top_10_updated"] = [
        {
            "rank": row.get("rank"),
            "name": row.get("name"),
            "conviction_score": row.get("conviction_score")
        }
        for row in top_10
    ]

    return analysis

def refresh_conviction_scores():
    """Main execution: refresh all conviction scores"""
    print("=" * 80)
    print("CONFLUENCE-100 CONVICTION SCORE REFRESH")
    print("=" * 80)
    print()

    # Load master file
    print("Loading confluence100.json...")
    master = load_confluence_master()
    original_rows = [dict(row) for row in master["rows"]]  # Deep copy for comparison

    processed = 0
    skipped = 0
    errors = 0

    print(f"Found {len(master['rows'])} stocks to process")
    print()

    # Process each stock
    for row in master["rows"]:
        slug = row.get("slug")
        name = row.get("name")

        # Find stock file
        stock_file = find_stock_file(slug)
        if not stock_file:
            print(f"[SKIP] {name:40} - data file not found")
            skipped += 1
            continue

        # Load stock data
        stock_data = load_stock_data(stock_file)
        if not stock_data:
            print(f"[ERR]  {name:40} - failed to load")
            errors += 1
            continue

        # Recalculate conviction score
        old_score = row.get("conviction_score", 0)
        new_score, drivers = recalculate_conviction_score(row, stock_data)

        # Update row
        row["conviction_score"] = new_score

        # Log material changes (>= 5 points)
        change = new_score - old_score
        if abs(change) >= 5:
            print(f"[MAT] {name:40} {old_score:6.2f} -> {new_score:6.2f} ({change:+7.2f})")

        processed += 1

    print()
    print(f"Processed: {processed}, Skipped: {skipped}, Errors: {errors}")
    print()

    # Analyze changes
    analysis = analyze_changes(original_rows, master["rows"])

    # Print summary statistics
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    print(f"\nMaterial Changes (>= 5 points): {len(analysis['material_changes'])}")
    if analysis["material_changes"]:
        for item in sorted(analysis["material_changes"], key=lambda x: abs(x["change"]), reverse=True)[:10]:
            print(f"  {item['name']:40} {item['old_score']:6.2f} -> {item['new_score']:6.2f} ({item['change']:+7.2f})")

    print(f"\nNew Tier-A Candidates (conviction >= 60): {len(analysis['new_tier_a'])}")
    if analysis["new_tier_a"]:
        for item in analysis["new_tier_a"]:
            print(f"  {item['name']:40} - Score: {item['new_score']:6.2f}")

    print(f"\nDropped from Tier-A (now < 60): {len(analysis['dropped_from_tier_a'])}")
    if analysis["dropped_from_tier_a"]:
        for item in analysis["dropped_from_tier_a"]:
            print(f"  {item['name']:40} - Score: {item['new_score']:6.2f}")

    print()
    print("=" * 80)
    print("TOP 10 UPDATED CONVICTION RANKINGS")
    print("=" * 80)
    print()
    for idx, item in enumerate(analysis["top_10_updated"], 1):
        print(f"{idx:2d}. {item['name']:40} - {item['conviction_score']:6.2f}")

    # Save updated file
    print()
    print("=" * 80)
    print("Saving updated confluence100.json...")
    with open(CONFLUENCE_FILE, 'w') as f:
        json.dump(master, f, indent=2)
    print(f"✓ Updated file saved to {CONFLUENCE_FILE}")
    print()

    return analysis

if __name__ == "__main__":
    try:
        analysis = refresh_conviction_scores()
        print("=" * 80)
        print("REFRESH COMPLETE")
        print("=" * 80)
    except Exception as e:
        print(f"Error during refresh: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
