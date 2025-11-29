"""
Analyze Flagged Songs
Quick analysis tool to understand why songs were flagged
"""
import json
import sys
from collections import defaultdict


def analyze_flagged_songs(flagged_file):
    """Analyze patterns in flagged songs"""

    with open(flagged_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print('='*80)
    print('FLAGGED SONGS ANALYSIS')
    print('='*80)
    print(f'File: {flagged_file}')
    print(f'Total flagged: {data["total_flagged"]}')
    print()

    # Analyze confidence distribution
    confidence_ranges = {
        '0.0-0.2': 0,
        '0.2-0.4': 0,
        '0.4-0.6': 0,
    }

    patterns = defaultdict(int)
    swapped_count = 0

    for song in data['flagged_songs']:
        conf = song['confidence']

        # Confidence range
        if conf < 0.2:
            confidence_ranges['0.0-0.2'] += 1
        elif conf < 0.4:
            confidence_ranges['0.2-0.4'] += 1
        else:
            confidence_ranges['0.4-0.6'] += 1

        # Check for swap
        if 'swapped' in song.get('confidence_explanation', ''):
            swapped_count += 1

        # Pattern analysis
        original_artist = song.get('original_artist', '')
        original_song = song.get('original_song', '')

        if '\n' in original_artist or '\n' in original_song:
            patterns['has_newlines'] += 1
        if len(original_artist) < 3 or len(original_song) < 3:
            patterns['too_short'] += 1
        if any(sep in original_artist.lower() for sep in [' and ', ' & ', ' feat', ' ft.']):
            patterns['multiple_artists'] += 1
        if ' - ' in original_artist:
            patterns['dash_in_artist'] += 1

    print('[CONFIDENCE DISTRIBUTION]')
    for range_name, count in confidence_ranges.items():
        pct = count / data['total_flagged'] * 100
        print(f'  {range_name}: {count} ({pct:.1f}%)')

    print(f'\n[SWAP DETECTION]')
    print(f'  Swapped: {swapped_count} ({swapped_count/data["total_flagged"]*100:.1f}%)')

    print(f'\n[PARSING PATTERNS DETECTED]')
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
        pct = count / data['total_flagged'] * 100
        print(f'  {pattern}: {count} ({pct:.1f}%)')

    # Show examples of lowest confidence
    print(f'\n[LOWEST CONFIDENCE EXAMPLES]')
    sorted_songs = sorted(data['flagged_songs'], key=lambda x: x['confidence'])
    for song in sorted_songs[:5]:
        print(f'\n  Confidence: {song["confidence"]:.3f}')
        print(f'  Original: "{song["original_artist"]}" - "{song["original_song"]}"')
        print(f'  Matched:  "{song["clean_artist"]}" - "{song["clean_song"]}"')
        print(f'  Explanation: {song["confidence_explanation"]}')

    # Recommendations
    print(f'\n{"="*80}')
    print('[RECOMMENDATIONS]')
    print('='*80)

    if patterns['has_newlines'] > data['total_flagged'] * 0.1:
        print('[!] HIGH: Many songs have newlines - pre-processing should fix this')

    if patterns['multiple_artists'] > data['total_flagged'] * 0.1:
        print('[!] MEDIUM: Multiple artists detected - pre-processing should handle this')

    if swapped_count > data['total_flagged'] * 0.2:
        print('[!] HIGH: Many swaps detected - validation already handles this')

    if patterns['dash_in_artist'] > data['total_flagged'] * 0.05:
        print('[!] MEDIUM: Dashes in artist field - song leaked into artist field')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python analyze_flagged_songs.py <flagged_file.json>')
        print('Example: python analyze_flagged_songs.py spotify_batch_1_results_v2_NEEDS_AI_REVIEW.json')
        sys.exit(1)

    analyze_flagged_songs(sys.argv[1])
