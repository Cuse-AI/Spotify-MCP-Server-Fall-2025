# -*- coding: utf-8 -*-
"""
MIDDEN TEST SCRAPER - YouTube
=============================
A clean, quality-first YouTube scraper built from scratch.

Key differences from Reddit:
- Song/artist comes from VIDEO TITLE (not comment extraction)
- Comments provide EMOTIONAL CONTEXT only
- Extra filters for YouTube-specific spam (timestamps, "who's here in 2024", etc.)

Usage:
    python test_scraper_yt.py

Output:
    testing/scrapers/youtube/output/[vibe]_youtube_scraped.json
    
Next step:
    Ask Claude to verify the output quality before Ananki analysis!
"""

import os
import re
import json
import time
import random
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()
load_dotenv(Path(__file__).parent.parent.parent.parent / 'code' / 'web' / '.env')

# Force UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class YouTubeQualityFilter:
    """
    Quality filter for YouTube comments - includes YouTube-specific spam patterns.
    """
    
    MIN_LENGTH = 30
    MAX_LENGTH = 500
    
    # URL patterns
    URL_PATTERNS = ['http://', 'https://', 'www.', 'spotify.com', 'youtube.com', 
                    'youtu.be', '.com/', 'bit.ly']
    
    # Generic phrases (same as Reddit)
    GENERIC_PATTERNS = [
        r'^great song\.?!?$', r'^love this\.?!?$', r'^amazing\.?!?$',
        r'^this slaps\.?!?$', r'^banger\.?!?$', r'^fire\.?!?$',
        r'^masterpiece\.?!?$', r'^underrated\.?!?$',
        r'^same\.?!?$', r'^mood\.?!?$', r'^vibe\.?!?$',
        r'^beautiful\.?!?$', r'^perfect\.?!?$', r'^legend\.?!?$',
    ]
    
    # YouTube-specific spam patterns
    YOUTUBE_SPAM_PATTERNS = [
        r'^\d+:\d+',                      # Timestamp "2:34" or "1:23:45"
        r'who.*here.*202\d',              # "who's here in 2024"
        r'who.*listening.*202\d',         # "who's listening in 2024"
        r'anyone.*202\d',                 # "anyone else 2024"
        r'still.*202\d',                  # "still listening 2024"
        r'algorithm brought me',          # Algorithm spam
        r'algorithm blessed',
        r'recommended.*brought',
        r'^first!*$',                     # "First!"
        r'like if you',                   # Engagement bait
        r'thumbs up if',
        r'subscribe',                     # Self-promo
        r'check out my',
        r'my channel',
        r'notification squad',
        r'early squad',
        r'before.*million',               # "here before 1 million"
        r'here before.*viral',
        r'i was here',
        r'goosebumps$',                   # Low-effort
        r'^chills\.?!?$',
        r'^wow\.?!?$',
        r'^damn\.?!?$',
    ]
    
    # Emoji-only patterns
    EMOJI_ONLY_PATTERN = r'^[\U0001F300-\U0001F9FF\s\.,!]+$'
    
    # Emotional indicators (same as Reddit)
    EMOTIONAL_WORDS = [
        'feel', 'felt', 'feeling', 'emotion',
        'helps me', 'helped me', 'makes me', 'made me',
        'reminds me', 'reminded', 'remember',
        'going through', 'went through', 'been through',
        'when i', 'whenever i',
        'cry', 'cried', 'tears',
        'healing', 'comfort', 'relate',
        'perfect for', 'great for',
        'this song', 'this track',
        'listened to this', 'listening to this',
        'discovered', 'found this',
        'got me through', 'getting me through',
        'soundtrack', 'life',
    ]
    
    def __init__(self):
        self.stats = {
            'examined': 0,
            'passed': 0,
            'rejected_short': 0,
            'rejected_long': 0,
            'rejected_url': 0,
            'rejected_generic': 0,
            'rejected_youtube_spam': 0,
            'rejected_emoji_only': 0,
            'rejected_no_emotion': 0,
        }
    
    def check(self, text: str) -> tuple[bool, str]:
        """Check if YouTube comment passes quality standards."""
        self.stats['examined'] += 1
        
        if not text:
            self.stats['rejected_short'] += 1
            return False, 'empty'
        
        text = text.strip()
        text_lower = text.lower()
        
        # Length check
        if len(text) < self.MIN_LENGTH:
            self.stats['rejected_short'] += 1
            return False, 'too_short'
        
        if len(text) > self.MAX_LENGTH:
            self.stats['rejected_long'] += 1
            return False, 'too_long'
        
        # URL check
        if any(url in text_lower for url in self.URL_PATTERNS):
            self.stats['rejected_url'] += 1
            return False, 'has_url'
        
        # Generic phrase check
        for pattern in self.GENERIC_PATTERNS:
            if re.match(pattern, text_lower):
                self.stats['rejected_generic'] += 1
                return False, 'generic'
        
        # YouTube-specific spam check
        for pattern in self.YOUTUBE_SPAM_PATTERNS:
            if re.search(pattern, text_lower):
                self.stats['rejected_youtube_spam'] += 1
                return False, 'youtube_spam'
        
        # Emoji-only check
        if re.match(self.EMOJI_ONLY_PATTERN, text):
            self.stats['rejected_emoji_only'] += 1
            return False, 'emoji_only'
        
        # Emotional content check
        has_emotion = any(word in text_lower for word in self.EMOTIONAL_WORDS)
        if not has_emotion:
            self.stats['rejected_no_emotion'] += 1
            return False, 'no_emotion'
        
        self.stats['passed'] += 1
        return True, 'ok'
    
    def print_stats(self):
        """Print filtering statistics."""
        print("\n" + "="*50)
        print("YOUTUBE QUALITY FILTER STATS")
        print("="*50)
        total = self.stats['examined']
        passed = self.stats['passed']
        print(f"Examined: {total}")
        print(f"Passed:   {passed} ({passed/total*100:.1f}%)" if total > 0 else "Passed: 0")
        print(f"\nRejection breakdown:")
        for key, val in self.stats.items():
            if key.startswith('rejected_') and val > 0:
                print(f"  {key.replace('rejected_', '')}: {val}")



class YouTubeTestScraper:
    """
    Clean test scraper for YouTube music comments.
    
    Strategy:
    1. Search for music videos matching vibe queries
    2. Extract song/artist from video title
    3. Get comments with emotional context
    4. Validate against Spotify
    """
    
    def __init__(self):
        # Initialize YouTube API
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY not found in environment!")
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Initialize Spotify
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
        )
        
        # Quality filter
        self.quality = YouTubeQualityFilter()
        
        # Track what we've seen
        self.seen_videos = set()
        self.seen_songs = set()
        
        # Results
        self.results = []
    
    def extract_song_from_title(self, title: str) -> tuple[str, str] | None:
        """
        Extract artist and song from YouTube video title.
        Common formats:
        - "Artist - Song"
        - "Artist - Song (Official Video)"
        - "Song by Artist"
        """
        # Clean up common suffixes
        clean_title = re.sub(r'\(Official.*?\)', '', title, flags=re.IGNORECASE)
        clean_title = re.sub(r'\(Music.*?\)', '', clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r'\(Lyric.*?\)', '', clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r'\(Audio.*?\)', '', clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r'\[.*?\]', '', clean_title)
        clean_title = re.sub(r'\|.*$', '', clean_title)
        clean_title = clean_title.strip()
        
        # Pattern 1: Artist - Song
        if ' - ' in clean_title:
            parts = clean_title.split(' - ', 1)
            if len(parts) == 2:
                artist = parts[0].strip()
                song = parts[1].strip()
                if len(artist) > 1 and len(song) > 1:
                    return (artist, song)
        
        # Pattern 2: "Song" by Artist
        by_match = re.search(r'^["\']?(.+?)["\']?\s+by\s+(.+)$', clean_title, re.IGNORECASE)
        if by_match:
            song = by_match.group(1).strip()
            artist = by_match.group(2).strip()
            if len(artist) > 1 and len(song) > 1:
                return (artist, song)
        
        return None
    
    def search_spotify(self, artist: str, song: str) -> dict | None:
        """Validate and get metadata from Spotify."""
        try:
            query = f"{song} {artist}"
            results = self.sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                return {
                    'spotify_id': track['id'],
                    'spotify_uri': track['uri'],
                    'title': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'popularity': track['popularity'],
                }
            return None
        except Exception as e:
            print(f"    [Spotify error: {e}]")
            return None
    
    def get_video_comments(self, video_id: str, max_comments: int = 50) -> list[dict]:
        """Get comments from a YouTube video."""
        comments = []
        try:
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(max_comments, 100),
                order='relevance',
                textFormat='plainText'
            )
            response = request.execute()
            
            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'text': snippet['textDisplay'],
                    'likes': snippet['likeCount'],
                    'author': snippet['authorDisplayName'],
                })
        except Exception as e:
            if 'commentsDisabled' in str(e):
                pass  # Comments disabled, skip silently
            else:
                print(f"    [Comment error: {e}]")
        
        return comments
    
    def search_videos(self, query: str, max_results: int = 10) -> list[dict]:
        """Search for music videos."""
        videos = []
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                videoCategoryId='10',  # Music category
                maxResults=max_results,
                order='relevance'
            )
            response = request.execute()
            
            for item in response.get('items', []):
                videos.append({
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'channel': item['snippet']['channelTitle'],
                })
        except Exception as e:
            print(f"    [Search error: {e}]")
        
        return videos


    
    def scrape(self, config: dict, target: int = 30):
        """
        Main scraping function.
        
        config = {
            'name': 'Drive',
            'queries': ['road trip songs', 'driving playlist', ...],
        }
        """
        name = config['name']
        queries = config['queries']
        
        print("\n" + "="*70)
        print(f"YOUTUBE SCRAPING: {name}")
        print("="*70)
        print(f"Target: {target} songs")
        print(f"Queries: {queries[:3]}...")
        print("="*70)
        
        for query in queries:
            if len(self.results) >= target:
                break
            
            print(f"\n[Query: '{query}']")
            
            # Search for videos
            videos = self.search_videos(query, max_results=15)
            print(f"  Found {len(videos)} videos")
            
            for video in videos:
                if len(self.results) >= target:
                    break
                
                video_id = video['video_id']
                
                # Skip if we've seen this video
                if video_id in self.seen_videos:
                    continue
                self.seen_videos.add(video_id)
                
                # Extract song from title
                song_info = self.extract_song_from_title(video['title'])
                if not song_info:
                    continue
                
                artist, song = song_info
                
                # Skip if we've seen this song
                song_key = (artist.lower(), song.lower())
                if song_key in self.seen_songs:
                    continue
                
                # Validate with Spotify
                track = self.search_spotify(artist, song)
                if not track:
                    continue
                
                # Update song key with Spotify's canonical names
                song_key = (track['artist'].lower(), track['title'].lower())
                if song_key in self.seen_songs:
                    continue
                self.seen_songs.add(song_key)
                
                # Get comments
                comments = self.get_video_comments(video_id, max_comments=30)
                
                # Find a quality comment
                best_comment = None
                for comment in comments:
                    passed, reason = self.quality.check(comment['text'])
                    if passed:
                        best_comment = comment
                        break
                
                if not best_comment:
                    continue
                
                # Build result
                result = {
                    'artist': track['artist'],
                    'song': track['title'],
                    'spotify_id': track['spotify_id'],
                    'spotify_uri': track['spotify_uri'],
                    'album': track['album'],
                    'comment_text': best_comment['text'][:400],
                    'comment_likes': best_comment['likes'],
                    'video_title': video['title'],
                    'video_id': video_id,
                    'source_url': f"https://youtube.com/watch?v={video_id}",
                    'target_vibe': name,
                    'scraped_at': datetime.now().isoformat(),
                }
                
                self.results.append(result)
                print(f"    ✓ {track['artist']} - {track['title']}")
                
                time.sleep(0.5)  # Be nice to YouTube API
            
            time.sleep(1)  # Between queries
        
        return self.results
    
    def save(self, filename: str = None):
        """Save results to JSON file."""
        output_dir = Path(__file__).parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_scraped_{timestamp}.json"
        
        output_path = output_dir / filename
        
        output_data = {
            'source': 'youtube',
            'scraped_at': datetime.now().isoformat(),
            'total_songs': len(self.results),
            'quality_stats': self.quality.stats,
            'songs': self.results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(self.results)} songs to: {output_path}")
        return output_path
    
    def show_samples(self, n: int = 5):
        """Show random samples for quality verification."""
        if not self.results:
            print("No results to show!")
            return
        
        samples = random.sample(self.results, min(n, len(self.results)))
        
        print("\n" + "="*70)
        print(f"SAMPLE OUTPUT ({n} random songs)")
        print("="*70)
        
        for i, song in enumerate(samples, 1):
            print(f"\n--- Sample {i} ---")
            print(f"🎵 {song['artist']} - {song['song']}")
            print(f"📝 Comment: {song['comment_text'][:150]}...")
            print(f"👍 Likes: {song['comment_likes']} | Video: {song['video_title'][:40]}...")


# =============================================================================
# SCRAPER CONFIGS - Same vibes as Reddit scraper
# =============================================================================

DRIVE_CONFIG = {
    'name': 'Drive',
    'queries': [
        'road trip playlist songs',
        'driving music best songs',
        'night drive playlist',
        'highway driving songs',
        'cruising music playlist',
        'windows down summer songs',
        'long drive playlist',
        'scenic drive music',
    ]
}

PARTY_CONFIG = {
    'name': 'Party',
    'queries': [
        'party playlist songs',
        'pregame music playlist',
        'house party songs best',
        'club bangers playlist',
        'dance party hits',
        'hype songs playlist',
        'turn up music',
        'college party songs',
    ]
}

NIGHT_CONFIG = {
    'name': 'Night',
    'queries': [
        'late night music playlist',
        '3am vibes songs',
        'midnight playlist',
        'cant sleep music',
        'late night drive songs',
        'after hours playlist',
        'night owl music',
        'contemplative night songs',
    ]
}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("="*70)
    print("MIDDEN TEST SCRAPER - YOUTUBE")
    print("="*70)
    print("\nThis scraper has QUALITY FILTERING built in.")
    print("YouTube-specific spam (timestamps, 'who's here 2024', etc.) is filtered.")
    print("\nAfter scraping, STOP and verify quality with Claude")
    print("before running Ananki analysis!")
    print("="*70)
    
    # Create scraper
    scraper = YouTubeTestScraper()
    
    # Run with Drive config (our weakest meta-vibe)
    results = scraper.scrape(DRIVE_CONFIG, target=30)
    
    # Show stats
    scraper.quality.print_stats()
    
    # Show samples for verification
    scraper.show_samples(5)
    
    # Save results
    scraper.save('drive_youtube_test.json')
    
    print("\n" + "="*70)
    print("NEXT STEP:")
    print("="*70)
    print("1. Check output/drive_youtube_test.json")
    print("2. Ask Claude to verify the comment quality")
    print("3. If quality is good, proceed to Ananki analysis")
    print("4. If quality is bad, adjust filters and re-run")
    print("="*70)
