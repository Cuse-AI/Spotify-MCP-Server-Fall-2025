import json

# Load the tapestry and coordinates
with open('ananki_outputs/tapestry_complete.json', encoding='utf-8') as f:
    tapestry_data = json.load(f)

with open('ananki_outputs/vibe_coordinates.json', encoding='utf-8') as f:
    coord_data = json.load(f)

with open('ananki_outputs/vibe_categories_extracted.json', encoding='utf-8') as f:
    categories_data = json.load(f)

vibes = tapestry_data['vibes']
central_positions = coord_data['central_vibe_positions']
categories = categories_data['categories']

# For Ananki to analyze: get sample songs and contexts from each sub-vibe
print('\n=== PREPARING SUB-VIBE DATA FOR ANANKI ANALYSIS ===')
print(f'Total sub-vibes to analyze: {len(vibes)}\n')

subvibe_analysis_data = {}

for subvibe_name, subvibe_data in vibes.items():
    # Get parent category
    if ' - ' in subvibe_name:
        parent = subvibe_name.split(' - ')[0]
    else:
        parent = 'Other'
    
    # Sample some songs and their contexts
    songs = subvibe_data['songs'][:5]  # First 5 songs as sample
    
    # Get vibe descriptions from songs
    contexts = []
    for song in songs:
        if 'vibe_description' in song and song['vibe_description']:
            contexts.append(song['vibe_description'])
        if 'recommendation_reasoning' in song and song['recommendation_reasoning']:
            contexts.append(song['recommendation_reasoning'][:200])
    
    subvibe_analysis_data[subvibe_name] = {
        'parent_category': parent,
        'total_songs': len(subvibe_data['songs']),
        'sample_songs': [f"{s['artist']} - {s['song']}" for s in songs],
        'context_samples': contexts[:10],  # Max 10 context samples
        'needs_analysis': True
    }

# Save for Ananki to analyze
output = {
    'subvibes': subvibe_analysis_data,
    'total_subvibes': len(subvibe_analysis_data),
    'central_positions': central_positions,
    'instructions': 'Ananki will analyze each sub-vibe and determine its emotional composition'
}

with open('ananki_outputs/subvibes_for_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f'Prepared {len(subvibe_analysis_data)} sub-vibes for Ananki analysis')
print('\nSample data structure for first sub-vibe:')
first_subvibe = list(subvibe_analysis_data.keys())[0]
print(f'\n{first_subvibe}:')
print(f'  Parent: {subvibe_analysis_data[first_subvibe]["parent_category"]}')
print(f'  Songs: {subvibe_analysis_data[first_subvibe]["total_songs"]}')
print(f'  Sample songs: {subvibe_analysis_data[first_subvibe]["sample_songs"][:3]}')
print(f'  Context samples: {len(subvibe_analysis_data[first_subvibe]["context_samples"])} descriptions')

print('\nSaved to: ananki_outputs/subvibes_for_analysis.json')
print('\nNext: Ananki will analyze emotional composition of each sub-vibe!')
