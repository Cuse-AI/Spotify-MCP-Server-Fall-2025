import json
import math

# Load the relationships
with open('ananki_outputs/central_vibe_relationships.json', encoding='utf-8') as f:
    data = json.load(f)

central_vibes = data['central_vibes']

# Initialize random positions for each vibe
import random
random.seed(42)  # For reproducibility

positions = {}
for vibe in central_vibes.keys():
    angle = random.random() * 2 * math.pi
    radius = random.random() * 100 + 50
    positions[vibe] = {
        'x': radius * math.cos(angle),
        'y': radius * math.sin(angle)
    }

# Force-directed layout: iteratively adjust positions
# Connected vibes should be close, non-connected should be far
iterations = 1000
learning_rate = 0.1
ideal_distance = 80  # Ideal distance for connected vibes
repulsion_strength = 5000  # How much non-connected vibes repel

print('\n=== COMPUTING VIBE COORDINATES ===')
print('Using force-directed layout algorithm...')

for iteration in range(iterations):
    forces = {vibe: {'x': 0, 'y': 0} for vibe in central_vibes.keys()}
    
    # Calculate forces between all pairs
    vibes_list = list(central_vibes.keys())
    for i, vibe1 in enumerate(vibes_list):
        for vibe2 in vibes_list[i+1:]:
            # Calculate distance
            dx = positions[vibe2]['x'] - positions[vibe1]['x']
            dy = positions[vibe2]['y'] - positions[vibe1]['y']
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < 1:
                distance = 1
            
            # Are they connected?
            connected = vibe2 in central_vibes[vibe1]['connects_to']
            
            if connected:
                # Attraction: pull together if too far
                force_magnitude = (distance - ideal_distance) * 0.01
            else:
                # Repulsion: push apart
                force_magnitude = -repulsion_strength / (distance * distance)
            
            # Apply force
            fx = (dx / distance) * force_magnitude
            fy = (dy / distance) * force_magnitude
            
            forces[vibe1]['x'] += fx
            forces[vibe1]['y'] += fy
            forces[vibe2]['x'] -= fx
            forces[vibe2]['y'] -= fy
    
    # Update positions
    for vibe in central_vibes.keys():
        positions[vibe]['x'] += forces[vibe]['x'] * learning_rate
        positions[vibe]['y'] += forces[vibe]['y'] * learning_rate
    
    if iteration % 200 == 0:
        print(f'  Iteration {iteration}/{iterations}...')

print('Coordinates computed!')

# Normalize to a nice range (0-1000)
min_x = min(p['x'] for p in positions.values())
max_x = max(p['x'] for p in positions.values())
min_y = min(p['y'] for p in positions.values())
max_y = max(p['y'] for p in positions.values())

for vibe in positions:
    positions[vibe]['x'] = ((positions[vibe]['x'] - min_x) / (max_x - min_x)) * 1000
    positions[vibe]['y'] = ((positions[vibe]['y'] - min_y) / (max_y - min_y)) * 1000

# Save coordinates
output = {
    'central_vibe_positions': positions,
    'coordinate_system': {
        'range_x': [0, 1000],
        'range_y': [0, 1000],
        'algorithm': 'force_directed_layout'
    }
}

with open('ananki_outputs/vibe_coordinates.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== COORDINATES ASSIGNED ===')
for vibe, pos in sorted(positions.items()):
    print(f'{vibe:20s} -> ({pos["x"]:.1f}, {pos["y"]:.1f})')

print('\nSaved to: ananki_outputs/vibe_coordinates.json')
