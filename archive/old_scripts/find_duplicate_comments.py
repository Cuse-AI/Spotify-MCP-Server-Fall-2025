import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

songs = [s for v in tapestry['vibes'].values() for s in v.get('songs', [])]

# Group songs by their comment text
comment_to_songs = defaultdict(list)
for s in songs:
    comment = s.get('comment_text', '').strip()
    if comment and len(comment) > 20:  # Only check meaningful comments
        comment_to_songs[comment].append(s)

# Find duplicates
duplicates = {k: v for k, v in comment_to_songs.items() if len(v) > 1}

print(f"Total songs: {len(songs)}")
print(f"Unique comments (>20 chars): {len(comment_to_songs)}")
print(f"Duplicate comments found: {len(duplicates)}")
print("=" * 70)

if duplicates:
    print(f"\nDUPLICATE COMMENTS ({len(duplicates)} found):\n")
    for comment, song_list in sorted(duplicates.items(), key=lambda x: -len(x[1])):
        print(f"Comment ({len(song_list)} songs): \"{comment[:100]}{'...' if len(comment) > 100 else ''}\"")
        print("Songs with this comment:")
        for s in song_list:
            print(f"  - {s['artist']} - {s['song']}")
            print(f"    Source: {s.get('source_url', 'N/A')}")
        print("-" * 70)
else:
    print("\n✅ No duplicate comments found!")
