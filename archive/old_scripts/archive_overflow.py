"""
Archive Overflow Songs - Balance the Tapestry
Keeps best songs from over-represented vibes, archives the rest
"""

import json
from pathlib import Path
from datetime import datetime
import shutil

def archive_overflow():
    print("="*70)
    print("ARCHIVING OVERFLOW - BALANCING TAPESTRY")
    print("="*70)
    
    # Load tapestry
    tapestry_file = Path('tapestry_VALIDATED_ONLY.json')
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Create archive directory
    archive_dir = Path('tapestry_overflow')
    archive_dir.mkdir(exist_ok=True)
    
    # Settings
    MAX_PER_SUBVIBE = 150  # Keep top 150 per sub-vibe
    
    archived_songs = {}
    total_archived = 0
    total_kept = 0
    
    for subvibe_name, subvibe_data in tapestry['vibes'].items():
        songs = subvibe_data.get('songs', [])
        
        if len(songs) > MAX_PER_SUBVIBE:
            # Sort by quality (Ananki confidence, then comment score)
            sorted_songs = sorted(
                songs,
                key=lambda s: (
                    s.get('ananki_confidence', s.get('mapping_confidence', 0)),
                    s.get('comment_score', 0)
                ),
                reverse=True
            )
            
            # Keep top MAX_PER_SUBVIBE
            keep = sorted_songs[:MAX_PER_SUBVIBE]
            archive = sorted_songs[MAX_PER_SUBVIBE:]
            
            print(f"{subvibe_name:30} {len(songs):4} -> Keeping {len(keep)}, Archiving {len(archive)}")
            
            tapestry['vibes'][subvibe_name]['songs'] = keep
            archived_songs[subvibe_name] = archive
            
            total_archived += len(archive)
            total_kept += len(keep)
        else:
            total_kept += len(songs)
    
    # Save updated tapestry
    print(f"\n{' '*70}")
    print(f"Total archived: {total_archived} songs")
    print(f"Total kept: {total_kept} songs")
    print(f"Reduction: {total_archived / (total_archived + total_kept) * 100:.1f}%")
    
    # Backup original
    backup_file = archive_dir / f'tapestry_BEFORE_ARCHIVE_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    shutil.copy(tapestry_file, backup_file)
    print(f"\nBackup saved: {backup_file}")
    
    # Save archived songs
    if archived_songs:
        archive_file = archive_dir / f'archived_overflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump({
                'archived_date': datetime.now().isoformat(),
                'total_archived': total_archived,
                'reason': f'Overflow - kept top {MAX_PER_SUBVIBE} per sub-vibe by quality',
                'songs_by_subvibe': archived_songs
            }, f, indent=2, ensure_ascii=False)
        print(f"Archived songs saved: {archive_file}")
    
    # Save balanced tapestry
    with open(tapestry_file, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    
    print(f"\nBalanced tapestry saved: {tapestry_file}")
    print("="*70)
    
    return total_kept, total_archived

if __name__ == '__main__':
    kept, archived = archive_overflow()
    print(f"\n✅ Tapestry balanced!")
    print(f"   Active songs: {kept}")
    print(f"   Archived: {archived}")
    print(f"\nYou can restore archived songs anytime from tapestry_overflow/")
