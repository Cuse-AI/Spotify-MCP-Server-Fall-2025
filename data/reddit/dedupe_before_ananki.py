"""
Pre-Ananki Deduplication Script
Removes songs that already exist in tapestry BEFORE costly Ananki analysis
CRITICAL: Run this BEFORE true_ananki_claude_api.py to save API costs!
"""

import json
from pathlib import Path
import sys

def dedupe_before_ananki(scraped_file, output_file=None):
    """
    Remove songs that already exist in tapestry by Spotify ID
    Returns only NEW songs that need Ananki analysis
    """
    
    print("\n" + "="*70)
    print("PRE-ANANKI DEDUPLICATION")
    print("="*70)
    
    # Load tapestry
    tapestry_file = Path(__file__).parent.parent.parent / 'core' / 'tapestry.json'
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Build global Spotify ID index
    existing_ids = set()
    for subvibe_data in tapestry['vibes'].values():
        for song in subvibe_data.get('songs', []):
            if 'spotify_id' in song:
                existing_ids.add(song['spotify_id'])
    
    print(f"Existing songs in tapestry: {len(existing_ids)}")
    
    # Load scraped songs
    with open(scraped_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    songs = data.get('mapped_songs', data.get('songs', []))
    print(f"Scraped songs to check: {len(songs)}")
    
    # Filter out duplicates
    new_songs = []
    duplicates = 0
    
    for song in songs:
        spotify_id = song.get('spotify_id')
        if spotify_id and spotify_id in existing_ids:
            duplicates += 1
        else:
            new_songs.append(song)
            if spotify_id:
                existing_ids.add(spotify_id)  # Track within this file too
    
    print(f"\nResults:")
    print(f"  New songs (need Ananki): {len(new_songs)}")
    print(f"  Duplicates (skipped): {duplicates}")
    print(f"  Savings: ${duplicates * 0.003:.2f} (avoided analyzing {duplicates} duplicates!)")
    
    # Save deduplicated file
    if output_file is None:
        output_file = Path(scraped_file).parent / f"{Path(scraped_file).stem}_DEDUPED.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'meta_vibe': data.get('meta_vibe', 'unknown'),
            'source': data.get('source', 'unknown'),
            'total': len(new_songs),
            'note': 'Deduplicated - ready for Ananki',
            'songs': new_songs
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_file}")
    print(f"\nNext: python true_ananki_claude_api.py {output_file.name}")
    print("="*70)
    
    return new_songs, duplicates


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python dedupe_before_ananki.py <scraped_file.json>")
        print("\nExample:")
        print("  python dedupe_before_ananki.py ../youtube/test_results/sad_youtube_extraction.json")
        sys.exit(1)
    
    scraped_file = sys.argv[1]
    dedupe_before_ananki(scraped_file)
