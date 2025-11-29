"""
Batch run Ananki on all deduped files
"""

import subprocess
import sys
from pathlib import Path
import time

def run_ananki(deduped_file):
    """Run Ananki on a single deduped file"""
    file_path = Path(deduped_file)
    vibe_name = file_path.stem.replace('_DEDUPED', '')

    print(f"\n{'='*70}")
    print(f"Processing: {vibe_name}")
    print(f"{'='*70}")

    try:
        result = subprocess.run(
            [sys.executable, 'true_ananki_claude_api.py', str(file_path)],
            cwd=str(Path(__file__).parent),
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode == 0:
            # Show summary from output
            output_lines = result.stdout.strip().split('\n')
            summary_lines = [l for l in output_lines if 'songs analyzed' in l.lower() or 'saved to' in l.lower() or 'cost' in l.lower()]

            print(f"[SUCCESS] {vibe_name}")
            for line in summary_lines[-5:]:
                print(f"  {line.strip()}")
            return True
        else:
            print(f"[FAILED] {vibe_name}")
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                for line in error_lines[-3:]:
                    print(f"  {line}")
            return False

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {vibe_name}")
        return False
    except Exception as e:
        print(f"[ERROR] {vibe_name}: {e}")
        return False

def main():
    deduped_dir = Path(__file__).parent.parent / '2_deduped'

    if not deduped_dir.exists():
        print(f"ERROR: Deduped directory not found: {deduped_dir}")
        return

    deduped_files = sorted(deduped_dir.glob('*_DEDUPED.json'))

    print("\n" + "="*70)
    print("BATCH ANANKI ANALYSIS")
    print("="*70)
    print(f"Found {len(deduped_files)} deduped files to process")
    print("="*70)

    success_count = 0
    fail_count = 0

    for i, deduped_file in enumerate(deduped_files, 1):
        print(f"\n[{i}/{len(deduped_files)}]")

        if run_ananki(deduped_file):
            success_count += 1
        else:
            fail_count += 1

        # Small delay between files
        if i < len(deduped_files):
            time.sleep(1)

    print(f"\n\n{'='*70}")
    print("BATCH ANANKI COMPLETE")
    print(f"{'='*70}")
    print(f"Success: {success_count}/{len(deduped_files)}")
    print(f"Failed: {fail_count}/{len(deduped_files)}")
    print("="*70)

if __name__ == '__main__':
    main()
