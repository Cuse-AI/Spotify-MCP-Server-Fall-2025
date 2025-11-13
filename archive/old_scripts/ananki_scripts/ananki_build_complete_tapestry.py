"""
Ananki Master Tapestry Builder
================================
Merges all data sources (Reddit + YouTube + Spotify)
Enriches all songs with Spotify IDs
Rebuilds tapestry with granular sub-vibes
"""

import pandas as pd
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import time

load_dotenv('spotify/.env')

print("="*70)
print("ANANKI MASTER TAPESTRY BUILDER")
print("="*70)

# ============================================================================
# STEP 1: Load all analyzed data
# ============================================================================

print("\n[STEP 1] Loading all analyzed data sources...")

reddit_df = pd.read_csv('reddit_analyzed_by_ananki_20251107.csv')
youtube_df = pd.read_csv('youtube_analyzed_by_ananki_20251107.csv')
spotify_df = pd.read_csv('spotify_analyzed_by_ananki_20251107.csv')

print(f"  Reddit: {len(reddit_df)} songs")
print(f"  YouTube: {len(youtube_df)} songs")
print(f"  Spotify: {len(spotify_df)} songs")

# Combine all
all_df = pd.concat([reddit_df, youtube_df, spotify_df], ignore_index=True)
print(f"  Combined: {len(all_df)} total songs")

# ============================================================================
# STEP 2: Enrich ALL songs with Spotify IDs
# ============================================================================

print("\n[STEP 2] Enriching with Spotify IDs...")

# Initialize Spotify client
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Add spotify_id column if not exists
if 'spotify_id' not in all_df.columns:
    all_df['spotify_id'] = None

# Function to search for Spotify ID
def get_spotify_id(song, artist):
    """Search Spotify for song and return ID"""
    try:
        query = f"track:{song} artist:{artist}"
        results = sp.search(q=query, type='track', limit=1)
        
        if results['tracks']['items']:
            return results['tracks']['items'][0]['id']
        return None
    except Exception as e:
        return None

# Enrich songs that don't have Spotify ID
print("  Searching for Spotify IDs...")
enriched_count = 0
failed_count = 0

for idx, row in all_df.iterrows():
    # Skip if already has ID
    if pd.notna(row['spotify_id']) and row['spotify_id'] != '':
        continue
    
    song = row['song_name']
    artist = row['artist_name']
    
    if pd.notna(song) and pd.notna(artist):
        spotify_id = get_spotify_id(song, artist)
        
        if spotify_id:
            all_df.at[idx, 'spotify_id'] = spotify_id
            enriched_count += 1
        else:
            failed_count += 1
    
    # Progress and rate limiting
    if (idx + 1) % 100 == 0:
        print(f"    Processed {idx + 1} / {len(all_df)}...")
        time.sleep(1)  # Rate limiting
    elif (idx + 1) % 10 == 0:
        time.sleep(0.2)

print(f"  Enriched {enriched_count} songs with Spotify IDs")
print(f"  Failed to find: {failed_count} songs")

has_spotify_id = all_df['spotify_id'].notna() & (all_df['spotify_id'] != '')
print(f"  Total with Spotify ID: {has_spotify_id.sum()} / {len(all_df)} ({has_spotify_id.sum()/len(all_df)*100:.1f}%)")

# ============================================================================
# STEP 3: Detect sub-vibes from context
# ============================================================================

print("\n[STEP 3] Detecting sub-vibes from context...")

# (Using same sub-vibe detection as before)
SUB_VIBE_PATTERNS = {
    'Emotional/Sad': {
        'Heartbreak/Breakup': ['heartbreak', 'breakup', 'broke up', 'ex girlfriend', 'ex boyfriend'],
        'Crying/Cathartic': ['cry', 'crying', 'tears', 'sob'],
        'Melancholic/Bittersweet': ['melanchol', 'bittersweet', 'wistful'],
        'Lonely/Isolated': ['lonely', 'alone', 'isolated', 'solitude'],
    },
    'Night/Sleep': {
        'Midnight Drive': ['midnight', 'late night drive', 'night drive', 'driving at night'],
        'Sleep/Bedtime': ['sleep', 'bedtime', 'sleeping'],
        '3AM Thoughts': ['3am', '3 am', 'late night thoughts'],
    },
    'Chill/Relaxing': {
        'Ambient/Background': ['ambient', 'background', 'study', 'work'],
        'Beach/Summer': ['beach', 'summer', 'tropical'],
    },
    'Energetic/Motivational': {
        'Workout/Gym': ['workout', 'gym', 'exercise'],
        'Pump-Up/Hype': ['pump up', 'hype', 'beast mode'],
    },
    'Focus/Study': {
        'Deep Work': ['deep work', 'concentration', 'intense focus'],
        'Productive/Work': ['productive', 'work music', 'office'],
    },
    'Party/Dance': {
        'Club/Nightclub': ['club', 'nightclub', 'clubbing'],
        'Pregame': ['pregame', 'getting ready', 'pre party'],
    },
}

def detect_sub_vibe(text, main_vibe):
    if main_vibe not in SUB_VIBE_PATTERNS:
        return None
    text_lower = text.lower()
    for sub_vibe, keywords in SUB_VIBE_PATTERNS[main_vibe].items():
        if any(kw in text_lower for kw in keywords):
            return f"{main_vibe}/{sub_vibe}"
    return None

all_df['sub_vibe'] = None
for idx, row in all_df.iterrows():
    if pd.notna(row['vibe_category']):
        text = str(row['vibe_description']) + ' ' + str(row['recommendation_reasoning'])
        sub_vibe = detect_sub_vibe(text, row['vibe_category'])
        if sub_vibe:
            all_df.at[idx, 'sub_vibe'] = sub_vibe
    
    if (idx + 1) % 500 == 0:
        print(f"    Processed {idx + 1} / {len(all_df)}...")

sub_vibes_found = all_df['sub_vibe'].notna().sum()
print(f"  Detected sub-vibes for {sub_vibes_found} songs")

# ============================================================================
# STEP 4: Build complete tapestry with sub-vibes
# ============================================================================

print("\n[STEP 4] Building complete tapestry...")

tapestry = {
    'vibes': {},
    'stats': {}
}

# Get all unique vibes (parent + sub)
all_vibes = set()
for idx, row in all_df.iterrows():
    if pd.notna(row['sub_vibe']):
        all_vibes.add(row['sub_vibe'])
    elif pd.notna(row['vibe_category']):
        all_vibes.add(row['vibe_category'])

print(f"  Total unique vibes: {len(all_vibes)}")

# Build each vibe node
for vibe in all_vibes:
    # Get songs for this vibe
    if '/' in vibe and vibe.count('/') > 1:
        # Sub-vibe
        vibe_songs = all_df[all_df['sub_vibe'] == vibe]
        node_type = 'sub_vibe'
        parent_vibe = vibe.split('/')[0] + '/' + vibe.split('/')[1]
    else:
        # Parent vibe (includes songs without sub-vibe AND those with sub-vibes)
        vibe_songs = all_df[all_df['vibe_category'] == vibe]
        node_type = 'parent_vibe'
        parent_vibe = None
    
    songs_list = []
    artists_set = set()
    
    for idx, row in vibe_songs.iterrows():
        if pd.notna(row['song_name']) and pd.notna(row['artist_name']):
            song_entry = {
                'song': row['song_name'],
                'artist': row['artist_name'],
                'comment_score': int(row.get('comment_score', 0)),
                'source_url': row.get('source_url', ''),
                'data_source': row.get('data_source', ''),
            }
            
            # Add Spotify ID if available
            if pd.notna(row.get('spotify_id')) and row['spotify_id'] != '':
                song_entry['spotify_id'] = row['spotify_id']
                song_entry['spotify_url'] = f"https://open.spotify.com/track/{row['spotify_id']}"
            
            songs_list.append(song_entry)
            artists_set.add(row['artist_name'])
    
    tapestry['vibes'][vibe] = {
        'songs': songs_list,
        'artists': sorted(list(artists_set)),
        'song_count': len(songs_list),
        'artist_count': len(artists_set),
        'node_type': node_type,
        'parent_vibe': parent_vibe,
        'nearby_vibes': []
    }

print(f"  Built {len(tapestry['vibes'])} vibe nodes")

# Calculate stats
total_songs = sum(v['song_count'] for v in tapestry['vibes'].values())
all_artists = set()
for v in tapestry['vibes'].values():
    all_artists.update(v['artists'])

songs_with_spotify = sum(
    1 for v in tapestry['vibes'].values()
    for s in v['songs']
    if 'spotify_id' in s
)

tapestry['stats'] = {
    'total_vibes': len(tapestry['vibes']),
    'total_songs': total_songs,
    'total_artists': len(all_artists),
    'songs_with_spotify_id': songs_with_spotify,
    'spotify_coverage': f"{songs_with_spotify/total_songs*100:.1f}%",
    'data_sources': ['reddit', 'youtube', 'spotify'],
    'generated': datetime.now().isoformat()
}

# Save
output_file = 'ananki_outputs/tapestry_complete.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Saved to: {output_file}")

print("\n" + "="*70)
print("COMPLETE TAPESTRY BUILT!")
print("="*70)

print(f"\nTotal vibes: {len(tapestry['vibes'])}")
print(f"Total songs: {total_songs}")
print(f"Total artists: {len(all_artists)}")
print(f"With Spotify IDs: {songs_with_spotify} ({songs_with_spotify/total_songs*100:.1f}%)")
print(f"\nData sources: Reddit + YouTube + Spotify ✓")

print(f"\n[COMPLETE] Three-lens tapestry ready!")
print(f"[NEXT] Organize files and prepare for Phase 2 (sonic analysis)")
