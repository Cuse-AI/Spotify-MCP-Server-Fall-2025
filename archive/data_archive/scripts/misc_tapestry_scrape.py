"""
TAPESTRY SCRAPER - Simple Unified Interface
============================================

One command to scrape and process songs into your tapestry!

Usage:
    python tapestry_scrape.py reddit happy,sad,dark
    python tapestry_scrape.py youtube all
    python tapestry_scrape.py both party,night,romantic

This will:
  1. Scrape from specified source(s)
  2. Automatically deduplicate
  3. Run Ananki analysis ($)
  4. Inject to tapestry
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent

def print_banner():
    print("\n" + "="*70)
    print(" TAPESTRY SCRAPER - Unified Data Loading Interface")
    print("="*70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def print_help():
    print("""
USAGE:
    python tapestry_scrape.py <source> <vibes>

SOURCES:
    reddit   - Scrape from Reddit music recommendation threads
    youtube  - Scrape from YouTube playlist comments
    both     - Scrape from both sources

VIBES:
    all                  - All available vibes
    happy,sad,dark,...   - Specific comma-separated vibes

AVAILABLE VIBES:
    angry, anxious, bitter, bored, chaotic, chill, confident, dark,
    drive, energy, excited, grateful, happy, hopeful, introspective,
    jealous, night, nostalgic, party, peaceful, playful, romantic, sad

EXAMPLES:
    python tapestry_scrape.py reddit happy,sad,dark
    python tapestry_scrape.py youtube all
    python tapestry_scrape.py both party,night,romantic

WHAT HAPPENS:
    1. Scrapes songs with emotional context (FREE - no API cost)
    2. Deduplicates against tapestry (saves money!)
    3. Runs Claude Ananki analysis ($ ~$0.003 per song)
    4. Injects to tapestry automatically
    5. Shows final song count
    """)

def main():
    print_banner()

    # Check arguments
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print_help()
        return

    source = sys.argv[1].lower()
    vibes = sys.argv[2] if len(sys.argv) > 2 else "all"

    if source not in ['reddit', 'youtube', 'both']:
        print(f"ERROR: Invalid source '{source}'")
        print("Must be: reddit, youtube, or both")
        print("\nRun 'python tapestry_scrape.py help' for usage")
        return

    print(f"Source: {source.upper()}")
    print(f"Vibes: {vibes}")
    print("\n" + "="*70)
    print(" STARTING SCRAPE")
    print("="*70)

    try:
        if source == 'reddit':
            # Run Reddit scrapers
            script = SCRIPTS_DIR / 'run_reddit_scrapers.py'
            if vibes.lower() == 'all':
                subprocess.run([sys.executable, str(script)], check=True)
            else:
                subprocess.run([sys.executable, str(script), vibes], check=True)

        elif source == 'youtube':
            # Run YouTube scrapers
            script = SCRIPTS_DIR / 'run_scrapers.py'
            if vibes.lower() == 'all':
                subprocess.run([sys.executable, str(script)], check=True)
            else:
                subprocess.run([sys.executable, str(script), vibes], check=True)

        elif source == 'both':
            # Run both
            script = SCRIPTS_DIR / 'scrape_all.py'
            if vibes.lower() == 'all':
                subprocess.run([sys.executable, str(script)], check=True)
            else:
                # Parse vibes for both sources
                subprocess.run([sys.executable, str(script),
                              '--youtube', vibes, '--reddit', vibes], check=True)

        print("\n" + "="*70)
        print(" ALL DONE!")
        print("="*70)
        print("\nCheck your tapestry for new songs!")
        print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Scraping failed with exit code {e.returncode}")
        return 1
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main() or 0)
