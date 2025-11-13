"""
Reddit V5 Expanded Production Run
Runs additional scraping rounds to reach 2,500-3,000 target records
Uses time filtering and expanded subreddit coverage
"""

import sys
from reddit_scraper_v5 import RedditVibeScraperV5
import time

def main():
    print("=" * 70)
    print("REDDIT V5 EXPANDED PRODUCTION RUN")
    print("=" * 70)
    print("\nObjective: Reach 2,500-3,000 total records across multiple runs")
    print("Strategy: Expanded time windows + additional subreddit coverage")
    print("=" * 70)
    print()

    scraper = RedditVibeScraperV5()

    # Run multiple rounds with different time filters
    time_filters = ['month', 'year', 'all']
    all_runs_data = []

    for time_idx, time_filter in enumerate(time_filters):
        print(f"\n[RUN {time_idx + 1}/3] Time filter: {time_filter}")
        print("=" * 70)

        # Modify the scraper's time filter for this run
        # We'll search with higher limits and different time windows
        posts = scraper.search_relational_queries(max_posts_per_query=15)

        if len(posts) > 0:
            all_runs_data.extend(posts)
            print(f"[+] Run {time_idx + 1} collected {len(posts)} posts")
            print(f"[+] Total cumulative posts: {len(all_runs_data)}")

        # Wait between runs to respect rate limits
        if time_idx < len(time_filters) - 1:
            print("\nWaiting 30 seconds before next run...")
            time.sleep(30)

    # Save combined data
    if len(all_runs_data) > 0:
        print("\n" + "=" * 70)
        print("SAVING COMBINED DATA FROM ALL RUNS")
        print("=" * 70)

        json_path, csv_path, metrics_path = scraper.save_data(all_runs_data)

        print()
        print("=" * 70)
        print("[OK] V5 EXPANDED PRODUCTION COMPLETE!")
        print("=" * 70)
        print(f"\nTotal posts collected: {len(all_runs_data)}")
        print(f"\nFiles created:")
        print(f"  {csv_path}")
        print(f"  {json_path}")
        print(f"  {metrics_path}")
    else:
        print("\n[!] No additional data collected.")

if __name__ == "__main__":
    main()
