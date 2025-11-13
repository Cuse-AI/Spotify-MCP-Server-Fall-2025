"""
Ananki Tapestry Updater
Merges analyzed data into tapestry_map.json
Handles Reddit, YouTube, and Spotify data
"""

import json
import pandas as pd
from collections import defaultdict
import sys

print("="*70)
print("ANANKI TAPESTRY UPDATER")
print("="*70)

# Get input file from command line
if len(sys.argv) < 2:
    print("\n[ERROR] Please provide analyzed CSV file")
    print("Usage: python ananki_tapestry_updater.py <analyzed_file.csv>")
    exit(1)

input_file = sys.argv[1]

# Load analyzed data
print(f"\n[LOADING] Analyzed data from {input_file}...")
df = pd.read_csv(input_file)
print(f"  {len(df)} records to merge")

# Load tapestry
print("\n[LOADING] Current tapestry...")
with open('ananki_outputs/tapestry_map.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

print(f"  Current: {tapestry['stats']['total_songs']} songs, {tapestry['stats']['total_artists']} artists")

# Merge new songs into vibes
print("\n[MERGING] Adding new songs to tapestry vibes...")

added_count = 0
for idx, row in df.iterrows():
    vibe = row['vibe_category']
    
    if pd.isna(vibe) or vibe not in tapestry['vibes']:
        continue
    
    song = row['song_name']
    artist = row['artist_name']
    
    if pd.isna(song) or pd.isna(artist):
        continue
    
    # Check if already exists
    existing_songs = [(s['song'].lower(), s['artist'].lower()) 
                      for s in tapestry['vibes'][vibe]['songs']]
    
    song_key = (str(song).lower(), str(artist).lower())
    
    if song_key not in existing_songs:
        # Add new song
        tapestry['vibes'][vibe]['songs'].append({
            'song': song,
            'artist': artist,
            'comment_score': int(row['comment_score']) if pd.notna(row['comment_score']) else 0,
            'source_url': row['source_url'] if pd.notna(row['source_url']) else ''
        })
        added_count += 1

print(f"  Added {added_count} new songs")

# Update artist lists and counts
print("\n[UPDATING] Artist lists and stats...")
for vibe in tapestry['vibes']:
    # Get unique artists
    artists = list(set([s['artist'] for s in tapestry['vibes'][vibe]['songs']]))
    tapestry['vibes'][vibe]['artists'] = sorted(artists)
    
    # Update counts
    tapestry['vibes'][vibe]['song_count'] = len(tapestry['vibes'][vibe]['songs'])
    tapestry['vibes'][vibe]['artist_count'] = len(artists)

# Update global stats
tapestry['stats']['total_songs'] = sum(v['song_count'] for v in tapestry['vibes'].values())
tapestry['stats']['total_artists'] = len(set(
    artist 
    for vibe_data in tapestry['vibes'].values() 
    for artist in vibe_data['artists']
))

print(f"  New totals: {tapestry['stats']['total_songs']} songs, {tapestry['stats']['total_artists']} artists")

# Save updated tapestry
print("\n[SAVING] Updated tapestry...")
with open('ananki_outputs/tapestry_map.json', 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print(f"  Saved to: ananki_outputs/tapestry_map.json")

# Show vibe improvements
print("\n" + "="*70)
print("TAPESTRY IMPROVEMENTS:")
print("="*70)

vibe_improvements = []
for idx, row in df.iterrows():
    vibe = row['vibe_category']
    if pd.notna(vibe) and vibe in tapestry['vibes']:
        vibe_improvements.append(vibe)

from collections import Counter
improvements = Counter(vibe_improvements)

print("\nSongs added per vibe:")
for vibe, count in improvements.most_common():
    total = tapestry['vibes'][vibe]['song_count']
    print(f"  {vibe}: +{count} (now {total} total)")

print("\n[COMPLETE] Tapestry updated successfully!")
