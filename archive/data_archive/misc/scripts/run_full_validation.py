"""
Full Validation Pipeline Runner
Automates the complete workflow: preprocess -> validate -> add to tapestry
Processes all songs in batches of 500
"""
import json
import os
import time
from step0_preprocess_songs import preprocess_tapestry
from step1_spotify_validate_v2 import SpotifyValidatorV2


def run_full_pipeline(start_batch=1, num_batches=None):
    """
    Run the complete validation pipeline

    Args:
        start_batch: Which batch to start from (1-indexed)
        num_batches: How many batches to process (None = all remaining)
    """

    print('='*80)
    print('FULL VALIDATION PIPELINE')
    print('='*80)

    # Step 0: Preprocess (only needed once)
    preprocessed_file = '../../ananki_outputs/tapestry_PREPROCESSED.json'
    if not os.path.exists(preprocessed_file):
        print('\n[STEP 0] Pre-processing tapestry...')
        preprocess_tapestry(
            '../../ananki_outputs/tapestry_CLEANED_WITH_SPOTIFY.json',
            preprocessed_file
        )
    else:
        print(f'\n[STEP 0] Using existing preprocessed tapestry: {preprocessed_file}')

    # Load preprocessed tapestry
    with open(preprocessed_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)

    # Collect all songs
    all_songs = []
    for vibe_name, vibe_data in tapestry['vibes'].items():
        for song in vibe_data['songs']:
            all_songs.append({
                'artist': song.get('artist', ''),
                'song': song.get('song', ''),
                'vibe': vibe_name
            })

    total_songs = len(all_songs)
    batch_size = 500
    total_batches = (total_songs + batch_size - 1) // batch_size

    print(f'\nTotal songs: {total_songs}')
    print(f'Total batches: {total_batches}')
    print(f'Starting from batch: {start_batch}')

    if num_batches:
        end_batch = min(start_batch + num_batches - 1, total_batches)
    else:
        end_batch = total_batches

    print(f'Processing batches: {start_batch} to {end_batch}')

    # Initialize validator
    validator = SpotifyValidatorV2()

    # Process each batch
    cumulative_stats = {
        'total_processed': 0,
        'total_good': 0,
        'total_questionable': 0,
        'total_unmatched': 0,
        'batches_completed': 0
    }

    for batch_num in range(start_batch, end_batch + 1):
        print(f'\n{"="*80}')
        print(f'BATCH {batch_num}/{total_batches}')
        print(f'{"="*80}')

        # Get batch songs
        start_idx = (batch_num - 1) * batch_size
        end_idx = min(start_idx + batch_size, total_songs)
        batch_songs = all_songs[start_idx:end_idx]

        print(f'Processing songs {start_idx+1} to {end_idx}...')

        # Step 1: Validate with Spotify
        print(f'\n[STEP 1] Validating {len(batch_songs)} songs...')
        matched_good, matched_questionable, unmatched = validator.validate_batch(
            batch_songs, batch_num, total_batches, min_confidence=0.6
        )

        # Save validation results
        results_file = f'../batch_results/spotify_batch_{batch_num}_results_v2.json'
        results = {
            'batch_num': batch_num,
            'total_processed': len(batch_songs),
            'matched_good': len(matched_good),
            'matched_questionable': len(matched_questionable),
            'unmatched': len(unmatched),
            'match_rate_good': f'{(len(matched_good)/len(batch_songs)*100):.1f}%',
            'match_rate_questionable': f'{(len(matched_questionable)/len(batch_songs)*100):.1f}%',
            'good_matches': matched_good,
            'questionable_matches': matched_questionable,
            'unmatched_songs': unmatched
        }

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f'[OK] Saved: {results_file}')

        # Step 2: Merge to tapestry (done separately with merge_to_tapestry.py)
        # print(f'\n[STEP 2] Adding high-confidence songs to tapestry...')
        # We'll merge all batches at once after validation completes

        # Update cumulative stats
        cumulative_stats['total_processed'] += len(batch_songs)
        cumulative_stats['total_good'] += len(matched_good)
        cumulative_stats['total_questionable'] += len(matched_questionable)
        cumulative_stats['total_unmatched'] += len(unmatched)
        cumulative_stats['batches_completed'] += 1

        print(f'\n[BATCH {batch_num} SUMMARY]')
        print(f'  High Confidence: {len(matched_good)} ({len(matched_good)/len(batch_songs)*100:.1f}%)')
        print(f'  Low Confidence: {len(matched_questionable)} ({len(matched_questionable)/len(batch_songs)*100:.1f}%)')
        print(f'  Unmatched: {len(unmatched)} ({len(unmatched)/len(batch_songs)*100:.1f}%)')

        # Pause between batches (except last one)
        if batch_num < end_batch:
            print(f'\n[Pausing 10 seconds before next batch...]')
            time.sleep(10)

    # Final summary
    print(f'\n{"="*80}')
    print('PIPELINE COMPLETE')
    print(f'{"="*80}')
    print(f'Total Batches: {cumulative_stats["batches_completed"]}')
    print(f'Total Songs Processed: {cumulative_stats["total_processed"]}')
    print(f'High Confidence: {cumulative_stats["total_good"]} ({cumulative_stats["total_good"]/cumulative_stats["total_processed"]*100:.1f}%)')
    print(f'Low Confidence: {cumulative_stats["total_questionable"]} ({cumulative_stats["total_questionable"]/cumulative_stats["total_processed"]*100:.1f}%)')
    print(f'Unmatched: {cumulative_stats["total_unmatched"]} ({cumulative_stats["total_unmatched"]/cumulative_stats["total_processed"]*100:.1f}%)')
    print(f'\nAPI Requests Made: {validator.request_count}')
    print(f'\n[NEXT STEP] AI should review flagged songs for quality check')

    return cumulative_stats


if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    start_batch = 1
    num_batches = 3
    
    for i, arg in enumerate(sys.argv):
        if arg == '--start-batch' and i + 1 < len(sys.argv):
            start_batch = int(sys.argv[i + 1])
        elif arg == '--num-batches' and i + 1 < len(sys.argv):
            num_batches = int(sys.argv[i + 1])
    
    print(f"\nStarting validation from batch {start_batch}, processing {num_batches} batches\n")
    stats = run_full_pipeline(start_batch=start_batch, num_batches=num_batches)
