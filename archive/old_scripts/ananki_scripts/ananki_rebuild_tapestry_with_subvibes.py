"""
Ananki Tapestry Rebuilder
Rebuilds tapestry with sub-vibes as PRIMARY nodes

The AI will traverse this granular map to build truly authentic playlists
backed by human data and specific emotional contexts.
"""

import pandas as pd
import json
from collections import defaultdict

print("="*70)
print("ANANKI TAPESTRY REBUILDER - SUB-VIBES AS PRIMARY")
print("="*70)

# Load all analyzed data
print("\n[LOADING] All analyzed data...")
reddit_df = pd.read_csv('reddit_analyzed_by_ananki_20251107.csv')
youtube_df = pd.read_csv('youtube_analyzed_by_ananki_20251107.csv')

all_df = pd.concat([reddit_df, youtube_df], ignore_index=True)
print(f"  Total: {len(all_df)} songs")

# Load sub-vibe detection results
print("\n[LOADING] Sub-vibe analysis...")
with open('ananki_outputs/sub_vibe_map.json', 'r', encoding='utf-8') as f:
    sub_vibe_data = json.load(f)

print(f"  {len(sub_vibe_data['sub_vibes'])} sub-vibes detected")

# ============================================================================
# STRATEGY: Build tapestry with BOTH parent vibes AND sub-vibes as nodes
# ============================================================================

print("\n[BUILDING] New tapestry structure...")

tapestry = {
    'vibes': {},
    'relationships': {},
    'stats': {}
}

# PART 1: Add sub-vibes as primary nodes
print("\n  Adding sub-vibe nodes...")
for sub_vibe, data in sub_vibe_data['sub_vibes'].items():
    tapestry['vibes'][sub_vibe] = {
        'songs': data['songs'],
        'artists': data['artists'],
        'song_count': data['song_count'],
        'artist_count': data['artist_count'],
        'parent_vibe': data['parent_vibe'],
        'nearby_vibes': data['nearby_vibes'],
        'node_type': 'sub_vibe'
    }
    print(f"    {sub_vibe}: {data['song_count']} songs")

# PART 2: Keep parent vibes as aggregate nodes
print("\n  Adding parent vibe nodes...")

parent_vibes = [
    'Emotional/Sad', 'Chill/Relaxing', 'Night/Sleep', 'Energetic/Motivational',
    'Focus/Study', 'Driving/Travel', 'Party/Dance', 'Dark/Atmospheric',
    'Introspective/Thoughtful', 'Romantic/Sensual', 'Happy/Upbeat',
    'Discovery/Exploration', 'Nostalgic', 'Rainy/Cozy', 'Epic/Cinematic',
    'Rebellious/Punk', 'Ethereal/Dreamy', 'Innovative/Unique', 'Psychedelic/Trippy'
]

for parent in parent_vibes:
    # Get all songs for this parent (including those NOT in sub-vibes)
    parent_songs_df = all_df[all_df['vibe_category'] == parent]
    
    songs_list = []
    artists_set = set()
    
    for idx, row in parent_songs_df.iterrows():
        if pd.notna(row['song_name']) and pd.notna(row['artist_name']):
            songs_list.append({
                'song': row['song_name'],
                'artist': row['artist_name'],
                'comment_score': row.get('comment_score', 0),
                'source_url': row.get('source_url', '')
            })
            artists_set.add(row['artist_name'])
    
    # Find child sub-vibes
    child_sub_vibes = [sv for sv in tapestry['vibes'] 
                       if tapestry['vibes'][sv].get('parent_vibe') == parent]
    
    tapestry['vibes'][parent] = {
        'songs': songs_list,
        'artists': sorted(list(artists_set)),
        'song_count': len(songs_list),
        'artist_count': len(artists_set),
        'child_sub_vibes': child_sub_vibes,
        'nearby_vibes': [],  # Will populate next
        'node_type': 'parent_vibe'
    }
    
    print(f"    {parent}: {len(songs_list)} songs ({len(child_sub_vibes)} sub-vibes)")

# PART 3: Define parent vibe relationships (same as before)
print("\n  Mapping parent vibe relationships...")

PARENT_RELATIONSHIPS = {
    'Emotional/Sad': ['Introspective/Thoughtful', 'Nostalgic', 'Night/Sleep', 'Rainy/Cozy', 'Ethereal/Dreamy'],
    'Angry/Intense': ['Rebellious/Punk', 'Energetic/Motivational', 'Dark/Atmospheric'],
    'Happy/Upbeat': ['Party/Dance', 'Energetic/Motivational', 'Driving/Travel', 'Romantic/Sensual'],
    'Chill/Relaxing': ['Rainy/Cozy', 'Night/Sleep', 'Ethereal/Dreamy', 'Focus/Study'],
    'Dark/Atmospheric': ['Emotional/Sad', 'Night/Sleep', 'Ethereal/Dreamy', 'Epic/Cinematic'],
    'Introspective/Thoughtful': ['Emotional/Sad', 'Chill/Relaxing', 'Night/Sleep', 'Nostalgic'],
    'Romantic/Sensual': ['Happy/Upbeat', 'Emotional/Sad', 'Night/Sleep', 'Chill/Relaxing'],
    'Night/Sleep': ['Chill/Relaxing', 'Emotional/Sad', 'Introspective/Thoughtful', 'Dark/Atmospheric'],
    'Driving/Travel': ['Happy/Upbeat', 'Energetic/Motivational', 'Chill/Relaxing', 'Nostalgic'],
    'Party/Dance': ['Happy/Upbeat', 'Energetic/Motivational', 'Romantic/Sensual'],
    'Nostalgic': ['Emotional/Sad', 'Introspective/Thoughtful', 'Romantic/Sensual', 'Rainy/Cozy'],
    'Focus/Study': ['Chill/Relaxing', 'Introspective/Thoughtful', 'Ethereal/Dreamy'],
    'Discovery/Exploration': ['Introspective/Thoughtful', 'Happy/Upbeat', 'Epic/Cinematic'],
    'Rainy/Cozy': ['Chill/Relaxing', 'Emotional/Sad', 'Night/Sleep', 'Nostalgic'],
    'Epic/Cinematic': ['Dark/Atmospheric', 'Discovery/Exploration', 'Energetic/Motivational'],
    'Rebellious/Punk': ['Angry/Intense', 'Energetic/Motivational', 'Party/Dance'],
    'Ethereal/Dreamy': ['Chill/Relaxing', 'Night/Sleep', 'Dark/Atmospheric'],
    'Energetic/Motivational': ['Happy/Upbeat', 'Party/Dance', 'Driving/Travel'],
    'Innovative/Unique': ['Discovery/Exploration', 'Epic/Cinematic'],
    'Psychedelic/Trippy': ['Ethereal/Dreamy', 'Discovery/Exploration', 'Introspective/Thoughtful'],
}

for parent, nearby in PARENT_RELATIONSHIPS.items():
    if parent in tapestry['vibes']:
        tapestry['vibes'][parent]['nearby_vibes'] = nearby

# Update relationships dict
tapestry['relationships'] = PARENT_RELATIONSHIPS

# Calculate stats
print("\n  Calculating statistics...")

total_nodes = len(tapestry['vibes'])
parent_nodes = sum(1 for v in tapestry['vibes'].values() if v['node_type'] == 'parent_vibe')
sub_nodes = sum(1 for v in tapestry['vibes'].values() if v['node_type'] == 'sub_vibe')
total_songs = sum(v['song_count'] for v in tapestry['vibes'].values())
all_artists = set()
for vibe_data in tapestry['vibes'].values():
    all_artists.update(vibe_data['artists'])

tapestry['stats'] = {
    'total_vibes': total_nodes,
    'parent_vibes': parent_nodes,
    'sub_vibes': sub_nodes,
    'total_songs': total_songs,
    'total_artists': len(all_artists),
    'songs_in_sub_vibes': sub_vibe_data['stats']['total_songs_in_sub_vibes'],
    'avg_songs_per_vibe': total_songs / total_nodes
}

# Save new tapestry
print("\n[SAVING] Rebuilt tapestry...")
with open('ananki_outputs/tapestry_map_with_subvibes.json', 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print(f"  Saved to: ananki_outputs/tapestry_map_with_subvibes.json")

print("\n" + "="*70)
print("TAPESTRY REBUILT!")
print("="*70)

print(f"\nStructure:")
print(f"  Parent vibes: {parent_nodes}")
print(f"  Sub-vibes: {sub_nodes}")
print(f"  Total nodes: {total_nodes}")
print(f"  Total songs: {total_songs}")
print(f"  Total artists: {len(all_artists)}")

print(f"\nExample navigation:")
print(f"  User: 'I'm sad about a breakup'")
print(f"  AI: Emotional/Sad → Heartbreak/Breakup (100 specific songs!)")
print(f"  ")
print(f"  User: 'I want midnight driving vibes'")
print(f"  AI: Night/Sleep → Midnight Drive (108 songs!)")

print(f"\n[COMPLETE] Tapestry is now GRANULAR and HUMAN-BACKED!")
