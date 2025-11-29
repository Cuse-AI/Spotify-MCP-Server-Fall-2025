# -*- coding: utf-8 -*-
"""
Remove empty/useless sub-vibes from tapestry and manifold.
These sub-vibes either don't match natural language or overlap with others.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Sub-vibes to remove
REMOVE_VIBES = [
    'Chill - Lounge',           # Umbrella under Jazz/Evening
    'Dark - Anxious Social Anxiety',  # Too specific
    'Dark - Competitive',       # Doesn't fit Dark
    'Dark - Envious',           # Overlaps with Jealousy
    'Energy - Frantic',         # Not natural vocabulary
    'Energy - Scattered',       # Not natural vocabulary
    'Energy - Victorious',      # Goes under Pump Up
    'Happy - Thankful',         # Identical to Grateful
]

def main():
    print("="*60)
    print("REMOVING EMPTY/USELESS SUB-VIBES")
    print("="*60)
    
    # Paths
    tapestry_path = Path('core/tapestry.json')
    manifold_path = Path('data/emotional_manifold_COMPLETE.json')
    
    # Load tapestry
    print(f"\nLoading tapestry...")
    with open(tapestry_path, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    before_count = len(tapestry['vibes'])
    print(f"Sub-vibes before: {before_count}")
    
    # Remove from tapestry
    removed = []
    for vibe in REMOVE_VIBES:
        if vibe in tapestry['vibes']:
            song_count = len(tapestry['vibes'][vibe].get('songs', []))
            del tapestry['vibes'][vibe]
            removed.append((vibe, song_count))
            print(f"  ✓ Removed: {vibe} ({song_count} songs)")
        else:
            print(f"  - Not found: {vibe}")
    
    after_count = len(tapestry['vibes'])
    print(f"\nSub-vibes after: {after_count}")
    
    # Save tapestry
    with open(tapestry_path, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    print(f"✅ Tapestry saved")
    
    # Load and update manifold
    print(f"\nUpdating manifold...")
    with open(manifold_path, 'r', encoding='utf-8') as f:
        manifold = json.load(f)
    
    # Remove from manifold sub_vibes list
    if 'sub_vibes' in manifold:
        manifold['sub_vibes'] = [v for v in manifold['sub_vibes'] if v.get('name') not in REMOVE_VIBES]
    
    # Update metadata
    if 'metadata' in manifold:
        manifold['metadata']['total_sub_vibes'] = after_count
        manifold['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Save manifold
    with open(manifold_path, 'w', encoding='utf-8') as f:
        json.dump(manifold, f, indent=2, ensure_ascii=False)
    print(f"✅ Manifold saved")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Removed {len(removed)} sub-vibes:")
    for vibe, count in removed:
        print(f"  - {vibe} ({count} songs)")
    print(f"\nSub-vibes: {before_count} → {after_count}")
    print("="*60)

if __name__ == '__main__':
    main()
