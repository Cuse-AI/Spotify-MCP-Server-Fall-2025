"""
Batch Pre-Ananki Deduplication
Dedupes multiple files at once, checking against BOTH tapestry AND each other
Prevents wasting API credits on songs that appear in multiple scrapes
"""

import json
from pathlib import Path
import sys

def batch_dedupe(file_list):
    """
    Dedupe multiple files at once, checking against tapestry AND against each other
    """
    
    print("\n" + "="*70)
    print("BATCH PRE-ANANKI DEDUPLICATION")
    print("="*70)
    
    # Load tapestry
    tapestry_file = Path(__file__).parent.parent.parent / 'core' / 'tapestry.json'
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Build global Spotify ID index from tapestry
    existing_ids = set()
    for subvibe_data in tapestry['vibes'].values():
        for song in subvibe_data.get('songs', []):
            if 'spotify_id' in song:
                existing_ids.add(song['spotify_id'])
    
    print(f"Existing songs in tapestry: {len(existing_ids):,}")
    print(f"Files to process: {len(file_list)}\n")
    
    # Track IDs across all files being processed
    cross_file_ids = set()
    
    total_new = 0
    total_dup_tapestry = 0
    total_dup_crossfile = 0
    
    for scraped_file in file_list:
        scraped_path = Path(scraped_file)
        
        # Load scraped songs
        with open(scraped_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        songs = data.get('songs', [])
        
        # Filter out duplicates
        new_songs = []
        dup_tapestry = 0
        dup_crossfile = 0
        
        for song in songs:
            spotify_id = song.get('spotify_id')
            
            if not spotify_id:
                continue
            
            # Check against tapestry
            if spotify_id in existing_ids:
                dup_tapestry += 1
                continue
            
            # Check against other files being processed
            if spotify_id in cross_file_ids:
                dup_crossfile += 1
                continue
            
            # It's new! Add it
            new_songs.append(song)
            cross_file_ids.add(spotify_id)
        
        # Save deduped file
        output_file = scraped_path.parent / f"{scraped_path.stem}_DEDUPED.json"
        
        output_data = {
            'meta_vibe': data.get('meta_vibe', 'Unknown'),
            'songs': new_songs,
            'deduplication_stats': {
                'original_count': len(songs),
                'new_count': len(new_songs),
                'duplicates_in_tapestry': dup_tapestry,
                'duplicates_in_batch': dup_crossfile
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Stats
        savings_tapestry = dup_tapestry * 0.003
        savings_crossfile = dup_crossfile * 0.003
        
        print(f"{scraped_path.name}:")
        print(f"  New songs: {len(new_songs)}")
        print(f"  Duplicates (in tapestry): {dup_tapestry} (saved ${savings_tapestry:.2f})")
        print(f"  Duplicates (cross-file): {dup_crossfile} (saved ${savings_crossfile:.2f})")
        print(f"  Saved to: {output_file.name}\n")
        
        total_new += len(new_songs)
        total_dup_tapestry += dup_tapestry
        total_dup_crossfile += dup_crossfile
    
    # Summary
    total_savings = (total_dup_tapestry + total_dup_crossfile) * 0.003
    
    print("="*70)
    print(f"BATCH SUMMARY:")
    print(f"  Total new songs: {total_new}")
    print(f"  Duplicates in tapestry: {total_dup_tapestry}")
    print(f"  Duplicates across files: {total_dup_crossfile}")
    print(f"  Total API savings: ${total_savings:.2f}")
    print("="*70)
    
    print(f"\nNext: Run TRUE Ananki on each *_DEDUPED.json file")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Multiple files passed as arguments
        batch_dedupe(sys.argv[1:])
    else:
        print("Usage: python batch_dedupe_before_ananki.py file1.json file2.json file3.json ...")
        print("\nExample:")
        print("python batch_dedupe_before_ananki.py test_results/party.json test_results/drive.json")
