import json

# Ananki's emotional analysis for Batch 11 (FINAL): Bored + Grateful + Confident sub-vibes
batch11_analysis = {
    "Bored - Restless": {
        "emotional_composition": {
            "Bored": 0.70,
            "Anxious": 0.20,
            "Energy": 0.10
        },
        "analysis": "Mastodon, Coal Chamber, Cypress Hill. Understimulated but agitated. Need something to do. Pacing energy. Can't settle but nothing appeals.",
        "proximity_notes": "Between Bored and Anxious/Energy. Restless = boredom + nervous energy, agitated understimulation."
    },
    
    "Bored - Understimulated": {
        "emotional_composition": {
            "Bored": 0.80,
            "Sad": 0.10,
            "Chill": 0.05,
            "Anxious": 0.05
        },
        "analysis": "Radiohead 'Everything In Its Right Place', Velvet Underground, ambient tracks. Brain not engaged. Empty feeling. Numb from lack of input.",
        "proximity_notes": "Very close to Bored center. Understimulated = pure boredom, empty understimulation."
    },
    
    "Bored - Waiting": {
        "emotional_composition": {
            "Bored": 0.65,
            "Anxious": 0.20,
            "Introspective": 0.10,
            "Peaceful": 0.05
        },
        "analysis": "Tommy Emmanuel, Genesis 'Horizons', Norah Jones 'Sunrise'. Stuck in limbo. Time dragging. Anticipation mixed with tedium. Impatient patience.",
        "proximity_notes": "Between Bored and Anxious. Waiting = boredom + anticipation, tedious impatience."
    },
    
    "Bored - Monotonous": {
        "emotional_composition": {
            "Bored": 0.75,
            "Sad": 0.15,
            "Dark": 0.10
        },
        "analysis": "The Frames, Vetusta Morla, Porcupine Tree 'Lightbulb Sun'. Repetitive grind. Same thing over and over. Draining sameness. Depression-adjacent.",
        "proximity_notes": "Between Bored and Sad/Dark. Monotonous = boredom with heaviness, draining repetition."
    },
    
    "Grateful - Thankful": {
        "emotional_composition": {
            "Grateful": 0.80,
            "Happy": 0.15,
            "Peaceful": 0.05
        },
        "analysis": "Grateful Dead 'Ripple', Elton John 'Tumbleweed Connection', The Meters. Appreciation and warmth. Counting blessings. Joy in gratitude.",
        "proximity_notes": "Very close to Grateful center. Thankful = pure gratitude, warm appreciation."
    },
    
    "Grateful - Content": {
        "emotional_composition": {
            "Grateful": 0.70,
            "Peaceful": 0.20,
            "Happy": 0.10
        },
        "analysis": "Polyphonic Spree 'Reach For the Sun', Brian Jonestown Massacre, Low, Smog 'Rock Bottom Riser'. Satisfied and settled. Enough is enough. Peaceful appreciation.",
        "proximity_notes": "Between Grateful and Peaceful. Content = gratitude + peace, satisfied stillness."
    },
    
    "Grateful - Reflective Gratitude": {
        "emotional_composition": {
            "Grateful": 0.70,
            "Introspective": 0.20,
            "Nostalgic": 0.05,
            "Happy": 0.05
        },
        "analysis": "Sharon Jones, Christmas songs, thoughtful appreciation music. Looking back with thanks. Realizing blessings. Contemplative appreciation.",
        "proximity_notes": "Between Grateful and Introspective. Reflective = gratitude + contemplation, thoughtful thanks."
    },
    
    "Grateful - Warm Appreciation": {
        "emotional_composition": {
            "Grateful": 0.75,
            "Happy": 0.15,
            "Romantic": 0.05,
            "Peaceful": 0.05
        },
        "analysis": "Chromatics, Cults 'Always Forever', Jidenna 'Bambi', Bon Iver. Affectionate gratitude. Appreciating people and moments. Love-adjacent thanks.",
        "proximity_notes": "Between Grateful and Happy/Romantic. Warm appreciation = gratitude with affection, loving thanks."
    },
    
    "Confident - Self-Assured": {
        "emotional_composition": {
            "Confident": 0.80,
            "Happy": 0.10,
            "Energy": 0.10
        },
        "analysis": "Sia 'Unstoppable', empowerment anthems. Knowing your worth. Secure in yourself. Unshakeable belief. Comfortable in skin.",
        "proximity_notes": "Very close to Confident center. Self-assured = pure confidence, secure self-belief."
    },
    
    "Confident - Powerful": {
        "emotional_composition": {
            "Confident": 0.75,
            "Energy": 0.15,
            "Dark": 0.05,
            "Angry": 0.05
        },
        "analysis": "The Protomen, The War on Drugs, The Waterboys. Force and strength. Commanding presence. Intensity of power. Dominant energy.",
        "proximity_notes": "Between Confident and Energy. Powerful = confidence + force, strength and dominance."
    },
    
    "Confident - Bold": {
        "emotional_composition": {
            "Confident": 0.75,
            "Energy": 0.15,
            "Excited": 0.05,
            "Playful": 0.05
        },
        "analysis": "Aram Khachaturian, Hot Milk, Jambinai. Daring and fearless. Taking risks. Unapologetic. Brave energy. Standing out.",
        "proximity_notes": "Between Confident and Energy/Excited. Bold = confidence + daring, fearless assertion."
    },
    
    "Confident - Victorious": {
        "emotional_composition": {
            "Confident": 0.70,
            "Happy": 0.20,
            "Excited": 0.05,
            "Grateful": 0.05
        },
        "analysis": "'Walking on Sunshine', 'You Make My Dreams Come True', Whitney Houston. Winner energy. Triumph and celebration. Achieved success. Peak confidence.",
        "proximity_notes": "Between Confident and Happy. Victorious = confidence + joy from winning, triumphant celebration."
    },
    
    "Confident - Unstoppable": {
        "emotional_composition": {
            "Confident": 0.80,
            "Energy": 0.15,
            "Angry": 0.05
        },
        "analysis": "Disturbed 'A Reason To Fight', Metallica, Johnny Cash 'I Won't Back Down'. Indomitable will. Cannot be stopped. Relentless determination.",
        "proximity_notes": "Between Confident and Energy/Angry. Unstoppable = fierce confidence, relentless power."
    },
    
    "Confident - Boss": {
        "emotional_composition": {
            "Confident": 0.75,
            "Dark": 0.10,
            "Energy": 0.10,
            "Happy": 0.05
        },
        "analysis": "Johnny Cash 'Ring of Fire', 'Ghost Riders', Lynyrd Skynyrd 'Freebird'. Command and authority. Leader energy. Take charge. Boss mode.",
        "proximity_notes": "Between Confident and Dark/Energy. Boss = commanding confidence, authoritative power."
    }
}

# Save Batch 11 (FINAL)
output = {
    "batch": 11,
    "sub_vibes_analyzed": list(batch11_analysis.keys()),
    "total_in_batch": len(batch11_analysis),
    "analysis": batch11_analysis,
    "status": "Batch 11 complete - ALL 114 SUB-VIBES ANALYZED! COMPLETE!"
}

with open('ananki_outputs/emotional_analysis_batch11_FINAL.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 11 (FINAL) ===')
print(f'Analyzed: {len(batch11_analysis)} sub-vibes\n')

for subvibe, data in batch11_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Analysis: {data["analysis"][:80]}...\n')

print('Saved to: ananki_outputs/emotional_analysis_batch11_FINAL.json')
print('\n' + '='*70)
print('🎉 COMPLETE! ALL 114 SUB-VIBES ANALYZED! 🎉')
print('='*70)
print('Progress: 114/114 sub-vibes complete (100%)')
print('\nReady to merge all batches into master file!')
