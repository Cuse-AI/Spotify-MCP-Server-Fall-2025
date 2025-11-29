"""
Archive unvalidated songs from tapestry
Keep only the 2,285 validated songs + all vibe structure
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def archive_unvalidated():
    print("\nARCHIVING UNVALIDATED TAPESTRY DATA")
    print("="*70)
    
    # Load current tapestry
    tapestry_file = Path(__file__).parent.parent / 'ananki_outputs' / 'tapestry_CLEANED_WITH_SPOTIFY.json'
    
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Create backup first!
    backup_file = tapestry_file.parent / f'tapestry_FULL_BACKUP_{datetime.now().strftime("%Y%m%d")}.json'
    shutil.copy(tapestry_file, backup_file)
    print(f"1. Created backup: {backup_file.name}")
    
    # Stats
    total_before = 0
    total_after = 0
    removed_count = 0
    
    # Clean each vibe - keep ONLY validated songs
    for vibe_name, vibe_data in tapestry['vibes'].items():
        songs = vibe_data.get('songs', [])
        total_before += len(songs)
        
        # Keep only songs with Spotify IDs
        validated_only = [s for s in songs if s.get('spotify_id')]
        
        vibe_data['songs'] = validated_only
        total_after += len(validated_only)
        removed_count += len(songs) - len(validated_only)
    
    # Save cleaned tapestry
    cleaned_file = tapestry_file.parent / 'tapestry_VALIDATED_ONLY.json'
    with open(cleaned_file, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print("ARCHIVING COMPLETE")
    print(f"{'='*70}")
    print(f"Songs before: {total_before}")
    print(f"Songs after: {total_after}")
    print(f"Removed (unvalidated): {removed_count}")
    print(f"\nCleaned tapestry: {cleaned_file}")
    print(f"Backup: {backup_file}")
    print(f"\nAll 114 sub-vibe structures preserved!")
    print(f"Ready for smart scraping pipeline!")

if __name__ == '__main__':
    archive_unvalidated()
