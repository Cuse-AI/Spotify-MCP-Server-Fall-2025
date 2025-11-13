"""
FIXED: Properly replace unvalidated songs with validated versions
Instead of just adding, we remove the old entry first
"""
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def load_current_tapestry():
    """Load the existing tapestry."""
    tapestry_file = Path(__file__).parent.parent.parent / 'ananki_outputs' / 'tapestry_CLEANED_WITH_SPOTIFY.json'
    
    if not tapestry_file.exists():
        print("ERROR: tapestry not found!")
        return None
    
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_confirmed_songs():
    """Load songs ready to add."""
    base_dir = Path(__file__).parent
    songs_file = base_dir.parent / 'confirmed_songs_for_tapestry.json'
    
    with open(songs_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['songs']

def replace_and_merge_songs(tapestry, new_songs):
    """
    REPLACE unvalidated songs with validated versions.
    Remove old entry first, then add new validated entry.
    """
    stats = {
        'total_new': len(new_songs),
        'replaced': 0,
        'added_new': 0,
        'by_vibe': defaultdict(int)
    }
    
    # For each vibe, process songs
    for vibe_name, vibe_data in tapestry.get('vibes', {}).items():
        if 'songs' not in vibe_data:
            vibe_data['songs'] = []
        
        existing_songs = vibe_data['songs']
        
        # Find songs to replace/add in this vibe
        relevant_new_songs = [s for s in new_songs if s['vibe'] == vibe_name]
        
        if not relevant_new_songs:
            continue
        
        # Build lookup of new songs by normalized key
        new_songs_dict = {}
        for song in relevant_new_songs:
            key = (song['artist'].lower().strip(), song['song'].lower().strip())
            new_songs_dict[key] = song
        
        # Remove old versions and track what was removed
        songs_to_keep = []
        for existing_song in existing_songs:
            key = (existing_song.get('artist', '').lower().strip(), 
                   existing_song.get('song', '').lower().strip())
            
            if key in new_songs_dict:
                # This song has a validated replacement - skip the old version
                stats['replaced'] += 1
            else:
                # Keep this song (no replacement available)
                songs_to_keep.append(existing_song)
        
        # Add all the new validated songs
        for song in relevant_new_songs:
            songs_to_keep.append(song)
            key = (song['artist'].lower().strip(), song['song'].lower().strip())
            
            # Was it a replacement or truly new?
            found_match = any(
                (s.get('artist', '').lower().strip(), s.get('song', '').lower().strip()) == key
                for s in existing_songs
            )
            
            if not found_match:
                stats['added_new'] += 1
            
            stats['by_vibe'][vibe_name] += 1
        
        # Update the vibe with cleaned songs
        vibe_data['songs'] = songs_to_keep
    
    return tapestry, stats

def main():
    print("\nREPLACING UNVALIDATED SONGS WITH VALIDATED VERSIONS")
    print("=" * 70)
    
    # Load tapestry
    print("\n1. Loading tapestry...")
    tapestry = load_current_tapestry()
    if not tapestry:
        return
    
    original_song_count = sum(len(v.get('songs', [])) for v in tapestry.get('vibes', {}).values())
    print(f"   Current total songs: {original_song_count}")
    
    # Load confirmed songs
    print("\n2. Loading validated songs...")
    confirmed = load_confirmed_songs()
    print(f"   Validated songs to process: {len(confirmed)}")
    
    # Replace and merge
    print("\n3. Replacing unvalidated with validated...")
    updated_tapestry, stats = replace_and_merge_songs(tapestry, confirmed)
    
    new_song_count = sum(len(v.get('songs', [])) for v in updated_tapestry.get('vibes', {}).values())
    
    # Save with backup
    tapestry_file = Path(__file__).parent.parent.parent / 'ananki_outputs' / 'tapestry_CLEANED_WITH_SPOTIFY.json'
    backup_file = tapestry_file.parent / f'tapestry_backup_before_PROPER_merge.json'
    
    print("\n4. Creating backup...")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    print(f"   Backup: {backup_file.name}")
    
    # Save updated
    with open(tapestry_file, 'w', encoding='utf-8') as f:
        json.dump(updated_tapestry, f, indent=2, ensure_ascii=False)
    
    # Print results
    print("\n" + "=" * 70)
    print("MERGE COMPLETE!")
    print("=" * 70)
    print(f"Original song count: {original_song_count}")
    print(f"New song count: {new_song_count}")
    print(f"Net change: {new_song_count - original_song_count:+d}")
    print(f"\nReplaced (upgraded): {stats['replaced']} songs")
    print(f"Added (truly new): {stats['added_new']} songs")
    print(f"\nTop vibes updated:")
    for vibe, count in sorted(stats['by_vibe'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {vibe}: {count} songs")
    
    print(f"\nUpdated tapestry saved!")
    
    return updated_tapestry

if __name__ == '__main__':
    main()
