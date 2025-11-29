"""
Set ALL scrapers (YouTube + Reddit) to target 100 songs
"""

import re
from pathlib import Path


def update_target(file_path):
    """Update target_songs to 100 in a scraper"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Replace target_songs=1000 or target_songs=1500 with target_songs=100
    content = re.sub(
        r'target_songs=\d+\)',
        'target_songs=100)',
        content
    )

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    # Update YouTube scrapers
    youtube_dir = Path(__file__).parent / 'youtube' / 'scrapers'
    youtube_scrapers = sorted(youtube_dir.glob('scrape_*.py'))

    # Update Reddit scrapers
    reddit_dir = Path(__file__).parent / 'reddit' / 'smart_scrapers'
    reddit_scrapers = sorted(reddit_dir.glob('scrape_*.py'))

    print("="*70)
    print("SETTING ALL SCRAPERS TO TARGET 100 SONGS")
    print("="*70)

    youtube_updated = 0
    for scraper in youtube_scrapers:
        if update_target(scraper):
            youtube_updated += 1

    reddit_updated = 0
    for scraper in reddit_scrapers:
        if update_target(scraper):
            reddit_updated += 1

    print(f"\nYouTube: Updated {youtube_updated}/{len(youtube_scrapers)} scrapers to target 100")
    print(f"Reddit: Updated {reddit_updated}/{len(reddit_scrapers)} scrapers to target 100")
    print(f"\nTotal: {youtube_updated + reddit_updated}/{len(youtube_scrapers) + len(reddit_scrapers)} scrapers updated")
    print("="*70)


if __name__ == '__main__':
    main()
