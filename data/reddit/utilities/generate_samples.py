import pandas as pd

df = pd.read_csv('scraped_data/reddit_v5_training_20251107_174019.csv')

print('=== SAMPLE RECORDS (5 Representative Examples) ===\n')

# Get diverse samples (different relation types)
proximity_sample = df[df['relation_type'] == 'proximity'].sample(2)
contextual_sample = df[df['relation_type'] == 'contextual'].sample(2)
general_sample = df[df['relation_type'] == 'general'].sample(1)

samples = pd.concat([proximity_sample, contextual_sample, general_sample])

for i, (idx, row) in enumerate(samples.iterrows(), 1):
    print(f'\n--- SAMPLE {i} ---')
    print(f'Vibe Request: {row["vibe_request"][:200]}...')
    print(f'Song: {row["song_name"]} by {row["artist_name"]}')
    print(f'Relation Type: {row["relation_type"]}')

    if pd.notna(row["delta_description"]):
        print(f'Delta: {str(row["delta_description"])[:150]}...')
    else:
        print(f'Delta: None')

    if pd.notna(row["reasoning_text"]):
        print(f'Reasoning: {str(row["reasoning_text"])[:150]}...')
    else:
        print(f'Reasoning: None')

    if pd.notna(row['anchor_reference_artist']):
        anchor_song = row["anchor_reference_song"] if pd.notna(row["anchor_reference_song"]) else "(artist only)"
        print(f'Anchor: {row["anchor_reference_artist"]} - {anchor_song}')
    else:
        print(f'Anchor: None')

    print(f'Confidence: {row["extraction_confidence"]}')
    print(f'Method: {row["extraction_method"]}')
