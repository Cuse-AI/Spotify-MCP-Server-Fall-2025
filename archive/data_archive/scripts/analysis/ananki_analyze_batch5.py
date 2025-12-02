import json

# Ananki's emotional analysis for Batch 5: Party + Romantic + Dark sub-vibes
batch5_analysis = {
    "Party - College": {
        "emotional_composition": {
            "Party": 0.70,
            "Playful": 0.15,
            "Dark": 0.10,
            "Energy": 0.05
        },
        "analysis": "Gothic Archies 'The World is a Very Scary Place', Ministry 'Everyday is Halloween'. Alternative/goth college party vibes. Edgy and weird. Underground scene energy.",
        "proximity_notes": "Party pulled toward Playful and Dark. College = alternative party energy, quirky edge."
    },
    
    "Party - Dance": {
        "emotional_composition": {
            "Party": 0.80,
            "Energy": 0.15,
            "Happy": 0.05
        },
        "analysis": "Pure dance floor energy. Slayyyter, Cobrah, electronic beats. Body movement focus. Rhythmic and physical. Club bangers.",
        "proximity_notes": "Very close to Party center. Dance = concentrated party energy, movement-focused celebration."
    },
    
    "Romantic - First Love": {
        "emotional_composition": {
            "Romantic": 0.75,
            "Happy": 0.15,
            "Excited": 0.10
        },
        "analysis": "Indie folk and dreamy vibes. Anna von Hausswolff, Emma Ruth Rundle. Tender and new. Butterflies and wonder. Innocence of first connection.",
        "proximity_notes": "Near Romantic center with Happy/Excited pull. First love = romance + joy + nervous anticipation."
    },
    
    "Romantic - Intimate": {
        "emotional_composition": {
            "Romantic": 0.80,
            "Chill": 0.10,
            "Night": 0.05,
            "Dark": 0.05
        },
        "analysis": "Tracy Chapman, Sofia Isella. Close and vulnerable. Private moments. Deep connection. Quiet intensity. Bedroom vibes.",
        "proximity_notes": "Close to Romantic center with Chill/Night quality. Intimate = private romance, vulnerable closeness."
    },
    
    "Romantic - Date Night": {
        "emotional_composition": {
            "Romantic": 0.70,
            "Happy": 0.15,
            "Chill": 0.10,
            "Excited": 0.05
        },
        "analysis": "'Chasing Cars', Radiohead. Intentional romance. Getting ready, anticipation. Effort and care. Creating special moments.",
        "proximity_notes": "Romantic pulled toward Happy and Chill. Date night = planned romance, excited but relaxed."
    },
    
    "Romantic - Long Distance": {
        "emotional_composition": {
            "Romantic": 0.60,
            "Sad": 0.25,
            "Nostalgic": 0.10,
            "Hopeful": 0.05
        },
        "analysis": "Neil Young, Saint Motel. Longing and missing someone. Love mixed with ache. Distance creates bittersweet feelings. Holding on.",
        "proximity_notes": "Between Romantic and Sad. Long distance = love + longing + melancholy separation."
    },
    
    "Romantic - Anniversary": {
        "emotional_composition": {
            "Romantic": 0.65,
            "Nostalgic": 0.20,
            "Grateful": 0.10,
            "Happy": 0.05
        },
        "analysis": "'Think of Laura', Alice in Chains 'Brother'. Reflection on journey together. Appreciating what you've built. Time and commitment celebrated.",
        "proximity_notes": "Between Romantic and Nostalgic/Grateful. Anniversary = romance + reflection + appreciation."
    },
    
    "Romantic - Proposal": {
        "emotional_composition": {
            "Romantic": 0.70,
            "Excited": 0.15,
            "Hopeful": 0.10,
            "Anxious": 0.05
        },
        "analysis": "Pearl Jam vibes. Major life moment. Nervous energy mixed with deep love. Commitment and future. Vulnerability of asking.",
        "proximity_notes": "Romantic pulled toward Excited/Hopeful with slight Anxious. Proposal = romance + anticipation + nerves."
    },
    
    "Romantic - Slow Dance": {
        "emotional_composition": {
            "Romantic": 0.75,
            "Happy": 0.15,
            "Nostalgic": 0.05,
            "Chill": 0.05
        },
        "analysis": "'Walking on Sunshine', Whitney Houston 'I Wanna Dance With Somebody'. Physical closeness and joy. Swaying together. Classic romance.",
        "proximity_notes": "Near Romantic center with Happy pull. Slow dance = romance + joy + physical connection."
    },
    
    "Dark - Gothic": {
        "emotional_composition": {
            "Dark": 0.80,
            "Sad": 0.10,
            "Romantic": 0.05,
            "Introspective": 0.05
        },
        "analysis": "Murderfolk, The Goddamn Gallows, O'Death 'Lowtide'. Dark folk and gothic aesthetics. Death imagery. Melancholic darkness. Victorian vibes.",
        "proximity_notes": "Very close to Dark center. Gothic = pure darkness with melancholic and romantic edge."
    }
}

# Save Batch 5
output = {
    "batch": 5,
    "sub_vibes_analyzed": list(batch5_analysis.keys()),
    "total_in_batch": len(batch5_analysis),
    "analysis": batch5_analysis,
    "status": "Batch 5 complete - 50 of 114 sub-vibes analyzed (cumulative)"
}

with open('ananki_outputs/emotional_analysis_batch5.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('\n=== ANANKI EMOTIONAL ANALYSIS - BATCH 5 ===')
print(f'Analyzed: {len(batch5_analysis)} sub-vibes\n')

for subvibe, data in batch5_analysis.items():
    print(f'{subvibe}:')
    comps = [f'{vibe}({int(pct*100)}%)' for vibe, pct in sorted(data['emotional_composition'].items(), key=lambda x: x[1], reverse=True)]
    print(f'  Composition: {", ".join(comps)}')
    print(f'  Analysis: {data["analysis"][:80]}...\n')

print('Saved to: ananki_outputs/emotional_analysis_batch5.json')
print('Progress: 50/114 sub-vibes complete (43.9%)!')
print('\nReady for Batch 6!')
