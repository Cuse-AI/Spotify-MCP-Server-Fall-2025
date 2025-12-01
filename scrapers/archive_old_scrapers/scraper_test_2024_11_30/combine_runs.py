import json
from datetime import datetime

f1 = r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\testing\scraper_test_2024_11_30\RAW_hybrid_scraper_20251130_013915.json'
f2 = r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\testing\scraper_test_2024_11_30\RAW_hybrid_scraper_20251130_014919.json'
out = r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\testing\scraper_test_2024_11_30\RAW_COMBINED_162_songs.json'

with open(f1, 'r', encoding='utf-8') as f:
    d1 = json.load(f)
with open(f2, 'r', encoding='utf-8') as f:
    d2 = json.load(f)

combined = {
    'metadata': {
        'description': 'Combined output from 2 scraper runs',
        'run1_songs': len(d1['songs']),
        'run2_songs': len(d2['songs']),
        'total_songs': len(d1['songs']) + len(d2['songs']),
        'created': datetime.now().isoformat(),
        'pipeline_stage': 'RAW',
        'next_step': 'Move to data/pipeline/1_raw/ then dedupe',
        'needs_ananki': True,
    },
    'songs': d1['songs'] + d2['songs']
}

with open(out, 'w', encoding='utf-8') as f:
    json.dump(combined, f, indent=2, ensure_ascii=False)

print(f"Created: RAW_COMBINED_162_songs.json")
print(f"Total songs: {len(combined['songs'])}")
