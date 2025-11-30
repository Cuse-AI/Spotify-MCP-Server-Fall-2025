"""
BALANCED HYBRID SCRAPER
=======================
Each run scrapes ALL 107 subvibes evenly.

Example: songs_per_vibe=3 → attempts 3 songs for each of 107 vibes = ~321 attempts
With ~35% acceptance rate → ~112 new quality songs per run, evenly distributed

FLOW:
  For each subvibe:
    1. Reddit: Find songs in emotional context for this vibe
    2. YouTube: Get emotional comment (score >= 6)
    3. If quality → add to tapestry
    4. Move to next subvibe
    
No vibe gets ahead of others. Perfect balance from day 1.
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BalancedHybridScraper")


# =============================================================================
# SUBVIBE SEARCH MAPPINGS - All 107 vibes with search terms
# =============================================================================

SUBVIBE_SEARCHES = {
    # === CHILL (16 subvibes) ===
    "Chill - Ambient": ["ambient music relaxing", "atmospheric background music"],
    "Chill - Beach/Summer": ["summer vibes playlist", "beach songs feeling"],
    "Chill - Evening": ["evening wind down music", "relaxing night songs"],
    "Chill - Gentle": ["gentle soft music", "tender calm songs"],
    "Chill - Jazz": ["chill jazz playlist", "smooth jazz relaxing"],
    "Chill - Lofi": ["lofi hip hop chill", "lofi beats studying"],
    "Chill - Meditative": ["meditation music peaceful", "mindfulness songs"],
    "Chill - Monotonous": ["repetitive calming music", "droning ambient"],
    "Chill - Morning Coffee": ["morning coffee playlist", "sunday morning songs"],
    "Chill - Quiet Reflection": ["quiet reflection music", "peaceful thinking songs"],
    "Chill - Rainy Day": ["rainy day playlist", "cozy rain music"],
    "Chill - Restless": ["restless calm music", "uneasy ambient"],
    "Chill - Serene": ["serene peaceful music", "tranquil songs"],
    "Chill - Sunday": ["lazy sunday playlist", "sunday afternoon music"],
    "Chill - Understimulated": ["understimulated music", "need stimulation playlist"],
    "Chill - Waiting": ["waiting room music", "patient calm songs"],
    
    # === DARK (12 subvibes) ===
    "Dark - Anxious Calming Anxiety": ["music helps my anxiety", "songs calm panic attacks"],
    "Dark - Anxious Existential Dread": ["existential dread music", "void staring songs"],
    "Dark - Anxious Nervous Energy": ["nervous energy playlist", "jittery anxious songs"],
    "Dark - Anxious Overwhelmed": ["overwhelmed music helps", "too much anxiety songs"],
    "Dark - Anxious Panic": ["panic attack music", "songs during panic"],
    "Dark - Apocalyptic": ["apocalyptic playlist", "end of world music"],
    "Dark - Betrayed": ["betrayal songs", "music feeling betrayed"],
    "Dark - Brooding": ["brooding dark music", "moody atmospheric songs"],
    "Dark - Gothic": ["gothic music playlist", "dark aesthetic songs"],
    "Dark - Haunting": ["haunting music", "eerie beautiful songs"],
    "Dark - Insecure": ["insecure feeling music", "self doubt songs"],
    "Dark - Noir": ["noir music playlist", "detective dark jazz"],
    "Dark - Resentful": ["resentment songs", "bitter angry music"],
    "Dark - Romantic Jealousy": ["jealousy songs", "envious love music"],
    "Dark - Villain Arc": ["villain arc playlist", "villain energy songs"],
    "Dark - Witchy": ["witchy playlist", "witch aesthetic music"],
    
    # === DRIVE (6 subvibes) ===
    "Drive - Alone": ["driving alone music", "solo car ride songs"],
    "Drive - City": ["city driving playlist", "urban night drive"],
    "Drive - Night Drive": ["night drive playlist", "midnight driving songs"],
    "Drive - Road Trip": ["road trip playlist", "long drive songs"],
    "Drive - Scenic": ["scenic drive music", "beautiful drive playlist"],
    "Drive - Speed": ["speeding playlist", "fast driving songs"],
    
    # === ENERGY (16 subvibes) ===
    "Energy - Adventure": ["adventure music epic", "exploration songs"],
    "Energy - Aggressive": ["aggressive music workout", "angry energy songs"],
    "Energy - Anticipation": ["anticipation building music", "exciting buildup songs"],
    "Energy - Bold": ["bold confident music", "fearless songs"],
    "Energy - Boss": ["boss music playlist", "feeling like boss songs"],
    "Energy - Cathartic Anger": ["angry music catharsis", "rage release songs"],
    "Energy - Confidence": ["confidence playlist", "songs make me confident"],
    "Energy - Frustrated": ["frustrated angry music", "venting songs"],
    "Energy - Overwhelming": ["overwhelming energy music", "intense songs"],
    "Energy - Powerful": ["powerful music playlist", "empowering songs"],
    "Energy - Pump Up": ["pump up playlist", "hype songs energy"],
    "Energy - Rage": ["rage music playlist", "pure anger songs"],
    "Energy - Running": ["running playlist", "jogging music motivation"],
    "Energy - Self-Assured": ["self assured music", "secure confident songs"],
    "Energy - Sports": ["sports hype playlist", "game day music"],
    "Energy - Unhinged": ["unhinged energy music", "chaotic songs"],
    "Energy - Unstoppable": ["unstoppable playlist", "nothing can stop me songs"],
    "Energy - Workout": ["workout playlist", "gym motivation music"],
    
    # === HAPPY (14 subvibes) ===
    "Happy - Carefree": ["carefree happy music", "no worries songs"],
    "Happy - Celebration": ["celebration playlist", "party happy songs"],
    "Happy - Childlike": ["childlike wonder music", "innocent happy songs"],
    "Happy - Content": ["content peaceful happy", "satisfied calm music"],
    "Happy - Euphoric": ["euphoric music playlist", "pure joy songs"],
    "Happy - Feel Good": ["feel good playlist", "songs make me happy"],
    "Happy - Fun": ["fun upbeat music", "playful happy songs"],
    "Happy - Healing": ["healing music recovery", "songs helped me heal"],
    "Happy - New Beginnings": ["new beginnings playlist", "fresh start songs"],
    "Happy - Optimistic": ["optimistic music hopeful", "positive outlook songs"],
    "Happy - Reflective Gratitude": ["gratitude music", "thankful reflection songs"],
    "Happy - Silly": ["silly goofy music", "funny happy songs"],
    "Happy - Sunshine": ["sunshine happy playlist", "bright cheerful songs"],
    "Happy - Warm Appreciation": ["warm appreciation music", "grateful love songs"],
    "Happy - Whimsical": ["whimsical music magical", "fairy tale songs"],
    
    # === NIGHT (12 subvibes) ===
    "Night - 3AM Thoughts": ["3am thoughts playlist", "late night overthinking songs"],
    "Night - City Nights": ["city nights music", "urban night playlist"],
    "Night - Contemplative": ["contemplative night music", "deep thinking songs"],
    "Night - Introspective Contemplative": ["introspective music thinking", "self reflection songs"],
    "Night - Introspective Growth": ["personal growth music", "becoming better songs"],
    "Night - Introspective Life Changes": ["life changes music", "transition period songs"],
    "Night - Introspective Philosophical": ["philosophical music", "meaning of life songs"],
    "Night - Introspective Questioning": ["questioning everything music", "doubt songs"],
    "Night - Introspective Self-Reflection": ["self reflection playlist", "looking inward songs"],
    "Night - Midnight Drive": ["midnight drive playlist", "late driving songs"],
    "Night - Sleep": ["sleep playlist", "falling asleep music"],
    
    # === PARTY (6 subvibes) ===
    "Party - Club": ["club music playlist", "nightclub songs"],
    "Party - College": ["college party playlist", "university party songs"],
    "Party - Dance": ["dance playlist", "dancing songs"],
    "Party - Festival": ["festival playlist", "music festival songs"],
    "Party - House Party": ["house party playlist", "party at home songs"],
    "Party - Pregame": ["pregame playlist", "getting ready party songs"],
    
    # === ROMANTIC (7 subvibes) ===
    "Romantic - Anniversary": ["anniversary songs", "relationship milestone music"],
    "Romantic - Date Night": ["date night playlist", "romantic evening songs"],
    "Romantic - First Love": ["first love songs", "new relationship music"],
    "Romantic - Intimate": ["intimate music playlist", "close romantic songs"],
    "Romantic - Long Distance": ["long distance relationship songs", "missing partner music"],
    "Romantic - Proposal": ["proposal songs", "engagement music"],
    "Romantic - Slow Dance": ["slow dance playlist", "romantic slow songs"],
    
    # === SAD (12 subvibes) ===
    "Sad - Crying": ["crying playlist", "songs make me cry"],
    "Sad - Depressive": ["depression music", "songs when depressed"],
    "Sad - Grief": ["grief playlist", "songs about loss death"],
    "Sad - Heartbreak": ["heartbreak playlist", "breakup songs crying"],
    "Sad - Lonely": ["lonely playlist", "feeling alone songs"],
    "Sad - Melancholic": ["melancholic music", "bittersweet sad songs"],
    "Sad - Nostalgic 2000s": ["2000s nostalgia", "nostalgic 2000s songs"],
    "Sad - Nostalgic 90s": ["90s nostalgia playlist", "nostalgic 90s songs"],
    "Sad - Nostalgic Childhood": ["childhood nostalgia music", "songs from childhood"],
    "Sad - Nostalgic Sad": ["nostalgic sad playlist", "bittersweet memories songs"],
    "Sad - Nostalgic Simpler Times": ["simpler times music", "nostalgic past songs"],
    "Sad - Nostalgic Teen Years": ["teen years nostalgia", "high school songs memories"],
}

# Reddit subreddits for emotional context discovery
EMOTIONAL_SUBREDDITS = [
    # Mental Health (high emotional signal)
    "depression", "anxiety", "mentalhealth", "CPTSD", "BPD",
    
    # Relationships
    "BreakUps", "ExNoContact", "relationship_advice", "heartbreak",
    
    # Grief
    "GriefSupport", "widowers", "ChildLoss", "Petloss",
    
    # Music Discovery (with emotional framing)  
    "ifyoulikeblank", "musicsuggestions", "spotify", "Music",
    "Frisson", "makemefeelgood",
    
    # Life Situations
    "CasualConversation", "offmychest", "TrueOffMyChest",
    "DecidingToBeBetter", "selfimprovement",
]


# =============================================================================
# DATA STRUCTURES  
# =============================================================================

@dataclass
class ScrapedSong:
    artist: str
    song: str
    subvibe: str
    comment_text: str
    comment_score: int
    comment_reasons: List[str]
    youtube_url: str
    reddit_context: str
    spotify_id: Optional[str] = None
    spotify_uri: Optional[str] = None
    data_source: str = "hybrid_balanced_v1"
    created_at: str = ""


# =============================================================================
# YOUTUBE API KEY ROTATION
# =============================================================================

class YouTubeKeyManager:
    """Manages multiple YouTube API keys with automatic rotation"""
    
    def __init__(self):
        self.keys = []
        # Load all available keys from environment
        for i in range(1, 10):  # Support up to 10 keys
            key_name = f"YOUTUBE_API_KEY_{i}" if i > 1 else "YOUTUBE_API_KEY"
            key = os.getenv(key_name)
            if key:
                self.keys.append(key)
        
        if not self.keys:
            raise ValueError("No YouTube API keys found! Set YOUTUBE_API_KEY in environment.")
        
        self.current_index = 0
        self.quotas_exhausted = set()
        logger.info(f"Loaded {len(self.keys)} YouTube API key(s)")
    
    def get_key(self) -> str:
        """Get current active key"""
        return self.keys[self.current_index]
    
    def rotate(self) -> bool:
        """
        Rotate to next key. Returns False if all keys exhausted.
        """
        self.quotas_exhausted.add(self.current_index)
        
        # Find next available key
        for i in range(len(self.keys)):
            next_idx = (self.current_index + 1 + i) % len(self.keys)
            if next_idx not in self.quotas_exhausted:
                self.current_index = next_idx
                logger.warning(f"Rotated to YouTube API key #{next_idx + 1}")
                return True
        
        logger.error("All YouTube API keys exhausted!")
        return False
    
    def reset_quotas(self):
        """Reset quota tracking (call at start of new day)"""
        self.quotas_exhausted.clear()
        self.current_index = 0


# =============================================================================
# BALANCED HYBRID SCRAPER
# =============================================================================

class BalancedHybridScraper:
    """
    Scrapes ALL subvibes evenly each run.
    
    Usage:
        scraper = BalancedHybridScraper()
        results = scraper.run(songs_per_vibe=3)  # 3 songs per vibe = ~321 attempts
    """
    
    def __init__(self, reddit_client=None, youtube_client=None, spotify_client=None):
        self.reddit = reddit_client
        self.youtube = youtube_client
        self.spotify = spotify_client
        self.yt_keys = YouTubeKeyManager() if not youtube_client else None
        
        # Stats
        self.stats = {
            "vibes_processed": 0,
            "songs_attempted": 0,
            "songs_accepted": 0,
            "songs_rejected": 0,
            "youtube_calls": 0,
            "quota_rotations": 0,
        }
    
    def run(self, songs_per_vibe: int = 3, min_score: int = 6) -> List[ScrapedSong]:
        """
        Run balanced scrape across ALL subvibes.
        
        Args:
            songs_per_vibe: How many songs to attempt per subvibe (default 3)
            min_score: Minimum comment quality score (default 6)
        
        Returns:
            List of ScrapedSong objects ready for tapestry
        """
        results = []
        all_vibes = list(SUBVIBE_SEARCHES.keys())
        
        logger.info("=" * 60)
        logger.info(f"BALANCED HYBRID SCRAPER")
        logger.info(f"Vibes: {len(all_vibes)} | Songs per vibe: {songs_per_vibe}")
        logger.info(f"Total attempts: ~{len(all_vibes) * songs_per_vibe}")
        logger.info("=" * 60)
        
        for i, subvibe in enumerate(all_vibes):
            logger.info(f"\n[{i+1}/{len(all_vibes)}] {subvibe}")
            self.stats["vibes_processed"] += 1
            
            # Get search queries for this vibe
            search_queries = SUBVIBE_SEARCHES.get(subvibe, [])
            if not search_queries:
                logger.warning(f"  No search queries for {subvibe}, skipping")
                continue
            
            # Attempt to find songs_per_vibe songs for this vibe
            vibe_results = self._scrape_vibe(subvibe, search_queries, songs_per_vibe, min_score)
            results.extend(vibe_results)
            
            logger.info(f"  → Got {len(vibe_results)} quality songs")
            
            # Small delay between vibes to be nice to APIs
            time.sleep(0.5)
        
        # Final stats
        self._print_stats()
        
        return results
    
    def _scrape_vibe(self, subvibe: str, queries: List[str], target: int, min_score: int) -> List[ScrapedSong]:
        """Scrape songs for a single subvibe"""
        results = []
        attempts = 0
        max_attempts = target * 3  # Try up to 3x to hit target
        
        for query in queries:
            if len(results) >= target or attempts >= max_attempts:
                break
            
            # Find songs via YouTube search (more direct than Reddit for discovery)
            songs = self._youtube_search_songs(query, limit=5)
            
            for artist, song, video_id in songs:
                if len(results) >= target or attempts >= max_attempts:
                    break
                
                attempts += 1
                self.stats["songs_attempted"] += 1
                
                # Get emotional comment from this video
                comment_data = self._get_quality_comment(video_id, min_score)
                
                if comment_data:
                    self.stats["songs_accepted"] += 1
                    
                    # Get Spotify ID if possible
                    spotify_id, spotify_uri = self._spotify_lookup(artist, song)
                    
                    results.append(ScrapedSong(
                        artist=artist,
                        song=song,
                        subvibe=subvibe,
                        comment_text=comment_data["text"],
                        comment_score=comment_data["score"],
                        comment_reasons=comment_data["reasons"],
                        youtube_url=f"https://youtube.com/watch?v={video_id}",
                        reddit_context=query,  # Using search query as context
                        spotify_id=spotify_id,
                        spotify_uri=spotify_uri,
                        created_at=datetime.now().isoformat()
                    ))
                else:
                    self.stats["songs_rejected"] += 1
        
        return results

    
    def _youtube_search_songs(self, query: str, limit: int = 5) -> List[tuple]:
        """
        Search YouTube for songs matching query.
        Returns list of (artist, song, video_id) tuples.
        """
        self.stats["youtube_calls"] += 1
        
        # This is a placeholder - actual implementation needs YouTube API
        # In real implementation:
        # 1. Search YouTube for query
        # 2. Parse video titles for "Artist - Song" pattern
        # 3. Return matches
        
        try:
            if self.youtube:
                request = self.youtube.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    maxResults=limit,
                    videoCategoryId="10"  # Music category
                )
                response = request.execute()
                
                results = []
                for item in response.get("items", []):
                    title = item["snippet"]["title"]
                    video_id = item["id"]["videoId"]
                    
                    # Try to parse "Artist - Song" from title
                    parsed = self._parse_song_title(title)
                    if parsed:
                        artist, song = parsed
                        results.append((artist, song, video_id))
                
                return results
        except Exception as e:
            if "quotaExceeded" in str(e):
                if self.yt_keys and self.yt_keys.rotate():
                    self.stats["quota_rotations"] += 1
                    return self._youtube_search_songs(query, limit)  # Retry with new key
            logger.error(f"YouTube search error: {e}")
        
        return []
    
    def _parse_song_title(self, title: str) -> Optional[tuple]:
        """Parse 'Artist - Song' from video title"""
        import re
        
        # Common patterns
        patterns = [
            r'^(.+?)\s*[-–—]\s*(.+?)(?:\s*[\(\[].*)?$',  # Artist - Song (Official Video)
            r'^(.+?)\s*[-–—]\s*["\'](.+?)["\']',  # Artist - "Song"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, title)
            if match:
                artist = match.group(1).strip()
                song = match.group(2).strip()
                
                # Clean up common suffixes
                for suffix in ["Official Video", "Official Audio", "Lyric Video", "Lyrics", 
                              "Official Music Video", "Audio", "HD", "HQ"]:
                    song = re.sub(rf'\s*[\(\[]?\s*{suffix}\s*[\)\]]?\s*$', '', song, flags=re.I)
                
                if len(artist) > 1 and len(song) > 1:
                    return (artist, song)
        
        return None
    
    def _get_quality_comment(self, video_id: str, min_score: int) -> Optional[dict]:
        """
        Get the best emotional comment from a video.
        Returns None if no comment meets quality threshold.
        """
        self.stats["youtube_calls"] += 1
        
        try:
            if self.youtube:
                request = self.youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=30,
                    order="relevance"
                )
                response = request.execute()
                
                best = None
                best_score = 0
                
                for item in response.get("items", []):
                    snippet = item["snippet"]["topLevelComment"]["snippet"]
                    text = snippet["textDisplay"]
                    likes = snippet["likeCount"]
                    
                    # Score the comment
                    score, reasons, warnings = self._score_comment(text)
                    
                    # Bonus for highly-liked comments
                    if likes > 100:
                        score += 1
                    if likes > 1000:
                        score += 1
                    
                    if score >= min_score and score > best_score:
                        best_score = score
                        best = {
                            "text": text,
                            "score": score,
                            "reasons": reasons,
                            "likes": likes
                        }
                
                return best
                
        except Exception as e:
            if "quotaExceeded" in str(e):
                if self.yt_keys and self.yt_keys.rotate():
                    self.stats["quota_rotations"] += 1
                    return self._get_quality_comment(video_id, min_score)
            logger.error(f"Comment fetch error: {e}")
        
        return None
    
    def _score_comment(self, text: str) -> tuple:
        """Score comment using v2 classifier logic"""
        # Import from our classifier
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent / "analysis"))
            from scorched_earth_v2 import score_comment_v2
            return score_comment_v2(text)
        except ImportError:
            # Fallback basic scoring if import fails
            return self._basic_score(text)
    
    def _basic_score(self, text: str) -> tuple:
        """Basic fallback scorer"""
        import re
        score = 0
        reasons = []
        
        c = text.lower()
        
        if re.search(r'\b(i|me|my)\b', c):
            score += 1
            reasons.append("first_person")
        
        if re.search(r'\b(cry|crying|tears|cried)\b', c):
            score += 2
            reasons.append("emotional")
        
        if re.search(r'\b(breakup|divorce|death|grief|anxiety|depression)\b', c):
            score += 2
            reasons.append("life_event")
        
        if re.search(r'\b(makes? me feel|got me through|reminds? me)\b', c):
            score += 2
            reasons.append("cause_effect")
        
        if len(text) > 100:
            score += 1
            reasons.append("good_length")
        
        return score, reasons, []
    
    def _spotify_lookup(self, artist: str, song: str) -> tuple:
        """Look up Spotify ID for a song"""
        if not self.spotify:
            return None, None
        
        try:
            results = self.spotify.search(q=f"artist:{artist} track:{song}", type="track", limit=1)
            if results["tracks"]["items"]:
                track = results["tracks"]["items"][0]
                return track["id"], track["uri"]
        except Exception as e:
            logger.error(f"Spotify lookup error: {e}")
        
        return None, None
    
    def _print_stats(self):
        """Print final statistics"""
        logger.info("\n" + "=" * 60)
        logger.info("SCRAPE COMPLETE - STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Vibes processed:    {self.stats['vibes_processed']}")
        logger.info(f"Songs attempted:    {self.stats['songs_attempted']}")
        logger.info(f"Songs accepted:     {self.stats['songs_accepted']}")
        logger.info(f"Songs rejected:     {self.stats['songs_rejected']}")
        logger.info(f"YouTube API calls:  {self.stats['youtube_calls']}")
        logger.info(f"Key rotations:      {self.stats['quota_rotations']}")
        
        if self.stats['songs_attempted'] > 0:
            rate = (self.stats['songs_accepted'] / self.stats['songs_attempted']) * 100
            logger.info(f"Acceptance rate:    {rate:.1f}%")
        
        logger.info("=" * 60)


# =============================================================================
# TAPESTRY INJECTION
# =============================================================================

def inject_to_tapestry(songs: List[ScrapedSong], tapestry_path: str) -> int:
    """
    Add scraped songs to tapestry.json
    Returns number of songs added.
    """
    with open(tapestry_path, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    added = 0
    for song in songs:
        vibe = song.subvibe
        
        # Ensure vibe exists
        if vibe not in tapestry.get('vibes', {}):
            tapestry['vibes'][vibe] = {'songs': []}
        
        # Add song
        tapestry['vibes'][vibe]['songs'].append({
            "artist": song.artist,
            "song": song.song,
            "spotify_id": song.spotify_id,
            "spotify_uri": song.spotify_uri,
            "comment_text": song.comment_text,
            "comment_score": song.comment_score,
            "source_url": song.youtube_url,
            "data_source": song.data_source,
            "mapped_subvibe": song.subvibe,
            "created_at": song.created_at,
        })
        added += 1
    
    with open(tapestry_path, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Injected {added} songs to tapestry")
    return added


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║               BALANCED HYBRID SCRAPER                             ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║                                                                   ║
    ║   Scrapes ALL 107 subvibes EVENLY each run.                       ║
    ║                                                                   ║
    ║   Example: songs_per_vibe=3                                       ║
    ║   → 107 vibes × 3 attempts = ~321 total attempts                  ║
    ║   → ~35% acceptance rate = ~112 quality songs                     ║
    ║   → Evenly distributed across all vibes!                          ║
    ║                                                                   ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║                                                                   ║
    ║   USAGE:                                                          ║
    ║                                                                   ║
    ║   # Setup                                                         ║
    ║   from googleapiclient.discovery import build                     ║
    ║   import spotipy                                                  ║
    ║                                                                   ║
    ║   youtube = build('youtube', 'v3', developerKey=os.getenv(...))   ║
    ║   spotify = spotipy.Spotify(auth_manager=...)                     ║
    ║                                                                   ║
    ║   # Run scraper                                                   ║
    ║   scraper = BalancedHybridScraper(youtube=youtube, spotify=sp)    ║
    ║   songs = scraper.run(songs_per_vibe=3, min_score=6)              ║
    ║                                                                   ║
    ║   # Add to tapestry                                               ║
    ║   inject_to_tapestry(songs, "core/tapestry.json")                 ║
    ║                                                                   ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║                                                                   ║
    ║   API KEYS: Set these environment variables:                      ║
    ║   - YOUTUBE_API_KEY (required)                                    ║
    ║   - YOUTUBE_API_KEY_2 (optional, for rotation)                    ║
    ║   - YOUTUBE_API_KEY_3 (optional, for rotation)                    ║
    ║   - SPOTIFY_CLIENT_ID                                             ║
    ║   - SPOTIFY_CLIENT_SECRET                                         ║
    ║                                                                   ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║                                                                   ║
    ║   EXPECTED RESULTS:                                               ║
    ║                                                                   ║
    ║   With songs_per_vibe=3:                                          ║
    ║   - ~321 YouTube searches                                         ║
    ║   - ~321 comment fetches                                          ║
    ║   - ~640 API calls total                                          ║
    ║   - Uses ~6,400 quota (10k daily limit per key)                   ║
    ║   - With 2 keys: can run 3x per day                               ║
    ║   - Output: ~100-150 quality songs, balanced across vibes         ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Quick test without API clients
    print("\nSubvibe count:", len(SUBVIBE_SEARCHES))
    print("Sample vibes and their search queries:")
    for vibe in list(SUBVIBE_SEARCHES.keys())[:5]:
        print(f"  {vibe}: {SUBVIBE_SEARCHES[vibe][0]}")
