import json
import re

def check_chunk_quality(chunk_path):
    """Check for quality issues in a tapestry chunk"""
    
    with open(chunk_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    issues = []
    total_songs = 0
    
    for vibe, vibe_data in data.get('vibes', {}).items():
        for song in vibe_data.get('songs', []):
            total_songs += 1
            artist = song.get('artist', '').strip().lower()
            song_name = song.get('song', '').strip().lower()
            comment = song.get('comment_text', '').strip()
            comment_lower = comment.lower()
            
            # Check 1: Artist name IS the comment (or nearly)
            if comment_lower == artist or comment_lower == song_name:
                issues.append({
                    'type': 'ARTIST/SONG_AS_COMMENT',
                    'artist': song.get('artist'),
                    'song': song.get('song'),
                    'comment': comment,
                    'vibe': vibe
                })
            
            # Check 2: Comment is just artist name with minor additions
            if len(comment) < 50 and artist in comment_lower:
                # Check if comment is basically just the artist name
                cleaned = comment_lower.replace(artist, '').strip()
                if len(cleaned) < 10:
                    issues.append({
                        'type': 'MINIMAL_ARTIST_COMMENT',
                        'artist': song.get('artist'),
                        'song': song.get('song'),
                        'comment': comment,
                        'vibe': vibe
                    })
            
            # Check 3: Very short comments (less than 20 chars)
            if len(comment) < 20:
                issues.append({
                    'type': 'TOO_SHORT',
                    'artist': song.get('artist'),
                    'song': song.get('song'),
                    'comment': comment,
                    'vibe': vibe
                })
            
            # Check 4: Generic viral patterns
            viral_patterns = [
                r'^who.?s here in 20\d\d',
                r'^anyone.? 20\d\d',
                r'^still listening',
                r'^legend.?ary',
                r'^first\s*$',
                r'^second\s*$',
                r'like if you',
                r'thumbs up if',
            ]
            for pattern in viral_patterns:
                if re.search(pattern, comment_lower):
                    issues.append({
                        'type': 'VIRAL_PATTERN',
                        'artist': song.get('artist'),
                        'song': song.get('song'),
                        'comment': comment,
                        'pattern': pattern,
                        'vibe': vibe
                    })
                    break
            
            # Check 5: Empty or placeholder comments
            if not comment or comment in ['...', '-', 'N/A', 'n/a', 'none']:
                issues.append({
                    'type': 'EMPTY_COMMENT',
                    'artist': song.get('artist'),
                    'song': song.get('song'),
                    'comment': comment,
                    'vibe': vibe
                })
    
    return {
        'total_songs': total_songs,
        'issues_found': len(issues),
        'issues': issues
    }

# Run on current chunk
chunk_num = '10'
path = f'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_0{chunk_num}_CLEANED.json'

print(f"=== QUALITY CHECK: CHUNK {chunk_num:02d} ===\n")
results = check_chunk_quality(path)

print(f"Total songs: {results['total_songs']}")
print(f"Issues found: {results['issues_found']}\n")

if results['issues']:
    # Group by type
    by_type = {}
    for issue in results['issues']:
        t = issue['type']
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(issue)
    
    for issue_type, items in by_type.items():
        print(f"\n--- {issue_type} ({len(items)}) ---")
        for item in items[:5]:  # Show first 5 of each type
            print(f"  {item['artist']} - {item['song']}")
            print(f"    Comment: \"{item['comment'][:80]}...\"" if len(item.get('comment','')) > 80 else f"    Comment: \"{item.get('comment','')}\"")
            print(f"    Vibe: {item['vibe']}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
else:
    print("[OK] No quality issues detected!")
