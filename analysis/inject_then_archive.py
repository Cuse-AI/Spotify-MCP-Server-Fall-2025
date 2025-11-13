"""
Re-inject the 48 "lost" songs that were mapped to invalid sub-vibes
Now that we have consolidated manifold, map them to closest valid sub-vibes
"""
import json
from pathlib import Path

# Load tapestry
with open('data/ananki_outputs/tapestry_VALIDATED_ONLY.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

valid_subvibes = set(tapestry['vibes'].keys())

# Load all CLAUDE_MAPPED files
youtube_dir = Path('data/youtube/test_results')
reddit_dir = Path('data/reddit/test_results')
all_mapped_files = list(youtube_dir.glob('*CLAUDE_MAPPED.json')) + list(reddit_dir.glob('*CLAUDE_MAPPED.json'))

# Find songs with invalid sub-vibes and map them
invalid_to_valid = {
    'Chill - Contemplative': 'Chill - Meditative',
    'Happy - Nostalgic': 'Sad - Nostalgic Sad',
    'Happy - Nostalgic Sad': 'Sad - Nostalgic Sad',
    'Romantic - Feel Good': 'Romantic - Wholesome',
    'Dark - Anxious': 'Dark - Anxious Panic',
    'Romantic - Dark Romance': 'Dark - Romance',
    'Sad - Longing': 'Sad - Yearning',
    'Dark - Unsettling': 'Dark - Eerie',
    'Dark - Anxiety': 'Dark - Anxious Panic',
    'Dark - Existential': 'Night - Existential',
    'Dark - Overstimulation': 'Dark - Chaos',
    'Energy - Duty': 'Energy - Motivated',
    'Dark - Resentment': 'Dark - Bitter',
    'Dark - Satirical': 'Dark - Humor',
    'Chill - Sofa': 'Chill - Lounge',
    'Chill - Mellow': 'Chill - Gentle',
    'Dark - Suspenseful': 'Dark - Tense',
    'Dark - Contemplative': 'Night - Deep Thoughts',
    'Dark - Corrupted Love': 'Dark - Romance',
    'Chill - Carefree': 'Happy - Carefree',
    'Romantic - First Dance': 'Romantic - Intimate',
    'Happy - Nostalgic Celebration': 'Sad - Nostalgic Sad',
    'Romantic - Heartbreak': 'Sad - Heartbreak',
    'Romantic - Nostalgic': 'Sad - Nostalgic Sad',
    'Party - Pump Up': 'Energy - Pump Up',
    'Party - DJ': 'Party - Dance',
    'Energy - Punk/Rebellious': 'Energy - Rebellious',
    'Energy - Punk/Aggressive': 'Energy - Aggressive',
    'Dark - Cathartic': 'Dark - Release',
    'Dark - Angry': 'Energy - Rage',
    'Dark - Emo/Screamo': 'Dark - Emo',
    'Dark - Industrial': 'Dark - Heavy'
}

songs_to_inject = []
for mapped_file in all_mapped_files:
    with open(mapped_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    songs = data.get('mapped_songs', data.get('songs', []))

    for song in songs:
        subvibe = song.get('ananki_subvibe', '')

        if subvibe and subvibe not in valid_subvibes:
            # This song needs remapping
            if subvibe in invalid_to_valid:
                new_subvibe = invalid_to_valid[subvibe]
                song['ananki_subvibe'] = new_subvibe
                song['ananki_reasoning'] += f" [Remapped from '{subvibe}']"
                songs_to_inject.append(song)

print(f'Found {len(songs_to_inject)} songs to inject')

# Inject them
from collections import Counter
injected_count = 0
skipped_duplicates = 0
subvibe_counts = Counter()

for song in songs_to_inject:
    subvibe = song['ananki_subvibe']
    spotify_id = song.get('spotify_id')

    # Check for duplicates
    if spotify_id:
        found = False
        for sv_data in tapestry['vibes'].values():
            for existing_song in sv_data.get('songs', []):
                if existing_song.get('spotify_id') == spotify_id:
                    found = True
                    break
            if found:
                break

        if found:
            skipped_duplicates += 1
            continue

    # Inject!
    if subvibe in tapestry['vibes']:
        tapestry['vibes'][subvibe]['songs'].append({
            'artist': song['artist'],
            'song': song['song'],
            'spotify_id': song['spotify_id'],
            'spotify_uri': song['spotify_uri'],
            'comment_score': song.get('comment_score', 0),
            'source_url': song.get('source_url', ''),
            'data_source': song.get('data_source', song.get('source', 'youtube')),
            'extraction_confidence': song.get('extraction_confidence', 1.0),
            'mapping_confidence': song.get('ananki_confidence', 0.9),
            'full_context': song.get('full_context', ''),
            'post_title': song.get('post_title', ''),
            'comment_text': song.get('comment_text', ''),
            'ananki_reasoning': song.get('ananki_reasoning', ''),
            'mapped_subvibe': subvibe
        })
        injected_count += 1
        subvibe_counts[subvibe] += 1

print(f'\nInjected: {injected_count} songs')
print(f'Skipped (duplicates): {skipped_duplicates} songs')
print(f'\nTop sub-vibes:')
for sv, count in subvibe_counts.most_common(10):
    print(f'  {sv}: {count}')

# Save
with open('data/ananki_outputs/tapestry_VALIDATED_ONLY.json', 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print(f'\nSaved! Total songs now: {sum(len(d.get("songs", [])) for d in tapestry["vibes"].values())}')
