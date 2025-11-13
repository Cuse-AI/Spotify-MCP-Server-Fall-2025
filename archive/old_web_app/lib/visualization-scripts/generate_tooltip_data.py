"""
Generate real sub-vibe data for interactive map tooltips
Uses actual songs from tapestry with Ananki reasoning
"""

import json
from pathlib import Path

# Load tapestry
tapestry_file = Path('tapestry_VALIDATED_ONLY.json')
with open(tapestry_file, 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Build tooltip data for each sub-vibe
updated_subvibes = {}

for subvibe_name, subvibe_data in tapestry['vibes'].items():
    songs = subvibe_data.get('songs', [])
    
    if len(songs) > 0:
        # Get first song as example
        example_song = songs[0]
        
        # Build analysis text from real data
        song_count = len(songs)
        artist = example_song.get('artist', 'Unknown')
        song_name = example_song.get('song', 'Unknown')
        reasoning = example_song.get('ananki_reasoning', 'No reasoning available')[:200]
        
        analysis_text = f"{song_count} songs. Example: {artist} - {song_name}. {reasoning}..."
        
    else:
        analysis_text = "No songs yet - needs scraping!"
    
    # Keep existing coordinates and composition
    if subvibe_name in manifold_data['sub_vibes']:
        updated_subvibes[subvibe_name] = {
            'emotional_composition': manifold_data['sub_vibes'][subvibe_name]['emotional_composition'],
            'coordinates': manifold_data['sub_vibes'][subvibe_name]['coordinates'],
            'analysis': analysis_text,
            'song_count': len(songs)
        }

print(f'Updated {len(updated_subvibes)} sub-vibes with real data!')
print(f'Empty sub-vibes: {114 - len(updated_subvibes)}')

# Save for inspection
with open('updated_subvibe_tooltips.json', 'w', encoding='utf-8') as f:
    json.dump(updated_subvibes, f, indent=2, ensure_ascii=False)

print('Saved to: updated_subvibe_tooltips.json')
