"""Define Emotional Properties Part 1"""
import json

with open('ananki_outputs/discovered_structure.json', encoding='utf-8') as f:
    structure = json.load(f)

print('=== DEFINING EMOTIONAL SPACE ===')

# Part 1: Define first batch of central vibes
central_definitions = {
    'Sad': {'description': 'Sadness, sorrow, grief, melancholy, heartbreak', 'valence': -0.8, 'energy': 0.2, 'color': '#4A90E2'},
    'Happy': {'description': 'Happiness, joy, positivity, celebration, sunshine', 'valence': 0.9, 'energy': 0.7, 'color': '#FFD700'},
    'Angry': {'description': 'Anger, rage, fury, aggression, frustration', 'valence': -0.7, 'energy': 0.9, 'color': '#FF4444'},
    'Bitter': {'description': 'Bitterness, resentment, betrayal, spite', 'valence': -0.8, 'energy': 0.4, 'color': '#8B4513'},
    'Anxious': {'description': 'Anxiety, worry, stress, tension, panic', 'valence': -0.6, 'energy': 0.8, 'color': '#9370DB'},
    'Calm': {'description': 'Calmness, relaxation, peace, tranquility', 'valence': 0.5, 'energy': 0.2, 'color': '#87CEEB'},
    'Peaceful': {'description': 'Peace, serenity, stillness, harmony', 'valence': 0.7, 'energy': 0.1, 'color': '#98FB98'},
    'Energetic': {'description': 'Energy, motivation, power, drive', 'valence': 0.7, 'energy': 0.95, 'color': '#FF6B35'},
}

print(f'Batch 1: {len(central_definitions)} vibes defined')
