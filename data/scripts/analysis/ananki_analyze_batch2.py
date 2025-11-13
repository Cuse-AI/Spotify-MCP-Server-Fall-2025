import json

# Ananki's emotional analysis for Batch 2: Happy + Chill sub-vibes
batch2_analysis = {
    "Happy - Sunshine": {
        "emotional_composition": {
            "Happy": 0.75,
            "Energy": 0.15,
            "Playful": 0.10
        },
        "analysis": "Bright, uplifting happiness with bounce. 'All Right' by Kenny Loggins, Led Zeppelin - upbeat classic rock energy. Playful lightness. Optimistic warmth.",
        "proximity_notes": "Near Happy center with pull toward Energy and Playful. Sunshine = happy + energetic + light."
    },
    
    "Happy - Carefree": {
        "emotional_composition": {
            "Happy": 0.70,
            "Chill": 0.20,
            "Peaceful": 0.10
        },
        "analysis": "Relaxed, unburdened happiness. Ichiko Aoba's gentle folk vibes. Not energetic - more floating/easy. Freedom from worry.",
        "proximity_notes": "Between Happy and Chill. Carefree = contentment without tension. Gentle happiness."
    },
    
    "Chill - Morning Coffee": {
        "emotional_composition": {
            "Chill": 0.80,
            "Peaceful": 0.10,
            "Grateful": 0.10
        },
        "analysis": "Quiet start to the day. Thelonious Monk jazz, calm acoustic. Ritualistic comfort. Present and grounded. Gentle awakening energy.",
        "proximity_notes": "Close to Chill center with slight pull toward Peaceful and Grateful. Morning serenity."
    },
    
    "Chill - Rainy Day": {
        "emotional_composition": {
            "Chill": 0.70,
            "Sad": 0.15,
            "Introspective": 0.15
        },
        "analysis": "Cozy melancholy. Rain = gentle sadness + introspection. Billie Eilish, Hozier - moody but not heavy. Comfort in the grey.",
        "proximity_notes": "Between Chill and Sad/Introspective. Rain brings contemplative mood without depression."
    },
    
    "Chill - Beach/Summer": {
        "emotional_composition": {
            "Chill": 0.75,
            "Happy": 0.20,
            "Nostalgic": 0.05
        },
        "analysis": "Warm, lazy relaxation. Summer ease and sunshine. Happy without being energetic. Nostalgic summer memory quality.",
        "proximity_notes": "Between Chill and Happy. Beach vibes = relaxed happiness, vacation mode."
    },
    
    "Chill - Evening": {
        "emotional_composition": {
            "Chill": 0.75,
            "Night": 0.15,
            "Introspective": 0.10
        },
        "analysis": "Winding down. Jazz standards (Miles Davis, Count Basie). Transition to night. Reflective but not heavy. Gentle dimming.",
        "proximity_notes": "Between Chill and Night. Evening = still awake but settling, contemplative relaxation."
    },
    
    "Chill - Sunday": {
        "emotional_composition": {
            "Chill": 0.80,
            "Nostalgic": 0.10,
            "Peaceful": 0.10
        },
        "analysis": "Slow weekend morning. Depeche Mode, Peter Gabriel - 80s reflective vibes. No urgency. Savoring stillness. Sacred rest.",
        "proximity_notes": "Near Chill center with nostalgic quality. Sunday = intentional slowness, weekly ritual."
    },
    
    "Chill - Lofi": {
        "emotional_composition": {
            "Chill": 0.75,
            "Introspective": 0.15,
            "Night": 0.10
        },
        "analysis": "Study/focus ambient. Boards of Canada, Cocteau Twins. Dreamy, hazy. Background consciousness. Slight melancholy.",
        "proximity_notes": "Between Chill and Introspective/Night. Lofi = ambient thought space, contemplative calm."
    },
    
    "Chill - Jazz": {
        "emotional_composition": {
            "Chill": 0.70,
            "Introspective": 0.15,
            "Romantic": 0.10,
            "Night": 0.05
        },
        "analysis": "Sophisticated relaxation. Jazz standards create intimate, thoughtful atmosphere. Late night café vibes. Romantic undertone.",
        "proximity_notes": "Chill center pulled toward Introspective and Romantic. Jazz = cultured calm with emotional depth."
    },
    
    "Chill - Ambient": {
        "emotional_composition": {
            "Chill": 0.65,
            "Peaceful": 0.20,
            "Introspective": 0.10,
            "Dark": 0.05
        },
        "analysis": "Pure atmospheric sound. Jean Michel Jarre, Animal Collective. Spacious, ethereal. Meditation quality. Can touch slightly dark/experimental.",
        "proximity_notes": "Between Chill and Peaceful with introspective edge. Ambient = consciousness without thought."
    }
}

# Save Batch 2
output = {
    "batch": 2,
    "sub_vibes_analyzed": list(batch2_analysis.keys()),
    "total_in_batch": len(batch2_analysis),
    "analysis": batch2_analysis,
    "status": "Batch 2 complete - 20 of 114 sub-vibes analyzed (cumulative)"
}

with open('ananki_outputs/emotional_analysis_batch2.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 2 ===')
print(f'Analyzed: {len(batch2_analysis)} sub-vibes\n')

for subvibe, data in batch2_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Analysis: {data["analysis"][:80]}...\n')

print('Saved to: ananki_outputs/emotional_analysis_batch2.json')
print('Progress: 20/114 sub-vibes complete!')
print('\nReady for Batch 3!')
