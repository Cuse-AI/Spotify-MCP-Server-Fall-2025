"""
Apply relevancy results to tapestry - keep only score 3+ songs
Archives 1s and 2s to separate file
"""
import json
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).parent
output_dir = project_root / "ananki" / "output"
archive_dir = project_root / "data" / "archive" / "relevancy_archived"
archive_dir.mkdir(parents=True, exist_ok=True)

# Load the passed songs from relevancy check
passed_file = output_dir / "RELEVANCY_PASSED_20251201_222203.json"
with open(passed_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

songs = data['songs']
print(f"Loaded {len(songs)} passed songs")

# Separate by score
score_3_plus = []
score_2_archive = []

for song in songs:
    score = song.get('relevancy_score', 0)
    if score >= 3:
        score_3_plus.append(song)
    elif score == 2:
        score_2_archive.append(song)

print(f"\nScore 3+: {len(score_3_plus)} songs (KEEPING)")
print(f"Score 2:  {len(score_2_archive)} songs (ARCHIVING)")

# Archive the 2s
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
archive_file = archive_dir / f"archived_score_2_{timestamp}.json"
with open(archive_file, 'w', encoding='utf-8') as f:
    json.dump({
        'reason': 'Score 2 - weak relevancy, archived for potential future use',
        'count': len(score_2_archive),
        'songs': score_2_archive
    }, f, indent=2, ensure_ascii=False)
print(f"Archived 2s to: {archive_file.name}")

# Load current tapestry to get structure
tapestry_path = project_root / "core" / "tapestry.json"
with open(tapestry_path, 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Create a lookup of kept songs by spotify_id
kept_ids = set()
for song in score_3_plus:
    sid = song.get('spotify_id') or song.get('track_id', '')
    sid = sid.replace('spotify:track:', '')
    kept_ids.add(sid)

print(f"\nKept IDs: {len(kept_ids)}")

# Filter tapestry vibes to only include kept songs
new_tapestry = {
    'version': tapestry.get('version', '2.0'),
    'generated': datetime.now().isoformat(),
    'description': 'Filtered tapestry - relevancy score 3+ only',
    'vibes': {}
}

total_kept = 0
total_removed = 0

for vibe_name, vibe_data in tapestry['vibes'].items():
    kept_songs = []
    for song in vibe_data.get('songs', []):
        sid = song.get('spotify_id') or song.get('track_id', '')
        sid = sid.replace('spotify:track:', '')
        if sid in kept_ids:
            kept_songs.append(song)
            total_kept += 1
        else:
            total_removed += 1
    
    new_tapestry['vibes'][vibe_name] = {
        **vibe_data,
        'songs': kept_songs,
        'song_count': len(kept_songs)
    }

print(f"\nTapestry filtering complete:")
print(f"  Kept: {total_kept}")
print(f"  Removed: {total_removed}")

# Save new tapestry
new_tapestry_path = project_root / "core" / "tapestry_quality.json"
with open(new_tapestry_path, 'w', encoding='utf-8') as f:
    json.dump(new_tapestry, f, indent=2, ensure_ascii=False)

print(f"\nSaved quality tapestry to: {new_tapestry_path}")

# Show vibe distribution
print(f"\n{'='*60}")
print("VIBE DISTRIBUTION (Score 3+ only):")
print('='*60)
for vibe_name, vibe_data in sorted(new_tapestry['vibes'].items()):
    count = len(vibe_data.get('songs', []))
    if count > 0:
        print(f"  {vibe_name}: {count}")
