"""
Ananki Sub-Vibe Creator
Analyzes existing data to create granular sub-vibes from context
"""

import pandas as pd
import json
import re
from collections import defaultdict

print("="*70)
print("ANANKI SUB-VIBE CREATOR")
print("="*70)

# Load all data
print("\n[LOADING] All analyzed data...")
reddit_df = pd.read_csv('reddit_analyzed_by_ananki_20251107.csv')
youtube_df = pd.read_csv('youtube_analyzed_by_ananki_20251107.csv')

all_df = pd.concat([reddit_df, youtube_df], ignore_index=True)
print(f"  Total: {len(all_df)} songs across both sources")

# ============================================================================
# ANANKI'S SUB-VIBE ANALYSIS
# ============================================================================

# Patterns to detect sub-vibes within main vibes
SUB_VIBE_PATTERNS = {
    'Emotional/Sad': {
        'Heartbreak/Breakup': ['heartbreak', 'breakup', 'broke up', 'ex girlfriend', 'ex boyfriend', 'lost love'],
        'Grief/Loss': ['grief', 'loss', 'mourning', 'death', 'passed away', 'losing someone'],
        'Melancholic/Bittersweet': ['melanchol', 'bittersweet', 'wistful', 'longing', 'yearning'],
        'Crying/Cathartic': ['cry', 'crying', 'tears', 'sob', 'weep', 'emotional release'],
        'Lonely/Isolated': ['lonely', 'alone', 'isolated', 'solitude', 'empty'],
        'Depressive/Heavy': ['depress', 'hopeless', 'despair', 'dark sad', 'heavy sad'],
    },
    
    'Chill/Relaxing': {
        'Morning Chill': ['morning', 'wake up', 'breakfast', 'sunrise', 'coffee'],
        'Evening Wind-Down': ['evening', 'sunset', 'wind down', 'unwind', 'after work'],
        'Sunday Vibes': ['sunday', 'weekend', 'lazy day', 'slow morning'],
        'Ambient/Background': ['ambient', 'background', 'study', 'work', 'instrumental'],
        'Beach/Summer': ['beach', 'summer', 'tropical', 'vacation', 'ocean'],
        'Lofi/Beats': ['lofi', 'lo-fi', 'beats', 'hip hop chill', 'study beats'],
    },
    
    'Night/Sleep': {
        '3AM Thoughts': ['3am', '3 am', 'late night thoughts', 'insomnia', 'cant sleep'],
        'Sleep/Bedtime': ['sleep', 'bedtime', 'lullaby', 'sleeping', 'dream'],
        'Midnight Drive': ['midnight', 'late night drive', 'night drive', 'nocturnal'],
        'Contemplative Night': ['night thoughts', 'nighttime', 'darkness', 'moon'],
    },
    
    'Energetic/Motivational': {
        'Workout/Gym': ['workout', 'gym', 'exercise', 'training', 'fitness'],
        'Pump-Up/Hype': ['pump up', 'hype', 'get hyped', 'beast mode', 'lets go'],
        'Confidence/Badass': ['confidence', 'confident', 'badass', 'powerful', 'boss'],
        'Morning Energy': ['morning energy', 'wake up', 'start the day', 'energize'],
    },
    
    'Driving/Travel': {
        'Road Trip': ['road trip', 'long drive', 'highway', 'cross country'],
        'Night Drive': ['night drive', 'midnight drive', 'driving at night', 'late night cruise'],
        'City Driving': ['city drive', 'urban', 'traffic', 'commute'],
        'Open Road': ['open road', 'freedom', 'cruising', 'windows down'],
    },
    
    'Introspective/Thoughtful': {
        'Philosophical/Existential': ['philosophical', 'existential', 'meaning of life', 'deep thoughts'],
        'Self-Reflection': ['self reflection', 'looking inward', 'introspection', 'soul searching'],
        'Contemplative/Meditative': ['contemplative', 'meditative', 'mindful', 'zen', 'peaceful thoughts'],
    },
    
    'Dark/Atmospheric': {
        'Gothic/Dark': ['gothic', 'goth', 'dark aesthetic', 'black', 'darkness'],
        'Brooding/Moody': ['brooding', 'moody', 'sullen', 'somber'],
        'Haunting/Eerie': ['haunting', 'eerie', 'creepy', 'unsettling', 'mysterious'],
        'Noir/Cinematic Dark': ['noir', 'detective', 'mystery', 'film noir', 'dark cinema'],
    },
    
    'Romantic/Sensual': {
        'First Love/Crush': ['first love', 'crush', 'falling in love', 'butterflies'],
        'Intimate/Sensual': ['intimate', 'sensual', 'sexy', 'seductive', 'passion'],
        'Long-term Love': ['long term', 'marriage', 'committed', 'partnership', 'devotion'],
        'Unrequited Love': ['unrequited', 'one sided', 'love from afar', 'cant have you'],
    },
    
    'Party/Dance': {
        'Club/Nightclub': ['club', 'nightclub', 'clubbing', 'dj', 'dance floor'],
        'House Party': ['house party', 'party at home', 'small party', 'friends'],
        'Festival/Rave': ['festival', 'rave', 'edm', 'electronic dance'],
        'Pregame/Getting Ready': ['pregame', 'getting ready', 'pre party', 'hype up'],
    },
    
    'Happy/Upbeat': {
        'Feel-Good/Positive': ['feel good', 'positive', 'uplifting', 'happy vibes'],
        'Celebration/Joy': ['celebrate', 'celebration', 'joy', 'excited', 'euphoric'],
        'Sunny/Summer': ['sunny', 'summer', 'sunshine', 'bright', 'cheerful'],
    },
    
    'Focus/Study': {
        'Deep Work': ['deep work', 'concentration', 'focus hard', 'intense focus'],
        'Background Study': ['background music', 'study background', 'ambient study'],
        'Productive/Work': ['productive', 'work music', 'office', 'get things done'],
    },
}

def detect_sub_vibes(text, main_vibe):
    """Detect sub-vibes within a main vibe category"""
    if main_vibe not in SUB_VIBE_PATTERNS:
        return None
    
    text_lower = text.lower()
    sub_vibe_patterns = SUB_VIBE_PATTERNS[main_vibe]
    
    # Check each sub-vibe pattern
    for sub_vibe, keywords in sub_vibe_patterns.items():
        for keyword in keywords:
            if keyword in text_lower:
                return sub_vibe
    
    return None

# Analyze sub-vibes
print("\n[ANALYZING] Detecting sub-vibes in data...")

all_df['sub_vibe'] = None
for idx, row in all_df.iterrows():
    main_vibe = row['vibe_category']
    if pd.isna(main_vibe):
        continue
    
    # Check vibe description and reasoning
    text = str(row['vibe_description']) + ' ' + str(row['recommendation_reasoning'])
    sub_vibe = detect_sub_vibes(text, main_vibe)
    
    if sub_vibe:
        all_df.at[idx, 'sub_vibe'] = f"{main_vibe}/{sub_vibe}"
    
    if (idx + 1) % 500 == 0:
        print(f"  Processed {idx + 1} / {len(all_df)}...")

# Count sub-vibes found
sub_vibe_counts = all_df[all_df['sub_vibe'].notna()]['sub_vibe'].value_counts()

print(f"\n" + "="*70)
print("SUB-VIBES DETECTED:")
print("="*70)

print(f"\nTotal songs with sub-vibes: {len(all_df[all_df['sub_vibe'].notna()])}")
print(f"Distinct sub-vibes found: {len(sub_vibe_counts)}")

print(f"\nTop sub-vibes (>10 songs):")
for sub_vibe, count in sub_vibe_counts.items():
    if count >= 10:
        print(f"  {sub_vibe}: {count} songs")

# Build sub-vibe structure for tapestry
print(f"\n[BUILDING] Sub-vibe nodes...")

# Load tapestry to get parent relationships
with open('ananki_outputs/tapestry_map.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

sub_vibe_nodes = {}
for sub_vibe in sub_vibe_counts.index:
    if sub_vibe_counts[sub_vibe] >= 10:  # Only create node if >=10 songs
        sub_df = all_df[all_df['sub_vibe'] == sub_vibe]
        
        songs_list = []
        for idx, row in sub_df.iterrows():
            songs_list.append({
                'song': row['song_name'],
                'artist': row['artist_name'],
                'comment_score': row.get('comment_score', 0),
                'source_url': row.get('source_url', '')
            })
        
        artists = list(set([s['artist'] for s in songs_list]))
        
        # Determine parent vibe
        parent_vibe = sub_vibe.split('/')[0]
        
        sub_vibe_nodes[sub_vibe] = {
            'songs': songs_list,
            'artists': sorted(artists),
            'song_count': len(songs_list),
            'artist_count': len(artists),
            'parent_vibe': parent_vibe,
            'nearby_vibes': []  # Will determine relationships
        }

print(f"  Created {len(sub_vibe_nodes)} sub-vibe nodes (>=10 songs each)")

# Determine sub-vibe relationships (within same parent and nearby parents)
print(f"\n[ANALYZING] Sub-vibe relationships...")

for sub_vibe in sub_vibe_nodes:
    parent = sub_vibe_nodes[sub_vibe]['parent_vibe']
    nearby = []
    
    # 1. Siblings (other sub-vibes of same parent)
    for other_sub in sub_vibe_nodes:
        if other_sub != sub_vibe and sub_vibe_nodes[other_sub]['parent_vibe'] == parent:
            nearby.append(other_sub)
    
    # 2. Parent vibe
    nearby.append(parent)
    
    # 3. Sub-vibes of nearby parent vibes
    if parent in tapestry['vibes'] and 'nearby_vibes' in tapestry['vibes'][parent]:
        for nearby_parent in tapestry['vibes'][parent]['nearby_vibes'][:3]:  # Top 3 closest
            for other_sub in sub_vibe_nodes:
                if sub_vibe_nodes[other_sub]['parent_vibe'] == nearby_parent:
                    nearby.append(other_sub)
    
    sub_vibe_nodes[sub_vibe]['nearby_vibes'] = nearby[:7]  # Limit to 7 closest

print(f"  Mapped relationships for {len(sub_vibe_nodes)} sub-vibes")

# Save sub-vibe structure
output = {
    'sub_vibes': sub_vibe_nodes,
    'stats': {
        'total_sub_vibes': len(sub_vibe_nodes),
        'total_songs_in_sub_vibes': sum(n['song_count'] for n in sub_vibe_nodes.values()),
        'avg_songs_per_sub_vibe': sum(n['song_count'] for n in sub_vibe_nodes.values()) / len(sub_vibe_nodes) if sub_vibe_nodes else 0
    }
}

with open('ananki_outputs/sub_vibe_map.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Saved to: ananki_outputs/sub_vibe_map.json")

print(f"\n" + "="*70)
print("SUB-VIBE MAP CREATED!")
print("="*70)
print(f"\nTotal sub-vibes: {len(sub_vibe_nodes)}")
print(f"Total songs in sub-vibes: {output['stats']['total_songs_in_sub_vibes']}")
print(f"Average songs per sub-vibe: {output['stats']['avg_songs_per_sub_vibe']:.0f}")

print("\nSub-vibes created:")
for sub_vibe in sorted(sub_vibe_nodes.keys()):
    count = sub_vibe_nodes[sub_vibe]['song_count']
    parent = sub_vibe_nodes[sub_vibe]['parent_vibe']
    print(f"  {sub_vibe}: {count} songs (parent: {parent})")