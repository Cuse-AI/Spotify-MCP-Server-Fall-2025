# -*- coding: utf-8 -*-
"""
MIDDEN TEST SCRAPER - Reddit
============================
A clean, quality-first scraper built from scratch.

Key principles:
1. Quality filtering AT THE SOURCE - bad data never saved
2. Target specific sub-vibes with targeted queries
3. Human checkpoint before Ananki (saves API credits)
4. Simple, readable, debuggable

Usage:
    python test_scraper.py

Output:
    testing/scrapers/reddit/output/[vibe]_scraped.json
    
Next step after running:
    Ask Claude to verify the output quality before Ananki analysis!
"""

import praw
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import re
import json
import time
import random
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from multiple possible locations
load_dotenv()
load_dotenv(Path(__file__).parent.parent.parent.parent / 'code' / 'web' / '.env')
load_dotenv(Path(__file__).parent.parent.parent.parent / 'data' / 'spotify' / '.env')

# Force UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class QualityFilter:
    """
    STRICT quality filter - rejects bad data BEFORE it enters our system.
    
    V2 TIGHTENED FILTERS:
    - Better list detection (newlines, bullets, numbered)
    - Require DEEPER emotional content (not just "reminds me")
    - Minimum word count for substance
    - Reject shallow "X reminds me of Y" without WHY
    """
    
    # Minimum/maximum comment length
    MIN_LENGTH = 50  # Raised from 30 - need more substance
    MAX_LENGTH = 500
    MIN_WORDS = 12   # NEW - need actual sentences, not fragments
    
    # URL patterns to reject
    URL_PATTERNS = ['http://', 'https://', 'www.', 'spotify.com', 'youtube.com', 
                    'youtu.be', 'open.spotify', 'soundcloud.com', '.com/watch',
                    '.com/track', '.com/playlist']
    
    # Generic phrases that don't provide emotional context
    GENERIC_PATTERNS = [
        r'^great song\.?!?$', r'^love this\.?!?$', r'^amazing\.?!?$',
        r'^this slaps\.?!?$', r'^banger\.?!?$', r'^fire\.?!?$',
        r'^masterpiece\.?!?$', r'^underrated\.?!?$',
        r'who.*listening.*202\d', r'anyone.*202\d',
        r'^same\.?!?$', r'^mood\.?!?$', r'^vibe\.?!?$',
    ]
    
    # Emotional indicators - DEEPER requirements
    # Need phrases that suggest actual reasoning, not just mentioning
    EMOTIONAL_PHRASES = [
        # WHY phrases - these explain the emotional connection
        'because', 'makes me feel', 'made me feel', 'helps me', 'helped me',
        'whenever i listen', 'every time i hear', 'when i hear this',
        'takes me back', 'transports me', 'brings me',
        'going through', 'went through', 'been through',
        'gets me through', 'got me through',
        'perfectly captures', 'captures the feeling', 'captures that',
        'this song is', 'this track is',  # Usually followed by explanation
        'i play this when', 'i listen to this when',
        'cry every time', 'tears every time', 'always makes me',
        'healing', 'therapeutic', 'cathartic',
        'relate to', 'resonates', 'speaks to me',
        'the lyrics', 'the melody', 'the way',  # Specific element discussion
        'love this because', 'love this song because',
        'perfect for when', 'great for when',
        'reminds me of when', 'reminds me of the time',  # Specific memory
    ]
    
    # SHALLOW phrases to reject - mention emotion but no depth
    SHALLOW_PATTERNS = [
        r'^[^.]{0,40}reminds me of [^.]{0,20}$',  # Just "X reminds me of Y" with nothing else
        r'^[^.]{0,30}great for [^.]{0,20}$',  # Just "great for X" 
        r'^check out\b', r'^try\b', r'^listen to\b',  # Just recommendations
        r'^my (go-?to|favorite)\b[^.]{0,30}$',  # "My go-to for X" with nothing else
    ]
    
    def __init__(self):
        self.stats = {
            'examined': 0,
            'passed': 0,
            'rejected_short': 0,
            'rejected_long': 0,
            'rejected_few_words': 0,
            'rejected_url': 0,
            'rejected_generic': 0,
            'rejected_list': 0,
            'rejected_shallow': 0,
            'rejected_no_emotion': 0,
        }
    
    def check(self, text: str) -> tuple[bool, str]:
        """
        Check if comment passes quality standards.
        Returns (passed, reason) - reason is 'ok' if passed, else rejection reason.
        
        V2: Much stricter - we want QUALITY over QUANTITY
        """
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
        
        # Word count check (NEW)
        word_count = len(text.split())
        if word_count < self.MIN_WORDS:
            self.stats['rejected_few_words'] += 1
            return False, 'few_words'
        
        # URL check
        if any(url in text_lower for url in self.URL_PATTERNS):
            self.stats['rejected_url'] += 1
            return False, 'has_url'
        
        # Generic phrase check
        for pattern in self.GENERIC_PATTERNS:
            if re.match(pattern, text_lower):
                self.stats['rejected_generic'] += 1
                return False, 'generic'
        
        # LIST FORMAT CHECK - MUCH STRICTER
        # Check for newline-separated lists
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 3:
            # If most lines look like song entries, reject
            song_pattern_lines = sum(1 for l in lines if re.search(r'[-–—]|by\s+[A-Z]', l))
            if song_pattern_lines >= len(lines) * 0.5:
                self.stats['rejected_list'] += 1
                return False, 'song_list'
        
        # Check for dash-separated entries (even without spaces)
        dash_count = len(re.findall(r'[A-Za-z][-–—][A-Za-z]', text))
        if dash_count >= 2:
            self.stats['rejected_list'] += 1
            return False, 'song_list'
        
        # Check for numbered or bulleted lists
        if re.search(r'^\s*[\d\.\)\-\*•]', text, re.MULTILINE):
            list_items = len(re.findall(r'^\s*[\d\.\)\-\*•]', text, re.MULTILINE))
            if list_items >= 3:
                self.stats['rejected_list'] += 1
                return False, 'song_list'
        
        # SHALLOW PATTERN CHECK (NEW)
        for pattern in self.SHALLOW_PATTERNS:
            if re.match(pattern, text_lower, re.IGNORECASE):
                self.stats['rejected_shallow'] += 1
                return False, 'shallow'
        
        # EMOTIONAL DEPTH CHECK - need meaningful phrases
        has_depth = any(phrase in text_lower for phrase in self.EMOTIONAL_PHRASES)
        if not has_depth:
            self.stats['rejected_no_emotion'] += 1
            return False, 'no_emotion'
        
        self.stats['passed'] += 1
        return True, 'ok'
    
    def print_stats(self):
        """Print filtering statistics"""
        print("\n" + "="*50)
        print("QUALITY FILTER STATS (V2 - STRICT)")
        print("="*50)
        total = self.stats['examined']
        passed = self.stats['passed']
        print(f"Examined: {total}")
        print(f"Passed:   {passed} ({passed/total*100:.1f}%)" if total > 0 else "Passed: 0")
        print(f"\nRejection breakdown:")
        rejection_order = ['rejected_short', 'rejected_long', 'rejected_few_words', 
                          'rejected_url', 'rejected_generic', 'rejected_list', 
                          'rejected_shallow', 'rejected_no_emotion']
        for key in rejection_order:
            val = self.stats.get(key, 0)
            if val > 0:
                label = key.replace('rejected_', '').replace('_', ' ')
                print(f"  {label}: {val}")



class TestScraper:
    """
    Clean test scraper for Reddit music recommendations.
    """
    
    def __init__(self):
        # Initialize Spotify
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
        )
        
        # Initialize Reddit
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'MiddenScraper/1.0')
        )
        
        # Quality filter
        self.quality = QualityFilter()
        
        # Track what we've seen
        self.seen_urls = set()
        self.seen_songs = set()  # (artist, title) tuples
        
        # Results
        self.results = []
    
    def search_spotify(self, query: str) -> dict | None:
        """Search Spotify for a track, return metadata if found."""
        try:
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
    
    def extract_song_mentions(self, text: str) -> list[str]:
        """Extract potential song mentions from text."""
        candidates = []
        
        # Pattern: "Song" by Artist
        by_matches = re.findall(r'"([^"]{3,50})"\s+by\s+([A-Za-z][^,.\n]{2,30})', text, re.IGNORECASE)
        for song, artist in by_matches:
            candidates.append(f"{song} {artist}")
        
        # Pattern: Artist - Song (both capitalized)
        dash_matches = re.findall(r'([A-Z][A-Za-z\s&\'\.]{2,30})\s*[-–—]\s*([A-Z][^\n,;]{3,50})', text)
        for artist, song in dash_matches:
            candidates.append(f"{song.strip()} {artist.strip()}")
        
        return candidates
    
    def scrape(self, config: dict, target: int = 50):
        """
        Main scraping function.
        
        config = {
            'name': 'Drive - Road Trip',
            'queries': ['road trip songs', 'driving music playlist', ...],
            'subreddits': ['musicsuggestions', 'ifyoulikeblank', ...]
        }
        """
        name = config['name']
        queries = config['queries']
        subreddits = config.get('subreddits', ['musicsuggestions', 'ifyoulikeblank', 'Music'])
        
        print("\n" + "="*70)
        print(f"SCRAPING: {name}")
        print("="*70)
        print(f"Target: {target} songs")
        print(f"Queries: {queries}")
        print(f"Subreddits: {subreddits}")
        print("="*70)
        
        for query in queries:
            if len(self.results) >= target:
                break
                
            print(f"\n[Query: '{query}']")
            
            for sub_name in subreddits:
                if len(self.results) >= target:
                    break
                
                print(f"  Searching r/{sub_name}...")
                
                try:
                    sub = self.reddit.subreddit(sub_name)
                    posts = list(sub.search(query, limit=15, time_filter='year'))
                    
                    for post in posts:
                        if len(self.results) >= target:
                            break
                        
                        # Get comments
                        post.comments.replace_more(limit=0)
                        comments = post.comments.list()[:25]
                        
                        for comment in comments:
                            if len(self.results) >= target:
                                break
                            
                            if not hasattr(comment, 'body'):
                                continue
                            
                            # Skip low-score comments
                            if comment.score < 2:
                                continue
                            
                            # Skip if we've seen this URL
                            url = f"https://reddit.com{comment.permalink}"
                            if url in self.seen_urls:
                                continue
                            self.seen_urls.add(url)
                            
                            # QUALITY CHECK - the key step!
                            passed, reason = self.quality.check(comment.body)
                            if not passed:
                                continue
                            
                            # Try to extract song mentions
                            mentions = self.extract_song_mentions(comment.body)
                            
                            for mention in mentions:
                                if len(self.results) >= target:
                                    break
                                
                                # Search Spotify
                                track = self.search_spotify(mention)
                                if not track:
                                    continue
                                
                                # Skip duplicates
                                song_key = (track['artist'].lower(), track['title'].lower())
                                if song_key in self.seen_songs:
                                    continue
                                self.seen_songs.add(song_key)
                                
                                # Build result
                                result = {
                                    'artist': track['artist'],
                                    'song': track['title'],
                                    'spotify_id': track['spotify_id'],
                                    'spotify_uri': track['spotify_uri'],
                                    'album': track['album'],
                                    'comment_text': comment.body[:400],
                                    'comment_score': comment.score,
                                    'post_title': post.title,
                                    'source_url': url,
                                    'target_vibe': name,
                                    'scraped_at': datetime.now().isoformat(),
                                }
                                
                                self.results.append(result)
                                print(f"    ✓ {track['artist']} - {track['title']}")
                        
                        time.sleep(0.5)  # Be nice to Reddit
                    
                except Exception as e:
                    if 'rate' in str(e).lower():
                        print(f"    [RATE LIMITED - stopping gracefully]")
                        return self.results
                    print(f"    [Error: {e}]")
                
                time.sleep(1)  # Between subreddits
        
        return self.results


    
    def save(self, filename: str = None):
        """Save results to JSON file."""
        output_dir = Path(__file__).parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_{timestamp}.json"
        
        output_path = output_dir / filename
        
        output_data = {
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
            print(f"📊 Score: {song['comment_score']} | Post: {song['post_title'][:50]}...")


# =============================================================================
# SCRAPER CONFIGS - Define what to scrape
# =============================================================================

# Priority: Drive (weakest at 296 songs)
DRIVE_CONFIG = {
    'name': 'Drive',
    'queries': [
        'road trip songs playlist',
        'driving music playlist',
        'songs for long drives',
        'night drive music',
        'highway driving songs',
        'cruising music playlist',
        'car ride songs',
        'scenic drive music',
        'solo drive playlist',
        'windows down music'
    ],
    'subreddits': ['musicsuggestions', 'ifyoulikeblank', 'Music', 'listentothis', 'spotify']
}

# Party (335 songs)
PARTY_CONFIG = {
    'name': 'Party',
    'queries': [
        'party playlist songs',
        'pregame music playlist',
        'house party songs',
        'club music playlist',
        'dance party songs',
        'festival music vibes',
        'college party playlist',
        'get hyped songs'
    ],
    'subreddits': ['musicsuggestions', 'ifyoulikeblank', 'Music', 'EDM', 'hiphopheads']
}

# Night (394 songs)  
NIGHT_CONFIG = {
    'name': 'Night',
    'queries': [
        'late night music playlist',
        '3am songs playlist',
        'midnight music vibes',
        'cant sleep playlist',
        'introspective night music',
        'contemplative songs night',
        'alone at night music',
        'existential songs late night'
    ],
    'subreddits': ['musicsuggestions', 'ifyoulikeblank', 'Music', 'listentothis']
}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("="*70)
    print("MIDDEN TEST SCRAPER")
    print("="*70)
    print("\nThis scraper has QUALITY FILTERING built in.")
    print("Bad data is rejected BEFORE it enters our system.")
    print("\nAfter scraping, STOP and verify quality with Claude")
    print("before running Ananki analysis!")
    print("="*70)
    
    # Create scraper
    scraper = TestScraper()
    
    # Run with Drive config (our weakest meta-vibe)
    # Change to PARTY_CONFIG or NIGHT_CONFIG to target those
    results = scraper.scrape(DRIVE_CONFIG, target=30)
    
    # Show stats
    scraper.quality.print_stats()
    
    # Show samples for verification
    scraper.show_samples(5)
    
    # Save results
    scraper.save('drive_test_scrape.json')
    
    print("\n" + "="*70)
    print("NEXT STEP:")
    print("="*70)
    print("1. Check output/drive_test_scrape.json")
    print("2. Ask Claude to verify the comment quality")
    print("3. If quality is good, proceed to Ananki analysis")
    print("4. If quality is bad, adjust filters and re-run")
    print("="*70)
