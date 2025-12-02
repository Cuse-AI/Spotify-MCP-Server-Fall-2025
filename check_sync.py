import json

# Load both files
with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\manifold\emotional_manifold_COMPLETE.json', 'r', encoding='utf-8') as f:
    manifold = json.load(f)

# Get vibes from each
tapestry_vibes = set(tapestry['vibes'].keys())
manifold_vibes = set(manifold['sub_vibes'].keys()) if 'sub_vibes' in manifold else set()

print(f"Tapestry vibes: {len(tapestry_vibes)}")
print(f"Manifold vibes: {len(manifold_vibes)}")

# Find differences
in_tapestry_not_manifold = tapestry_vibes - manifold_vibes
in_manifold_not_tapestry = manifold_vibes - tapestry_vibes

if in_tapestry_not_manifold:
    print(f"\nIn TAPESTRY but NOT in manifold ({len(in_tapestry_not_manifold)}):")
    for v in sorted(in_tapestry_not_manifold):
        print(f"  - {v}")

if in_manifold_not_tapestry:
    print(f"\nIn MANIFOLD but NOT in tapestry ({len(in_manifold_not_tapestry)}):")
    for v in sorted(in_manifold_not_tapestry):
        print(f"  - {v}")

if not in_tapestry_not_manifold and not in_manifold_not_tapestry:
    print("\n✓ Perfect match between tapestry and manifold!")

# Also check total songs
total_songs = sum(len(v['songs']) for v in tapestry['vibes'].values())
print(f"\nTotal songs in tapestry: {total_songs}")
print(f"Manifold metadata says: {manifold['metadata']['total_sub_vibes']} sub-vibes, {manifold['metadata']['total_central_vibes']} meta-vibes")
