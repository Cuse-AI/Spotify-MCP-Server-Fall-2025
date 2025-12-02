"""
Consolidate 23 meta-vibes to 9 core metas
"""
import json
from datetime import datetime

# Define consolidation mapping
CONSOLIDATION_MAP = {
    'Anxious': 'Dark',
    'Nostalgic': 'Sad',
    'Introspective': 'Night',
    'Angry': 'Energy',
    'Bitter': 'Dark',
    'Excited': 'Energy',
    'Hopeful': 'Happy',
    'Jealous': 'Dark',
    'Peaceful': 'Chill',
    'Playful': 'Happy',
    'Chaotic': 'Energy',
    'Bored': 'Chill',
    'Grateful': 'Happy',
    'Confident': 'Energy'
}

CORE_METAS = ['Sad', 'Happy', 'Chill', 'Energy', 'Dark', 'Romantic', 'Night', 'Drive', 'Party']

print("="*70)
print("CONSOLIDATING 23 META-VIBES TO 9 CORE METAS")
print("="*70)

# Load original manifold
print("\n[1/5] Loading original manifold...")
with open('data/ananki_outputs/emotional_manifold_COMPLETE.json', 'r', encoding='utf-8') as f:
    old_manifold = json.load(f)

print(f"  Original: {old_manifold['metadata']['total_sub_vibes']} sub-vibes, {old_manifold['metadata']['total_central_vibes']} metas")

# Build new manifold
print("\n[2/5] Building new consolidated manifold...")
new_manifold = {
    'metadata': {
        'total_sub_vibes': 0,
        'total_central_vibes': 9,
        'analysis_complete': True,
        'restructure_date': '2025-11-12',
        'restructure_note': 'Consolidated 23 meta-vibes to 9 core metas',
        'coordinate_system': old_manifold['metadata']['coordinate_system']
    },
    'central_vibes': {
        'positions': {meta: old_manifold['central_vibes']['positions'][meta] for meta in CORE_METAS},
        'total': 9
    },
    'sub_vibes': {}
}

subvibe_remap = {}

for old_subvibe_name, subvibe_data in old_manifold['sub_vibes'].items():
    if ' - ' not in old_subvibe_name:
        continue

    old_meta, descriptor = old_subvibe_name.split(' - ', 1)

    if old_meta in CORE_METAS:
        new_meta = old_meta
        new_subvibe_name = old_subvibe_name
    elif old_meta in CONSOLIDATION_MAP:
        new_meta = CONSOLIDATION_MAP[old_meta]
        if old_meta in ['Anxious', 'Nostalgic', 'Introspective']:
            new_subvibe_name = f"{new_meta} - {old_meta} {descriptor}"
        else:
            new_subvibe_name = f"{new_meta} - {descriptor}"
    else:
        continue

    subvibe_remap[old_subvibe_name] = new_subvibe_name
    new_manifold['sub_vibes'][new_subvibe_name] = subvibe_data

new_manifold['metadata']['total_sub_vibes'] = len(new_manifold['sub_vibes'])
print(f"  New: {len(new_manifold['sub_vibes'])} sub-vibes, 9 metas")

# Save new manifold
with open('data/ananki_outputs/emotional_manifold_COMPLETE.json', 'w', encoding='utf-8') as f:
    json.dump(new_manifold, f, indent=2, ensure_ascii=False)
print("  Saved new manifold")

# Load current tapestry
print("\n[3/5] Loading current tapestry...")
with open('data/ananki_outputs/tapestry_VALIDATED_ONLY.json', 'r', encoding='utf-8') as f:
    old_tapestry = json.load(f)

total_old_songs = sum(len(data.get('songs', [])) for data in old_tapestry['vibes'].values())
print(f"  Current: {total_old_songs} songs")

# Create fresh tapestry
print("\n[4/5] Creating new tapestry...")
new_tapestry = {'vibes': {}}
for new_subvibe_name in new_manifold['sub_vibes'].keys():
    new_tapestry['vibes'][new_subvibe_name] = {'songs': []}

# Migrate songs
songs_migrated = 0
for old_subvibe, data in old_tapestry['vibes'].items():
    songs = data.get('songs', [])
    if not songs:
        continue

    if old_subvibe in subvibe_remap:
        new_subvibe = subvibe_remap[old_subvibe]
    else:
        new_subvibe = old_subvibe

    if new_subvibe in new_tapestry['vibes']:
        new_tapestry['vibes'][new_subvibe]['songs'] = songs
        songs_migrated += len(songs)

print(f"  Migrated: {songs_migrated} songs")

# Save
with open('data/ananki_outputs/tapestry_VALIDATED_ONLY.json', 'w', encoding='utf-8') as f:
    json.dump(new_tapestry, f, indent=2, ensure_ascii=False)
print("  Saved new tapestry")

# Show distribution
print("\n[5/5] New distribution...")
meta_counts = {}
for subvibe_name, data in new_tapestry['vibes'].items():
    if ' - ' in subvibe_name:
        meta = subvibe_name.split(' - ')[0]
        if meta not in meta_counts:
            meta_counts[meta] = 0
        meta_counts[meta] += len(data.get('songs', []))

for meta in sorted(CORE_METAS):
    count = meta_counts.get(meta, 0)
    pct = (count / songs_migrated * 100) if songs_migrated > 0 else 0
    print(f"  {meta:12} {count:5,} songs ({pct:5.1f}%)")

print("\n" + "="*70)
print("COMPLETE!")
print("="*70)
