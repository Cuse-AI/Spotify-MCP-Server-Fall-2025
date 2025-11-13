import json
import random

# Load the tapestry with all the songs
with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

all_songs = tapestry['vibes']

# The 20 vibes that were selected
selected_vibes = [
    "Sad - Crying",
    "Energy - Pump Up", 
    "Romantic - Anniversary",
    "Happy - Feel Good",
    "Dark - Haunting",
    "Hopeful - New Beginnings",
    "Nostalgic - Simpler Times",
    "Dark - Villain Arc",
    "Sad - Depressive",
    "Night - Midnight Drive",
    "Confident - Unstoppable",
    "Peaceful - Quiet Reflection",
    "Hopeful - New Beginnings",
    "Peaceful - Serene",
    "Grateful - Warm Appreciation",
    "Party - Dance",
    "Bored - Understimulated",
    "Nostalgic - 90s",
    "Night - Midnight Drive",
    "Chaotic - Scattered"
]

prompts = [
    "I'm feeling really sad after my breakup",
    "Need pump up music for my workout",
    "Chill vibes for a Sunday morning coffee",
    "I'm so happy and celebrating good news!",
    "I'm sad but also kind of angry about being betrayed",
    "Feeling hopeful but still a little anxious about the future",
    "Nostalgic and melancholic about my childhood",
    "Confident but with a dark edge, like a villain",
    "Music that feels like 3am thoughts spiraling",
    "Songs for when you're driving alone through a neon-lit city at night",
    "I want to feel like the main character in a coming-of-age movie",
    "Music that sounds like rain on a window while you're safe inside",
    "Soundtrack for exploring an abandoned space station",
    "Music for a quiet morning in a cottage in the woods",
    "Songs that feel like wandering through a misty forest at dawn",
    "I'm at a underground rave in an alternate timeline",
    "I'm bored but restless and can't settle on anything",
    "Feeling grateful but also a little sad it has to end",
    "Music for when you're excited about adventure but also terrified",
    "I need songs that are both chaotic and weirdly playful"
]

print('\n' + '='*80)
print('YOUR TAPESTRY PLAYLIST - 20 SONGS TO LISTEN TO')
print('='*80)

for i, (prompt, vibe) in enumerate(zip(prompts, selected_vibes), 1):
    print(f'\n[{i}] "{prompt}"')
    print(f'    -> Vibe: {vibe}')
    
    if vibe in all_songs and all_songs[vibe]['songs']:
        song = random.choice(all_songs[vibe]['songs'])
        artist = song.get('artist', 'Unknown Artist')
        song_name = song.get('song', 'Unknown Song')
        print(f'    LISTEN: {artist} - {song_name}')
    else:
        print(f'    No songs found in this vibe')

print('\n' + '='*80)
print('Enjoy your journey through the Tapestry!')
print('='*80)
