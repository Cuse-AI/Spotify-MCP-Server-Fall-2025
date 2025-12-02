"""
Run coordinate assignment on the quality tapestry (score 3+)
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ananki.helper_coordinates import CoordinateAssigner
from datetime import datetime

# Load quality tapestry
tapestry_path = project_root / "core" / "tapestry_quality.json"
with open(tapestry_path, 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Count songs
total_songs = sum(len(v.get('songs', [])) for v in tapestry['vibes'].values())
print(f"Loaded quality tapestry with {total_songs} songs")

# Initialize assigner
assigner = CoordinateAssigner()

# Process each vibe
processed = 0
output_dir = project_root / "ananki" / "output"
checkpoint_path = output_dir / "COORDS_QUALITY_CHECKPOINT.json"

for vibe_name, vibe_data in tapestry['vibes'].items():
    songs = vibe_data.get('songs', [])
    if not songs:
        continue
    
    print(f"\n[{vibe_name}] Processing {len(songs)} songs...")
    
    for i, song in enumerate(songs):
        # Add current_vibe for context
        song['current_vibe'] = vibe_name
        
        # Assign coordinates
        result = assigner.assign_coordinates(song)
        
        # Update in place
        songs[i] = result
        processed += 1
        
        coords = result['coordinates']
        if processed % 20 == 0:
            print(f"  [{processed}/{total_songs}] {song.get('artist', '?')[:15]} - {song.get('song', '?')[:20]} -> ({coords['x']:.0f}, {coords['y']:.0f})")
        
        # Checkpoint every 100
        if processed % 100 == 0:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump({'tapestry': tapestry, 'processed': processed}, f, ensure_ascii=False)
            print(f"  [CHECKPOINT] {processed}/{total_songs}")

# Final save
final_path = project_root / "core" / "tapestry_quality_final.json"
with open(final_path, 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"[COMPLETE] Assigned coordinates to {processed} songs")
print(f"Saved to: {final_path}")
print('='*60)
