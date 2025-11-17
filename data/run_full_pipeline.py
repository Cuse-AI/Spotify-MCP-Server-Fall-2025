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

    # Step 3: Run Ananki Analysis
    print("\n\n" + "="*70)
    print("STEP 3: ANANKI EMOTIONAL ANALYSIS")
    print("="*70)

    deduped_dir = script_dir / '2_deduped'
    if not deduped_dir.exists():
        print(f"[ERROR] Deduped directory not found: {deduped_dir}")
        return

    deduped_files = list(deduped_dir.glob('*_DEDUPED.json'))
    print(f"\nFound {len(deduped_files)} deduped files for Ananki analysis")

    ananki_script = script_dir / 'scripts' / 'batch_ananki.py'
    if not ananki_script.exists():
        print(f"[ERROR] Ananki script not found: {ananki_script}")
        return

    print("\nRunning Ananki analysis (this will take time)...")
    ananki_result = subprocess.run(
        [sys.executable, str(ananki_script)],
        cwd=str(script_dir / 'scripts')
    )

    if ananki_result.returncode != 0:
        print("\n[ERROR] Ananki analysis failed!")
        return

    print("\n[SUCCESS] Ananki analysis complete!")

    # Step 4: Inject into Tapestry
    print("\n\n" + "="*70)
    print("STEP 4: INJECT INTO TAPESTRY")
    print("="*70)

    ananki_ready_dir = script_dir / '3_ananki_ready'
    if not ananki_ready_dir.exists():
        print(f"[ERROR] Ananki ready directory not found: {ananki_ready_dir}")
        return

    ananki_ready_files = list(ananki_ready_dir.glob('*_ananki_ready.json'))
    print(f"\nFound {len(ananki_ready_files)} Ananki-analyzed files to inject")

    inject_script = script_dir / 'scripts' / 'inject_to_tapestry.py'
    if not inject_script.exists():
        print(f"[ERROR] Inject script not found: {inject_script}")
        return

    for ananki_file in ananki_ready_files:
        vibe = ananki_file.stem.replace('_ananki_ready', '')
        print(f"\nInjecting: {vibe}")

        inject_result = subprocess.run(
            [sys.executable, str(inject_script), str(ananki_file)],
            capture_output=True,
            text=True
        )

        if inject_result.returncode == 0:
            # Show summary
            for line in inject_result.stdout.split('\n'):
                if 'injected' in line.lower() or 'added' in line.lower():
                    print(f"  {line.strip()}")
        else:
            print(f"  [ERROR] Injection failed for {vibe}")

    # Final summary
    print("\n\n" + "="*70)
    print("FULL PIPELINE COMPLETE!")
    print("="*70)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nPipeline Status:")
    print("  ✅ Step 1: Scraping complete")
    print("  ✅ Step 2: Deduplication complete")
    print("  ✅ Step 3: Ananki analysis complete")
    print("  ✅ Step 4: Tapestry injection complete")
    print("\nAll new songs analyzed and added to tapestry!")
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
