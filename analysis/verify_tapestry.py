"""
Quick verification of current tapestry state
"""
import json
from pathlib import Path

tapestry_path = Path('data/ananki_outputs/tapestry_VALIDATED_ONLY.json')

with open(tapestry_path, 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

total_songs = 0
with_reasoning = 0
without_reasoning = 0
meta_vibe_counts = {}

for subvibe, data in tapestry['vibes'].items():
    meta = subvibe.split(' - ')[0]
    songs = data.get('songs', [])

    if meta not in meta_vibe_counts:
        meta_vibe_counts[meta] = 0
    meta_vibe_counts[meta] += len(songs)

    total_songs += len(songs)

    for song in songs:
        if 'ananki_reasoning' in song and song['ananki_reasoning']:
            with_reasoning += 1
        else:
            without_reasoning += 1

print(f"\n{'='*70}")
print(f"CURRENT TAPESTRY STATE")
print(f"{'='*70}")
print(f"\nTotal Songs: {total_songs:,}")
print(f"With TRUE Ananki: {with_reasoning:,} ({with_reasoning/total_songs*100:.1f}%)")
print(f"Without Reasoning: {without_reasoning:,} ({without_reasoning/total_songs*100:.1f}%)")

print(f"\n{'='*70}")
print(f"META-VIBE DISTRIBUTION")
print(f"{'='*70}")

sorted_vibes = sorted(meta_vibe_counts.items(), key=lambda x: x[1], reverse=True)
for meta, count in sorted_vibes:
    pct = count / total_songs * 100
    print(f"{meta:20} {count:5,} songs ({pct:5.1f}%)")

print(f"\n{'='*70}")
