import json
from collections import defaultdict

# Load tapestry
print("[*] Loading tapestry...")
tapestry = json.load(open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json', encoding='utf-8'))

# Collect all songs
all_songs = []
for vibe_name, vibe_data in tapestry['vibes'].items():
    for song in vibe_data.get('songs', []):
        all_songs.append(song)

total_songs = len(all_songs)
print(f"[*] Total songs: {total_songs}")

# Analyze context
has_ananki = 0
has_comment_text = 0
has_post_title = 0
has_full_context = 0
from_nov27_batch = 0
pre_nov27 = 0

for song in all_songs:
    # Check for emotional context indicators
    ananki_reasoning = song.get('ananki_reasoning', '')
    if ananki_reasoning and len(ananki_reasoning) > 50:  # Substantial reasoning
        has_ananki += 1
    
    if song.get('comment_text') and len(song.get('comment_text', '')) > 20:
        has_comment_text += 1
    
    if song.get('post_title') and len(song.get('post_title', '')) > 5:
        has_post_title += 1
    
    if song.get('full_context') and len(song.get('full_context', '')) > 0:
        has_full_context += 1
    
    # Check data source
    data_source = song.get('data_source', '')
    if 'analyzed_batch_nov27' in data_source:
        from_nov27_batch += 1
    else:
        pre_nov27 += 1

print("\n[CONTEXT ANALYSIS]")
print(f"Songs with Ananki reasoning: {has_ananki}/{total_songs} ({has_ananki*100/total_songs:.1f}%)")
print(f"Songs with comment text: {has_comment_text}/{total_songs} ({has_comment_text*100/total_songs:.1f}%)")
print(f"Songs with post title: {has_post_title}/{total_songs} ({has_post_title*100/total_songs:.1f}%)")
print(f"Songs with full context: {has_full_context}/{total_songs} ({has_full_context*100/total_songs:.1f}%)")

print("\n[DATA SOURCE BREAKDOWN]")
print(f"From Nov 27 batch (analyzed_batch_nov27): {from_nov27_batch} ({from_nov27_batch*100/total_songs:.1f}%)")
print(f"Pre-Nov 27 (older data): {pre_nov27} ({pre_nov27*100/total_songs:.1f}%)")

# Sample analysis
print("\n[SAMPLE SONGS WITH CONTEXT]")
print("\nSample 1 (with full context):")
for song in all_songs[:5]:
    if song.get('ananki_reasoning') and len(song.get('ananki_reasoning', '')) > 100:
        print(f"  Artist: {song.get('artist')}")
        print(f"  Song: {song.get('song')}")
        print(f"  Comment: {song.get('comment_text')[:100]}...")
        print(f"  Reasoning length: {len(song.get('ananki_reasoning', ''))} chars")
        break

# Count by how many context fields filled
print("\n[CONTEXT RICHNESS]")
rich_context_count = 0
for song in all_songs:
    context_fields = 0
    if song.get('ananki_reasoning') and len(song.get('ananki_reasoning', '')) > 50:
        context_fields += 1
    if song.get('comment_text') and len(song.get('comment_text', '')) > 20:
        context_fields += 1
    if song.get('post_title') and len(song.get('post_title', '')) > 5:
        context_fields += 1
    
    if context_fields >= 2:  # At least 2 context fields
        rich_context_count += 1

print(f"Songs with rich context (2+ context fields): {rich_context_count}/{total_songs} ({rich_context_count*100/total_songs:.1f}%)")
print(f"Songs with minimal/no context: {total_songs - rich_context_count}/{total_songs} ({(total_songs-rich_context_count)*100/total_songs:.1f}%)")

print("\n[CONCLUSION]")
emotional_content_pct = has_ananki * 100 / total_songs
if emotional_content_pct > 70:
    print(f"[GOOD] {emotional_content_pct:.1f}% of songs have Ananki emotional analysis!")
elif emotional_content_pct > 50:
    print(f"[OKAY] {emotional_content_pct:.1f}% of songs have Ananki analysis - room for improvement")
else:
    print(f"[WARNING] Only {emotional_content_pct:.1f}% have full emotional context")
