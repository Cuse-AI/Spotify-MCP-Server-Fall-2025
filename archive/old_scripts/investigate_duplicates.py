import json
from collections import defaultdict

# Load tapestry
with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

vibes = tapestry['vibes']

# Track where each duplicate appears
song_locations = defaultdict(list)

for vibe_name, vibe_data in vibes.items():
    for song in vibe_data['songs']:
        song_key = f"{song.get('artist', '')} - {song.get('song', '')}"
        song_locations[song_key].append(vibe_name)

# Find the worst offenders
duplicates = {song: vibes_list for song, vibes_list in song_locations.items() if len(vibes_list) > 5}

print('\n' + '='*80)
print('DUPLICATE INVESTIGATION')
print('='*80)

print(f'\nSongs appearing in MORE than 5 vibes: {len(duplicates)}')

print(f'\n\nTOP 20 WORST OFFENDERS:')
for song, vibes_list in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
    print(f'\n"{song}" - appears {len(vibes_list)} times in:')
    for vibe in vibes_list[:10]:  # Show first 10
        print(f'  - {vibe}')
    if len(vibes_list) > 10:
        print(f'  ... and {len(vibes_list) - 10} more vibes')

# Check if these are legitimate or errors
print(f'\n\n' + '='*80)
print('DIAGNOSIS:')
print('='*80)

# Look at "Nutshell - Alice" specifically
nutshell_vibes = song_locations.get('Nutshell - Alice', [])
print(f'\n"Nutshell - Alice" appears in {len(nutshell_vibes)} vibes:')
for vibe in nutshell_vibes:
    print(f'  - {vibe}')

print(f'\nIs this legitimate? A song CAN fit multiple emotions...')
print(f'But 28 times seems excessive!')
print(f'\nPossible causes:')
print(f'  1. Same Reddit post scraped multiple times across different batch runs')
print(f'  2. Merging batches without checking for existing songs')
print(f'  3. Different search queries finding same discussions')

# Save detailed report
with open('data_validation/duplicate_investigation.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_songs_over_5_vibes': len(duplicates),
        'top_offenders': {song: len(vibes_list) for song, vibes_list in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:50]},
        'nutshell_example': {
            'song': 'Nutshell - Alice',
            'count': len(nutshell_vibes),
            'appears_in': nutshell_vibes
        }
    }, f, indent=2)

print(f'\nReport saved to: data_validation/duplicate_investigation.json')
