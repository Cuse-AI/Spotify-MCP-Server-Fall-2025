"""
Ananki Micro-Vibe Detector
Finds even more granular emotional sub-categories within sub-vibes
"""

import pandas as pd
import re
from collections import Counter

print("="*70)
print("ANANKI MICRO-VIBE ANALYSIS - BATCH 1")
print("="*70)

df = pd.read_csv('../reddit_batch1_sad_variations_20251107_225307.csv')
print(f"\nAnalyzing {len(df)} songs for micro-patterns...")

# Micro-vibe detection patterns
MICRO_VIBE_PATTERNS = {
    'Sad - Heartbreak': {
        'Fresh Breakup': ['just broke up', 'recent breakup', 'just ended', 'newly single'],
        'Getting Over Ex': ['getting over', 'moving on', 'post breakup', 'heal from breakup'],
        'Unrequited Love': ['unrequited', 'one sided', 'dont love me back', 'cant have you'],
        'Long Distance Pain': ['long distance', 'far away love', 'distance hurts'],
        'Cheating/Betrayal': ['cheated', 'betrayed', 'unfaithful', 'affair', 'lied to me'],
    },
    'Sad - Crying': {
        'Ugly Crying': ['ugly cry', 'sob uncontrollably', 'breakdown crying'],
        'Cathartic Release': ['cathartic', 'release emotions', 'let it all out'],
        'Late Night Tears': ['crying at night', 'late night tears', '3am crying'],
        'Public Crying': ['cry in public', 'tears at work', 'crying in car'],
    },
    'Sad - Lonely': {
        'Alone in Crowd': ['lonely in crowd', 'surrounded but alone', 'social loneliness'],
        'Isolated/Quarantine': ['isolated', 'isolation', 'stuck inside', 'quarantine'],
        'Friday Night Alone': ['alone friday night', 'lonely weekend', 'everyone out except me'],
        'Missing Someone Specific': ['missing you', 'wish you were here', 'need you here'],
    },
    'Sad - Melancholic': {
        'Autumn Melancholy': ['autumn', 'fall sadness', 'october melancholy', 'november'],
        'Rainy Day Melancholy': ['rainy melancholy', 'rain sadness', 'grey day sad'],
        'Beautiful Sadness': ['beautiful sad', 'pretty melancholy', 'gorgeous sadness'],
        'Sunday Evening Blues': ['sunday evening', 'sunday scaries', 'end of weekend sad'],
    },
    'Sad - Grief': {
        'Death of Parent': ['parent died', 'lost mom', 'lost dad', 'father passed'],
        'Death of Friend': ['friend died', 'lost friend', 'friend passed away'],
        'Pet Loss': ['pet died', 'dog passed', 'cat died', 'lost my pet'],
        'General Loss': ['someone died', 'death', 'passed away', 'funeral'],
    },
    'Sad - Depressive': {
        'Clinical Depression': ['depression diagnosed', 'clinical depression', 'depressed'],
        'Hopeless/Giving Up': ['hopeless', 'giving up', 'no point', 'why bother'],
        'Empty/Numb': ['feel nothing', 'numb', 'empty inside', 'void'],
        'Self-Loathing': ['hate myself', 'self hate', 'worthless', 'not good enough'],
    },
    'Sad - Nostalgic Sad': {
        'Childhood Memories': ['childhood', 'growing up', 'when I was kid', 'youth'],
        'Past Relationship': ['used to be together', 'what we had', 'remember us'],
        'Old Friends': ['old friends', 'lost touch', 'friendship ended', 'miss my friends'],
        'Simpler Times': ['simpler times', 'easier back then', 'good old days'],
    },
}

def detect_micro_vibes(text, sub_vibe_category):
    if sub_vibe_category not in MICRO_VIBE_PATTERNS:
        return []
    text_lower = text.lower()
    found = []
    for micro_vibe, keywords in MICRO_VIBE_PATTERNS[sub_vibe_category].items():
        for keyword in keywords:
            if keyword in text_lower:
                found.append(f"{sub_vibe_category}/{micro_vibe}")
                break
    return found

# Detect micro-vibes
print("\nDetecting micro-vibes...")
micro_vibe_list = []

for idx, row in df.iterrows():
    category = row['vibe_sub_category']
    text = str(row['vibe_description']) + ' ' + str(row['recommendation_reasoning'])
    micros = detect_micro_vibes(text, category)
    micro_vibe_list.extend(micros)
    
    if (idx + 1) % 1000 == 0:
        print(f"  {idx + 1}/{len(df)}...")

# Results
micro_counts = Counter(micro_vibe_list)

print(f"\n" + "="*70)
print("MICRO-VIBES DETECTED:")
print("="*70)

print(f"\nTotal instances: {len(micro_vibe_list)}")
print(f"Unique micro-vibes: {len(micro_counts)}")

print(f"\nMicro-vibes with 10+ songs:")
viable_micros = []
for micro, count in micro_counts.most_common():
    if count >= 10:
        print(f"  {micro}: {count} songs")
        viable_micros.append(micro)
    else:
        break

print(f"\n[RESULT] {len(viable_micros)} viable micro-vibes found!")
print(f"[CONCLUSION] We can create {len(viable_micros)} additional granular nodes!")

# Recommendation
print(f"\n" + "="*70)
print("RECOMMENDATION:")
print("="*70)
print(f"\nCurrent structure: 7 sad sub-vibes")
print(f"Potential expansion: +{len(viable_micros)} micro-vibes")
print(f"Total possible sad variants: {7 + len(viable_micros)}")
print(f"\nThis gives users VERY specific emotional targeting!")
print(f"Example: 'Fresh Breakup' vs 'Getting Over Ex' - different healing stages!")
