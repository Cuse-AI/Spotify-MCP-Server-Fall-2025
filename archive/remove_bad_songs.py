"""
Remove specific problematic songs from tapestry
"""

import json

def remove_songs():
    # Load tapestry
    with open('tapestry.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    vibes = data.get('vibes', {})

    removed_count = 0

    for vibe_name, vibe_data in vibes.items():
        if 'songs' not in vibe_data:
            continue

        original_count = len(vibe_data['songs'])

        # Filter out the two problematic songs
        vibe_data['songs'] = [
            song for song in vibe_data['songs']
            if not (
                # Remove "Soft Calming Music" channel entry (artist/song are swapped)
                (song.get('artist') == 'Relaxing Music for Stress Relief' and
                 song.get('song') == 'Soft Calming Music')
                or
                # Remove "I Ain't Worried" by OneRepublic
                (song.get('artist') == 'OneRepublic' and
                 song.get('song') == "I Ain't Worried")
            )
        ]

        removed = original_count - len(vibe_data['songs'])
        if removed > 0:
            removed_count += removed
            print(f"[OK] {vibe_name}: Removed {removed} song(s)")

    # Save updated tapestry
    with open('tapestry.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n[DONE] Total removed: {removed_count} songs")

    # Count final songs
    total_songs = sum(
        len(vibe_data.get('songs', []))
        for vibe_data in vibes.values()
    )
    print(f"[STATS] Final count: {total_songs} songs")

if __name__ == '__main__':
    remove_songs()
