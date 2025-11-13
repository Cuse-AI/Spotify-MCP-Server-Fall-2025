"""
Build Complete Emotional Relationship Map
Maps all 114 sub-vibes to their central vibes and creates relationship graph
"""
import json
from collections import defaultdict

# Load the complete tapestry
with open('ananki_outputs/tapestry_complete.json', encoding='utf-8') as f:
    data = json.load(f)

vibes = data['vibes']

print(f'\n=== BUILDING COMPLETE EMOTIONAL MAP ===')
print(f'Total sub-vibes to map: {len(vibes)}')

# Step 1: Extract all unique central vibe categories
central_vibes = defaultdict(list)

for sub_vibe_name in vibes.keys():
    # Extract central vibe (everything before the dash)
    if ' - ' in sub_vibe_name:
        central = sub_vibe_name.split(' - ')[0].strip()
        central_vibes[central].append(sub_vibe_name)
    else:
        print(f'WARNING: No dash found in: {sub_vibe_name}')

print(f'\n=== DISCOVERED CENTRAL VIBES ===')
print(f'Total central vibes: {len(central_vibes)}')
for central, subs in sorted(central_vibes.items()):
    print(f'{central}: {len(subs)} sub-vibes')

# Save the discovered structure
output = {
    'central_vibes': {},
    'metadata': {
        'total_central_vibes': len(central_vibes),
        'total_sub_vibes': len(vibes),
        'date_created': '2025-11-09'
    }
}

for central, sub_list in sorted(central_vibes.items()):
    output['central_vibes'][central] = {
        'sub_vibes': sorted(sub_list),
        'count': len(sub_list)
    }

# Save to file
with open('ananki_outputs/discovered_structure.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\n=== SAVED ===')
print(f'discovered_structure.json created!')
print(f'\nNext: Define emotional properties and relationships for each central vibe')
