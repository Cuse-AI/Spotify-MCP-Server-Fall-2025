import json

d = json.load(open('core/tapestry_quality_final.json', encoding='utf-8'))
total = sum(len(v.get('songs', [])) for v in d['vibes'].values())
print(f'Total songs: {total}')

s = list(d['vibes'].values())[0]['songs'][0]
print(f'Has coordinates: {"coordinates" in s}')
print(f'Sample coords: {s.get("coordinates")}')
print(f'Has emotional_composition: {"emotional_composition" in s}')
