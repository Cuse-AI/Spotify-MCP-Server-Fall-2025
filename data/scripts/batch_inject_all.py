"""
Batch inject all CLAUDE_MAPPED files to restore TRUE Ananki tapestry
"""
import subprocess
from pathlib import Path

# Files are now in 3_analyzed/mapped/ directory
mapped_dir = Path(__file__).parent.parent / '3_analyzed' / 'mapped'
all_files = sorted(mapped_dir.glob('*_CLAUDE_MAPPED.json'))

print(f"\nFound {len(all_files)} CLAUDE_MAPPED files")
print("="*70)

total_injected = 0

for i, file in enumerate(all_files, 1):
    vibe_name = file.stem.replace('_youtube_extraction_CLAUDE_MAPPED', '').replace('_youtube_extraction_DEDUPED_CLAUDE_MAPPED', '').replace('_smart_extraction_CLAUDE_MAPPED', '').replace('_checkpoint_DEDUPED_CLAUDE_MAPPED', '')

    print(f"\n[{i}/{len(all_files)}] {vibe_name}")

    result = subprocess.run(
        ['python', 'inject_to_tapestry.py', str(file)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    # Extract counts
    for line in result.stdout.split('\n'):
        if line.startswith('Injected:'):
            count = int(line.split(':')[1].split()[0])
            total_injected += count
            print(f"  +{count} songs")
            break

print("\n" + "="*70)
print(f"TOTAL INJECTED: {total_injected:,} songs")
print("="*70)
