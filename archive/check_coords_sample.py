import json

d = json.load(open('ananki/output/COORDS_QUALITY_CHECKPOINT.json', encoding='utf-8'))
t = d.get('tapestry', {})
vibes = t.get('vibes', {})
first_vibe = list(vibes.keys())[0]
songs = vibes[first_vibe].get('songs', [])
s = songs[0]

print('=== SAMPLE SONG WITH COORDINATES ===')
print(f"Artist: {s.get('artist')}")
print(f"Song: {s.get('song')}")
print(f"Mapped Subvibe: {s.get('mapped_subvibe')}")
print(f"Coordinates: {s.get('coordinates')}")
print()
print(f"Emotional Composition:")
for vibe, weight in s.get('emotional_composition', {}).items():
    if weight > 0:
        print(f"  {vibe}: {weight:.2f}")
