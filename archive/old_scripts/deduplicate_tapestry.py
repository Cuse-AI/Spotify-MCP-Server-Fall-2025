import json

# Load tapestry
with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

vibes = tapestry['vibes']
stats = tapestry['stats']

print('\n' + '='*80)
print('DEDUPLICATION PROCESS')
print('='*80)

print(f'\nBEFORE:')
print(f'  Total entries: {stats["total_songs"]}')

# Deduplicate within each vibe
total_before = 0
total_after = 0
removed_per_vibe = {}

for vibe_name, vibe_data in vibes.items():
    songs = vibe_data['songs']
    before_count = len(songs)
    total_before += before_count
    
    # Create unique songs using artist-song key
    seen = set()
    unique_songs = []
    
    for song in songs:
        song_key = f"{song.get('artist', 'Unknown')}|||{song.get('song', 'Unknown')}"
        if song_key not in seen:
            seen.add(song_key)
            unique_songs.append(song)
    
    after_count = len(unique_songs)
    total_after += after_count
    removed = before_count - after_count
    
    if removed > 0:
        removed_per_vibe[vibe_name] = removed
    
    # Update the vibe with deduplicated songs
    vibe_data['songs'] = unique_songs

# Update stats
stats['total_songs'] = total_after
tapestry['stats'] = stats

# Save deduplicated tapestry
with open('ananki_outputs/tapestry_deduplicated.json', 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2)

print(f'\nAFTER:')
print(f'  Total entries: {total_after}')
print(f'  Removed duplicates: {total_before - total_after}')
print(f'  Reduction: {((total_before - total_after) / total_before * 100):.1f}%')

print(f'\nTop 10 vibes with most duplicates removed:')
for vibe, count in sorted(removed_per_vibe.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f'  {vibe}: {count} duplicates')

print(f'\nSaved to: ananki_outputs/tapestry_deduplicated.json')
