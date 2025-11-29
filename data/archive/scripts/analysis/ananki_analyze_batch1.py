import json

# Load necessary data
with open('ananki_outputs/tapestry_complete.json', encoding='utf-8') as f:
    tapestry_data = json.load(f)

with open('ananki_outputs/vibe_coordinates.json', encoding='utf-8') as f:
    coord_data = json.load(f)

vibes = tapestry_data['vibes']
central_positions = coord_data['central_vibe_positions']

# Ananki's emotional analysis for Batch 1: Sad sub-vibes
batch1_analysis = {
    "Sad - Heartbreak": {
        "emotional_composition": {
            "Sad": 0.70,
            "Bitter": 0.15,
            "Romantic": 0.10,
            "Angry": 0.05
        },
        "analysis": "Heartbreak sits at the painful intersection of sadness and lost love. Strong bitter/resentful component from feeling hurt. Slight anger at situation or person.",
        "proximity_notes": "Orbits Sad center but pulled significantly toward Bitter and Romantic. More complex than pure sadness."
    },
    
    "Sad - Crying": {
        "emotional_composition": {
            "Sad": 0.90,
            "Introspective": 0.05,
            "Chill": 0.05
        },
        "analysis": "Nearly pure sadness with cathartic release. Songs like 'Nutshell' and 'Cat In The Cradle' are deeply melancholic. Slight introspective quality from reflecting on what caused tears.",
        "proximity_notes": "Very close to Sad center. Minimal pull toward other vibes. This is concentrated grief/sorrow."
    },
    
    "Sad - Lonely": {
        "emotional_composition": {
            "Sad": 0.70,
            "Anxious": 0.20,
            "Introspective": 0.10
        },
        "analysis": "Loneliness combines sadness with anxious isolation. The anxiety of being alone creates nervous energy. Introspective because isolation forces self-reflection.",
        "proximity_notes": "Orbits Sad but pulled notably toward Anxious. Loneliness has a worried, restless quality beyond pure sadness."
    },
    
    "Sad - Melancholic": {
        "emotional_composition": {
            "Sad": 0.65,
            "Introspective": 0.25,
            "Nostalgic": 0.10
        },
        "analysis": "Melancholy is contemplative sadness. Classical pieces (Debussy, Rachmaninoff) suggest deep reflection. Not acute pain but lingering sorrow. Nostalgic quality of dwelling on past.",
        "proximity_notes": "Between Sad and Introspective. More thoughtful than raw emotional pain. Gentle rather than sharp sadness."
    },
    
    "Sad - Grief": {
        "emotional_composition": {
            "Sad": 0.85,
            "Dark": 0.10,
            "Introspective": 0.05
        },
        "analysis": "Heavy, profound loss. Songs about death and permanent absence. Darker than regular sadness - touches on mortality and void. Some processing/reflection but overwhelmingly sorrowful.",
        "proximity_notes": "Close to Sad center with pull toward Dark. Grief has weight and shadow that goes beyond typical sadness."
    },
    
    "Sad - Depressive": {
        "emotional_composition": {
            "Sad": 0.80,
            "Dark": 0.10,
            "Anxious": 0.05,
            "Bored": 0.05
        },
        "analysis": "Heavy, lingering sadness with numbness. 'Hurt' by Johnny Cash captures devastating emptiness. Darker than melancholy - touches despair. Slight anxious quality and emotional flatness.",
        "proximity_notes": "Near Sad center but pulled toward Dark and slightly toward Bored (emotional numbness/emptiness)."
    },
    
    "Sad - Nostalgic Sad": {
        "emotional_composition": {
            "Sad": 0.55,
            "Nostalgic": 0.35,
            "Introspective": 0.10
        },
        "analysis": "Bittersweet longing for the past. Equal parts sadness and nostalgia - missing what was. Reflective quality of looking backward. Gentler than pure grief.",
        "proximity_notes": "Halfway between Sad and Nostalgic. Strong pull in both directions. This is where two emotions truly blend."
    },
    
    "Happy - Euphoric": {
        "emotional_composition": {
            "Happy": 0.80,
            "Energy": 0.15,
            "Excited": 0.05
        },
        "analysis": "Peak happiness with high energy. 'Bulletproof' and intense upbeat tracks. Not just contentment but explosive joy. Energetic celebration.",
        "proximity_notes": "Near Happy center but pulled toward Energy. Euphoria has momentum and intensity beyond calm happiness."
    },
    
    "Happy - Feel Good": {
        "emotional_composition": {
            "Happy": 0.85,
            "Chill": 0.10,
            "Grateful": 0.05
        },
        "analysis": "Classic positive vibes. 'Lovely Day' captures comfortable, warm happiness. Not intense - sustainable good mood. Grateful/content quality.",
        "proximity_notes": "Close to Happy center with gentle pull toward Chill and Grateful. Relaxed happiness, not manic."
    },
    
    "Happy - Celebration": {
        "emotional_composition": {
            "Happy": 0.70,
            "Party": 0.20,
            "Energy": 0.10
        },
        "analysis": "Social, event-based happiness. Made for gatherings and milestones. Higher energy than feel-good, more outward-focused. Party energy channeled into joy.",
        "proximity_notes": "Between Happy and Party, pulled toward Energy. Celebration is happy + social + energetic."
    }
}

# Save Batch 1
output = {
    "batch": 1,
    "sub_vibes_analyzed": list(batch1_analysis.keys()),
    "total_in_batch": len(batch1_analysis),
    "analysis": batch1_analysis,
    "status": "Batch 1 complete - 10 of 114 sub-vibes analyzed"
}

with open('ananki_outputs/emotional_analysis_batch1.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 1 ===')
print(f'Analyzed: {len(batch1_analysis)} sub-vibes\n')

for subvibe, data in batch1_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Note: {data["proximity_notes"]}\n')

print('Saved to: ananki_outputs/emotional_analysis_batch1.json')
print('\nReady for Batch 2!')
