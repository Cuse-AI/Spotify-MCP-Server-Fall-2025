"""
Balance Tapestry by Archiving Overflow Sad Songs
Keeps top songs by quality, archives the rest
"""

import json
from pathlib import Path
from datetime import datetime
import shutil

print("="*70)
print("BALANCING TAPESTRY - ARCHIVING SAD OVERFLOW")
print("="*70)

# Load tapestry
tapestry_file = Path('tapestry_VALIDATED_ONLY.json')
with open(tapestry_file, 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Create archive folder
archive_dir = Path('tapestry_overflow')
archive_dir.mkdir(exist_ok=True)

# Target: Keep 150 best songs per Sad sub-vibe
TARGET_PER_SUBVIBE = 150

sad_subvibes = [v for v in tapestry['vibes'].keys() if v.startswith('Sad - ')]

archived_total = 0
kept_total = 0

for subvibe in sad_subvibes:
    songs = tapestry['vibes'][subvibe].get('songs', [])
    
    if len(songs) <= TARGET_PER_SUBVIBE:
        print(f"{subvibe}: {len(songs)} songs (keeping all)")
        kept_total += len(songs)
        continue
    
    # Sort by quality: confidence score, then comment score
    sorted_songs = sorted(
        songs,
        key=lambda s: (s.get('ananki_confidence', 0), s.get('mapping_confidence', 0), s.get('comment_score', 0)),
        reverse=True
    )
    
    # Keep top 150
    keep_songs = sorted_songs[:TARGET_PER_SUBVIBE]
    archive_songs = sorted_songs[TARGET_PER_SUBVIBE:]
    
    print(f"{subvibe}: {len(songs)} songs → Keeping {len(keep_songs)}, Archiving {len(archive_songs)}")
    
    # Save archived songs
    if archive_songs:
        archive_file = archive_dir / f"{subvibe.lower().replace(' - ', '_')}_overflow.json"
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump({
                'subvibe': subvibe,
                'archived_date': datetime.now().isoformat(),
                'reason': 'Tapestry balancing - can restore if needed',
                'songs': archive_songs
            }, f, indent=2, ensure_ascii=False)
    
    # Update tapestry with kept songs
    tapestry['vibes'][subvibe]['songs'] = keep_songs
    
    archived_total += len(archive_songs)
    kept_total += len(keep_songs)

# Save balanced tapestry
backup_file = Path(f'tapestry_BEFORE_BALANCING_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
shutil.copy(tapestry_file, backup_file)
print(f"\nBackup saved: {backup_file}")

with open(tapestry_file, 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print("\n" + "="*70)
print("BALANCING COMPLETE")
print("="*70)
print(f"Sad songs kept: {kept_total}")
print(f"Sad songs archived: {archived_total}")
print(f"Reduction: {archived_total/(kept_total+archived_total)*100:.1f}% of Sad removed")
print(f"\nArchived to: {archive_dir}/")
print(f"Backup saved: {backup_file}")
print("\nTapestry is now more balanced!")
print("="*70)
