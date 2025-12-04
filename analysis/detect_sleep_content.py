"""
DETECTOR: Generic Sleep/Ambient/Wellness Content
=================================================
Finds songs that are likely generic sleep playlists, ambient soundscapes,
meditation music, etc. rather than actual songs with emotional context.

TIGHT FILTER - Only flags when BOTH artist AND title suggest generic content.
Real artists like "Sleep Token", "Sleeping At Last" won't be flagged.
"""

import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

t = json.load(open('core/tapestry.json', encoding='utf-8'))

# Generic/wellness artist name patterns (not real artist names)
GENERIC_ARTIST_PATTERNS = [
    r'relax(ing|ation)?\s*(music|sounds?)?',
    r'sleep(ing)?\s*(music|sounds?)?',
    r'meditation\s*(music)?',
    r'calm(ing)?\s*(music|sounds?)?',
    r'ambient\s*(music|sounds?)?',
    r'nature\s*sounds?',
    r'white\s*noise',
    r'stress\s*relief',
    r'healing\s*(music|sounds?)?',
    r'spa\s*music',
    r'yoga\s*music',
    r'asmr',
    r'silent\s*rhythm',
    r'peaceful\s*(music|piano)?',
    r'soothing\s*(music|sounds?)?',
]

# Generic/wellness title patterns
GENERIC_TITLE_PATTERNS = [
    r'deep\s*(healing)?\s*sleep',
    r'stress\s*relief',
    r'relaxation\s*(music)?',
    r'soundscape',
    r'white\s*noise',
    r'rain\s*sounds?',
    r'ocean\s*(waves|sounds?)',
    r'nature\s*sounds?',
    r'meditation\s*music',
    r'calming\s*(music|sounds?)',
    r'sleep\s*music',
    r'healing\s*(music|frequency|sounds?)',
    r'ambient\s*mix',
    r'spa\s*music',
]

def is_generic_content(song):
    artist = song.get('artist', '').lower()
    title = song.get('song', '').lower()
    
    artist_flags = []
    title_flags = []
    
    # Check artist against generic patterns
    for pattern in GENERIC_ARTIST_PATTERNS:
        if re.search(pattern, artist):
            artist_flags.append(pattern)
    
    # Check title against generic patterns
    for pattern in GENERIC_TITLE_PATTERNS:
        if re.search(pattern, title):
            title_flags.append(pattern)
    
    # Only flag if BOTH artist AND title match generic patterns
    # OR if artist is very obviously generic (like "Relaxing Music for Stress Relief")
    is_suspicious = (len(artist_flags) > 0 and len(title_flags) > 0) or len(artist_flags) >= 2
    
    return is_suspicious, artist_flags, title_flags

# Find suspicious content
suspicious = []
for vibe, data in t['vibes'].items():
    for song in data.get('songs', []):
        is_generic, artist_flags, title_flags = is_generic_content(song)
        if is_generic:
            suspicious.append({
                'vibe': vibe,
                'artist': song.get('artist'),
                'song': song.get('song'),
                'artist_flags': artist_flags,
                'title_flags': title_flags,
                'comment_preview': song.get('comment_text', '')[:150]
            })

print(f"Found {len(suspicious)} generic sleep/ambient tracks:\n")
print("=" * 70)
for s in suspicious:
    print(f"\n{s['artist']} - {s['song']}")
    print(f"  Vibe: {s['vibe']}")
    print(f"  Artist flags: {s['artist_flags']}")
    print(f"  Title flags: {s['title_flags']}")
    print(f"  Comment: {s['comment_preview']}...")
print("\n" + "=" * 70)
print(f"\nTotal: {len(suspicious)} generic tracks to review")
