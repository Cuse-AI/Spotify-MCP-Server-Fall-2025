"""
Analyze low-confidence Spotify matches to determine:
1. Which are actually GOOD matches (keep)
2. Which are complete mismatches (discard)
3. Which should be checked on YouTube (potential rescue)

Human-in-the-loop analysis by Claude (Ananki) to review patterns.
"""

import json
from pathlib import Path

def analyze_match(entry):
    """
    Analyze a low-confidence match and categorize it.
    
    Returns: ('KEEP', 'DISCARD', 'CHECK_YOUTUBE', reason)
    """
    original_artist = entry['original_artist']
    original_song = entry['original_song']
    clean_artist = entry['clean_artist']
    clean_song = entry['clean_song']
    confidence = entry['confidence']
    
    # Pattern 1: Garbled extraction (multiple words mashed together)
    if any([
        len(original_artist.split()) > 3 and ' ' not in original_artist,
        'adjacent' in original_artist.lower(),
        'named' in original_artist.lower() and 'desire' in original_artist.lower(),
    ]):
        return ('DISCARD', f'Garbled extraction - multiple concepts mashed: "{original_artist}"')
    
    # Pattern 2: Very low confidence AND completely different artists
    if confidence < 0.35:
        artist_overlap = set(original_artist.lower().split()) & set(clean_artist.lower().split())
        if not artist_overlap:
            return ('DISCARD', f'No artist overlap + very low conf ({confidence:.2f})')
    
    # Pattern 3: Generic single words that got terrible matches
    if len(original_artist) <= 5 and len(original_song) <= 10 and confidence < 0.5:
        return ('DISCARD', f'Too generic - "{original_artist}" / "{original_song}" with low conf')
    
    # Pattern 4: Swapped artist/song with decent partial match
    if '(swapped)' in entry.get('confidence_explanation', ''):
        # Check if there's meaningful overlap
        all_original = (original_artist + ' ' + original_song).lower()
        all_clean = (clean_artist + ' ' + clean_song).lower()
        
        original_words = set(all_original.split())
        clean_words = set(all_clean.split())
        overlap = original_words & clean_words
        
        if len(overlap) >= 2 and confidence > 0.6:
            return ('KEEP', f'Swapped but good overlap: {overlap}')
        elif confidence < 0.5:
            return ('DISCARD', 'Swapped with poor match')
    
    # Pattern 5: Obscure artist names that might be real
    if confidence < 0.5 and len(original_artist) > 8:
        # Could be real obscure band
        return ('CHECK_YOUTUBE', f'Potential obscure artist: "{original_artist}" - "{original_song}"')
    
    # Pattern 6: Partial artist name match (e.g., "Bareilles" -> "Sara Bareilles")
    if original_artist.lower() in clean_artist.lower() or clean_artist.lower() in original_artist.lower():
        if confidence > 0.55:
            return ('KEEP', f'Partial artist match with decent conf')
    
    # Default: if confidence is borderline, flag for YouTube check
    if 0.45 <= confidence < 0.6:
        return ('CHECK_YOUTUBE', 'Borderline confidence - worth YouTube verification')
    
    # Very low confidence - likely bad
    if confidence < 0.45:
        return ('DISCARD', f'Low confidence ({confidence:.2f}) without clear reason to keep')
    
    # Medium-high confidence - probably okay
    if confidence >= 0.6:
        return ('KEEP', f'Confidence {confidence:.2f} is acceptable')
    
    return ('CHECK_YOUTUBE', 'Uncertain - needs manual review')


def main():
    base_dir = Path(__file__).parent
    
    results = {
        'KEEP': [],
        'DISCARD': [],
        'CHECK_YOUTUBE': []
    }
    
    stats = {
        'total_reviewed': 0,
        'KEEP': 0,
        'DISCARD': 0,
        'CHECK_YOUTUBE': 0
    }
    
    # Process all batches
    for batch_num in [1, 2, 3, 4, 5, 6, 7, 8]:
        review_file = base_dir.parent / 'batch_results' / f'spotify_batch_{batch_num}_results_v2_NEEDS_AI_REVIEW.json'
        
        if not review_file.exists():
            print(f"WARNING: Batch {batch_num} review file not found")
            continue
        
        with open(review_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\nProcessing Batch {batch_num}: {data['total_flagged']} low-confidence matches...")
        
        for entry in data['flagged_songs']:
            stats['total_reviewed'] += 1
            decision, reason = analyze_match(entry)
            
            stats[decision] += 1
            results[decision].append({
                'batch': batch_num,
                **entry,
                'analysis_reason': reason
            })
    
    # Save results
    output_file = base_dir.parent / 'low_confidence_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'stats': stats,
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("LOW CONFIDENCE ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total reviewed: {stats['total_reviewed']}")
    print(f"KEEP: {stats['KEEP']} ({stats['KEEP']/stats['total_reviewed']*100:.1f}%)")
    print(f"DISCARD: {stats['DISCARD']} ({stats['DISCARD']/stats['total_reviewed']*100:.1f}%)")
    print(f"CHECK_YOUTUBE: {stats['CHECK_YOUTUBE']} ({stats['CHECK_YOUTUBE']/stats['total_reviewed']*100:.1f}%)")
    print(f"\nSaved to: {output_file}")
    
    # Show sample decisions
    print("\nSAMPLE DECISIONS:")
    for decision_type in ['KEEP', 'DISCARD', 'CHECK_YOUTUBE']:
        if results[decision_type]:
            sample = results[decision_type][0]
            print(f"\n{decision_type}: \"{sample['original_artist']}\" - \"{sample['original_song']}\"")
            print(f"  Matched: \"{sample['clean_artist']}\" - \"{sample['clean_song']}\"")
            print(f"  Reason: {sample['analysis_reason']}")
    
    return results, stats


if __name__ == '__main__':
    results, stats = main()
