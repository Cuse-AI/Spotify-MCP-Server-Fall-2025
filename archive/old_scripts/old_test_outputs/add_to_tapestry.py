"""
Add scraped songs to NEW_TAPESTRY and track counts.
Songs go into 'songs' array (flat) - Ananki will later assign to vibes.
"""
import json
from datetime import datetime

TAPESTRY_PATH = r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\testing\scrapers\output\NEW_TAPESTRY.json'

def add_songs_to_tapestry(songs_file: str):
    """Add songs from a scrape output file to the new tapestry."""
    
    # Load current tapestry
    with open(TAPESTRY_PATH, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Load new songs
    with open(songs_file, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    new_songs = new_data.get('songs', [])
    
    # Dedupe against existing
    existing_keys = set()
    for s in tapestry['songs']:
        key = (s['artist'].lower(), s['song'].lower())
        existing_keys.add(key)
    
    added = 0
    for song in new_songs:
        key = (song['artist'].lower(), song['song'].lower())
        if key not in existing_keys:
            tapestry['songs'].append(song)
            existing_keys.add(key)
            added += 1
    
    # Update counts
    tapestry['counts']['total'] = len(tapestry['songs'])
    tapestry['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Save
    with open(TAPESTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    
    print(f"Added {added} new songs")
    print(f"Total songs in new tapestry: {tapestry['counts']['total']}")
    return added

if __name__ == '__main__':
    # Add the combined 15 songs
    combined_file = r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\testing\scrapers\output\COMBINED_15_songs.json'
    add_songs_to_tapestry(combined_file)
