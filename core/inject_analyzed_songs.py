#!/usr/bin/env python3
"""
Inject analyzed songs from data/3_analyzed/mapped/ into core/tapestry.json
"""

import json
import os
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def sync_to_vercel(tapestry_path: Path):
    """Copy tapestry to Vercel deployment locations"""
    import shutil
    
    project_root = tapestry_path.parent.parent  # core/ -> project root
    
    vercel_locations = [
        project_root / "code" / "web" / "core" / "tapestry.json",
        project_root / "code" / "web" / "client" / "public" / "core" / "tapestry.json",
    ]
    
    print(f"\n[*] Syncing to Vercel deployment locations...")
    
    for dest in vercel_locations:
        if dest.parent.exists():
            try:
                shutil.copy2(tapestry_path, dest)
                print(f"    ✅ Synced to: {dest.relative_to(project_root)}")
            except Exception as e:
                print(f"    ❌ Failed to sync to {dest.name}: {e}")
        else:
            print(f"    ⚠️  Skipped (dir not found): {dest.relative_to(project_root)}")
    
    print(f"[OK] Vercel sync complete!")


def inject_analyzed_songs():
    """Load tapestry, inject all mapped songs, save atomically"""
    
    # Paths
    project_root = Path(__file__).parent
    tapestry_path = project_root / "tapestry.json"
    analyzed_dir = project_root.parent / "data" / "3_analyzed" / "mapped"
    
    print(f"[*] Loading tapestry from: {tapestry_path}")
    
    # Load current tapestry
    with open(tapestry_path, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    initial_count = sum(len(v.get('songs', [])) for v in tapestry['vibes'].values())
    print(f"[*] Starting count: {initial_count} songs")
    
    # Find all analyzed files
    analyzed_files = sorted(analyzed_dir.glob("*CLAUDE_MAPPED.json"))
    print(f"[*] Found {len(analyzed_files)} analyzed files to inject")
    
    total_added = 0
    files_processed = 0
    
    for analyzed_file in analyzed_files:
        print(f"\n  Processing: {analyzed_file.name}")
        
        with open(analyzed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mapped_count = data.get('mapped', 0)
        ambiguous_count = data.get('ambiguous', 0)
        
        print(f"    - Mapped: {mapped_count}, Ambiguous: {ambiguous_count}")
        
        # Process mapped songs
        if data.get('mapped_songs'):
            for song in data['mapped_songs']:
                sub_vibe = song.get('ananki_subvibe')
                
                if not sub_vibe:
                    print(f"    WARNING: Skipping song (no sub_vibe): {song.get('artist')} - {song.get('song')}")
                    continue
                
                # Create sub_vibe category if it doesn't exist
                if sub_vibe not in tapestry['vibes']:
                    tapestry['vibes'][sub_vibe] = {'songs': []}
                
                # Transform song to tapestry format
                tapestry_song = {
                    'artist': song.get('artist'),
                    'song': song.get('song'),
                    'spotify_id': song.get('spotify_id'),
                    'spotify_uri': song.get('spotify_uri'),
                    'comment_score': song.get('comment_score', 0),
                    'source_url': song.get('source_url', ''),
                    'data_source': 'analyzed_batch_nov27',
                    'extraction_confidence': song.get('extraction_confidence', 1),
                    'mapping_confidence': song.get('ananki_confidence', 0.9),
                    'full_context': '',
                    'post_title': song.get('post_title', ''),
                    'comment_text': song.get('comment_text', ''),
                    'ananki_reasoning': song.get('ananki_reasoning', ''),
                    'mapped_subvibe': sub_vibe,
                }
                
                # Check if song already exists (avoid duplicates)
                existing = any(
                    s['spotify_id'] == tapestry_song['spotify_id'] 
                    for s in tapestry['vibes'][sub_vibe]['songs']
                )
                
                if not existing:
                    tapestry['vibes'][sub_vibe]['songs'].append(tapestry_song)
                    total_added += 1
        
        files_processed += 1
    
    # Final count
    final_count = sum(len(v.get('songs', [])) for v in tapestry['vibes'].values())
    
    print(f"\n{'='*60}")
    print(f"[SUCCESS] INJECTION SUMMARY")
    print(f"{'='*60}")
    print(f"Files processed: {files_processed}/16")
    print(f"Songs added: {total_added}")
    print(f"Initial count: {initial_count}")
    print(f"Final count:   {final_count}")
    print(f"Increase: +{final_count - initial_count}")
    
    # Save atomically (write to temp, then rename)
    temp_path = str(tapestry_path) + '.tmp'
    
    try:
        print(f"\n[*] Saving to: {temp_path}")
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(tapestry, f, indent=2, ensure_ascii=False)
        
        # Verify it's valid JSON by reading it back
        with open(temp_path, 'r', encoding='utf-8') as f:
            json.load(f)
        
        print("[OK] Temp file verified as valid JSON")
        
        # Atomic rename
        import shutil
        shutil.move(temp_path, str(tapestry_path))
        print(f"[OK] Atomically replaced {tapestry_path.name}")
        
        # Auto-sync to Vercel deployment locations
        sync_to_vercel(tapestry_path)
        
        print(f"\n[COMPLETE] Your tapestry now has {final_count} songs!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

if __name__ == '__main__':
    success = inject_analyzed_songs()
    exit(0 if success else 1)
