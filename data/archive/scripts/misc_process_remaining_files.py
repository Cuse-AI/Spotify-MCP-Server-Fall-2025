"""
Process all remaining deduped files through Ananki and inject to tapestry
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DEDUPED_DIR = PROJECT_ROOT / '2_deduped'
MAPPED_DIR = PROJECT_ROOT / '3_analyzed' / 'mapped'
SCRIPTS_DIR = Path(__file__).parent

# Files to process (excluding dark_smart which is done)
files_to_process = [
    'night_smart_extraction_DEDUPED.json',
    'party_smart_extraction_DEDUPED.json',
    'dark_youtube_extraction_DEDUPED.json',
    'night_youtube_extraction_DEDUPED.json',
    'party_youtube_extraction_DEDUPED.json',
    'drive_youtube_extraction_DEDUPED.json',
    'happy_youtube_extraction_DEDUPED.json',
    'romantic_youtube_extraction_DEDUPED.json'
]

print("\n" + "="*70)
print(" PROCESSING REMAINING FILES")
print("="*70)
print(f"Files to process: {len(files_to_process)}")
print("This will: Ananki analysis -> Inject to tapestry")
print("="*70 + "\n")

total_injected = 0

for i, filename in enumerate(files_to_process, 1):
    deduped_file = DEDUPED_DIR / filename

    if not deduped_file.exists():
        print(f"[{i}/{len(files_to_process)}] SKIP: {filename} (not found)")
        continue

    print(f"\n[{i}/{len(files_to_process)}] Processing: {filename}")
    print("="*70)

    # Run Ananki
    print("Running Ananki analysis...")
    try:
        result = subprocess.run(
            [sys.executable, 'true_ananki_claude_api.py', str(deduped_file)],
            cwd=SCRIPTS_DIR,
            capture_output=False
        )

        if result.returncode != 0:
            print(f"  [ERROR] Ananki failed for {filename}")
            continue

    except Exception as e:
        print(f"  [ERROR] Exception running Ananki: {e}")
        continue

    # Inject to tapestry
    mapped_file = MAPPED_DIR / f"{deduped_file.stem}_CLAUDE_MAPPED.json"

    if not mapped_file.exists():
        print(f"  [SKIP] No mapped file created: {mapped_file.name}")
        continue

    print(f"\nInjecting {mapped_file.name}...")
    try:
        result = subprocess.run(
            [sys.executable, 'inject_to_tapestry.py', str(mapped_file)],
            cwd=SCRIPTS_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Count injected from output
            if 'Injected:' in result.stdout:
                import re
                match = re.search(r'Injected: (\d+)', result.stdout)
                if match:
                    injected = int(match.group(1))
                    total_injected += injected
                    print(f"  [OK] Injected {injected} songs")
            else:
                print(f"  [OK] Injection complete")
        else:
            print(f"  [ERROR] Injection failed")
            print(result.stderr)

    except Exception as e:
        print(f"  [ERROR] Exception during injection: {e}")

print("\n" + "="*70)
print(" COMPLETE!")
print("="*70)
print(f"Total songs injected: {total_injected}")

# Show final tapestry count
import json
tapestry_file = PROJECT_ROOT.parent / 'core' / 'tapestry.json'
if tapestry_file.exists():
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        t = json.load(f)
    total = sum(len(v['songs']) for v in t['vibes'].values())
    print(f"Tapestry now has: {total:,} songs!")
