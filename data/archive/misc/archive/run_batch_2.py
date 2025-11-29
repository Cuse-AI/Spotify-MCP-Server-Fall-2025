import json
import sys

# Load the preprocessed tapestry
with open('../ananki_outputs/tapestry_PREPROCESSED.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Collect all songs
all_songs = []
for vibe_name, vibe_data in tapestry['vibes'].items():
    for song in vibe_data['songs']:
        all_songs.append({
            'artist': song.get('artist', ''),
            'song': song.get('song', ''),
            'vibe': vibe_name
        })

# Process batch 2: songs 500-1000
batch_start = 500
batch_end = 1000
batch_num = 2

print(f'Preparing Batch {batch_num}: songs {batch_start}-{batch_end}')
print(f'Total songs available: {len(all_songs)}')

batch_songs = all_songs[batch_start:batch_end]
print(f'Batch {batch_num} size: {len(batch_songs)} songs')
print(f'\nReady to validate!')
