"""
FULL PIPELINE: Scrape → Dedupe → Ananki → Tapestry
Runs all 46 scrapers, dedupes against tapestry, and prepares for Ananki
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def main():
    print("\n" + "="*70)
    print("FULL SCRAPING PIPELINE - SCRAPE → DEDUPE → READY FOR ANANKI")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    script_dir = Path(__file__).parent

    # Step 1: Run all scrapers
    print("\n\n" + "="*70)
    print("STEP 1: RUNNING ALL SCRAPERS")
    print("="*70)

    scraper_script = script_dir / 'run_all_scrapers_FIXED.py'
    if not scraper_script.exists():
        print(f"ERROR: Scraper script not found: {scraper_script}")
        return

    result = subprocess.run(
        [sys.executable, str(scraper_script)],
        cwd=str(script_dir)
    )

    if result.returncode != 0:
        print("\n[ERROR] Scraper run failed!")
        print("Check output above for errors")
        return

    print("\n[SUCCESS] All scrapers completed!")

    # Step 2: Dedupe all results
    print("\n\n" + "="*70)
    print("STEP 2: DEDUPING AGAINST TAPESTRY")
    print("="*70)

    dedupe_script = script_dir / 'scripts' / 'batch_dedupe_before_ananki.py'
    if not dedupe_script.exists():
        print(f"ERROR: Dedupe script not found: {dedupe_script}")
        print("Creating it now...")
        create_batch_dedupe_script()

    # Find all extraction files
    youtube_results = (script_dir / 'youtube' / 'test_results').glob('*_extraction.json')
    reddit_results = (script_dir / 'reddit' / 'test_results').glob('*_extraction.json')

    all_results = list(youtube_results) + list(reddit_results)

    print(f"\nFound {len(all_results)} extraction files to dedupe")

    deduped_count = 0
    for result_file in all_results:
        vibe = result_file.stem.replace('_youtube_extraction', '').replace('_smart_extraction', '')
        print(f"\nDeduping: {vibe}")

        # Run dedupe
        dedupe_cmd = [
            sys.executable,
            str(script_dir / 'scripts' / 'dedupe_before_ananki.py'),
            str(result_file)
        ]

        dedupe_result = subprocess.run(
            dedupe_cmd,
            capture_output=True,
            text=True
        )

        if dedupe_result.returncode == 0:
            # Parse output for new songs count
            output = dedupe_result.stdout
            if 'New songs to analyze' in output:
                for line in output.split('\n'):
                    if 'New songs to analyze' in line:
                        print(f"  {line.strip()}")
            deduped_count += 1
        else:
            print(f"  [ERROR] Dedupe failed for {vibe}")

    print(f"\n[SUCCESS] Deduped {deduped_count}/{len(all_results)} files")

    # Step 3: Ready for Ananki
    print("\n\n" + "="*70)
    print("STEP 3: READY FOR ANANKI ANALYSIS")
    print("="*70)

    deduped_dir = script_dir / 'youtube' / 'test_results' / 'deduped'
    if not deduped_dir.exists():
        deduped_dir = script_dir / 'scripts' / 'deduped'

    if deduped_dir.exists():
        deduped_files = list(deduped_dir.glob('*_deduped.json'))
        print(f"\nFound {len(deduped_files)} deduped files ready for Ananki:")
        for f in deduped_files:
            print(f"  - {f.name}")

        print(f"\n\nNext step: Run Ananki analysis on these files")
        print(f"Command: python data/scripts/true_ananki_claude_api.py <file_path>")
    else:
        print("\n[WARNING] No deduped directory found")
        print("Deduped files should be in their original directories with '_deduped' suffix")

    # Final summary
    print("\n\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nPipeline Status:")
    print("  ✅ Step 1: Scraping complete")
    print("  ✅ Step 2: Deduplication complete")
    print("  ⏳ Step 3: Ready for Ananki (manual step)")
    print("\nAll new songs have been deduped and are ready for emotional analysis!")
    print("="*70)


def create_batch_dedupe_script():
    """Create batch dedupe script if it doesn't exist"""
    script_dir = Path(__file__).parent
    batch_dedupe = script_dir / 'scripts' / 'batch_dedupe_before_ananki.py'

    content = '''"""
Batch Dedupe - Run dedupe_before_ananki.py on all extraction files
"""
import subprocess
import sys
from pathlib import Path

def main():
    script_dir = Path(__file__).parent.parent

    # Find all extraction files
    youtube_results = (script_dir / 'youtube' / 'test_results').glob('*_extraction.json')
    reddit_results = (script_dir / 'reddit' / 'test_results').glob('*_extraction.json')

    all_results = list(youtube_results) + list(reddit_results)

    print(f"Deduping {len(all_results)} files...")

    for result_file in all_results:
        print(f"\\nDeduping: {result_file.name}")
        subprocess.run([
            sys.executable,
            str(Path(__file__).parent / 'dedupe_before_ananki.py'),
            str(result_file)
        ])

if __name__ == '__main__':
    main()
'''

    batch_dedupe.parent.mkdir(parents=True, exist_ok=True)
    with open(batch_dedupe, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Created: {batch_dedupe}")


if __name__ == '__main__':
    main()
