import json

# Songs to remove from chunk 10
to_remove = [
    ("Ari Abdul", "Girls On The Internet"),
    ("Miracle Healing Tones TP", "5 Hz: Improve Creativity (Theta Waves)"),
    ("Eptic", "Light Up"),
]

path = 'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_10_CLEANED.json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

removed = []
for vibe, vibe_data in data.get('vibes', {}).items():
    original_count = len(vibe_data.get('songs', []))
    vibe_data['songs'] = [
        s for s in vibe_data.get('songs', [])
        if (s.get('artist'), s.get('song')) not in to_remove
    ]
    new_count = len(vibe_data['songs'])
    if original_count != new_count:
        removed.append(f"{vibe}: removed {original_count - new_count}")

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Removed from chunk 10:")
for r in removed:
    print(f"  {r}")
print(f"\nTotal removed: {len(removed)} songs")
