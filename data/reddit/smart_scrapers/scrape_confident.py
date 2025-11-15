"""
Smart Scraper - CONFIDENT Meta-Vibe
Created: Nov 10, 2025

Workflow: Scrape â†’ TRUE Ananki Analysis â†’ Inject to Tapestry
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

class ConfidentSmartScraper:
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
        text_lower = text.lower()
        music_indicators = ['song', 'track', 'album', 'artist', 'band', 'listen', 'music', 'playlist']
        return any(word in text_lower for word in music_indicators)

    def find_music_mentions(self, text):
        if not self.is_music_comment(text):
            return []
        candidates = []
        by_pattern = r'["\']([^"\']{3,60})["\']?\s+by\s+([A-Za-z][^\n,;]{2,40})(?:\.|,|\n|;|$)'
        by_matches = re.findall(by_pattern, text, re.IGNORECASE)
        candidates.extend([(f"{m[0].strip()} {m[1].strip()}", 'by_pattern') for m in by_matches])
        dash_pattern = r'([A-Z][A-Za-z\s&\',]{2,40})\s*[-â€“â€”]\s*([A-Z][^\n]{3,60}?)(?:\.|,|\n|;|$)'
        dash_matches = re.findall(dash_pattern, text)
        candidates.extend([(f"{m[1].strip()} {m[0].strip()}", 'dash') for m in dash_matches])
        quoted = re.findall(r'"([A-Z][^"]{3,60})"', text)
        candidates.extend([(q.strip(), 'quoted') for q in quoted])
        return candidates

    def is_valid_track(self, track):
        try:
            if track.get('type') != 'track':
                return False
            artist_id = track['artists'][0]['id']
            artist_info = self.sp.artist(artist_id)
            if artist_info.get('popularity', 0) < 3:
                return False
            genres = artist_info.get('genres', [])
            spoken_genres = ['spoken word', 'audiobook', 'podcast', 'comedy']
            if any(sg in ' '.join(genres).lower() for sg in spoken_genres):
                return False
            return True
        except:
            return True

    def search_spotify(self, query_text):
        try:
            results = self.sp.search(q=query_text, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]

                # Skip if already in tapestry
                track_id = track['id']
                if track_id in self.existing_spotify_ids:
                    return None

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

    def scrape_confident_vibes(self, target_songs=500):
        cp = CheckpointManager('Confident')
        queries = [
            'confident music playlist',
            'monotonous songs',
            'restless music',
            'waiting room music',
            'understimulated playlist',
            'songs for boring day'
        ]

        print("\n" + "="*70)
        print("SMART SCRAPING - CONFIDENT VIBES")
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
                                songs = self.extract_from_comment(comment.body, url, comment.score, post_title, post_body)
                                cp.update_progress(songs)
                        time.sleep(1)
                except Exception as e:
                    error_msg = str(e)
                    if 'rate' in error_msg.lower() or 'limit' in error_msg.lower():
                        print(f"  [RATE LIMIT] Hit Reddit API limit in r/{sub_name}")
                        print(f"  [STOPPING] Gracefully exiting with {len(cp.all_results)} songs")
                        print(f"  [NOTE] Checkpoint saved - can resume later!")
                        return cp.all_results
                    print(f"  Error in r/{sub_name}: {e}")
            if len(cp.all_results) >= target_songs:
                break
        output = Path('../test_results/confident_smart_extraction.json')
        results = cp.finalize(output, target_songs)
        return results

if __name__ == '__main__':
    scraper = ConfidentSmartScraper()
    results = scraper.scrape_confident_vibes(target_songs=500)
    print(f"\n{'='*70}")
    print(f"SCRAPING COMPLETE!")
    print(f"{'='*70}")
    print(f"Total unique songs: {len(results)}")
    print(f"\nSaved to: test_results/confident_smart_extraction.json")
    print("\nNext: python ../true_ananki_claude_api.py test_results/confident_smart_extraction.json")
