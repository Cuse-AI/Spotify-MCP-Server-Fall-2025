"""
Step 2: Calculate Relationships Between Central Vibes
Uses Euclidean distance in valence-energy space
"""
import json
import math

# Load step 1 data
central_vibes = {
    'Sad': {'valence': -0.8, 'energy': 0.2}, 'Happy': {'valence': 0.9, 'energy': 0.7},
    'Angry': {'valence': -0.7, 'energy': 0.9}, 'Bitter': {'valence': -0.8, 'energy': 0.4},
    'Anxious': {'valence': -0.6, 'energy': 0.8}, 'Chill': {'valence': 0.5, 'energy': 0.2},
    'Peaceful': {'valence': 0.7, 'energy': 0.1}, 'Energy': {'valence': 0.7, 'energy': 0.95},
    'Confident': {'valence': 0.8, 'energy': 0.85}, 'Excited': {'valence': 0.8, 'energy': 0.9},
    'Hopeful': {'valence': 0.6, 'energy': 0.5}, 'Dark': {'valence': -0.3, 'energy': 0.4},
    'Introspective': {'valence': 0.0, 'energy': 0.3}, 'Romantic': {'valence': 0.8, 'energy': 0.5},
    'Nostalgic': {'valence': 0.2, 'energy': 0.3}, 'Night': {'valence': -0.2, 'energy': 0.3},
    'Drive': {'valence': 0.3, 'energy': 0.6}, 'Party': {'valence': 0.9, 'energy': 1.0},
    'Jealous': {'valence': -0.7, 'energy': 0.6}, 'Playful': {'valence': 0.8, 'energy': 0.7},
    'Chaotic': {'valence': -0.4, 'energy': 0.95}, 'Bored': {'valence': -0.3, 'energy': 0.2},
    'Grateful': {'valence': 0.8, 'energy': 0.4}
}

def calculate_distance(v1, v2):
    """Euclidean distance in 2D emotional space"""
    dv = v1['valence'] - v2['valence']
    de = v1['energy'] - v2['energy']
    return math.sqrt(dv**2 + de**2)

print('=== CALCULATING RELATIONSHIPS ===')

# For each central vibe, find its nearest neighbors
relationships = {}
for vibe1, props1 in central_vibes.items():
    distances = []
    for vibe2, props2 in central_vibes.items():
        if vibe1 != vibe2:
            dist = calculate_distance(props1, props2)
            distances.append((vibe2, dist))
    
    # Sort by distance and take closest 5
    distances.sort(key=lambda x: x[1])
    relationships[vibe1] = [v[0] for v in distances[:5]]
    
    print(f'{vibe1}: {relationships[vibe1][:3]}...')

print(f'\\nRelationships calculated for {len(relationships)} central vibes')
print('Saving...')

with open('ananki_outputs/relationships_only.json', 'w') as f:
    json.dump(relationships, f, indent=2)

print('DONE: relationships_only.json created')
