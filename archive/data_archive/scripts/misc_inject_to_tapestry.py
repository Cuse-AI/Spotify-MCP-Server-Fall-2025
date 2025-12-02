"""
Inject Ananki-mapped songs directly into tapestry
"""

import json
from pathlib import Path
from datetime import datetime

def inject_to_tapestry(mapped_songs_file):
    print("\nINJECTING SONGS TO TAPESTRY")
    print("="*70)
    
    # Load tapestry
    tapestry_file = Path(__file__).parent.parent.parent / 'core' / 'tapestry.json'
    
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Build GLOBAL Spotify ID index for duplicate checking
    global_spotify_ids = set()
    for subvibe_name, subvibe_data in tapestry['vibes'].items():
        for song in subvibe_data.get('songs', []):
            if 'spotify_id' in song:
                global_spotify_ids.add(song['spotify_id'])
    
    print(f"Existing songs in tapestry: {len(global_spotify_ids)}")
    
    # Load mapped songs
    with open(mapped_songs_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both old and new format
    songs = data.get('mapped_songs', data.get('songs', []))
    print(f"Songs to inject: {len(songs)}")
    
    # Inject into correct sub-vibes
    stats = {
        'injected': 0,
        'skipped_duplicate': 0,
        'skipped_no_subvibe': 0,
        'by_subvibe': {}
    }
    
    for song in songs:
        # Try both old and new field names
        subvibe = song.get('ananki_subvibe') or song.get('mapped_subvibe')
        
        # Skip if no sub-vibe mapping
        if not subvibe or subvibe == 'NEEDS_REVIEW' or subvibe == 'AMBIGUOUS':
            stats['skipped_no_subvibe'] += 1
            continue
        
        # Check if sub-vibe exists
        if subvibe not in tapestry['vibes']:
            print(f"WARNING: Sub-vibe '{subvibe}' not in tapestry!")
            stats['skipped_no_subvibe'] += 1
            continue
        
        # GLOBAL duplicate check by Spotify ID (most reliable!)
        spotify_id = song.get('spotify_id')
        if spotify_id and spotify_id in global_spotify_ids:
            stats['skipped_duplicate'] += 1
            continue
        
        # Legacy duplicate check by name (for songs without spotify_id)
        existing_songs = tapestry['vibes'][subvibe].get('songs', [])
        key = (song['artist'].lower(), song['song'].lower())
        existing_keys = {(s.get('artist', '').lower(), s.get('song', '').lower()) for s in existing_songs}
        
        if key in existing_keys:
            stats['skipped_duplicate'] += 1
            continue
        
        # Add to tapestry!
        if 'songs' not in tapestry['vibes'][subvibe]:
            tapestry['vibes'][subvibe]['songs'] = []
        
        tapestry['vibes'][subvibe]['songs'].append({
            'artist': song['artist'],
            'song': song['song'],
            'spotify_id': song['spotify_id'],
            'spotify_uri': song['spotify_uri'],
            'comment_score': song.get('comment_score', 0),
            'source_url': song.get('source_url', ''),
            'data_source': song.get('data_source', 'reddit_smart_v2'),
            'extraction_confidence': song.get('extraction_confidence', 1.0),
            'mapping_confidence': song.get('ananki_confidence', song.get('mapping_confidence', 0)),
            # CRITICAL: Save ALL context for human-sourced proof!
            'full_context': song.get('full_context', ''),
            'post_title': song.get('post_title', ''),
            'comment_text': song.get('comment_text', ''),
            'ananki_reasoning': song.get('ananki_reasoning', song.get('ananki_analysis', '')),
            'mapped_subvibe': subvibe
        })
        
        stats['injected'] += 1
        if subvibe not in stats['by_subvibe']:
            stats['by_subvibe'][subvibe] = 0
        stats['by_subvibe'][subvibe] += 1
        
        # Add to global index to prevent duplicates in same injection run
        if spotify_id:
            global_spotify_ids.add(spotify_id)
    
    # Save updated tapestry
    with open(tapestry_file, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print("INJECTION COMPLETE")
    print(f"{'='*70}")
    print(f"Injected: {stats['injected']}")
    print(f"Skipped (duplicates): {stats['skipped_duplicate']}")
    print(f"Skipped (no mapping): {stats['skipped_no_subvibe']}")
    print(f"\nBy sub-vibe:")
    for subvibe, count in sorted(stats['by_subvibe'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {subvibe}: +{count} songs")
    
    print(f"\nTapestry updated: {tapestry_file}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        inject_to_tapestry(sys.argv[1])
    else:
        inject_to_tapestry('test_results/happy_smart_extraction_500_MAPPED.json')
