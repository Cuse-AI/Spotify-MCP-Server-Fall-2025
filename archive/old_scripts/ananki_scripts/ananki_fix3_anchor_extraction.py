"""
Ananki Fix #3: Aggressive Anchor Extraction

Current coverage: 1.7% (131 / 7,740)
Target: 70% (5,418 / 7,740)

Strategy:
1. Multi-pattern anchor detection (quoted, unquoted, title case, lists)
2. Extract from both vibe_description AND recommendation_reasoning
3. Validate and score confidence for each extracted anchor
4. Handle edge cases (multiple anchors, artist-only references, album references)
"""

import pandas as pd
import re
from collections import defaultdict

# Comprehensive anchor extraction patterns
ANCHOR_PATTERNS = [
    # High confidence - quoted with "by"
    (r'"([^"]+)"\s+by\s+([A-Z][^,.\n!?]+?)(?:\s|,|\.|\n|$)', 'quoted_by', 0.9),
    (r"'([^']+)'\s+by\s+([A-Z][^,.\n!?]+?)(?:\s|,|\.|\n|$)", 'quoted_by', 0.9),
    
    # High confidence - "Artist - Song" format
    (r'\b([A-Z][A-Za-z\s&]+?)\s*-\s*([A-Z][^-\n]+?)(?:\s|,|\.|\n|$)', 'dash_format', 0.85),
    
    # Medium confidence - Title Case by Artist
    (r'\b([A-Z][A-Za-z\s]+?)\s+by\s+([A-Z][^,.\n!?]+?)(?:\s|,|\.|\n|$)', 'title_case_by', 0.75),
    
    # Medium confidence - "like/similar to X"
    (r'(?:like|similar to|sounds like|reminds me of|fans of)\s+"([^"]+)"\s+by\s+([A-Z][^,.\n]+)', 'similarity_quoted', 0.8),
    (r'(?:like|similar to|sounds like|reminds me of|fans of)\s+([A-Z][A-Za-z\s]+?)(?:\s+by\s+|\s*$|\s+and)', 'similarity_unquoted', 0.6),
    
    # Lower confidence - artist name after "by" (song name extracted from context)
    (r'by\s+([A-Z][A-Za-z\s&]+?)(?:\s|,|\.|\n|and|or|$)', 'artist_only', 0.4),
    
    # Lists with "and"
    (r'"([^"]+)"\s+by\s+([A-Z][^"]+?)\s+and\s+"([^"]+)"\s+by\s+([A-Z][^"]+)', 'list_format', 0.85),
]

def clean_anchor_name(text):
    """Clean and validate anchor song/artist name"""
    if not text:
        return None
    
    text = text.strip()
    
    # Remove trailing punctuation
    text = re.sub(r'[,.\n!?]+$', '', text)
    
    # Remove common noise words at start/end
    noise_patterns = [
        r'^(?:the song|the track|song|track|album|by|and|or|with)\s+',
        r'\s+(?:song|track|album|by|and|or|with)$'
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    text = text.strip()
    
    # Validation
    if len(text) < 2 or len(text) > 100:
        return None
    
    # Reject if mostly numbers or special chars
    if re.match(r'^[\d\s\-_]+$', text):
        return None
    
    # Reject vibe description phrases (not song names)
    vibe_phrases = [
        'pure unadulterated', 'give me', 'looking for', 'i need', 'songs for',
        'music for', 'playlist for', 'recommendations', 'similar to'
    ]
    text_lower = text.lower()
    if any(phrase in text_lower for phrase in vibe_phrases):
        return None
    
    # Reject common non-musical phrases
    reject_phrases = [
        'spotify', 'youtube', 'playlist', 'reddit', 'link', 'http',
        'i think', 'i like', 'i love', 'listen to', 'check out'
    ]
    if any(phrase in text_lower for phrase in reject_phrases):
        return None
    
    return text

def extract_anchors_from_text(text, source_type='reasoning'):
    """
    Extract all possible anchors from a text using multiple patterns.
    Returns list of (song, artist, confidence, method) tuples.
    
    source_type: 'vibe' or 'reasoning' - affects which patterns are used
    """
    if not text or pd.isna(text):
        return []
    
    anchors = []
    text = str(text)
    
    # Select patterns based on source type
    patterns_to_use = ANCHOR_PATTERNS
    if source_type == 'vibe':
        # For vibe descriptions, skip dash-format (it catches vibe titles)
        patterns_to_use = [(p, m, c) for p, m, c in ANCHOR_PATTERNS if m != 'dash_format']
    
    for pattern, method, confidence in patterns_to_use:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            groups = match.groups()
            
            if method == 'artist_only':
                # Artist-only extraction - try to find song in nearby context
                artist = clean_anchor_name(groups[0])
                if artist:
                    anchors.append((None, artist, confidence * 0.5, method))
            
            elif method == 'list_format':
                # Multiple songs in one match
                song1 = clean_anchor_name(groups[0])
                artist1 = clean_anchor_name(groups[1])
                song2 = clean_anchor_name(groups[2])
                artist2 = clean_anchor_name(groups[3])
                
                if song1 and artist1:
                    anchors.append((song1, artist1, confidence, method))
                if song2 and artist2:
                    anchors.append((song2, artist2, confidence, method))
            
            elif method == 'dash_format':
                # Artist - Song (need to determine which is which)
                part1 = clean_anchor_name(groups[0])
                part2 = clean_anchor_name(groups[1])
                
                if part1 and part2:
                    # Artist is usually first in dash format
                    anchors.append((part2, part1, confidence, method))
            
            elif len(groups) >= 2:
                # Standard (song, artist) extraction
                song = clean_anchor_name(groups[0])
                artist = clean_anchor_name(groups[1])
                
                if song or artist:  # At least one must be valid
                    anchors.append((song, artist, confidence, method))
    
    return anchors

def deduplicate_anchors(anchors):
    """Remove duplicate anchors, keeping highest confidence"""
    if not anchors:
        return []
    
    # Group by (song, artist) pair
    anchor_dict = defaultdict(lambda: {'confidence': 0, 'method': None})
    
    for song, artist, confidence, method in anchors:
        key = (song or '', artist or '')
        if confidence > anchor_dict[key]['confidence']:
            anchor_dict[key] = {'confidence': confidence, 'method': method, 'song': song, 'artist': artist}
    
    # Convert back to list, sorted by confidence
    result = [(v['song'], v['artist'], v['confidence'], v['method']) 
              for v in sorted(anchor_dict.values(), key=lambda x: x['confidence'], reverse=True)]
    
    return result

def enhance_anchor_extraction(df):
    """
    Main function to enhance anchor extraction across the dataset.
    
    Process:
    1. For each record, try to extract anchors from multiple sources
    2. Combine anchors from vibe_description and recommendation_reasoning
    3. Deduplicate and score confidence
    4. Update records with best anchor found
    """
    
    print("\n[ANALYZING] Current anchor coverage...")
    has_anchor = (~df['anchor_reference_song'].isna()) & (df['anchor_reference_song'] != '')
    current_coverage = has_anchor.sum()
    print(f"  Current: {current_coverage} / {len(df)} ({current_coverage/len(df)*100:.1f}%)")
    
    print(f"\n[WORKING] Extracting anchors with aggressive pattern matching...")
    
    new_anchors_found = 0
    improved_anchors = 0
    
    for idx, row in df.iterrows():
        # Check if already has high-confidence anchor
        existing_anchor = row.get('anchor_reference_song')
        has_existing = existing_anchor and not pd.isna(existing_anchor) and existing_anchor != ''
        
        # Extract from multiple sources
        all_anchors = []
        
        # Source 1: vibe_description (skip dash-format to avoid false positives)
        if 'vibe_description' in row and pd.notna(row['vibe_description']):
            anchors_from_vibe = extract_anchors_from_text(row['vibe_description'], source_type='vibe')
            all_anchors.extend(anchors_from_vibe)
        
        # Source 2: recommendation_reasoning (use all patterns)
        if 'recommendation_reasoning' in row and pd.notna(row['recommendation_reasoning']):
            anchors_from_reasoning = extract_anchors_from_text(row['recommendation_reasoning'], source_type='reasoning')
            all_anchors.extend(anchors_from_reasoning)
        
        # Deduplicate and get best anchor
        best_anchors = deduplicate_anchors(all_anchors)
        
        if best_anchors:
            best_song, best_artist, best_confidence, best_method = best_anchors[0]
            
            # Update if: no existing anchor OR new anchor has higher confidence
            if not has_existing or best_confidence > 0.7:
                if best_song:
                    df.at[idx, 'anchor_reference_song'] = best_song
                if best_artist:
                    df.at[idx, 'anchor_reference_artist'] = best_artist
                
                # Add metadata
                if 'anchor_extraction_method' not in df.columns:
                    df['anchor_extraction_method'] = None
                if 'anchor_confidence' not in df.columns:
                    df['anchor_confidence'] = None
                
                df.at[idx, 'anchor_extraction_method'] = best_method
                df.at[idx, 'anchor_confidence'] = f"{best_confidence:.2f}"
                
                if has_existing:
                    improved_anchors += 1
                else:
                    new_anchors_found += 1
        
        # Progress indicator
        if (idx + 1) % 1000 == 0:
            print(f"    Processed {idx + 1} / {len(df)} records...")
    
    return df, new_anchors_found, improved_anchors

# Main execution
print("="*70)
print("ANANKI FIX #3: Aggressive Anchor Extraction")
print("="*70)

# Load Ananki v2 data (output from Fix #2)
try:
    df = pd.read_csv('ananki_outputs/ananki_v2_with_implicit_deltas.csv')
    print(f"\n[OK] Loaded {len(df)} records from Fix #2 output")
except FileNotFoundError:
    print("\n[ERROR] Fix #2 output not found. Please run Fix #2 first.")
    print("Looking for: ananki_outputs/ananki_v2_with_implicit_deltas.csv")
    exit(1)

# Enhance anchor extraction
df_enhanced, new_count, improved_count = enhance_anchor_extraction(df)

# Calculate improvement
has_anchor_new = (~df_enhanced['anchor_reference_song'].isna()) & (df_enhanced['anchor_reference_song'] != '')
new_coverage = has_anchor_new.sum()
new_coverage_pct = (new_coverage / len(df_enhanced)) * 100

print(f"\n" + "="*70)
print("RESULTS:")
print("="*70)

print(f"\nAnchor Coverage:")
print(f"  Before: 131 / {len(df)} (1.7%)")
print(f"  After:  {new_coverage} / {len(df_enhanced)} ({new_coverage_pct:.1f}%)")
print(f"  New anchors found: {new_count}")
print(f"  Existing anchors improved: {improved_count}")
print(f"  Total improvement: {new_coverage - 131} anchors (+{new_coverage_pct - 1.7:.1f}pp)")

# Save enhanced data
output_file = 'ananki_outputs/ananki_v3_with_anchors.csv'
df_enhanced.to_csv(output_file, index=False)
print(f"\n[OK] Saved enhanced data to: {output_file}")

# Sample some extracted anchors
print(f"\n" + "="*70)
print("SAMPLE EXTRACTED ANCHORS:")
print("="*70)

new_anchors_mask = df_enhanced['anchor_extraction_method'].notna()
samples = df_enhanced[new_anchors_mask].head(15)

for idx, row in samples.iterrows():
    print(f"\nVibe: {row['vibe_description'][:70]}...")
    if pd.notna(row.get('anchor_reference_song')):
        print(f"  Anchor Song: {row['anchor_reference_song']}")
    if pd.notna(row.get('anchor_reference_artist')):
        print(f"  Anchor Artist: {row['anchor_reference_artist']}")
    print(f"  Method: {row['anchor_extraction_method']}")
    print(f"  Confidence: {row['anchor_confidence']}")

print(f"\n[COMPLETE] Fix #3 Complete!")
print(f"\n[NEXT] Ready for Fix #4: Create booster scraper templates")
