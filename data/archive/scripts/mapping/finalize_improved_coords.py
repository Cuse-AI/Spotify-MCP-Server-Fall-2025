import json

# Load improved coordinates
with open('ananki_outputs/vibe_coordinates_v2.json', 'r', encoding='utf-8') as f:
    improved_coords = json.load(f)

# Update the main manifold file with improved coordinates
with open('ananki_outputs/emotional_manifold_COMPLETE.json', 'r', encoding='utf-8') as f:
    manifold = json.load(f)

# Replace central positions
manifold['central_vibes']['positions'] = improved_coords['central_vibe_positions']

# Recalculate sub-vibe positions based on improved central positions
for subvibe_name, subvibe_data in manifold['sub_vibes'].items():
    composition = subvibe_data['emotional_composition']
    
    # Weighted average based on improved positions
    x_total = 0
    y_total = 0
    
    for central_vibe, weight in composition.items():
        if central_vibe in improved_coords['central_vibe_positions']:
            x_total += improved_coords['central_vibe_positions'][central_vibe]['x'] * weight
            y_total += improved_coords['central_vibe_positions'][central_vibe]['y'] * weight
    
    subvibe_data['coordinates'] = {
        'x': round(x_total, 2),
        'y': round(y_total, 2)
    }

# Save updated manifold
with open('ananki_outputs/emotional_manifold_COMPLETE.json', 'w', encoding='utf-8') as f:
    json.dump(manifold, f, indent=2)

print('Manifold updated with improved coordinates!')
print('All 114 sub-vibe positions recalculated.')
