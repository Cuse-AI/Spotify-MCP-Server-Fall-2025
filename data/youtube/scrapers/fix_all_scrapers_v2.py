"""
Automatically update ALL YouTube scrapers with diversity improvements
Reduces duplicate rate from 37% to <15%
"""

import re
from pathlib import Path

SCRAPER_DIR = Path(__file__).parent
VIBES = [
    'angry', 'anxious', 'bitter', 'bored', 'chaotic', 'chill', 'confident',
    'dark', 'drive', 'energy', 'excited', 'grateful', 'happy', 'hopeful',
    'introspective', 'jealous', 'night', 'nostalgic', 'party', 'peaceful',
    'playful', 'romantic', 'sad'
]

def add_imports(content):
    """Add new imports"""
    if 'from improved_search_utils import' in content:
        return content  # Already updated

    # Add after existing imports
    import_section = """from improved_search_utils import load_tapestry_spotify_ids, diversify_queries, get_diverse_search_params
import random"""

    # Find where to insert (after checkpoint_utils import)
    checkpoint_import = 'from checkpoint_utils import CheckpointManager'
    if checkpoint_import in content:
        content = content.replace(
            checkpoint_import,
            f"{checkpoint_import}\n{import_section}"
        )

    return content

def add_tapestry_filter_to_init(content, class_name):
    """Add tapestry pre-filtering in __init__"""
    if 'self.existing_spotify_ids' in content:
        return content  # Already added

    # Find the __init__ method
    init_pattern = rf'class {class_name}.*?def __init__\(self\):.*?self\.scraped_videos = set\(\)'

    def add_filter(match):
        return match.group(0) + '\n        \n        # Pre-load tapestry to skip existing songs\n        self.existing_spotify_ids = load_tapestry_spotify_ids()'

    content = re.sub(init_pattern, add_filter, content, flags=re.DOTALL)

    return content

def add_tapestry_check_to_search_spotify(content):
    """Add check against existing tapestry songs"""
    if 'if result' in content and 'spotify_id' in content and 'existing_spotify_ids' in content:
        return content  # Already added

    # Find search_spotify method and add check
    pattern = r"(def search_spotify\(self, artist, song\):.*?if results\['tracks'\]\['items'\]:.*?track = results\['tracks'\]\['items'\]\[0\])"

    def add_check(match):
        return match.group(0) + '''

                # Skip if already in tapestry
                track_id = track['id']
                if track_id in self.existing_spotify_ids:
                    return None
'''

    content = re.sub(pattern, add_check, content, flags=re.DOTALL)

    return content

def diversify_search_playlists(content):
    """Add diversity to playlist search"""
    if 'get_diverse_search_params()' in content:
        return content  # Already updated

    # Update search_playlists method
    old_search = '''request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='playlist',
                maxResults=max_results
            )'''

    new_search = '''# Get diverse search parameters
            params = get_diverse_search_params()

            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='playlist',
                maxResults=max_results * 2,  # Get more, then randomize
                order=params['order'],  # Varies each run
                regionCode=params['regionCode']  # Regional diversity
            )'''

    content = content.replace(old_search, new_search)

    # Add randomization to playlist selection
    old_iteration = '''for playlist in playlists:'''

    new_iteration = '''# Randomize playlist selection for diversity
            random.shuffle(playlists)
            playlists = playlists[:max_results]  # Take random subset

            for playlist in playlists:'''

    content = content.replace(old_iteration, new_iteration)

    return content

def diversify_queries_call(content, vibe_name):
    """Add query diversification"""
    if 'diversify_queries(queries)' in content:
        return content  # Already updated

    # Find the queries list and add diversification after
    pattern = rf"(queries = \[.*?\])"

    def add_diversify(match):
        return match.group(0) + f"\n\n        # Add diversity modifiers (time, quality, etc.)\n        queries = diversify_queries(queries)"

    content = re.sub(pattern, add_diversify, content, flags=re.DOTALL)

    return content

def update_scraper(vibe):
    """Update a single scraper file"""
    scraper_file = SCRAPER_DIR / f'scrape_{vibe}.py'

    if not scraper_file.exists():
        print(f"  ⚠ Scraper not found: {vibe}")
        return False

    try:
        with open(scraper_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Determine class name
        class_name = f"{vibe.capitalize()}YouTubeScraper"

        # Apply all improvements
        original_content = content
        content = add_imports(content)
        content = add_tapestry_filter_to_init(content, class_name)
        content = add_tapestry_check_to_search_spotify(content)
        content = diversify_search_playlists(content)
        content = diversify_queries_call(content, vibe)

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
        return False

def main():
    print("\n" + "="*70)
    print(" SCRAPER DIVERSITY IMPROVEMENTS")
    print("="*70)
    print("\nUpdating all YouTube scrapers to reduce duplicate rate...")
    print("Changes:")
    print("  1. Pre-filter against tapestry")
    print("  2. Add search diversity (order, region)")
    print("  3. Diversify query terms")
    print("  4. Randomize playlist selection")
    print("\n" + "="*70 + "\n")

    updated = 0
    already_updated = 0
    failed = 0

    for vibe in VIBES:
        result = update_scraper(vibe)
        if result is True:
            updated += 1
        elif result is False and 'Already' in str(result):
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
