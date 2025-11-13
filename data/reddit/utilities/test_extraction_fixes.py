"""
Test Extraction Fixes for V5 Reddit Scraper

This script validates the improved extraction logic on existing test data.
Success criteria:
- Anchor reference: >=70% capture rate (currently 1.3%)
- Delta description: >=70% human-legible (currently 58.8% with fragments)
- Reasoning text: >=30-40% coverage (currently 5.6%)

Usage: python test_extraction_fixes.py reddit_v5_training_20251107_164412.csv
"""

import pandas as pd
import numpy as np
import json
import sys
import re
from datetime import datetime
from reddit_scraper_v5 import RedditVibeScraperV5


def load_test_data(csv_path):
    """Load existing V5 test data"""
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"[OK] Loaded {len(df)} records from {csv_path}")
    return df


def re_extract_fields(df, scraper):
    """
    Re-run extraction on existing vibe_request and comment_context fields
    This tests the new extraction logic without re-scraping
    """
    print("\n[>>] Re-running extraction with improved logic...")

    results = []

    for idx, row in df.iterrows():
        # Combine vibe_request (post) and comment_context for extraction
        post_text = str(row.get('vibe_request', ''))
        comment_text = str(row.get('comment_context', ''))
        combined_text = f"{post_text} {comment_text}"

        # Re-extract anchor reference from post
        anchor_artist, anchor_song = scraper.extract_anchor_reference(post_text)

        # Re-extract delta description from post
        delta_description = scraper.extract_delta_description(post_text)

        # Re-extract reasoning from comment
        reasoning_text = scraper.extract_reasoning_text(comment_text)

        results.append({
            'original_index': idx,
            'song_name': row.get('song_name'),
            'artist_name': row.get('artist_name'),
            'relation_type': row.get('relation_type'),

            # Original extraction results
            'old_anchor_artist': row.get('anchor_reference_artist'),
            'old_anchor_song': row.get('anchor_reference_song'),
            'old_delta': row.get('delta_description'),
            'old_reasoning': row.get('reasoning_text'),

            # New extraction results
            'new_anchor_artist': anchor_artist,
            'new_anchor_song': anchor_song,
            'new_delta': delta_description,
            'new_reasoning': reasoning_text,

            # Context for validation
            'vibe_request': post_text[:500],
            'comment_context': comment_text[:500],
        })

        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(df)} records...")

    print(f"[OK] Extraction complete!")
    return pd.DataFrame(results)


def calculate_quality_metrics(results_df):
    """
    Calculate extraction quality metrics
    """
    total = len(results_df)

    # Anchor reference metrics
    old_anchor_count = results_df['old_anchor_artist'].notna().sum()
    new_anchor_count = results_df['new_anchor_artist'].notna().sum()

    old_anchor_rate = (old_anchor_count / total) * 100
    new_anchor_rate = (new_anchor_count / total) * 100

    # Delta description metrics
    old_delta_count = results_df['old_delta'].notna().sum()
    new_delta_count = results_df['new_delta'].notna().sum()

    old_delta_rate = (old_delta_count / total) * 100
    new_delta_rate = (new_delta_count / total) * 100

    # Reasoning text metrics
    old_reasoning_count = results_df['old_reasoning'].notna().sum()
    new_reasoning_count = results_df['new_reasoning'].notna().sum()

    old_reasoning_rate = (old_reasoning_count / total) * 100
    new_reasoning_rate = (new_reasoning_count / total) * 100

    # Delta quality check (semantic vs noise)
    def is_semantic_delta(delta_text):
        """Check if delta is semantic (not noise fragments)"""
        if pd.isna(delta_text) or not delta_text:
            return False

        # Check for noise patterns (fragments like "preferably not | prefer")
        noise_indicators = [
            r'^[a-z]{1,4}(\s+\|\s+[a-z]{1,4})+$',  # Short word fragments
            r'^\w+\s+\|\s+\w+$',  # Just two words
            r'^(this is|you feel|I think|they have|it builds)',  # Common fragments
        ]

        if any(re.search(pattern, str(delta_text).lower()) for pattern in noise_indicators):
            return False

        # Check for semantic content
        semantic_indicators = [
            r'\b(more|less|very|much|way|really|extremely)\s+\w+',
            r'\b(darker|lighter|heavier|softer|slower|faster|mellower|harder)\b',
            r'\b(happier|sadder|calmer|angrier|peaceful|intense|uplifting)\b',
            r'\b(with|without|plus|minus|adding)\s+\w+',
        ]

        return any(re.search(pattern, str(delta_text).lower()) for pattern in semantic_indicators)

    old_semantic_deltas = sum(1 for delta in results_df['old_delta'] if is_semantic_delta(delta))
    new_semantic_deltas = sum(1 for delta in results_df['new_delta'] if is_semantic_delta(delta))

    old_semantic_rate = (old_semantic_deltas / max(old_delta_count, 1)) * 100 if old_delta_count > 0 else 0
    new_semantic_rate = (new_semantic_deltas / max(new_delta_count, 1)) * 100 if new_delta_count > 0 else 0

    metrics = {
        'total_records': total,

        # Anchor metrics
        'old_anchor_count': old_anchor_count,
        'new_anchor_count': new_anchor_count,
        'old_anchor_rate': old_anchor_rate,
        'new_anchor_rate': new_anchor_rate,
        'anchor_improvement': new_anchor_rate - old_anchor_rate,

        # Delta metrics
        'old_delta_count': old_delta_count,
        'new_delta_count': new_delta_count,
        'old_delta_rate': old_delta_rate,
        'new_delta_rate': new_delta_rate,
        'delta_improvement': new_delta_rate - old_delta_rate,

        # Delta quality
        'old_semantic_deltas': old_semantic_deltas,
        'new_semantic_deltas': new_semantic_deltas,
        'old_semantic_rate': old_semantic_rate,
        'new_semantic_rate': new_semantic_rate,
        'semantic_improvement': new_semantic_rate - old_semantic_rate,

        # Reasoning metrics
        'old_reasoning_count': old_reasoning_count,
        'new_reasoning_count': new_reasoning_count,
        'old_reasoning_rate': old_reasoning_rate,
        'new_reasoning_rate': new_reasoning_rate,
        'reasoning_improvement': new_reasoning_rate - old_reasoning_rate,

        # Success criteria check
        'anchor_target_met': new_anchor_rate >= 70,
        'delta_target_met': new_delta_rate >= 70 and new_semantic_rate >= 70,
        'reasoning_target_met': new_reasoning_rate >= 30,
    }

    return metrics


def generate_validation_report(metrics, results_df):
    """
    Generate human-readable validation report
    """
    print("\n" + "="*80)
    print("EXTRACTION FIX VALIDATION REPORT")
    print("="*80)

    print(f"\nDataset: {metrics['total_records']} records")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n" + "-"*80)
    print("ANCHOR REFERENCE EXTRACTION")
    print("-"*80)
    print(f"Old Coverage:  {metrics['old_anchor_count']:>3} / {metrics['total_records']} = {metrics['old_anchor_rate']:>5.1f}%")
    print(f"New Coverage:  {metrics['new_anchor_count']:>3} / {metrics['total_records']} = {metrics['new_anchor_rate']:>5.1f}%")
    print(f"Improvement:   {metrics['anchor_improvement']:>+5.1f} percentage points")
    print(f"Target:        >= 70.0%")
    print(f"Status:        {'PASS' if metrics['anchor_target_met'] else 'FAIL'}")

    print("\n" + "-"*80)
    print("DELTA DESCRIPTION EXTRACTION")
    print("-"*80)
    print(f"Old Coverage:  {metrics['old_delta_count']:>3} / {metrics['total_records']} = {metrics['old_delta_rate']:>5.1f}%")
    print(f"New Coverage:  {metrics['new_delta_count']:>3} / {metrics['total_records']} = {metrics['new_delta_rate']:>5.1f}%")
    print(f"Improvement:   {metrics['delta_improvement']:>+5.1f} percentage points")
    print()
    print(f"Old Semantic:  {metrics['old_semantic_deltas']:>3} / {metrics['old_delta_count']:>3} = {metrics['old_semantic_rate']:>5.1f}% (of captured)")
    print(f"New Semantic:  {metrics['new_semantic_deltas']:>3} / {metrics['new_delta_count']:>3} = {metrics['new_semantic_rate']:>5.1f}% (of captured)")
    print(f"Quality Gain:  {metrics['semantic_improvement']:>+5.1f} percentage points")
    print(f"Target:        >= 70.0% coverage with >= 70% semantic")
    print(f"Status:        {'PASS' if metrics['delta_target_met'] else 'FAIL'}")

    print("\n" + "-"*80)
    print("REASONING TEXT EXTRACTION")
    print("-"*80)
    print(f"Old Coverage:  {metrics['old_reasoning_count']:>3} / {metrics['total_records']} = {metrics['old_reasoning_rate']:>5.1f}%")
    print(f"New Coverage:  {metrics['new_reasoning_count']:>3} / {metrics['total_records']} = {metrics['new_reasoning_rate']:>5.1f}%")
    print(f"Improvement:   {metrics['reasoning_improvement']:>+5.1f} percentage points")
    print(f"Target:        >= 30.0%")
    print(f"Status:        {'PASS' if metrics['reasoning_target_met'] else 'FAIL'}")

    # Overall validation status
    print("\n" + "="*80)
    all_passed = all([
        metrics['anchor_target_met'],
        metrics['delta_target_met'],
        metrics['reasoning_target_met']
    ])

    if all_passed:
        print("OVERALL STATUS: PASS - Ready for production scaling")
    else:
        print("OVERALL STATUS: FAIL - Needs further iteration")

    print("="*80)

    # Sample outputs for manual review
    print("\n" + "-"*80)
    print("SAMPLE EXTRACTIONS (Manual Review)")
    print("-"*80)

    # Get 10 random samples with proximity relation
    proximity_samples = results_df[results_df['relation_type'] == 'proximity'].sample(min(10, len(results_df)))

    for idx, row in proximity_samples.iterrows():
        print(f"\n[Sample {idx}]")
        print(f"Vibe Request: {row['vibe_request'][:150]}...")
        print(f"Target Song:  {row['song_name']} by {row['artist_name']}")
        print()
        print(f"  OLD Anchor: {row['old_anchor_artist']} - {row['old_anchor_song']}")
        print(f"  NEW Anchor: {row['new_anchor_artist']} - {row['new_anchor_song']}")
        print()
        print(f"  OLD Delta:  {row['old_delta']}")
        print(f"  NEW Delta:  {row['new_delta']}")
        print()
        print(f"  OLD Reasoning: {str(row['old_reasoning'])[:100] if pd.notna(row['old_reasoning']) else 'None'}...")
        print(f"  NEW Reasoning: {str(row['new_reasoning'])[:100] if pd.notna(row['new_reasoning']) else 'None'}...")
        print("-"*80)

    return all_passed


def save_results(results_df, metrics):
    """Save validation results to files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save detailed results CSV
    results_csv = f"reddit_v5_extraction_test_{timestamp}.csv"
    results_df.to_csv(results_csv, index=False, encoding='utf-8')
    print(f"\n[OK] Saved detailed results: {results_csv}")

    # Save metrics JSON (convert numpy types to native Python types)
    metrics_json = f"reddit_v5_extraction_metrics_{timestamp}.json"
    with open(metrics_json, 'w', encoding='utf-8') as f:
        # Convert numpy types to Python native types for JSON serialization
        json_metrics = {}
        for k, v in metrics.items():
            if isinstance(v, (np.integer, np.int64)):
                json_metrics[k] = int(v)
            elif isinstance(v, (np.floating, np.float64)):
                json_metrics[k] = float(v)
            elif isinstance(v, np.bool_):
                json_metrics[k] = bool(v)
            else:
                json_metrics[k] = v
        json.dump(json_metrics, f, indent=2)
    print(f"[OK] Saved metrics: {metrics_json}")

    return results_csv, metrics_json


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_extraction_fixes.py <csv_file>")
        print("\nExample:")
        print("  python test_extraction_fixes.py reddit_v5_training_20251107_164412.csv")
        sys.exit(1)

    csv_path = sys.argv[1]

    print("="*80)
    print("V5 EXTRACTION FIX VALIDATION TEST")
    print("="*80)
    print(f"\nTesting improved extraction logic on: {csv_path}")
    print("\nSuccess Criteria:")
    print("  - Anchor reference: >= 70% capture rate")
    print("  - Delta description: >= 70% coverage with >= 70% semantic quality")
    print("  - Reasoning text:    >= 30% coverage")
    print()

    # Load data
    df = load_test_data(csv_path)

    # Initialize scraper with new extraction logic
    scraper = RedditVibeScraperV5()

    # Re-extract fields
    results_df = re_extract_fields(df, scraper)

    # Calculate metrics
    metrics = calculate_quality_metrics(results_df)

    # Generate report
    validation_passed = generate_validation_report(metrics, results_df)

    # Save results
    save_results(results_df, metrics)

    # Exit with appropriate code
    sys.exit(0 if validation_passed else 1)


if __name__ == "__main__":
    main()
