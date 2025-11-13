import json

# Ananki's emotional analysis for Batch 3: Night + Energy sub-vibes
batch3_analysis = {
    "Night - 3AM Thoughts": {
        "emotional_composition": {
            "Night": 0.60,
            "Introspective": 0.25,
            "Sad": 0.10,
            "Anxious": 0.05
        },
        "analysis": "Deep existential contemplation. 'Nutshell', 'Say Hello to Heaven' - heavy emotional processing. Vulnerability of late night. Mind won't stop. Slight anxiety and melancholy.",
        "proximity_notes": "Between Night and Introspective with Sad pull. 3AM = when defenses are down, raw thoughts emerge."
    },
    
    "Night - Midnight Drive": {
        "emotional_composition": {
            "Night": 0.65,
            "Drive": 0.25,
            "Introspective": 0.10
        },
        "analysis": "Movement through darkness. Contemplative but active. Solitary journey. Van Morrison, Orville Peck. Freedom and reflection combined.",
        "proximity_notes": "Between Night and Drive. Midnight drive = nocturnal + movement, active contemplation."
    },
    
    "Night - Sleep": {
        "emotional_composition": {
            "Night": 0.60,
            "Chill": 0.25,
            "Peaceful": 0.15
        },
        "analysis": "Winding down to rest. Arctic Monkeys 'Only Ones Who Know', Death Cab. Gentle, soothing. Releasing the day. Calm preparation for sleep.",
        "proximity_notes": "Between Night, Chill, and Peaceful. Sleep music = nocturnal calm, restorative stillness."
    },
    
    "Night - Contemplative": {
        "emotional_composition": {
            "Night": 0.55,
            "Introspective": 0.35,
            "Sad": 0.10
        },
        "analysis": "'Chasing Cars', Radiohead 'How to disappear completely'. Deep thought during darkness. Questioning and wondering. Slight melancholy of night reflection.",
        "proximity_notes": "Halfway between Night and Introspective. Night amplifies contemplation, makes it heavier."
    },
    
    "Night - City Nights": {
        "emotional_composition": {
            "Night": 0.60,
            "Energy": 0.20,
            "Party": 0.10,
            "Dark": 0.10
        },
        "analysis": "Urban nocturnal energy. Dance music, UK chart hits. Neon lights and movement. Slightly edgy/mysterious. City never sleeps vibe.",
        "proximity_notes": "Night pulled toward Energy and Party. City nights = nocturnal + social + electric atmosphere."
    },
    
    "Energy - Workout": {
        "emotional_composition": {
            "Energy": 0.85,
            "Confident": 0.10,
            "Angry": 0.05
        },
        "analysis": "'Till I Collapse' - Eminem, 'Maniac'. Pure physical motivation. Push harder. Aggressive determination. Channeled intensity.",
        "proximity_notes": "Very close to Energy center. Workout = focused physical power, slight aggressive edge for push."
    },
    
    "Energy - Pump Up": {
        "emotional_composition": {
            "Energy": 0.75,
            "Happy": 0.15,
            "Party": 0.10
        },
        "analysis": "90s eurodance! 'Rhythm of the Night', 'Beautiful Life', Ace of Base. Positive high energy. Celebration energy. Pure hype.",
        "proximity_notes": "Between Energy and Happy/Party. Pump up = energetic joy, motivational positivity."
    },
    
    "Energy - Confidence": {
        "emotional_composition": {
            "Energy": 0.60,
            "Confident": 0.35,
            "Happy": 0.05
        },
        "analysis": "'Unstoppable' by Sia, empowerment anthems. Self-assured power. Bold energy. Feeling capable and strong. Motivational swagger.",
        "proximity_notes": "Between Energy and Confident. Confidence boost = energized self-assurance."
    },
    
    "Energy - Running": {
        "emotional_composition": {
            "Energy": 0.80,
            "Drive": 0.15,
            "Excited": 0.05
        },
        "analysis": "Jimi Hendrix, Black Sabbath, Rush. Sustained momentum. Forward motion. Racing energy. Rhythmic propulsion.",
        "proximity_notes": "Near Energy center with Drive pull. Running = continuous energetic movement, rhythmic power."
    },
    
    "Energy - Sports": {
        "emotional_composition": {
            "Energy": 0.75,
            "Confident": 0.15,
            "Angry": 0.10
        },
        "analysis": "Rammstein 'Du Hast', Def Leppard, Mötley Crüe. Aggressive competitive energy. Game face. Bring the intensity. Victory mindset.",
        "proximity_notes": "Energy pulled toward Confident and Angry. Sports = competitive aggression, powered confidence."
    }
}

# Save Batch 3
output = {
    "batch": 3,
    "sub_vibes_analyzed": list(batch3_analysis.keys()),
    "total_in_batch": len(batch3_analysis),
    "analysis": batch3_analysis,
    "status": "Batch 3 complete - 30 of 114 sub-vibes analyzed (cumulative)"
}

with open('ananki_outputs/emotional_analysis_batch3.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 3 ===')
print(f'Analyzed: {len(batch3_analysis)} sub-vibes\n')

for subvibe, data in batch3_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Analysis: {data["analysis"][:80]}...\n')

print('Saved to: ananki_outputs/emotional_analysis_batch3.json')
print('Progress: 30/114 sub-vibes complete (26.3%)!')
print('\nReady for Batch 4!')
