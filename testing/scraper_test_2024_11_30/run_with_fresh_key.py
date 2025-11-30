"""Run scraper with fresh YouTube API key"""
import os, sys, json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")
sys.path.insert(0, str(project_root / "scrapers"))

from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from balanced_hybrid_scraper import BalancedHybridScraper, SUBVIBE_SEARCHES

# Use the fresh key
FRESH_KEY = "AIzaSyB8LGZNWegDI9vAzNWkXbvDfHAFpYHCDa8"

youtube = build('youtube', 'v3', developerKey=FRESH_KEY)
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
))

print("=" * 60)
print("SCRAPER RUN #2 - FRESH API KEY")
print("=" * 60)

# Create scraper with fresh YouTube client
scraper = BalancedHybridScraper(youtube_client=youtube, spotify_client=spotify)

# Run with 2 songs per vibe again
songs = scraper.run(songs_per_vibe=2, min_score=6)

# Save results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = Path(__file__).parent

songs_data = []
for song in songs:
    songs_data.append({
        "artist": song.artist,
        "song": song.song,
        "comment_text": song.comment_text,
        "comment_score": song.comment_score,
        "comment_reasons": song.comment_reasons,
        "youtube_url": song.youtube_url,
        "search_context": song.reddit_context,
        "spotify_id": song.spotify_id,
        "spotify_uri": song.spotify_uri,
        "data_source": song.data_source,
        "created_at": song.created_at,
        "_needs_ananki_analysis": True,
    })

raw_file = output_dir / f"RAW_hybrid_scraper_{timestamp}.json"
with open(raw_file, 'w', encoding='utf-8') as f:
    json.dump({
        "metadata": {
            "scraper": "balanced_hybrid_v1",
            "timestamp": timestamp,
            "songs_per_vibe_attempted": 2,
            "min_score": 6,
            "total_vibes": len(SUBVIBE_SEARCHES),
            "songs_collected": len(songs_data),
            "pipeline_stage": "RAW",
            "next_step": "Move to data/pipeline/1_raw/ then dedupe",
            "needs_ananki": True,
            "run_number": 2,
        },
        "songs": songs_data
    }, f, indent=2, ensure_ascii=False)

print(f"\nSaved: {raw_file.name}")
print(f"Songs collected: {len(songs_data)}")
