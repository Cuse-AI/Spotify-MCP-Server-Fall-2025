"""
Quick test runner for Iteration 2 - bypasses Unicode printing issues
"""
import sys
sys.path.insert(0, '.')

from test_extraction_fixes import *

if __name__ == "__main__":
    csv_path = "scraped_data/reddit_v5_training_20251107_164412.csv"

    print("="*80)
    print("V5 EXTRACTION ITERATION 2 TEST")
    print("="*80)

    # Load data
    df = load_test_data(csv_path)

    # Initialize scraper
    scraper = RedditVibeScraperV5()

    # Re-extract fields
    results_df = re_extract_fields(df, scraper)

    # Calculate metrics
    metrics = calculate_quality_metrics(results_df)

    # Print metrics only (skip sample output to avoid Unicode issues)
    print("\n" + "="*80)
    print("EXTRACTION FIX VALIDATION REPORT (ITERATION 2)")
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
        print("OVERALL STATUS: PARTIAL - Some metrics need improvement")

    print("="*80)

    # Save results
    results_csv, metrics_json = save_results(results_df, metrics)

    print(f"\nResults saved:")
    print(f"  Details: {results_csv}")
    print(f"  Metrics: {metrics_json}")

    sys.exit(0 if all_passed else 1)
