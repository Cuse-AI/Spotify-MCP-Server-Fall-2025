import json
import random
import math

# Load the complete tapestry
with open('ananki_outputs/emotional_manifold_COMPLETE.json', 'r', encoding='utf-8') as f:
    manifold = json.load(f)

with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

sub_vibes = manifold['sub_vibes']
central_positions = manifold['central_vibes']['positions']
all_songs = tapestry['vibes']

# 20 Test Prompts (mix of normal, edge cases, abstract, imaginary)
test_prompts = [
    # Normal emotional states
    "I'm feeling really sad after my breakup",
    "Need pump up music for my workout",
    "Chill vibes for a Sunday morning coffee",
    "I'm so happy and celebrating good news!",
    
    # Complex/mixed emotions
    "I'm sad but also kind of angry about being betrayed",
    "Feeling hopeful but still a little anxious about the future",
    "Nostalgic and melancholic about my childhood",
    "Confident but with a dark edge, like a villain",
    
    # Abstract/metaphorical
    "Music that feels like 3am thoughts spiraling",
    "Songs for when you're driving alone through a neon-lit city at night",
    "I want to feel like the main character in a coming-of-age movie",
    "Music that sounds like rain on a window while you're safe inside",
    
    # Imaginary places/scenarios
    "Soundtrack for exploring an abandoned space station",
    "Music for a quiet morning in a cottage in the woods",
    "Songs that feel like wandering through a misty forest at dawn",
    "I'm at a underground rave in an alternate timeline",
    
    # Weird/edge cases
    "I'm bored but restless and can't settle on anything",
    "Feeling grateful but also a little sad it has to end",
    "Music for when you're excited about adventure but also terrified",
    "I need songs that are both chaotic and weirdly playful"
]

def analyze_prompt(prompt):
    """Ananki analyzes the prompt and determines emotional composition"""
    prompt_lower = prompt.lower()
    
    # Emotional keyword detection with weights
    detected_emotions = {}
    
    # Keywords for each emotion
    emotion_keywords = {
        'Sad': ['sad', 'heartbreak', 'crying', 'lonely', 'grief', 'depressed', 'melancholy', 'breakup', 'miss'],
        'Happy': ['happy', 'celebrating', 'joy', 'sunshine', 'good news', 'celebration', 'euphoric'],
        'Chill': ['chill', 'relaxed', 'calm', 'sunday', 'coffee', 'peaceful', 'easy'],
        'Anxious': ['anxious', 'worried', 'nervous', 'panic', 'stressed', 'overwhelmed', 'terrified'],
        'Energy': ['pump up', 'workout', 'energetic', 'hype', 'motivated', 'running', 'sports'],
        'Dark': ['dark', 'villain', 'gothic', 'shadow', 'noir', 'apocalyptic', 'haunting'],
        'Introspective': ['thoughts', 'contemplating', 'reflecting', 'pondering', 'wondering', 'spiraling'],
        'Romantic': ['love', 'romance', 'intimate', 'date', 'relationship'],
        'Nostalgic': ['nostalgic', 'childhood', 'memories', 'past', 'simpler times', '90s', '2000s'],
        'Night': ['night', '3am', 'midnight', 'nocturnal', 'late'],
        'Drive': ['driving', 'road', 'journey', 'car', 'highway'],
        'Party': ['party', 'club', 'rave', 'dance', 'festival'],
        'Angry': ['angry', 'rage', 'mad', 'furious', 'frustrated'],
        'Bitter': ['betrayed', 'resentful', 'bitter'],
        'Hopeful': ['hopeful', 'optimistic', 'healing', 'better'],
        'Excited': ['excited', 'adventure', 'anticipation', 'exploring'],
        'Jealous': ['jealous', 'envious'],
        'Peaceful': ['peaceful', 'serene', 'quiet', 'gentle', 'safe inside', 'cottage', 'woods'],
        'Playful': ['playful', 'silly', 'fun', 'whimsical'],
        'Chaotic': ['chaotic', 'frantic', 'overwhelming', 'scattered', 'abandoned'],
        'Bored': ['bored', 'restless', 'waiting', 'monotonous'],
        'Grateful': ['grateful', 'thankful', 'appreciative'],
        'Confident': ['confident', 'powerful', 'boss', 'unstoppable', 'main character']
    }
    
    # Metaphor/context modifiers
    if 'rain' in prompt_lower and 'window' in prompt_lower:
        detected_emotions['Chill'] = detected_emotions.get('Chill', 0) + 0.4
        detected_emotions['Peaceful'] = detected_emotions.get('Peaceful', 0) + 0.3
        detected_emotions['Introspective'] = detected_emotions.get('Introspective', 0) + 0.2
    
    if 'neon' in prompt_lower or 'city' in prompt_lower and 'night' in prompt_lower:
        detected_emotions['Night'] = detected_emotions.get('Night', 0) + 0.4
        detected_emotions['Drive'] = detected_emotions.get('Drive', 0) + 0.3
        detected_emotions['Dark'] = detected_emotions.get('Dark', 0) + 0.2
    
    if 'forest' in prompt_lower or 'misty' in prompt_lower or 'dawn' in prompt_lower:
        detected_emotions['Peaceful'] = detected_emotions.get('Peaceful', 0) + 0.4
        detected_emotions['Introspective'] = detected_emotions.get('Introspective', 0) + 0.3
    
    if 'space' in prompt_lower or 'abandoned' in prompt_lower:
        detected_emotions['Dark'] = detected_emotions.get('Dark', 0) + 0.3
        detected_emotions['Introspective'] = detected_emotions.get('Introspective', 0) + 0.3
        detected_emotions['Anxious'] = detected_emotions.get('Anxious', 0) + 0.2
    
    # Detect keywords
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in prompt_lower:
                detected_emotions[emotion] = detected_emotions.get(emotion, 0) + 0.3
    
    # Normalize to sum to 1.0
    if detected_emotions:
        total = sum(detected_emotions.values())
        detected_emotions = {k: v/total for k, v in detected_emotions.items()}
    else:
        # Default to chill if nothing detected
        detected_emotions = {'Chill': 1.0}
    
    return detected_emotions

def calculate_target_coords(emotional_composition, central_positions):
    """Calculate target coordinates based on emotional composition"""
    x_total = 0
    y_total = 0
    
    for vibe, weight in emotional_composition.items():
        if vibe in central_positions:
            x_total += central_positions[vibe]['x'] * weight
            y_total += central_positions[vibe]['y'] * weight
    
    return {'x': x_total, 'y': y_total}

def find_nearest_subvibe(target_coords, sub_vibes):
    """Find the nearest sub-vibe to target coordinates"""
    min_distance = float('inf')
    nearest_vibe = None
    
    for vibe_name, vibe_data in sub_vibes.items():
        coords = vibe_data['coordinates']
        distance = math.sqrt((coords['x'] - target_coords['x'])**2 + 
                           (coords['y'] - target_coords['y'])**2)
        
        if distance < min_distance:
            min_distance = distance
            nearest_vibe = vibe_name
    
    return nearest_vibe, min_distance

def get_random_song(vibe_name, all_songs):
    """Get a random song from the vibe"""
    if vibe_name in all_songs and all_songs[vibe_name]['songs']:
        song = random.choice(all_songs[vibe_name]['songs'])
        return f"{song['artist']} - {song['song']}"
    return "No song found"

# Run the test!
print('\n' + '='*80)
print('TAPESTRY WALKER: Testing the Emotional Manifold')
print('='*80)

for i, prompt in enumerate(test_prompts, 1):
    print(f'\n[{i}/20] USER PROMPT:')
    print(f'"{prompt}"')
    
    # Ananki analyzes the prompt
    emotional_comp = analyze_prompt(prompt)
    print(f'\nANANKI ANALYSIS:')
    top_emotions = sorted(emotional_comp.items(), key=lambda x: x[1], reverse=True)[:3]
    for emotion, weight in top_emotions:
        print(f'  {emotion}: {int(weight*100)}%')
    
    # Calculate target coordinates
    target = calculate_target_coords(emotional_comp, central_positions)
    print(f'\nTARGET COORDINATES: ({target["x"]:.1f}, {target["y"]:.1f})')
    
    # Find nearest sub-vibe
    nearest_vibe, distance = find_nearest_subvibe(target, sub_vibes)
    print(f'NEAREST SUB-VIBE: {nearest_vibe} (distance: {distance:.1f})')
    
    # Get a song recommendation
    song = get_random_song(nearest_vibe, all_songs)
    print(f'\nRECOMMENDATION: {song}')
    print('-'*80)

print('\n' + '='*80)
print('Test complete! Ready to build playlists!')
print('='*80)
