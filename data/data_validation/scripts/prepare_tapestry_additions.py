"""
Add validated songs to the Tapestry

This script:
1. Combines high-confidence Spotify matches (808 songs)
2. Adds the KEEP songs from low-confidence analysis (58 songs)
3. Prepares them for tapestry integration

Total: 866 confirmed songs ready to add!
"""

import json
from pathlib import Path
from datetime import datetime

def load_batch_results(batch_num, result_type='good'):
    """Load results from a specific batch."""
    base_dir = Path(__file__).parent
    batch_file = base_dir.parent / 'batch_results' / f'spotify_batch_{batch_num}_results_v2.json'
    
    with open(batch_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if result_type == 'good':
        return data['good_matches']
    else:
        return data['questionable_matches']


def load_keep_songs():
    """Load the KEEP songs from low-confidence analysis."""
    base_dir = Path(__file__).parent
    analysis_file = base_dir.parent / 'low_confidence_analysis.json'
    
    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['results']['KEEP']


def prepare_for_tapestry(song_entry):
    """
    Convert a validated song entry to tapestry format.
    
    Tapestry format needs:
    - artist, song, vibe
    - spotify_id, spotify_uri (if available)
    - confidence score
    - source (where this data came from)
    """
    return {
        'artist': song_entry.get('clean_artist', song_entry.get('original_artist')),
        'song': song_entry.get('clean_song', song_entry.get('original_song')),
        'vibe': song_entry['vibe'],
        'spotify_id': song_entry.get('spotify_id'),
        'spotify_uri': song_entry.get('spotify_uri'),
        'confidence': song_entry['confidence'],
        'validation_source': 'spotify_api_v2',
        'original_artist': song_entry['original_artist'],
        'original_song': song_entry['original_song'],
        'matched': song_entry.get('matched', True)
    }


def main():
    """Collect all confirmed songs and prepare for tapestry."""
    
    print("\nCollecting validated songs...")
    print("=" * 60)
    
    all_confirmed = []
    
    # 1. Collect high-confidence matches from all batches
    print("\n1. High-confidence Spotify matches:")
    for batch_num in [1, 2, 3, 4, 5, 6, 7, 8]:
        good_matches = load_batch_results(batch_num, 'good')
        all_confirmed.extend(good_matches)
        print(f"   Batch {batch_num}: {len(good_matches)} songs")
    
    high_conf_count = len(all_confirmed)
    print(f"   TOTAL: {high_conf_count} high-confidence songs")
    
    # 2. Add KEEP songs from low-confidence analysis
    print("\n2. Rescued from low-confidence (KEEP category):")
    keep_songs = load_keep_songs()
    all_confirmed.extend(keep_songs)
    print(f"   KEEP: {len(keep_songs)} songs")
    
    print(f"\n   GRAND TOTAL: {len(all_confirmed)} confirmed songs")
    
    # 3. Convert to tapestry format
    print("\n3. Converting to tapestry format...")
    tapestry_ready = [prepare_for_tapestry(song) for song in all_confirmed]
    
    # 4. Save results
    base_dir = Path(__file__).parent
    output_file = base_dir.parent / 'confirmed_songs_for_tapestry.json'
    
    output_data = {
        'metadata': {
            'total_songs': len(tapestry_ready),
            'high_confidence_spotify': high_conf_count,
            'rescued_from_low_conf': len(keep_songs),
            'generated_at': datetime.now().isoformat(),
            'validation_batches': [1, 2, 3, 4, 5, 6, 7, 8],
            'source': 'reddit_v5_spotify_validated'
        },
        'songs': tapestry_ready
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # 5. Stats breakdown by vibe
    print("\n4. Breakdown by vibe:")
    vibe_counts = {}
    for song in tapestry_ready:
        vibe = song['vibe']
        vibe_counts[vibe] = vibe_counts.get(vibe, 0) + 1
    
    for vibe, count in sorted(vibe_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {vibe}: {count} songs")
    
    print("\n" + "=" * 60)
    print("PREPARATION COMPLETE")
    print("=" * 60)
    print(f"Total songs ready: {len(tapestry_ready)}")
    print(f"Saved to: {output_file}")
    print(f"\nNext step: Merge these into the tapestry!")
    
    return tapestry_ready


if __name__ == '__main__':
    confirmed_songs = main()
