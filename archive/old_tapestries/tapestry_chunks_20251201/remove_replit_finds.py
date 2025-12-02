import json

# Additional songs to remove based on Replit's analysis
chunk_10_remove = [
    ("Celestial Aeon Project", "Corruption of Power"),
    ("KISS", "Rock And Roll All Nite"),
    ("Ghost", "Mary On A Cross"),
]

chunk_11_remove = [
    ("NEFFEX", "Rumors"),
]

# Fix chunk 10
path_10 = 'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_10_CLEANED.json'
with open(path_10, 'r', encoding='utf-8') as f:
    data_10 = json.load(f)

removed_10 = []
for vibe, vibe_data in data_10.get('vibes', {}).items():
    original = len(vibe_data.get('songs', []))
    vibe_data['songs'] = [
        s for s in vibe_data.get('songs', [])
        if (s.get('artist'), s.get('song')) not in chunk_10_remove
    ]
    diff = original - len(vibe_data['songs'])
    if diff > 0:
        removed_10.append(f"{vibe}: {diff}")

with open(path_10, 'w', encoding='utf-8') as f:
    json.dump(data_10, f, indent=2, ensure_ascii=False)

print("Chunk 10 removals:")
for r in removed_10:
    print(f"  {r}")

# Fix chunk 11
path_11 = 'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_11_CLEANED.json'
with open(path_11, 'r', encoding='utf-8') as f:
    data_11 = json.load(f)

removed_11 = []
for vibe, vibe_data in data_11.get('vibes', {}).items():
    original = len(vibe_data.get('songs', []))
    vibe_data['songs'] = [
        s for s in vibe_data.get('songs', [])
        if (s.get('artist'), s.get('song')) not in chunk_11_remove
    ]
    diff = original - len(vibe_data['songs'])
    if diff > 0:
        removed_11.append(f"{vibe}: {diff}")

with open(path_11, 'w', encoding='utf-8') as f:
    json.dump(data_11, f, indent=2, ensure_ascii=False)

print("\nChunk 11 removals:")
for r in removed_11:
    print(f"  {r}")

print(f"\nTotal additional removals: {len(removed_10) + len(removed_11)}")
