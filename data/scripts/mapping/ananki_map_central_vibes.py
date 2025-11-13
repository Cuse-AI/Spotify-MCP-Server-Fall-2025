"""
Ananki Central Vibe Mapper
Creates the foundational emotional map with central vibes and sub-vibe orbits
"""

import json
import pandas as pd

print("="*70)
print("ANANKI CENTRAL VIBE MAPPER")
print("="*70)

# Load tapestry
with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

print(f"\nCurrent tapestry: {len(tapestry['vibes'])} vibes, {tapestry['stats']['total_songs']} songs")

# ============================================================================
# STEP 1: Define Central Vibes (The Emotional Continents)
# ============================================================================

CENTRAL_VIBES = {
    'Sad': {
        'description': 'Sadness, sorrow, grief, melancholy',
        'valence': 'negative',
        'energy': 'low-medium',
        'sub_vibes': ['Sad - Heartbreak', 'Sad - Crying', 'Sad - Lonely', 'Sad - Melancholic', 
                      'Sad - Grief', 'Sad - Depressive', 'Sad - Nostalgic Sad']
    },
    
    'Happy': {
        'description': 'Happiness, joy, positivity, celebration',
        'valence': 'positive',
        'energy': 'medium-high',
        'sub_vibes': ['Happy - Feel Good', 'Happy - Sunshine', 'Happy - Carefree', 
                      'Happy - Euphoric', 'Happy - Celebration']
    },
    
    'Calm': {
        'description': 'Relaxation, peace, tranquility, chill',
        'valence': 'positive-neutral',
        'energy': 'low',
        'sub_vibes': ['Chill - Morning Coffee', 'Chill - Rainy Day', 'Chill - Beach/Summer',
                      'Chill - Evening', 'Chill - Sunday', 'Chill - Lofi', 'Chill - Jazz', 'Chill - Ambient']
    },
    
    'Anxious': {
        'description': 'Anxiety, worry, stress, tension',
        'valence': 'negative',
        'energy': 'medium-high',
        'sub_vibes': ['Anxious - Overwhelmed', 'Anxious - Panic', 'Anxious - Nervous Energy',
                      'Anxious - Social Anxiety', 'Anxious - Existential Dread', 'Anxious - Calming Anxiety']
    },
    
    'Energetic': {
        'description': 'Energy, motivation, power, drive',
        'valence': 'positive',
        'energy': 'very high',
        'sub_vibes': ['Energy - Pump Up', 'Energy - Sports', 'Energy - Workout',
                      'Energy - Confidence', 'Energy - Running']
    },
    
    'Dark': {
        'description': 'Darkness, mystery, shadow, gothic',
        'valence': 'neutral-negative',
        'energy': 'variable',
        'sub_vibes': ['Dark - Apocalyptic', 'Dark - Gothic', 'Dark - Haunting',
                      'Dark - Witchy', 'Dark - Noir', 'Dark - Villain Arc', 'Dark - Brooding']
    },
    
    'Introspective': {
        'description': 'Reflection, contemplation, deep thought',
        'valence': 'neutral',
        'energy': 'low-medium',
        'sub_vibes': ['Introspective - Life Changes', 'Introspective - Philosophical',
                      'Introspective - Self-Reflection', 'Introspective - Growth',
                      'Introspective - Questioning', 'Introspective - Contemplative']
    },
    
    'Romantic': {
        'description': 'Love, romance, intimacy, connection',
        'valence': 'positive',
        'energy': 'medium',
        'sub_vibes': ['Romantic - First Love', 'Romantic - Intimate', 'Romantic - Anniversary',
                      'Romantic - Slow Dance', 'Romantic - Date Night', 'Romantic - Long Distance',
                      'Romantic - Proposal']
    },
    
    'Nostalgic': {
        'description': 'Nostalgia, longing for past, memories',
        'valence': 'bittersweet',
        'energy': 'low',
        'sub_vibes': ['Nostalgic - Simpler Times', 'Nostalgic - Childhood',
                      'Nostalgic - Teen Years', 'Nostalgic - 90s', 'Nostalgic - 2000s']
    },
    
    'Night': {
        'description': 'Nighttime emotions, late-night thoughts, nocturnal',
        'valence': 'varies',
        'energy': 'low-medium',
        'sub_vibes': ['Night - 3AM Thoughts', 'Night - Midnight Drive', 'Night - Sleep',
                      'Night - City Nights', 'Night - Contemplative']
    },
    
    'Driving': {
        'description': 'Driving emotions, journey, movement',
        'valence': 'varies',
        'energy': 'medium',
        'sub_vibes': ['Drive - Road Trip', 'Drive - Night Drive', 'Drive - Speed',
                      'Drive - City', 'Drive - Scenic', 'Drive - Alone']
    },
    
    'Party': {
        'description': 'Social celebration, dancing, festive energy',
        'valence': 'positive',
        'energy': 'very high',
        'sub_vibes': ['Party - Club', 'Party - Pregame', 'Party - House Party',
                      'Party - College', 'Party - Dance', 'Party - Festival']
    },
}

# ============================================================================
# STEP 2: Map Central Vibe Relationships
# ============================================================================

CENTRAL_RELATIONSHIPS = {
    'Sad': ['Anxious', 'Dark', 'Introspective', 'Nostalgic', 'Calm'],
    'Happy': ['Energetic', 'Romantic', 'Calm', 'Party', 'Nostalgic'],
    'Calm': ['Happy', 'Introspective', 'Nostalgic', 'Romantic', 'Sad', 'Night'],
    'Anxious': ['Sad', 'Introspective', 'Dark', 'Energetic', 'Night'],
    'Energetic': ['Happy', 'Party', 'Anxious', 'Driving'],
    'Dark': ['Sad', 'Anxious', 'Introspective', 'Night', 'Romantic'],
    'Introspective': ['Sad', 'Anxious', 'Dark', 'Calm', 'Nostalgic', 'Night'],
    'Romantic': ['Happy', 'Sad', 'Calm', 'Dark', 'Nostalgic', 'Night'],
    'Nostalgic': ['Sad', 'Happy', 'Introspective', 'Romantic', 'Calm'],
    'Night': ['Introspective', 'Dark', 'Anxious', 'Calm', 'Sad', 'Driving'],
    'Driving': ['Energetic', 'Calm', 'Night', 'Happy', 'Introspective'],
    'Party': ['Happy', 'Energetic', 'Romantic', 'Night'],
}

print("\n" + "="*70)
print("CENTRAL VIBE MAP DEFINED")
print("="*70)

print(f"\n{len(CENTRAL_VIBES)} Central Vibes:")
for central in CENTRAL_VIBES:
    sub_count = len(CENTRAL_VIBES[central]['sub_vibes'])
    print(f"  {central}: {sub_count} sub-vibes")

print(f"\nRelationships mapped!")

# Save
output = {
    'central_vibes': CENTRAL_VIBES,
    'central_relationships': CENTRAL_RELATIONSHIPS,
    'total_central_vibes': len(CENTRAL_VIBES),
    'total_sub_vibes': sum(len(v['sub_vibes']) for v in CENTRAL_VIBES.values())
}

with open('ananki_outputs/central_vibe_map.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n[SAVED] ananki_outputs/central_vibe_map.json")
print(f"\n[NEXT] Arrange sub-vibes around their central vibes")
print(f"[NEXT] Map sub-vibe to sub-vibe relationships")
