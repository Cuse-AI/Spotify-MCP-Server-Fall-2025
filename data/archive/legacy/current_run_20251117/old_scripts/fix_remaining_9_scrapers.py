"""
Fix the 9 remaining scrapers that still have bare except in is_valid_track()
Per code review: scrape_bitter, bored, chaotic, confident, excited, grateful, hopeful, jealous, playful
"""

from pathlib import Path

def fix_is_valid_track_logging(file_path):
    """Fix bare except in is_valid_track() method"""
    print(f"Fixing: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Find and replace bare except in is_valid_track
    # Some scrapers have the comment, some don't
    old_code_with_comment = '''        except:
            return True  # If we can't check, allow it (TRUE Ananki will catch false positives)'''

    old_code_no_comment = '''        except:
            return True'''

    new_code = '''        except Exception as e:
            self.logger.warning(f"Failed to validate track '{track.get('name', 'unknown')}': {e}")
            return True  # Allow on validation failure - quality filter will catch bad comments'''

    # Try both patterns
    changed = False
    if old_code_with_comment in content:
        content = content.replace(old_code_with_comment, new_code)
        changed = True
    elif old_code_no_comment in content:
        content = content.replace(old_code_no_comment, new_code)
        changed = True

    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] Fixed is_valid_track() logging")
        return True
    else:
        print(f"  [SKIP] Pattern not found or already fixed")
        return False


def main():
    scrapers_dir = Path(__file__).parent / 'reddit' / 'smart_scrapers'

    # The 9 scrapers that need fixing
    scrapers_to_fix = [
        'scrape_bitter.py',
        'scrape_bored.py',
        'scrape_chaotic.py',
        'scrape_confident.py',
        'scrape_excited.py',
        'scrape_grateful.py',
        'scrape_hopeful.py',
        'scrape_jealous.py',
        'scrape_playful.py'
    ]

    print("="*70)
    print("FIXING 9 REMAINING SCRAPERS")
    print("="*70)

    fixed = 0
    for scraper_name in scrapers_to_fix:
        scraper_path = scrapers_dir / scraper_name
        if scraper_path.exists():
            if fix_is_valid_track_logging(scraper_path):
                fixed += 1
        else:
            print(f"[WARN] File not found: {scraper_name}")

    print(f"\n{'='*70}")
    print(f"COMPLETE: Fixed {fixed}/{len(scrapers_to_fix)} scrapers")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
