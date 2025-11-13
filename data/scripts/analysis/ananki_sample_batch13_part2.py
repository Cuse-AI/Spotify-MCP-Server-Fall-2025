import pandas as pd
import random

df = pd.read_csv('reddit/reddit_batch13_part2_hopeful_excited_20251108_195309.csv')

vibes = df['vibe_sub_category'].unique()
for v in sorted(vibes):
    print(f'\n=== {v} ===')
    subset = df[df['vibe_sub_category'] == v]
    samples = subset.sample(min(5, len(subset)))
    for _, row in samples.iterrows():
        artist = str(row['artist_name']).strip()
        song = str(row['song_name']).strip()
        reasoning = str(row['recommendation_reasoning'])[:100]
        print(f'  {artist} - {song}')
        if reasoning and reasoning != 'nan':
            print(f'    Context: {reasoning}...')
