# Generate all 23 YouTube scrapers
# Uses Chill scraper as template

import re

# Read the Chill template
with open('scrape_chill.py', 'r', encoding='utf-8') as f:
    template = f.read()

# All 23 vibes with their search queries
scrapers_to_create = [
    ('angry', 'Angry', [
        'angry music playlist',
        'rage songs',
        'aggressive music mix',
        'furious playlist',
        'cathartic anger songs',
        'frustrated music'
    ]),
    ('anxious', 'Anxious', [
        'anxious music playlist',
        'nervous energy songs',
        'panic attack playlist',
        'overwhelming feelings music',
        'existential dread songs',
        'calming anxiety music'
    ]),
    ('bitter', 'Bitter', [
        'bitter breakup songs',
        'resentful music playlist',
        'betrayal songs',
        'bitter feelings playlist',
        'songs about being wronged',
        'resentment music'
    ]),
    ('bored', 'Bored', [
        'bored music playlist',
        'monotonous songs',
        'restless music',
        'waiting room playlist',
        'understimulated songs',
        'boring day music'
    ]),
    ('chaotic', 'Chaotic', [
        'chaotic music playlist',
        'frantic songs',
        'overwhelming music',
        'scattered energy playlist',
        'unhinged songs',
        'frenetic music mix'
    ]),
    ('confident', 'Confident', [
        'confidence music playlist',
        'bold songs',
        'boss music mix',
        'powerful confidence playlist',
        'unstoppable music',
        'self assured songs'
    ]),
    ('dark', 'Dark', [
        'dark music playlist',
        'gothic songs',
        'brooding music mix',
        'haunting playlist',
        'noir music',
        'apocalyptic songs'
    ]),
    ('drive', 'Drive', [
        'driving music playlist',
        'road trip songs',
        'highway music mix',
        'night drive playlist',
        'scenic drive music',
        'alone in car songs'
    ]),
    ('energy', 'Energy', [
        'energy music playlist',
        'pump up songs',
        'workout music mix',
        'running playlist',
        'sports hype music',
        'high energy songs'
    ]),
    ('excited', 'Excited', [
        'excited music playlist',
        'hyper songs',
        'thrilled music mix',
        'anticipation playlist',
        'pumped up songs',
        'exhilarating music'
    ]),
    ('grateful', 'Grateful', [
        'grateful music playlist',
        'thankful songs',
        'appreciation music',
        'gratitude playlist',
        'blessed feeling songs',
        'counting blessings music'
    ]),
    ('happy', 'Happy', [
        'happy music playlist',
        'feel good songs',
        'joyful music mix',
        'upbeat happy playlist',
        'cheerful songs',
        'sunshine music'
    ]),
    ('hopeful', 'Hopeful', [
        'hopeful music playlist',
        'optimistic songs',
        'looking forward music',
        'hope playlist',
        'better tomorrow songs',
        'inspiring hope music'
    ]),
    ('introspective', 'Introspective', [
        'introspective music playlist',
        'deep thinking songs',
        'contemplative music',
        'self reflection playlist',
        'philosophical songs',
        'pensive music'
    ]),
    ('jealous', 'Jealous', [
        'jealous songs playlist',
        'envious music',
        'jealousy songs',
        'seeing ex playlist',
        'covet songs',
        'envy music'
    ]),
    ('night', 'Night', [
        'late night music playlist',
        '3am songs',
        'midnight vibes',
        'night time music',
        'insomnia playlist',
        'nighttime feelings'
    ]),
    ('nostalgic', 'Nostalgic', [
        'nostalgic music playlist',
        'throwback songs',
        'memories music',
        'nostalgia playlist',
        'reminiscing songs',
        'good old days music'
    ]),
    ('party', 'Party', [
        'party music playlist',
        'dance songs',
        'club music mix',
        'hype party playlist',
        'pregame music',
        'party vibes'
    ]),
    ('peaceful', 'Peaceful', [
        'peaceful music playlist',
        'calm songs',
        'tranquil music',
        'serene playlist',
        'zen music',
        'peace and calm songs'
    ]),
    ('playful', 'Playful', [
        'playful music playlist',
        'silly songs',
        'fun lighthearted music',
        'mischievous playlist',
        'whimsical music',
        'goofy songs'
    ]),
    ('romantic', 'Romantic', [
        'romantic music playlist',
        'love songs',
        'romantic vibes',
        'date night playlist',
        'intimate music',
        'couple songs'
    ]),
    ('sad', 'Sad', [
        'sad music playlist',
        'crying songs',
        'heartbreak music',
        'melancholic playlist',
        'depressing songs',
        'sadness music'
    ])
]

# Generate each scraper
for vibe_lower, vibe_title, queries in scrapers_to_create:
    content = template
    
    # Replace class name
    content = content.replace('ChillYouTubeScraper', f'{vibe_title}YouTubeScraper')
    
    # Replace vibe names in strings
    content = content.replace('CHILL VIBES', f'{vibe_title.upper()} VIBES')
    content = content.replace('Chill vibes', f'{vibe_title} vibes')
    content = content.replace("'Chill'", f"'{vibe_title}'")
    content = content.replace('chill_youtube_extraction', f'{vibe_lower}_youtube_extraction')
    content = content.replace('scrape_chill_vibes', f'scrape_{vibe_lower}_vibes')
    
    # Replace queries
    old_queries = """queries = [
            'chill vibes playlist',
            'relaxing music mix',
            'chill songs to vibe to',
            'laid back playlist',
            'mellow music mix',
            'sunday morning chill'
        ]"""
    
    new_queries = f"queries = {queries}"
    content = content.replace(old_queries, new_queries)
    
    # Write file
    with open(f'scrape_{vibe_lower}.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Created scrape_{vibe_lower}.py')

print('\\nDone! All 22 scrapers created.')
print('\\nTotal YouTube scrapers: 23')
