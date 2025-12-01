import json
from collections import defaultdict
import os

BASE_PATH = 'C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/core/tapestry_chunks'

def analyze_all_chunks():
    """Analyze all cleaned chunks and compile stats"""
    
    all_stats = defaultdict(int)
    meta_vibe_stats = defaultdict(int)
    chunk_stats = {}
    
    for i in range(1, 12):
        chunk_num = f"{i:02d}"
        path = f"{BASE_PATH}/tapestry_chunk_{chunk_num}_CLEANED.json"
        
        if not os.path.exists(path):
            print(f"Chunk {chunk_num}: NOT FOUND")
            continue
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunk_total = 0
        chunk_vibes = defaultdict(int)
        
        for vibe_name, vibe_data in data['vibes'].items():
            count = len(vibe_data.get('songs', []))
            all_stats[vibe_name] += count
            chunk_vibes[vibe_name] = count
            chunk_total += count
            
            # Extract meta-vibe
            meta = vibe_name.split(' - ')[0] if ' - ' in vibe_name else vibe_name
            meta_vibe_stats[meta] += count
        
        chunk_stats[chunk_num] = {
            'total': chunk_total,
            'vibes': dict(chunk_vibes)
        }
        
        print(f"Chunk {chunk_num}: {chunk_total} songs")
    
    return all_stats, meta_vibe_stats, chunk_stats

print("=" * 80)
print("TAPESTRY STATS - ALL CLEANED CHUNKS")
print("=" * 80)

all_stats, meta_stats, chunk_stats = analyze_all_chunks()

print("\n" + "=" * 80)
print("META-VIBE DISTRIBUTION")
print("=" * 80)
grand_total = 0
for meta, count in sorted(meta_stats.items(), key=lambda x: -x[1]):
    pct = (count / sum(meta_stats.values())) * 100
    bar = "#" * int(pct / 2)
    print(f"{meta:15} {count:5} ({pct:5.1f}%) {bar}")
    grand_total += count

print(f"\n{'TOTAL':15} {grand_total:5}")

print("\n" + "=" * 80)
print("SUB-VIBE DISTRIBUTION (sorted by count)")
print("=" * 80)
for vibe, count in sorted(all_stats.items(), key=lambda x: -x[1]):
    pct = (count / sum(all_stats.values())) * 100
    print(f"  {vibe:35} {count:4} ({pct:4.1f}%)")

print(f"\n  {'TOTAL':35} {sum(all_stats.values()):4}")

# Save stats to JSON for tracking
stats_output = {
    'grand_total': grand_total,
    'meta_vibes': dict(meta_stats),
    'sub_vibes': dict(all_stats),
    'by_chunk': chunk_stats
}

with open(f'{BASE_PATH}/tapestry_stats.json', 'w', encoding='utf-8') as f:
    json.dump(stats_output, f, indent=2)

print(f"\nStats saved to: {BASE_PATH}/tapestry_stats.json")
