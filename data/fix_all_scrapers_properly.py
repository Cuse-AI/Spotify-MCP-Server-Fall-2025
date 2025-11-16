"""
Fix ALL Reddit scrapers properly by applying changes from scrape_sad.py template
Uses the WORKING scrape_sad.py as a reference
"""

import re
from pathlib import Path

def fix_scraper_properly(file_path):
    """Fix a single scraper using proper patterns"""
    print(f"\nFixing: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes = []

    # 1. Add quality filter import (if not present)
    if 'from quality_filters import QualityFilter' not in content:
        # Find where to insert (after random import, before load_dotenv)
        insert_pos = content.find('import random')
        if insert_pos > 0:
            next_line = content.find('\n', insert_pos)
            content = (content[:next_line + 1] +
                      '\n# Quality filtering\nimport logging\nsys.path.insert(0, str(Path(__file__).parent.parent))\nfrom quality_filters import QualityFilter\n' +
                      content[next_line + 1:])
            changes.append("Added quality filter import")

    # 2. Fix broken __init__ method
    # Find class definition
    class_match = re.search(r'class (\w+)SmartScraper:', content)
    if class_match:
        # Find __init__ start
        init_start = content.find('def __init__(self):', class_match.end())
        if init_start > 0:
            # Find where __init__ should end (before next method def)
            next_method = content.find('\n    def ', init_start + 20)
            if next_method > 0:
                # Extract the broken __init__
                broken_init = content[init_start:next_method]

                # Rebuild correct __init__
                correct_init = '''def __init__(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
        )

        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )

        self.scraped_urls = set()

        # Pre-load tapestry to skip existing songs
        self.existing_spotify_ids = load_tapestry_spotify_ids()

        # Initialize quality filter
        self.quality_filter = QualityFilter()

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger(__name__)
'''

                # Replace
                content = content[:init_start] + correct_init + content[next_method:]
                changes.append("Fixed __init__ method")

    # 3. Add quality check to extract_from_comment (if not present)
    if 'is_quality_emotional_context' not in content:
        # Find extract_from_comment method
        extract_start = content.find('def extract_from_comment')
        if extract_start > 0:
            # Find where candidates = self.find_music_mentions appears
            candidates_line = content.find('candidates = self.find_music_mentions(comment_text)', extract_start)
            if candidates_line > 0:
                # Insert quality check before candidates line
                indent = '        '
                quality_check = f'''{indent}# QUALITY CHECK FIRST - before Spotify API calls
{indent}is_valid, reject_reason = self.quality_filter.is_quality_emotional_context(comment_text)
{indent}if not is_valid:
{indent}    self.logger.debug(f"Rejected comment ({{reject_reason}}): {{comment_text[:50]}}...")
{indent}    return []

{indent}'''
                content = content[:candidates_line] + quality_check + content[candidates_line:]

                # Add stats tracking after candidates line
                songs_line = content.find('songs = []', candidates_line)
                if songs_line > 0:
                    insert_pos = content.find('\n', content.find('candidates = self.find_music_mentions', candidates_line))
                    content = content[:insert_pos + 1] + f'\n{indent}self.quality_filter.stats[\'songs_extracted\'] += len(candidates)\n' + content[insert_pos + 1:]

                changes.append("Added quality check to extract_from_comment")

    # 4. Add stats logging at end of scrape method (if not present)
    if 'quality_filter.log_stats' not in content:
        # Find "# Deduplicate" comment
        dedupe_line = content.find('# Deduplicate')
        if dedupe_line > 0:
            indent = '        '
            content = content[:dedupe_line] + f'{indent}# Log quality statistics\n{indent}self.quality_filter.log_stats(self.logger)\n\n{indent}' + content[dedupe_line:]
            changes.append("Added stats logging")

    # 5. Fix error handling
    content = re.sub(
        r'print\(f"  Error in r/\{sub_name\}: \{e\}"\)',
        r'self.logger.error(f"Error in r/{sub_name}: {e}", exc_info=True)',
        content
    )
    if 'self.logger.error' in content and 'print(f"  Error' not in content:
        changes.append("Fixed error handling")

    # Write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] Applied {len(changes)} changes")
        for change in changes:
            print(f"    - {change}")
        return True
    else:
        print(f"  [SKIP] Already fixed")
        return False


def main():
    scrapers_dir = Path(__file__).parent / 'reddit' / 'smart_scrapers'
    scraper_files = sorted(scrapers_dir.glob('scrape_*.py'))

    # Exclude scrape_sad.py since it's already fixed
    scraper_files = [f for f in scraper_files if f.name != 'scrape_sad.py']

    print("="*70)
    print("PROPERLY FIXING ALL REDDIT SCRAPERS")
    print("="*70)
    print(f"Found {len(scraper_files)} scrapers to fix\n")

    fixed = 0
    for scraper in scraper_files:
        if fix_scraper_properly(scraper):
            fixed += 1

    print(f"\n{'='*70}")
    print(f"COMPLETE: Fixed {fixed}/{len(scraper_files)} scrapers")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
