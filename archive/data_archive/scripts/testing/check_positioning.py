import json
import math

# Load data
with open('ananki_outputs/vibe_coordinates.json', 'r', encoding='utf-8') as f:
    coords = json.load(f)

with open('ananki_outputs/central_vibe_relationships.json', 'r', encoding='utf-8') as f:
    relationships = json.load(f)

positions = coords['central_vibe_positions']
central_vibes = relationships['central_vibes']

# Check Playful and Jealous
problem_vibes = ['Playful', 'Jealous']

for vibe in problem_vibes:
    print(f'\n{"="*70}')
    print(f'{vibe} Analysis:')
    print(f'{"="*70}')
    
    vibe_pos = positions[vibe]
    print(f'Position: ({vibe_pos["x"]:.1f}, {vibe_pos["y"]:.1f})')
    
    connections = central_vibes[vibe]['connects_to']
    print(f'\nConnections: {", ".join(connections)}')
    
    print(f'\nDistances to connected vibes:')
    for connected in connections:
        if connected in positions:
            connected_pos = positions[connected]
            distance = math.sqrt((vibe_pos['x'] - connected_pos['x'])**2 + 
                               (vibe_pos['y'] - connected_pos['y'])**2)
            print(f'  {connected:20s} -> Distance: {distance:6.1f}  at ({connected_pos["x"]:.1f}, {connected_pos["y"]:.1f})')
    
    # Find average distance to connections
    distances = []
    for connected in connections:
        if connected in positions:
            connected_pos = positions[connected]
            distance = math.sqrt((vibe_pos['x'] - connected_pos['x'])**2 + 
                               (vibe_pos['y'] - connected_pos['y'])**2)
            distances.append(distance)
    
    avg_dist = sum(distances) / len(distances) if distances else 0
    print(f'\nAverage distance to connections: {avg_dist:.1f}')
    print(f'Max distance: {max(distances):.1f}')
    print(f'Min distance: {min(distances):.1f}')

print(f'\n{"="*70}')
print('Analysis complete')
print(f'{"="*70}')
