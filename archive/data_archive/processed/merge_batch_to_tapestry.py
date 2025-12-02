"""
Ananki Tapestry Merger - Batch Integration
Merges batch data into the complete tapestry with sub-vibes
"""

import pandas as pd
import json
from collections import defaultdict

print("="*70)
print("ANANKI TAPESTRY MERGER - BATCH 1")
print("="*70)

# Load analyzed batch data
import sys
if len(sys.argv) < 2:
    print("Usage: python merge_batch_to_tapestry.py <batch_file.csv>")
    exit(1)

batch_file = sys.argv[1]
print(f"\n[LOADING] {batch_file}...")
batch1 = pd.read_csv(batch_file)
print(f"  {len(batch1)} songs to merge")

# Load existing tapestry (if exists)
tapestry_file = '../ananki_outputs/tapestry_complete.json'
try:
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    print(f"\n[LOADING] Existing tapestry...")
    print(f"  Current: {tapestry['stats']['total_songs']} songs")
except FileNotFoundError:
    print(f"\n[CREATING] New tapestry (no existing file)...")
    tapestry = {
        'vibes': {},
        'stats': {}
    }

# Merge songs into vibe nodes
print(f"\n[MERGING] Adding songs to sub-vibe nodes...")

for idx, row in batch1.iterrows():
    sub_vibe = row['vibe_sub_category']  # e.g., "Sad - Heartbreak"
    parent_vibe = row['vibe_category']   # e.g., "Emotional/Sad"
    
    if pd.isna(sub_vibe) or pd.isna(row['song_name']) or pd.isna(row['artist_name']):
        continue
    
    # Create node if doesn't exist
    if sub_vibe not in tapestry['vibes']:
        tapestry['vibes'][sub_vibe] = {
            'songs': [],
            'artists': [],
            'song_count': 0,
            'artist_count': 0,
            'parent_vibe': parent_vibe,
            'node_type': 'sub_vibe',
            'nearby_vibes': []
        }
    
    # Check for duplicates
    existing = [(s['song'].lower(), s['artist'].lower()) 
                for s in tapestry['vibes'][sub_vibe]['songs']]
    
    song_key = (str(row['song_name']).lower(), str(row['artist_name']).lower())
    
    if song_key not in existing:
        tapestry['vibes'][sub_vibe]['songs'].append({
            'song': row['song_name'],
            'artist': row['artist_name'],
            'comment_score': int(row['comment_score']) if pd.notna(row['comment_score']) else 0,
            'source_url': row['source_url'] if pd.notna(row['source_url']) else '',
            'data_source': row['data_source']
        })
    
    if (idx + 1) % 1000 == 0:
        print(f"    Processed {idx + 1}/{len(batch1)}...")

# Update artist lists and counts
print(f"\n[UPDATING] Counts and stats...")
for vibe in tapestry['vibes']:
    artists = list(set([s['artist'] for s in tapestry['vibes'][vibe]['songs']]))
    tapestry['vibes'][vibe]['artists'] = sorted(artists)
    tapestry['vibes'][vibe]['song_count'] = len(tapestry['vibes'][vibe]['songs'])
    tapestry['vibes'][vibe]['artist_count'] = len(artists)

# Calculate global stats
total_songs = sum(v['song_count'] for v in tapestry['vibes'].values())
all_artists = set()
for v in tapestry['vibes'].values():
    all_artists.update(v['artists'])

tapestry['stats'] = {
    'total_vibes': len(tapestry['vibes']),
    'total_songs': total_songs,
    'total_artists': len(all_artists),
    'data_sources': ['reddit', 'youtube', 'spotify'],
}

# Save updated tapestry
print(f"\n[SAVING] Updated tapestry...")
with open(tapestry_file, 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print(f"  Saved to: {tapestry_file}")

print("\n" + "="*70)
print("TAPESTRY UPDATED!")
print("="*70)

print(f"\nNew Statistics:")
print(f"  Total vibes: {len(tapestry['vibes'])}")
print(f"  Total songs: {total_songs}")
print(f"  Total artists: {len(all_artists)}")

print(f"\nNew sub-vibes added:")
for vibe in sorted(tapestry['vibes'].keys()):
    if 'Sad' in vibe:
        print(f"  {vibe}: {tapestry['vibes'][vibe]['song_count']} songs, {tapestry['vibes'][vibe]['artist_count']} artists")

print(f"\n[COMPLETE] Batch 1 merged into tapestry!")
