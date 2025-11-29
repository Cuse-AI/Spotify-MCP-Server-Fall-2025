import json

# Ananki's emotional analysis for Batch 10: Peaceful + Playful + Chaotic sub-vibes
batch10_analysis = {
    "Peaceful - Quiet Reflection": {
        "emotional_composition": {
            "Peaceful": 0.70,
            "Introspective": 0.20,
            "Sad": 0.05,
            "Chill": 0.05
        },
        "analysis": "Kings of Convenience 'Gold in the Air', Muse 'Unintended', T.Swift 'Peace'. Gentle pondering. Soft contemplation. Peaceful thought.",
        "proximity_notes": "Between Peaceful and Introspective. Quiet reflection = peace + gentle thought, calm processing."
    },
    
    "Peaceful - Gentle": {
        "emotional_composition": {
            "Peaceful": 0.75,
            "Chill": 0.15,
            "Happy": 0.05,
            "Grateful": 0.05
        },
        "analysis": "Mars Volta acoustic moments, TAUK, Elbow 'AUDIO VERTIGO'. Soft and kind. Tender energy. Delicate and warm. Nurturing peace.",
        "proximity_notes": "Near Peaceful center with Chill. Gentle = soft peace, tender calm, nurturing stillness."
    },
    
    "Playful - Silly": {
        "emotional_composition": {
            "Playful": 0.85,
            "Happy": 0.10,
            "Party": 0.05
        },
        "analysis": "Chuck Berry 'My Ding-a-Ling', They Might Be Giants 'We Want A Rock', 'The Loophole', novelty songs. Pure goofiness. Not taking seriously. Comedy music.",
        "proximity_notes": "Very close to Playful center. Silly = pure playfulness, maximum goofiness, comedic fun."
    },
    
    "Playful - Whimsical": {
        "emotional_composition": {
            "Playful": 0.75,
            "Happy": 0.15,
            "Introspective": 0.05,
            "Peaceful": 0.05
        },
        "analysis": "Plaid 'Tearisci', Devin Townsend experimental, Kurt Vile. Quirky and imaginative. Light but creative. Fantastical and odd. Dreamy playfulness.",
        "proximity_notes": "Near Playful center with Happy. Whimsical = creative playfulness, imaginative lightness."
    },
    
    "Playful - Fun": {
        "emotional_composition": {
            "Playful": 0.70,
            "Happy": 0.20,
            "Party": 0.10
        },
        "analysis": "Twenty One Pilots 'Shy Away', BabyMetal 'Gimme Chocolate', Madness, Bad Manners, Little Big 'Skibidi'. Energetic good times. Upbeat joy. Party-adjacent fun.",
        "proximity_notes": "Between Playful and Happy/Party. Fun = joyful playfulness, energetic celebration."
    },
    
    "Playful - Childlike": {
        "emotional_composition": {
            "Playful": 0.65,
            "Nostalgic": 0.20,
            "Happy": 0.10,
            "Peaceful": 0.05
        },
        "analysis": "Dire Straits 'Money for Nothing', Phil Collins 'In the Air Tonight', Ravel 'Bolero'. Innocent wonder. Simple joy. Rediscovering play. Youth energy.",
        "proximity_notes": "Between Playful and Nostalgic. Childlike = playfulness + innocent nostalgia, wonder reclaimed."
    },
    
    "Chaotic - Frantic": {
        "emotional_composition": {
            "Chaotic": 0.80,
            "Anxious": 0.15,
            "Energy": 0.05
        },
        "analysis": "Experimental electronic, Biosphere, Dungen. Scattered and rushing. Can't keep up. Everything at once. Overwhelming pace.",
        "proximity_notes": "Very close to Chaotic center. Frantic = pure chaos, overwhelming scattered energy."
    },
    
    "Chaotic - Overwhelming": {
        "emotional_composition": {
            "Chaotic": 0.75,
            "Anxious": 0.15,
            "Sad": 0.05,
            "Dark": 0.05
        },
        "analysis": "Marcus King, Peter Gabriel 'Intruder', experimental intensity. Too much stimulus. Sensory overload. Drowning in chaos. Heavy overwhelm.",
        "proximity_notes": "Near Chaotic center with Anxious. Overwhelming = chaos + anxiety, crushing intensity."
    },
    
    "Chaotic - Unhinged": {
        "emotional_composition": {
            "Chaotic": 0.70,
            "Dark": 0.15,
            "Angry": 0.10,
            "Playful": 0.05
        },
        "analysis": "Gunship & Health, GosT 'Supreme', darkwave synthwave. Out of control. Wild and dangerous. Unstable energy. Madness edge.",
        "proximity_notes": "Between Chaotic and Dark/Angry. Unhinged = chaos + darkness + rage, dangerous instability."
    },
    
    "Chaotic - Scattered": {
        "emotional_composition": {
            "Chaotic": 0.75,
            "Anxious": 0.15,
            "Bored": 0.10
        },
        "analysis": "Experimental tracks, Lemaitre, Godsmack. Can't focus. Mind all over. Distracted and disjointed. Lost in noise.",
        "proximity_notes": "Between Chaotic and Anxious/Bored. Scattered = chaos + distraction, unfocused overwhelm."
    }
}

# Save Batch 10
output = {
    "batch": 10,
    "sub_vibes_analyzed": list(batch10_analysis.keys()),
    "total_in_batch": len(batch10_analysis),
    "analysis": batch10_analysis,
    "status": "Batch 10 complete - 100 of 114 sub-vibes analyzed (cumulative)"
}

with open('ananki_outputs/emotional_analysis_batch10.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 10 ===')
print(f'Analyzed: {len(batch10_analysis)} sub-vibes\n')

for subvibe, data in batch10_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Analysis: {data["analysis"][:80]}...\n')

print('Saved to: ananki_outputs/emotional_analysis_batch10.json')
print('Progress: 100/114 sub-vibes complete (87.7%)!')
print('\nReady for FINAL Batch 11!')
