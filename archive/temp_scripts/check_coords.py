import json

with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("Sample songs with coordinates:")
print("=" * 60)

# Get songs from different vibes
vibes = list(d['vibes'].items())[:5]
for vibe_name, vibe_data in vibes:
    print(f"\n{vibe_name}:")
    for s in vibe_data['songs'][:2]:
        coords = s.get('coordinates', {})
        print(f"  {s['artist']} - {s['song']}")
        print(f"    -> ({coords.get('x', 'N/A')}, {coords.get('y', 'N/A')})")
