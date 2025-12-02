#!/usr/bin/env python3
"""
V5 Foundation Analysis Script
Comprehensive diagnostics before scaling production run
"""

import pandas as pd
import json
from collections import Counter
from pathlib import Path
import re

def load_data():
    """Load V5 training data and metrics"""
    base_path = Path(r'c:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\reddit')

    df = pd.read_csv(base_path / 'reddit_v5_training_20251107_164412.csv')

    with open(base_path / 'reddit_v5_metrics_20251107_164412.json', 'r', encoding='utf-8') as f:
        metrics = json.load(f)

    with open(base_path / 'reddit_v5_relational_20251107_164412.json', 'r', encoding='utf-8') as f:
        relational_data = json.load(f)

    return df, metrics, relational_data

def analyze_relation_types(df):
    """A. Distribution Analysis - Relation Types"""
    print("=" * 80)
    print("A. RELATION TYPE DISTRIBUTION")
    print("=" * 80)

    rel_counts = df['relation_type'].value_counts()
    total = len(df)

    print(f"\nTotal records: {total}")
    print(f"\nRelation type breakdown:")
    for rel_type, count in rel_counts.items():
        pct = (count / total) * 100
        print(f"  {rel_type:20s}: {count:4d} ({pct:5.1f}%)")

    # Check for variety in proximity queries
    proximity_df = df[df['relation_type'] == 'proximity']
    print(f"\n  Proximity queries represent {len(proximity_df)/total*100:.1f}% of dataset")
    print(f"  This is the core relational signal - GOOD if >70%")

    return rel_counts

def analyze_delta_descriptions(df):
    """A. Distribution Analysis - Delta Descriptions"""
    print("\n" + "=" * 80)
    print("A. DELTA DESCRIPTION VARIETY")
    print("=" * 80)

    # Filter rows with delta descriptions
    delta_df = df[df['delta_description'].notna()]
    print(f"\nRecords with delta_description: {len(delta_df)} / {len(df)} ({len(delta_df)/len(df)*100:.1f}%)")

    if len(delta_df) == 0:
        print("\nWARNING: No delta descriptions found! This is critical for geometric learning.")
        return

    # Extract transformation terms
    deltas = delta_df['delta_description'].tolist()

    # Common transformation patterns
    patterns = {
        'more': r'\bmore\s+(\w+)',
        'less': r'\bless\s+(\w+)',
        'slower': r'\bslower\b',
        'faster': r'\bfaster\b',
        'heavier': r'\bheavier\b',
        'lighter': r'\blighter\b',
        'darker': r'\bdarker\b',
        'brighter': r'\bbrighter\b',
        'similar': r'\bsimilar\b',
        'without': r'\bwithout\s+(\w+)',
    }

    pattern_matches = Counter()
    for delta in deltas:
        if pd.isna(delta):
            continue
        delta_lower = str(delta).lower()
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, delta_lower):
                pattern_matches[pattern_name] += 1

    print(f"\nTransformation pattern diversity:")
    for pattern, count in pattern_matches.most_common():
        print(f"  {pattern:15s}: {count:3d} occurrences")

    # Show sample deltas
    print(f"\n10 Example delta_descriptions:")
    sample_deltas = delta_df['delta_description'].dropna().sample(min(10, len(delta_df)))
    for i, delta in enumerate(sample_deltas, 1):
        print(f"  {i:2d}. {delta[:80]}...")

    # Check for repetitive patterns
    unique_deltas = delta_df['delta_description'].nunique()
    print(f"\nUnique delta descriptions: {unique_deltas} / {len(delta_df)}")
    if unique_deltas / len(delta_df) < 0.5:
        print("  WARNING: Low variety - many repeated delta descriptions")
    else:
        print("  GOOD: High variety in transformations")

def analyze_anchor_tracks(df):
    """B. Anchor Track Analysis"""
    print("\n" + "=" * 80)
    print("B. ANCHOR TRACK ANALYSIS")
    print("=" * 80)

    # Count anchor references
    anchor_artist_counts = df['anchor_reference_artist'].notna().sum()
    anchor_song_counts = df['anchor_reference_song'].notna().sum()

    print(f"\nRecords with anchor_reference_artist: {anchor_artist_counts} / {len(df)} ({anchor_artist_counts/len(df)*100:.1f}%)")
    print(f"Records with anchor_reference_song: {anchor_song_counts} / {len(df)} ({anchor_song_counts/len(df)*100:.1f}%)")

    # Analyze anchor combinations
    df['anchor_combo'] = df.apply(
        lambda row: f"{row['anchor_reference_artist']} - {row['anchor_reference_song']}"
        if pd.notna(row['anchor_reference_artist']) and pd.notna(row['anchor_reference_song'])
        else None,
        axis=1
    )

    anchor_df = df[df['anchor_combo'].notna()]
    if len(anchor_df) == 0:
        print("\nWARNING: No complete anchor tracks (artist+song) found!")
        print("This severely limits geometric learning capability.")
        return

    unique_anchors = anchor_df['anchor_combo'].nunique()
    total_anchors = len(anchor_df)

    print(f"\nUnique anchor tracks: {unique_anchors}")
    print(f"Total anchor references: {total_anchors}")
    print(f"Reuse ratio: {total_anchors/unique_anchors:.2f}x")

    if unique_anchors / total_anchors > 0.8:
        print("  WARNING: Very little anchor reuse - might be too sparse for manifold")
    elif unique_anchors / total_anchors < 0.2:
        print("  WARNING: Heavy anchor repetition - limited coverage")
    else:
        print("  GOOD: Balanced anchor reuse creates dense neighborhoods")

    # Most common anchors
    print(f"\nTop 10 most referenced anchor tracks:")
    top_anchors = anchor_df['anchor_combo'].value_counts().head(10)
    for anchor, count in top_anchors.items():
        print(f"  {count:3d}x: {anchor}")

def analyze_reasoning_quality(df):
    """C. Reasoning Quality Check"""
    print("\n" + "=" * 80)
    print("C. REASONING QUALITY CHECK")
    print("=" * 80)

    reasoning_df = df[df['reasoning_text'].notna()]
    print(f"\nRecords with reasoning_text: {len(reasoning_df)} / {len(df)} ({len(reasoning_df)/len(df)*100:.1f}%)")

    if len(reasoning_df) == 0:
        print("\nWARNING: No reasoning text found!")
        print("Reasoning provides crucial context for understanding vibe transformations.")
        return

    # Sample reasoning quality
    print(f"\n15 Sample reasoning_text entries for manual quality review:")
    print("-" * 80)

    sample_reasoning = reasoning_df.sample(min(15, len(reasoning_df)))
    for idx, row in sample_reasoning.iterrows():
        print(f"\n[{idx}] Vibe: {row['vibe_request'][:60]}...")
        print(f"    Song: {row['artist_name']} - {row['song_name']}")
        print(f"    Reasoning: {row['reasoning_text'][:150]}...")
        if pd.notna(row['delta_description']):
            print(f"    Delta: {row['delta_description'][:100]}...")

    # Check reasoning length as proxy for quality
    reasoning_lengths = reasoning_df['reasoning_text'].str.len()
    print(f"\nReasoning text length statistics:")
    print(f"  Mean: {reasoning_lengths.mean():.0f} characters")
    print(f"  Median: {reasoning_lengths.median():.0f} characters")
    print(f"  Min: {reasoning_lengths.min():.0f} characters")
    print(f"  Max: {reasoning_lengths.max():.0f} characters")

    if reasoning_lengths.mean() < 50:
        print("  WARNING: Very short reasoning text - may be low quality")
    else:
        print("  GOOD: Reasoning text has substance")

def check_v4_overlap():
    """D. V4/V5 Overlap Analysis"""
    print("\n" + "=" * 80)
    print("D. V4/V5 OVERLAP ANALYSIS")
    print("=" * 80)

    base_path = Path(r'c:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\reddit')

    # Try to find V4 data
    v4_files = list(base_path.glob('*v4*.csv'))
    if not v4_files:
        print("\nNo V4 data files found for comparison.")
        print("Skipping overlap analysis.")
        return

    print(f"\nFound V4 files: {[f.name for f in v4_files]}")

    # Load V4 and V5 data
    v5_df = pd.read_csv(base_path / 'reddit_v5_training_20251107_164412.csv')

    # Try to load most recent V4
    try:
        v4_df = pd.read_csv(v4_files[0])

        # Create track identifiers
        v5_df['track_id'] = v5_df['artist_name'] + ' - ' + v5_df['song_name']
        v4_df['track_id'] = v4_df['artist_name'] + ' - ' + v4_df['song_name']

        v5_tracks = set(v5_df['track_id'].dropna().unique())
        v4_tracks = set(v4_df['track_id'].dropna().unique())

        overlap = v5_tracks & v4_tracks
        v5_only = v5_tracks - v4_tracks
        v4_only = v4_tracks - v5_tracks

        print(f"\nV4 unique tracks: {len(v4_tracks)}")
        print(f"V5 unique tracks: {len(v5_tracks)}")
        print(f"Overlapping tracks: {len(overlap)} ({len(overlap)/len(v5_tracks)*100:.1f}% of V5)")
        print(f"V5-exclusive tracks: {len(v5_only)}")
        print(f"V4-exclusive tracks: {len(v4_only)}")

        if len(overlap) / len(v5_tracks) > 0.8:
            print("\n  WARNING: Heavy overlap with V4 - limited new coverage")
        elif len(overlap) / len(v5_tracks) < 0.1:
            print("\n  WARNING: Almost no overlap - datasets may be disconnected")
        else:
            print("\n  GOOD: Moderate overlap creates bridges between datasets")

    except Exception as e:
        print(f"\nError loading V4 data: {e}")

def scaling_recommendations(df, metrics):
    """Recommendations for scaling strategy"""
    print("\n" + "=" * 80)
    print("SCALING RECOMMENDATIONS")
    print("=" * 80)

    # Calculate key metrics
    proximity_pct = (df['relation_type'] == 'proximity').sum() / len(df) * 100
    has_delta_pct = metrics['has_delta']
    has_reasoning_pct = metrics['has_reasoning']
    manifold_readiness = metrics['manifold_readiness_score']

    print(f"\nManifold Readiness Score: {manifold_readiness:.1f}/100")
    print(f"  Proximity queries: {proximity_pct:.1f}%")
    print(f"  Has delta: {has_delta_pct:.1f}%")
    print(f"  Has reasoning: {has_reasoning_pct:.1f}%")

    print("\n" + "-" * 80)
    print("RECOMMENDATION: ", end="")

    if manifold_readiness < 40:
        print("CRITICAL ISSUES - DO NOT SCALE YET")
        print("\nPriority fixes needed:")
        if has_delta_pct < 50:
            print("  1. Improve delta description extraction (currently {:.1f}%)".format(has_delta_pct))
        if has_reasoning_pct < 20:
            print("  2. Improve reasoning text capture (currently {:.1f}%)".format(has_reasoning_pct))
        if proximity_pct < 60:
            print("  3. Increase proximity query ratio (currently {:.1f}%)".format(proximity_pct))

    elif manifold_readiness < 60:
        print("VERTICAL SCALING (Depth First)")
        print("\nRationale:")
        print("  - Foundation is solid but could be denser")
        print("  - Increase posts_per_query from current settings")
        print("  - Focus on existing successful query patterns")
        print("\nSuggested changes:")
        print("  - Double posts_per_query for proximity queries")
        print("  - Add more 'like X but Y' variations")
        print("  - Target subreddits with rich transformation language")

    else:
        print("HORIZONTAL SCALING (Breadth)")
        print("\nRationale:")
        print("  - Strong foundation with good density")
        print("  - Ready to expand genre/emotional coverage")
        print("\nSuggested changes:")
        print("  - Add new subreddits (r/listentothis, r/under10k)")
        print("  - Expand genre families (add subgenres)")
        print("  - Test new relational query patterns")

    # Query type focus
    print("\n" + "-" * 80)
    print("QUERY TYPE OPTIMIZATION:")
    print("\nDouble down on these query types:")
    rel_counts = df['relation_type'].value_counts()
    for rel_type, count in rel_counts.items():
        if count > 50:
            print(f"  - {rel_type} (currently {count} records) - CORE SIGNAL")

    print("\nExperiment with these query types:")
    for rel_type, count in rel_counts.items():
        if count < 20:
            print(f"  - {rel_type} (currently {count} records) - NEEDS MORE DATA")

def merge_strategy():
    """Recommendations for V4/V5 merge"""
    print("\n" + "=" * 80)
    print("V4/V5 MERGE STRATEGY")
    print("=" * 80)

    print("\nConceptual roles:")
    print("  V4 (General vibes) - Vocabulary & Coverage")
    print("    - Teaches: What songs exist in each emotional space")
    print("    - Teaches: Broad genre-vibe associations")
    print("    - Weight: 1.0x (baseline)")
    print()
    print("  V5 (Relational vibes) - Geometry & Transformations")
    print("    - Teaches: How songs differ from each other")
    print("    - Teaches: Directional movement in vibe space")
    print("    - Weight: 2.0-3.0x (geometric supervisor)")

    print("\nMerge implementation:")
    print("  1. Keep datasets separate initially")
    print("  2. Create unified track ID space (Spotify IDs preferred)")
    print("  3. During training:")
    print("     - V4: Standard triplet/contrastive loss")
    print("     - V5: Geometric constraint loss (anchor-target with delta)")
    print("     - V5 loss weight = 2-3x V4 loss weight")

    print("\nPreprocessing needed:")
    print("  - Validate all track IDs against Spotify API")
    print("  - Create canonical track objects merging metadata")
    print("  - Extract delta vectors from delta_description text")
    print("  - Compute confidence scores for each relation")
    print("  - Flag low-quality relations for filtering")

    print("\nQuality thresholds for merge:")
    print("  V5 records must have:")
    print("    - relation_type = 'proximity' OR 'contextual'")
    print("    - extraction_confidence >= 0.7")
    print("    - Either delta_description OR reasoning_text present")
    print("    - Both anchor and target tracks validated")

def main():
    """Run complete foundation analysis"""
    print("\n" + "=" * 80)
    print("V5 FOUNDATION ANALYSIS")
    print("Before Scaling to Production")
    print("=" * 80)

    # Load data
    df, metrics, relational_data = load_data()

    # Run all analyses
    analyze_relation_types(df)
    analyze_delta_descriptions(df)
    analyze_anchor_tracks(df)
    analyze_reasoning_quality(df)
    check_v4_overlap()

    # Recommendations
    scaling_recommendations(df, metrics)
    merge_strategy()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Review sample reasoning text for quality")
    print("  2. Decide on scaling direction (breadth vs depth)")
    print("  3. Adjust scraper configuration accordingly")
    print("  4. Run production V5 scrape")
    print("  5. Begin V4/V5 merge process")
    print()

if __name__ == '__main__':
    main()
