import json

# Ananki's emotional analysis for Batch 7: Introspective + Anxious + Nostalgic sub-vibes
batch7_analysis = {
    "Introspective - Growth": {
        "emotional_composition": {
            "Introspective": 0.70,
            "Hopeful": 0.15,
            "Grateful": 0.10,
            "Sad": 0.05
        },
        "analysis": "The Byrds, Todd Snider, Amy Winehouse 'Back to Black'. Processing lessons learned. Becoming better. Reflecting on progress. Bittersweet development.",
        "proximity_notes": "Between Introspective and Hopeful/Grateful. Growth = reflection + optimism + appreciation."
    },
    
    "Introspective - Questioning": {
        "emotional_composition": {
            "Introspective": 0.75,
            "Anxious": 0.15,
            "Sad": 0.10
        },
        "analysis": "Lou Armstrong 'What a Wonderful World', 'Rainbow Connection', Jim Croce 'Time In A Bottle'. Asking why. Seeking answers. Uncertainty and wonder mixed.",
        "proximity_notes": "Between Introspective and Anxious/Sad. Questioning = deep thought + uncertainty + melancholy."
    },
    
    "Anxious - Panic": {
        "emotional_composition": {
            "Anxious": 0.85,
            "Chaotic": 0.10,
            "Dark": 0.05
        },
        "analysis": "John Coltrane experimental, Hans Zimmer tense scores, Hiatus Kaiyote intensity. Heart racing. Overwhelming fear. Loss of control. Peak anxiety.",
        "proximity_notes": "Very close to Anxious center. Panic = pure anxiety at its peak, chaotic overwhelming."
    },
    
    "Anxious - Overwhelmed": {
        "emotional_composition": {
            "Anxious": 0.75,
            "Sad": 0.10,
            "Chaotic": 0.10,
            "Bored": 0.05
        },
        "analysis": "Bad Religion, Stella Paris, M.Ward. Too much at once. Can't keep up. Drowning in tasks and emotions. Exhausted worry.",
        "proximity_notes": "Near Anxious center pulled toward Chaotic/Sad. Overwhelmed = anxiety + chaos + exhaustion."
    },
    
    "Anxious - Nervous Energy": {
        "emotional_composition": {
            "Anxious": 0.70,
            "Energy": 0.20,
            "Excited": 0.10
        },
        "analysis": "Dance With the Dead, Carpenter Brut, Perturbator. Restless and wired. Can't sit still. Anxious but mobilized. Synthwave tension.",
        "proximity_notes": "Between Anxious and Energy. Nervous energy = anxiety channeled into movement, restless power."
    },
    
    "Anxious - Calming Anxiety": {
        "emotional_composition": {
            "Anxious": 0.50,
            "Chill": 0.30,
            "Peaceful": 0.20
        },
        "analysis": "Juanma Salinas 'Calmo', Camel 'The Snow Goose', Mike Oldfield. Soothing worried mind. Gentle reassurance. Coming down from anxiety.",
        "proximity_notes": "Halfway between Anxious and Chill/Peaceful. Calming = anxiety being soothed, transitional state."
    },
    
    "Anxious - Existential Dread": {
        "emotional_composition": {
            "Anxious": 0.65,
            "Dark": 0.20,
            "Introspective": 0.15
        },
        "analysis": "Tool 'Aenima', Soundgarden, Tori Amos 'Precious Things'. Big scary questions. Mortality and meaninglessness. Cosmic anxiety. Deep philosophical fear.",
        "proximity_notes": "Between Anxious, Dark, and Introspective. Existential dread = anxiety + darkness + deep thought."
    },
    
    "Anxious - Social Anxiety": {
        "emotional_composition": {
            "Anxious": 0.75,
            "Sad": 0.15,
            "Introspective": 0.10
        },
        "analysis": "Ethel Cain 'Ptolemaea', Aphex Twin experimental, Diamanda Galas intensity. Fear of judgment. Awkwardness and isolation. Self-consciousness.",
        "proximity_notes": "Near Anxious center with Sad pull. Social anxiety = specific anxiety + isolation + self-focus."
    },
    
    "Nostalgic - Childhood": {
        "emotional_composition": {
            "Nostalgic": 0.75,
            "Happy": 0.15,
            "Sad": 0.10
        },
        "analysis": "Heart, Boards of Canada 'Geogaddi', The Caretaker 'Everywhere at the End of Time'. Longing for innocence. Bittersweet memories. Simpler times.",
        "proximity_notes": "Near Nostalgic center between Happy and Sad. Childhood = bittersweet memory, innocence lost."
    },
    
    "Nostalgic - Teen Years": {
        "emotional_composition": {
            "Nostalgic": 0.70,
            "Sad": 0.15,
            "Introspective": 0.10,
            "Happy": 0.05
        },
        "analysis": "Sisters of Mercy, The Cure, Depeche Mode, Postal Service. Coming-of-age memories. First experiences. Identity formation. Angsty nostalgia.",
        "proximity_notes": "Between Nostalgic and Sad/Introspective. Teen years = reflective nostalgia with complexity."
    }
}

# Save Batch 7
output = {
    "batch": 7,
    "sub_vibes_analyzed": list(batch7_analysis.keys()),
    "total_in_batch": len(batch7_analysis),
    "analysis": batch7_analysis,
    "status": "Batch 7 complete - 70 of 114 sub-vibes analyzed (cumulative)"
}

with open('ananki_outputs/emotional_analysis_batch7.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 7 ===')
print(f'Analyzed: {len(batch7_analysis)} sub-vibes\n')

for subvibe, data in batch7_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Analysis: {data["analysis"][:80]}...\n')

print('Saved to: ananki_outputs/emotional_analysis_batch7.json')
print('Progress: 70/114 sub-vibes complete (61.4%)!')
print('\nReady for Batch 8!')
