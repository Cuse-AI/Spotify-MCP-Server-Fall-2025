import json
import os

# Load all 11 batch files
batches = []
for i in range(1, 12):
    if i == 11:
        filename = f'ananki_outputs/emotional_analysis_batch{i}_FINAL.json'
    else:
        filename = f'ananki_outputs/emotional_analysis_batch{i}.json'
    
    with open(filename, 'r', encoding='utf-8') as f:
        batch_data = json.load(f)
        batches.append(batch_data)

# Merge all analyses into one master dictionary
master_analysis = {}
for batch in batches:
    master_analysis.update(batch['analysis'])

# Load the central vibe coordinates
with open('ananki_outputs/vibe_coordinates.json', 'r', encoding='utf-8') as f:
    coord_data = json.load(f)

central_positions = coord_data['central_vibe_positions']

# Now calculate actual 2D coordinates for each sub-vibe based on its emotional composition
subvibe_coordinates = {}

for subvibe_name, analysis in master_analysis.items():
    composition = analysis['emotional_composition']
    
    # Calculate weighted average position based on emotional composition
    x_total = 0
    y_total = 0
    
    for central_vibe, weight in composition.items():
        if central_vibe in central_positions:
            x_total += central_positions[central_vibe]['x'] * weight
            y_total += central_positions[central_vibe]['y'] * weight
    
    subvibe_coordinates[subvibe_name] = {
        'x': round(x_total, 2),
        'y': round(y_total, 2)
    }

# Create the complete master file
master_output = {
    'metadata': {
        'total_sub_vibes': len(master_analysis),
        'total_central_vibes': len(central_positions),
        'analysis_complete': True,
        'coordinate_system': {
            'range_x': [0, 1000],
            'range_y': [0, 1000],
            'algorithm': 'weighted_composition'
        }
    },
    'central_vibes': {
        'positions': central_positions,
        'total': len(central_positions)
    },
    'sub_vibes': {}
}

# Add each sub-vibe with its full analysis and coordinates
for subvibe_name, analysis in master_analysis.items():
    master_output['sub_vibes'][subvibe_name] = {
        'emotional_composition': analysis['emotional_composition'],
        'coordinates': subvibe_coordinates[subvibe_name],
        'analysis': analysis['analysis'],
        'proximity_notes': analysis['proximity_notes']
    }

# Save the master file
with open('ananki_outputs/emotional_manifold_COMPLETE.json', 'w', encoding='utf-8') as f:
    json.dump(master_output, f, indent=2)

print('\n' + '='*70)
print('EMOTIONAL MANIFOLD COMPLETE')
print('='*70)
print(f'\nTotal sub-vibes: {len(master_analysis)}')
print(f'Total central vibes: {len(central_positions)}')
print('\nSample sub-vibe coordinates:')
for i, (name, coords) in enumerate(list(subvibe_coordinates.items())[:5]):
    print(f'  {name}: ({coords["x"]}, {coords["y"]})')
print('  ...')

print(f'\nSaved to: ananki_outputs/emotional_manifold_COMPLETE.json')
print('\nThe emotional manifold is now fully mapped!')
print('Each sub-vibe has:')
print('  - Emotional composition (% of each central vibe)')
print('  - 2D coordinates in the manifold')
print('  - Human analysis notes')
print('  - Proximity relationships')
