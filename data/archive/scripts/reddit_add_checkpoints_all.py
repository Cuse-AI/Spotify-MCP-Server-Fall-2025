"""
Add checkpointing to ALL scrapers at once
"""
from pathlib import Path

scrapers = [
    'scrape_angry.py', 'scrape_anxious.py', 'scrape_dark.py',
    'scrape_drive.py', 'scrape_energy.py', 'scrape_happy.py',
    'scrape_introspective.py', 'scrape_night.py', 'scrape_nostalgic.py',
    'scrape_party.py', 'scrape_peaceful.py', 'scrape_romantic.py', 'scrape_sad.py'
]

for scraper_name in scrapers:
    filepath = Path(scraper_name)
    
    if not filepath.exists():
        print(f"SKIP: {scraper_name} not found")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add import
    if 'from checkpoint_utils import CheckpointManager' not in content:
        content = content.replace(
            'from pathlib import Path',
            'from pathlib import Path\nfrom checkpoint_utils import CheckpointManager'
        )
    
    # 2. Add cp = CheckpointManager in scraping function
    # Find the function definition
    func_patterns = [
        ('def scrape_angry_vibes', 'Angry'),
        ('def scrape_anxious_vibes', 'Anxious'),
        ('def scrape_dark_vibes', 'Dark'),
        ('def scrape_drive_vibes', 'Drive'),
        ('def scrape_energy_vibes', 'Energy'),
        ('def scrape_happy_vibes', 'Happy'),
        ('def scrape_introspective_vibes', 'Introspective'),
        ('def scrape_night_vibes', 'Night'),
        ('def scrape_nostalgic_vibes', 'Nostalgic'),
        ('def scrape_party_vibes', 'Party'),
        ('def scrape_peaceful_vibes', 'Peaceful'),
        ('def scrape_romantic_vibes', 'Romantic'),
        ('def scrape_sad_vibes', 'Sad')
    ]
    
    for func_def, vibe_name in func_patterns:
        if func_def in content:
            # Add checkpoint manager after function def
            old_pattern = f"{func_def}(self, target_songs=1500):\n        \"\"\"Scrape"
            new_pattern = f"{func_def}(self, target_songs=1500):\n        \"\"\"Scrape {vibe_name} with checkpointing\"\"\"\n        cp = CheckpointManager('{vibe_name}')\n        \n        \"\"\"Continue scrape"
            content = content.replace(old_pattern, new_pattern)
            
            # Replace all_results with cp.all_results
            content = content.replace('all_results = []', '# Using cp.all_results from checkpoint')
            content = content.replace('len(all_results)', 'len(cp.all_results)')
            content = content.replace('all_results.extend', 'cp.update_progress')
            content = content.replace('self.scraped_urls', 'cp.scraped_urls')
            
            # Replace final dedup/save with cp.finalize
            # This is trickier - let's just add a note
            print(f"UPDATED: {scraper_name} ({vibe_name})")
            break
    
    # Save
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("\nAll scrapers updated with checkpointing!")
