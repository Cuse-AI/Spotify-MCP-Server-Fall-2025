import json
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Build lookup
all_songs = {}
for vibe_name, vibe_data in tapestry['vibes'].items():
    for song in vibe_data.get('songs', []):
        key = f"{song.get('artist', '').lower()}|{song.get('song', '').lower()}"
        all_songs[key] = song

# Songs from the user's screenshot
test_songs = [
    ("ROOKiEZ is PUNK'D", "コンプリケイション"),
    ("Nirvana", "Smells Like Teen Spirit"),
    ("Kanye West", "POWER"),
    ("Daft Punk", "Contact"),
    ("Elton John", "I'm Still Standing"),
    ("M83", "Outro"),
    ("Die Apokalyptischen Reiter", "Adrenalin"),
    ("Brian Eno", "1/1"),
    ("Tangerine Dream", "Alpha Centauri"),
    ("Pouring Voices", "Koto Winds"),
    ("Amethystium", "Strangely Beautiful"),
    ("Sigur Ros", "Svefn-g-englar"),
]

print("="*80)
print("CHECKING IF SONGS ARE IN TAPESTRY + THEIR ACTUAL QUOTES")
print("="*80)

for artist, title in test_songs:
    key = f"{artist.lower()}|{title.lower()}"
    
    # Try exact match first
    found = all_songs.get(key)
    
    # Try partial match if not found
    if not found:
        for k, v in all_songs.items():
            if artist.lower() in k.split('|')[0]:
                song_title = v.get('song', '').lower()
                if title.lower()[:10] in song_title or song_title[:10] in title.lower():
                    found = v
                    break
    
    print(f"\n{'='*60}")
    print(f"{artist} - {title}")
    
    if found:
        print("STATUS: IN TAPESTRY")
        comment = found.get('comment_text', '')
        if comment:
            preview = comment[:250] + ('...' if len(comment) > 250 else '')
            print(f"QUOTE: \"{preview}\"")
        else:
            print("QUOTE: [NONE]")
    else:
        print("STATUS: NOT IN TAPESTRY (EXTRAPOLATED)")
        print("Any quote shown is AI-GENERATED")
