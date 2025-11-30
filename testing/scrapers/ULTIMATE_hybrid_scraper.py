# -*- coding: utf-8 -*-
"""
ULTIMATE HYBRID SCRAPER v4
==========================
THE PERFECTED FLOW:
1. Reddit: Find comments where people recommend specific songs with emotional context
2. Extract: "Artist - Song" from the comment  
3. Spotify: Validate it's a real song (FREE API - no quota!)
4. Dedupe: Skip if already in tapestry (SAVES quota!)
5. YouTube: Search for the song - TRY MULTIPLE VERSIONS until we find good comments:
   - Official video
   - Lyrics video (often has the BEST emotional comments!)
   - Slowed + reverb (huge emotional community)
   - Acoustic version
   - Live performance
6. Get quality emotional comment (score >= 6)
7. Save with full context

KEY INSIGHT: We only spend extra quota when the first version fails.
Most songs cost 100 units. "Rescue missions" for difficult songs cost more
but SAVE songs that would otherwise be lost.

Run: python ULTIMATE_hybrid_scraper.py
"""

import os
import re
import json
import html
import time
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Set, Dict, List, Optional, Tuple

try:
    from dotenv import load_dotenv
    import praw
    from googleapiclient.discovery import build
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install python-dotenv praw google-api-python-client spotipy")
    sys.exit(1)

# Load environment variables from multiple locations
load_dotenv()
for parent in ['.', '..', '../..', '../../..']:
    env_path = Path(__file__).parent / parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class QuotaExhaustedError(Exception):
    """Raised when all YouTube API keys have exhausted their quota."""
    pass


# =============================================================================
# VIDEO VERSION STRATEGIES - Try multiple versions to find emotional comments
# =============================================================================

VIDEO_VERSIONS = [
    # Format: (suffix, description)
    ("official", "Official video"),
    ("lyrics", "Lyrics video - often has BEST emotional comments!"),
    ("slowed reverb", "Slowed + reverb - emotional community"),
    ("acoustic", "Acoustic version"),
    ("live", "Live performance"),
]


# =============================================================================
# YOUTUBE KEY MANAGER - Rotate keys when quota exhausted
# =============================================================================

class YouTubeKeyManager:
    """
    Manages multiple YouTube API keys with automatic rotation.
    When one key hits quota, automatically switches to the next.
    """
    
    def __init__(self):
        self.keys = []
        self.current_index = 0
        self.exhausted_keys = set()
        
        # Load all available keys
        key_names = ['YOUTUBE_API_KEY', 'YOUTUBE_API_KEY_2', 'YOUTUBE_API_KEY_3', 
                     'YOUTUBE_API_KEY_4', 'YOUTUBE_API_KEY_5']
        for name in key_names:
            key = os.getenv(name)
            if key:
                self.keys.append(key)
        
        if not self.keys:
            raise ValueError("No YouTube API keys found in environment!")
        
        print(f"[YT KEYS] Loaded {len(self.keys)} YouTube API keys")
        self._build_client()
    
    def _build_client(self):
        """Build YouTube client with current key."""
        self.client = build('youtube', 'v3', developerKey=self.keys[self.current_index])
    
    def get_client(self):
        """Get current YouTube client."""
        return self.client
    
    def rotate_key(self) -> bool:
        """
        Rotate to next available key.
        Returns True if rotation successful, False if all keys exhausted.
        """
        self.exhausted_keys.add(self.current_index)
        
        # Find next non-exhausted key
        for i in range(len(self.keys)):
            if i not in self.exhausted_keys:
                self.current_index = i
                self._build_client()
                print(f"\n[YT KEYS] Rotated to key #{i + 1} of {len(self.keys)}")
                return True
        
        print("\n[YT KEYS] ALL KEYS EXHAUSTED!")
        return False
    
    def handle_quota_error(self) -> bool:
        """
        Called when quota exceeded error occurs.
        Returns True if successfully rotated, False if all keys exhausted.
        """
        print(f"\n[YT KEYS] Key #{self.current_index + 1} quota exceeded!")
        return self.rotate_key()
    
    def keys_remaining(self) -> int:
        """Return number of non-exhausted keys."""
        return len(self.keys) - len(self.exhausted_keys)


# =============================================================================
# DEDUPLICATION - Load existing tapestry to avoid re-scraping
# =============================================================================

def load_existing_catalog(tapestry_path: str = None) -> Set[Tuple[str, str]]:
    """
    Load all existing songs from tapestry to avoid re-scraping.
    Returns set of (artist.lower(), song.lower()) tuples.
    """
    if tapestry_path is None:
        # Try multiple paths
        candidates = [
            Path(__file__).parent / '../../core/tapestry.json',
            Path(__file__).parent / '../../../core/tapestry.json',
            Path('core/tapestry.json'),
        ]
        for p in candidates:
            if p.exists():
                tapestry_path = str(p)
                break
    
    existing = set()
    try:
        with open(tapestry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for vibe_name, vibe_data in data.get('vibes', {}).items():
            for song in vibe_data.get('songs', []):
                artist = song.get('artist', '').lower().strip()
                title = song.get('song', '').lower().strip()
                if artist and title:
                    existing.add((artist, title))
        
        print(f"[DEDUPE] Loaded {len(existing)} existing songs from tapestry")
    except Exception as e:
        print(f"[WARNING] Could not load tapestry: {e}")
    
    return existing


# =============================================================================
# CHECKPOINT - Resume between runs
# =============================================================================

CHECKPOINT_FILE = Path(__file__).parent / 'output' / 'ultimate_checkpoint.json'

def load_checkpoint() -> Dict:
    """Load scraping progress from checkpoint file."""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "completed_queries": [],
        "processed_songs": [],
        "last_run": None,
        "total_songs_collected": 0
    }

def save_checkpoint(data: Dict):
    """Save scraping progress to checkpoint file."""
    CHECKPOINT_FILE.parent.mkdir(exist_ok=True)
    data["last_run"] = datetime.now().isoformat()
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# =============================================================================
# CHANNEL BLACKLIST - Skip ambient/soundscape channels
# =============================================================================

class ChannelBlacklist:
    """Channels that produce ambient soundscapes, not real songs."""
    
    PATTERNS = [
        r'relaxing', r'ambient', r'sleep\s*music', r'meditation',
        r'lofi\s*(hip\s*hop|beats)', r'chill\s*beats', r'calming',
        r'soothing', r'healing', r'peaceful', r'nature\s*sounds',
        r'rain\s*sounds', r'white\s*noise', r'asmr', r'\d+\s*hours?',
        r'background\s*music', r'focus\s*music', r'spa\s*music',
        r'yoga', r'massage', r'chillout\s*lounge', r'study\s*music',
        r'compilation', r'mix\s*20\d\d', r'sensory', r'4k\s*relax',
    ]
    
    EXACT = [
        'Chillhop Music', 'Lofi Girl', 'Yellow Brick Cinema',
        'Soothing Relaxation', 'Meditation Relax Music',
    ]
    
    @classmethod
    def is_blocked(cls, channel_name: str) -> bool:
        if not channel_name:
            return True
        name = channel_name.lower()
        if channel_name in cls.EXACT:
            return True
        return any(re.search(p, name, re.I) for p in cls.PATTERNS)


# =============================================================================
# COMMENT QUALITY SCORER - Using v2 classifier patterns
# =============================================================================

class CommentScorer:
    """Score comments for emotional quality. Threshold: score >= 6."""
    
    SPAM = [
        r'who.*here.*202\d', r'still.*listening', r'like if you',
        r'subscribe', r'first!', r'early squad', r'algorithm',
        r'anyone.*202\d', r'notification', r'who.*watching',
    ]
    
    # Lyric dump detection (from v2 classifier)
    LYRIC_PATTERNS = [
        r'^[A-Z][^.!?]*\n[A-Z][^.!?]*\n[A-Z][^.!?]*',  # Multiple capitalized lines
        r'(\b\w+\b)\s+\1\s+\1',  # Repeated words (chorus)
    ]
    
    @classmethod
    def score(cls, text: str) -> Tuple[int, List[str]]:
        """Score a comment. Returns (score, reasons)."""
        if not text or len(text) < 40:
            return 0, []
        
        # Decode HTML entities
        text = html.unescape(text)
        text_lower = text.lower()
        
        # Reject spam
        for p in cls.SPAM:
            if re.search(p, text_lower):
                return 0, ['spam']
        
        # Reject lyric dumps
        for p in cls.LYRIC_PATTERNS:
            if re.search(p, text, re.MULTILINE):
                return 0, ['lyric_dump']
        
        score = 0
        reasons = []
        
        # First person (+1)
        if re.search(r'\b(i|me|my|we|our)\b', text_lower):
            score += 1
            reasons.append('first_person')
        
        # Story context (+2)
        if re.search(r'(when i was|years ago|remember when|back when|back in)', text_lower):
            score += 2
            reasons.append('story')
        
        # Cause/effect - THE KEY PATTERN (+2)
        if re.search(r'(makes? me|helps? me|reminds? me|takes? me|got me through|saved me)', text_lower):
            score += 2
            reasons.append('cause_effect')
        
        # Temporal transformation (+2) - from v2 classifier
        if re.search(r'(used to|no longer|still to this day|after all these years)', text_lower):
            score += 2
            reasons.append('temporal')
        
        # Emotional words (+1 each, max 2)
        emotional = ['cry', 'cried', 'tears', 'healing', 'anxiety', 
                     'depression', 'grief', 'comfort', 'pain', 'heart', 'soul',
                     'broke', 'broken', 'saved', 'peace']
        matches = sum(1 for w in emotional if w in text_lower)
        if matches:
            score += min(matches, 2)
            reasons.append(f'emotional_{matches}')
        
        # Life events (+2)
        if re.search(r'(break.?up|divorce|passed away|died|death|surgery|hospital|wedding|funeral|lost my)', text_lower):
            score += 2
            reasons.append('life_event')
        
        # Action statements (+1) - from v2 classifier
        if re.search(r'(i (always|never|used to) (play|listen|hear))', text_lower):
            score += 1
            reasons.append('action')
        
        # Length bonus
        if len(text) > 200:
            score += 2
            reasons.append('great_length')
        elif len(text) > 100:
            score += 1
            reasons.append('good_length')
        
        return score, reasons


# =============================================================================
# SONG EXTRACTOR - Find "Artist - Song" mentions in Reddit comments
# =============================================================================

class SongExtractor:
    """Extract song mentions from Reddit comments."""
    
    @staticmethod
    def extract(text: str) -> List[Tuple[str, str]]:
        """
        Extract (artist, song) pairs from text.
        Returns list of tuples ready for Spotify validation.
        """
        results = []
        
        # Decode HTML entities first
        text = html.unescape(text)
        
        # Pattern 1: "Song Title" by Artist
        by_matches = re.findall(
            r'["\']([^"\']{3,50})["\']?\s+by\s+([A-Za-z][^,.\n]{2,30})',
            text, re.IGNORECASE
        )
        for song, artist in by_matches:
            results.append((artist.strip(), song.strip()))
        
        # Pattern 2: Artist - Song (with various dashes)
        dash_matches = re.findall(
            r'([A-Z][A-Za-z\s&\'\.]{2,30})\s*[-–—]\s*([A-Z][^\n,;]{3,40})',
            text
        )
        for artist, song in dash_matches:
            # Clean up
            song = re.sub(r'\(.*?\)', '', song).strip()
            song = re.sub(r'\[.*?\]', '', song).strip()
            if len(artist) > 2 and len(song) > 2:
                results.append((artist.strip(), song.strip()))
        
        # Pattern 3: "Artist's Song Title" or Artist's "Song Title"
        possessive = re.findall(
            r"([A-Z][A-Za-z\s]{2,20})'s\s+[\"']?([A-Z][^\"'\n,]{3,30})[\"']?",
            text
        )
        for artist, song in possessive:
            results.append((artist.strip(), song.strip()))
        
        return results


# =============================================================================
# THE ULTIMATE HYBRID SCRAPER
# =============================================================================

class UltimateHybridScraper:
    """
    The PERFECTED hybrid scraping flow with multi-version fallback:
    
    1. Reddit: Find comments mentioning specific songs with emotional context
    2. Extract: Parse "Artist - Song" from the comment
    3. Spotify: Validate it's a real song (FREE - no quota!)
    4. Dedupe: Skip if already in tapestry
    5. YouTube: Try MULTIPLE VERSIONS until we find a quality comment:
       - Official → Lyrics → Slowed+Reverb → Acoustic → Live
       - STOP as soon as we find a good comment (save quota!)
    6. Save: Add to results with full context
    
    This approach RESCUES songs that would otherwise be lost because the
    official video had comments disabled or no emotional content.
    """
    
    # Reddit subreddits with quality emotional discussions
    SUBREDDITS = [
        'depression', 'anxiety', 'mentalhealth',  # High emotional signal
        'ifyoulikeblank', 'musicsuggestions',     # Music recommendations
        'Music', 'spotify', 'listentothis',       # General music
        'BreakUps', 'heartbreak', 'GriefSupport', # Life situations
        'CasualConversation', 'offmychest',       # Organic mentions
    ]
    
    # Search queries that find REAL SONG recommendations
    QUERIES = [
        # Sad/Emotional (highest quality)
        'song that made me cry', 'music helped my depression',
        'song for heartbreak', 'songs about grief', 'songs about loss',
        'song that hits different', 'underrated sad songs',
        
        # Healing
        'song that helped me heal', 'music for anxiety',
        'therapeutic songs', 'songs that comfort me',
        
        # Night/Introspective
        'songs for 3am', 'late night songs', 'songs when cant sleep',
        'introspective songs', 'songs for overthinking',
        
        # Drive
        'driving songs', 'road trip songs', 'night drive songs',
        
        # Energy
        'songs that hype me up', 'pump up songs', 'confidence songs',
        
        # Happy/Uplifting
        'songs that make me happy', 'feel good songs', 'songs for good mood',
        
        # Nostalgia
        'nostalgic songs', 'songs from childhood', 'songs that take me back',
    ]

    
    def __init__(self):
        # Initialize Reddit (FREE - generous limits)
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'UltimateHybridScraper/4.0')
        )
        
        # Initialize Spotify (FREE - no quota!)
        self.spotify = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
        )
        
        # Initialize YouTube with KEY MANAGER (handles rotation!)
        self.yt_manager = YouTubeKeyManager()
        self.youtube = self.yt_manager.get_client()
        
        # Load existing songs to skip
        self.existing_catalog = load_existing_catalog()
        
        # Load checkpoint
        self.checkpoint = load_checkpoint()
        
        # Tracking
        self.seen_songs = set(self.existing_catalog)  # Pre-populate with existing!
        self.results = []
        
        # Stats
        self.stats = {
            'reddit_comments': 0,
            'songs_extracted': 0,
            'spotify_validated': 0,
            'already_in_tapestry': 0,
            'youtube_searches': 0,
            'youtube_comments': 0,
            'rescued_by_fallback': 0,  # Songs saved by trying alternate versions
            'quality_passed': 0,
            'songs_saved': 0,
            'yt_quota_used': 0,
        }
        
        print(f"\n{'='*70}")
        print("ULTIMATE HYBRID SCRAPER v4")
        print("Now with multi-version fallback (lyrics, slowed+reverb, etc.)")
        print(f"{'='*70}")
        print(f"Pre-loaded {len(self.existing_catalog)} songs from tapestry (will skip)")
        print(f"Checkpoint: {len(self.checkpoint.get('completed_queries', []))} queries already done")
    
    def validate_spotify(self, artist: str, song: str) -> Optional[Dict]:
        """Validate song on Spotify. FREE API - no quota!"""
        try:
            query = f"track:{song} artist:{artist}"
            results = self.spotify.search(q=query, type='track', limit=3)
            if results['tracks']['items']:
                # Find best match
                for track in results['tracks']['items']:
                    track_artist = track['artists'][0]['name'].lower()
                    track_name = track['name'].lower()
                    # Loose matching
                    if (artist.lower() in track_artist or track_artist in artist.lower()) and \
                       (song.lower()[:10] in track_name or track_name[:10] in song.lower()):
                        return {
                            'spotify_id': track['id'],
                            'spotify_uri': track['uri'],
                            'artist': track['artists'][0]['name'],
                            'song': track['name'],
                            'album': track['album']['name'],
                        }
                # Fall back to first result if no good match
                track = results['tracks']['items'][0]
                return {
                    'spotify_id': track['id'],
                    'spotify_uri': track['uri'],
                    'artist': track['artists'][0]['name'],
                    'song': track['name'],
                    'album': track['album']['name'],
                }
        except Exception as e:
            pass
        return None

    def _youtube_search(self, query: str) -> Optional[Dict]:
        """
        Single YouTube search. Returns video info or None.
        Cost: 100 units
        """
        self.stats['youtube_searches'] += 1
        self.stats['yt_quota_used'] += 100
        
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                videoCategoryId='10',  # Music
                maxResults=3
            )
            response = request.execute()
            
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                channel = item['snippet']['channelTitle']
                
                # Skip blacklisted channels
                if ChannelBlacklist.is_blocked(channel):
                    continue
                
                return {
                    'video_id': video_id,
                    'title': title,
                    'channel': channel,
                }
            
        except Exception as e:
            if 'quotaExceeded' in str(e):
                if self.yt_manager.handle_quota_error():
                    self.youtube = self.yt_manager.get_client()
                    return self._youtube_search(query)  # Retry with new key
                else:
                    raise QuotaExhaustedError("All YouTube API keys exhausted!")
            print(f"    [YouTube search error: {e}]")
        
        return None
    
    def _get_video_comments(self, video_id: str, min_score: int = 6) -> Optional[Dict]:
        """
        Get the best quality emotional comment from a video.
        Cost: 1 unit per call (cheap!)
        """
        self.stats['youtube_comments'] += 1
        self.stats['yt_quota_used'] += 1
        
        try:
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=50,
                order='relevance',
                textFormat='plainText'
            )
            response = request.execute()
            
            best = None
            best_score = 0
            
            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                text = snippet['textDisplay']
                likes = snippet['likeCount']
                
                score, reasons = CommentScorer.score(text)
                
                # Bonus for likes
                if likes > 100:
                    score += 1
                if likes > 1000:
                    score += 1
                
                if score >= min_score and score > best_score:
                    best_score = score
                    best = {
                        'text': text[:500],
                        'score': score,
                        'reasons': reasons,
                        'likes': likes,
                    }
            
            return best
            
        except Exception as e:
            if 'quotaExceeded' in str(e):
                if self.yt_manager.handle_quota_error():
                    self.youtube = self.yt_manager.get_client()
                    return self._get_video_comments(video_id, min_score)
                else:
                    raise QuotaExhaustedError("All YouTube API keys exhausted!")
            # Comments disabled is common, don't spam the log
            if 'commentsDisabled' not in str(e):
                print(f"    [Comment error: {e}]")
            return None

    def search_with_fallback(self, artist: str, song: str, min_score: int = 6) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Try multiple video versions until we find one with quality comments.
        
        Returns: (video_info, comment_data) or (None, None) if all fail
        
        This is the KEY INNOVATION: Instead of giving up when the official
        video has no good comments, we try lyrics, slowed+reverb, etc.
        """
        for version_suffix, version_desc in VIDEO_VERSIONS:
            query = f"{artist} {song} {version_suffix}"
            
            # Search for this version
            video = self._youtube_search(query)
            if not video:
                continue
            
            # Try to get quality comment
            comment = self._get_video_comments(video['video_id'], min_score)
            if comment:
                # SUCCESS! Found a quality comment
                if version_suffix != "official":
                    self.stats['rescued_by_fallback'] += 1
                    print(f"      [RESCUED by {version_suffix} version!]")
                
                video['version'] = version_suffix
                return video, comment
            
            # No good comment, try next version...
            time.sleep(0.2)
        
        # All versions failed
        return None, None

    def process_reddit_comment(self, comment, post_title: str, subreddit: str) -> List[Dict]:
        """Process a Reddit comment - extract songs and validate."""
        results = []
        
        if not hasattr(comment, 'body'):
            return results
        
        text = comment.body
        self.stats['reddit_comments'] += 1
        
        # Must have decent length
        if len(text) < 40:
            return results
        
        # Extract song mentions
        song_mentions = SongExtractor.extract(text)
        if not song_mentions:
            return results
        
        self.stats['songs_extracted'] += len(song_mentions)
        
        for artist, song in song_mentions:
            # Check if already in tapestry (SKIP - save quota!)
            song_key = (artist.lower().strip(), song.lower().strip())
            if song_key in self.seen_songs:
                self.stats['already_in_tapestry'] += 1
                continue
            
            # Validate on Spotify (FREE!)
            spotify_data = self.validate_spotify(artist, song)
            if not spotify_data:
                continue
            
            self.stats['spotify_validated'] += 1
            
            # Final dedupe check with Spotify's normalized names
            final_key = (spotify_data['artist'].lower(), spotify_data['song'].lower())
            if final_key in self.seen_songs:
                self.stats['already_in_tapestry'] += 1
                continue
            self.seen_songs.add(final_key)
            
            # Try to find YouTube video with quality comments
            # Uses fallback: official → lyrics → slowed → acoustic → live
            video, comment_data = self.search_with_fallback(
                spotify_data['artist'], 
                spotify_data['song']
            )
            
            if not video or not comment_data:
                continue
            
            self.stats['quality_passed'] += 1
            
            # SUCCESS! We have a quality song with emotional context
            result = {
                'artist': spotify_data['artist'],
                'song': spotify_data['song'],
                'spotify_id': spotify_data['spotify_id'],
                'spotify_uri': spotify_data['spotify_uri'],
                'album': spotify_data['album'],
                'comment_text': comment_data['text'],
                'comment_score': comment_data['score'],
                'comment_reasons': comment_data['reasons'],
                'youtube_url': f"https://youtube.com/watch?v={video['video_id']}",
                'youtube_version': video.get('version', 'official'),
                'reddit_context': f"{post_title} | r/{subreddit}",
                'data_source': 'ultimate_hybrid_v4',
                'scraped_at': datetime.now().isoformat(),
                '_needs_ananki_analysis': True,
            }
            
            results.append(result)
            self.stats['songs_saved'] += 1
            version_tag = f" [{video.get('version', 'official')}]" if video.get('version') != 'official' else ""
            print(f"  [Q{comment_data['score']}]{version_tag} {spotify_data['artist']} - {spotify_data['song']}")
        
        return results

    def scrape(self, target: int = 50, max_yt_quota: int = 5000):
        """
        Main scraping loop.
        
        Args:
            target: Number of songs to collect
            max_yt_quota: Stop when this much YT quota is used (default 5000 = 50%)
        """
        print(f"\nTarget: {target} songs | Max YT quota: {max_yt_quota} units")
        print(f"Video fallback enabled: official -> lyrics -> slowed -> acoustic -> live")
        print(f"{'='*70}\n")
        
        completed_queries = set(self.checkpoint.get('completed_queries', []))
        
        for query in self.QUERIES:
            if len(self.results) >= target:
                print(f"\n[TARGET REACHED: {target} songs]")
                break
            
            if self.stats['yt_quota_used'] >= max_yt_quota:
                print(f"\n[YT QUOTA LIMIT REACHED: {self.stats['yt_quota_used']} units]")
                break
            
            if query in completed_queries:
                print(f"[SKIP - already done] {query}")
                continue
            
            print(f"\n[Query: '{query}']")
            
            # Search across multiple subreddits
            for sub_name in random.sample(self.SUBREDDITS, min(5, len(self.SUBREDDITS))):
                if len(self.results) >= target:
                    break
                if self.stats['yt_quota_used'] >= max_yt_quota:
                    break
                
                try:
                    sub = self.reddit.subreddit(sub_name)
                    posts = list(sub.search(query, limit=10, time_filter='year'))
                    
                    for post in posts:
                        if len(self.results) >= target:
                            break
                        if self.stats['yt_quota_used'] >= max_yt_quota:
                            break
                        
                        # Get comments
                        post.comments.replace_more(limit=0)
                        comments = post.comments.list()[:30]
                        
                        for comment in comments:
                            if hasattr(comment, 'score') and comment.score < 2:
                                continue
                            
                            try:
                                new_songs = self.process_reddit_comment(
                                    comment, post.title, sub_name
                                )
                                self.results.extend(new_songs)
                            except QuotaExhaustedError:
                                print("\n[!] ALL YOUTUBE KEYS EXHAUSTED - stopping")
                                self._save_checkpoint(completed_queries)
                                return self.results
                            except Exception as e:
                                print(f"  [Error: {e}]")
                            
                            if len(self.results) >= target:
                                break
                        
                        time.sleep(0.3)
                    
                except QuotaExhaustedError:
                    print("\n[!] ALL YOUTUBE KEYS EXHAUSTED - stopping")
                    self._save_checkpoint(completed_queries)
                    return self.results
                except Exception as e:
                    if 'rate' in str(e).lower():
                        print(f"  [RATE LIMITED - waiting 60s]")
                        time.sleep(60)
                    else:
                        print(f"  [Error r/{sub_name}: {e}]")
                
                time.sleep(0.5)
            
            # Mark query complete
            completed_queries.add(query)
            self._save_checkpoint(completed_queries)
        
        return self.results
    
    def _save_checkpoint(self, completed_queries: set):
        """Save checkpoint with current progress."""
        self.checkpoint['completed_queries'] = list(completed_queries)
        self.checkpoint['total_songs_collected'] = len(self.results)
        save_checkpoint(self.checkpoint)

    def print_stats(self):
        """Print detailed statistics."""
        print(f"\n{'='*70}")
        print("SCRAPING STATISTICS")
        print(f"{'='*70}")
        print(f"Reddit comments processed: {self.stats['reddit_comments']}")
        print(f"Songs extracted from comments: {self.stats['songs_extracted']}")
        print(f"Validated on Spotify: {self.stats['spotify_validated']}")
        print(f"Already in tapestry (SKIPPED): {self.stats['already_in_tapestry']}")
        print(f"YouTube searches: {self.stats['youtube_searches']}")
        print(f"YouTube comment fetches: {self.stats['youtube_comments']}")
        print(f"Quality threshold passed: {self.stats['quality_passed']}")
        print(f"\n*** RESCUED BY FALLBACK: {self.stats['rescued_by_fallback']} songs ***")
        print(f"(These would have been LOST without multi-version search!)")
        print(f"\nFINAL SONGS SAVED: {self.stats['songs_saved']}")
        print(f"\nYOUTUBE API KEYS: {self.yt_manager.keys_remaining()}/{len(self.yt_manager.keys)} remaining")
        print(f"YOUTUBE QUOTA USED: {self.stats['yt_quota_used']} units (estimated)")
        
        if self.stats['spotify_validated'] > 0:
            efficiency = 100 * self.stats['songs_saved'] / self.stats['spotify_validated']
            print(f"Efficiency (saved/validated): {efficiency:.1f}%")
        
        if self.stats['songs_saved'] > 0:
            avg_cost = self.stats['yt_quota_used'] / self.stats['songs_saved']
            print(f"Average quota cost per song: {avg_cost:.0f} units")
    
    def save(self, filename: str = None):
        """Save results to JSON."""
        output_dir = Path(__file__).parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ultimate_hybrid_{timestamp}.json"
        
        output_path = output_dir / filename
        
        data = {
            'source': 'ultimate_hybrid_v4',
            'scraped_at': datetime.now().isoformat(),
            'total_songs': len(self.results),
            'stats': self.stats,
            'songs': self.results,
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(self.results)} songs to: {output_path}")
        return output_path


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("ULTIMATE HYBRID SCRAPER v4")
    print("Reddit -> Spotify -> YouTube (with multi-version fallback)")
    print("="*70)
    
    scraper = UltimateHybridScraper()
    
    # Start scraping
    # - target: how many songs to collect
    # - max_yt_quota: stop when this much YT quota used
    results = scraper.scrape(target=100, max_yt_quota=5000)
    
    scraper.print_stats()
    scraper.save()
    
    print("\n[DONE]")
