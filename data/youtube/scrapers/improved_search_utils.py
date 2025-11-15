"""
Improved search utilities to find MORE DIVERSE content
Reduces duplicate rate by adding search variety
"""

import json
from pathlib import Path
import random

def load_tapestry_spotify_ids():
    """Load all Spotify IDs from tapestry to avoid re-scraping"""
    tapestry_path = Path(__file__).parent.parent.parent / 'core' / 'tapestry.json'
    try:
        with open(tapestry_path, 'r', encoding='utf-8') as f:
            tapestry = json.load(f)

        spotify_ids = set()
        for vibe_data in tapestry['vibes'].values():
            for song in vibe_data['songs']:
                if 'spotify_id' in song:
                    spotify_ids.add(song['spotify_id'])

        print(f"[DIVERSITY] Loaded {len(spotify_ids)} existing songs from tapestry to skip")
        return spotify_ids
    except:
        return set()

def get_diverse_search_params():
    """Return diverse search parameters to find different playlists"""

    # Randomize search order to get different results each run
    orders = ['relevance', 'date', 'viewCount', 'rating']

    # Randomize time ranges to find different content
    time_ranges = ['2024', '2023', '2022', 'recent', 'new', 'best']

    # Regional diversity
    regions = ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'ES', 'JP', 'KR', 'BR']

    return {
        'order': random.choice(orders),
        'publishedAfter': None,  # Could add date ranges
        'regionCode': random.choice(regions)
    }

def diversify_queries(base_queries):
    """Add diversity modifiers to queries"""
    time_modifiers = ['2024', '2023', 'new', 'recent', 'best', 'top', 'latest', 'hidden gems']
    quality_modifiers = ['underrated', 'deep cuts', 'lesser known', 'indie', 'underground']

    diversified = list(base_queries)

    # Add time-based variations
    for query in base_queries[:5]:  # First 5 queries
        modifier = random.choice(time_modifiers)
        diversified.append(f"{query} {modifier}")

    # Add quality variations
    for query in base_queries[:3]:  # First 3 queries
        modifier = random.choice(quality_modifiers)
        diversified.append(f"{modifier} {query}")

    # Shuffle to randomize order
    random.shuffle(diversified)

    return diversified
