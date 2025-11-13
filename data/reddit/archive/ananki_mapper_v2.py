"""
TRUE ANANKI MAPPER - Human-like emotional analysis
Each song gets analyzed with REASONING, not just keyword matching!
"""

import json
from pathlib import Path
from collections import defaultdict

class TrueAnankiMapper:
    def __init__(self):
        # Load available sub-vibes from tapestry
        tapestry_file = Path(__file__).parent.parent / 'ananki_outputs' / 'tapestry_VALIDATED_ONLY.json'
        with open(tapestry_file, 'r', encoding='utf-8') as f:
            tapestry = json.load(f)
        self.available_subvibes = list(tapestry['vibes'].keys())
        print(f"Loaded {len(self.available_subvibes)} sub-vibes from tapestry")
    
    def analyze_song_context(self, song_data):
        """
        ANANKI ANALYSIS - Read context like a human and determine sub-vibe
        
        Returns: (subvibe, reasoning, confidence)
        """
        # Get full context (excluding artist/song names!)
        context = song_data.get('full_context', '')
        post_title = song_data.get('post_title', '')
        comment = song_data.get('comment_text', '')
        
        # Remove artist/song from context to avoid false positives
        artist = song_data.get('artist', '')
        song_name = song_data.get('song', '')
        
        clean_context = context.lower()
        for term in [artist.lower(), song_name.lower()]:
            if term:
                clean_context = clean_context.replace(term, '')
        
        # ANANKI THINKS: What is the emotional intent here?
        reasoning_parts = []
        scores = defaultdict(float)
        
        # Analyze for SAD sub-vibes
        if any(word in clean_context for word in ['cry', 'crying', 'tears', 'weep', 'sob']):
            scores['Sad - Crying'] += 2.0
            reasoning_parts.append("mentions crying/tears")
        
        if any(word in clean_context for word in ['heartbreak', 'heartbroken', 'breakup', 'broke up', 'ex ']):
            scores['Sad - Heartbreak'] += 2.0
            reasoning_parts.append("discusses heartbreak/breakup")
        
        if any(word in clean_context for word in ['lonely', 'alone', 'loneliness', 'isolated', 'solitude']):
            scores['Sad - Lonely'] += 2.0
            reasoning_parts.append("expresses loneliness/isolation")
        
        if any(word in clean_context for word in ['grief', 'loss', 'death', 'died', 'funeral', 'mourning', 'passed away']):
            scores['Sad - Grief'] += 2.0
            reasoning_parts.append("about grief/loss/death")
        
        if any(word in clean_context for word in ['depress', 'hopeless', 'empty', 'numb', 'void', 'dark place']):
            scores['Sad - Depressive'] += 2.0
            reasoning_parts.append("describes depression/hopelessness")
        
        if any(word in clean_context for word in ['melanchol', 'bittersweet', 'wistful', 'pensive', 'somber']):
            scores['Sad - Melancholic'] += 2.0
            reasoning_parts.append("melancholic/bittersweet tone")
        
        if any(word in clean_context for word in ['nostalg', 'remember when', 'used to', 'miss the', 'back then']):
            scores['Sad - Nostalgic Sad'] += 2.0
            reasoning_parts.append("nostalgic for the past")
        
        # HAPPY sub-vibes
        if any(word in clean_context for word in ['feel good', 'uplifting', 'positive', 'cheerful', 'joyful', 'happy', 'good mood', 'smile']):
            scores['Happy - Feel Good'] += 2.0
            reasoning_parts.append("feel-good/uplifting vibe")
        
        if any(word in clean_context for word in ['euphori', 'ecstatic', 'bliss', 'elated', 'pure joy', 'over the moon']):
            scores['Happy - Euphoric'] += 2.0
            reasoning_parts.append("euphoric/ecstatic energy")
        
        if any(word in clean_context for word in ['sunshine', 'bright', 'sunny', 'radiant', 'warm', 'golden']):
            scores['Happy - Sunshine'] += 2.0
            reasoning_parts.append("sunny/bright imagery")
        
        if any(word in clean_context for word in ['carefree', 'playful', 'fun', 'lighthearted', 'silly', 'goofy']):
            scores['Happy - Carefree'] += 2.0
            reasoning_parts.append("playful/carefree spirit")
        
        if any(word in clean_context for word in ['celebrat', 'party', 'victory', 'grateful', 'thankful', 'blessed']):
            scores['Happy - Celebration'] += 2.0
            reasoning_parts.append("celebratory/grateful context")
        
        # ENERGY sub-vibes
        if any(word in clean_context for word in ['workout', 'gym', 'exercise', 'training', 'fitness', 'lift']):
            scores['Energy - Workout'] += 2.0
            reasoning_parts.append("workout/gym context")
        
        if any(word in clean_context for word in ['pump up', 'pumped', 'hype', 'energize', 'amped', 'hyped up']):
            scores['Energy - Pump Up'] += 2.0
            reasoning_parts.append("pump-up/hype energy")
        
        if any(word in clean_context for word in ['running', 'run', 'cardio', 'marathon', 'jog']):
            scores['Energy - Running'] += 2.0
            reasoning_parts.append("running/cardio specific")
        
        if any(word in clean_context for word in ['confident', 'powerful', 'motivat', 'inspiring', 'beast mode', 'unstoppable']):
            scores['Energy - Confidence'] += 2.0
            reasoning_parts.append("confidence/motivation theme")
        
        if any(word in clean_context for word in ['sport', 'game day', 'competition', 'athletic', 'team']):
            scores['Energy - Sports'] += 2.0
            reasoning_parts.append("sports/competition context")
        
        # ROMANTIC sub-vibes (adding now!)
        if any(word in clean_context for word in ['first love', 'young love', 'new love', 'falling in love']):
            scores['Romantic - First Love'] += 2.0
            reasoning_parts.append("first/new love theme")
        
        if any(word in clean_context for word in ['deep love', 'true love', 'unconditional', 'soulmate', 'forever']):
            scores['Romantic - Deep Love'] += 2.0
            reasoning_parts.append("deep/true love context")
        
        if any(word in clean_context for word in ['miss you', 'missing', 'longing', 'distance', 'far away', 'long distance']):
            scores['Romantic - Longing'] += 2.0
            reasoning_parts.append("longing/missing someone")
        
        if any(word in clean_context for word in ['slow dance', 'dancing', 'dance with', 'hold close']):
            scores['Romantic - Slow Dance'] += 2.0
            reasoning_parts.append("slow dance/intimacy")
        
        if any(word in clean_context for word in ['wedding', 'marry', 'marriage', 'bride', 'groom', 'proposal']):
            scores['Romantic - Wedding'] += 2.0
            reasoning_parts.append("wedding/marriage context")
        
        if any(word in clean_context for word in ['passionate', 'desire', 'intense love', 'obsess']):
            scores['Romantic - Passionate'] += 2.0
            reasoning_parts.append("passionate/intense love")
        
        if any(word in clean_context for word in ['crush', 'attraction', 'butterflies', 'nervous around']):
            scores['Romantic - Crush'] += 2.0
            reasoning_parts.append("crush/attraction feelings")
        
        # Determine best match
        if scores:
            best_subvibe = max(scores.items(), key=lambda x: x[1])
            subvibe = best_subvibe[0]
            confidence = best_subvibe[1]
            
            # Build reasoning
            reasoning = f"Ananki analysis: {'; '.join(reasoning_parts)}. Mapped to {subvibe}."
            
            return subvibe, reasoning, confidence
        
        # No clear match - truly ambiguous
        return None, "No clear emotional indicators found in context - needs deeper analysis or may lack specific emotional intent", 0.0
    
    def map_all_songs(self, songs_data):
        """Map all songs with full Ananki analysis"""
        results = {
            'mapped': [],
            'ambiguous': []
        }
        
        stats = {
            'total': len(songs_data),
            'mapped': 0,
            'ambiguous': 0,
            'by_subvibe': defaultdict(int)
        }
        
        for song in songs_data:
            subvibe, reasoning, confidence = self.analyze_song_context(song)
            
            if subvibe and confidence > 0:
                # Mapped successfully!
                song['mapped_subvibe'] = subvibe
                song['ananki_analysis'] = reasoning
                song['mapping_confidence'] = confidence
                results['mapped'].append(song)
                stats['mapped'] += 1
                stats['by_subvibe'][subvibe] += 1
            else:
                # Truly ambiguous - set aside for review
                song['mapped_subvibe'] = 'AMBIGUOUS'
                song['ananki_analysis'] = reasoning
                song['mapping_confidence'] = 0
                results['ambiguous'].append(song)
                stats['ambiguous'] += 1
        
        return results, stats


def main(input_file):
    print("\nTRUE ANANKI MAPPER - WITH REASONING")
    print("="*70)
    
    # Load songs
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    songs = data.get('songs', [])
    print(f"Analyzing {len(songs)} songs with full context...\n")
    
    # Map
    mapper = TrueAnankiMapper()
    results, stats = mapper.map_all_songs(songs)
    
    # Print results
    print(f"\n{'='*70}")
    print("ANANKI ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"Total: {stats['total']}")
    print(f"Mapped with reasoning: {stats['mapped']} ({stats['mapped']/stats['total']*100:.1f}%)")
    print(f"Ambiguous (set aside): {stats['ambiguous']} ({stats['ambiguous']/stats['total']*100:.1f}%)")
    print(f"\nMapped sub-vibes:")
    for subvibe, count in sorted(stats['by_subvibe'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {subvibe}: {count} songs")
    
    # Show example reasoning
    if results['mapped']:
        print(f"\n{'='*70}")
        print("EXAMPLE ANANKI REASONING:")
        print(f"{'='*70}")
        example = results['mapped'][0]
        print(f"Song: {example['artist']} - {example['song']}")
        print(f"Context: {example.get('post_title', '')[:60]}...")
        print(f"Ananki: {example['ananki_analysis']}")
    
    # Save with separated ambiguous
    output_file = Path(input_file).parent / f"{Path(input_file).stem}_ANANKI_MAPPED.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'stats': dict(stats),
            'mapped_songs': results['mapped'],
            'ambiguous_songs': results['ambiguous']
        }, f, indent=2, ensure_ascii=False)
    
    # Save ambiguous separately for review
    if results['ambiguous']:
        ambiguous_file = Path(input_file).parent / f"{Path(input_file).stem}_AMBIGUOUS_FOR_REVIEW.json"
        with open(ambiguous_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(results['ambiguous']),
                'note': 'These songs lack clear emotional context - may need new sub-vibes or should be discarded',
                'songs': results['ambiguous']
            }, f, indent=2, ensure_ascii=False)
        print(f"\nAmbiguous songs saved to: {ambiguous_file.name}")
    
    print(f"\nMapped songs saved to: {output_file}")
    return results

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Usage: python ananki_mapper_v2.py <input_file>")
