import json
from collections import defaultdict

# Load tapestry
with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

vibes = tapestry['vibes']
stats = tapestry['stats']

print('\n' + '='*80)
print('GLOBAL DEDUPLICATION - Keeping First Appearance Only')
print('='*80)

# Track which songs we've seen globally
seen_songs = {}  # song_key -> first vibe it appeared in
total_before = 0
total_after = 0
removed_count = 0

# Process vibes in order (assuming earlier vibes are more accurate)
vibe_order = list(vibes.keys())

for vibe_name in vibe_order:
    vibe_data = vibes[vibe_name]
    songs = vibe_data['songs']
    before = len(songs)
    total_before += before
    
    unique_songs = []
    
    for song in songs:
        song_key = f"{song.get('artist', 'Unknown')}|||{song.get('song', 'Unknown')}"
        
        if song_key not in seen_songs:
            # First time seeing this song - keep it!
            seen_songs[song_key] = vibe_name
            unique_songs.append(song)
        else:
            # Already saw this song in another vibe - skip it!
            removed_count += 1
    
    after = len(unique_songs)
    total_after += after
    
    # Update vibe with cleaned songs
    vibe_data['songs'] = unique_songs
    
    if before != after:
        print(f'{vibe_name}: {before} -> {after} ({before - after} removed)')

# Update stats
stats['total_songs'] = total_after
stats['unique_songs_enforced'] = True
tapestry['stats'] = stats

# Count unique artists after deduplication
all_artists = set()
for vibe_data in vibes.values():
    for song in vibe_data['songs']:
        all_artists.add(song.get('artist', 'Unknown'))

stats['total_artists'] = len(all_artists)

# Save cleaned tapestry
with open('ananki_outputs/tapestry_CLEANED.json', 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2)

print(f'\n' + '='*80)
print('DEDUPLICATION COMPLETE')
print('='*80)
print(f'BEFORE: {total_before} total entries')
print(f'AFTER:  {total_after} unique songs')
print(f'REMOVED: {removed_count} duplicates ({(removed_count/total_before*100):.1f}%)')
print(f'Artists: {len(all_artists)}')
print(f'\nSaved to: ananki_outputs/tapestry_CLEANED.json')
