"""
Fix all Reddit scrapers to mark posts as processed
"""
import re
from pathlib import Path

def fix_scraper(file_path):
    """Add mark_post_processed call if missing"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already has mark_post_processed
    if 'mark_post_processed' in content:
        print(f"  {file_path.name} - already has mark_post_processed")
        return False

    # Pattern: Find "time.sleep(1)" that comes after the comment loop
    # This is at the end of the post processing, before the exception handler
    pattern = r'(\s+cp\.update_progress\(songs\)\s*\n\s+)(time\.sleep\(1\))'

    replacement = r'\1# Mark post as processed\n\1cp.mark_post_processed(post_id)\n\1\2'

    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  {file_path.name} - FIXED")
        return True
    else:
        print(f"  {file_path.name} - NO MATCH (manual fix needed)")
        return False

if __name__ == '__main__':
    scrapers_dir = Path(__file__).parent

    # All Reddit scrapers to fix
    vibes = [
        'chill', 'drive', 'happy', 'night', 'party', 'romantic', 'sad'
    ]

    print("\nFixing Reddit scrapers to mark posts as processed...")
    print("="*70)

    for vibe in vibes:
        scraper_file = scrapers_dir / f'scrape_{vibe}.py'
        if scraper_file.exists():
            fix_scraper(scraper_file)

    print("\nDone!")
