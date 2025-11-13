"""
Checkpointing utilities for Last.fm scrapers
Import and use checkpoint_manager to get automatic progress saves
"""

import json
import time
from pathlib import Path
from datetime import datetime

class CheckpointManager:
    def __init__(self, meta_vibe_name):
        self.meta_vibe_name = meta_vibe_name
        self.checkpoint_file = Path(__file__).parent.parent / 'test_results' / f'{meta_vibe_name.lower()}_checkpoint.json'
        self.start_time = time.time()
        self.last_status_time = time.time()
        
        # Load existing checkpoint if resuming
        self.all_results = []
        self.scraped_urls = set()
        
        if self.checkpoint_file.exists():
            print(f"[RESUME] Found checkpoint! Loading previous progress...")
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
                self.all_results = checkpoint.get('songs', [])
                self.scraped_urls = set(checkpoint.get('scraped_urls', []))
            print(f"[RESUME] Continuing from {len(self.all_results)} songs!")
    
    def save_checkpoint(self):
        """Save progress"""
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump({
                'meta_vibe': self.meta_vibe_name,
                'songs': self.all_results,
                'scraped_urls': list(self.scraped_urls),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def update_progress(self, new_songs):
        """Add songs and auto-checkpoint"""
        self.all_results.extend(new_songs)
        
        # Checkpoint every 100 songs
        if len(self.all_results) % 100 == 0:
            self.save_checkpoint()
            print(f"  [CHECKPOINT] {len(self.all_results)} songs saved")
        
        # Status every 60 seconds
        current_time = time.time()
        if (current_time - self.last_status_time) >= 60:
            elapsed = int(current_time - self.start_time)
            unique = len(set((s['artist'].lower(), s['song'].lower()) for s in self.all_results))
            print(f"  [STATUS] {elapsed//60}m{elapsed%60}s | {len(self.all_results)} total ({unique} unique) | {len(self.scraped_urls)} URLs")
            self.last_status_time = current_time
    
    def finalize(self, output_file, target_songs=None):
        """Save final and cleanup checkpoint"""
        # Deduplicate
        seen = set()
        unique = []
        for r in self.all_results:
            key = (r['artist'].lower(), r['song'].lower())
            if key not in seen:
                seen.add(key)
                unique.append(r)
        
        if target_songs and len(unique) > target_songs:
            unique = unique[:target_songs]
        
        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'meta_vibe': self.meta_vibe_name,
                'source': 'lastfm',
                'total': len(unique),
                'note': 'Ready for TRUE Ananki',
                'songs': unique
            }, f, indent=2, ensure_ascii=False)
        
        # Delete checkpoint
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        
        return unique
