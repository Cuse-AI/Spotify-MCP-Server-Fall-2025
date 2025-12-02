import json
import sys

chunk_num = sys.argv[1] if len(sys.argv) > 1 else "01"

# Load chunk
input_path = f'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_{chunk_num}_of_11.json'
with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Patterns that indicate LOW QUALITY comments to REMOVE
low_quality_patterns = [
    'appreciate how beautiful',
    'let this song die',
    'future generations',
    'Any fans of',
    'fans here?',
    "Who's here",
    'who else is here',
    'still listening in 202',
    'People slept on',
    'slept on it',
    'found it on a skate video',
    'I was here',
    'Write I was here',
    'Leaving this here so',
    'before this goes viral',
    'goes viral',
    'masterpiece released',
    'came here from',
    'who came from',
    'algorithm brought me',
    'the algorithm',
    'notification squad',
    'early gang',
    'Anyone else here from',
    'Here from',
    'came from tiktok',
    'tiktok brought me',
]

def is_low_quality(comment_text):
    if not comment_text:
        return True
    text_lower = comment_text.lower()
    
    # Check for low quality patterns
    for pattern in low_quality_patterns:
        if pattern.lower() in text_lower:
            return True
    
    # Check if comment is too short AND generic
    if len(comment_text) < 50:
        generic_short = ['love this', 'so good', 'amazing', 'beautiful', 'perfect', 'fire', 'best song', 'this slaps', 'banger']
        for g in generic_short:
            if g in text_lower:
                return True
    
    return False

# Process and filter
cleaned_data = {'vibes': {}}
removed_count = 0
kept_count = 0
removed_songs = []

for vibe_name, vibe_data in data['vibes'].items():
    cleaned_songs = []
    for song in vibe_data.get('songs', []):
        comment = song.get('comment_text', '')
        if is_low_quality(comment):
            removed_count += 1
            removed_songs.append({
                'artist': song['artist'],
                'song': song['song'],
                'comment': comment[:150],
                'vibe': vibe_name
            })
        else:
            cleaned_songs.append(song)
            kept_count += 1
    
    if cleaned_songs:
        cleaned_data['vibes'][vibe_name] = {'songs': cleaned_songs}

print(f'=== CHUNK {chunk_num} CLEANING RESULTS ===')
print(f'Kept: {kept_count}')
print(f'Removed: {removed_count}')
print(f'Total: {kept_count + removed_count}')
print()

if removed_songs:
    print('=== REMOVED SONGS ===')
    for r in removed_songs:
        # Encode safely for console output
        artist = r['artist'].encode('ascii', 'replace').decode('ascii')
        song = r['song'].encode('ascii', 'replace').decode('ascii')
        comment = r['comment'].encode('ascii', 'replace').decode('ascii')
        print(f"- {artist} - {song}")
        print(f"  Vibe: {r['vibe']}")
        print(f"  Comment: {comment}...")
        print()

# Save cleaned version
output_path = f'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_{chunk_num}_CLEANED.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print(f'Saved to: {output_path}')
