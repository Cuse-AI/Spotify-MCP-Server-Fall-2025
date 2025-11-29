import json

# Ananki's emotional analysis for Batch 6: Dark + Introspective sub-vibes
batch6_analysis = {
    "Dark - Brooding": {
        "emotional_composition": {
            "Dark": 0.70,
            "Introspective": 0.20,
            "Anxious": 0.10
        },
        "analysis": "Kraftwerk 'Radioactivity', Portishead 'Dummy', Kiki Rockwell. Moody and heavy. Storm cloud energy. Dwelling in shadow. Internal tension.",
        "proximity_notes": "Between Dark and Introspective. Brooding = darkness + deep thought + worried edge."
    },
    
    "Dark - Haunting": {
        "emotional_composition": {
            "Dark": 0.75,
            "Sad": 0.15,
            "Introspective": 0.10
        },
        "analysis": "Hendrix 'All Along the Watchtower', Jeff Buckley 'Hallelujah', Soft Cell 'Tainted Love'. Eerie beauty. Ghost-like quality. Melancholic darkness.",
        "proximity_notes": "Near Dark center with Sad pull. Haunting = darkness with emotional weight, spectral sadness."
    },
    
    "Dark - Noir": {
        "emotional_composition": {
            "Dark": 0.70,
            "Night": 0.15,
            "Introspective": 0.10,
            "Romantic": 0.05
        },
        "analysis": "Black Sabbath vibes, La Femme. Detective movie soundtrack energy. Urban shadows. Mystery and danger. Stylized darkness.",
        "proximity_notes": "Between Dark and Night. Noir = cinematic darkness, nocturnal mystery, dangerous romance."
    },
    
    "Dark - Witchy": {
        "emotional_composition": {
            "Dark": 0.70,
            "Romantic": 0.15,
            "Introspective": 0.10,
            "Playful": 0.05
        },
        "analysis": "Fleetwood Mac 'Rhiannon', Stevie Nicks 'Sorcerer', Heilung, Wardruna. Mystical and powerful. Pagan energy. Feminine darkness. Magic and ritual.",
        "proximity_notes": "Dark pulled toward Romantic and slightly Playful. Witchy = mystical darkness, enchanted power."
    },
    
    "Dark - Villain Arc": {
        "emotional_composition": {
            "Dark": 0.65,
            "Angry": 0.20,
            "Confident": 0.15
        },
        "analysis": "Oceano, PJ Harvey 'This Wicked Tongue', Garbage 'Hammering'. Embracing the shadow. Power in darkness. Unapologetic edge. Anti-hero energy.",
        "proximity_notes": "Between Dark and Angry/Confident. Villain arc = darkness + rage + powerful self-assertion."
    },
    
    "Dark - Apocalyptic": {
        "emotional_composition": {
            "Dark": 0.80,
            "Anxious": 0.10,
            "Sad": 0.05,
            "Chaotic": 0.05
        },
        "analysis": "Mayhem, Axis of Perdition. End-times energy. Dread and doom. Heavy and overwhelming. World-ending atmosphere. Existential darkness.",
        "proximity_notes": "Very close to Dark center. Apocalyptic = intense darkness with dread, overwhelming shadow."
    },
    
    "Introspective - Philosophical": {
        "emotional_composition": {
            "Introspective": 0.75,
            "Sad": 0.10,
            "Dark": 0.10,
            "Chill": 0.05
        },
        "analysis": "Mozart 'Requiem', Rush 'La Villa Strangiato', Elliott Smith. Deep existential questioning. Life's big questions. Contemplating meaning and mortality.",
        "proximity_notes": "Near Introspective center with Sad/Dark touches. Philosophical = deep thought + existential weight."
    },
    
    "Introspective - Self-Reflection": {
        "emotional_composition": {
            "Introspective": 0.80,
            "Sad": 0.10,
            "Chill": 0.10
        },
        "analysis": "Japanese artists - Uru, Ado, Yoshino. Personal examination. Looking inward. Understanding yourself. Processing experiences. Inner journey.",
        "proximity_notes": "Very close to Introspective center. Self-reflection = pure internal focus, personal processing."
    },
    
    "Introspective - Contemplative": {
        "emotional_composition": {
            "Introspective": 0.75,
            "Sad": 0.15,
            "Night": 0.10
        },
        "analysis": "'Chasing Cars', Radiohead 'How to disappear completely', Tool 'Lateralus'. Quiet thinking. Stillness and wonder. Pondering without urgency.",
        "proximity_notes": "Between Introspective and Sad/Night. Contemplative = gentle deep thought, reflective mood."
    },
    
    "Introspective - Life Changes": {
        "emotional_composition": {
            "Introspective": 0.65,
            "Anxious": 0.15,
            "Hopeful": 0.10,
            "Sad": 0.10
        },
        "analysis": "Sisters of Mercy, The Cure 'Staring', Depeche Mode 'Violator', Postal Service. Processing transitions. Uncertainty and growth. Mixed emotions of change.",
        "proximity_notes": "Introspective pulled toward Anxious/Hopeful/Sad. Life changes = reflection + uncertainty + hope + loss."
    }
}

# Save Batch 6
output = {
    "batch": 6,
    "sub_vibes_analyzed": list(batch6_analysis.keys()),
    "total_in_batch": len(batch6_analysis),
    "analysis": batch6_analysis,
    "status": "Batch 6 complete - 60 of 114 sub-vibes analyzed (cumulative)"
}

with open('ananki_outputs/emotional_analysis_batch6.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 6 ===')
print(f'Analyzed: {len(batch6_analysis)} sub-vibes\n')

for subvibe, data in batch6_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Analysis: {data["analysis"][:80]}...\n')

print('Saved to: ananki_outputs/emotional_analysis_batch6.json')
print('Progress: 60/114 sub-vibes complete (52.6%)!')
print('\nReady for Batch 7!')
