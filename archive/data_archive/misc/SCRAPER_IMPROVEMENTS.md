# Scraper Improvements to Reduce Duplicates

## Problem Identified:
YouTube scrapers have 37% duplicate rate because:
1. YouTube search returns same popular playlists for different queries
2. Scrapers don't pre-filter against tapestry before scraping
3. No search diversity (order, region, time)

## Solutions Implemented:

### 1. Pre-Filter Against Tapestry
Load all existing Spotify IDs from tapestry BEFORE scraping:
```python
from improved_search_utils import load_tapestry_spotify_ids

# In __init__:
self.existing_spotify_ids = load_tapestry_spotify_ids()

# In search_spotify:
if result['spotify_id'] in self.existing_spotify_ids:
    return None  # Skip songs already in tapestry
```

### 2. Add Search Diversity
Use different search parameters each run:
```python
from improved_search_utils import get_diverse_search_params

def search_playlists(self, query, max_results=10):
    params = get_diverse_search_params()

    request = self.youtube.search().list(
        part='snippet',
        q=query,
        type='playlist',
        maxResults=max_results,
        order=params['order'],  # Varies: relevance, date, viewCount, rating
        regionCode=params['regionCode']  # Varies by country
    )
```

### 3. Diversify Query Terms
Add modifiers to base queries:
```python
from improved_search_utils import diversify_queries

queries = [
    'party music playlist',
    'dance songs',
    # ... base queries
]

# This adds variations like:
# "party music playlist 2024"
# "underrated dance songs"
# "hidden gems party music"
queries = diversify_queries(queries)
```

### 4. Increase Playlist Variety Per Query
Instead of top 10, get top 20 but randomize which 10 we process:
```python
playlists = self.search_playlists(query, max_results=20)
random.shuffle(playlists)  # Randomize
playlists = playlists[:10]  # Process random 10
```

## Expected Impact:
- **Reduce duplicate rate from 37% to <15%**
- Find more unique, diverse content
- Better coverage of "hidden gem" playlists
- Regional diversity (international hits)

## How to Apply:

1. Add `import random` to scraper
2. Import from `improved_search_utils`
3. Add `self.existing_spotify_ids = load_tapestry_spotify_ids()` in `__init__`
4. Check against existing IDs in `search_spotify`
5. Use `diversify_queries()` on query list
6. Use `get_diverse_search_params()` in `search_playlists`
7. Randomize playlist selection

## Auto-Update Script:
Run `python fix_all_youtube_scrapers.py` to apply these changes to all 23 scrapers automatically.
