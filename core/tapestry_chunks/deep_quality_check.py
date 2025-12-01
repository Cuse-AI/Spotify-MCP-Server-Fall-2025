import json
import re

def deep_quality_check(chunk_path):
    """More rigorous quality check for tapestry chunks"""
    
    with open(chunk_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    issues = []
    total_songs = 0
    
    # Negative sentiment patterns - song is bad/disappointing
    negative_patterns = [
        r'\bnot (that )?good\b',
        r'\bdisappoint',
        r'\boverhyped\b',
        r'\boverrated\b',
        r'\bboring\b',
        r'\bweak\b',
        r'\bworse\b',
        r'\bworst\b',
        r'\bhate (this|it|the)\b',
        r'\bdon\'?t like\b',
        r'\bnot (a )?fan\b',
        r'\bskip(ped)?\b',
        r'\btrash\b',
        r'\bgarbage\b',
        r'\bterrible\b',
        r'\bawful\b',
        r'\bmissing something\b',
        r'\bnot impressive\b',
        r'\bdrop is not\b',
        r'\bcould be better\b',
        r'\blet( me)? down\b',
        r'\bmeh\b',
        r'\bforgettable\b',
    ]
    
    # Non-emotional/technical patterns
    non_emotional_patterns = [
        r'^(first|1st)[\!\.]?$',
        r'^like\.?$',
        r'^nice\.?$',
        r'^cool\.?$',
        r'^great\.?$',
        r'^amazing\.?$',
        r'^wow\.?$',
        r'^yes\.?$',
        r'^no\.?$',
        r'subscribe',
        r'check out my',
        r'link in bio',
        r'follow me',
        r'^\d+:\d+',  # Timestamps only
        r'^[^\w\s]+$',  # Only symbols/emojis
        r'algorithm brought me',
        r'who\'?s (here|watching) (in|from) \d{4}',
        r'anyone (here )?(in|from) \d{4}',
        r'\d{4} anyone',
        r'still (listening|watching|here)',
        r'who else (is )?(here|listening)',
        r'came (here )?from',
        r'what (app|game|movie|show|video)',
        r'what brings you here',
        r'how did (you|i) (find|get)',
    ]
    
    # Generic/low-value patterns
    generic_patterns = [
        r'^this (is )?(a )?(song|track|music)\.?$',
        r'^(the )?artist is',
        r'^released in \d{4}',
        r'^from (the )?(album|ep)',
        r'spotify\.com',
        r'apple music',
        r'youtube\.com',
        r'^rip\b',  # Just "RIP" without context
    ]
    
    for vibe, vibe_data in data.get('vibes', {}).items():
        for song in vibe_data.get('songs', []):
            total_songs += 1
            comment = song.get('comment_text', '').strip()
            comment_lower = comment.lower()
            artist = song.get('artist', '')
            song_name = song.get('song', '')
            
            # Check 1: Negative sentiment about the song
            for pattern in negative_patterns:
                if re.search(pattern, comment_lower):
                    issues.append({
                        'type': 'NEGATIVE_SENTIMENT',
                        'pattern': pattern,
                        'artist': artist,
                        'song': song_name,
                        'comment': comment[:200],
                        'vibe': vibe
                    })
                    break
            
            # Check 2: Non-emotional/technical comments
            for pattern in non_emotional_patterns:
                if re.search(pattern, comment_lower):
                    issues.append({
                        'type': 'NON_EMOTIONAL',
                        'pattern': pattern,
                        'artist': artist,
                        'song': song_name,
                        'comment': comment[:200],
                        'vibe': vibe
                    })
                    break
            
            # Check 3: Generic/low-value
            for pattern in generic_patterns:
                if re.search(pattern, comment_lower):
                    issues.append({
                        'type': 'GENERIC_LOW_VALUE',
                        'pattern': pattern,
                        'artist': artist,
                        'song': song_name,
                        'comment': comment[:200],
                        'vibe': vibe
                    })
                    break
            
            # Check 4: Very short comments (under 20 chars)
            if len(comment) < 20:
                issues.append({
                    'type': 'TOO_SHORT',
                    'artist': artist,
                    'song': song_name,
                    'comment': comment,
                    'vibe': vibe
                })
            
            # Check 5: Comment is just artist/song name
            if comment_lower == artist.lower() or comment_lower == song_name.lower():
                issues.append({
                    'type': 'ARTIST_SONG_AS_COMMENT',
                    'artist': artist,
                    'song': song_name,
                    'comment': comment,
                    'vibe': vibe
                })
    
    return issues, total_songs

if __name__ == '__main__':
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    chunk_num = sys.argv[1] if len(sys.argv) > 1 else '10'
    path = f'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_{chunk_num}_CLEANED.json'
    
    print(f"=== DEEP QUALITY CHECK: CHUNK {chunk_num} ===\n")
    
    issues, total = deep_quality_check(path)
    
    # Group by type
    by_type = {}
    for issue in issues:
        t = issue['type']
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(issue)
    
    print(f"Total songs: {total}")
    print(f"Total issues found: {len(issues)}\n")
    
    for issue_type, items in sorted(by_type.items()):
        print(f"\n{'='*60}")
        print(f"{issue_type}: {len(items)} issues")
        print('='*60)
        for item in items[:10]:  # Show first 10 of each type
            print(f"\n  Artist: {item['artist']}")
            print(f"  Song: {item['song']}")
            print(f"  Vibe: {item['vibe']}")
            print(f"  Comment: {item['comment'][:150]}...")
            if 'pattern' in item:
                print(f"  Matched: {item['pattern']}")
        if len(items) > 10:
            print(f"\n  ... and {len(items) - 10} more")
