import json
import os

chunks_dir = 'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/'

# Gather all vibes from all chunks
all_vibes = {}
meta_vibes = {}

for i in range(1, 12):
    chunk_file = f'tapestry_chunk_{i:02d}_CLEANED.json'
    path = os.path.join(chunks_dir, chunk_file)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for vibe, vibe_data in data.get('vibes', {}).items():
            count = len(vibe_data.get('songs', []))
            if vibe not in all_vibes:
                all_vibes[vibe] = 0
            all_vibes[vibe] += count
            
            # Extract meta-vibe
            meta = vibe.split(' - ')[0]
            if meta not in meta_vibes:
                meta_vibes[meta] = 0
            meta_vibes[meta] += count

print("=== ALL VIBES ACROSS ALL CHUNKS ===\n")
for vibe in sorted(all_vibes.keys()):
    print(f"  {vibe}: {all_vibes[vibe]} songs")

print(f"\n=== META-VIBE TOTALS ===\n")
for meta in sorted(meta_vibes.keys(), key=lambda x: meta_vibes[x], reverse=True):
    print(f"  {meta}: {meta_vibes[meta]} songs")

print(f"\n=== TOTAL: {sum(all_vibes.values())} songs ===")
