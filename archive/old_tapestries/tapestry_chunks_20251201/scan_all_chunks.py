import json
import re
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def smart_quality_check(chunk_path):
    """Smarter quality check - avoids false positives"""
    
    with open(chunk_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    issues = []
    total_songs = 0
    
    for vibe, vibe_data in data.get('vibes', {}).items():
        for song in vibe_data.get('songs', []):
            total_songs += 1
            comment = song.get('comment_text', '').strip()
            comment_lower = comment.lower()
            artist = song.get('artist', '')
            song_name = song.get('song', '')
            
            # TRUE NEGATIVE patterns - actually criticizing the song
            is_negative = False
            neg_reason = ""
            
            # "this song is [negative]" patterns
            if re.search(r'this (song|track|one) (is|sounds?|feels?) (bad|boring|weak|terrible|awful|trash|garbage|meh|disappointing)', comment_lower):
                is_negative = True
                neg_reason = "Direct criticism of song"
            
            # "not impressed" / "missing something" about the song itself
            if re.search(r'(song|track|drop|beat|hook|chorus) (is )?(not |isn\'t )?(impressive|good|great)', comment_lower):
                is_negative = True
                neg_reason = "Song element criticized"
            
            if 'missing something' in comment_lower and 'song' in comment_lower[:50]:
                is_negative = True
                neg_reason = "Song missing something"
            
            # "overrated/overhyped" 
            if re.search(r'\b(overrated|overhyped)\b', comment_lower):
                is_negative = True
                neg_reason = "Called overrated/overhyped"
            
            # "garbage/trash" when talking about the music
            if re.search(r'(sounds?|music|song|this) (like |is )?(garbage|trash|terrible|awful)', comment_lower):
                is_negative = True
                neg_reason = "Called garbage/trash"
            
            if is_negative:
                issues.append({
                    'type': 'NEGATIVE_SENTIMENT',
                    'reason': neg_reason,
                    'artist': artist,
                    'song': song_name,
                    'comment': comment[:300],
                    'vibe': vibe
                })
                continue
            
            # NON-EMOTIONAL - about something other than the music/feelings
            is_non_emotional = False
            non_reason = ""
            
            # Self-promotion
            if re.search(r'(check out|subscribe|follow) (my|me|us)', comment_lower):
                is_non_emotional = True
                non_reason = "Self-promotion"
            
            # Just asking what brought people here (no emotional content)
            if re.search(r'^(what|who) (brought|brings|app|game|movie|show)', comment_lower):
                is_non_emotional = True
                non_reason = "Just asking source"
            
            # Pure timestamp with nothing meaningful
            if re.match(r'^\d+:\d+\s*$', comment.strip()):
                is_non_emotional = True
                non_reason = "Just a timestamp"
            
            # "you deserve more subscribers" type comments
            if re.search(r'(deserve|need|should have) more (subscribers|views|recognition)', comment_lower):
                is_non_emotional = True
                non_reason = "About channel metrics, not song"
            
            if is_non_emotional:
                issues.append({
                    'type': 'NON_EMOTIONAL',
                    'reason': non_reason,
                    'artist': artist,
                    'song': song_name,
                    'comment': comment[:300],
                    'vibe': vibe
                })
                continue
            
            # TOO SHORT (under 15 chars and not meaningful)
            if len(comment) < 15:
                issues.append({
                    'type': 'TOO_SHORT',
                    'artist': artist,
                    'song': song_name,
                    'comment': comment,
                    'vibe': vibe
                })
    
    return issues, total_songs

# Run on all chunks
base_path = 'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks'

all_issues = []
total_all = 0

for i in range(1, 12):
    chunk_num = f"{i:02d}" if i < 10 else str(i)
    path = os.path.join(base_path, f'tapestry_chunk_{chunk_num}_CLEANED.json')
    if os.path.exists(path):
        issues, total = smart_quality_check(path)
        total_all += total
        for issue in issues:
            issue['chunk'] = i
            all_issues.append(issue)
        print(f"Chunk {i:02d}: {total} songs, {len(issues)} issues")

print(f"\n{'='*60}")
print(f"TOTAL: {total_all} songs, {len(all_issues)} issues")
print('='*60)

if all_issues:
    print("\nALL ISSUES FOUND:")
    for issue in all_issues:
        print(f"\n  Chunk {issue['chunk']}")
        print(f"  Type: {issue['type']}")
        print(f"  Artist: {issue['artist']}")
        print(f"  Song: {issue['song']}")
        print(f"  Vibe: {issue['vibe']}")
        print(f"  Comment: {issue['comment'][:150]}...")
        if 'reason' in issue:
            print(f"  Reason: {issue['reason']}")
