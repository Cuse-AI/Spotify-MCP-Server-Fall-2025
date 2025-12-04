import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

t = json.load(open('core/tapestry.json', encoding='utf-8'))

def looks_like_lyrics(comment):
    if not comment:
        return False, ''
    
    # Red flags for lyrics
    lines = comment.split('\n')
    
    # 1. Too many short lines (verse structure)
    short_lines = sum(1 for l in lines if 5 < len(l.strip()) < 50)
    if len(lines) > 5 and short_lines / len(lines) > 0.7:
        return True, 'verse structure'
    
    # 2. Repetitive phrases (chorus)
    words = comment.lower().split()
    if len(words) > 20:
        phrases = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        phrase_counts = {}
        for p in phrases:
            phrase_counts[p] = phrase_counts.get(p, 0) + 1
        max_repeat = max(phrase_counts.values()) if phrase_counts else 0
        if max_repeat >= 4:
            return True, 'repetitive phrases'
    
    # 3. Very long comment with no personal pronouns indicating experience
    personal = ['i ', 'my ', 'me ', 'we ', 'our ', 'this song', 'this track', 'reminds me', 'makes me', 'when i', 'feel']
    has_personal = any(p in comment.lower() for p in personal)
    if len(comment) > 500 and not has_personal:
        return True, 'long without personal context'
    
    # 4. Common lyric patterns
    lyric_patterns = [
        r'oh oh oh',
        r'yeah yeah yeah',
        r'la la la', 
        r'na na na',
        r'ey oh ey oh',
        r'hmm hmm',
        r'ooh ooh',
    ]
    for pattern in lyric_patterns:
        if re.search(pattern, comment.lower()):
            return True, f'lyric pattern: {pattern}'
    
    return False, ''

# Find suspicious comments
suspicious = []
for vibe, data in t['vibes'].items():
    for song in data.get('songs', []):
        comment = song.get('comment_text', '')
        is_lyrics, reason = looks_like_lyrics(comment)
        if is_lyrics:
            suspicious.append({
                'vibe': vibe,
                'song': song.get('song'),
                'artist': song.get('artist'),
                'reason': reason,
                'comment': comment
            })

print(f'Found {len(suspicious)} suspicious comments:\n')
for s in suspicious:
    print('=' * 60)
    print(f"{s['artist']} - {s['song']}")
    print(f"Vibe: {s['vibe']}")
    print(f"Reason: {s['reason']}")
    print(f"Comment: {s['comment'][:200]}...")
    print()
