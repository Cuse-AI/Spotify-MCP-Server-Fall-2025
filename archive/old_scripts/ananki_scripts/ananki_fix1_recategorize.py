"""
Ananki Fix #1: Semantic Re-categorization of "Other" and "Various"
Uses keyword analysis and pattern matching to infer better categories
"""

import pandas as pd
import re
from collections import defaultdict

# Enhanced category keyword mapping
CATEGORY_KEYWORDS = {
    'Emotional/Sad': [
        'sad', 'crying', 'tear', 'melanchol', 'depress', 'heartbreak', 'grief',
        'sorrow', 'lonely', 'blue', 'mourn', 'painful', 'hurt', 'somber'
    ],
    'Angry/Intense': [
        'angry', 'rage', 'furious', 'aggressive', 'intense', 'heavy', 'brutal',
        'violent', 'chaotic', 'destructive', 'primal', 'raw power'
    ],
    'Happy/Upbeat': [
        'happy', 'upbeat', 'cheerful', 'joyful', 'positive', 'bright', 'sunny',
        'feel good', 'uplifting', 'optimistic', 'fun', 'smile', 'celebrate'
    ],
    'Chill/Relaxing': [
        'chill', 'relax', 'calm', 'mellow', 'smooth', 'easy', 'laid back',
        'tranquil', 'peaceful', 'soothing', 'gentle', 'soft'
    ],
    'Dark/Atmospheric': [
        'dark', 'gothic', 'atmospheric', 'moody', 'haunting', 'eerie', 'brooding',
        'mysterious', 'ominous', 'sinister', 'shadowy', 'noir'
    ],
    'Energetic/Motivational': [
        'energetic', 'hype', 'pump', 'motivat', 'power', 'strong', 'confident',
        'badass', 'fierce', 'dynamic', 'adrenaline', 'workout', 'gym'
    ],
    'Introspective/Thoughtful': [
        'introspective', 'thoughtful', 'contemplative', 'reflective', 'deep',
        'philosophical', 'existential', 'meditative', 'pensive', 'soul-searching'
    ],
    'Romantic/Sensual': [
        'romantic', 'love', 'sensual', 'intimate', 'sexy', 'passionate',
        'seductive', 'affection', 'tender', 'valentine', 'crush', 'romance'
    ],
    'Night/Sleep': [
        'night', 'sleep', 'midnight', '3am', 'late night', 'insomnia', 'dream',
        'nocturnal', 'twilight', 'bedtime', 'lullaby'
    ],
    'Driving/Travel': [
        'driving', 'drive', 'road trip', 'highway', 'car', 'travel', 'journey',
        'cruising', 'road', 'commute', 'adventure'
    ],
    'Party/Dance': [
        'party', 'dance', 'club', 'rave', 'dj', 'festival', 'groove', 'funky',
        'disco', 'nightclub', 'social', 'celebration'
    ],
    'Nostalgic': [
        'nostalgic', 'nostalgia', 'throwback', 'memories', 'childhood', 'past',
        'vintage', 'classic', 'remember', 'old school', '90s', '80s', '70s'
    ],
    'Focus/Study': [
        'focus', 'study', 'concentration', 'work', 'productive', 'reading',
        'background', 'ambient study', 'homework', 'library'
    ],
    'Discovery/Exploration': [
        'discover', 'new music', 'obscure', 'underrated', 'hidden gem', 'unknown',
        'explore', 'experimental', 'avant-garde', 'unique', 'weird', 'strange'
    ],
    'Rainy/Cozy': [
        'rainy', 'rain', 'cozy', 'coffee', 'autumn', 'fall', 'winter', 'cloudy',
        'grey day', 'sweater weather', 'fireplace', 'comfort'
    ],
    'Epic/Cinematic': [
        'epic', 'cinematic', 'dramatic', 'orchestral', 'grand', 'majestic',
        'sweeping', 'soundtrack', 'score', 'triumphant', 'heroic'
    ],
    'Psychedelic/Trippy': [
        'psychedelic', 'trippy', 'surreal', 'mind-bending', 'hallucinogenic',
        'spacey', 'cosmic', 'otherworldly', 'lysergic', 'acid'
    ],
    'Rebellious/Punk': [
        'rebel', 'punk', 'anarchist', 'anti-establishment', 'protest', 'riot',
        'revolution', 'defiant', 'counterculture', 'underground'
    ],
    'Ethereal/Dreamy': [
        'ethereal', 'dreamy', 'floating', 'ambient', 'shoegaze', 'reverb',
        'hazy', 'celestial', 'angelic', 'transcendent', 'otherworldly'
    ]
}

def score_vibe_for_category(vibe_text, keywords):
    """Score how well a vibe matches a category based on keywords"""
    vibe_lower = vibe_text.lower()
    score = 0
    for keyword in keywords:
        if keyword in vibe_lower:
            score += 1
    return score

def recategorize_vibe(vibe_text, current_category):
    """Use semantic analysis to find better category"""
    
    # Keep existing non-"Other" categories
    if current_category != 'Other':
        return current_category
    
    # Score against all categories
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = score_vibe_for_category(vibe_text, keywords)
    
    # Get best match
    best_category = max(scores.items(), key=lambda x: x[1])
    
    # Only recategorize if we have confidence (score >= 1)
    if best_category[1] >= 1:
        return best_category[0]
    
    return 'Other'  # Keep as Other if no clear match

def analyze_genre_patterns(vibe_text):
    """Analyze vibe text for genre-specific patterns"""
    vibe_lower = vibe_text.lower()
    
    genre_patterns = {
        'Jazz': r'\b(jazz|bebop|swing|fusion|free jazz|modal)\b',
        'Classical': r'\b(classical|symphony|concerto|chamber|baroque|romantic era)\b',
        'Electronic': r'\b(electronic|edm|techno|house|trance|idm|ambient electronic)\b',
        'Hip-Hop': r'\b(hip hop|rap|beats|trap|underground hip hop)\b',
        'Metal': r'\b(metal|doom|black metal|death metal|thrash)\b',
        'Folk': r'\b(folk|bluegrass|americana|singer-songwriter)\b',
        'Rock': r'\b(rock|indie rock|alternative|grunge)\b',
        'Experimental': r'\b(experimental|noise|avant-garde|abstract|unconventional)\b'
    }
    
    for genre, pattern in genre_patterns.items():
        if re.search(pattern, vibe_lower):
            return genre
    
    return 'Various'

# Main execution
print("="*70)
print("ANANKI FIX #1: Semantic Re-categorization")
print("="*70)

# Load data
df = pd.read_csv('training_data_structured.csv')
print(f"\n[OK] Loaded {len(df)} records")

# Current distribution
print(f"\nCURRENT DISTRIBUTION:")
print(df['vibe_category'].value_counts())

# Apply recategorization to "Other" vibes
print(f"\n[WORKING] Recategorizing {len(df[df['vibe_category'] == 'Other'])} 'Other' vibes...")
df['vibe_category_new'] = df.apply(
    lambda row: recategorize_vibe(row['vibe_description'], row['vibe_category']),
    axis=1
)

# Apply genre analysis to "Various" genres
print(f"[WORKING] Re-analyzing {len(df[df['genre_category'] == 'Various'])} 'Various' genres...")
df['genre_category_new'] = df.apply(
    lambda row: analyze_genre_patterns(row['vibe_description']) 
                if row['genre_category'] == 'Various' 
                else row['genre_category'],
    axis=1
)

# Show improvements
print(f"\n" + "="*70)
print("RESULTS:")
print("="*70)

vibes_recategorized = (df['vibe_category'] != df['vibe_category_new']).sum()
genres_recategorized = (df['genre_category'] != df['genre_category_new']).sum()

print(f"\n[OK] Recategorized {vibes_recategorized} vibe categories")
print(f"[OK] Recategorized {genres_recategorized} genre categories")

print(f"\nNEW VIBE DISTRIBUTION:")
print(df['vibe_category_new'].value_counts())

print(f"\nNEW GENRE DISTRIBUTION:")
print(df['genre_category_new'].value_counts())

# Save updated data
output_file = 'training_data_structured_ananki_v1.csv'
df_output = df.copy()
df_output['vibe_category'] = df_output['vibe_category_new']
df_output['genre_category'] = df_output['genre_category_new']
df_output = df_output.drop(['vibe_category_new', 'genre_category_new'], axis=1)

df_output.to_csv(output_file, index=False)
print(f"\n[OK] Saved updated data to: {output_file}")

# Generate improvement report
print(f"\n" + "="*70)
print("IMPROVEMENT ANALYSIS:")
print("="*70)

old_other_pct = (df['vibe_category'] == 'Other').sum() / len(df) * 100
new_other_pct = (df['vibe_category_new'] == 'Other').sum() / len(df) * 100
old_various_pct = (df['genre_category'] == 'Various').sum() / len(df) * 100
new_various_pct = (df['genre_category_new'] == 'Various').sum() / len(df) * 100

print(f"\nVibe 'Other' category:")
print(f"  Before: {old_other_pct:.1f}%")
print(f"  After:  {new_other_pct:.1f}%")
print(f"  Improvement: {old_other_pct - new_other_pct:.1f} percentage points")

print(f"\nGenre 'Various' category:")
print(f"  Before: {old_various_pct:.1f}%")
print(f"  After:  {new_various_pct:.1f}%")
print(f"  Improvement: {old_various_pct - new_various_pct:.1f} percentage points")

print(f"\n[COMPLETE] Fix #1 Complete!")
