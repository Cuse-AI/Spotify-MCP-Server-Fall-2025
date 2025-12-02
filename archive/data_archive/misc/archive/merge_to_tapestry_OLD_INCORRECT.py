"""
Merge validated songs into the Tapestry

Takes the 1,147 confirmed songs and integrates them into tapestry_map.json
"""

import json
from pathlib import Path
from collections import defaultdict

def load_current_tapestry():
    """Load the existing tapestry."""
    tapestry_file = Path(__file__).parent.parent.parent / 'ananki_outputs' / 'tapestry_CLEANED_WITH_SPOTIFY.json'
    
    if not tapestry_file.exists():
        print("ERROR: tapestry_map.json not found!")
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


def deduplicate_songs(songs_list):
    """Remove duplicates based on artist + song."""
    seen = set()
    unique = []
    
    for song in songs_list:
        key = (song['artist'].lower(), song['song'].lower())
        if key not in seen:
            seen.add(key)
            unique.append(song)
    
    return unique


def merge_into_tapestry(tapestry, new_songs):
    """
    Merge new songs into tapestry structure.
    Adds to appropriate vibe nodes.
    """
    stats = {
        'total_new': len(new_songs),
        'added': 0,
        'duplicates': 0,
        'by_vibe': defaultdict(int)
    }
    
    # Get existing songs for deduplication
    existing_songs = set()
    for vibe_name, vibe_data in tapestry.get('vibes', {}).items():
        for song in vibe_data.get('songs', []):
            key = (song['artist'].lower(), song['song'].lower())
            existing_songs.add(key)
    
    # Add new songs to appropriate vibes
    for song in new_songs:
        song_key = (song['artist'].lower(), song['song'].lower())
        
        # Check if duplicate
        if song_key in existing_songs:
            stats['duplicates'] += 1
            continue
        
        # Find the vibe
        vibe = song['vibe']
        
        # Make sure vibe exists in tapestry
        if vibe not in tapestry.get('vibes', {}):
            print(f"WARNING: Vibe '{vibe}' not in tapestry! Skipping song.")
            continue
        
        # Add song to vibe
        if 'songs' not in tapestry['vibes'][vibe]:
            tapestry['vibes'][vibe]['songs'] = []
        
        tapestry['vibes'][vibe]['songs'].append(song)
        stats['added'] += 1
        stats['by_vibe'][vibe] += 1
        existing_songs.add(song_key)
    
    return tapestry, stats


def main():
    print("\nMERGING VALIDATED SONGS TO TAPESTRY")
    print("=" * 60)
    
    # 1. Load tapestry
    print("\n1. Loading tapestry...")
    tapestry = load_current_tapestry()
    if not tapestry:
        return
    
    original_vibe_count = len(tapestry.get('vibes', {}))
    print(f"   Current vibes: {original_vibe_count}")
    
    # 2. Load confirmed songs
    print("\n2. Loading confirmed songs...")
    confirmed = load_confirmed_songs()
    print(f"   Confirmed songs to add: {len(confirmed)}")
    
    # 3. Deduplicate within new songs
    print("\n3. Deduplicating new songs...")
    unique_new = deduplicate_songs(confirmed)
    print(f"   Unique new songs: {len(unique_new)}")
    print(f"   Duplicates removed: {len(confirmed) - len(unique_new)}")
    
    # 4. Merge
    print("\n4. Merging into tapestry...")
    updated_tapestry, stats = merge_into_tapestry(tapestry, unique_new)
    
    # 5. Save updated tapestry
    tapestry_file = Path(__file__).parent.parent.parent / 'ananki_outputs' / 'tapestry_CLEANED_WITH_SPOTIFY.json'
    backup_file = tapestry_file.parent / f'tapestry_backup_before_batch1-8_merge.json'
    
    # Backup first
    print("\n5. Creating backup...")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    print(f"   Backup: {backup_file.name}")
    
    # Save updated
    with open(tapestry_file, 'w', encoding='utf-8') as f:
        json.dump(updated_tapestry, f, indent=2, ensure_ascii=False)
    
    # 6. Print results
    print("\n" + "=" * 60)
    print("MERGE COMPLETE!")
    print("=" * 60)
    print(f"Added to tapestry: {stats['added']} songs")
    print(f"Skipped (duplicates): {stats['duplicates']} songs")
    print(f"\nBreakdown by vibe:")
    for vibe, count in sorted(stats['by_vibe'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {vibe}: +{count} songs")
    
    print(f"\nUpdated tapestry saved to: {tapestry_file}")
    
    return updated_tapestry


if __name__ == '__main__':
    main()
