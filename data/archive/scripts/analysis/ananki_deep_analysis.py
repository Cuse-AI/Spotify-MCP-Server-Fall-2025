"""
Ananki Deep Analysis - Batch 13 Part 2
Acting as human-in-the-loop to validate emotional authenticity
"""
import pandas as pd
import random

df = pd.read_csv('reddit/reddit_batch13_part2_hopeful_excited_20251108_195309.csv')

print("="*80)
print("ANANKI EMOTIONAL VALIDATION - BATCH 13 PART 2")
print("="*80)

vibes = sorted(df['vibe_sub_category'].unique())
for vibe in vibes:
    print(f"\n{'='*80}")
    print(f"VIBE: {vibe}")
    print(f"{'='*80}")

    subset = df[df['vibe_sub_category'] == vibe]
    print(f"Total songs: {len(subset)}")

    # Sample 10 for deep review
    samples = subset.sample(min(10, len(subset)), random_state=42)

    print("\n--- Sample Songs for Emotional Validation ---")
    for idx, (_, row) in enumerate(samples.iterrows(), 1):
        artist = str(row['artist_name']).strip()
        song = str(row['song_name']).strip()
        reasoning = str(row['recommendation_reasoning']).strip()
        desc = str(row['vibe_description']).strip()

        print(f"\n{idx}. {artist} - {song}")
        if desc and desc != 'nan':
            print(f"   Query: {desc[:150]}")
        if reasoning and reasoning != 'nan' and len(reasoning) > 10:
            print(f"   Context: {reasoning[:200]}")

    print("\n--- Emotional Analysis ---")
    # Examine vibe descriptions to understand what users were seeking
    unique_descs = subset['vibe_description'].value_counts().head(3)
    print("Top user requests:")
    for desc, count in unique_descs.items():
        if str(desc) != 'nan':
            print(f"  - '{desc[:100]}' ({count} songs)")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
