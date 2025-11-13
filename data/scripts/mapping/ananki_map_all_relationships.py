"""
Ananki Complete Relationship Mapper
Updates ALL vibe relationships now that we have 114 vibes
Maps the complete emotional web with proper connections and separations
"""

import json

print("="*70)
print("ANANKI COMPLETE RELATIONSHIP MAPPER")
print("="*70)

# Load tapestry
with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

print(f"\nMapping {len(tapestry['vibes'])} vibes...")

# ============================================================================
# UPDATED CENTRAL VIBES (Now includes all new categories!)
# ============================================================================

CENTRAL_VIBES = {
    'Sad': ['Sad - Heartbreak', 'Sad - Crying', 'Sad - Lonely', 'Sad - Melancholic', 
            'Sad - Grief', 'Sad - Depressive', 'Sad - Nostalgic Sad'],
    
    'Happy': ['Happy - Feel Good', 'Happy - Sunshine', 'Happy - Carefree', 
              'Happy - Euphoric', 'Happy - Celebration'],
    
    'Angry': ['Angry - Rage', 'Angry - Aggressive', 'Angry - Cathartic Anger', 
              'Angry - Frustrated'],
    
    'Bitter': ['Bitter - Resentful', 'Bitter - Betrayed'],
    
    'Calm': ['Chill - Morning Coffee', 'Chill - Rainy Day', 'Chill - Beach/Summer',
             'Chill - Evening', 'Chill - Sunday', 'Chill - Lofi', 'Chill - Jazz', 'Chill - Ambient'],
    
    'Peaceful': ['Peaceful - Serene', 'Peaceful - Quiet Reflection', 
                 'Peaceful - Gentle', 'Peaceful - Meditative'],
    
    'Anxious': ['Anxious - Overwhelmed', 'Anxious - Panic', 'Anxious - Nervous Energy',
                'Anxious - Social Anxiety', 'Anxious - Existential Dread', 'Anxious - Calming Anxiety'],
    
    'Energetic': ['Energy - Pump Up', 'Energy - Sports', 'Energy - Workout',
                  'Energy - Confidence', 'Energy - Running'],
    
    'Confident': ['Confident - Self-Assured', 'Confident - Powerful', 'Confident - Bold',
                  'Confident - Unstoppable', 'Confident - Victorious', 'Confident - Boss'],
    
    'Dark': ['Dark - Apocalyptic', 'Dark - Gothic', 'Dark - Haunting',
             'Dark - Witchy', 'Dark - Noir', 'Dark - Villain Arc', 'Dark - Brooding'],
    
    'Introspective': ['Introspective - Life Changes', 'Introspective - Philosophical',
                      'Introspective - Self-Reflection', 'Introspective - Growth',
                      'Introspective - Questioning', 'Introspective - Contemplative'],
    
    'Romantic': ['Romantic - First Love', 'Romantic - Intimate', 'Romantic - Anniversary',
                 'Romantic - Slow Dance', 'Romantic - Date Night', 'Romantic - Long Distance',
                 'Romantic - Proposal'],
    
    'Nostalgic': ['Nostalgic - Simpler Times', 'Nostalgic - Childhood',
                  'Nostalgic - Teen Years', 'Nostalgic - 90s', 'Nostalgic - 2000s'],
    
    'Hopeful': ['Hopeful - Optimistic', 'Hopeful - Healing', 'Hopeful - New Beginnings'],
    
    'Excited': ['Excited - Adventure', 'Excited - Anticipation'],
    
    'Jealous': ['Jealous - Romantic Jealousy', 'Jealous - Insecure', 
                'Jealous - Competitive', 'Jealous - Envious'],
    
    'Playful': ['Playful - Silly', 'Playful - Fun', 'Playful - Whimsical', 'Playful - Childlike'],
    
    'Chaotic': ['Chaotic - Overwhelming', 'Chaotic - Frantic', 
                'Chaotic - Unhinged', 'Chaotic - Scattered'],
    
    'Bored': ['Bored - Waiting', 'Bored - Restless', 'Bored - Understimulated', 'Bored - Monotonous'],
    
    'Grateful': ['Grateful - Thankful', 'Grateful - Content', 
                 'Grateful - Reflective Gratitude', 'Grateful - Warm Appreciation'],
    
    'Night': ['Night - 3AM Thoughts', 'Night - Midnight Drive', 'Night - Sleep',
              'Night - City Nights', 'Night - Contemplative'],
    
    'Driving': ['Drive - Road Trip', 'Drive - Night Drive', 'Drive - Speed',
                'Drive - City', 'Drive - Scenic', 'Drive - Alone'],
    
    'Party': ['Party - Club', 'Party - Pregame', 'Party - House Party',
              'Party - College', 'Party - Dance', 'Party - Festival'],
}

# Map central vibe relationships
CENTRAL_RELATIONSHIPS = {
    'Sad': ['Anxious', 'Bitter', 'Dark', 'Introspective', 'Nostalgic', 'Hopeful', 'Calm'],
    'Happy': ['Excited', 'Energetic', 'Playful', 'Grateful', 'Hopeful', 'Romantic', 'Party'],
    'Angry': ['Bitter', 'Jealous', 'Chaotic', 'Dark', 'Energetic', 'Anxious'],
    'Bitter': ['Sad', 'Angry', 'Jealous', 'Dark', 'Introspective'],
    'Calm': ['Peaceful', 'Happy', 'Introspective', 'Nostalgic', 'Grateful', 'Night'],
    'Peaceful': ['Calm', 'Grateful', 'Introspective', 'Hopeful', 'Night'],
    'Anxious': ['Sad', 'Chaotic', 'Introspective', 'Dark', 'Night', 'Bored'],
    'Energetic': ['Happy', 'Excited', 'Party', 'Confident', 'Angry', 'Chaotic'],
    'Confident': ['Energetic', 'Happy', 'Playful', 'Dark', 'Angry'],
    'Dark': ['Sad', 'Anxious', 'Angry', 'Bitter', 'Introspective', 'Night', 'Romantic'],
    'Introspective': ['Sad', 'Anxious', 'Dark', 'Calm', 'Peaceful', 'Nostalgic', 'Hopeful', 'Night'],
    'Romantic': ['Happy', 'Sad', 'Excited', 'Jealous', 'Nostalgic', 'Dark', 'Peaceful', 'Night'],
    'Nostalgic': ['Sad', 'Happy', 'Introspective', 'Romantic', 'Calm', 'Bored'],
    'Hopeful': ['Sad', 'Happy', 'Introspective', 'Peaceful', 'Grateful', 'Excited'],
    'Excited': ['Happy', 'Energetic', 'Hopeful', 'Romantic', 'Party', 'Anxious'],
    'Jealous': ['Angry', 'Bitter', 'Anxious', 'Sad', 'Romantic', 'Introspective'],
    'Playful': ['Happy', 'Excited', 'Energetic', 'Confident', 'Party', 'Grateful'],
    'Chaotic': ['Anxious', 'Angry', 'Energetic', 'Bored', 'Dark'],
    'Bored': ['Anxious', 'Chaotic', 'Sad', 'Nostalgic', 'Introspective'],
    'Grateful': ['Happy', 'Peaceful', 'Calm', 'Hopeful', 'Introspective', 'Playful'],
    'Night': ['Introspective', 'Dark', 'Anxious', 'Calm', 'Peaceful', 'Sad', 'Driving', 'Romantic'],
    'Driving': ['Energetic', 'Calm', 'Night', 'Happy', 'Introspective', 'Angry'],
    'Party': ['Happy', 'Energetic', 'Excited', 'Playful', 'Confident', 'Romantic'],
}

print(f"\n[STEP 1] Defined {len(CENTRAL_VIBES)} central vibe categories")

# ============================================================================
# Map sub-vibe relationships
# ============================================================================

print(f"\n[STEP 2] Mapping sub-vibe relationships...")

def get_nearby_vibes(sub_vibe):
    """Determine nearby vibes for a given sub-vibe"""
    
    # Find parent central vibe
    parent = None
    for central, subs in CENTRAL_VIBES.items():
        if sub_vibe in subs:
            parent = central
            break
    
    if not parent:
        return []
    
    nearby = []
    
    # 1. Siblings (same central vibe)
    siblings = [v for v in CENTRAL_VIBES[parent] if v != sub_vibe]
    nearby.extend(siblings[:5])  # Top 5 siblings
    
    # 2. Sub-vibes from related central vibes
    if parent in CENTRAL_RELATIONSHIPS:
        for related_central in CENTRAL_RELATIONSHIPS[parent][:4]:  # Top 4 related
            if related_central in CENTRAL_VIBES:
                related_subs = CENTRAL_VIBES[related_central][:3]  # Top 3 from each
                nearby.extend(related_subs)
    
    return nearby[:12]  # Limit to 12 nearest

# Update all vibes
updated = 0
for vibe_name in tapestry['vibes']:
    nearby = get_nearby_vibes(vibe_name)
    tapestry['vibes'][vibe_name]['nearby_vibes'] = nearby
    updated += 1
    
    if updated % 20 == 0:
        print(f"    Mapped {updated}/{len(tapestry['vibes'])}...")

print(f"  [OK] Mapped all {updated} vibes!")

# Save
with open('ananki_outputs/tapestry_complete.json', 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] Updated tapestry with complete relationships!")

# Show samples
print(f"\n" + "="*70)
print("SAMPLE RELATIONSHIPS:")
print("="*70)

samples = ['Sad - Heartbreak', 'Angry - Rage', 'Hopeful - Optimistic', 'Jealous - Romantic Jealousy']
for vibe in samples:
    if vibe in tapestry['vibes']:
        nearby = tapestry['vibes'][vibe]['nearby_vibes'][:5]
        print(f"\n{vibe} →")
        for n in nearby:
            print(f"  • {n}")

print(f"\n[COMPLETE] All 114 vibes mapped in emotional web!")
