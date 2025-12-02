import json

# Load tapestry
with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Get all songs
all_songs = []
for vibe_name, vibe_data in tapestry['vibes'].items():
    for song in vibe_data.get('songs', []):
        song['_vibe'] = vibe_name
        all_songs.append(song)

print(f"Total songs: {len(all_songs)}")

# Check what keys songs have
print("\n=== SAMPLE SONG STRUCTURES ===")
for i in [0, 100, 500, 1000, 2000]:
    if i < len(all_songs):
        s = all_songs[i]
        print(f"\nSong {i}: {s.get('artist')} - {s.get('song')}")
        print(f"  Keys: {list(s.keys())}")

# Find songs WITH context
print("\n=== SONGS WITH CONTEXT ===")
context_songs = [s for s in all_songs if s.get('full_context') or s.get('ananki_analysis') or s.get('comment_text') or s.get('reddit_context')]
print(f"Found {len(context_songs)} songs with some kind of context")

if context_songs:
    for s in context_songs[:5]:
        print(f"\n{s.get('artist')} - {s.get('song')}")
        for key in ['full_context', 'ananki_analysis', 'comment_text', 'reddit_context', 'ananki_reasoning']:
            if s.get(key):
                print(f"  {key}: {str(s.get(key))[:150]}...")

# Check all unique keys across all songs
all_keys = set()
for s in all_songs:
    all_keys.update(s.keys())
print(f"\n=== ALL UNIQUE KEYS FOUND ===")
print(sorted(all_keys))
