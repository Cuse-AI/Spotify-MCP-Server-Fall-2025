"""
TEST RUNNER FOR BALANCED HYBRID SCRAPER
=======================================
Outputs to testing folder with clear naming.
If results look good, move to data/pipeline/1_raw/

OUTPUT FILES:
- RAW_hybrid_scraper_YYYYMMDD_HHMMSS.json  → Raw song data (needs Ananki)
- STATS_hybrid_scraper_YYYYMMDD_HHMMSS.json → Run statistics

NEXT STEPS AFTER TEST:
1. Review RAW file - do comments look quality?
2. If good: move to data/pipeline/1_raw/
3. Run deduplication
4. Run Ananki analysis (maps to subvibes)
5. Inject to tapestry
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

# Load .env from project root
from dotenv import load_dotenv
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scrapers"))

from balanced_hybrid_scraper import BalancedHybridScraper, SUBVIBE_SEARCHES

def run_test(songs_per_vibe: int = 2, min_score: int = 6, output_dir: str = None):
    """
    Run a test scrape and save results with clear naming.
    
    Args:
        songs_per_vibe: Songs to attempt per vibe (default 2 for testing)
        min_score: Minimum comment quality score
        output_dir: Where to save results
    """
    
    if output_dir is None:
        output_dir = Path(__file__).parent
    else:
        output_dir = Path(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("=" * 60)
    print("BALANCED HYBRID SCRAPER - TEST RUN")
    print("=" * 60)
    print(f"Songs per vibe: {songs_per_vibe}")
    print(f"Total vibes: {len(SUBVIBE_SEARCHES)}")
    print(f"Min score: {min_score}")
    print(f"Output dir: {output_dir}")
    print("=" * 60)
    
    # Check for API clients
    youtube_client = None
    spotify_client = None
    
    # Try to set up YouTube client
    try:
        from googleapiclient.discovery import build
        yt_key = os.getenv("YOUTUBE_API_KEY")
        if yt_key:
            youtube_client = build('youtube', 'v3', developerKey=yt_key)
            print("YouTube API: Connected")
        else:
            print("YouTube API: No key found (set YOUTUBE_API_KEY)")
    except ImportError:
        print("YouTube API: google-api-python-client not installed")
    
    # Try to set up Spotify client
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if client_id and client_secret:
            spotify_client = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
            )
            print("Spotify API: Connected")
        else:
            print("Spotify API: No credentials found")
    except ImportError:
        print("Spotify API: spotipy not installed")
    
    print("=" * 60)
    
    if not youtube_client:
        print("\nERROR: Cannot run without YouTube API!")
        print("Set YOUTUBE_API_KEY environment variable")
        return None
    
    # Run scraper
    scraper = BalancedHybridScraper(
        youtube_client=youtube_client,
        spotify_client=spotify_client
    )
    
    songs = scraper.run(songs_per_vibe=songs_per_vibe, min_score=min_score)
    
    # Convert to serializable format
    songs_data = []
    for song in songs:
        songs_data.append({
            "artist": song.artist,
            "song": song.song,
            "comment_text": song.comment_text,
            "comment_score": song.comment_score,
            "comment_reasons": song.comment_reasons,
            "youtube_url": song.youtube_url,
            "search_context": song.reddit_context,  # Actually the search query used
            "spotify_id": song.spotify_id,
            "spotify_uri": song.spotify_uri,
            "data_source": song.data_source,
            "created_at": song.created_at,
            # NOTE: mapped_subvibe will be set by Ananki later!
            "_needs_ananki_analysis": True,
        })
    
    # Save RAW output
    raw_file = output_dir / f"RAW_hybrid_scraper_{timestamp}.json"
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "scraper": "balanced_hybrid_v1",
                "timestamp": timestamp,
                "songs_per_vibe_attempted": songs_per_vibe,
                "min_score": min_score,
                "total_vibes": len(SUBVIBE_SEARCHES),
                "songs_collected": len(songs_data),
                "pipeline_stage": "RAW",
                "next_step": "Move to data/pipeline/1_raw/ then dedupe",
                "needs_ananki": True,
            },
            "songs": songs_data
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved RAW data: {raw_file.name}")
    
    # Save stats
    stats_file = output_dir / f"STATS_hybrid_scraper_{timestamp}.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "config": {
                "songs_per_vibe": songs_per_vibe,
                "min_score": min_score,
                "total_vibes": len(SUBVIBE_SEARCHES),
            },
            "results": scraper.stats,
            "acceptance_rate": f"{(scraper.stats['songs_accepted'] / max(1, scraper.stats['songs_attempted'])) * 100:.1f}%",
            "output_file": str(raw_file.name),
        }, f, indent=2)
    
    print(f"Saved stats: {stats_file.name}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"Songs collected: {len(songs_data)}")
    print(f"Acceptance rate: {(scraper.stats['songs_accepted'] / max(1, scraper.stats['songs_attempted'])) * 100:.1f}%")
    print()
    print("NEXT STEPS:")
    print("1. Review RAW file - check comment quality")
    print("2. If good: move to data/pipeline/1_raw/")
    print("3. Run deduplication")
    print("4. Run Ananki analysis (expensive!)")
    print("5. Move to ready, inject to tapestry")
    print("=" * 60)
    
    return songs_data


if __name__ == "__main__":
    # Default test run - small batch
    run_test(songs_per_vibe=2, min_score=6)
