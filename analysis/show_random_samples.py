import json, random

# Load tapestry
t = json.load(open('../ananki_outputs/tapestry_VALIDATED_ONLY.json', encoding='utf-8'))

# Get all vibes with songs
vibes_with_songs = [(k, v['songs']) for k, v in t['vibes'].items() if len(v['songs']) > 0]

print('='*70)
print('RANDOM SAMPLES: PROVING EVERY SONG HAS CONTEXT + REASONING')
print('='*70)

# Show 5 random samples
for i in range(5):
    vibe_name, songs = random.choice(vibes_with_songs)
    song = random.choice(songs)

    print(f'\n[SAMPLE {i+1}]')
    print(f'Artist: {song["artist"]}')
    print(f'Song: {song["song"]}')
    print(f'Sub-vibe: {vibe_name}')
    print(f'Spotify ID: {song["spotify_id"]}')
    print(f'')
    print(f'WHY ITS HERE:')
    print(f'  Post: {song.get("post_title", "N/A")[:80]}')
    print(f'  Ananki: {song.get("ananki_analysis", "N/A")}')
    print(f'  Confidence: {song.get("mapping_confidence", "N/A")}')
    print(f'  Source: {song.get("source_url", "N/A")[:70]}...')

print('\n' + '='*70)
print('TOTAL VALIDATED SONGS:', sum(len(v['songs']) for v in t['vibes'].values()))
print('='*70)
