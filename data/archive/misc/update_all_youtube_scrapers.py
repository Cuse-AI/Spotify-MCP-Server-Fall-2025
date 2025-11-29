"""
Update ALL YouTube scrapers with:
1. Improved quality filters (relaxed thresholds)
2. Proper logging
3. Quality check when selecting comments
4. Stats tracking
"""

import re
from pathlib import Path


def update_youtube_scraper(file_path):
    """Update a single YouTube scraper"""
    print(f"\nUpdating: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes = []

    # 1. Add quality filter import (after other imports)
    if 'from improved_quality_filters import ImprovedQualityFilter' not in content:
        # Find the last import before load_dotenv
        load_dotenv_pos = content.find('load_dotenv()')
        if load_dotenv_pos > 0:
            # Find the last import line before load_dotenv
            imports_section = content[:load_dotenv_pos]
            last_import = imports_section.rfind('\nimport ')
            if last_import < 0:
                last_import = imports_section.rfind('\nfrom ')

            if last_import > 0:
                insert_pos = content.find('\n', last_import + 1)
                content = (content[:insert_pos + 1] +
                          'import logging\n' +
                          'from improved_quality_filters import ImprovedQualityFilter\n' +
                          content[insert_pos + 1:])
                changes.append("Added quality filter import")

    # 2. Add quality filter initialization in __init__
    if 'self.quality_filter = ImprovedQualityFilter()' not in content:
        # Find __init__ method and add after existing_spotify_ids line
        init_match = re.search(
            r'(self\.existing_spotify_ids = load_tapestry_spotify_ids\(\))',
            content
        )
        if init_match:
            insert_pos = content.find('\n', init_match.end())
            content = (content[:insert_pos + 1] +
                      '\n        # Initialize quality filter\n' +
                      '        self.quality_filter = ImprovedQualityFilter()\n' +
                      '\n        # Setup logging\n' +
                      '        logging.basicConfig(\n' +
                      '            level=logging.INFO,\n' +
                      "            format='%(asctime)s [%(levelname)s] %(message)s'\n" +
                      '        )\n' +
                      '        self.logger = logging.getLogger(__name__)\n' +
                      content[insert_pos + 1:])
            changes.append("Added quality filter initialization")

    # 3. Update comment selection to use quality filter
    # Find the "Find best emotional comment" section
    comment_section = re.search(
        r'# Find best emotional comment\s+best_comment = "".*?best_likes = comment\[\'likes\'\]',
        content,
        re.DOTALL
    )

    if comment_section and 'is_quality_emotional_context' not in comment_section.group():
        old_section = comment_section.group()
        new_section = '''# Find best emotional comment (with quality filtering)
                        best_comment = ""
                        best_likes = 0
                        for comment in comments:
                            comment_text = comment['text']
                            # Check quality FIRST
                            is_valid, _ = self.quality_filter.is_quality_emotional_context(
                                comment_text,
                                post_title=playlist['title'],
                                post_body=playlist.get('description', '')
                            )
                            if is_valid and comment['likes'] > best_likes:
                                best_comment = comment_text
                                best_likes = comment['likes']
                                self.quality_filter.stats['songs_extracted'] += 1'''

        content = content.replace(old_section, new_section)
        changes.append("Updated comment selection with quality filter")

    # 4. Add stats logging at end of scrape method
    if 'quality_filter.log_stats' not in content:
        # Find the return statement near the end of the scrape method
        # Look for "return cp.all_results[:target_songs]" or similar
        return_match = re.search(
            r'(\n\s+)(return (?:cp\.all_results|unique)\[:target_songs\])',
            content
        )
        if return_match:
            indent = return_match.group(1)
            content = content.replace(
                return_match.group(),
                f'{indent}# Log quality statistics\n' +
                f'{indent}self.quality_filter.log_stats(self.logger)\n' +
                f'{indent}\n' +
                return_match.group(2)
            )
            changes.append("Added stats logging")

    # 5. Fix bare except in search_spotify if it exists
    if 'except:\n            return None' in content:
        content = content.replace(
            'except:\n            return None',
            'except Exception as e:\n            self.logger.debug(f"Spotify search failed: {e}")\n            return None'
        )
        changes.append("Fixed search_spotify logging")

    # 6. Fix bare except in get_video_comments if it exists
    if 'def get_video_comments' in content and 'except:\n            return []' in content:
        # Find the get_video_comments method
        method_start = content.find('def get_video_comments')
        method_section = content[method_start:method_start + 500]
        if 'except:\n            return []' in method_section:
            content = content.replace(
                'except:\n            return []',
                'except Exception as e:\n            self.logger.debug(f"Failed to get comments: {e}")\n            return []',
                1  # Only replace first occurrence in get_video_comments
            )
            changes.append("Fixed get_video_comments logging")

    # Write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] Applied {len(changes)} changes")
        for change in changes:
            print(f"    - {change}")
        return True
    else:
        print(f"  [SKIP] Already updated")
        return False


def main():
    scrapers_dir = Path(__file__).parent / 'scrapers'
    scraper_files = sorted(scrapers_dir.glob('scrape_*.py'))

    print("="*70)
    print("UPDATING ALL YOUTUBE SCRAPERS")
    print("="*70)
    print(f"Found {len(scraper_files)} scrapers\n")

    updated = 0
    for scraper in scraper_files:
        if update_youtube_scraper(scraper):
            updated += 1

    print(f"\n{'='*70}")
    print(f"COMPLETE: Updated {updated}/{len(scraper_files)} scrapers")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
