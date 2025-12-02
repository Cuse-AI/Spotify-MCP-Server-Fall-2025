"""
Apply YouTube API Manager to ALL YouTube Scrapers
Uses the working party scraper as a template
"""

import re
from pathlib import Path
import shutil

def update_scraper(file_path):
    """Update a single scraper to use API manager"""
    print(f"\nUpdating: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Backup
    backup_path = file_path.with_suffix('.py.backup')
    shutil.copy(file_path, backup_path)

    changes = []

    # 1. Add API manager import if not present
    if 'from youtube_api_manager import YouTubeAPIManager' not in content:
        # Add after other imports, before class definition
        old_imports = 'import random\n\nload_dotenv()'
        new_imports = '''import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()'''

        if old_imports in content:
            content = content.replace(old_imports, new_imports)

        # Add API manager import
        old_import_line = 'from improved_search_utils import'
        new_import_line = 'from youtube_api_manager import YouTubeAPIManager\nfrom improved_search_utils import'
        content = content.replace(old_import_line, new_import_line)
        changes.append("Added imports")

    # 2. Replace YouTube initialization
    old_init = '''# Initialize YouTube
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY not found in .env")
        self.youtube = build('youtube', 'v3', developerKey=api_key)'''

    new_init = '''# Initialize YouTube with API Manager (supports rotation)
        logger.info("Initializing YouTube API Manager...")
        self.youtube_manager = YouTubeAPIManager()
        logger.info(f"YouTube API ready: {self.youtube_manager.get_current_key_info()}")'''

    if old_init in content:
        content = content.replace(old_init, new_init)
        changes.append("Updated __init__")

    # 3. Update search_playlists to use API manager
    # Find the method and replace self.youtube.search() calls
    content = re.sub(
        r'request = self\.youtube\.search\(\)\.list\(',
        'logger.info(f"Searching: \\'{query[:50]}...\\' (order={params[\\'order\\']}, region={params[\\'regionCode\\']})\")\n\n            # Use API manager\n            response, error = self.youtube_manager.search(',
        content
    )

    content = re.sub(
        r'\)\s*response = request\.execute\(\)',
        '''\n            )

            if error:
                logger.error(f"[X] API Error: {error}")
                if error.get('all_keys_exhausted'):
                    raise Exception("All YouTube API keys exhausted")
                return []''',
        content
    )

    if 'response, error = self.youtube_manager.search' in content:
        changes.append("Updated search_playlists")

    # 4. Replace old error prints with logger
    content = content.replace('print(f"  Error searching playlists: {e}")',
                              'logger.error(f"[X] Error: {e}")')
    content = content.replace('print(f"  Error getting playlist: {e}")',
                              'logger.error(f"[X] Error getting playlist: {e}")')

    if changes:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] Applied {len(changes)} changes: {', '.join(changes)}")
        return True
    else:
        print(f"  [SKIP] Already updated")
        return False

def main():
    scrapers_dir = Path(__file__).parent
    scraper_files = sorted(scrapers_dir.glob('scrape_*.py'))

    print("="*70)
    print("APPLYING API MANAGER TO ALL YOUTUBE SCRAPERS")
    print("="*70)
    print(f"Found {len(scraper_files)} scrapers\n")

    updated = 0
    for scraper in scraper_files:
        if update_scraper(scraper):
            updated += 1

    print(f"\n{'='*70}")
    print(f"COMPLETE: Updated {updated}/{len(scraper_files)} scrapers")
    print(f"{'='*70}")
    print("\nAll scrapers now have:")
    print("  - YouTube API Manager with 2-key rotation")
    print("  - Comprehensive error logging")
    print("  - Automatic key fallback on quota errors")

if __name__ == '__main__':
    main()
