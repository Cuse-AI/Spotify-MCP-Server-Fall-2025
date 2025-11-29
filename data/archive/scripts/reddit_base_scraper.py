"""
BASE SMART SCRAPER WITH CHECKPOINTING
All meta-vibe scrapers inherit from this to get:
- Progress saves every 100 songs
- Status updates every minute
- Resume capability if interrupted
"""

import json
import time
from pathlib import Path
from datetime import datetime

class SmartScraperBase:
    def __init__(self, meta_vibe_name):
        self.meta_vibe_name = meta_vibe_name
        self.checkpoint_interval = 100  # Save every 100 songs
        self.status_interval = 60  # Print update every 60 seconds
        self.last_status_time = time.time()
        self.start_time = time.time()
        
        # Checkpoint file
        self.checkpoint_file = Path(__file__).parent.parent / 'test_results' / f'{meta_vibe_name.lower()}_checkpoint.json'
        
        # Load existing checkpoint if resuming
        self.all_results = []
        self.scraped_urls = set()
        
        if self.checkpoint_file.exists():
            print(f"Found checkpoint! Loading previous progress...")
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
                self.all_results = checkpoint.get('songs', [])
                self.scraped_urls = set(checkpoint.get('scraped_urls', []))
            print(f"Resumed with {len(self.all_results)} songs already scraped!")
    
    def save_checkpoint(self):
        """Save current progress"""
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump({
                'meta_vibe': self.meta_vibe_name,
                'songs': self.all_results,
                'scraped_urls': list(self.scraped_urls),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def print_status(self, force=False):
        """Print status update"""
        current_time = time.time()
        
        if force or (current_time - self.last_status_time) >= self.status_interval:
            elapsed = int(current_time - self.start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            
            # Deduplicate count
            unique_count = len(set((s['artist'].lower(), s['song'].lower()) for s in self.all_results))
            
            print(f"\n[STATUS UPDATE - {mins}m {secs}s elapsed]")
            print(f"  Songs collected: {len(self.all_results)} ({unique_count} unique)")
            print(f"  URLs scraped: {len(self.scraped_urls)}")
            print(f"  Rate: {len(self.all_results)/(elapsed/60):.1f} songs/min")
            
            self.last_status_time = current_time
    
    def add_songs(self, new_songs):
        """Add songs and checkpoint if needed"""
        self.all_results.extend(new_songs)
        
        # Checkpoint every 100 songs
        if len(self.all_results) % self.checkpoint_interval == 0:
            self.save_checkpoint()
            print(f"  [CHECKPOINT] Saved progress: {len(self.all_results)} songs")
        
        # Print status update
        self.print_status()
    
    def finalize(self, output_file, target_songs=None):
        """Deduplicate, trim to target, and save final output"""
        # Deduplicate
        seen = set()
        unique = []
        for r in self.all_results:
            key = (r['artist'].lower(), r['song'].lower())
            if key not in seen:
                seen.add(key)
                unique.append(r)
        
        # Trim to target if specified
        if target_songs and len(unique) > target_songs:
            unique = unique[:target_songs]
        
        # Save final output
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'meta_vibe': self.meta_vibe_name,
                'total': len(unique),
                'note': 'Pre-validated - ready for TRUE Ananki analysis',
                'songs': unique
            }, f, indent=2, ensure_ascii=False)
        
        # Delete checkpoint
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        
        return unique
