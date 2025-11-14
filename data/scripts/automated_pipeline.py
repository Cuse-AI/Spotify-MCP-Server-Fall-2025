"""
AUTOMATED TAPESTRY PIPELINE
Monitors 1_raw_scrapes/ and automatically processes new files through the entire workflow:
1. Dedupe (→ 2_deduped/)
2. Ananki Analysis (→ 3_analyzed/mapped/)
3. Inject to Tapestry (→ 4_injected/)

Run this after scraping completes!
"""

import json
import os
import sys
import subprocess
from pathlib import Path
import time

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / '1_raw_scrapes'
DEDUPED_DIR = PROJECT_ROOT / '2_deduped'
ANALYZED_DIR = PROJECT_ROOT / '3_analyzed' / 'mapped'
INJECTED_DIR = PROJECT_ROOT / '4_injected'
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'

def run_command(cmd, desc):
    """Run a command and show output"""
    print(f"\n{'='*70}")
    print(f"⚡ {desc}")
    print(f"{'='*70}")
    
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=SCRIPTS_DIR,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    return True

def process_pipeline():
    print("\n" + "="*70)
    print("🎵 AUTOMATED TAPESTRY PIPELINE")
    print("="*70)
    
    # Find all files in 1_raw_scrapes/
    raw_files = list(RAW_DIR.glob('*.json'))
    
    if not raw_files:
        print("\n✅ No new files in 1_raw_scrapes/ - nothing to process!")
        return
    
    print(f"\nFound {len(raw_files)} files to process:\n")
    for f in raw_files:
        print(f"  📄 {f.name}")
    
    input("\nPress Enter to start automated processing...")
    
    # STEP 1: BATCH DEDUPE
    print("\n" + "🔸"*35)
    print("STEP 1: BATCH DEDUPLICATION")
    print("🔸"*35)
    
    file_args = ' '.join([f'"{f}"' for f in raw_files])
    dedupe_cmd = f'python batch_dedupe_before_ananki.py {file_args}'
    
    if not run_command(dedupe_cmd, "Running batch deduplication"):
        print("❌ Deduplication failed!")
        return
    
    # STEP 2: RUN ANANKI ON ALL DEDUPED FILES
    print("\n" + "🔸"*35)
    print("STEP 2: TRUE ANANKI ANALYSIS")
    print("🔸"*35)
    
    deduped_files = list(DEDUPED_DIR.glob('*_DEDUPED.json'))
    # Filter to only files that don't have MAPPED versions yet
    need_ananki = []
    for f in deduped_files:
        mapped_file = ANALYZED_DIR / f"{f.stem}_CLAUDE_MAPPED.json"
        if not mapped_file.exists():
            need_ananki.append(f)
    
    if not need_ananki:
        print("✅ All deduped files already analyzed!")
    else:
        print(f"\nRunning Ananki on {len(need_ananki)} files...")
        
        for f in need_ananki:
            ananki_cmd = f'python true_ananki_claude_api.py "{f}"'
            if not run_command(ananki_cmd, f"Analyzing {f.name}"):
                print(f"⚠️  Skipping {f.name} due to error")
                continue
    
    # STEP 3: INJECT TO TAPESTRY
    print("\n" + "🔸"*35)
    print("STEP 3: INJECT TO TAPESTRY")
    print("🔸"*35)
    
    mapped_files = list(ANALYZED_DIR.glob('*_CLAUDE_MAPPED.json'))
    
    if not mapped_files:
        print("⚠️  No mapped files found in 3_analyzed/mapped/")
        return
    
    print(f"\nInjecting {len(mapped_files)} files to tapestry...")
    
    for f in mapped_files:
        inject_cmd = f'python inject_to_tapestry.py "{f}"'
        if not run_command(inject_cmd, f"Injecting {f.name}"):
            print(f"⚠️  Skipping {f.name} due to error")
            continue
        
        # Move to 4_injected/
        dest = INJECTED_DIR / f.name
        f.rename(dest)
        print(f"📦 Moved to: {dest}")
        
        # Also move the ambiguous file if it exists
        ambig_file = f.parent.parent / 'ambiguous' / f"{f.stem.replace('_MAPPED', '_AMBIGUOUS')}.json"
        if ambig_file.exists():
            ambig_dest = INJECTED_DIR / ambig_file.name
            ambig_file.rename(ambig_dest)
    
    # STEP 4: CLEANUP - Move raw files to archive
    print("\n" + "🔸"*35)
    print("STEP 4: CLEANUP")
    print("🔸"*35)
    
    archive_dir = PROJECT_ROOT / 'archive' / 'processed_scrapes'
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    for f in raw_files:
        if f.exists():  # Still exists (wasn't moved yet)
            dest = archive_dir / f.name
            f.rename(dest)
            print(f"📁 Archived: {f.name}")
    
    # Move deduped files too
    for f in DEDUPED_DIR.glob('*.json'):
        if not f.name.endswith('_CHECKPOINT.json'):  # Keep checkpoints
            dest = archive_dir / f.name
            f.rename(dest)
    
    print("\n" + "="*70)
    print("🎊 PIPELINE COMPLETE!")
    print("="*70)
    
    # Show final stats
    from pathlib import Path
    tapestry_file = PROJECT_ROOT / 'core' / 'tapestry.json'
    if tapestry_file.exists():
        t = json.load(open(tapestry_file, encoding='utf-8'))
        total = sum(len(v['songs']) for v in t['vibes'].values())
        print(f"\n✨ Tapestry now has: {total:,} songs!")

if __name__ == '__main__':
    process_pipeline()
