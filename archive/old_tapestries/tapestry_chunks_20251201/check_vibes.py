import json

path = 'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_10_CLEANED.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("VIBES IN CHUNK 02:")
for vibe in data['vibes']:
    count = len(data['vibes'][vibe]['songs'])
    print(f"  {vibe}: {count} songs")
