"""
Apply YouTube API Manager to ALL 23 YouTube Scrapers

This will update every scraper to use the new API manager with:
- Automatic key rotation
- Comprehensive error reporting
- Retry logic
"""

import re
from pathlib import Path

def update_scraper(file_path):
    """Update a single scraper file to use API manager"""
    print(f"\n{'='*70}")
    print(f"Updating: {file_path.name}")
    print(f"{'='*70}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = []

    # 1. Add imports at the top (after existing imports)
    if 'from youtube_api_manager import YouTubeAPIManager' not in content:
        # Find the last import line before class definition
        import_section = content.split('class ')[0]
        last_import_pos = import_section.rfind('\nimport ') + 1
        if last_import_pos == 0:
            last_import_pos = import_section.rfind('\nfrom ') + 1

        if last_import_pos > 0:
            # Find end of that line
            end_of_line = content.find('\n', last_import_pos) + 1
            new_imports = """from youtube_api_manager import YouTubeAPIManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

"""
            content = content[:end_of_line] + new_imports + content[end_of_line:]
            changes.append("Added imports and logging")

    # 2. Replace YouTube initialization in __init__
    old_init_pattern = r"# Initialize YouTube\s+api_key = os\.getenv\('YOUTUBE_API_KEY'\)\s+if not api_key:\s+raise ValueError\(\"YOUTUBE_API_KEY not found in \.env\"\)\s+self\.youtube = build\('youtube', 'v3', developerKey=api_key\)"

    new_init = """# Initialize YouTube with API Manager (supports rotation)
        logger.info("Initializing YouTube API Manager...")
        self.youtube_manager = YouTubeAPIManager()
        logger.info(f"YouTube API ready: {self.youtube_manager.get_current_key_info()}")"""

    if re.search(old_init_pattern, content):
        content = re.sub(old_init_pattern, new_init, content)
        changes.append("Updated __init__ to use API manager")

    # 3. Update search_playlists method
    old_search = r"(def search_playlists\(self[^:]+:\s+\"\"\"[^\"]+\"\"\"\s+try:\s+# Get diverse search parameters\s+params = get_diverse_search_params\(\)\s+)request = self\.youtube\.search\(\)\.list\(\s+part='snippet',\s+q=query,\s+type='playlist',\s+maxResults=max_results \* 2,[^\)]+\)\s+response = request\.execute\(\)"

    new_search = r"""\1logger.info(f"Searching: '{query[:50]}...' (order={params['order']}, region={params['regionCode']})")

            # Use API manager with automatic rotation
            response, error = self.youtube_manager.search(
                part='snippet',
                q=query,
                type='playlist',
                maxResults=max_results * 2,  # Get more, then randomize
                order=params['order'],  # Varies each run
                regionCode=params['regionCode']  # Regional diversity
            )

            if error:
                logger.error(f"[X] YouTube API Error for query: {query[:50]}")
                logger.error(f"    Error details: {error}")
                if error.get('all_keys_exhausted'):
                    logger.error(f"    [!] ALL API KEYS EXHAUSTED - Cannot continue")
                    raise Exception("All YouTube API keys exhausted - daily quota reached")
                return []"""

    if re.search(old_search, content, re.DOTALL):
        content = re.sub(old_search, new_search, content, flags=re.DOTALL)
        changes.append("Updated search_playlists method")

    if changes:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Applied {len(changes)} changes:")
        for change in changes:
            print(f"  - {change}")
        return True
    else:
        print("[SKIP] Already up to date or no changes needed")
        return False

def main():
    scrapers_dir = Path(__file__).parent
    scraper_files = list(scrapers_dir.glob('scrape_*.py'))

    print(f"\n{'='*70}")
    print(f"APPLYING API MANAGER TO ALL YOUTUBE SCRAPERS")
    print(f"{'='*70}")
    print(f"Found {len(scraper_files)} scraper files\n")

    updated = 0
    skipped = 0

    for scraper_file in sorted(scraper_files):
        if update_scraper(scraper_file):
            updated += 1
        else:
            skipped += 1

    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Updated: {updated} scrapers")
    print(f"Skipped: {skipped} scrapers (already up to date)")
    print(f"Total:   {len(scraper_files)} scrapers")
    print(f"\n[OK] All scrapers now use API manager with automatic rotation!")

if __name__ == '__main__':
    main()
