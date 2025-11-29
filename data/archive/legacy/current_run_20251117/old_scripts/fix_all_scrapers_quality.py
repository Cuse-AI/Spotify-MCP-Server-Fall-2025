"""
Apply Quality Filters and Proper Error Handling to ALL Scrapers

Based on Replit's analysis:
1. Add quality filter import and initialization
2. Add proper logging
3. Apply filter BEFORE Spotify search in extract_from_comment
4. Track rejection statistics
5. Fix error handling (no more bare except)
"""

import re
from pathlib import Path


def fix_scraper(file_path):
    """Add quality filters and proper error handling to a scraper"""
    print(f"\nFixing: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = []

    # 1. Add quality filter import after other imports
    if 'from quality_filters import QualityFilter' not in content:
        # Find imports section
        import_section_end = content.find('\nclass ')
        if import_section_end > 0:
            # Add before class definition
            new_imports = "\n# Quality filtering\nimport logging\nfrom quality_filters import QualityFilter\n\n"
            content = content[:import_section_end] + new_imports + content[import_section_end:]
            changes.append("Added quality filter import")

    # 2. Add quality filter initialization in __init__
    init_pattern = r'(def __init__\(self\):.*?self\.reddit = praw\.Reddit\([^)]+\))'
    if re.search(init_pattern, content, re.DOTALL):
        replacement = r'\1\n\n        # Initialize quality filter\n        self.quality_filter = QualityFilter()\n\n        # Setup logging\n        logging.basicConfig(\n            level=logging.INFO,\n            format=\'%(asctime)s [%(levelname)s] %(message)s\'\n        )\n        self.logger = logging.getLogger(__name__)'
        content = re.sub(init_pattern, replacement, content, flags=re.DOTALL)
        changes.append("Added quality filter and logging to __init__")

    # 3. Add quality check in extract_from_comment BEFORE Spotify search
    # Find where songs are appended
    extract_pattern = r'(def extract_from_comment.*?)(for candidate in candidates:.*?result = self\.search_spotify)'
    if re.search(extract_pattern, content, re.DOTALL):
        # Add quality check before the loop
        replacement = r'\1# QUALITY CHECK FIRST - before Spotify API calls\n        is_valid, reject_reason = self.quality_filter.is_quality_emotional_context(comment_text)\n        if not is_valid:\n            self.logger.debug(f"Rejected comment ({reject_reason}): {comment_text[:50]}...")\n            return []\n\n        self.quality_filter.stats[\'songs_extracted\'] += len(candidates)\n\n        \2'
        content = re.sub(extract_pattern, replacement, content, flags=re.DOTALL, count=1)
        changes.append("Added quality check before Spotify search")

    # 4. Add stats logging at end of scrape method
    return_pattern = r'(return unique\[:target_songs\])'
    if return_pattern in content:
        replacement = r'# Log quality statistics\n        self.quality_filter.log_stats(self.logger)\n\n        \1'
        content = re.sub(return_pattern, replacement, content)
        changes.append("Added stats logging")

    # 5. Fix bare except blocks
    bare_except_pattern = r'except Exception as e:\s+print\(f"'
    if re.search(bare_except_pattern, content):
        content = re.sub(
            r'except Exception as e:\s+print\(f"([^"]+)"\)',
            r'except Exception as e:\n                self.logger.error(f"\1", exc_info=True)',
            content
        )
        changes.append("Fixed error handling")

    if changes:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] Applied {len(changes)} changes")
        for change in changes:
            print(f"    - {change}")
        return True
    else:
        print(f"  [SKIP] Already fixed or no changes needed")
        return False


def main():
    # Fix all Reddit smart scrapers
    reddit_scrapers = Path(__file__).parent / 'reddit' / 'smart_scrapers'
    reddit_scrapers = reddit_scrapers.glob('scrape_*.py')

    print("="*70)
    print("APPLYING QUALITY FILTERS TO ALL SCRAPERS")
    print("="*70)

    fixed = 0
    for scraper in sorted(reddit_scrapers):
        if fix_scraper(scraper):
            fixed += 1

    print(f"\n{'='*70}")
    print(f"COMPLETE: Fixed {fixed} scrapers")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
