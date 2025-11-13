"""
Ananki Fix #2: Fill in Implicit Deltas for Proximity Queries

Analyzes proximity queries where delta/transformation is implied but not stated.
Examples:
- "songs similar to X" → infer what makes X special from context
- "like X but Y" → extract the Y delta
- "reminds me of X" → infer emotional/sonic qualities

This enriches the geometric structure for manifold training.
"""

import pandas as pd
import re

def extract_anchor_song_from_query(query_text):
    """Extract the anchor song/artist being referenced"""
    query_lower = query_text.lower()
    
    # Common patterns for anchor references
    patterns = [
        r'(?:like|similar to|reminds me of|sounds like)\s+["\']?([^"\',.!?]+?)["\']?\s+by\s+([^"\',.!?]+)',
        r'(?:like|similar to|reminds me of|sounds like)\s+([A-Z][^,.!?]+?)(?:\s+by\s+|\s*$)',
        r'fans of\s+([A-Z][^,.!?]+?)(?:\s+and|\s*,|\s*$)',
        r'if you (?:like|love)\s+([A-Z][^,.!?]+?)(?:\s+|,|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def infer_delta_from_context(query_text, reasoning_text):
    """
    Infer implicit delta from query context and recommendation reasoning.
    
    Strategy:
    1. Look for emotional/sonic descriptors in reasoning
    2. Look for comparative language ("more", "less", "but")
    3. Look for mood/vibe keywords that suggest transformation
    """
    
    # Combine texts for analysis
    full_text = f"{query_text} {reasoning_text}".lower()
    
    # Emotional/sonic descriptor patterns
    descriptor_patterns = {
        'energy': r'\b(energetic|high energy|hype|intense|powerful|aggressive|heavy)\b',
        'calmness': r'\b(calm|chill|relaxing|mellow|smooth|peaceful|tranquil)\b',
        'darkness': r'\b(dark|darker|moody|atmospheric|haunting|brooding|gothic)\b',
        'lightness': r'\b(bright|lighter|uplifting|cheerful|positive|happy)\b',
        'rawness': r'\b(raw|gritty|unpolished|rough|visceral|primal)\b',
        'polish': r'\b(polished|clean|refined|pristine|production)\b',
        'complexity': r'\b(complex|intricate|layered|experimental|progressive)\b',
        'simplicity': r'\b(simple|straightforward|minimalist|stripped down)\b',
        'emotional_intensity': r'\b(emotional|feelings|heartfelt|passionate|intimate)\b',
        'introspection': r'\b(introspective|thoughtful|contemplative|reflective|meditative)\b',
    }
    
    found_descriptors = []
    for quality, pattern in descriptor_patterns.items():
        if re.search(pattern, full_text):
            found_descriptors.append(quality)
    
    # Comparative language patterns (explicit deltas)
    comparative_patterns = [
        r'(?:but |more |less |with |without |adds? |keeps? )([a-z]+(?:\s+[a-z]+)?)',
        r'(?:preferably |hopefully |ideally )([a-z]+(?:\s+[a-z]+)?)',
    ]
    
    explicit_deltas = []
    for pattern in comparative_patterns:
        matches = re.finditer(pattern, full_text)
        for match in matches:
            delta_phrase = match.group(1).strip()
            # Filter out common words
            if delta_phrase not in ['the', 'a', 'an', 'to', 'of', 'in', 'on', 'at']:
                explicit_deltas.append(delta_phrase)
    
    # Combine found descriptors and explicit deltas
    all_deltas = found_descriptors + explicit_deltas
    
    if all_deltas:
        return ' | '.join(all_deltas[:5])  # Limit to 5 most relevant
    
    return None

def enhance_with_implicit_deltas(df):
    """
    Main function to enhance dataset with implicit delta inference.
    
    Process:
    1. Identify records with missing deltas
    2. Try to infer delta from query + reasoning context
    3. Add inferred deltas with confidence scoring
    """
    
    print("\n[ANALYZING] Identifying records with missing deltas...")
    
    # Records that might have implicit deltas
    missing_deltas = df['delta_description'].isna() | (df['delta_description'] == '')
    potential_proximity = df['vibe_description'].str.contains(
        r'\b(like|similar|reminds|sounds like|fans of|if you like)\b',
        case=False,
        na=False
    )
    
    candidates = df[missing_deltas & potential_proximity].copy()
    print(f"  Found {len(candidates)} proximity queries with missing deltas")
    
    if len(candidates) == 0:
        print("  No candidates found - all proximity queries already have deltas!")
        return df
    
    # Infer deltas for candidates
    print(f"\n[WORKING] Inferring implicit deltas...")
    inferred_deltas = []
    confidence_scores = []
    
    for idx, row in candidates.iterrows():
        query = str(row.get('vibe_description', ''))
        reasoning = str(row.get('recommendation_reasoning', ''))
        
        inferred_delta = infer_delta_from_context(query, reasoning)
        
        if inferred_delta:
            inferred_deltas.append((idx, inferred_delta))
            # Simple confidence: more descriptors = higher confidence
            descriptor_count = len(inferred_delta.split('|'))
            confidence = min(descriptor_count / 3.0, 1.0)  # Max confidence at 3+ descriptors
            confidence_scores.append(confidence)
    
    print(f"  Successfully inferred deltas for {len(inferred_deltas)} records")
    
    # Apply inferred deltas to dataframe
    df_enhanced = df.copy()
    for (idx, delta), confidence in zip(inferred_deltas, confidence_scores):
        df_enhanced.at[idx, 'delta_description'] = delta
        # Add confidence metadata if column exists
        if 'delta_inference_confidence' not in df_enhanced.columns:
            df_enhanced['delta_inference_confidence'] = None
        df_enhanced.at[idx, 'delta_inference_confidence'] = f"{confidence:.2f}"
    
    return df_enhanced

# Main execution
print("="*70)
print("ANANKI FIX #2: Fill in Implicit Deltas")
print("="*70)

# Load the merged V4+V5 data
try:
    df = pd.read_csv('training_data_structured_merged_v4v5.csv')
    print(f"\n[OK] Loaded {len(df)} records from merged V4+V5 dataset")
except FileNotFoundError:
    print("\n[ERROR] Merged dataset not found. Please run merge script first.")
    print("Looking for: training_data_structured_merged_v4v5.csv")
    exit(1)

# Check if we have delta columns (V5 data)
has_deltas = 'delta_description' in df.columns
if not has_deltas:
    print("\n[INFO] No delta_description column found.")
    print("This appears to be V4 data without geometric extraction.")
    print("Delta inference requires V5 data with relation_type, anchor_reference, etc.")
    print("\n[SKIP] Skipping Fix #2 - will be applied after V5 merge")
    exit(0)

# Analyze current delta coverage
print(f"\n[ANALYZING] Current delta coverage:")
total_records = len(df)
has_delta = (~df['delta_description'].isna()) & (df['delta_description'] != '')
delta_count = has_delta.sum()
delta_pct = (delta_count / total_records) * 100

print(f"  Records with deltas: {delta_count} / {total_records} ({delta_pct:.1f}%)")
print(f"  Records missing deltas: {total_records - delta_count} ({100 - delta_pct:.1f}%)")

# Enhance with implicit delta inference
df_enhanced = enhance_with_implicit_deltas(df)

# Calculate improvement
has_delta_new = (~df_enhanced['delta_description'].isna()) & (df_enhanced['delta_description'] != '')
delta_count_new = has_delta_new.sum()
delta_pct_new = (delta_count_new / total_records) * 100

print(f"\n" + "="*70)
print("RESULTS:")
print("="*70)

print(f"\nDelta Coverage:")
print(f"  Before: {delta_count} / {total_records} ({delta_pct:.1f}%)")
print(f"  After:  {delta_count_new} / {total_records} ({delta_pct_new:.1f}%)")
print(f"  Improvement: {delta_count_new - delta_count} deltas added ({delta_pct_new - delta_pct:.1f}pp)")

# Save enhanced data
output_file = 'training_data_structured_ananki_v2.csv'
df_enhanced.to_csv(output_file, index=False)
print(f"\n[OK] Saved enhanced data to: {output_file}")

# Sample some inferred deltas
print(f"\n" + "="*70)
print("SAMPLE INFERRED DELTAS:")
print("="*70)

inferred_mask = df_enhanced['delta_inference_confidence'].notna()
samples = df_enhanced[inferred_mask].head(10)

for idx, row in samples.iterrows():
    print(f"\nQuery: {row['vibe_description'][:80]}...")
    print(f"Inferred Delta: {row['delta_description']}")
    print(f"Confidence: {row['delta_inference_confidence']}")

print(f"\n[COMPLETE] Fix #2 Complete!")
print(f"\n[NEXT] Ready for Fix #3: Improve anchor extraction")
