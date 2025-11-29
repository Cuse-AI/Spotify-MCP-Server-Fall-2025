"""
Automatically update ALL Reddit scrapers with diversity improvements
Reduces duplicate rate by pre-filtering and varying searches
"""

import re
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'youtube' / 'scrapers'))

SCRAPER_DIR = Path(__file__).parent
VIBES = [
    'angry', 'anxious', 'bitter', 'bored', 'chaotic', 'chill', 'confident',
    'dark', 'drive', 'energy', 'excited', 'grateful', 'happy', 'hopeful',
    'introspective', 'jealous', 'night', 'nostalgic', 'party', 'peaceful',
    'playful', 'romantic', 'sad'
]

def add_imports(content):
    """Add tapestry pre-filtering import"""
    if 'load_tapestry_spotify_ids' in content:
        return content  # Already updated

    # Add after existing imports
    import_section = """
# Import tapestry pre-filtering
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'youtube' / 'scrapers'))
from improved_search_utils import load_tapestry_spotify_ids
import random"""

    # Find where to insert (after checkpoint_utils import)
    checkpoint_import = 'from checkpoint_utils import CheckpointManager'
    if checkpoint_import in content:
        content = content.replace(
            checkpoint_import,
            f"{checkpoint_import}{import_section}"
        )

    return content

def add_tapestry_filter_to_init(content, class_name):
    """Add tapestry pre-filtering in __init__"""
    if 'self.existing_spotify_ids' in content:
        return content  # Already added

    # Find the __init__ method
    init_pattern = rf'class {class_name}.*?def __init__\(self\):.*?self\.scraped_urls = set\(\)'

    def add_filter(match):
        return match.group(0) + '\n        \n        # Pre-load tapestry to skip existing songs\n        self.existing_spotify_ids = load_tapestry_spotify_ids()'

    content = re.sub(init_pattern, add_filter, content, flags=re.DOTALL)

    return content

def add_tapestry_check_to_search_spotify(content):
    """Add check against existing tapestry songs"""
    if 'existing_spotify_ids' in content and 'spotify_id' in content and 'in self.existing_spotify_ids' in content:
        return content  # Already added

    # Find search_spotify method and add check
    pattern = r"(def search_spotify\(self, query_text\):.*?if results\['tracks'\]\['items'\]:.*?track = results\['tracks'\]\['items'\]\[0\])"

    def add_check(match):
        return match.group(0) + '''

                # Skip if already in tapestry
                track_id = track['id']
                if track_id in self.existing_spotify_ids:
                    return None
'''

    content = re.sub(pattern, add_check, content, flags=re.DOTALL)

    return content

def randomize_subreddit_order(content):
    """Add randomization to subreddit search order"""
    if 'random.shuffle(subreddits)' in content:
        return content  # Already added

    # Find subreddits list and add shuffle after
    pattern = r"(subreddits = \[.*?\])"

    def add_shuffle(match):
        return match.group(0) + "\n        random.shuffle(subreddits)  # Randomize search order for diversity"

    content = re.sub(pattern, add_shuffle, content, flags=re.DOTALL)

    return content

def add_time_filters(content):
    """Add time-based search filters to find fresh content"""
    if "time_filter=" in content:
        return content  # Already added

    # Find submission search and add time filter variety
    old_search = r"subreddit\.search\(query, limit=(\d+)\)"
    new_search = r"subreddit.search(query, limit=\1, time_filter=random.choice(['week', 'month', 'year', 'all']))"

    content = re.sub(old_search, new_search, content)

    return content

def update_scraper(vibe):
    """Update a single scraper file"""
    scraper_file = SCRAPER_DIR / f'scrape_{vibe}.py'

    if not scraper_file.exists():
        print(f"  [SKIP] Scraper not found: {vibe}")
        return False

    try:
        with open(scraper_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Determine class name
        class_name = f"{vibe.capitalize()}SmartScraper"

        # Apply all improvements
        original_content = content
        content = add_imports(content)
        content = add_tapestry_filter_to_init(content, class_name)
        content = add_tapestry_check_to_search_spotify(content)
        content = randomize_subreddit_order(content)
        content = add_time_filters(content)

        # Only write if changed
        if content != original_content:
            with open(scraper_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] Updated: {vibe}")
            return True
        else:
            print(f"  [-] Already updated: {vibe}")
            return False

    except Exception as e:
        print(f"  [ERROR] Error updating {vibe}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*70)
    print(" REDDIT SCRAPER DIVERSITY IMPROVEMENTS")
    print("="*70)
    print("\nUpdating all Reddit scrapers to reduce duplicate rate...")
    print("Changes:")
    print("  1. Pre-filter against tapestry (skip existing songs)")
    print("  2. Randomize subreddit search order")
    print("  3. Add time-based search filters (week/month/year/all)")
    print("\n" + "="*70 + "\n")

    updated = 0
    already_updated = 0
    failed = 0

    for vibe in VIBES:
        result = update_scraper(vibe)
        if result is True:
            updated += 1
        elif result is False:
            already_updated += 1
        else:
            failed += 1

    print("\n" + "="*70)
    print(" SUMMARY")
    print("="*70)
    print(f"  Updated: {updated}")
    print(f"  Already current: {already_updated}")
    print(f"  Failed: {failed}")
    print(f"  Total scrapers: {len(VIBES)}")
    print("\n[OK] Next scrape will find more unique content!")

if __name__ == '__main__':
    main()
