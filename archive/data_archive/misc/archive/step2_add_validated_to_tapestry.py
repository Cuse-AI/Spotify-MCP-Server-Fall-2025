"""
STEP 2: Add Validated Songs to Tapestry
Takes high-confidence Spotify matches and adds them to the tapestry with IDs
Saves questionable matches for manual AI review
"""
import json
from collections import defaultdict

def add_validated_songs_to_tapestry(validation_results_file, tapestry_file, min_confidence=0.6):
    """
    Add high-confidence validated songs to tapestry
    Returns: (added_count, questionable_count, analysis_needed)
    """

    # Load validation results
    with open(validation_results_file, 'r', encoding='utf-8') as f:
        validation = json.load(f)

    # Load tapestry
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)

    print(f'Loading validation results from: {validation_results_file}')
    print(f'High confidence matches: {validation["matched_good"]}')
    print(f'Questionable matches: {validation["matched_questionable"]}')
    print(f'Unmatched: {validation["unmatched"]}')

    # Group validated songs by vibe
    songs_by_vibe = defaultdict(list)
    for match in validation['good_matches']:
        songs_by_vibe[match['vibe']].append({
            'song': match['clean_song'],
            'artist': match['clean_artist'],
            'spotify_id': match['spotify_id'],
            'spotify_uri': match['spotify_uri'],
            'confidence': match['confidence'],
            'original_song': match['original_song'],
            'original_artist': match['original_artist'],
            'validated': True
        })

    # Add to tapestry
    added_count = 0
    for vibe_name, validated_songs in songs_by_vibe.items():
        if vibe_name in tapestry['vibes']:
            # Check for duplicates (by Spotify ID)
            existing_ids = set()
            for song in tapestry['vibes'][vibe_name]['songs']:
                if 'spotify_id' in song:
                    existing_ids.add(song['spotify_id'])

            # Add non-duplicate validated songs
            for vsong in validated_songs:
                if vsong['spotify_id'] not in existing_ids:
                    tapestry['vibes'][vibe_name]['songs'].append(vsong)
                    added_count += 1

    # Update stats
    total_songs = sum(len(v['songs']) for v in tapestry['vibes'].values())
    all_artists = set()
    for vibe_data in tapestry['vibes'].values():
        for song in vibe_data['songs']:
            all_artists.add(song.get('artist', ''))

    tapestry['stats']['total_songs'] = total_songs
    tapestry['stats']['total_artists'] = len(all_artists)
    tapestry['stats']['validated_songs'] = sum(
        1 for v in tapestry['vibes'].values()
        for s in v['songs']
        if s.get('validated', False)
    )

    # Save updated tapestry
    output_file = tapestry_file.replace('.json', '_WITH_SPOTIFY.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)

    print(f'\n[OK] Added {added_count} high-confidence songs to tapestry')
    print(f'[SAVED] {output_file}')

    # Prepare questionable matches for AI review
    questionable_file = validation_results_file.replace('.json', '_NEEDS_AI_REVIEW.json')
    ai_review_data = {
        'total_flagged': len(validation['questionable_matches']),
        'flagged_songs': validation['questionable_matches'],
        'instructions': 'These songs need AI analysis to determine if they are correct matches',
        'analysis_tasks': [
            'Check if the match is actually correct (artist/song swapped?)',
            'Determine if the low confidence is due to parsing errors',
            'Identify which ones can be rescued with better parsing',
            'Flag truly bad matches for rejection'
        ]
    }

    with open(questionable_file, 'w', encoding='utf-8') as f:
        json.dump(ai_review_data, f, indent=2, ensure_ascii=False)

    print(f'[FLAGGED] Saved {len(validation["questionable_matches"])} questionable matches for AI review')
    print(f'[REVIEW FILE] {questionable_file}')

    return added_count, len(validation['questionable_matches']), questionable_file

def main():
    validation_file = 'spotify_batch_1_results_v2.json'
    tapestry_file = '../ananki_outputs/tapestry_PREPROCESSED.json'

    print('='*80)
    print('STEP 2: ADDING VALIDATED SONGS TO TAPESTRY')
    print('='*80)

    added, questionable, review_file = add_validated_songs_to_tapestry(
        validation_file,
        tapestry_file,
        min_confidence=0.6
    )

    print(f'\n[COMPLETE]')
    print(f'   Added: {added} songs')
    print(f'   Needs AI Review: {questionable} songs')
    print(f'\nNext: AI agent should analyze: {review_file}')

if __name__ == '__main__':
    main()
