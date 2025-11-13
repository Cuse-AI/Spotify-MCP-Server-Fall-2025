import json

t = json.load(open('C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/data/ananki_outputs/tapestry_VALIDATED_ONLY.json', encoding='utf-8'))

populated = {}
empty = []

for vibe, data in t['vibes'].items():
    count = len(data.get('songs', []))
    if count > 0:
        populated[vibe] = count
    else:
        empty.append(vibe)

print("TAPESTRY CURRENT STATUS")
print("="*70)
print(f"Total sub-vibes: {len(t['vibes'])}")
print(f"Populated: {len(populated)}")
print(f"Empty: {len(empty)}")
print(f"Total songs: {sum(populated.values())}")

print(f"\n{'='*70}")
print("POPULATED SUB-VIBES (have songs):")
print(f"{'='*70}")
for vibe, count in sorted(populated.items(), key=lambda x: x[1], reverse=True):
    print(f"{vibe}: {count} songs")

print(f"\n{'='*70}")
print(f"EMPTY SUB-VIBES: {len(empty)}")
print(f"{'='*70}")
print("First 20 empty sub-vibes:")
for vibe in empty[:20]:
    print(f"  {vibe}")
