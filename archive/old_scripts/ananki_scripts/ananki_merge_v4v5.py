"""
Ananki Data Merge: Combine V4 (vocabulary) + V5 (geometry)

V4 provides: 7,359 song recommendations with basic vibe categorization
V5 provides: Geometric structure (anchors, deltas, reasoning) for proximity queries

This merge creates the complete Tapestry dataset ready for manifold training.
"""

import pandas as pd
import json

print("="*70)
print("ANANKI DATA MERGE: V4 + V5 Integration")
print("="*70)

# Load V4 data (with Ananki Fix #1 improvements)
print("\n[LOADING] V4 vocabulary data...")
v4_df = pd.read_csv('training_data_structured_ananki_v1.csv')
print(f"  Loaded {len(v4_df)} V4 records")
print(f"  Columns: {list(v4_df.columns)}")

# Load V5 production data
print("\n[LOADING] V5 geometric data...")
try:
    v5_df = pd.read_csv('reddit/production_data/V5_PRODUCTION_FOR_ANANKI.csv')
    print(f"  Loaded {len(v5_df)} V5 records")
    print(f"  Columns: {list(v5_df.columns)}")
except FileNotFoundError:
    print("  [ERROR] V5 production data not found!")
    print("  Expected: reddit/production_data/V5_PRODUCTION_FOR_ANANKI.csv")
    exit(1)

# Analyze V5 geometric coverage
print(f"\n[ANALYZING] V5 geometric structure:")
has_anchor = (~v5_df['anchor_reference_song'].isna()) & (v5_df['anchor_reference_song'] != '')
has_delta = (~v5_df['delta_description'].isna()) & (v5_df['delta_description'] != '')
has_reasoning = (~v5_df['reasoning_text'].isna()) & (v5_df['reasoning_text'] != '')

anchor_pct = (has_anchor.sum() / len(v5_df)) * 100
delta_pct = (has_delta.sum() / len(v5_df)) * 100
reasoning_pct = (has_reasoning.sum() / len(v5_df)) * 100

print(f"  Anchor coverage: {has_anchor.sum()} / {len(v5_df)} ({anchor_pct:.1f}%)")
print(f"  Delta coverage: {has_delta.sum()} / {len(v5_df)} ({delta_pct:.1f}%)")
print(f"  Reasoning coverage: {has_reasoning.sum()} / {len(v5_df)} ({reasoning_pct:.1f}%)")

# Merge strategy:
# V4 records = complete vocabulary (7,359 songs)
# V5 records = add geometric structure where available
# Result = V4 base + V5 geometric enrichment

print(f"\n[MERGING] Combining datasets...")

# Add V5 columns to V4 dataframe (initialize with NaN)
v5_columns = [
    'relation_type',
    'anchor_reference_artist', 
    'anchor_reference_song',
    'delta_description',
    'reasoning_text',
    'sequence_order'
]

for col in v5_columns:
    if col not in v4_df.columns:
        v4_df[col] = None

# Try to match V5 records to V4 records
# Match on: song_name + artist_name + vibe_description (partial)
print(f"  Matching V5 geometric data to V4 vocabulary...")

matches_found = 0
for idx, v5_row in v5_df.iterrows():
    # Find matching V4 record
    v4_matches = v4_df[
        (v4_df['song_name'] == v5_row['song_name']) &
        (v4_df['artist_name'] == v5_row['artist_name'])
    ]
    
    if len(v4_matches) > 0:
        # Update first match with V5 geometric data
        v4_idx = v4_matches.index[0]
        for col in v5_columns:
            if col in v5_row and pd.notna(v5_row[col]) and v5_row[col] != '':
                v4_df.at[v4_idx, col] = v5_row[col]
        matches_found += 1

print(f"  Matched {matches_found} V5 records to V4 base")

# Append unmatched V5 records as new entries
print(f"  Adding {len(v5_df) - matches_found} new V5 records...")

# Find V5 records that didn't match V4
v5_unmatched = []
for idx, v5_row in v5_df.iterrows():
    v4_matches = v4_df[
        (v4_df['song_name'] == v5_row['song_name']) &
        (v4_df['artist_name'] == v5_row['artist_name'])
    ]
    if len(v4_matches) == 0:
        v5_unmatched.append(v5_row)

if len(v5_unmatched) > 0:
    v5_unmatched_df = pd.DataFrame(v5_unmatched)
    
    # Map V5 columns to V4 columns where possible
    column_mapping = {
        'vibe_request': 'vibe_description',
        'comment_context': 'recommendation_reasoning',
        # Add other mappings as needed
    }
    
    for v5_col, v4_col in column_mapping.items():
        if v5_col in v5_unmatched_df.columns and v4_col not in v5_unmatched_df.columns:
            v5_unmatched_df[v4_col] = v5_unmatched_df[v5_col]
    
    # Ensure all V4 columns exist
    for col in v4_df.columns:
        if col not in v5_unmatched_df.columns:
            v5_unmatched_df[col] = None
    
    # Append to V4
    merged_df = pd.concat([v4_df, v5_unmatched_df[v4_df.columns]], ignore_index=True)
else:
    merged_df = v4_df

print(f"\n" + "="*70)
print("MERGE RESULTS:")
print("="*70)

print(f"\nTotal records: {len(merged_df)}")
print(f"  From V4 base: {len(v4_df)}")
print(f"  New from V5: {len(merged_df) - len(v4_df)}")

# Analyze geometric enrichment in merged dataset
has_anchor_merged = (~merged_df['anchor_reference_song'].isna()) & (merged_df['anchor_reference_song'] != '')
has_delta_merged = (~merged_df['delta_description'].isna()) & (merged_df['delta_description'] != '')
has_reasoning_merged = (~merged_df['reasoning_text'].isna()) & (merged_df['reasoning_text'] != '')

print(f"\nGeometric Structure Coverage:")
print(f"  Anchors: {has_anchor_merged.sum()} records ({has_anchor_merged.sum()/len(merged_df)*100:.1f}%)")
print(f"  Deltas: {has_delta_merged.sum()} records ({has_delta_merged.sum()/len(merged_df)*100:.1f}%)")
print(f"  Reasoning: {has_reasoning_merged.sum()} records ({has_reasoning_merged.sum()/len(merged_df)*100:.1f}%)")

# Save merged dataset
output_file = 'training_data_structured_merged_v4v5.csv'
merged_df.to_csv(output_file, index=False)
print(f"\n[OK] Saved merged data to: {output_file}")

print(f"\n[COMPLETE] Merge complete!")
print(f"\n[NEXT] Now Fix #2 can be applied to enhance implicit deltas")
