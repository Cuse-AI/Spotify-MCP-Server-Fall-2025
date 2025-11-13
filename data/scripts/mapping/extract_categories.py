import json

with open('ananki_outputs/tapestry_complete.json', encoding='utf-8') as f:
    data = json.load(f)

vibes = data['vibes']

# Group sub-vibes by their category (prefix before the dash)
categories = {}
for vibe_name in vibes.keys():
    if ' - ' in vibe_name:
        category = vibe_name.split(' - ')[0]
        if category not in categories:
            categories[category] = []
        categories[category].append(vibe_name)
    else:
        # Handle any without dashes
        if 'Other' not in categories:
            categories['Other'] = []
        categories['Other'].append(vibe_name)

# Sort categories by number of sub-vibes
sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

print('\n=== ALL VIBE CATEGORIES ===')
print(f'Total categories: {len(categories)}')
print(f'Total sub-vibes: {sum(len(v) for v in categories.values())}\n')

for cat, subs in sorted_cats:
    print(f'\n{cat} ({len(subs)} sub-vibes):')
    for sub in subs:
        song_count = len(vibes[sub]['songs'])
        print(f'  - {sub}: {song_count} songs')

# Save structured output
output = {
    'categories': categories,
    'total_categories': len(categories),
    'total_sub_vibes': sum(len(v) for v in categories.values())
}

with open('ananki_outputs/vibe_categories_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n\n✅ Saved to: ananki_outputs/vibe_categories_extracted.json')
