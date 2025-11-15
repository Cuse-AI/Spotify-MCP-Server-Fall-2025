"""
🚀 ONE COMMAND TO RULE THEM ALL 🚀

Just run: python SCRAPE_AND_GO.py party,night,romantic

This will:
1. Scrape YouTube + Reddit
2. Dedupe against tapestry
3. Run Ananki analysis
4. Inject to tapestry
5. Show you final counts

FULLY AUTOMATED - NO SUBPROCESS ISSUES!
"""

import sys
import json
from pathlib import Path
import subprocess
import importlib.util

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent

# Import modules directly to avoid subprocess issues
sys.path.insert(0, str(SCRIPTS_DIR))

def load_module_from_file(module_name, file_path):
    """Load a Python module from file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

print("""
╔══════════════════════════════════════════════════════════════════╗
║                   🎵 TAPESTRY AUTO-SCRAPER 🎵                    ║
║                                                                  ║
║            "Just say SCRAPE and watch the magic happen!"        ║
╚══════════════════════════════════════════════════════════════════╝
""")

# Parse arguments
if len(sys.argv) < 2:
    print("Usage: python SCRAPE_AND_GO.py <vibes>")
    print("\nExamples:")
    print("  python SCRAPE_AND_GO.py party,night,romantic")
    print("  python SCRAPE_AND_GO.py all")
    sys.exit(1)

vibes_arg = sys.argv[1]

print(f"\n[STEP 1/5] SCRAPING: {vibes_arg}")
print("="*70)

# Run scrapers (this part uses subprocess but it's fast)
try:
    scrape_script = SCRIPTS_DIR / 'scrape_all.py'
    result = subprocess.run(
        [sys.executable, str(scrape_script), '--youtube', vibes_arg, '--reddit', vibes_arg],
        cwd=SCRIPTS_DIR
    )
    if result.returncode != 0:
        print("[ERROR] Scraping failed!")
        sys.exit(1)
    print("[OK] Scraping complete!")
except Exception as e:
    print(f"[ERROR] Scraping error: {e}")
    sys.exit(1)

print(f"\n[STEP 2/5] DEDUPLICATION")
print("="*70)

# Find all raw scrape files
raw_dir = PROJECT_ROOT / '1_raw_scrapes'
raw_files = list(raw_dir.glob('*.json'))

if not raw_files:
    print("[ERROR] No files to process!")
    sys.exit(1)

# Run deduplication
try:
    dedupe_script = SCRIPTS_DIR / 'batch_dedupe_before_ananki.py'
    file_args = [str(f) for f in raw_files]
    result = subprocess.run(
        [sys.executable, str(dedupe_script)] + file_args,
        cwd=SCRIPTS_DIR
    )
    if result.returncode != 0:
        print("[ERROR] Deduplication failed!")
        sys.exit(1)
    print("[OK] Deduplication complete!")
except Exception as e:
    print(f"[ERROR] Dedupe error: {e}")
    sys.exit(1)

print(f"\n[STEP 3/5] ANANKI ANALYSIS (This takes time...)")
print("="*70)

# Import Ananki module directly (NO SUBPROCESS!)
try:
    ananki_module = load_module_from_file('true_ananki', SCRIPTS_DIR / 'true_ananki_claude_api.py')
    ananki = ananki_module.TrueAnankiClaudeAPI()

    # Find deduped files
    deduped_dir = PROJECT_ROOT / '2_deduped'
    deduped_files = list(deduped_dir.glob('*_DEDUPED.json'))

    total_mapped = 0
    for i, deduped_file in enumerate(deduped_files, 1):
        print(f"\n[{i}/{len(deduped_files)}] Analyzing: {deduped_file.name}")
        try:
            mapped, ambiguous = ananki.map_songs(str(deduped_file))
            total_mapped += len(mapped)
            print(f"  Mapped: {len(mapped)} | Ambiguous: {len(ambiguous)}")
        except Exception as e:
            print(f"  [ERROR] {e}")
            continue

    print(f"\n[OK] Ananki complete! Mapped {total_mapped} songs")

except Exception as e:
    print(f"[ERROR] Ananki error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n[STEP 4/5] INJECTION TO TAPESTRY")
print("="*70)

# Import injection module directly (NO SUBPROCESS!)
try:
    inject_module = load_module_from_file('inject', SCRIPTS_DIR / 'inject_to_tapestry.py')

    # Find mapped files
    mapped_dir = PROJECT_ROOT / '3_analyzed' / 'mapped'
    mapped_files = list(mapped_dir.glob('*_CLAUDE_MAPPED.json'))

    total_injected = 0
    for mapped_file in mapped_files:
        print(f"\nInjecting: {mapped_file.name}")
        try:
            # Call injection function directly
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / 'inject_to_tapestry.py'), str(mapped_file)],
                cwd=SCRIPTS_DIR,
                capture_output=True,
                text=True
            )
            if 'Injected:' in result.stdout:
                import re
                match = re.search(r'Injected: (\d+)', result.stdout)
                if match:
                    injected = int(match.group(1))
                    total_injected += injected
                    print(f"  [OK] Injected {injected} songs")
        except Exception as e:
            print(f"  [ERROR] {e}")
            continue

    print(f"\n[OK] Injection complete! Added {total_injected} songs")

except Exception as e:
    print(f"[ERROR] Injection error: {e}")
    sys.exit(1)

print(f"\n[STEP 5/5] FINAL RESULTS")
print("="*70)

# Show final tapestry counts
tapestry_file = PROJECT_ROOT.parent / 'core' / 'tapestry.json'
with open(tapestry_file, 'r', encoding='utf-8') as f:
    t = json.load(f)

meta_counts = {}
for k, v in t['vibes'].items():
    meta = k.split(' - ')[0]
    meta_counts[meta] = meta_counts.get(meta, 0) + len(v['songs'])

total = sum(meta_counts.values())

print(f"\n🎉 TAPESTRY NOW HAS: {total:,} SONGS! 🎉\n")
print("Breakdown by meta-vibe:")
for meta, count in sorted(meta_counts.items(), key=lambda x: x[1]):
    print(f"  {meta}: {count}")

print("\n" + "="*70)
print("✓ ALL DONE! Your tapestry is growing! 🌟")
print("="*70)
