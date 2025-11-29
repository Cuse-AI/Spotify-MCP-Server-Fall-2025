# -*- coding: utf-8 -*-
"""Analyze tapestry distribution by meta-vibe and sub-vibe"""
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

with open('core/tapestry.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Collect stats
meta_vibes = defaultdict(lambda: {'total': 0, 'sub_vibes': {}})

for vibe_name, vibe_data in data['vibes'].items():
    count = len(vibe_data.get('songs', []))
    
    # Parse meta-vibe from "Meta - Sub" format
    if ' - ' in vibe_name:
        meta = vibe_name.split(' - ')[0]
    else:
        meta = vibe_name
    
    meta_vibes[meta]['total'] += count
    meta_vibes[meta]['sub_vibes'][vibe_name] = count

total_songs = sum(m['total'] for m in meta_vibes.values())

# Print meta-vibe summary
print("=" * 70)
print("TAPESTRY DISTRIBUTION ANALYSIS")
print("=" * 70)
print(f"\nTotal songs: {total_songs:,}")
print(f"Total sub-vibes: {len(data['vibes'])}")

print("\n" + "=" * 70)
print("META-VIBE BREAKDOWN (sorted by count)")
print("=" * 70)

sorted_metas = sorted(meta_vibes.items(), key=lambda x: -x[1]['total'])

for meta, mdata in sorted_metas:
    pct = mdata['total'] / total_songs * 100
    bar = '█' * int(pct / 2)
    status = '✅' if mdata['total'] >= 500 else '⚠️' if mdata['total'] >= 200 else '🔴'
    print(f"\n{status} {meta}: {mdata['total']:,} songs ({pct:.1f}%)")
    print(f"   {bar}")
    
    # Show sub-vibes for this meta
    sorted_subs = sorted(mdata['sub_vibes'].items(), key=lambda x: -x[1])
    for sub_name, sub_count in sorted_subs:
        sub_status = '✓' if sub_count >= 50 else '○' if sub_count >= 20 else '·'
        print(f"   {sub_status} {sub_name}: {sub_count}")

# Summary of weak areas
print("\n" + "=" * 70)
print("PRIORITY TARGETS FOR SCRAPING")
print("=" * 70)

# Meta-vibes needing help
weak_metas = [(m, d['total']) for m, d in meta_vibes.items() if d['total'] < 400]
if weak_metas:
    print("\n🔴 META-VIBES NEEDING MORE DATA (<400 songs):")
    for meta, count in sorted(weak_metas, key=lambda x: x[1]):
        print(f"   {meta}: {count} songs")

# Sub-vibes with very few songs
print("\n⚠️ SUB-VIBES WITH <30 SONGS:")
weak_subs = []
for vibe_name, vibe_data in data['vibes'].items():
    count = len(vibe_data.get('songs', []))
    if count < 30:
        weak_subs.append((vibe_name, count))

for sub, count in sorted(weak_subs, key=lambda x: x[1]):
    print(f"   {sub}: {count}")

# Empty sub-vibes
empty = [v for v, d in data['vibes'].items() if len(d.get('songs', [])) == 0]
if empty:
    print(f"\n🚫 EMPTY SUB-VIBES ({len(empty)}):")
    for v in sorted(empty):
        print(f"   {v}")
