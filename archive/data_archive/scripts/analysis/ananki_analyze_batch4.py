import json

# Ananki's emotional analysis for Batch 4: Drive + Party sub-vibes
batch4_analysis = {
    "Drive - Road Trip": {
        "emotional_composition": {
            "Drive": 0.70,
            "Happy": 0.15,
            "Excited": 0.10,
            "Nostalgic": 0.05
        },
        "analysis": "Adventure and freedom! Chris Rea 'On The Beach', Yellowcard 'Ocean Avenue', MGMT. Open road energy. Positive journey vibes. Discovery and exploration.",
        "proximity_notes": "Drive center pulled toward Happy and Excited. Road trip = movement + joy + anticipation."
    },
    
    "Drive - Night Drive": {
        "emotional_composition": {
            "Drive": 0.60,
            "Night": 0.30,
            "Introspective": 0.10
        },
        "analysis": "Nocturnal movement. New Order, Bauhaus, Stone Roses. Moody driving. Reflective but kinetic. Headlights cutting through darkness. Solitary momentum.",
        "proximity_notes": "Between Drive and Night. Night drive = nocturnal journey, contemplative motion."
    },
    
    "Drive - City": {
        "emotional_composition": {
            "Drive": 0.70,
            "Energy": 0.20,
            "Night": 0.10
        },
        "analysis": "Urban navigation. Faster pace, more stimulation. City lights and traffic. Alert and engaged. Soundtrack to concrete jungle.",
        "proximity_notes": "Drive pulled toward Energy and Night. City driving = energetic navigation, urban intensity."
    },
    
    "Drive - Speed": {
        "emotional_composition": {
            "Drive": 0.65,
            "Energy": 0.25,
            "Excited": 0.10
        },
        "analysis": "'Radar Love', 'Highway Star' - Deep Purple, 'Barracuda'. Pure velocity. Adrenaline rush. Pedal to the metal. Exhilaration of going fast.",
        "proximity_notes": "Between Drive and Energy. Speed = intense driving, adrenaline-fueled movement."
    },
    
    "Drive - Scenic": {
        "emotional_composition": {
            "Drive": 0.65,
            "Chill": 0.20,
            "Happy": 0.10,
            "Peaceful": 0.05
        },
        "analysis": "Leisurely cruising. Beautiful views. George Clinton, relaxed funk. Not rushing. Enjoying the journey. Windows down, taking it in.",
        "proximity_notes": "Between Drive and Chill/Happy. Scenic drive = relaxed movement, appreciative travel."
    },
    
    "Drive - Alone": {
        "emotional_composition": {
            "Drive": 0.60,
            "Introspective": 0.25,
            "Sad": 0.10,
            "Night": 0.05
        },
        "analysis": "'Nutshell', Temple of the Dog, Mount Eerie. Solitary reflection while moving. Processing emotions through motion. Therapeutic driving. Slight melancholy.",
        "proximity_notes": "Between Drive and Introspective/Sad. Alone = driving as meditation, movement through feelings."
    },
    
    "Party - Pregame": {
        "emotional_composition": {
            "Party": 0.70,
            "Energy": 0.20,
            "Excited": 0.10
        },
        "analysis": "Building anticipation! Getting hyped before going out. High energy prep. Dropkick Murphys, punk rock intensity. The ramp-up phase.",
        "proximity_notes": "Party pulled toward Energy and Excited. Pregame = building party energy, anticipatory hype."
    },
    
    "Party - Club": {
        "emotional_composition": {
            "Party": 0.75,
            "Energy": 0.15,
            "Dark": 0.05,
            "Romantic": 0.05
        },
        "analysis": "Electronic dance beats. 'Across 110th Street', Marvin Gaye. Club atmosphere - pulsing bass, dim lights. Social energy. Nightclub vibe.",
        "proximity_notes": "Near Party center with Energy. Club = concentrated party energy, electronic social space."
    },
    
    "Party - House Party": {
        "emotional_composition": {
            "Party": 0.70,
            "Happy": 0.20,
            "Playful": 0.10
        },
        "analysis": "Cage the Elephant, Maroon 5, Lady Gaga. More intimate than club. Friends and fun. Casual celebration. Mix of genres. Everyone's vibing.",
        "proximity_notes": "Between Party and Happy. House party = social happiness, relaxed celebration with friends."
    },
    
    "Party - Festival": {
        "emotional_composition": {
            "Party": 0.65,
            "Happy": 0.20,
            "Excited": 0.10,
            "Energy": 0.05
        },
        "analysis": "Trans-Siberian Orchestra, Bruno Mars. Massive crowd energy. Communal celebration. Euphoric shared experience. Peak moments.",
        "proximity_notes": "Party pulled toward Happy and Excited. Festival = collective joy, epic celebration energy."
    }
}

# Save Batch 4
output = {
    "batch": 4,
    "sub_vibes_analyzed": list(batch4_analysis.keys()),
    "total_in_batch": len(batch4_analysis),
    "analysis": batch4_analysis,
    "status": "Batch 4 complete - 40 of 114 sub-vibes analyzed (cumulative)"
}

with open('ananki_outputs/emotional_analysis_batch4.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 4 ===')
print(f'Analyzed: {len(batch4_analysis)} sub-vibes\n')

for subvibe, data in batch4_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Analysis: {data["analysis"][:80]}...\n')

print('Saved to: ananki_outputs/emotional_analysis_batch4.json')
print('Progress: 40/114 sub-vibes complete (35.1%)!')
print('\nReady for Batch 5!')
