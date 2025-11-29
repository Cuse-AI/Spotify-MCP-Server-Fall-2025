import json

with open('ananki_outputs/tapestry_complete.json', encoding='utf-8') as f:
    data = json.load(f)

t = data['vibes']
stats = data['stats']

print(f'\n=== TAPESTRY SUMMARY ===')
print(f'Total sub-vibes: {len(t)}')
print(f'Total songs: {stats.get("total_songs", "N/A")}')
print(f'Total artists: {stats.get("total_artists", "N/A")}')

print(f'\n=== FIRST 30 SUB-VIBES ===')
for i, (vibe, vdata) in enumerate(list(t.items())[:30], 1):
    print(f'{i}. {vibe} ({len(vdata["songs"])} songs)')

print(f'\n=== LAST 20 SUB-VIBES ===')
all_vibes = list(t.items())
for i, (vibe, vdata) in enumerate(all_vibes[-20:], len(all_vibes)-19):
    print(f'{i}. {vibe} ({len(vdata["songs"])} songs)')

print(f'\n=== STATS FROM FILE ===')
for key, value in stats.items():
    print(f'{key}: {value}')
