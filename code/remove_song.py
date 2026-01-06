"""
Quick script to remove a song from tapestry.json by spotify_id
Handles the vibe-organized structure
"""
import json
import shutil
from datetime import datetime
import sys

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Song to remove
SPOTIFY_ID_TO_REMOVE = "2mqaYmF0XmV8egZB6jQOtN"  # Man! I Feel Like A Woman! - Shania Twain

# Files to update
TAPESTRY_FILES = [
    r"C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json",
    r"C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\code\web\core\tapestry.json"
]

def remove_song(filepath, spotify_id):
    """Remove a song from tapestry by spotify_id"""
    # Load the file
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Track what we find
    found = False
    total_removed = 0
    
    # Iterate through each vibe
    for vibe_name, vibe_data in data.get('vibes', {}).items():
        songs = vibe_data.get('songs', [])
        original_count = len(songs)
        
        # Find and show the song being removed
        for song in songs:
            if song.get('spotify_id') == spotify_id:
                found = True
                print(f"\n[FOUND in '{vibe_name}']")
                print(f"   Artist: {song.get('artist')}")
                print(f"   Song: {song.get('song')}")
                comment = song.get('comment_text', 'N/A')
                print(f"   Comment: {comment[:100] if comment else 'N/A'}...")
        
        # Filter out the song
        vibe_data['songs'] = [s for s in songs if s.get('spotify_id') != spotify_id]
        
        removed_count = original_count - len(vibe_data['songs'])
        total_removed += removed_count
    
    if not found:
        print(f"[ERROR] Song with spotify_id {spotify_id} not found in {filepath}")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.replace('.json', f'_backup_{timestamp}.json')
    shutil.copy(filepath, backup_path)
    print(f"[BACKUP] Created: {backup_path}")
    
    # Save
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"[REMOVED] {total_removed} instance(s) from {filepath}")
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("SONG REMOVAL SCRIPT")
    print("=" * 50)
    print(f"Removing spotify_id: {SPOTIFY_ID_TO_REMOVE}")
    
    for filepath in TAPESTRY_FILES:
        print(f"\n[FILE] Processing: {filepath}")
        remove_song(filepath, SPOTIFY_ID_TO_REMOVE)
    
    print("\n" + "=" * 50)
    print("Done! Remember to redeploy to Vercel if needed.")
    print("=" * 50)
