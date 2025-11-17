"""
Master script to run ALL scrapers (YouTube + Reddit) with improved quality filters
Runs each scraper with 100 song target
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime

def run_scraper(scraper_path, scraper_type):
    """Run a single scraper"""
    scraper_name = scraper_path.stem
    vibe = scraper_name.replace('scrape_', '')

    print(f"\n{'='*70}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] STARTING: {vibe.upper()} ({scraper_type})")
    print(f"{'='*70}")

    start_time = time.time()

    try:
        result = subprocess.run(
            ['python', str(scraper_path)],
            cwd=str(scraper_path.parent),
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per scraper
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            # Parse output for song count
            output = result.stdout
            if 'Total' in output and 'songs' in output:
                # Extract song count
                for line in output.split('\n'):
                    if 'Total' in line and ('songs' in line or 'unique' in line):
                        print(f"[SUCCESS] {vibe}: {line.strip()} ({elapsed:.1f}s)")
                        break
            else:
                print(f"[SUCCESS] {vibe} completed ({elapsed:.1f}s)")

            return True, elapsed
        else:
            print(f"[ERROR] {vibe} failed: {result.stderr[:200]}")
            return False, elapsed

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {vibe} exceeded 10 minutes")
        return False, 600
    except Exception as e:
        print(f"[ERROR] {vibe}: {e}")
        return False, 0


def main():
    print("\n" + "="*70)
    print("RUNNING ALL SCRAPERS - IMPROVED QUALITY FILTERS")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: 100 songs per scraper")
    print(f"Total scrapers: 46 (23 YouTube + 23 Reddit)")
    print("="*70)

    # Get all scrapers
    youtube_dir = Path(__file__).parent / 'youtube' / 'scrapers'
    reddit_dir = Path(__file__).parent / 'reddit' / 'smart_scrapers'

    youtube_scrapers = sorted(youtube_dir.glob('scrape_*.py'))
    reddit_scrapers = sorted(reddit_dir.glob('scrape_*.py'))

    print(f"\nFound {len(youtube_scrapers)} YouTube scrapers")
    print(f"Found {len(reddit_scrapers)} Reddit scrapers")

    results = {
        'youtube': {'success': 0, 'failed': 0, 'total_time': 0},
        'reddit': {'success': 0, 'failed': 0, 'total_time': 0}
    }

    # Run YouTube scrapers first (faster, better emotional content)
    print(f"\n\n{'='*70}")
    print("PHASE 1: YOUTUBE SCRAPERS")
    print(f"{'='*70}")

    for scraper in youtube_scrapers:
        success, elapsed = run_scraper(scraper, 'YouTube')
        results['youtube']['total_time'] += elapsed
        if success:
            results['youtube']['success'] += 1
        else:
            results['youtube']['failed'] += 1

        # Small delay between scrapers to avoid rate limits
        time.sleep(2)

    # Run Reddit scrapers
    print(f"\n\n{'='*70}")
    print("PHASE 2: REDDIT SCRAPERS")
    print(f"{'='*70}")

    for scraper in reddit_scrapers:
        success, elapsed = run_scraper(scraper, 'Reddit')
        results['reddit']['total_time'] += elapsed
        if success:
            results['reddit']['success'] += 1
        else:
            results['reddit']['failed'] += 1

        # Small delay between scrapers
        time.sleep(2)

    # Final summary
    print(f"\n\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("YouTube Scrapers:")
    print(f"  Success: {results['youtube']['success']}/{len(youtube_scrapers)}")
    print(f"  Failed: {results['youtube']['failed']}/{len(youtube_scrapers)}")
    print(f"  Total time: {results['youtube']['total_time']/60:.1f} minutes")
    print()
    print("Reddit Scrapers:")
    print(f"  Success: {results['reddit']['success']}/{len(reddit_scrapers)}")
    print(f"  Failed: {results['reddit']['failed']}/{len(reddit_scrapers)}")
    print(f"  Total time: {results['reddit']['total_time']/60:.1f} minutes")
    print()
    total_success = results['youtube']['success'] + results['reddit']['success']
    total_scrapers = len(youtube_scrapers) + len(reddit_scrapers)
    print(f"OVERALL: {total_success}/{total_scrapers} scrapers successful")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
