"""
ANANKI TAPESTRY INTEGRATION - Batch 13 Part 2
Map validated songs into tapestry_complete.json
"""
import json
import pandas as pd
from collections import defaultdict

# Load the tapestry
print("Loading tapestry...")
with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

print(f"Current tapestry: {len(tapestry['vibes'])} vibes, {tapestry['stats']['total_songs']} songs")

# Load the analyzed batch
df = pd.read_csv('analyzed_batches/batch13_part2_analyzed_by_ananki.csv')
print(f"\nBatch 13 Part 2: {len(df)} songs across {df['vibe_sub_category'].nunique()} vibes")

# ANANKI INTEGRATION PROCESS
# Using human understanding to map sub-vibes and maintain emotional connections

# Group by sub-vibe
for vibe_name in sorted(df['vibe_sub_category'].unique()):
    print(f"\nProcessing: {vibe_name}")
    vibe_df = df[df['vibe_sub_category'] == vibe_name]

    # Check if vibe already exists
    if vibe_name in tapestry['vibes']:
        print(f"  Vibe exists - adding {len(vibe_df)} new songs")
        existing_songs = {(s['song'], s['artist']) for s in tapestry['vibes'][vibe_name]['songs']}
        new_count = 0

        for _, row in vibe_df.iterrows():
            song_tuple = (str(row['song_name']), str(row['artist_name']))
            if song_tuple not in existing_songs:
                song_obj = {
                    'song': str(row['song_name']),
                    'artist': str(row['artist_name']),
                    'comment_score': int(row['comment_score']) if pd.notna(row['comment_score']) else 0,
                    'source_url': str(row['source_url']),
                    'data_source': str(row['data_source'])
                }
                tapestry['vibes'][vibe_name]['songs'].append(song_obj)
                existing_songs.add(song_tuple)
                new_count += 1

        print(f"  Added {new_count} unique songs (skipped {len(vibe_df) - new_count} duplicates)")

    else:
        # Create new vibe entry
        print(f"  NEW VIBE - creating entry with {len(vibe_df)} songs")

        # Determine parent vibe
        parent = vibe_name.split(' - ')[0]  # e.g., "Hopeful - Healing" -> "Hopeful"

        # Build songs list (deduplicate)
        seen = set()
        songs = []
        for _, row in vibe_df.iterrows():
            song_tuple = (str(row['song_name']), str(row['artist_name']))
            if song_tuple not in seen:
                songs.append({
                    'song': str(row['song_name']),
                    'artist': str(row['artist_name']),
                    'comment_score': int(row['comment_score']) if pd.notna(row['comment_score']) else 0,
                    'source_url': str(row['source_url']),
                    'data_source': str(row['data_source'])
                })
                seen.add(song_tuple)

        # Get unique artists
        artists = sorted(list(set(str(row['artist_name']) for _, row in vibe_df.iterrows())))

        # Create vibe entry
        tapestry['vibes'][vibe_name] = {
            'songs': songs,
            'artists': artists,
            'parent_vibe': parent,
            'node_type': 'sub',
            'song_count': len(songs),
            'artist_count': len(artists),
            'nearby_vibes': []  # Will be populated by relationship mapping script
        }

        print(f"  Created new vibe: {len(songs)} songs, {len(artists)} artists")

# Update counts in existing vibes
for vibe_name in tapestry['vibes']:
    tapestry['vibes'][vibe_name]['song_count'] = len(tapestry['vibes'][vibe_name]['songs'])
    tapestry['vibes'][vibe_name]['artist_count'] = len(tapestry['vibes'][vibe_name]['artists'])

# Recalculate global stats
total_songs = sum(v['song_count'] for v in tapestry['vibes'].values())
total_artists = len(set(artist for v in tapestry['vibes'].values() for artist in v['artists']))

tapestry['stats'] = {
    'total_vibes': len(tapestry['vibes']),
    'total_songs': total_songs,
    'total_artists': total_artists,
    'data_sources': ['reddit'],
    'last_updated': '2025-11-08'
}

# Save updated tapestry
print("\n" + "="*80)
print("Saving updated tapestry...")
with open('ananki_outputs/tapestry_complete.json', 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print(f"\nUPDATED TAPESTRY:")
print(f"  Total vibes: {tapestry['stats']['total_vibes']}")
print(f"  Total songs: {tapestry['stats']['total_songs']}")
print(f"  Total artists: {tapestry['stats']['total_artists']}")
print("="*80)
print("ANANKI INTEGRATION COMPLETE - BATCH 13 PART 2 MAPPED")
print("="*80)
