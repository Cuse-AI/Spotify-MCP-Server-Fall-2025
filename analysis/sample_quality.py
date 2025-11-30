import json
import random

# Load tapestry
with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Get all songs
all_songs = []
for vibe_name, vibe_data in tapestry['vibes'].items():
    for song in vibe_data.get('songs', []):
        song['_vibe'] = vibe_name
        all_songs.append(song)

print(f"Total songs: {len(all_songs)}")
print("\n" + "="*80)
print("RANDOM SAMPLE OF 15 SONGS - QUALITY CHECK")
print("="*80)

# Random sample
sample = random.sample(all_songs, 15)

for i, s in enumerate(sample, 1):
    print(f"\n--- Song {i} ---")
    print(f"Artist: {s.get('artist', 'N/A')}")
    print(f"Song: {s.get('song', 'N/A')}")
    print(f"Subvibe: {s.get('mapped_subvibe', s.get('_vibe', 'N/A'))}")
    print(f"Confidence: {s.get('mapping_confidence', 'N/A')}")
    
    context = s.get('full_context', '')
    if context:
        print(f"CONTEXT (Reddit quote): {context[:300]}{'...' if len(context) > 300 else ''}")
    else:
        print("CONTEXT: [NONE]")
    
    ananki = s.get('ananki_analysis', '')
    if ananki:
        print(f"ANANKI: {ananki[:300]}{'...' if len(ananki) > 300 else ''}")
    else:
        print("ANANKI: [NONE]")

# Stats on context quality
has_context = sum(1 for s in all_songs if s.get('full_context'))
has_ananki = sum(1 for s in all_songs if s.get('ananki_analysis'))

print("\n" + "="*80)
print("QUALITY STATS")
print("="*80)
print(f"Songs with full_context (Reddit quote): {has_context}/{len(all_songs)} ({100*has_context/len(all_songs):.1f}%)")
print(f"Songs with ananki_analysis: {has_ananki}/{len(all_songs)} ({100*has_ananki/len(all_songs):.1f}%)")
