"""
Ananki Tapestry Builder - CORRECT VERSION
==========================================

Builds the actual tapestry map:
- Nodes = Vibes/moods that exist in our scraped data
- Edges = Human analysis of how vibes relate to each other
- Each node has lists of songs and artists explicitly recommended by humans

NO psychological coordinates (that comes from Spotify audio_features later)
NO AI inference yet - just explicit human-sourced connections
"""

import pandas as pd
import json
from collections import defaultdict

print("="*70)
print("ANANKI TAPESTRY BUILDER")
print("="*70)

# Load data
df = pd.read_csv('ananki_outputs/ananki_v3_with_anchors.csv')
print(f"\n[OK] Loaded {len(df)} records")

# ============================================================================
# STEP 1: Extract all vibes that actually exist in the data
# ============================================================================

print(f"\n[ANALYZING] Finding all vibes in the data...")

# Get vibes with actual content (not just "Other" or empty)
vibe_counts = df['vibe_category'].value_counts()
print(f"\nFound {len(vibe_counts)} vibes in data:")
for vibe, count in vibe_counts.items():
    if pd.notna(vibe) and vibe != '':
        print(f"  {vibe}: {count} recommendations")

# Filter to meaningful vibes (exclude "Other" for now, we'll recategorize it later)
meaningful_vibes = [v for v in vibe_counts.index if pd.notna(v) and v != 'Other' and v != '']
print(f"\n{len(meaningful_vibes)} meaningful vibes to map")

# ============================================================================
# STEP 2: Human analysis - How are vibes related?
# ============================================================================

print(f"\n[ANANKI ANALYSIS] Determining vibe relationships...")

# Ananki's human-in-the-loop analysis of which vibes are "nearby" on the tapestry
# Format: {vibe: [nearby_vibes_in_order_of_closeness]}
VIBE_RELATIONSHIPS = {
    'Emotional/Sad': [
        'Introspective/Thoughtful',  # Both inward-focused, emotional
        'Nostalgic',                 # Sadness often tied to memory
        'Night/Sleep',               # Sad music for late nights
        'Rainy/Cozy',               # Melancholic comfort
        'Ethereal/Dreamy',          # Sad but beautiful
        'Dark/Atmospheric',          # Darker sadness
        'Romantic/Sensual',         # Lost love, heartbreak
    ],
    
    'Angry/Intense': [
        'Rebellious/Punk',          # Anger channeled into rebellion
        'Energetic/Motivational',    # Intense energy, different valence
        'Dark/Atmospheric',          # Dark intensity
        'Driving/Travel',           # Aggressive driving music
        'Party/Dance',              # High energy, different emotion
    ],
    
    'Happy/Upbeat': [
        'Party/Dance',              # Both high energy, positive
        'Energetic/Motivational',    # Positive energy
        'Driving/Travel',           # Feel-good road trip
        'Romantic/Sensual',         # Happy love songs
        'Discovery/Exploration',     # Excited about new things
    ],
    
    'Chill/Relaxing': [
        'Rainy/Cozy',               # Both comfort zones
        'Night/Sleep',              # Relaxing for sleep
        'Ethereal/Dreamy',          # Calm and dreamy
        'Focus/Study',              # Calm concentration
        'Introspective/Thoughtful',  # Calm reflection
    ],
    
    'Dark/Atmospheric': [
        'Emotional/Sad',            # Dark sadness
        'Night/Sleep',              # Dark nighttime
        'Ethereal/Dreamy',          # Dark but beautiful
        'Introspective/Thoughtful',  # Dark thoughts
        'Epic/Cinematic',           # Dark drama
        'Psychedelic/Trippy',       # Dark and surreal
    ],
    
    'Introspective/Thoughtful': [
        'Emotional/Sad',            # Thoughtful sadness
        'Chill/Relaxing',           # Calm thinking
        'Night/Sleep',              # Late-night thoughts
        'Discovery/Exploration',     # Intellectual curiosity
        'Focus/Study',              # Deep concentration
        'Nostalgic',                # Reflecting on past
    ],
    
    'Romantic/Sensual': [
        'Happy/Upbeat',             # Happy love
        'Emotional/Sad',            # Heartbreak
        'Night/Sleep',              # Intimate nighttime
        'Chill/Relaxing',           # Sensual and calm
        'Nostalgic',                # Past romances
    ],
    
    'Night/Sleep': [
        'Chill/Relaxing',           # Sleep music
        'Emotional/Sad',            # Late-night sadness
        'Introspective/Thoughtful',  # 3am thoughts
        'Dark/Atmospheric',          # Nighttime darkness
        'Ethereal/Dreamy',          # Sleep and dreams
        'Rainy/Cozy',               # Nighttime comfort
    ],
    
    'Driving/Travel': [
        'Happy/Upbeat',             # Road trip energy
        'Energetic/Motivational',    # Driving momentum
        'Chill/Relaxing',           # Highway cruise
        'Discovery/Exploration',     # Journey and adventure
        'Nostalgic',                # Road trip memories
    ],
    
    'Party/Dance': [
        'Happy/Upbeat',             # Party happiness
        'Energetic/Motivational',    # Hype energy
        'Angry/Intense',            # Aggressive party music
        'Romantic/Sensual',         # Dance floor romance
    ],
    
    'Nostalgic': [
        'Emotional/Sad',            # Bittersweet memories
        'Introspective/Thoughtful',  # Reflecting on past
        'Romantic/Sensual',         # Past relationships
        'Driving/Travel',           # Road trip memories
        'Rainy/Cozy',               # Cozy reminiscence
    ],
    
    'Focus/Study': [
        'Chill/Relaxing',           # Calm focus
        'Introspective/Thoughtful',  # Deep work
        'Ethereal/Dreamy',          # Ambient focus
        'Night/Sleep',              # Late-night study
    ],
    
    'Discovery/Exploration': [
        'Introspective/Thoughtful',  # Intellectual curiosity
        'Happy/Upbeat',             # Excited discovery
        'Psychedelic/Trippy',       # Mind-expanding
        'Epic/Cinematic',           # Grand exploration
        'Driving/Travel',           # Physical exploration
    ],
    
    'Rainy/Cozy': [
        'Chill/Relaxing',           # Cozy relaxation
        'Emotional/Sad',            # Rainy day sadness
        'Night/Sleep',              # Cozy sleep
        'Introspective/Thoughtful',  # Rainy contemplation
        'Nostalgic',                # Cozy memories
    ],
    
    'Epic/Cinematic': [
        'Dark/Atmospheric',          # Epic darkness
        'Discovery/Exploration',     # Epic journey
        'Energetic/Motivational',    # Epic motivation
        'Psychedelic/Trippy',       # Epic and surreal
    ],
    
    'Psychedelic/Trippy': [
        'Ethereal/Dreamy',          # Surreal and dreamy
        'Dark/Atmospheric',          # Dark psychedelia
        'Discovery/Exploration',     # Mind exploration
        'Epic/Cinematic',           # Psychedelic grandeur
        'Introspective/Thoughtful',  # Deep thoughts
    ],
    
    'Rebellious/Punk': [
        'Angry/Intense',            # Rebellion anger
        'Energetic/Motivational',    # Rebel energy
        'Discovery/Exploration',     # Alternative culture
        'Party/Dance',              # Punk shows
    ],
    
    'Ethereal/Dreamy': [
        'Chill/Relaxing',           # Dreamy calm
        'Night/Sleep',              # Dream state
        'Dark/Atmospheric',          # Dark dreams
        'Psychedelic/Trippy',       # Surreal dreams
        'Emotional/Sad',            # Melancholic beauty
        'Focus/Study',              # Ambient focus
    ],
    
    'Energetic/Motivational': [
        'Happy/Upbeat',             # Positive energy
        'Angry/Intense',            # Aggressive motivation
        'Party/Dance',              # High energy
        'Driving/Travel',           # Driving energy
        'Rebellious/Punk',          # Rebel motivation
    ],
    
    'Innovative/Unique': [
        'Discovery/Exploration',     # Discovering unique sounds
        'Psychedelic/Trippy',       # Weird and unique
        'Epic/Cinematic',           # Unique and grand
        'Experimental',             # (if we had this)
    ],
}

# ============================================================================
# STEP 3: Build graph structure of the tapestry (simple adjacency list)
# ============================================================================

print(f"\n[BUILDING] Tapestry graph structure...")

# Build adjacency list (no external library needed)
tapestry_graph = {}
edge_count = 0

for vibe in meaningful_vibes:
    tapestry_graph[vibe] = []

for vibe, nearby_vibes in VIBE_RELATIONSHIPS.items():
    if vibe not in meaningful_vibes:
        continue
    for nearby in nearby_vibes:
        if nearby in meaningful_vibes:
            # Distance = position in list (1-indexed)
            distance = nearby_vibes.index(nearby) + 1
            weight = 1.0 / distance
            tapestry_graph[vibe].append({
                'vibe': nearby,
                'distance': distance,
                'weight': weight
            })
            edge_count += 1

print(f"  Added {len(tapestry_graph)} vibe nodes")
print(f"  Added {edge_count} relationship edges")

# ============================================================================
# STEP 4: Attach songs and artists to each vibe
# ============================================================================

print(f"\n[ATTACHING] Songs and artists to each vibe...")

vibe_songs = defaultdict(list)
vibe_artists = defaultdict(set)

for idx, row in df.iterrows():
    vibe = row.get('vibe_category')
    song = row.get('song_name', '')
    artist = row.get('artist_name', '')
    
    # Skip invalid
    if pd.isna(vibe) or vibe == '' or vibe == 'Other':
        continue
    if not song or not artist or pd.isna(song) or pd.isna(artist):
        continue
    
    vibe_songs[vibe].append({
        'song': song,
        'artist': artist,
        'comment_score': row.get('comment_score', 0),
        'source_url': row.get('source_url', '')
    })
    vibe_artists[vibe].add(artist)

print(f"  Attached songs to {len(vibe_songs)} vibes")

# ============================================================================
# STEP 5: Save tapestry structure
# ============================================================================

print(f"\n[SAVING] Tapestry structure...")

tapestry = {
    'vibes': {},
    'relationships': VIBE_RELATIONSHIPS,
    'stats': {
        'total_vibes': len(meaningful_vibes),
        'total_edges': edge_count,
        'total_songs': sum(len(songs) for songs in vibe_songs.values()),
        'total_artists': sum(len(artists) for artists in vibe_artists.values())
    }
}

# Build each vibe node
for vibe in meaningful_vibes:
    songs_list = vibe_songs.get(vibe, [])
    
    # Sort songs by comment score
    songs_sorted = sorted(songs_list, key=lambda x: x['comment_score'], reverse=True)
    
    tapestry['vibes'][vibe] = {
        'songs': songs_sorted,
        'artists': sorted(list(vibe_artists.get(vibe, []))),
        'song_count': len(songs_list),
        'artist_count': len(vibe_artists.get(vibe, [])),
        'nearby_vibes': VIBE_RELATIONSHIPS.get(vibe, [])
    }

# Save
output_file = 'ananki_outputs/tapestry_map.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print(f"[OK] Saved to: {output_file}")

# ============================================================================
# STEP 6: Print tapestry visualization
# ============================================================================

print(f"\n" + "="*70)
print("TAPESTRY MAP:")
print("="*70)

print(f"\nTotal vibes: {len(meaningful_vibes)}")
print(f"Total songs: {tapestry['stats']['total_songs']}")
print(f"Total artists: {tapestry['stats']['total_artists']}")

print(f"\nVibe coverage:")
for vibe in sorted(meaningful_vibes):
    info = tapestry['vibes'][vibe]
    nearby = len(info['nearby_vibes'])
    print(f"  {vibe}:")
    print(f"    Songs: {info['song_count']}, Artists: {info['artist_count']}")
    print(f"    Connected to {nearby} nearby vibes")

print(f"\n[COMPLETE] Tapestry map ready!")
print(f"\nTo query: Find vibe on map -> return attached songs/artists")
print(f"For unknown vibes: Traverse nearby vibes to find related music")
