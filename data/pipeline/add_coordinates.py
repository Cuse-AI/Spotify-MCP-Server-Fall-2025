"""
ADD COORDINATES TO EXISTING SONGS
=================================
Assigns x,y coordinates to all songs based on their sub-vibe.
Adds slight randomization so songs in same sub-vibe spread out naturally.
"""

import json
import random
from pathlib import Path

def add_coordinates_to_tapestry():
    project_root = Path(__file__).parent.parent.parent
    
    # Load manifold for sub-vibe coordinates
    manifold_path = project_root / "data" / "manifold" / "emotional_manifold_COMPLETE.json"
    with open(manifold_path, 'r', encoding='utf-8') as f:
        manifold = json.load(f)
    
    subvibe_coords = {}
    for sv_name, sv_data in manifold.get('sub_vibes', {}).items():
        if 'coordinates' in sv_data:
            subvibe_coords[sv_name] = sv_data['coordinates']
    
    print(f"Loaded coordinates for {len(subvibe_coords)} sub-vibes")
    
    # Load tapestry
    tapestry_path = project_root / "core" / "tapestry.json"
    with open(tapestry_path, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Add coordinates to each song
    total_songs = 0
    songs_with_coords = 0
    missing_subvibes = set()
    
    for vibe_name, vibe_data in tapestry['vibes'].items():
        for song in vibe_data.get('songs', []):
            total_songs += 1
            
            # Get base coordinates from sub-vibe
            if vibe_name in subvibe_coords:
                base = subvibe_coords[vibe_name]
                
                # Add slight randomization (radius of ~20 units)
                # This spreads songs out within their sub-vibe cluster
                jitter_x = random.gauss(0, 8)
                jitter_y = random.gauss(0, 8)
                
                song['coordinates'] = {
                    'x': round(base['x'] + jitter_x, 2),
                    'y': round(base['y'] + jitter_y, 2)
                }
                songs_with_coords += 1
            else:
                missing_subvibes.add(vibe_name)
                # Fallback to center
                song['coordinates'] = {'x': 500, 'y': 500}
    
    # Save updated tapestry
    with open(tapestry_path, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    
    print(f"\n[DONE] Added coordinates to {songs_with_coords}/{total_songs} songs")
    
    if missing_subvibes:
        print(f"\n[WARNING] These sub-vibes had no coordinates in manifold:")
        for sv in sorted(missing_subvibes):
            print(f"  - {sv}")
    
    return songs_with_coords, total_songs

if __name__ == "__main__":
    add_coordinates_to_tapestry()
