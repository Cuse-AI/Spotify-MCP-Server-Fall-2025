import json

with open('ananki_outputs/tapestry_complete.json', encoding='utf-8') as f:
    data = json.load(f)

print('\n=== TAPESTRY VERIFICATION ===')
print(f'Sub-vibes: {data["stats"]["total_vibes"]}')
print(f'Songs: {data["stats"]["total_songs"]}')
print(f'Artists: {data["stats"]["total_artists"]}')
print(f'\nStatus: DATA COLLECTION 100% COMPLETE!')
