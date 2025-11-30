import json

# Load scraped data
with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\testing\scraper_test_2024_11_30\RAW_COMBINED_162_songs.json', 'r', encoding='utf-8') as f:
    scraped = json.load(f)

# Load existing tapestry
with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Build set of existing songs (lowercase for comparison)
existing = set()
for vibe_data in tapestry['vibes'].values():
    for song in vibe_data.get('songs', []):
        key = f"{song['artist'].lower()}|{song['song'].lower()}"
        existing.add(key)

print(f"Existing songs in tapestry: {len(existing)}")
print(f"Scraped songs: {len(scraped['songs'])}")
print()

# Check for duplicates
duplicates = 0
new_songs = 0

for song in scraped['songs']:
    key = f"{song['artist'].lower()}|{song['song'].lower()}"
    if key in existing:
        duplicates += 1
    else:
        new_songs += 1

print(f"DUPLICATES (already in tapestry): {duplicates}")
print(f"NEW songs: {new_songs}")
print()

# Now check how many new songs are actually REAL songs vs garbage
bad_keywords = ['relaxing', 'sleep', 'study', 'ambient', 'lofi', 'lo-fi', 
                'hours', 'meditation', 'healing', 'drone', 'mix', 'playlist',
                'vol.', 'compilation', 'best of', '4k', '8k', 'hd', 'asmr']

new_real = 0
new_garbage = 0

for song in scraped['songs']:
    key = f"{song['artist'].lower()}|{song['song'].lower()}"
    if key in existing:
        continue  # Skip duplicates
    
    artist_lower = song['artist'].lower()
    is_garbage = False
    
    if len(song['artist']) > 35:
        is_garbage = True
    
    for kw in bad_keywords:
        if kw in artist_lower:
            is_garbage = True
            break
    
    if is_garbage:
        new_garbage += 1
    else:
        new_real += 1

print("OF THE NEW SONGS:")
print(f"  Real-looking: {new_real}")
print(f"  Garbage: {new_garbage}")
print()
print(f"ACTUAL USABLE NEW SONGS: ~{new_real}")
