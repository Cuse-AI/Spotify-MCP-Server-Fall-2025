import json
import random

# Load CLEANED tapestry
with open('ananki_outputs/tapestry_CLEANED.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

vibes = tapestry['vibes']

print('\n' + '='*80)
print('CLEANED TAPESTRY QUALITY AUDIT')
print('='*80)

# Sample 200 random songs for validation (larger sample now)
all_songs = []
for vibe_name, vibe_data in vibes.items():
    for song in vibe_data['songs']:
        all_songs.append({
            'artist': song.get('artist', ''),
            'song': song.get('song', ''),
            'vibe': vibe_name
        })

random.seed(42)
sample = random.sample(all_songs, min(200, len(all_songs)))

# Categorize issues
flagged = []
issue_types = {
    'NEWLINE_BREAK': [],
    'URL_FRAGMENT': [],
    'SUSPICIOUS_CHARS': [],
    'TOO_SHORT': [],
    'TOO_LONG': [],
    'MISSING_ARTIST': []
}

for entry in sample:
    artist = entry['artist']
    song = entry['song']
    flags = []
    
    # Check for issues
    if '\n' in artist or '\n' in song:
        flags.append('NEWLINE_BREAK')
        issue_types['NEWLINE_BREAK'].append(entry)
    
    if 'http' in artist.lower() or 'http' in song.lower() or 'youtu' in artist.lower() or 'youtu' in song.lower():
        flags.append('URL_FRAGMENT')
        issue_types['URL_FRAGMENT'].append(entry)
    
    if any(c in artist + song for c in ['[', ']', '(', ')', 'open.spotify', 'spotify.link']):
        flags.append('SUSPICIOUS_CHARS')
        issue_types['SUSPICIOUS_CHARS'].append(entry)
    
    if len(artist) < 2 or len(song) < 2:
        flags.append('TOO_SHORT')
        issue_types['TOO_SHORT'].append(entry)
    
    if len(artist) > 60 or len(song) > 80:
        flags.append('TOO_LONG')
        issue_types['TOO_LONG'].append(entry)
    
    if not artist or artist == 'Unknown':
        flags.append('MISSING_ARTIST')
        issue_types['MISSING_ARTIST'].append(entry)
    
    if flags:
        flagged.append({
            'artist': artist,
            'song': song,
            'vibe': entry['vibe'],
            'flags': flags
        })

# Calculate quality metrics
clean_count = len(sample) - len(flagged)
quality_rate = (clean_count / len(sample)) * 100

print(f'\nSAMPLE SIZE: 200 songs')
print(f'CLEAN: {clean_count} ({quality_rate:.1f}%)')
print(f'FLAGGED: {len(flagged)} ({100-quality_rate:.1f}%)')

print(f'\nISSUE BREAKDOWN:')
for issue, entries in sorted(issue_types.items(), key=lambda x: len(x[1]), reverse=True):
    if entries:
        print(f'  {issue}: {len(entries)} songs')

# Save detailed report
output = {
    'audit_date': '2025-11-09',
    'tapestry_version': 'CLEANED',
    'total_songs_in_tapestry': len(all_songs),
    'sample_size': len(sample),
    'clean_songs': clean_count,
    'flagged_songs': len(flagged),
    'quality_rate': f'{quality_rate:.1f}%',
    'issue_breakdown': {k: len(v) for k, v in issue_types.items()},
    'flagged_entries': flagged[:100]  # Save first 100
}

with open('data_validation/cleaned_tapestry_audit.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

# Human-readable report
with open('data_validation/cleaned_tapestry_audit_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write('CLEANED TAPESTRY QUALITY AUDIT\n')
    f.write('='*80 + '\n\n')
    f.write(f'Total Songs: {len(all_songs)}\n')
    f.write(f'Sample Size: {len(sample)}\n')
    f.write(f'Clean Rate: {quality_rate:.1f}%\n')
    f.write(f'Issues Found: {len(flagged)} ({100-quality_rate:.1f}%)\n\n')
    
    f.write('ISSUE BREAKDOWN:\n')
    f.write('-'*80 + '\n')
    for issue, entries in sorted(issue_types.items(), key=lambda x: len(x[1]), reverse=True):
        if entries:
            f.write(f'\n{issue}: {len(entries)} songs\n')
            for entry in entries[:5]:  # Show first 5 examples
                f.write(f'  - {entry["artist"]} - {entry["song"]} (Vibe: {entry["vibe"]})\n')
            if len(entries) > 5:
                f.write(f'  ... and {len(entries)-5} more\n')

print(f'\nReports saved to:')
print(f'  - data_validation/cleaned_tapestry_audit.json')
print(f'  - data_validation/cleaned_tapestry_audit_REPORT.txt')
print(f'\nAudit complete!')
