"""
Complete Emotional Relationship Map Builder
Creates the full emotional manifold with all 23 central vibes
"""
import json
import math

print('=== LOADING DATA ===')
with open('ananki_outputs/discovered_structure.json', encoding='utf-8') as f:
    structure = json.load(f)

# Define ALL 23 central vibes with emotional coordinates
# valence: -1 (negative) to +1 (positive)
# energy: 0 (low) to 1 (high)
central_vibes = {
    'Sad': {'desc': 'Sadness, sorrow, grief', 'valence': -0.8, 'energy': 0.2, 'color': '#4A90E2'},
    'Happy': {'desc': 'Happiness, joy, celebration', 'valence': 0.9, 'energy': 0.7, 'color': '#FFD700'},
    'Angry': {'desc': 'Anger, rage, aggression', 'valence': -0.7, 'energy': 0.9, 'color': '#FF4444'},
    'Bitter': {'desc': 'Bitterness, resentment', 'valence': -0.8, 'energy': 0.4, 'color': '#8B4513'},
    'Anxious': {'desc': 'Anxiety, worry, tension', 'valence': -0.6, 'energy': 0.8, 'color': '#9370DB'},
    'Chill': {'desc': 'Calmness, relaxation', 'valence': 0.5, 'energy': 0.2, 'color': '#87CEEB'},
    'Peaceful': {'desc': 'Peace, serenity', 'valence': 0.7, 'energy': 0.1, 'color': '#98FB98'},
    'Energy': {'desc': 'Motivation, power', 'valence': 0.7, 'energy': 0.95, 'color': '#FF6B35'},
    'Confident': {'desc': 'Self-assurance, boldness', 'valence': 0.8, 'energy': 0.85, 'color': '#FFD700'},
    'Excited': {'desc': 'Excitement, anticipation', 'valence': 0.8, 'energy': 0.9, 'color': '#FF69B4'},
    'Hopeful': {'desc': 'Hope, optimism', 'valence': 0.6, 'energy': 0.5, 'color': '#FFB6C1'},
    'Dark': {'desc': 'Darkness, mystery', 'valence': -0.3, 'energy': 0.4, 'color': '#2F4F4F'},
    'Introspective': {'desc': 'Reflection, contemplation', 'valence': 0.0, 'energy': 0.3, 'color': '#708090'},
    'Romantic': {'desc': 'Love, intimacy', 'valence': 0.8, 'energy': 0.5, 'color': '#FF1493'},
    'Nostalgic': {'desc': 'Nostalgia, memories', 'valence': 0.2, 'energy': 0.3, 'color': '#DAA520'},
    'Night': {'desc': 'Late-night thoughts', 'valence': -0.2, 'energy': 0.3, 'color': '#191970'},
    'Drive': {'desc': 'Journey, movement', 'valence': 0.3, 'energy': 0.6, 'color': '#4682B4'},
    'Party': {'desc': 'Celebration, dancing', 'valence': 0.9, 'energy': 1.0, 'color': '#FF00FF'},
    'Jealous': {'desc': 'Jealousy, envy', 'valence': -0.7, 'energy': 0.6, 'color': '#228B22'},
    'Playful': {'desc': 'Playfulness, fun', 'valence': 0.8, 'energy': 0.7, 'color': '#FFB347'},
    'Chaotic': {'desc': 'Chaos, frenzy', 'valence': -0.4, 'energy': 0.95, 'color': '#DC143C'},
    'Bored': {'desc': 'Boredom, restlessness', 'valence': -0.3, 'energy': 0.2, 'color': '#A9A9A9'},
    'Grateful': {'desc': 'Gratitude, appreciation', 'valence': 0.8, 'energy': 0.4, 'color': '#F4A460'}
}

print(f'Defined {len(central_vibes)} central vibes')
print('\\nCalculating emotional distances...')
