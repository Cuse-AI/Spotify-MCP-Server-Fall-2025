"""
MASTER SCRAPER - Run YouTube AND Reddit scrapers together!
Then automatically process everything through the pipeline.

ONE COMMAND TO RULE THEM ALL!
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def main():
    print("\n" + "="*70)
    print(" MASTER SCRAPER - YOUTUBE + REDDIT")
    print("="*70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis will:")
    print("  1. Scrape YouTube playlists")
    print("  2. Scrape Reddit recommendation threads")
    print("  3. Dedupe against existing tapestry")
    print("  4. Run Ananki analysis ($)")
    print("  5. Inject to tapestry")
    print("\n" + "="*70)

    # Get vibe arguments if provided
    youtube_vibes = None
    reddit_vibes = None

    if len(sys.argv) > 1:
        if '--youtube' in sys.argv:
            idx = sys.argv.index('--youtube')
            if idx + 1 < len(sys.argv):
                youtube_vibes = sys.argv[idx + 1]
        if '--reddit' in sys.argv:
            idx = sys.argv.index('--reddit')
            if idx + 1 < len(sys.argv):
                reddit_vibes = sys.argv[idx + 1]

    scripts_dir = Path(__file__).parent

    # Run YouTube scrapers
    print("\n" + "="*70)
    print(" STEP 1: YOUTUBE SCRAPING")
    print("="*70)

    youtube_cmd = [sys.executable, str(scripts_dir / 'run_scrapers.py')]
    if youtube_vibes:
        youtube_cmd.append(youtube_vibes)
        print(f"\nRunning YouTube for: {youtube_vibes}")
    else:
        print("\nRunning ALL YouTube scrapers")

    try:
        youtube_result = subprocess.run(
            youtube_cmd,
            cwd=str(scripts_dir),
            capture_output=False,
            text=True
        )
        print(f"\nYouTube scraping completed with code: {youtube_result.returncode}")
    except Exception as e:
        print(f"\nERROR in YouTube scraping: {e}")

    # Run Reddit scrapers
    print("\n" + "="*70)
    print(" STEP 2: REDDIT SCRAPING")
    print("="*70)

    reddit_cmd = [sys.executable, str(scripts_dir / 'run_reddit_scrapers.py')]
    if reddit_vibes:
        reddit_cmd.append(reddit_vibes)
        print(f"\nRunning Reddit for: {reddit_vibes}")
    else:
        print("\nRunning ALL Reddit scrapers")

    try:
        reddit_result = subprocess.run(
            reddit_cmd,
            cwd=str(scripts_dir),
            capture_output=False,
            text=True
        )
        print(f"\nReddit scraping completed with code: {reddit_result.returncode}")
    except Exception as e:
        print(f"\nERROR in Reddit scraping: {e}")

    # Final summary
    print("\n" + "="*70)
    print(" ALL SCRAPING COMPLETE!")
    print("="*70)
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nCheck your tapestry for new songs!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
