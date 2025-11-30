import json

with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\testing\scraper_test_2024_11_30\RAW_COMBINED_162_songs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("FULL DATA AUDIT")
print("=" * 70)

# Count problems
channel_names = 0  # Long names, likely channels
no_dash = 0  # No " - " separator
html_entities = 0  # Contains &amp; etc
real_looking = 0

problems = []
real_songs = []

for song in data['songs']:
    artist = song['artist']
    title = song['song']
    
    is_problem = False
    reasons = []
    
    # Check for channel-like names
    if len(artist) > 35:
        channel_names += 1
        reasons.append("long_artist_name")
        is_problem = True
    
    # Check for HTML entities
    if '&' in artist or '&' in title:
        html_entities += 1
        reasons.append("html_entities")
    
    # Check for compilation keywords
    bad_keywords = ['relaxing', 'sleep', 'study', 'ambient', 'lofi', 'lo-fi', 
                    'hours', 'meditation', 'healing', 'drone', 'mix', 'playlist',
                    'vol.', 'compilation', 'best of', '4k', '8k', 'hd']
    artist_lower = artist.lower()
    for kw in bad_keywords:
        if kw in artist_lower:
            reasons.append(f"bad_keyword:{kw}")
            is_problem = True
            break
    
    if is_problem:
        problems.append({
            'artist': artist,
            'song': title,
            'reasons': reasons
        })
    else:
        real_songs.append({
            'artist': artist,
            'song': title
        })

print(f"TOTAL SONGS: {len(data['songs'])}")
print(f"PROBLEM SONGS: {len(problems)}")
print(f"REAL-LOOKING SONGS: {len(real_songs)}")
print()

print("PROBLEM SONGS (sample):")
print("-" * 70)
for p in problems[:15]:
    print(f"  {p['artist'][:40]} | {p['reasons']}")

print()
print("REAL-LOOKING SONGS (sample):")
print("-" * 70)
for r in real_songs[:15]:
    print(f"  {r['artist']} - {r['song'][:30]}")
