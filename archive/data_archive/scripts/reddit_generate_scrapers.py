# Quick script to generate remaining scrapers
import re

template = open('scrape_bored.py').read()

scrapers_to_create = [
    ('chaotic', 'Chaotic', ['chaotic music', 'frantic songs', 'overwhelming playlist', 'scattered energy music', 'unhinged songs', 'frenetic music']),
    ('confident', 'Confident', ['confidence music', 'bold songs playlist', 'boss music', 'powerful confidence songs', 'unstoppable music', 'self assured playlist']),
    ('excited', 'Excited', ['excited music playlist', 'hyper songs', 'thrilled music', 'anticipation songs', 'pumped up excited', 'exhilarating music']),
    ('grateful', 'Grateful', ['grateful music', 'thankful songs playlist', 'appreciation music', 'gratitude songs', 'blessed feeling music', 'counting blessings songs']),
    ('hopeful', 'Hopeful', ['hopeful music playlist', 'optimistic songs', 'looking forward music', 'hope songs', 'better tomorrow music', 'inspiring hope']),
    ('jealous', 'Jealous', ['jealous songs playlist', 'envious music', 'jealousy songs', 'seeing ex with someone', 'covet songs', 'want what they have music']),
    ('playful', 'Playful', ['playful music', 'silly songs playlist', 'fun lighthearted music', 'mischievous songs', 'whimsical playlist', 'goofy music'])
]

for vibe_lower, vibe_title, queries in scrapers_to_create:
    content = template
    
    # Replace class name
    content = content.replace('BoredSmartScraper', f'{vibe_title}SmartScraper')
    
    # Replace vibe names
    content = content.replace('BORED', vibe_title.upper())
    content = content.replace('Bored', vibe_title)
    content = content.replace('bored', vibe_lower)
    
    # Replace queries
    old_queries = '''queries = [
            'bored music playlist',
            'monotonous songs',
            'restless music',
            'waiting room music',
            'understimulated playlist',
            'songs for boring day'
        ]'''
    
    new_queries = f"queries = {queries}"
    content = content.replace(old_queries, f"queries = {queries}")
    
    # Write file
    with open(f'scrape_{vibe_lower}.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Created scrape_{vibe_lower}.py')

print('Done! All 7 scrapers created.')
