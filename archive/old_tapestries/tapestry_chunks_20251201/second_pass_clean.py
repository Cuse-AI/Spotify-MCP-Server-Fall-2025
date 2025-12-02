import json

# Additional removals identified in manual review
ADDITIONAL_REMOVE = [
    # Too generic / no real emotional context
    ("ROSÉ", "number one girl", "number one on our playlist and in our hearts"),
    ("Madison Bailey", "Honestly", "Already took fav actor now coming for fav artist too"),
    ("Alexander Stewart", "i wish you cheated", "Leaving this comment here so that when someone likes it"),
    # Notification/reminder requests (not emotional context)
    ("Gracie Abrams", "Cool", "THIS SHOULD'VE BEEN A MAIN TRACK"),
]

def should_remove(song):
    comment = song.get('comment_text', '').lower()
    artist = song.get('artist', '')
    song_name = song.get('song', '')
    
    for r_artist, r_song, r_pattern in ADDITIONAL_REMOVE:
        if r_artist.lower() in artist.lower() and r_song.lower() in song_name.lower():
            if r_pattern.lower() in comment:
                return True, r_pattern
    return False, None

# Load and process
path = 'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks/tapestry_chunk_01_CLEANED.json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

removed = []
cleaned_data = {'vibes': {}}

for vibe_name, vibe_data in data['vibes'].items():
    cleaned_songs = []
    for song in vibe_data.get('songs', []):
        remove, reason = should_remove(song)
        if remove:
            removed.append({
                'artist': song['artist'],
                'song': song['song'],
                'reason': reason
            })
        else:
            cleaned_songs.append(song)
    
    if cleaned_songs:
        cleaned_data['vibes'][vibe_name] = {'songs': cleaned_songs}

print(f"Second pass cleanup:")
print(f"Removed: {len(removed)} additional songs")
for r in removed:
    artist = r['artist'].encode('ascii', 'replace').decode('ascii')
    song = r['song'].encode('ascii', 'replace').decode('ascii')
    print(f"  - {artist} - {song}")
    print(f"    Reason: {r['reason'][:50]}...")

# Save
with open(path, 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print(f"\nUpdated: {path}")

# Count final stats
total = 0
for vibe_name, vibe_data in cleaned_data['vibes'].items():
    count = len(vibe_data.get('songs', []))
    total += count
    
print(f"\nFinal count: {total} songs")
