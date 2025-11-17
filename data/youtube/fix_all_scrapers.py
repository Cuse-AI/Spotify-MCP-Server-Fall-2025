"""
Applies Architect's 3 fixes to all YouTube scrapers:
1. Surface API errors (don't swallow exceptions)
2. Add API key rotation
3. Proper quota detection and handling
"""

import re
from pathlib import Path

def apply_fixes_to_scraper(file_path):
    """Apply all 3 Architect fixes to a single scraper"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Fix 1: Add HttpError import
    if 'from googleapiclient.errors import HttpError' not in content:
        # Add after googleapiclient.discovery import
        content = content.replace(
            'from googleapiclient.discovery import build',
            'from googleapiclient.discovery import build\nfrom googleapiclient.errors import HttpError'
        )

    # Fix 2: Replace __init__ to support API key rotation
    init_pattern = r'(class \w+YouTubeScraper:.*?def __init__\(self\):.*?# Initialize YouTube\s+)(api_key = os\.getenv\(\'YOUTUBE_API_KEY\'\).*?self\.youtube = build\(\'youtube\', \'v3\', developerKey=api_key\))'

    new_init = r'''\1# API key rotation support
        self.api_keys = [
            os.getenv('YOUTUBE_API_KEY'),
            os.getenv('YOUTUBE_API_KEY_2')
        ]
        self.api_keys = [k for k in self.api_keys if k]  # Remove None values
        if not self.api_keys:
            raise ValueError("No YOUTUBE_API_KEY found in .env")

        self.current_key_index = 0
        self.youtube = build('youtube', 'v3', developerKey=self.api_keys[self.current_key_index])
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized with {len(self.api_keys)} API key(s)")'''

    content = re.sub(init_pattern, new_init, content, flags=re.DOTALL)

    # Fix 3: Add rotate_api_key method (after __init__)
    if 'def rotate_api_key(self):' not in content:
        # Find the end of __init__ method
        init_end_pattern = r'(def __init__\(self\):.*?self\.existing_spotify_ids = load_tapestry_spotify_ids\(\))\s*\n'

        rotate_method = r'''\1

    def rotate_api_key(self):
        """Switch to next API key when quota exhausted"""
        if len(self.api_keys) <= 1:
            self.logger.error("No additional API keys available for rotation")
            raise Exception("All API keys exhausted")

        old_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.youtube = build('youtube', 'v3', developerKey=self.api_keys[self.current_key_index])
        self.logger.warning(f"[API KEY ROTATION] Switched from key #{old_index + 1} to key #{self.current_key_index + 1}")

'''

        content = re.sub(init_end_pattern, rotate_method, content, flags=re.DOTALL)

    # Fix 4: Update search_playlists to surface errors
    search_playlists_pattern = r'(def search_playlists\(self, query.*?\):.*?try:.*?)(except:.*?return \[\])'

    new_error_handling = r'''\1except HttpError as e:
            # Log the specific error
            self.logger.error(f"YouTube API error in search_playlists: {e.status_code if hasattr(e, 'status_code') else 'unknown'}")

            # Check if quota exceeded
            if 'quota' in str(e).lower() or (hasattr(e, 'status_code') and e.status_code == 403):
                self.logger.error("[QUOTA EXCEEDED] YouTube API quota exhausted!")
                # Try rotating API key
                try:
                    self.rotate_api_key()
                    # Retry with new key
                    response = self.youtube.search().list(
                        q=query,
                        type='playlist',
                        part='snippet',
                        maxResults=10
                    ).execute()
                    return response.get('items', [])
                except Exception as rotate_error:
                    self.logger.error(f"API key rotation failed: {rotate_error}")
                    raise  # Re-raise original error

            # Re-raise for other errors
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in search_playlists: {e}")
            raise'''

    content = re.sub(search_playlists_pattern, new_error_handling, content, flags=re.DOTALL)

    # Fix 5: Update get_playlist_videos to surface errors
    get_playlist_pattern = r'(def get_playlist_videos\(self, playlist_id.*?\):.*?try:.*?)(except:.*?return \[\])'

    new_playlist_error_handling = r'''\1except HttpError as e:
            self.logger.error(f"YouTube API error in get_playlist_videos: {e.status_code if hasattr(e, 'status_code') else 'unknown'}")

            if 'quota' in str(e).lower() or (hasattr(e, 'status_code') and e.status_code == 403):
                self.logger.error("[QUOTA EXCEEDED] Attempting API key rotation...")
                try:
                    self.rotate_api_key()
                    # Retry with new key
                    response = self.youtube.playlistItems().list(
                        playlistId=playlist_id,
                        part='contentDetails',
                        maxResults=50
                    ).execute()

                    video_ids = [item['contentDetails']['videoId'] for item in response.get('items', [])]
                    return video_ids[:20]
                except Exception as rotate_error:
                    self.logger.error(f"API key rotation failed: {rotate_error}")
                    raise

            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in get_playlist_videos: {e}")
            raise'''

    content = re.sub(get_playlist_pattern, new_playlist_error_handling, content, flags=re.DOTALL)

    # Fix 6: Update get_video_comments to surface errors
    get_comments_pattern = r'(def get_video_comments\(self, video_id.*?\):.*?try:.*?)(except:.*?return \[\])'

    new_comments_error_handling = r'''\1except HttpError as e:
            # Comments disabled is expected, don't log as error
            if 'commentsDisabled' in str(e):
                return []

            self.logger.error(f"YouTube API error in get_video_comments: {e.status_code if hasattr(e, 'status_code') else 'unknown'}")

            if 'quota' in str(e).lower() or (hasattr(e, 'status_code') and e.status_code == 403):
                self.logger.error("[QUOTA EXCEEDED] Attempting API key rotation...")
                try:
                    self.rotate_api_key()
                    # Retry with new key
                    response = self.youtube.commentThreads().list(
                        videoId=video_id,
                        part='snippet',
                        maxResults=100,
                        order='relevance'
                    ).execute()

                    comments = []
                    for item in response.get('items', []):
                        comment = item['snippet']['topLevelComment']['snippet']
                        comments.append({
                            'text': comment['textDisplay'],
                            'likes': comment['likeCount']
                        })

                    return sorted(comments, key=lambda x: x['likes'], reverse=True)[:10]
                except Exception as rotate_error:
                    self.logger.error(f"API key rotation failed: {rotate_error}")
                    return []  # For comments, we can continue without them

            return []  # For other comment errors, continue
        except Exception as e:
            self.logger.error(f"Unexpected error in get_video_comments: {e}")
            return []  # Comments are optional'''

    content = re.sub(get_comments_pattern, new_comments_error_handling, content, flags=re.DOTALL)

    # Check if anything changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    scrapers_dir = Path(__file__).parent / 'scrapers'

    scraper_files = list(scrapers_dir.glob('scrape_*.py'))

    print(f"Found {len(scraper_files)} YouTube scrapers")
    print("Applying Architect's 3 fixes:")
    print("  1. Surface API errors (HttpError handling)")
    print("  2. API key rotation")
    print("  3. Quota detection and retry logic")
    print()

    updated = 0
    for scraper_file in scraper_files:
        vibe = scraper_file.stem.replace('scrape_', '')
        try:
            if apply_fixes_to_scraper(scraper_file):
                print(f"[UPDATED] {vibe}")
                updated += 1
            else:
                print(f"[SKIP] {vibe} - already has fixes")
        except Exception as e:
            print(f"[ERROR] {vibe}: {e}")

    print(f"\nUpdated {updated}/{len(scraper_files)} scrapers")

if __name__ == '__main__':
    main()
