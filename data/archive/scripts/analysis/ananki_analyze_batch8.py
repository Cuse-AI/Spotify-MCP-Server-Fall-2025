import json

# Ananki's emotional analysis for Batch 8: Nostalgic + Angry + Bitter + Excited sub-vibes
batch8_analysis = {
    "Nostalgic - 90s": {
        "emotional_composition": {
            "Nostalgic": 0.80,
            "Happy": 0.15,
            "Playful": 0.05
        },
        "analysis": "New Radicals, Toad the Wet Sprocket, Sublime, RHCP 'Aeroplane', Foo Fighters. Specific decade longing. Alt-rock memories. MTV generation. Grunge and optimism.",
        "proximity_notes": "Near Nostalgic center with Happy pull. 90s = specific era memory, upbeat nostalgia."
    },
    
    "Nostalgic - 2000s": {
        "emotional_composition": {
            "Nostalgic": 0.75,
            "Happy": 0.15,
            "Sad": 0.10
        },
        "analysis": "Manic Street Preachers, The Script, Foo Fighters, Sugarcult. Y2K memories. Pop-punk and post-grunge. Coming of age in new millennium.",
        "proximity_notes": "Near Nostalgic center between Happy and Sad. 2000s = recent era nostalgia, bittersweet."
    },
    
    "Nostalgic - Simpler Times": {
        "emotional_composition": {
            "Nostalgic": 0.70,
            "Sad": 0.15,
            "Peaceful": 0.10,
            "Grateful": 0.05
        },
        "analysis": "Beastie Boys 'Sabotage', Genesis, Aphex Twin, Chemical Brothers, Primus. Longing for less complexity. When life felt easier. Wishing to go back.",
        "proximity_notes": "Between Nostalgic and Sad/Peaceful. Simpler times = yearning nostalgia, loss of innocence."
    },
    
    "Angry - Rage": {
        "emotional_composition": {
            "Angry": 0.90,
            "Dark": 0.05,
            "Chaotic": 0.05
        },
        "analysis": "Fit for an Autopsy, The Acacia Strain, deathcore intensity. Pure fury. Uncontrolled anger. Screaming energy. Maximum aggression.",
        "proximity_notes": "Very close to Angry center. Rage = pure concentrated anger at peak intensity."
    },
    
    "Angry - Frustrated": {
        "emotional_composition": {
            "Angry": 0.70,
            "Sad": 0.15,
            "Anxious": 0.10,
            "Bitter": 0.05
        },
        "analysis": "Pearl Jam 'Black', Derek and the Dominos 'Layla', Type O Negative. Blocked and stuck. Helpless anger. Things not working. Irritation with sadness.",
        "proximity_notes": "Between Angry and Sad/Anxious. Frustration = anger + helplessness + worry."
    },
    
    "Angry - Aggressive": {
        "emotional_composition": {
            "Angry": 0.85,
            "Energy": 0.10,
            "Dark": 0.05
        },
        "analysis": "Methwitch, Brand of Sacrifice, Terrorizer, Napalm Death. Outward hostility. Attack mode. Confrontational. Physical anger energy.",
        "proximity_notes": "Very close to Angry center with Energy. Aggressive = focused directed anger, combative."
    },
    
    "Angry - Cathartic Anger": {
        "emotional_composition": {
            "Angry": 0.65,
            "Sad": 0.20,
            "Introspective": 0.10,
            "Hopeful": 0.05
        },
        "analysis": "Pink Floyd 'Wish You Were Here', Genesis 'No Reply At All', Aphrodite's Child. Releasing anger healthily. Processing through rage. Therapeutic fury.",
        "proximity_notes": "Between Angry and Sad/Introspective. Cathartic = anger as release, healing rage."
    },
    
    "Bitter - Resentful": {
        "emotional_composition": {
            "Bitter": 0.75,
            "Angry": 0.15,
            "Sad": 0.10
        },
        "analysis": "MEGA DRIVE, Pendulum, The Divine Comedy. Holding grudges. Can't let go. Simmering negativity. Poisoned by past wrongs.",
        "proximity_notes": "Near Bitter center between Angry and Sad. Resentful = bitter + lingering anger + hurt."
    },
    
    "Bitter - Betrayed": {
        "emotional_composition": {
            "Bitter": 0.70,
            "Angry": 0.20,
            "Sad": 0.10
        },
        "analysis": "Babes in Toyland 'Bruise Violet', Rollins Band 'Liar', Silverstein. Feeling wronged. Trust broken. Wounded and vengeful. Specific hurt.",
        "proximity_notes": "Between Bitter and Angry/Sad. Betrayed = bitterness from specific violation, trust destroyed."
    },
    
    "Excited - Adventure": {
        "emotional_composition": {
            "Excited": 0.75,
            "Happy": 0.15,
            "Energy": 0.10
        },
        "analysis": "Two Steps From Hell, Thomas Bergersen epic scores. Quest and exploration. Unknown territory. Bold discovery. Thrilling anticipation.",
        "proximity_notes": "Near Excited center pulled toward Happy/Energy. Adventure = excited exploration, bold joy."
    }
}

# Save Batch 8
output = {
    "batch": 8,
    "sub_vibes_analyzed": list(batch8_analysis.keys()),
    "total_in_batch": len(batch8_analysis),
    "analysis": batch8_analysis,
    "status": "Batch 8 complete - 80 of 114 sub-vibes analyzed (cumulative)"
}

with open('ananki_outputs/emotional_analysis_batch8.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 8 ===')
print(f'Analyzed: {len(batch8_analysis)} sub-vibes\n')

for subvibe, data in batch8_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Analysis: {data["analysis"][:80]}...\n')

print('Saved to: ananki_outputs/emotional_analysis_batch8.json')
print('Progress: 80/114 sub-vibes complete (70.2%)!')
print('\nReady for Batch 9!')
