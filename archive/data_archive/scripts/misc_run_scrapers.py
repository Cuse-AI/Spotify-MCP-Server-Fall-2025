"""
AUTOMATED SCRAPER RUNNER
Runs YouTube/Reddit scrapers and moves results to 1_raw_scrapes/
Then you can run automated_pipeline.py to process them!

SAFE TO RUN - Only scrapes data, doesn't spend Ananki credits
"""

import subprocess
import sys
from pathlib import Path
import time
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
YOUTUBE_SCRAPERS = PROJECT_ROOT / 'youtube' / 'scrapers'
YOUTUBE_RESULTS = PROJECT_ROOT / 'youtube' / 'test_results'
RAW_SCRAPES_DIR = PROJECT_ROOT / '1_raw_scrapes'

# Ensure output directory exists
RAW_SCRAPES_DIR.mkdir(parents=True, exist_ok=True)

# Define which scrapers to run and target counts
SCRAPER_CONFIG = {
    # Vibes that need more songs (under 1000 in tapestry)
    'youtube': {
        'angry': 300,
        'anxious': 300,
        'bitter': 300,
        'bored': 300,
        'chaotic': 300,
        'chill': 300,
        'confident': 300,
        'dark': 300,
        'drive': 300,
        'excited': 300,
        'grateful': 300,
        'happy': 300,
        'hopeful': 300,
        'introspective': 300,
        'jealous': 300,
        'night': 300,
        'nostalgic': 300,
        'party': 300,
        'peaceful': 300,
        'playful': 300,
        'romantic': 300,
        # Skip sad and energy - already over 1000
    }
}

def run_scraper(scraper_type, vibe, target):
    """Run a single scraper"""
    print(f"\n{'='*70}")
    print(f"SCRAPING: {vibe.upper()} ({target} songs)")
    print(f"{'='*70}")

    if scraper_type == 'youtube':
        scraper_file = YOUTUBE_SCRAPERS / f'scrape_{vibe}.py'
        if not scraper_file.exists():
            print(f"  ERROR: Scraper not found: {scraper_file}")
            return False

        # Run scraper with target
        cmd = [sys.executable, str(scraper_file), str(target)]
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                cwd=str(YOUTUBE_SCRAPERS),
                capture_output=False,  # Show output in real-time
                text=True,
                timeout=600  # 10 minute timeout per scraper
            )

            elapsed = time.time() - start_time

            if result.returncode == 0:
                print(f"\n  SUCCESS! Completed in {elapsed/60:.1f} minutes")

                # Move result file to 1_raw_scrapes
                result_file = YOUTUBE_RESULTS / f'{vibe}_youtube_extraction.json'
                if result_file.exists():
                    dest_file = RAW_SCRAPES_DIR / result_file.name
                    # Copy instead of move to preserve original
                    import shutil
                    shutil.copy2(result_file, dest_file)
                    print(f"  Moved to: {dest_file}")
                    return True
                else:
                    print(f"  WARNING: Result file not found: {result_file}")
                    return False
            else:
                print(f"  FAILED with return code {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT after 10 minutes")
            return False
        except Exception as e:
            print(f"  ERROR: {e}")
            return False

    return False

def main():
    print("\n" + "="*70)
    print(" AUTOMATED SCRAPER RUNNER")
    print("="*70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nThis will scrape YouTube playlists for emotional music recommendations.")
    print("Results will be saved to 1_raw_scrapes/ for pipeline processing.")
    print("\nNOTE: This only scrapes data - no API credits spent until Ananki runs!")

    # Allow running specific vibes
    if len(sys.argv) > 1:
        vibes_to_run = sys.argv[1].split(',')
        print(f"\nRunning specific vibes: {', '.join(vibes_to_run)}")
    else:
        vibes_to_run = list(SCRAPER_CONFIG['youtube'].keys())
        print(f"\nRunning all {len(vibes_to_run)} YouTube scrapers")

    print("\n" + "="*70)
    print("Starting scrapers...")
    print("="*70)

    # Track results
    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }

    start_time = time.time()

    # Run YouTube scrapers
    for vibe in vibes_to_run:
        if vibe not in SCRAPER_CONFIG['youtube']:
            print(f"\nSkipping unknown vibe: {vibe}")
            results['skipped'].append(vibe)
            continue

        target = SCRAPER_CONFIG['youtube'][vibe]
        success = run_scraper('youtube', vibe, target)

        if success:
            results['success'].append(vibe)
        else:
            results['failed'].append(vibe)

        # Small delay between scrapers to be nice to APIs
        if vibe != vibes_to_run[-1]:
            print("\nWaiting 5 seconds before next scraper...")
            time.sleep(5)

    # Summary
    total_time = time.time() - start_time
    print("\n" + "="*70)
    print(" SCRAPING COMPLETE!")
    print("="*70)
    print(f"\nTotal time: {total_time/60:.1f} minutes")
    print(f"\nResults:")
    print(f"  Success: {len(results['success'])}")
    print(f"  Failed: {len(results['failed'])}")
    print(f"  Skipped: {len(results['skipped'])}")

    if results['success']:
        print(f"\nSuccessful vibes: {', '.join(results['success'])}")

    if results['failed']:
        print(f"\nFailed vibes: {', '.join(results['failed'])}")

    # Automatically run pipeline if we got successful scrapes
    if results['success']:
        print("\n" + "="*70)
        print(" STARTING AUTOMATED PIPELINE")
        print("="*70)
        print(f"\nEstimated Ananki cost: ~${len(results['success']) * 300 * 0.003:.2f}")
        print("\nPipeline will: dedupe → Ananki ($) → inject to tapestry")
        print("="*70)

        # Run the automated pipeline
        pipeline_script = Path(__file__).parent / 'automated_pipeline.py'

        try:
            print("\nStarting pipeline...\n")
            result = subprocess.run(
                [sys.executable, str(pipeline_script)],
                cwd=str(Path(__file__).parent),
                capture_output=False,  # Show output in real-time
                text=True
            )

            if result.returncode == 0:
                print("\n" + "="*70)
                print(" COMPLETE! Songs added to tapestry!")
                print("="*70)
            else:
                print("\n" + "="*70)
                print(" Pipeline had errors - check output above")
                print("="*70)

        except Exception as e:
            print(f"\nERROR running pipeline: {e}")
            print(f"\nYou can run manually: python {pipeline_script}")
    else:
        print("\n" + "="*70)
        print(" No successful scrapes - skipping pipeline")
        print("="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
