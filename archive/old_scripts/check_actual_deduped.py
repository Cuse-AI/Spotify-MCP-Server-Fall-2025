import json
import os

deduped_files = [
    r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\2_deduped\night_youtube_extraction_DEDUPED.json',
    r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\2_deduped\dark_youtube_extraction_DEDUPED.json',
    r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\2_deduped\romantic_youtube_extraction_DEDUPED.json',
    r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\2_deduped\drive_youtube_extraction_DEDUPED.json',
    r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\2_deduped\chill_youtube_extraction_DEDUPED.json',
    r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\2_deduped\sad_youtube_extraction_DEDUPED.json',
    r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\2_deduped\energy_youtube_extraction_DEDUPED.json',
]

print("="*60)
print("TODAY'S DEDUPED FILES - ACTUAL NEW SONGS")
print("="*60)

total = 0
for filepath in deduped_files:
    if os.path.exists(filepath):
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
        count = len(data.get('songs', []))
        vibe = os.path.basename(filepath).split('_')[0].title()
        print(f"{vibe:12} {count:3} NEW songs")
        total += count
    else:
        print(f"Missing: {os.path.basename(filepath)}")

print(f"\n{'='*60}")
print(f"TOTAL NEW SONGS (already deduped): {total}")
print(f"Ananki cost: ${total * 0.003:.2f}")
print(f"After injection: 6,542 + {total} = {6542 + total:,} songs")
