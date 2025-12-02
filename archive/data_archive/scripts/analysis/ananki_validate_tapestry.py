"""
Ananki Tapestry Validation
Checks both connections AND separations for authenticity
"""

import json

print("="*70)
print("ANANKI TAPESTRY VALIDATION")
print("="*70)

# Load tapestry with relationships
with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

print(f"\n{len(tapestry['vibes'])} vibes to validate...")

# ============================================================================
# CHECK 1: Are vibes that SHOULD be separated actually separated?
# ============================================================================

print("\n" + "="*70)
print("CHECKING SEPARATIONS (vibes that should NOT be connected)")
print("="*70)

# Define vibes that should NOT be closely connected
SHOULD_BE_SEPARATED = [
    ('Happy - Euphoric', 'Sad - Depressive'),  # Opposite emotional states
    ('Party - Club', 'Sad - Grief'),  # Completely different contexts
    ('Calm - Ambient', 'Anxious - Panic'),  # Opposite tension levels
    ('Romantic - First Love', 'Dark - Apocalyptic'),  # No overlap
    ('Energy - Workout', 'Night - Sleep'),  # Opposite energy
    ('Happy - Celebration', 'Anxious - Existential Dread'),  # Total opposites
    ('Chill - Beach/Summer', 'Dark - Gothic'),  # Opposite moods
]

print("\nValidating separations:")
issues = []

for vibe1, vibe2 in SHOULD_BE_SEPARATED:
    if vibe1 in tapestry['vibes'] and vibe2 in tapestry['vibes']:
        # Check if they're connected
        nearby1 = tapestry['vibes'][vibe1].get('nearby_vibes', [])
        nearby2 = tapestry['vibes'][vibe2].get('nearby_vibes', [])
        
        if vibe2 in nearby1 or vibe1 in nearby2:
            issues.append((vibe1, vibe2))
            print(f"  [!] {vibe1} <-X-> {vibe2} (should be separated!)")
        else:
            print(f"  [OK] {vibe1} -/- {vibe2} (properly separated)")

# ============================================================================
# CHECK 2: Are vibes that SHOULD be connected actually connected?
# ============================================================================

print("\n" + "="*70)
print("CHECKING CONNECTIONS (vibes that SHOULD be nearby)")
print("="*70)

SHOULD_BE_CONNECTED = [
    ('Sad - Heartbreak', 'Sad - Crying'),  # Both heartbreak emotions
    ('Dark - Gothic', 'Dark - Witchy'),  # Both dark aesthetic
    ('Night - 3AM Thoughts', 'Anxious - Existential Dread'),  # Late night dread
    ('Romantic - First Love', 'Happy - Euphoric'),  # New love euphoria
    ('Energy - Workout', 'Energy - Pump Up'),  # Both high energy
    ('Introspective - Philosophical', 'Introspective - Self-Reflection'),  # Both deep thought
]

print("\nValidating connections:")
missing = []

for vibe1, vibe2 in SHOULD_BE_CONNECTED:
    if vibe1 in tapestry['vibes'] and vibe2 in tapestry['vibes']:
        nearby1 = tapestry['vibes'][vibe1].get('nearby_vibes', [])
        nearby2 = tapestry['vibes'][vibe2].get('nearby_vibes', [])
        
        if vibe2 in nearby1 or vibe1 in nearby2:
            print(f"  [OK] {vibe1} <-> {vibe2} (connected!)")
        else:
            missing.append((vibe1, vibe2))
            print(f"  [!] {vibe1} -X- {vibe2} (should be connected!)")

# ============================================================================
# CHECK 3: Identify Emotional Gaps
# ============================================================================

print("\n" + "="*70)
print("EMOTIONAL GAP ANALYSIS")
print("="*70)

# Analyze what emotions we're missing
existing_emotions = set()
for vibe in tapestry['vibes'].keys():
    # Extract emotional keywords
    vibe_lower = vibe.lower()
    if 'sad' in vibe_lower: existing_emotions.add('sad')
    if 'happy' in vibe_lower: existing_emotions.add('happy')
    if 'angry' in vibe_lower or 'rage' in vibe_lower: existing_emotions.add('angry')
    if 'calm' in vibe_lower or 'chill' in vibe_lower: existing_emotions.add('calm')
    if 'anxious' in vibe_lower: existing_emotions.add('anxious')
    if 'dark' in vibe_lower: existing_emotions.add('dark')
    # Add more...

print(f"\nEmotions we HAVE: {sorted(existing_emotions)}")

MISSING_EMOTIONS = [
    'Bitter/Resentful',
    'Vengeful/Hateful', 
    'Jealous/Envious',
    'Peaceful/Serene',
    'Excited/Anticipatory',
    'Hopeful/Optimistic',
    'Playful/Silly',
    'Chaotic/Frantic',
    'Angry (general - we have energy but not pure anger!)',
    'Bored/Restless',
    'Grateful/Appreciative',
    'Confident/Powerful (we have some but could expand)',
]

print(f"\nEmotions we're MISSING or need more of:")
for emotion in MISSING_EMOTIONS:
    print(f"  - {emotion}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("VALIDATION SUMMARY")
print("="*70)

if issues:
    print(f"\n[!] {len(issues)} improper connections found (need fixing)")
else:
    print(f"\n[OK] All separations are proper!")

if missing:
    print(f"[!] {len(missing)} missing connections found (need adding)")
else:
    print(f"[OK] All expected connections exist!")

print(f"\n[GAPS] {len(MISSING_EMOTIONS)} emotional states missing")
print(f"\n[NEXT] Run targeted boosters for missing emotions")
