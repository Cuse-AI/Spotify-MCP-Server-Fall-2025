import json
import math
import random

# Load the relationships
with open('ananki_outputs/central_vibe_relationships.json', encoding='utf-8') as f:
    data = json.load(f)

central_vibes = data['central_vibes']

# Initialize positions - use more strategic starting positions
random.seed(42)
positions = {}

# Start with a circular arrangement to avoid edge clustering
vibes_list = list(central_vibes.keys())
n = len(vibes_list)

for i, vibe in enumerate(vibes_list):
    angle = (i / n) * 2 * math.pi
    radius = 300  # Start in middle, not at edges
    positions[vibe] = {
        'x': 500 + radius * math.cos(angle),
        'y': 500 + radius * math.sin(angle)
    }

print('Running improved force-directed layout...')

# Improved force-directed layout
iterations = 2000  # More iterations
learning_rate = 0.08  # Slightly lower for stability
ideal_distance = 150  # INCREASED from 80 - connections should be closer!
repulsion_strength = 8000  # Increased repulsion
connection_strength = 0.03  # INCREASED - pull connected vibes together more strongly!

for iteration in range(iterations):
    forces = {vibe: {'x': 0, 'y': 0} for vibe in central_vibes.keys()}
    
    # Calculate forces
    vibes_list = list(central_vibes.keys())
    for i, vibe1 in enumerate(vibes_list):
        for vibe2 in vibes_list[i+1:]:
            dx = positions[vibe2]['x'] - positions[vibe1]['x']
            dy = positions[vibe2]['y'] - positions[vibe1]['y']
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < 1:
                distance = 1
            
            connected = vibe2 in central_vibes[vibe1]['connects_to']
            
            if connected:
                # STRONGER attraction for connected vibes
                force_magnitude = (distance - ideal_distance) * connection_strength
            else:
                # Repulsion for non-connected
                force_magnitude = -repulsion_strength / (distance * distance)
            
            fx = (dx / distance) * force_magnitude
            fy = (dy / distance) * force_magnitude
            
            forces[vibe1]['x'] += fx
            forces[vibe1]['y'] += fy
            forces[vibe2]['x'] -= fx
            forces[vibe2]['y'] -= fy
    
    # Apply forces
    for vibe in central_vibes.keys():
        positions[vibe]['x'] += forces[vibe]['x'] * learning_rate
        positions[vibe]['y'] += forces[vibe]['y'] * learning_rate
    
    if iteration % 400 == 0:
        print(f'  Iteration {iteration}/{iterations}...')

print('Layout complete! Normalizing...')

# Normalize to 0-1000 range
min_x = min(p['x'] for p in positions.values())
max_x = max(p['x'] for p in positions.values())
min_y = min(p['y'] for p in positions.values())
max_y = max(p['y'] for p in positions.values())

for vibe in positions:
    positions[vibe]['x'] = ((positions[vibe]['x'] - min_x) / (max_x - min_x)) * 1000
    positions[vibe]['y'] = ((positions[vibe]['y'] - min_y) / (max_y - min_y)) * 1000

# Save improved coordinates
output = {
    'central_vibe_positions': positions,
    'coordinate_system': {
        'range_x': [0, 1000],
        'range_y': [0, 1000],
        'algorithm': 'improved_force_directed_layout',
        'notes': 'Increased connection strength and ideal distance to keep related vibes closer'
    }
}

with open('ananki_outputs/vibe_coordinates_v2.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\nImproved coordinates saved to: vibe_coordinates_v2.json')
print('\nChecking Playful and Jealous distances...')

# Check the problem vibes
for vibe in ['Playful', 'Jealous']:
    vibe_pos = positions[vibe]
    connections = central_vibes[vibe]['connects_to']
    distances = []
    
    for connected in connections:
        if connected in positions:
            connected_pos = positions[connected]
            distance = math.sqrt((vibe_pos['x'] - connected_pos['x'])**2 + 
                               (vibe_pos['y'] - connected_pos['y'])**2)
            distances.append(distance)
    
    avg_dist = sum(distances) / len(distances) if distances else 0
    print(f'{vibe}: Avg distance = {avg_dist:.1f} (was 452.9/558.9)')
