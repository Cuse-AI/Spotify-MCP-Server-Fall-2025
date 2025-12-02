import json

# Final removal - KISS with exact title
path_10 = 'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_10_CLEANED.json'
with open(path_10, 'r', encoding='utf-8') as f:
    data = json.load(f)

removed = 0
for vibe, vibe_data in data.get('vibes', {}).items():
    original = len(vibe_data.get('songs', []))
    vibe_data['songs'] = [
        s for s in vibe_data.get('songs', [])
        if not (s.get('artist') == 'KISS' and 'Rock And Roll All Nite' in s.get('song', ''))
    ]
    diff = original - len(vibe_data['songs'])
    if diff > 0:
        removed += diff
        print(f"Removed from {vibe}: {diff}")

with open(path_10, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nTotal removed: {removed}")
