"""
Quick script to add checkpointing to all scrapers
"""

import re
from pathlib import Path

scrapers = [
    'scrape_angry.py', 'scrape_anxious.py', 'scrape_chill.py', 'scrape_dark.py',
    'scrape_drive.py', 'scrape_energy.py', 'scrape_happy.py', 'scrape_introspective.py',
    'scrape_night.py', 'scrape_nostalgic.py', 'scrape_party.py', 'scrape_peaceful.py',
    'scrape_romantic.py', 'scrape_sad.py'
]

for scraper_file in scrapers:
    filepath = Path(scraper_file)
    
    if not filepath.exists():
        print(f"Skip: {scraper_file} (not found)")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add import at top if not present
    if 'from checkpoint_utils import CheckpointManager' not in content:
        # Find the last import
        import_section = content.split('\n\n')[0]
        content = content.replace(import_section, import_section + '\nfrom checkpoint_utils import CheckpointManager')
    
    # Find the scraping function and add checkpoint usage
    # This is complex - let me just print what needs to be done
    print(f"Update needed for: {scraper_file}")

print("\nManual updates needed:")
print("1. Add: from checkpoint_utils import CheckpointManager")
print("2. In __init__ or main: cp = CheckpointManager('MetaVibe')")
print("3. Replace: all_results = [] with: all_results = cp.all_results")
print("4. Replace: scraped_urls = set() with: scraped_urls = cp.scraped_urls")
print("5. After adding songs: cp.update_progress(new_songs)")
print("6. At end: cp.finalize(output_file, target_songs)")
