import json
import random
from collections import Counter

# Load the tapestry
with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

vibes = tapestry['vibes']

# Quality checks
print('\n' + '='*80)
print('TAPESTRY DATA QUALITY AUDIT')
print('='*80)

# 1. Check for duplicate songs across entire tapestry
all_songs = []
for vibe_name, vibe_data in vibes.items():
    for song in vibe_data['songs']:
        song_key = f"{song.get('artist', '')} - {song.get('song', '')}"
        all_songs.append((song_key, vibe_name))

song_counts = Counter([s[0] for s in all_songs])
duplicates = {song: count for song, count in song_counts.items() if count > 1}

print(f'\n1. DUPLICATE CHECK:')
print(f'   Total song entries: {len(all_songs)}')
print(f'   Unique songs: {len(song_counts)}')
print(f'   Duplicates: {len(duplicates)}')

# Show top duplicates
print(f'\n   Top 10 most duplicated songs:')
for song, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f'   - {song}: {count} times')

# 2. Sample 100 random songs for manual validation
print(f'\n2. SAMPLING 100 RANDOM SONGS FOR VALIDATION:')
random.seed(42)
sample_songs = random.sample(all_songs, min(100, len(all_songs)))

flagged_entries = []

for song_key, vibe in sample_songs:
    # Flag suspicious patterns
    flags = []
    
    artist, song = song_key.split(' - ', 1) if ' - ' in song_key else ('Unknown', song_key)
    
    # Flag empty or very short names
    if len(artist) < 2 or len(song) < 2:
        flags.append('TOO_SHORT')
    
    # Flag URLs/links
    if 'http' in artist.lower() or 'http' in song.lower():
        flags.append('CONTAINS_URL')
    
    # Flag special characters that suggest parsing errors
    if any(char in artist + song for char in ['[', ']', '(', ')', 'youtu', 'open.spotify']):
        flags.append('SUSPICIOUS_CHARS')
    
    # Flag incomplete names (single words for artist)
    if ' ' not in artist and len(artist) > 2 and len(artist) < 15:
        flags.append('SINGLE_WORD_ARTIST')
    
    # Flag very long names (likely parsing error)
    if len(artist) > 60 or len(song) > 80:
        flags.append('TOO_LONG')
    
    # Flag songs with newlines or weird formatting
    if '\n' in artist or '\n' in song:
        flags.append('CONTAINS_NEWLINE')
    
    if flags:
        flagged_entries.append({
            'artist': artist,
            'song': song,
            'vibe': vibe,
            'flags': flags,
            'needs_manual_check': True
        })

print(f'   Sampled: 100 songs')
print(f'   Flagged for issues: {len(flagged_entries)}')
print(f'   Clean rate: {100 - len(flagged_entries)}%')

# 3. Save flagged entries for manual review
output = {
    'audit_date': '2025-11-09',
    'total_songs': len(all_songs),
    'unique_songs': len(song_counts),
    'duplicates_found': len(duplicates),
    'top_duplicates': dict(sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:20]),
    'sample_size': 100,
    'flagged_count': len(flagged_entries),
    'estimated_clean_rate': f'{100 - len(flagged_entries)}%',
    'flagged_entries': flagged_entries
}

with open('data_validation/flagged_entries.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

# Also save human-readable version
with open('data_validation/flagged_entries_REVIEW.txt', 'w', encoding='utf-8') as f:
    f.write('TAPESTRY DATA QUALITY AUDIT - FLAGGED ENTRIES\n')
    f.write('='*80 + '\n\n')
    f.write(f'Sample Size: 100 songs\n')
    f.write(f'Flagged: {len(flagged_entries)} ({len(flagged_entries)}%)\n')
    f.write(f'Clean: {100 - len(flagged_entries)} ({100 - len(flagged_entries)}%)\n\n')
    f.write('='*80 + '\n')
    f.write('FLAGGED ENTRIES TO REVIEW:\n')
    f.write('='*80 + '\n\n')
    
    for i, entry in enumerate(flagged_entries, 1):
        f.write(f'[{i}] {entry["artist"]} - {entry["song"]}\n')
        f.write(f'    Vibe: {entry["vibe"]}\n')
        f.write(f'    Flags: {", ".join(entry["flags"])}\n')
        f.write(f'    Status: NEEDS_MANUAL_CHECK\n\n')

print(f'\n3. SAVED AUDIT RESULTS:')
print(f'   - data_validation/flagged_entries.json')
print(f'   - data_validation/flagged_entries_REVIEW.txt')
print(f'\nAudit complete! Check the files to review flagged entries.')
