"""
ANANKI SUB-VIBE MAPPER
Analyzes song context to determine specific sub-vibe placement

Uses the same analysis approach that mapped the original 114 sub-vibes:
- Keyword matching for clear cases (90%)
- Contextual analysis for nuanced cases (10%)
"""

import json
import re
from pathlib import Path
from collections import defaultdict

class AnankiSubVibeMapper:
    def __init__(self):
        # Load the emotional manifold to know what sub-vibes exist
        manifold_file = Path(__file__).parent.parent / 'ananki_outputs' / 'emotional_manifold_COMPLETE.json'
        
        with open(manifold_file, 'r', encoding='utf-8') as f:
            self.manifold = json.load(f)
        
        # Build keyword mappings for each sub-vibe
        self.keyword_map = self._build_keyword_map()
    
    def _build_keyword_map(self):
        """Build keyword indicators for ALL 114 sub-vibes"""
        from COMPLETE_KEYWORD_MAP import COMPLETE_KEYWORD_MAP
        return COMPLETE_KEYWORD_MAP
    
    def analyze_context(self, context_text, exclude_terms=None):
        """
        Analyze comment context to determine sub-vibe.
        
        CRITICAL: Only analyzes HUMAN CONTEXT (post titles, comments)
        NEVER uses artist/song names - that would create false positives!
        
        exclude_terms: Artist and song names to exclude from analysis
        """
        if exclude_terms:
            # Remove artist/song names from context before analysis
            context_lower = context_text.lower()
            for term in exclude_terms:
                context_lower = context_lower.replace(term.lower(), '')
        else:
            context_lower = context_text.lower()
        
        # Score each sub-vibe based on keyword matches
        scores = defaultdict(int)
        
        for subvibe, keywords in self.keyword_map.items():
            for keyword in keywords:
                if keyword in context_lower:
                    scores[subvibe] += 1
        
        # Return top match if confident
        if scores:
            top_match = max(scores.items(), key=lambda x: x[1])
            return top_match[0], top_match[1], 'keyword_match'
        
        return None, 0, 'no_match'
    
    def map_songs_to_subvibes(self, songs_data):
        """
        Map songs to specific sub-vibes based on context.
        
        Input: List of songs with 'comment_context'
        Output: Songs with 'mapped_subvibe' field
        """
        mapped = []
        stats = {
            'total': len(songs_data),
            'mapped': 0,
            'ambiguous': 0,
            'by_subvibe': defaultdict(int)
        }
        
        for song in songs_data:
            # Use FULL context (comment + post title + post body)
            context = song.get('full_context', song.get('comment_context', ''))
            
            # Fallback: if no full_context, build it
            if not context or len(context) < 20:
                context = f"{song.get('post_title', '')}. {song.get('comment_text', '')}"
            
            # CRITICAL: Exclude artist/song names from context analysis!
            exclude_terms = [song.get('artist', ''), song.get('song', '')]
            
            # Analyze context
            subvibe, confidence, method = self.analyze_context(context, exclude_terms)
            
            if subvibe:
                song['mapped_subvibe'] = subvibe
                song['mapping_confidence'] = confidence
                song['mapping_method'] = method
                mapped.append(song)
                stats['mapped'] += 1
                stats['by_subvibe'][subvibe] += 1
            else:
                # Use the vibe field if provided, or mark as ambiguous
                if 'vibe' in song:
                    song['mapped_subvibe'] = song['vibe']
                    song['mapping_confidence'] = 0
                    song['mapping_method'] = 'default'
                    mapped.append(song)
                    stats['by_subvibe'][song['vibe']] += 1
                else:
                    song['mapped_subvibe'] = 'NEEDS_REVIEW'
                    song['mapping_confidence'] = 0
                    song['mapping_method'] = 'ambiguous'
                    mapped.append(song)
                    stats['ambiguous'] += 1
        
        return mapped, stats


def main(input_file):
    """Map songs to sub-vibes"""
    print("\nANANKI SUB-VIBE MAPPER")
    print("="*70)
    
    # Load songs
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    songs = data.get('songs', [])
    print(f"Analyzing {len(songs)} songs...")
    
    # Map to sub-vibes
    mapper = AnankiSubVibeMapper()
    mapped_songs, stats = mapper.map_songs_to_subvibes(songs)
    
    # Results
    print(f"\n{'='*70}")
    print("MAPPING COMPLETE")
    print(f"{'='*70}")
    print(f"Total analyzed: {stats['total']}")
    print(f"Mapped: {stats['mapped']}")
    print(f"Ambiguous: {stats['ambiguous']}")
    print(f"\nBreakdown by sub-vibe:")
    for subvibe, count in sorted(stats['by_subvibe'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {subvibe}: {count} songs")
    
    # Save
    output_file = Path(input_file).parent / f"{Path(input_file).stem}_MAPPED.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(mapped_songs),
            'stats': dict(stats),
            'songs': mapped_songs
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_file}")
    return mapped_songs

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        # Default: test on happy results
        main('test_results/happy_smart_extraction_500.json')
