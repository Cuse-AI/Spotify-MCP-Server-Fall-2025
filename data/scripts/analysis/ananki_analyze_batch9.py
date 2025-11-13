import json

# Ananki's emotional analysis for Batch 9: Excited + Hopeful + Jealous + Peaceful sub-vibes
batch9_analysis = {
    "Excited - Anticipation": {
        "emotional_composition": {
            "Excited": 0.70,
            "Anxious": 0.15,
            "Happy": 0.10,
            "Energy": 0.05
        },
        "analysis": "Captain Beefheart 'Electricity', electric energy vibes. Waiting for something good. Nervous excitement. Can't wait feeling. Building tension.",
        "proximity_notes": "Between Excited and Anxious/Happy. Anticipation = excited + slightly nervous + joyful waiting."
    },
    
    "Hopeful - Healing": {
        "emotional_composition": {
            "Hopeful": 0.65,
            "Sad": 0.20,
            "Introspective": 0.10,
            "Peaceful": 0.05
        },
        "analysis": "Pink Floyd 'Wish You Were Here', The National 'Sorrow', LCD Soundsystem. Recovery process. Moving through pain. Getting better. Still hurting but improving.",
        "proximity_notes": "Between Hopeful and Sad. Healing = hope emerging from sadness, transitional recovery."
    },
    
    "Hopeful - New Beginnings": {
        "emotional_composition": {
            "Hopeful": 0.70,
            "Excited": 0.15,
            "Happy": 0.10,
            "Anxious": 0.05
        },
        "analysis": "Porcupine Tree, Karnivool, My Bloody Valentine 'Loveless', Alcest. Fresh starts. Blank slates. Turning the page. Optimistic about change.",
        "proximity_notes": "Between Hopeful and Excited/Happy. New beginnings = hope + anticipation + slight nerves."
    },
    
    "Hopeful - Optimistic": {
        "emotional_composition": {
            "Hopeful": 0.75,
            "Happy": 0.20,
            "Grateful": 0.05
        },
        "analysis": "'Let the Day Begin' - The Call, 'Prayer of St Francis', Tears for Fears 'Sowing the Seeds of Love'. Bright outlook. Believing in good. Positive future vision.",
        "proximity_notes": "Between Hopeful and Happy. Optimistic = strong hope + happiness + faith in good outcomes."
    },
    
    "Jealous - Romantic Jealousy": {
        "emotional_composition": {
            "Jealous": 0.75,
            "Angry": 0.15,
            "Sad": 0.05,
            "Anxious": 0.05
        },
        "analysis": "'Run for Your Life' - Beatles, 'Jolene' - Dolly Parton, Nick Jonas 'Jealous'. Possessive love. Fear of losing partner. Green-eyed monster.",
        "proximity_notes": "Near Jealous center with Angry pull. Romantic jealousy = envy + anger + insecurity in love."
    },
    
    "Jealous - Envious": {
        "emotional_composition": {
            "Jealous": 0.80,
            "Sad": 0.10,
            "Bitter": 0.05,
            "Anxious": 0.05
        },
        "analysis": "'Creep' - Radiohead, 'Possession' - Sarah McLachlan. Wanting what others have. Feeling inadequate. Comparing yourself. Longing for their life.",
        "proximity_notes": "Very close to Jealous center. Envious = pure jealousy with sadness from lacking."
    },
    
    "Jealous - Insecure": {
        "emotional_composition": {
            "Jealous": 0.65,
            "Anxious": 0.20,
            "Sad": 0.15
        },
        "analysis": "Swans 'Failure', Linkin Park 'Numb', NF 'Let You Down'. Self-doubt and comparison. Worried about not measuring up. Feeling less-than.",
        "proximity_notes": "Between Jealous and Anxious/Sad. Insecure = jealousy rooted in self-doubt and worry."
    },
    
    "Jealous - Competitive": {
        "emotional_composition": {
            "Jealous": 0.60,
            "Angry": 0.20,
            "Confident": 0.15,
            "Energy": 0.05
        },
        "analysis": "Illenium tracks, upbeat competitive vibes. Wanting to win. Rivalry energy. Driven by envy. Using jealousy as fuel.",
        "proximity_notes": "Between Jealous and Angry/Confident. Competitive = jealousy channeled into drive and determination."
    },
    
    "Peaceful - Serene": {
        "emotional_composition": {
            "Peaceful": 0.85,
            "Chill": 0.10,
            "Grateful": 0.05
        },
        "analysis": "Oh Wonder 'Lonely Star', Deuter, Brian Eno, Coldplay 'Ghost Stories'. Complete calm. Stillness and clarity. Deep tranquility. Zen state.",
        "proximity_notes": "Very close to Peaceful center. Serene = pure peace, deep calm, undisturbed stillness."
    },
    
    "Peaceful - Meditative": {
        "emotional_composition": {
            "Peaceful": 0.80,
            "Introspective": 0.15,
            "Chill": 0.05
        },
        "analysis": "Karunesh 'Solitude', Alice in Chains 'Nutshell' (acoustic), Genesis 'Ripples', Pink Floyd 'Echoes'. Contemplative peace. Mindfulness. Inner quiet.",
        "proximity_notes": "Between Peaceful and Introspective. Meditative = peace + gentle contemplation, conscious calm."
    }
}

# Save Batch 9
output = {
    "batch": 9,
    "sub_vibes_analyzed": list(batch9_analysis.keys()),
    "total_in_batch": len(batch9_analysis),
    "analysis": batch9_analysis,
    "status": "Batch 9 complete - 90 of 114 sub-vibes analyzed (cumulative)"
}

with open('ananki_outputs/emotional_analysis_batch9.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 9 ===')
print(f'Analyzed: {len(batch9_analysis)} sub-vibes\n')

for subvibe, data in batch9_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Analysis: {data["analysis"][:80]}...\n')

print('Saved to: ananki_outputs/emotional_analysis_batch9.json')
print('Progress: 90/114 sub-vibes complete (78.9%)!')
print('\nReady for Batch 10!')
