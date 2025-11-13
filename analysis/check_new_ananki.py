import json
import glob
import os

files = glob.glob(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\reddit\test_results\*checkpoint_DEDUPED_CLAUDE_MAPPED.json')
recent = [f for f in files if any(x in f for x in ['party', 'drive', 'dark', 'romantic'])]

print("="*60)
print("NEW ANANKI RESULTS")
print("="*60)

total_mapped = 0
for filepath in sorted(recent):
    filename = os.path.basename(filepath)
    vibe = filename.split('_')[0].title()
    
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    
    mapped = len(data['mapped_songs'])
    ambiguous = len(data.get('ambiguous_songs', []))
    
    print(f"{vibe:12} {mapped:3} mapped, {ambiguous:2} ambiguous")
    total_mapped += mapped

print(f"\n{'='*60}")
print(f"TOTAL NEW SONGS MAPPED: {total_mapped}")
print(f"Current tapestry: 5,105")
print(f"After injection: ~{5105 + total_mapped:,}")
