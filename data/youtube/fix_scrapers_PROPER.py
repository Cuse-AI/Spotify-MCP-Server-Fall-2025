"""
PROPER fix for API key rotation - replace the bare except blocks
that are preventing rotation from triggering
"""

import re
from pathlib import Path

def fix_search_playlists(content):
    """Fix search_playlists to properly handle quota errors"""

    # Find and replace the search_playlists method's exception handling
    pattern = r'(def search_playlists\(self, query.*?\):.*?response = request\.execute\(\).*?return playlists\s+)except Exception as e:\s+print\(f"  Error searching playlists: \{e\}"\)\s+return \[\]'

    replacement = r'''\1except HttpError as e:
            # Check if quota exceeded
            if 'quota' in str(e).lower() or (hasattr(e, 'status_code') and e.status_code == 403):
                self.logger.warning(f"[QUOTA] Attempting key rotation for search_playlists...")
                try:
                    self.rotate_api_key()
                    # Retry with new key
                    params = get_diverse_search_params()
                    request = self.youtube.search().list(
                        part='snippet',
                        q=query,
                        type='playlist',
                        maxResults=max_results * 2,
                        order=params['order'],
                        regionCode=params['regionCode']
                    )
                    response = request.execute()

                    playlists = []
                    for item in response.get('items', []):
                        playlists.append({
                            'id': item['id']['playlistId'],
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description']
                        })
                    return playlists
                except Exception as retry_error:
                    self.logger.error(f"Key rotation failed: {retry_error}")
                    return []  # Continue with empty results

            # For other errors, log and return empty
            print(f"  Error searching playlists: {e}")
            return []
        except Exception as e:
            print(f"  Error searching playlists: {e}")
            return []'''

    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def fix_get_playlist(content):
    """Fix get_playlist_videos to properly handle quota errors"""

    # Match the get_playlist_videos with simple exception handling
    pattern = r'(def get_playlist_videos\(self, playlist_id\):.*?return videos\s+)except Exception as e:\s+print\(f"  Error getting playlist: \{e\}"\)\s+return \[\]'

    replacement = r'''\1except HttpError as e:
            if 'quota' in str(e).lower() or (hasattr(e, 'status_code') and e.status_code == 403):
                self.logger.warning(f"[QUOTA] Attempting key rotation for get_playlist_videos...")
                try:
                    self.rotate_api_key()
                    # Retry with new key
                    videos = []
                    request = self.youtube.playlistItems().list(
                        part='snippet',
                        playlistId=playlist_id,
                        maxResults=50
                    )

                    while request and len(videos) < 100:
                        response = request.execute()
                        videos.extend(response.get('items', []))
                        request = self.youtube.playlistItems().list_next(request, response)

                    return videos
                except Exception as retry_error:
                    self.logger.error(f"Key rotation failed: {retry_error}")
                    return []

            print(f"  Error getting playlist: {e}")
            return []
        except Exception as e:
            print(f"  Error getting playlist: {e}")
            return []'''

    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def apply_proper_fixes(file_path):
    """Apply the proper fixes to a scraper"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Apply fixes
    content = fix_search_playlists(content)
    content = fix_get_playlist(content)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    scrapers_dir = Path(__file__).parent / 'scrapers'
    scraper_files = list(scrapers_dir.glob('scrape_*.py'))

    print(f"Found {len(scraper_files)} scrapers")
    print("Applying PROPER rotation fixes...")
    print()

    updated = 0
    for scraper_file in scraper_files:
        vibe = scraper_file.stem.replace('scrape_', '')
        try:
            if apply_proper_fixes(scraper_file):
                print(f"[FIXED] {vibe}")
                updated += 1
            else:
                print(f"[SKIP] {vibe}")
        except Exception as e:
            print(f"[ERROR] {vibe}: {e}")

    print(f"\nUpdated {updated}/{len(scraper_files)} scrapers")
    print("\nNow key rotation should ACTUALLY work!")

if __name__ == '__main__':
    main()
