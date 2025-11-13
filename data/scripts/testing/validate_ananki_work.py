"""
Validate Ananki Analysis - Check if human context was properly used
"""
import pandas as pd

df = pd.read_csv('analyzed_batches/batch13_part2_analyzed_by_ananki.csv')

print("="*80)
print("ANANKI WORK VALIDATION - BATCH 13 PART 2")
print("="*80)

# Check synthwave/electronic categorization
print("\n1. Genre Inference from Human Context")
print("-"*80)

synth = df[df['vibe_description'].str.contains('synthwave|cyberpunk|electronic', case=False, na=False)]
print(f"Posts mentioning synthwave/cyberpunk/electronic: {len(synth)}")
print(f"Genre assignments for these:")
print(synth['genre_category'].value_counts())

# Check a few examples
print("\nExamples:")
for idx, row in synth.head(5).iterrows():
    print(f"\nContext: '{row['vibe_description'][:80]}'")
    print(f"  Assigned genre: {row['genre_category']}")
    print(f"  Should be: Electronic")

# Check if vibe_description (the HUMAN question) is being used
print("\n\n2. Checking Use of Human-Sourced Descriptions")
print("-"*80)

unique_descs = df['vibe_description'].value_counts().head(10)
print(f"Total unique human requests: {df['vibe_description'].nunique()}")
print(f"\nTop 10 human requests:")
for desc, count in unique_descs.items():
    print(f"  '{desc[:60]}...' ({count} songs)")

# Check if recommendation_reasoning (HUMAN comments) preserved
print("\n\n3. Human Recommendation Context Preservation")
print("-"*80)

has_reasoning = df['recommendation_reasoning'].notna().sum()
print(f"Rows with human reasoning preserved: {has_reasoning}/{len(df)}")

sample = df.sample(5)
for idx, row in sample.iterrows():
    print(f"\nSong: {row['artist_name']} - {row['song_name']}")
    print(f"Human said: '{row['recommendation_reasoning'][:100]}...'")
    print(f"Categorized as: {row['vibe_category']} / {row['genre_category']}")

print("\n" + "="*80)
print("ISSUES FOUND:")
print("="*80)

# Find genre mismatches
electronic_keywords = ['synthwave', 'cyberpunk', 'electronic', 'edm', 'synth']
for kw in electronic_keywords:
    subset = df[df['vibe_description'].str.contains(kw, case=False, na=False)]
    if len(subset) > 0:
        wrong = subset[subset['genre_category'] != 'Electronic']
        if len(wrong) > 0:
            print(f"\n'{kw}' in description but not marked Electronic: {len(wrong)} songs")

print("\n" + "="*80)
