"""
Fix Silent Failures in All Reddit Scrapers
Per Replit feedback: Add logging to is_valid_track() and search_spotify()
"""

import re
from pathlib import Path


def fix_silent_failures(file_path):
    """Fix silent failures in is_valid_track() and search_spotify()"""
    print(f"\nFixing: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes = []

    # Fix #1: is_valid_track() exception handler
    old_except_1 = r'except:\s+return True\s+#\s+If we can\'t check, allow it \(TRUE Ananki will catch false positives\)'
    new_except_1 = '''except Exception as e:
            self.logger.warning(f"Failed to validate track '{track.get('name', 'unknown')}': {e}")
            return True  # Allow on validation failure - quality filter will catch bad comments'''

    if re.search(old_except_1, content):
        content = re.sub(old_except_1, new_except_1, content)
        changes.append("Fixed is_valid_track() logging")

    # Fix #2: search_spotify() exception handler
    # Find search_spotify method and fix its bare except
    search_method = re.search(
        r'(def search_spotify\(self, query_text\):.*?)'
        r'(except:)\s+'
        r'(return None)',
        content,
        re.DOTALL
    )

    if search_method:
        # Replace bare except with proper logging
        old_except_2 = search_method.group(2) + '\n            ' + search_method.group(3)
        new_except_2 = '''except Exception as e:
            self.logger.debug(f"Spotify search failed for '{query_text[:50]}': {e}")
            return None'''

        content = content.replace(old_except_2, new_except_2)
        changes.append("Fixed search_spotify() logging")

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

    print("="*70)
    print("FIXING SILENT FAILURES IN ALL REDDIT SCRAPERS")
    print("="*70)
    print(f"Found {len(scraper_files)} scrapers to fix\n")

    fixed = 0
    for scraper in scraper_files:
        if fix_silent_failures(scraper):
            fixed += 1

    print(f"\n{'='*70}")
    print(f"COMPLETE: Fixed {fixed}/{len(scraper_files)} scrapers")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
