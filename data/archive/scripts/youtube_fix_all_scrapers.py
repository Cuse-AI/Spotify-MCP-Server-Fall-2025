"""
Fix all YouTube scrapers to skip already-processed playlists
This prevents wasting YouTube quota on duplicate playlists
"""

import re
from pathlib import Path

# Get all scraper files
scraper_dir = Path(__file__).parent
scraper_files = list(scraper_dir.glob('scrape_*.py'))

print(f"Found {len(scraper_files)} scrapers to fix\n")

for scraper_file in scraper_files:
    print(f"Fixing: {scraper_file.name}")

    # Read the file
    with open(scraper_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already fixed
    if 'cp.is_playlist_processed' in content:
        print(f"  SKIP - already fixed\n")
        continue

    # Find the pattern where we iterate over playlists
    # Pattern: for playlist in playlists:
    #            if len(cp.all_results) >= target_songs:
    #                break
    #
    #            print(f"  Playlist: {playlist['title']...

    old_pattern = r"(\s+)for playlist in playlists:\s+if len\(cp\.all_results\) >= target_songs:\s+break\s+print\(f\"  Playlist: \{playlist\['title'\]"

    # New code with playlist skip logic
    replacement = r'''\1for playlist in playlists:
\1    if len(cp.all_results) >= target_songs:
\1        break
\1
\1    playlist_id = playlist['id']
\1
\1    # SKIP if we've already processed this playlist
\1    if cp.is_playlist_processed(playlist_id):
\1        print(f"  SKIP (already processed): {playlist['title'][:50].encode('ascii', 'ignore').decode()}...")
\1        continue
\1
\1    print(f"  Playlist: {playlist['title']'''

    # Try to replace
    new_content, count = re.subn(old_pattern, replacement, content, count=1)

    if count == 0:
        print(f"  WARNING - pattern not found, trying alternate pattern\n")
        # Try simpler pattern
        old_pattern2 = r"(\s+)for playlist in playlists:\s+if len\(cp\.all_results\) >= target_songs:\s+break\s+\s+print\(f\"  Playlist:"

        replacement2 = r'''\1for playlist in playlists:
\1    if len(cp.all_results) >= target_songs:
\1        break
\1
\1    playlist_id = playlist['id']
\1
\1    # SKIP if we've already processed this playlist
\1    if cp.is_playlist_processed(playlist_id):
\1        print(f"  SKIP (already processed): {playlist['title'][:50].encode('ascii', 'ignore').decode()}...")
\1        continue
\1
\1    print(f"  Playlist:'''

        new_content, count = re.subn(old_pattern2, replacement2, content, count=1)

        if count == 0:
            print(f"  ERROR - could not find pattern to replace\n")
            continue

    # Now add the playlist marking after processing videos
    # Look for: time.sleep(1)  # Between playlists
    # Add: cp.mark_playlist_processed(playlist_id)

    mark_pattern = r"(\s+)time\.sleep\(1\)  # Between playlists"
    mark_replacement = r"\1cp.mark_playlist_processed(playlist_id)\n\1time.sleep(1)  # Between playlists"

    new_content, mark_count = re.subn(mark_pattern, mark_replacement, new_content, count=1)

    if mark_count == 0:
        print(f"  WARNING - could not add playlist marking\n")

    # Also need to update references to playlist['id'] to use playlist_id variable
    # Replace: get_playlist_videos(playlist['id'])
    new_content = re.sub(r"get_playlist_videos\(playlist\['id'\]\)", "get_playlist_videos(playlist_id)", new_content)

    # Replace: 'playlist_id': playlist['id']
    new_content = re.sub(r"'playlist_id': playlist\['id'\]", "'playlist_id': playlist_id", new_content)

    # Write the fixed file
    with open(scraper_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  FIXED - added playlist skip logic\n")

print("All scrapers fixed!")
