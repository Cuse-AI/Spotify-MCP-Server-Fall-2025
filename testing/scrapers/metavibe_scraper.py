"""
METAVIBE SCRAPER - Dedicated scraper for a single meta-vibe
Run 9 instances in parallel for balanced data collection!

Usage:
    python metavibe_scraper.py Chill
    python metavibe_scraper.py Dark
    python metavibe_scraper.py Drive
    ... etc

Each meta-vibe has its own:
    - Dedicated YouTube API key
    - Targeted Reddit queries
    - Output file
    - Checkpoint file
"""

import os
import sys
import json
import time
import re
import html
import praw
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv

# Load environment
load_dotenv()

# ============================================================================
# META-VIBE CONFIGURATION
# ============================================================================

METAVIBE_CONFIG = {
    "Chill": {
        "key_env": "YOUTUBE_API_KEY_CHILL",
        "subreddits": ["chillmusic", "listentothis", "Music", "spotify", "ifyoulikeblank"],
        "queries": [
            "chill music recommendation",
            "relaxing songs playlist",
            "calm music for studying",
            "peaceful songs suggestions",
            "mellow music vibes",
            "ambient chill songs",
            "lo-fi recommendations",
            "songs to relax to"
        ]
    },
    "Dark": {
        "key_env": "YOUTUBE_API_KEY_DARK",
        "subreddits": ["Metal", "goth", "darkwave", "Music", "ifyoulikeblank", "anxiety", "depression"],
        "queries": [
            "dark atmospheric music",
            "brooding songs recommendation",
            "music for dark mood",
            "haunting beautiful songs",
            "melancholic music suggestions",
            "dark ambient songs",
            "eerie music recommendation",
            "songs with dark vibes"
        ]
    },
    "Drive": {
        "key_env": "YOUTUBE_API_KEY_DRIVE",
        "subreddits": ["Music", "spotify", "ifyoulikeblank", "roadtrip", "Autos"],
        "queries": [
            "driving playlist songs",
            "road trip music recommendations",
            "night drive songs",
            "highway driving music",
            "songs for long drives",
            "cruising music vibes",
            "windows down music",
            "driving at night songs"
        ]
    },
    "Energy": {
        "key_env": "YOUTUBE_API_KEY_ENERGY",
        "subreddits": ["Music", "spotify", "ifyoulikeblank", "Fitness", "running", "workout"],
        "queries": [
            "pump up songs recommendation",
            "workout music playlist",
            "high energy songs",
            "hype music suggestions",
            "adrenaline rush songs",
            "intense workout music",
            "songs that get you pumped",
            "motivational gym songs"
        ]
    },
    "Happy": {
        "key_env": "YOUTUBE_API_KEY_HAPPY",
        "subreddits": ["Music", "spotify", "ifyoulikeblank", "CasualConversation", "happy"],
        "queries": [
            "songs that make me happy",
            "feel good music recommendations",
            "happy songs playlist",
            "upbeat cheerful songs",
            "songs that boost mood",
            "joyful music suggestions",
            "songs that make you smile",
            "happy vibes music"
        ]
    },
    "Night": {
        "key_env": "YOUTUBE_API_KEY_NIGHT",
        "subreddits": ["Music", "spotify", "ifyoulikeblank", "insomnia", "nightowls", "LateNightMusic"],
        "queries": [
            "late night music recommendations",
            "3am songs playlist",
            "songs for insomnia",
            "midnight vibes music",
            "cant sleep music",
            "nocturnal songs suggestions",
            "songs for overthinking at night",
            "after midnight playlist"
        ]
    },
    "Party": {
        "key_env": "YOUTUBE_API_KEY_PARTY",
        "subreddits": ["Music", "spotify", "ifyoulikeblank", "EDM", "DJs", "house"],
        "queries": [
            "party playlist songs",
            "dance music recommendations",
            "club bangers playlist",
            "songs for parties",
            "get the party started songs",
            "house party music",
            "dancing songs suggestions",
            "best party anthems"
        ]
    },
    "Sad": {
        "key_env": "YOUTUBE_API_KEY_SAD",
        "subreddits": ["Music", "spotify", "ifyoulikeblank", "depression", "GriefSupport", "BreakUps", "heartbreak"],
        "queries": [
            "sad songs recommendation",
            "songs that make me cry",
            "heartbreak playlist",
            "songs about loss",
            "music for grief",
            "depressing beautiful songs",
            "songs for broken heart",
            "crying songs playlist"
        ]
    },
    "Uplifting": {
        "key_env": "YOUTUBE_API_KEY_UPLIFTING",
        "subreddits": ["Music", "spotify", "ifyoulikeblank", "GetMotivated", "DecidingToBeBetter"],
        "queries": [
            "uplifting music recommendations",
            "inspiring songs playlist",
            "songs that give hope",
            "motivational music suggestions",
            "songs for new beginnings",
            "empowering songs",
            "music that lifts spirits",
            "songs about overcoming"
        ]
    }
}

# Video versions to try (official first, then lyrics for rescue)
VIDEO_VERSIONS = [
    ("official", "Official video"),
    ("lyrics", "Lyrics video - emotional comments gold!"),
]

# ============================================================================
# CHANNEL BLACKLIST
# ============================================================================

CHANNEL_BLACKLIST_PATTERNS = [
    r'relaxing', r'meditation', r'sleep', r'ambient.*music', r'study.*music',
    r'lofi.*girl', r'chilled.*cow', r'cafe.*music', r'jazz.*hop',
    r'peaceful', r'calming', r'soothing', r'healing', r'spa.*music',
    r'nature.*sounds', r'rain.*sounds', r'white.*noise', r'asmr',
    r'compilation', r'mix.*20\d\d', r'playlist', r'best.*of',
    r'top.*\d+', r'\d+.*hours?', r'non.*stop', r'continuous'
]

# ============================================================================
# COMMENT SCORER (Same as ULTIMATE scraper)
# ============================================================================

class CommentScorer:
    """Score YouTube comments for emotional quality."""
    
    SPAM_PATTERNS = [
        r'who.*here.*202\d', r'still.*listening.*202\d', r'anyone.*202\d',
        r'like if you', r'subscribe', r'first!', r'early squad',
        r'algorithm', r'notification', r'who.*watching'
    ]
    
    LYRIC_PATTERNS = [
        r'^[A-Z][^a-z]{20,}',  # ALL CAPS lines
        r'(.{10,})\n\1',       # Repeated lines (chorus)
    ]
    
    STORY_PATTERNS = [
        r'when i was', r'years ago', r'remember when', r'back when', r'back in'
    ]
    
    CAUSE_EFFECT_PATTERNS = [
        r'makes? me', r'helps? me', r'reminds? me', r'takes? me',
        r'got me through', r'saved me', r'changed my'
    ]
    
    TEMPORAL_PATTERNS = [
        r'used to', r'no longer', r'still to this day', r'after all these years',
        r'every time i hear', r'whenever i listen'
    ]
    
    LIFE_EVENT_PATTERNS = [
        r'break.?up', r'divorce', r'passed away', r'died', r'death',
        r'surgery', r'hospital', r'wedding', r'funeral', r'lost my',
        r'cancer', r'accident', r'suicide', r'depression', r'anxiety'
    ]
    
    EMOTIONAL_WORDS = [
        'cry', 'cried', 'tears', 'healing', 'anxiety', 'depression',
        'grief', 'comfort', 'pain', 'heart', 'soul', 'broke', 'broken',
        'saved', 'peace', 'hope', 'love', 'miss', 'remember'
    ]
    
    def score(self, text: str) -> Tuple[int, List[str]]:
        """Score a comment. Returns (score, list of reasons)."""
        if not text or len(text) < 30:
            return 0, []
        
        text_lower = text.lower()
        score = 0
        reasons = []
        
        # Reject spam
        for pattern in self.SPAM_PATTERNS:
            if re.search(pattern, text_lower):
                return 0, ['spam']
        
        # Reject lyric dumps
        for pattern in self.LYRIC_PATTERNS:
            if re.search(pattern, text):
                return 0, ['lyrics']
        
        # First person (+1)
        if re.search(r'\b(i|me|my|we|our)\b', text_lower):
            score += 1
            reasons.append('first_person')
        
        # Story context (+2)
        for pattern in self.STORY_PATTERNS:
            if re.search(pattern, text_lower):
                score += 2
                reasons.append('story')
                break
        
        # Cause/effect (+2)
        for pattern in self.CAUSE_EFFECT_PATTERNS:
            if re.search(pattern, text_lower):
                score += 2
                reasons.append('cause_effect')
                break
        
        # Temporal transformation (+2)
        for pattern in self.TEMPORAL_PATTERNS:
            if re.search(pattern, text_lower):
                score += 2
                reasons.append('temporal')
                break
        
        # Life events (+2)
        for pattern in self.LIFE_EVENT_PATTERNS:
            if re.search(pattern, text_lower):
                score += 2
                reasons.append('life_event')
                break
        
        # Emotional words (+1 each, max 2)
        emotional_count = 0
        for word in self.EMOTIONAL_WORDS:
            if word in text_lower:
                emotional_count += 1
        if emotional_count >= 2:
            score += 2
            reasons.append('emotional_2')
        elif emotional_count == 1:
            score += 1
            reasons.append('emotional_1')
        
        # Length bonus
        if len(text) > 200:
            score += 2
            reasons.append('great_length')
        elif len(text) > 100:
            score += 1
            reasons.append('good_length')
        
        return score, reasons


# ============================================================================
# SONG EXTRACTOR
# ============================================================================

class SongExtractor:
    """Extract artist/song from Reddit comments."""
    
    PATTERNS = [
        # "Song" by Artist
        r'"([^"]+)"\s+by\s+([^,\.\n]+)',
        r"'([^']+)'\s+by\s+([^,\.\n]+)",
        # Artist - Song
        r'([A-Z][^-\n]{1,30})\s*[-–—]\s*([^,\.\n]{2,40})',
        # Artist's "Song"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'s\s+[\"']([^\"']+)[\"']",
    ]
    
    def extract(self, text: str) -> List[Tuple[str, str]]:
        """Extract (artist, song) tuples from text."""
        results = []
        
        for pattern in self.PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 2:
                    # Pattern gives (song, artist) or (artist, song)
                    if 'by' in pattern:
                        song, artist = match
                    else:
                        artist, song = match
                    
                    # Clean up
                    artist = artist.strip().strip('"\'')
                    song = song.strip().strip('"\'')
                    
                    # Basic validation
                    if 2 < len(artist) < 50 and 2 < len(song) < 80:
                        results.append((artist, song))
        
        return results


# ============================================================================
# METAVIBE SCRAPER
# ============================================================================

class MetavibeScraper:
    """Scraper dedicated to a single meta-vibe."""
    
    def __init__(self, metavibe: str):
        if metavibe not in METAVIBE_CONFIG:
            raise ValueError(f"Unknown metavibe: {metavibe}. Valid: {list(METAVIBE_CONFIG.keys())}")
        
        self.metavibe = metavibe
        self.config = METAVIBE_CONFIG[metavibe]
        
        # Output directory - use the main data pipeline
        # Go up from testing/scrapers to project root, then into data/pipeline/1_raw
        project_root = Path(__file__).parent.parent.parent
        self.output_dir = project_root / "data" / "pipeline" / "1_raw"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize APIs
        self._init_reddit()
        self._init_spotify()
        self._init_youtube()
        
        # Helpers
        self.scorer = CommentScorer()
        self.extractor = SongExtractor()
        
        # Load existing songs to dedupe
        self.existing_songs = self._load_existing_songs()
        self.seen_songs = set(self.existing_songs)
        
        # Load checkpoint
        self.checkpoint_file = self.output_dir / f"checkpoint_{metavibe}.json"
        self.checkpoint = self._load_checkpoint()
        
        # Results and stats
        self.results = []
        self.stats = {
            'metavibe': metavibe,
            'reddit_comments': 0,
            'songs_extracted': 0,
            'spotify_validated': 0,
            'already_exists': 0,
            'youtube_searches': 0,
            'youtube_comments': 0,
            'quality_passed': 0,
            'rescued_by_lyrics': 0,
            'songs_saved': 0,
            'yt_quota_used': 0
        }
    
    def _init_reddit(self):
        """Initialize Reddit API."""
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'MetavibeScraper')
        )
        print(f"[REDDIT] Connected")
    
    def _init_spotify(self):
        """Initialize Spotify API."""
        self.spotify = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
        )
        print(f"[SPOTIFY] Connected")
    
    def _init_youtube(self):
        """Initialize YouTube API with dedicated key."""
        key_env = self.config['key_env']
        api_key = os.getenv(key_env)
        if not api_key:
            raise ValueError(f"Missing YouTube API key: {key_env}")
        
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        print(f"[YOUTUBE] Using key: {key_env}")
    
    def _load_existing_songs(self) -> set:
        """Load existing songs from all pipeline stages to avoid duplicates."""
        songs = set()
        project_root = Path(__file__).parent.parent.parent
        
        # Check all pipeline stages (1_raw, 2_deduped, 3_analyzed, 4_ready)
        pipeline_dir = project_root / "data" / "pipeline"
        for stage in ["1_raw", "2_deduped", "3_analyzed", "4_ready"]:
            stage_dir = pipeline_dir / stage
            if stage_dir.exists():
                for file in stage_dir.glob("*.json"):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            for song in data.get('songs', []):
                                key = (song['artist'].lower(), song['song'].lower())
                                songs.add(key)
                    except:
                        pass
        
        print(f"[DEDUPE] Loaded {len(songs)} existing songs from pipeline")
        return songs
    
    def _load_checkpoint(self) -> dict:
        """Load checkpoint for resuming."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {'completed_queries': []}
    
    def _save_checkpoint(self):
        """Save checkpoint."""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f)
    
    def _is_blacklisted_channel(self, channel_name: str) -> bool:
        """Check if channel is blacklisted."""
        name_lower = channel_name.lower()
        for pattern in CHANNEL_BLACKLIST_PATTERNS:
            if re.search(pattern, name_lower):
                return True
        return False
    
    def validate_spotify(self, artist: str, song: str) -> Optional[Dict]:
        """Validate song exists on Spotify and get normalized info."""
        # Reject covers, tributes, karaoke versions
        REJECT_PATTERNS = ['tribute', 'cover', 'karaoke', 'in the style of', 'made famous']
        
        try:
            query = f"track:{song} artist:{artist}"
            results = self.spotify.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                
                # Check for cover/tribute in title or artist
                title_lower = track['name'].lower()
                artist_lower = track['artists'][0]['name'].lower()
                
                for pattern in REJECT_PATTERNS:
                    if pattern in title_lower or pattern in artist_lower:
                        return None  # Reject this match
                
                return {
                    'artist': track['artists'][0]['name'],
                    'song': track['name'],
                    'spotify_id': track['id'],
                    'spotify_uri': track['uri'],
                    'album': track['album']['name']
                }
        except Exception as e:
            pass
        return None
    
    def search_youtube(self, artist: str, song: str, version: str = "official") -> Optional[Dict]:
        """Search YouTube for a specific version of a song."""
        try:
            query = f"{artist} {song} {version}"
            
            response = self.youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=5,
                videoCategoryId='10'  # Music category
            ).execute()
            
            self.stats['youtube_searches'] += 1
            self.stats['yt_quota_used'] += 100
            
            for item in response.get('items', []):
                channel = item['snippet']['channelTitle']
                if self._is_blacklisted_channel(channel):
                    continue
                
                title = html.unescape(item['snippet']['title'])
                # Basic check that it's the right song
                if artist.lower().split()[0] in title.lower() or song.lower().split()[0] in title.lower():
                    return {
                        'video_id': item['id']['videoId'],
                        'title': title,
                        'channel': channel,
                        'version': version
                    }
        except Exception as e:
            if 'quotaExceeded' in str(e):
                print(f"\n[QUOTA EXCEEDED] YouTube API key exhausted!")
                raise
        return None
    
    def get_quality_comment(self, video_id: str, min_score: int = 6) -> Optional[Dict]:
        """Get a quality emotional comment from a video."""
        try:
            response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=50,
                order='relevance'
            ).execute()
            
            self.stats['youtube_comments'] += 1
            self.stats['yt_quota_used'] += 1
            
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                text = html.unescape(comment['textDisplay'])
                
                score, reasons = self.scorer.score(text)
                if score >= min_score:
                    return {
                        'text': text[:500],
                        'score': score,
                        'reasons': reasons
                    }
        except Exception as e:
            pass
        return None
    
    def search_with_fallback(self, artist: str, song: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Try official, then lyrics version."""
        for version, desc in VIDEO_VERSIONS:
            video = self.search_youtube(artist, song, version)
            if not video:
                continue
            
            comment = self.get_quality_comment(video['video_id'])
            if comment:
                if version != "official":
                    self.stats['rescued_by_lyrics'] += 1
                    print(f"      [RESCUED by {version}!]")
                return video, comment
            
            time.sleep(0.2)
        
        return None, None
    
    def scrape(self, target: int = 50, max_quota: int = 8000):
        """Main scraping loop."""
        print(f"\n{'='*70}")
        print(f"METAVIBE SCRAPER: {self.metavibe}")
        print(f"Target: {target} songs | Max quota: {max_quota}")
        print(f"Queries: {len(self.config['queries'])} | Subreddits: {len(self.config['subreddits'])}")
        print(f"{'='*70}\n")
        
        completed = set(self.checkpoint.get('completed_queries', []))
        
        for query in self.config['queries']:
            if len(self.results) >= target:
                print(f"\n[TARGET REACHED: {target} songs]")
                break
            
            if self.stats['yt_quota_used'] >= max_quota:
                print(f"\n[QUOTA LIMIT: {self.stats['yt_quota_used']} units]")
                break
            
            if query in completed:
                print(f"[SKIP] {query}")
                continue
            
            print(f"\n[Query: '{query}']")
            
            try:
                for subreddit_name in self.config['subreddits']:
                    if len(self.results) >= target or self.stats['yt_quota_used'] >= max_quota:
                        break
                    
                    try:
                        subreddit = self.reddit.subreddit(subreddit_name)
                        
                        for post in subreddit.search(query, limit=10, time_filter='all'):
                            if len(self.results) >= target or self.stats['yt_quota_used'] >= max_quota:
                                break
                            
                            # Process post and comments
                            all_text = [post.selftext] if post.selftext else []
                            
                            try:
                                post.comments.replace_more(limit=0)
                                for comment in post.comments.list()[:20]:
                                    if hasattr(comment, 'body'):
                                        all_text.append(comment.body)
                                        self.stats['reddit_comments'] += 1
                            except:
                                pass
                            
                            for text in all_text:
                                extractions = self.extractor.extract(text)
                                
                                for artist, song in extractions:
                                    self.stats['songs_extracted'] += 1
                                    
                                    # Check if already have it
                                    key = (artist.lower(), song.lower())
                                    if key in self.seen_songs:
                                        self.stats['already_exists'] += 1
                                        continue
                                    
                                    # Validate on Spotify
                                    spotify_data = self.validate_spotify(artist, song)
                                    if not spotify_data:
                                        continue
                                    
                                    self.stats['spotify_validated'] += 1
                                    
                                    # Final dedupe with Spotify's names
                                    final_key = (spotify_data['artist'].lower(), spotify_data['song'].lower())
                                    if final_key in self.seen_songs:
                                        self.stats['already_exists'] += 1
                                        continue
                                    self.seen_songs.add(final_key)
                                    
                                    # Search YouTube with fallback
                                    video, comment = self.search_with_fallback(
                                        spotify_data['artist'],
                                        spotify_data['song']
                                    )
                                    
                                    if not video or not comment:
                                        continue
                                    
                                    self.stats['quality_passed'] += 1
                                    
                                    # Build result
                                    result = {
                                        'artist': spotify_data['artist'],
                                        'song': spotify_data['song'],
                                        'spotify_id': spotify_data['spotify_id'],
                                        'spotify_uri': spotify_data['spotify_uri'],
                                        'album': spotify_data['album'],
                                        'comment_text': comment['text'],
                                        'comment_score': comment['score'],
                                        'comment_reasons': comment['reasons'],
                                        'youtube_url': f"https://youtube.com/watch?v={video['video_id']}",
                                        'youtube_version': video['version'],
                                        'reddit_context': f"{post.title[:50]} | r/{subreddit_name}",
                                        'metavibe': self.metavibe,
                                        'data_source': 'metavibe_scraper',
                                        'scraped_at': datetime.now().isoformat(),
                                        '_needs_ananki_analysis': True
                                    }
                                    
                                    self.results.append(result)
                                    self.stats['songs_saved'] += 1
                                    
                                    print(f"  [Q{comment['score']}] {spotify_data['artist']} - {spotify_data['song']}")
                                    
                                    time.sleep(0.3)
                    
                    except Exception as e:
                        continue
                
                # Mark query complete
                completed.add(query)
                self.checkpoint['completed_queries'] = list(completed)
                self._save_checkpoint()
                
            except Exception as e:
                if 'quotaExceeded' in str(e):
                    break
                print(f"  [ERROR] {e}")
        
        return self.results
    
    def print_stats(self):
        """Print scraping statistics."""
        print(f"\n{'='*70}")
        print(f"STATISTICS: {self.metavibe}")
        print(f"{'='*70}")
        print(f"Reddit comments processed: {self.stats['reddit_comments']}")
        print(f"Songs extracted: {self.stats['songs_extracted']}")
        print(f"Validated on Spotify: {self.stats['spotify_validated']}")
        print(f"Already existed (skipped): {self.stats['already_exists']}")
        print(f"YouTube searches: {self.stats['youtube_searches']}")
        print(f"YouTube comment fetches: {self.stats['youtube_comments']}")
        print(f"Quality threshold passed: {self.stats['quality_passed']}")
        print(f"\n*** RESCUED BY LYRICS: {self.stats['rescued_by_lyrics']} songs ***")
        print(f"\nFINAL SONGS SAVED: {self.stats['songs_saved']}")
        print(f"YOUTUBE QUOTA USED: {self.stats['yt_quota_used']} units")
        
        if self.stats['songs_saved'] > 0:
            avg_cost = self.stats['yt_quota_used'] / self.stats['songs_saved']
            print(f"Average quota per song: {avg_cost:.0f} units")
    
    def save(self):
        """Save results to file."""
        if not self.results:
            print("\n[No songs to save]")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f"{self.metavibe}_{timestamp}.json"
        
        output = {
            'metavibe': self.metavibe,
            'scraped_at': datetime.now().isoformat(),
            'total_songs': len(self.results),
            'stats': self.stats,
            'songs': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(self.results)} songs to: {filename}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python metavibe_scraper.py <MetaVibe>")
        print(f"Valid meta-vibes: {', '.join(METAVIBE_CONFIG.keys())}")
        sys.exit(1)
    
    metavibe = sys.argv[1]
    
    # Optional arguments
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    max_quota = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
    
    print(f"\n{'='*70}")
    print(f"METAVIBE SCRAPER")
    print(f"Meta-vibe: {metavibe}")
    print(f"{'='*70}")
    
    scraper = MetavibeScraper(metavibe)
    results = scraper.scrape(target=target, max_quota=max_quota)
    scraper.print_stats()
    scraper.save()
    
    print("\n[DONE]")
