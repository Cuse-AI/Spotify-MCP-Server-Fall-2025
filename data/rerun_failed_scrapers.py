"""
Re-run only the scrapers that failed or returned 0 songs
With Architect's fixes applied, these should now work with API key rotation
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import time

def get_song_count(output_file):
    """Get song count from output file"""
    try:
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data.get('songs', []))
    except:
        pass
    return None

def run_scraper(scraper_path, scraper_type):
    """Run a single scraper"""
    vibe = scraper_path.stem.replace('scrape_', '')

    print(f"\n{'='*70}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] RUNNING: {vibe.upper()} ({scraper_type})")
    print(f"{'='*70}")

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, scraper_path.name],
            cwd=str(scraper_path.parent),
            capture_output=True,
            text=True,
            timeout=600
        )

        elapsed = time.time() - start_time

        # Check output file
        if scraper_type == 'YouTube':
            output_file = scraper_path.parent.parent / 'test_results' / f'{vibe}_youtube_extraction.json'
        else:
            output_file = scraper_path.parent.parent / 'test_results' / f'{vibe}_smart_extraction.json'

        song_count = get_song_count(output_file)

        if result.returncode == 0 and song_count and song_count > 0:
            print(f"[SUCCESS] {vibe}: {song_count} songs ({elapsed:.1f}s)")
            return True, song_count, elapsed
        else:
            print(f"[FAILED] {vibe}: {song_count or 0} songs ({elapsed:.1f}s)")
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                print("Last 5 error lines:")
                for line in error_lines[-5:]:
                    print(f"  {line}")
            return False, song_count or 0, elapsed

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"[TIMEOUT] {vibe} exceeded 10 minutes")
        return False, 0, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] {vibe}: {e}")
        return False, 0, elapsed

def main():
    print("\n" + "="*70)
    print("RE-RUNNING FAILED SCRAPERS")
    print("With Architect's fixes: API key rotation + error surfacing")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    script_dir = Path(__file__).parent

    # YouTube scrapers that had 0 songs
    youtube_failed = [
        'bitter', 'chaotic', 'confident', 'excited', 'grateful',
        'hopeful', 'introspective', 'jealous', 'night', 'nostalgic',
        'peaceful', 'playful', 'romantic', 'sad'
    ]

    # YouTube scrapers that didn't run
    youtube_missing = ['lonely', 'party']

    # Reddit scrapers that haven't completed
    reddit_missing = [
        'angry', 'anxious', 'dark', 'drive', 'excited', 'grateful',
        'happy', 'hopeful', 'introspective', 'jealous', 'lonely',
        'night', 'nostalgic', 'party', 'peaceful', 'playful', 'romantic'
    ]

    youtube_dir = script_dir / 'youtube' / 'scrapers'
    reddit_dir = script_dir / 'reddit' / 'smart_scrapers'

    results = {
        'youtube': {'success': 0, 'failed': 0, 'total_songs': 0},
        'reddit': {'success': 0, 'failed': 0, 'total_songs': 0}
    }

    # Run failed YouTube scrapers
    print(f"\n{'='*70}")
    print(f"PHASE 1: YOUTUBE SCRAPERS ({len(youtube_failed + youtube_missing)} total)")
    print(f"{'='*70}")

    for i, vibe in enumerate(youtube_failed + youtube_missing, 1):
        scraper_path = youtube_dir / f'scrape_{vibe}.py'
        if scraper_path.exists():
            print(f"\n[YouTube {i}/{len(youtube_failed + youtube_missing)}]")
            success, songs, elapsed = run_scraper(scraper_path, 'YouTube')

            if success:
                results['youtube']['success'] += 1
                results['youtube']['total_songs'] += songs
            else:
                results['youtube']['failed'] += 1

            time.sleep(2)  # Rate limit
        else:
            print(f"[SKIP] {vibe}: scraper not found")

    # Run missing Reddit scrapers
    print(f"\n{'='*70}")
    print(f"PHASE 2: REDDIT SCRAPERS ({len(reddit_missing)} total)")
    print(f"{'='*70}")

    for i, vibe in enumerate(reddit_missing, 1):
        scraper_path = reddit_dir / f'scrape_{vibe}.py'
        if scraper_path.exists():
            print(f"\n[Reddit {i}/{len(reddit_missing)}]")
            success, songs, elapsed = run_scraper(scraper_path, 'Reddit')

            if success:
                results['reddit']['success'] += 1
                results['reddit']['total_songs'] += songs
            else:
                results['reddit']['failed'] += 1

            time.sleep(2)
        else:
            print(f"[SKIP] {vibe}: scraper not found")

    # Summary
    print(f"\n\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("YouTube Re-runs:")
    print(f"  Success: {results['youtube']['success']}")
    print(f"  Failed: {results['youtube']['failed']}")
    print(f"  Songs collected: {results['youtube']['total_songs']}")

    print()
    print("Reddit Re-runs:")
    print(f"  Success: {results['reddit']['success']}")
    print(f"  Failed: {results['reddit']['failed']}")
    print(f"  Songs collected: {results['reddit']['total_songs']}")

    print()
    total_songs = results['youtube']['total_songs'] + results['reddit']['total_songs']
    print(f"TOTAL NEW SONGS: {total_songs}")
    print("="*70)

if __name__ == '__main__':
    main()
