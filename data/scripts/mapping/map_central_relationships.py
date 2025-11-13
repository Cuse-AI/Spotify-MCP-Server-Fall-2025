import json

# Define all 23 central vibes with their relationships
# Relationships = which vibes are emotionally adjacent/connected

central_vibe_map = {
    "Sad": {
        "description": "Sadness, sorrow, grief, melancholy",
        "valence": "negative",
        "energy": "low-medium",
        "connects_to": ["Anxious", "Dark", "Introspective", "Nostalgic", "Chill", "Bitter", "Lonely", "Hopeful"]
    },
    "Happy": {
        "description": "Happiness, joy, positivity, celebration",
        "valence": "positive",
        "energy": "medium-high",
        "connects_to": ["Energy", "Romantic", "Chill", "Party", "Nostalgic", "Playful", "Grateful", "Excited", "Confident"]
    },
    "Chill": {
        "description": "Relaxation, peace, tranquility, calm",
        "valence": "positive-neutral",
        "energy": "low",
        "connects_to": ["Happy", "Introspective", "Nostalgic", "Romantic", "Sad", "Night", "Peaceful", "Grateful"]
    },
    "Anxious": {
        "description": "Anxiety, worry, stress, tension",
        "valence": "negative",
        "energy": "medium-high",
        "connects_to": ["Sad", "Introspective", "Dark", "Energy", "Night", "Chaotic", "Bored"]
    },
    "Energy": {
        "description": "Energetic, motivation, power, drive",
        "valence": "positive",
        "energy": "very high",
        "connects_to": ["Happy", "Party", "Anxious", "Drive", "Confident", "Excited", "Angry"]
    },
    "Dark": {
        "description": "Darkness, mystery, shadow, gothic",
        "valence": "neutral-negative",
        "energy": "variable",
        "connects_to": ["Sad", "Anxious", "Introspective", "Night", "Romantic", "Angry", "Bitter"]
    },
    "Introspective": {
        "description": "Reflection, contemplation, deep thought",
        "valence": "neutral",
        "energy": "low-medium",
        "connects_to": ["Sad", "Anxious", "Dark", "Chill", "Nostalgic", "Night", "Grateful", "Hopeful"]
    },
    "Romantic": {
        "description": "Love, romance, intimacy, connection",
        "valence": "positive",
        "energy": "medium",
        "connects_to": ["Happy", "Sad", "Chill", "Dark", "Nostalgic", "Night", "Jealous"]
    },
    "Nostalgic": {
        "description": "Nostalgia, longing for past, memories",
        "valence": "bittersweet",
        "energy": "low",
        "connects_to": ["Sad", "Happy", "Introspective", "Romantic", "Chill", "Hopeful"]
    },
    "Night": {
        "description": "Nighttime emotions, late-night thoughts, nocturnal",
        "valence": "varies",
        "energy": "low-medium",
        "connects_to": ["Introspective", "Dark", "Anxious", "Chill", "Sad", "Drive", "Romantic"]
    },
    "Drive": {
        "description": "Driving emotions, journey, movement",
        "valence": "varies",
        "energy": "medium",
        "connects_to": ["Energy", "Chill", "Night", "Happy", "Introspective", "Excited"]
    },
    "Party": {
        "description": "Social celebration, dancing, festive energy",
        "valence": "positive",
        "energy": "very high",
        "connects_to": ["Happy", "Energy", "Romantic", "Night", "Playful", "Excited"]
    },
    "Angry": {
        "description": "Anger, rage, frustration, aggression",
        "valence": "negative",
        "energy": "high",
        "connects_to": ["Bitter", "Jealous", "Dark", "Energy", "Sad", "Chaotic"]
    },
    "Bitter": {
        "description": "Bitterness, resentment, betrayal",
        "valence": "negative",
        "energy": "medium",
        "connects_to": ["Sad", "Angry", "Dark", "Jealous"]
    },
    "Hopeful": {
        "description": "Hope, optimism, looking forward",
        "valence": "positive",
        "energy": "medium",
        "connects_to": ["Sad", "Happy", "Introspective", "Nostalgic", "Excited", "Grateful"]
    },
    "Excited": {
        "description": "Excitement, anticipation, adventure",
        "valence": "positive",
        "energy": "high",
        "connects_to": ["Happy", "Energy", "Party", "Hopeful", "Drive", "Anxious"]
    },
    "Jealous": {
        "description": "Jealousy, envy, insecurity",
        "valence": "negative",
        "energy": "medium-high",
        "connects_to": ["Angry", "Bitter", "Anxious", "Romantic", "Sad"]
    },
    "Peaceful": {
        "description": "Peace, serenity, tranquility",
        "valence": "positive",
        "energy": "very low",
        "connects_to": ["Chill", "Grateful", "Introspective", "Night"]
    },
    "Playful": {
        "description": "Playfulness, silliness, fun",
        "valence": "positive",
        "energy": "medium-high",
        "connects_to": ["Happy", "Party", "Excited", "Chaotic"]
    },
    "Chaotic": {
        "description": "Chaos, frantic energy, overwhelming",
        "valence": "negative-neutral",
        "energy": "very high",
        "connects_to": ["Anxious", "Angry", "Playful", "Bored"]
    },
    "Bored": {
        "description": "Boredom, restlessness, understimulation",
        "valence": "negative-neutral",
        "energy": "low",
        "connects_to": ["Anxious", "Chaotic", "Introspective"]
    },
    "Grateful": {
        "description": "Gratitude, appreciation, thankfulness",
        "valence": "positive",
        "energy": "low-medium",
        "connects_to": ["Happy", "Peaceful", "Chill", "Introspective", "Hopeful"]
    },
    "Confident": {
        "description": "Confidence, power, self-assurance",
        "valence": "positive",
        "energy": "high",
        "connects_to": ["Happy", "Energy", "Angry", "Dark"]
    }
}

# Save the map
output = {
    "central_vibes": central_vibe_map,
    "total_central_vibes": len(central_vibe_map),
    "mapping_complete": True
}

with open('ananki_outputs/central_vibe_relationships.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== CENTRAL VIBE RELATIONSHIPS MAPPED ===')
print(f'Total central vibes: {len(central_vibe_map)}')
print('\nConnections per vibe:')
for vibe, data in central_vibe_map.items():
    print(f'{vibe}: {len(data["connects_to"])} connections')

print('\nSaved to: ananki_outputs/central_vibe_relationships.json')
