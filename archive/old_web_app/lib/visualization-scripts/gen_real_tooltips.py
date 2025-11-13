import json

# Load tapestry
t = json.load(open('tapestry_VALIDATED_ONLY.json', encoding='utf-8'))

# Load manifold structure
m = json.load(open('emotional_manifold_COMPLETE.json', encoding='utf-8'))

# Build updated sub-vibes
updated = {}
for name, data in m['sub_vibes'].items():
    songs = t['vibes'].get(name, {}).get('songs', [])
    
    if songs:
        ex = songs[0]
        reasoning = ex.get('ananki_reasoning', ex.get('comment_text', 'No context'))
        if len(reasoning) > 200:
            reasoning = reasoning[:197] + '...'
        
        analysis = f"{len(songs)} songs. Ex: {ex['artist']} - {ex['song']}. {reasoning}"
        analysis = analysis.replace('"', '\\\\"')
    else:
        analysis = 'Empty - needs scraping!'
    
    updated[name] = {
        'emotional_composition': data['emotional_composition'],
        'coordinates': data['coordinates'],
        'analysis': analysis
    }

with open('subvibes_with_real_data.json', 'w', encoding='utf-8') as f:
    json.dump(updated, f, indent=2, ensure_ascii=False)

print(f'Done! {len(updated)} sub-vibes updated with real examples')
