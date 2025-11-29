"""
FIXED Master Script - Runs ALL scrapers (YouTube + Reddit) with better error handling
Per Replit's recommendations + Architect's Fix #2 (validate output)
"""
import subprocess
import time
import sys
import json
from pathlib import Path
from datetime import datetime

def run_scraper(scraper_path, scraper_type):
    """Run a single scraper with proper error handling"""
    scraper_name = scraper_path.stem
    vibe = scraper_name.replace('scrape_', '')

    print(f"\n{'='*70}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] STARTING: {vibe.upper()} ({scraper_type})")
    print(f"{'='*70}")

    start_time = time.time()

    try:
        # IMPORTANT: Run from the scraper's directory so imports work
        result = subprocess.run(
            [sys.executable, scraper_path.name],
            cwd=str(scraper_path.parent),  # Run from scraper directory
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            # ARCHITECT'S FIX #2: Validate output - check if actually got songs
            output_file = None
            try:
                if scraper_type == 'YouTube':
                    output_file = scraper_path.parent.parent / 'test_results' / f'{vibe}_youtube_extraction.json'
                else:  # Reddit
                    output_file = scraper_path.parent.parent / 'test_results' / f'{vibe}_smart_extraction.json'

                if output_file and output_file.exists():
                    with open(output_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total_songs = len(data.get('songs', []))

                    if total_songs == 0:
                        print(f"[FAILED] {vibe}: 0 songs collected ({elapsed:.1f}s)")
                        print(f"  Likely cause: API quota exceeded or no results found")
                        return False, elapsed
                    else:
                        print(f"[SUCCESS] {vibe}: {total_songs} songs ({elapsed:.1f}s)")
                        return True, elapsed
                else:
                    print(f"[WARN] {vibe}: Output file not found, assuming success based on returncode")
                    return True, elapsed

            except Exception as e:
                # If can't validate, fall back to checking stdout
                print(f"[WARN] Could not validate output file: {e}")

            # Fallback: Show last few lines of output
            output_lines = result.stdout.strip().split('\n')
            relevant_lines = [l for l in output_lines if 'Total' in l or 'songs' in l or 'COMPLETE' in l]

            if relevant_lines:
                print(f"[SUCCESS] {vibe} ({elapsed:.1f}s)")
                for line in relevant_lines[-3:]:  # Show last 3 relevant lines
                    print(f"  {line.strip()}")
            else:
                print(f"[SUCCESS] {vibe} completed ({elapsed:.1f}s)")
                # Show last 3 lines of output
                for line in output_lines[-3:]:
                    print(f"  {line.strip()}")

            return True, elapsed

        else:
            # Show full error
            print(f"[ERROR] {vibe} failed ({elapsed:.1f}s)")
            print(f"Return code: {result.returncode}")

            # Show stderr
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                print("Error output:")
                for line in error_lines[-10:]:  # Show last 10 lines of error
                    print(f"  {line}")

            # Show stdout in case error is there
            if result.stdout and not result.stderr:
                output_lines = result.stdout.strip().split('\n')
                print("Output:")
                for line in output_lines[-10:]:
                    print(f"  {line}")

            return False, elapsed

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"[TIMEOUT] {vibe} exceeded 10 minutes ({elapsed:.1f}s)")
        return False, elapsed

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] {vibe} crashed: {e}")
        import traceback
        traceback.print_exc()
        return False, elapsed


def main():
    print("\n" + "="*70)
    print("RUNNING ALL SCRAPERS - IMPROVED QUALITY FILTERS")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: 100 songs per scraper")
    print(f"Total scrapers: 46 (23 YouTube + 23 Reddit)")
    print("="*70)

    # Get script location
    script_dir = Path(__file__).parent

    # Find scrapers
    youtube_dir = script_dir / 'youtube' / 'scrapers'
    reddit_dir = script_dir / 'reddit' / 'smart_scrapers'

    # Verify directories exist
    if not youtube_dir.exists():
        print(f"ERROR: YouTube directory not found: {youtube_dir}")
        return

    if not reddit_dir.exists():
        print(f"ERROR: Reddit directory not found: {reddit_dir}")
        return

    youtube_scrapers = sorted(youtube_dir.glob('scrape_*.py'))
    reddit_scrapers = sorted(reddit_dir.glob('scrape_*.py'))

    print(f"\nFound {len(youtube_scrapers)} YouTube scrapers")
    print(f"Found {len(reddit_scrapers)} Reddit scrapers")

    if len(youtube_scrapers) == 0 or len(reddit_scrapers) == 0:
        print("ERROR: No scrapers found!")
        return

    results = {
        'youtube': {'success': [], 'failed': [], 'total_time': 0},
        'reddit': {'success': [], 'failed': [], 'total_time': 0}
    }

    # Run YouTube scrapers first
    print(f"\n\n{'='*70}")
    print("PHASE 1: YOUTUBE SCRAPERS")
    print(f"{'='*70}")

    for i, scraper in enumerate(youtube_scrapers, 1):
        print(f"\n[YouTube {i}/{len(youtube_scrapers)}]")
        success, elapsed = run_scraper(scraper, 'YouTube')
        results['youtube']['total_time'] += elapsed

        vibe = scraper.stem.replace('scrape_', '')
        if success:
            results['youtube']['success'].append(vibe)
        else:
            results['youtube']['failed'].append(vibe)

        # Small delay to avoid rate limits
        if i < len(youtube_scrapers):
            time.sleep(2)

    # Run Reddit scrapers
    print(f"\n\n{'='*70}")
    print("PHASE 2: REDDIT SCRAPERS")
    print(f"{'='*70}")

    for i, scraper in enumerate(reddit_scrapers, 1):
        print(f"\n[Reddit {i}/{len(reddit_scrapers)}]")
        success, elapsed = run_scraper(scraper, 'Reddit')
        results['reddit']['total_time'] += elapsed

        vibe = scraper.stem.replace('scrape_', '')
        if success:
            results['reddit']['success'].append(vibe)
        else:
            results['reddit']['failed'].append(vibe)

        # Small delay
        if i < len(reddit_scrapers):
            time.sleep(2)

    # Final summary
    print(f"\n\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("YouTube Scrapers:")
    print(f"  Success: {len(results['youtube']['success'])}/{len(youtube_scrapers)}")
    if results['youtube']['success']:
        print(f"     {', '.join(results['youtube']['success'])}")
    print(f"  Failed: {len(results['youtube']['failed'])}/{len(youtube_scrapers)}")
    if results['youtube']['failed']:
        print(f"     {', '.join(results['youtube']['failed'])}")
    print(f"  Total time: {results['youtube']['total_time']/60:.1f} minutes")

    print()
    print("Reddit Scrapers:")
    print(f"  Success: {len(results['reddit']['success'])}/{len(reddit_scrapers)}")
    if results['reddit']['success']:
        print(f"     {', '.join(results['reddit']['success'])}")
    print(f"  Failed: {len(results['reddit']['failed'])}/{len(reddit_scrapers)}")
    if results['reddit']['failed']:
        print(f"     {', '.join(results['reddit']['failed'])}")
    print(f"  Total time: {results['reddit']['total_time']/60:.1f} minutes")

    print()
    total_success = len(results['youtube']['success']) + len(results['reddit']['success'])
    total_scrapers = len(youtube_scrapers) + len(reddit_scrapers)
    success_rate = (total_success / total_scrapers * 100) if total_scrapers > 0 else 0
    print(f"OVERALL: {total_success}/{total_scrapers} scrapers successful ({success_rate:.1f}%)")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
