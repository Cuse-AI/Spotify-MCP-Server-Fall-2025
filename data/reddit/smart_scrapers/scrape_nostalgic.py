"""
Smart Scraper - NOSTALGIC Meta-Vibe
UPDATED: Nov 10, 2025 - Fixed extraction patterns to prevent false positives

Workflow: Scrape -> TRUE Ananki Analysis -> Inject to Tapestry
"""

import praw
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import re
import json
import time
from dotenv import load_dotenv
from pathlib import Path
from checkpoint_utils import CheckpointManager
# Import tapestry pre-filtering
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'youtube' / 'scrapers'))
from improved_search_utils import load_tapestry_spotify_ids
import random

load_dotenv()
load_dotenv(Path(__file__).parent.parent / '.env')

class NostalgicSmartScraper:
    def __init__(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
        )

        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )

        self.scraped_urls = set()
        
        # Pre-load tapestry to skip existing songs
        self.existing_spotify_ids = load_tapestry_spotify_ids()

    def is_music_comment(self, text):
        """Check if comment is actually about music"""
        text_lower = text.lower()
        music_indicators = [
            'song', 'track', 'album', 'artist', 'band',
            'listen', 'music', 'playlist'
        ]
        return any(word in text_lower for word in music_indicators)

    def find_music_mentions(self, text):
        """Find potential song mentions - more conservative patterns"""
        if not self.is_music_comment(text):
            return []

        candidates = []

        # Pattern 1: "Song Title" by Artist
        by_pattern = r'["\']([^"\']{3,60})["\']?\s+by\s+([A-Za-z][^\n,;]{2,40})(?:\.|,|\n|;|$)'
        by_matches = re.findall(by_pattern, text, re.IGNORECASE)
        candidates.extend([(f"{m[0].strip()} {m[1].strip()}", 'by_pattern') for m in by_matches])

        # Pattern 2: Artist - Song (both must start with capital)
        dash_pattern = r'([A-Z][A-Za-z\s&\',]{2,40})\s*[-–—]\s*([A-Z][^\n]{3,60}?)(?:\.|,|\n|;|$)'
        dash_matches = re.findall(dash_pattern, text)
        candidates.extend([(f"{m[1].strip()} {m[0].strip()}", 'dash') for m in dash_matches])

        # Pattern 3: Quoted titles (only if text contains music indicators)
        quoted = re.findall(r'"([A-Z][^"]{3,60})"', text)
        candidates.extend([(q.strip(), 'quoted') for q in quoted])

        return candidates

    def is_valid_track(self, track):
        """Validate Spotify result is actual music track"""
        try:
            # Check if it's a track type
            if track.get('type') != 'track':
                return False

            # Get artist info to filter out spoken word/podcasts
            artist_id = track['artists'][0]['id']
            artist_info = self.sp.artist(artist_id)

            # Filter out very obscure artists (likely false matches)
            if artist_info.get('popularity', 0) < 3:
                return False

            # Check genres for spoken word indicators
            genres = artist_info.get('genres', [])
            spoken_genres = ['spoken word', 'audiobook', 'podcast', 'comedy']
            if any(sg in ' '.join(genres).lower() for sg in spoken_genres):
                return False

            return True
        except:
            return True  # If we can't check, allow it (TRUE Ananki will catch false positives)

    def search_spotify(self, query_text):
        """Search Spotify with validation"""
        try:
            results = self.sp.search(q=query_text, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]

                # Skip if already in tapestry
                track_id = track['id']
                if track_id in self.existing_spotify_ids:
                    return None


                # Validate it's actually music
                if not self.is_valid_track(track):
                    return None

                return {
                    'artist': track['artists'][0]['name'],
                    'song': track['name'],
                    'spotify_id': track['id'],
                    'spotify_uri': track['uri'],
                    'query_used': query_text[:100]
                }
            return None
        except:
            return None

    def extract_from_comment(self, comment_text, source_url, score, post_title='', post_body=''):
        """Extract with full context"""
        candidates = self.find_music_mentions(comment_text)
        songs = []
        seen = set()

        for candidate_text, pattern_type in candidates:
            if len(candidate_text) > 100:
                continue

            result = self.search_spotify(candidate_text)

            if result:
                key = (result['artist'].lower(), result['song'].lower())
                if key not in seen:
                    seen.add(key)
                    songs.append({
                        **result,
                        'extraction_pattern': pattern_type,
                        'comment_score': score,
                        'source_url': source_url,
                        'post_title': post_title,
                        'comment_text': comment_text
                    })

            time.sleep(0.1)

        return songs

    def scrape_nostalgic_vibes(self, target_songs=1500):
        """Scrape Nostalgic with checkpointing"""
        cp = CheckpointManager('Nostalgic')
        
        """Continue scrape Nostalgic meta-vibe"""
        queries = [
            'nostalgic songs playlist',
            'childhood songs',
            '90s nostalgia music',
            '2000s throwback songs',
            'simpler times playlist',
            'teen years songs'
        ]

        # Using cp.all_results from checkpoint

        print("\n" + "="*70)
        print("SMART SCRAPING - NOSTALGIC VIBES")
        print("="*70)
        print(f"Target: {target_songs} songs")
        print("Workflow: Scrape -> TRUE Ananki -> Tapestry")
        print("="*70)

        for query in queries:
            print(f"\nQuery: '{query}'")

            for sub_name in ['musicsuggestions', 'ifyoulikeblank', 'Music', 'listentothis']:
                if len(cp.all_results) >= target_songs:
                    break

                try:
                    sub = self.reddit.subreddit(sub_name)
                    posts = sub.search(query, limit=20, time_filter='year')

                    for post in posts:
                        if len(cp.all_results) >= target_songs:
                            break

                        post_title = post.title
                        post_body = post.selftext if hasattr(post, 'selftext') else ''

                        post.comments.replace_more(limit=0)

                        for comment in post.comments.list()[:30]:
                            if len(cp.all_results) >= target_songs:
                                break

                            if hasattr(comment, 'body') and comment.score >= 1:
                                url = f'https://reddit.com{comment.permalink}'

                                if url in cp.scraped_urls:
                                    continue
                                cp.scraped_urls.add(url)

                                songs = self.extract_from_comment(
                                    comment.body, url, comment.score,
                                    post_title, post_body
                                )
                                cp.update_progress(songs)

                        time.sleep(1)

                except Exception as e:
                    error_msg = str(e)
                    # Check for Reddit rate limit
                    if 'rate' in error_msg.lower() or 'limit' in error_msg.lower():
                        print(f"  [RATE LIMIT] Hit Reddit API limit in r/{sub_name}")
                        print(f"  [STOPPING] Gracefully exiting with {len(cp.all_results)} songs")
                        print(f"  [NOTE] Checkpoint saved - can resume later!")
                        return cp.all_results  # Return what we have so far
                    print(f"  Error in r/{sub_name}: {e}")

            print(f"  Progress: {len(cp.all_results)} songs")

            if len(cp.all_results) >= target_songs:
                break

        # Deduplicate
        seen = set()
        unique = []
        for r in all_results:
            key = (r['artist'].lower(), r['song'].lower())
            if key not in seen:
                seen.add(key)
                unique.append(r)

        return unique[:target_songs]


if __name__ == '__main__':
    scraper = NostalgicSmartScraper()
    results = scraper.scrape_nostalgic_vibes(target_songs=1500)

    print(f"\n{'='*70}")
    print(f"SCRAPING COMPLETE!")
    print(f"{'='*70}")
    print(f"Total songs: {len(results)}")
    print(f"All validated with Spotify IDs!")

    output = Path('../test_results/nostalgic_smart_extraction.json')
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            'meta_vibe': 'Nostalgic',
            'total': len(results),
            'note': 'Ready for TRUE Ananki analysis',
            'songs': results
        }, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {output}")
    print("\nNext step: python true_ananki_claude_api.py test_results/nostalgic_smart_extraction.json")
