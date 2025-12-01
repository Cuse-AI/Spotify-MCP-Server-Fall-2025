import json
import re
from collections import defaultdict

# Quality check patterns - comments that should have been removed
SHOULD_REMOVE_PATTERNS = [
    # Generic praise
    r'^(love this|so good|amazing|beautiful|perfect|fire|best song|great song)[\s!\.]*$',
    r'^this (is )?(so )?(good|amazing|beautiful|perfect)[\s!\.]*$',
    # Fan checks / timestamps
    r'who.*here.*\d{4}',
    r'still listening.*\d{4}',
    r'anyone.*\d{4}',
    r'\d{4} anyone',
    # Viral hype
    r'don\'?t let this (song )?die',
    r'future generation',
    r'goes viral',
    r'was here',
    r'leaving this here',
    # Artist-only praise (no emotional context)
    r'^[A-Za-z\s]+ (is|are) (so )?(amazing|incredible|the best|perfect)[\s!\.]*$',
    # Empty or too short
]

def analyze_comment_quality(comment):
    """Returns (is_good, issues) tuple"""
    if not comment or len(comment.strip()) < 20:
        return False, ["too_short"]
    
    comment_lower = comment.lower().strip()
    issues = []
    
    # Check for patterns that should have been removed
    for pattern in SHOULD_REMOVE_PATTERNS:
        if re.search(pattern, comment_lower, re.IGNORECASE):
            issues.append(f"matches_bad_pattern: {pattern[:30]}")
    
    # Check for GOOD indicators
    good_indicators = []
    
    # Personal story indicators
    if any(x in comment_lower for x in ['i ', 'my ', 'me ', 'we ', 'our ']):
        good_indicators.append("first_person")
    
    # Emotional depth
    emotional_words = ['cry', 'cried', 'tears', 'heart', 'soul', 'pain', 'hurt', 'healing', 
                       'broke', 'lost', 'miss', 'remember', 'feel', 'felt', 'love', 'loved']
    if sum(1 for w in emotional_words if w in comment_lower) >= 2:
        good_indicators.append("emotional_depth")
    
    # Story context
    story_words = ['when i', 'years ago', 'remember when', 'back when', 'used to', 
                   'reminds me', 'makes me', 'every time', 'this song']
    if any(x in comment_lower for x in story_words):
        good_indicators.append("story_context")
    
    # Life events
    life_events = ['breakup', 'break up', 'divorce', 'wedding', 'funeral', 'passed away',
                   'died', 'cancer', 'hospital', 'lost my', 'ex ', 'relationship']
    if any(x in comment_lower for x in life_events):
        good_indicators.append("life_event")
    
    # Length bonus
    if len(comment) > 100:
        good_indicators.append("good_length")
    if len(comment) > 200:
        good_indicators.append("great_length")
    
    is_good = len(issues) == 0 and len(good_indicators) >= 1
    
    return is_good, issues if issues else good_indicators

def analyze_chunk(chunk_num):
    """Analyze a cleaned chunk for quality and stats"""
    
    path = f'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_{chunk_num}_CLEANED.json'
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stats = defaultdict(int)
    quality_issues = []
    borderline = []
    gold = []
    
    for vibe_name, vibe_data in data['vibes'].items():
        for song in vibe_data.get('songs', []):
            stats[vibe_name] += 1
            
            comment = song.get('comment_text', '')
            is_good, details = analyze_comment_quality(comment)
            
            entry = {
                'artist': song['artist'],
                'song': song['song'],
                'vibe': vibe_name,
                'comment': comment[:200],
                'details': details
            }
            
            if not is_good and details and any('matches_bad' in d for d in details):
                quality_issues.append(entry)
            elif is_good and 'great_length' in details and ('life_event' in details or 'emotional_depth' in details):
                gold.append(entry)
            elif len(comment) < 60 or (is_good and len(details) == 1):
                borderline.append(entry)
    
    return stats, quality_issues, borderline, gold

# Analyze chunk 01
print("=" * 80)
print("CHUNK 01 DEEP QUALITY ANALYSIS")
print("=" * 80)

stats, issues, borderline, gold = analyze_chunk("01")

print("\n[STATS] VIBE/SUB-VIBE DISTRIBUTION:")
print("-" * 40)
total = 0
for vibe, count in sorted(stats.items()):
    print(f"  {vibe}: {count}")
    total += count
print(f"\n  TOTAL: {total}")

print("\n\n[ISSUES] POTENTIAL QUALITY ISSUES (should review):")
print("-" * 40)
if issues:
    for i, entry in enumerate(issues[:20], 1):
        artist = entry['artist'].encode('ascii', 'replace').decode('ascii')
        song = entry['song'].encode('ascii', 'replace').decode('ascii')
        comment = entry['comment'].encode('ascii', 'replace').decode('ascii')
        print(f"\n{i}. {artist} - {song}")
        print(f"   Vibe: {entry['vibe']}")
        print(f"   Comment: {comment[:100]}...")
        print(f"   Issues: {entry['details']}")
else:
    print("  None found!")

print("\n\n[BORDERLINE] BORDERLINE COMMENTS (short or weak context):")
print("-" * 40)
for i, entry in enumerate(borderline[:15], 1):
    artist = entry['artist'].encode('ascii', 'replace').decode('ascii')
    song = entry['song'].encode('ascii', 'replace').decode('ascii')
    comment = entry['comment'].encode('ascii', 'replace').decode('ascii')
    print(f"\n{i}. {artist} - {song}")
    print(f"   Comment: {comment[:80]}...")
    print(f"   Details: {entry['details']}")

print("\n\n[GOLD] GOLD COMMENTS (exemplary emotional context):")
print("-" * 40)
for i, entry in enumerate(gold[:10], 1):
    artist = entry['artist'].encode('ascii', 'replace').decode('ascii')
    song = entry['song'].encode('ascii', 'replace').decode('ascii')
    comment = entry['comment'].encode('ascii', 'replace').decode('ascii')
    print(f"\n{i}. {artist} - {song}")
    print(f"   Vibe: {entry['vibe']}")
    print(f"   Comment: {comment[:150]}...")
