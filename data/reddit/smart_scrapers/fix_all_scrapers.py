import os
from pathlib import Path

scrapers_dir = Path(__file__).parent
files = [f for f in os.listdir(scrapers_dir) if f.startswith('scrape_') and f.endswith('.py')]

for filename in files:
    filepath = scrapers_dir / filename
    try:
        content = open(filepath, 'r', encoding='utf-8').read()
        
        # Fix the cp -> self issue
        content = content.replace('cp.scraped_urls = set()', 'self.scraped_urls = set()')
        
        # Fix ALL arrow issues (both in comments and print statements)
        content = content.replace('→', '->')
        
        open(filepath, 'w', encoding='utf-8').write(content)
        print(f'Fixed {filename}')
    except Exception as e:
        print(f'Error fixing {filename}: {e}')

print('Done! All scrapers fixed.')
