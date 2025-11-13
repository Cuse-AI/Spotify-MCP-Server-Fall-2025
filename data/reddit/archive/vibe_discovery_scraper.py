"""
Ananki Vibe Discovery Scraper
===============================

TWO-PHASE APPROACH:
Phase 1: Discover new vibe phrases from human language
Phase 2: Scrape songs for those discovered vibes

This finds vibes WE haven't thought of yet!
"""

import praw
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import re
from collections import Counter

load_dotenv('.env')  # Load from same directory


class VibeDiscoveryScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        # Subreddits where people describe vibes
        self.subreddits = [
            'musicsuggestions',
            'ifyoulikeblank',
            'spotify',
            'Music',
        ]
    
    # ========================================================================
    # PHASE 1: DISCOVER VIBE PHRASES
    # ========================================================================
    
    def extract_vibe_phrases(self, text):
        """Extract emotional/vibe descriptions from text"""
        vibe_phrases = []
        
        # Pattern 1: "music for X" / "songs for X"
        p1 = r'(?:music|songs?|playlist) for ([^.!?\n]{10,80})'
        for match in re.finditer(p1, text, re.IGNORECASE):
            phrase = match.group(1).strip()
            if self.is_valid_vibe_phrase(phrase):
                vibe_phrases.append(phrase)
        
        # Pattern 2: "when you're X" / "when I'm X"
        p2 = r'when (?:you\'re|i\'m|im|youre) ([^.!?\n]{10,80})'
        for match in re.finditer(p2, text, re.IGNORECASE):
            phrase = f"when you're {match.group(1).strip()}"
            if self.is_valid_vibe_phrase(phrase):
                vibe_phrases.append(phrase)
        
        # Pattern 3: "feels like X" / "sounds like X"  
        p3 = r'(?:feels?|sounds?) like ([^.!?\n]{10,80})'
        for match in re.finditer(p3, text, re.IGNORECASE):
            phrase = f"feels like {match.group(1).strip()}"
            if self.is_valid_vibe_phrase(phrase):
                vibe_phrases.append(phrase)
        
        # Pattern 4: Direct descriptions "X vibes" / "X energy" / "X mood"
        p4 = r'([a-z][a-z\s]{5,40}?) (?:vibes?|energy|mood|feels|aesthetic)'
        for match in re.finditer(p4, text, re.IGNORECASE):
            phrase = match.group(1).strip()
            if self.is_valid_vibe_phrase(phrase):
                vibe_phrases.append(phrase)
        
        # Pattern 5: Time + emotion "3am thoughts" / "sunday morning X"
        p5 = r'(?:\d{1,2}\s*am|morning|evening|night|midnight|dawn|dusk|sunday|monday|weekend) ([a-z\s]{5,40})'
        for match in re.finditer(p5, text, re.IGNORECASE):
            full_phrase = match.group(0).strip()
            if self.is_valid_vibe_phrase(full_phrase):
                vibe_phrases.append(full_phrase)
        
        return vibe_phrases
    
    def is_valid_vibe_phrase(self, phrase):
        """Validate if this is actually a vibe description"""
        phrase = phrase.strip().lower()
        
        # Too short/long
        if len(phrase) < 5 or len(phrase) > 100:
            return False
        
        # Reject non-vibe patterns
        reject = [
            'spotify', 'youtube', 'playlist name', 'subreddit', 'http',
            'click here', 'check out', 'listen to', 'download', 'subscribe'
        ]
        if any(r in phrase for r in reject):
            return False
        
        # Must have some emotional/descriptive content
        emotional_indicators = [
            'feel', 'mood', 'vibe', 'energy', 'thought', 'emotion',
            'sad', 'happy', 'angry', 'chill', 'hype', 'calm', 'dark', 'bright',
            'drive', 'driving', 'study', 'work', 'sleep', 'party', 'dance',
            'rain', 'cozy', 'night', 'morning', 'am', 'pm'
        ]
        
        has_emotional_content = any(indicator in phrase for indicator in emotional_indicators)
        
        return has_emotional_content
    
    def discover_vibes_from_subreddit(self, subreddit_name, limit=50):
        """Scan subreddit for vibe phrases"""
        print(f"  Scanning r/{subreddit_name}...")
        
        all_phrases = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = subreddit.hot(limit=limit)
            
            for post in posts:
                # Extract from title
                phrases = self.extract_vibe_phrases(post.title)
                all_phrases.extend(phrases)
                
                # Extract from selftext
                if post.selftext:
                    phrases = self.extract_vibe_phrases(post.selftext)
                    all_phrases.extend(phrases)
                
                # Extract from top comments
                post.comments.replace_more(limit=0)
                for comment in post.comments.list()[:10]:
                    if hasattr(comment, 'body'):
                        phrases = self.extract_vibe_phrases(comment.body)
                        all_phrases.extend(phrases)
                
                time.sleep(0.3)
        
        except Exception as e:
            print(f"    [ERROR] {e}")
        
        return all_phrases
    
    def phase1_discover_vibes(self, posts_per_subreddit=50):
        """PHASE 1: Discover vibe phrases from Reddit"""
        print("\n" + "="*70)
        print("PHASE 1: DISCOVERING VIBE PHRASES")
        print("="*70)
        
        all_vibes = []
        
        for subreddit in self.subreddits:
            phrases = self.discover_vibes_from_subreddit(subreddit, limit=posts_per_subreddit)
            all_vibes.extend(phrases)
            print(f"    Found {len(phrases)} vibe phrases")
            time.sleep(2)
        
        # Count and rank
        vibe_counter = Counter(all_vibes)
        
        print(f"\n[DISCOVERED] {len(vibe_counter)} unique vibe phrases")
        print(f"[FILTERING] Keeping vibes mentioned 2+ times...")
        
        # Filter to vibes mentioned multiple times (signal vs noise)
        popular_vibes = {vibe: count for vibe, count in vibe_counter.items() if count >= 2}
        
        print(f"[RESULT] {len(popular_vibes)} validated vibe phrases")
        
        # Save discovered vibes
        vibe_df = pd.DataFrame([
            {'vibe_phrase': vibe, 'mention_count': count}
            for vibe, count in sorted(popular_vibes.items(), key=lambda x: x[1], reverse=True)
        ])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'discovered_vibes_{timestamp}.csv'
        vibe_df.to_csv(filename, index=False)
        
        print(f"\n[OK] Saved discovered vibes to: {filename}")
        print(f"\nTop 20 discovered vibes:")
        for i, row in vibe_df.head(20).iterrows():
            print(f"  {row['vibe_phrase']}: {row['mention_count']} mentions")
        
        return filename, popular_vibes
    
    # ========================================================================
    # PHASE 2: SCRAPE SONGS FOR DISCOVERED VIBES
    # ========================================================================
    
    def extract_songs_from_comment(self, comment_text):
        """Extract song/artist pairs"""
        songs = []
        
        # Pattern: "Song" by Artist
        p1 = r'"([^"]{3,100})"\s+by\s+([A-Z][^,.\n]{2,50}?)'
        for match in re.finditer(p1, comment_text, re.IGNORECASE):
            song = match.group(1).strip()
            artist = match.group(2).strip()
            if len(song) >= 3 and len(artist) >= 2:
                songs.append((song, artist))
        
        # Pattern: Artist - Song
        p2 = r'([A-Z][A-Za-z\s&]{2,40}?)\s*-\s*([A-Z][^-\n]{3,50}?)(?:\s|,|\.|\n|$)'
        for match in re.finditer(p2, comment_text):
            artist = match.group(1).strip()
            song = match.group(2).strip()
            if len(song) >= 3 and len(artist) >= 2 and len(song) < 50:
                songs.append((song, artist))
        
        return songs
    
    def phase2_scrape_for_vibe(self, vibe_phrase, max_posts=10):
        """PHASE 2: Scrape songs for a specific discovered vibe"""
        
        results = []
        
        # Search for this exact vibe phrase + music
        search_query = f'"{vibe_phrase}" music'
        
        for subreddit_name in self.subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.search(search_query, limit=max_posts, time_filter='year')
                
                for post in posts:
                    # Get comments
                    post.comments.replace_more(limit=0)
                    for comment in post.comments.list()[:20]:
                        if hasattr(comment, 'body') and comment.score >= 1:
                            songs = self.extract_songs_from_comment(comment.body)
                            
                            for song, artist in songs:
                                results.append({
                                    'discovered_vibe': vibe_phrase,
                                    'vibe_description': f"{post.title} - {post.selftext[:100]}",
                                    'song_name': song,
                                    'artist_name': artist,
                                    'recommendation_reasoning': comment.body[:300],
                                    'comment_score': comment.score,
                                    'subreddit': subreddit_name,
                                    'source_url': f"https://reddit.com{comment.permalink}",
                                    'data_source': 'reddit_vibe_discovery',
                                })
                
                time.sleep(1)
            except Exception as e:
                continue
        
        return results
    
    def phase2_scrape_all_vibes(self, discovered_vibes_file, max_vibes=30, posts_per_vibe=5):
        """PHASE 2: Scrape songs for top discovered vibes"""
        print("\n" + "="*70)
        print("PHASE 2: SCRAPING SONGS FOR DISCOVERED VIBES")
        print("="*70)
        
        # Load discovered vibes
        vibe_df = pd.read_csv(discovered_vibes_file)
        top_vibes = vibe_df.head(max_vibes)
        
        print(f"\n[SCRAPING] Top {len(top_vibes)} discovered vibes...")
        
        all_results = []
        
        for idx, row in top_vibes.iterrows():
            vibe_phrase = row['vibe_phrase']
            print(f"\n  [{idx+1}/{len(top_vibes)}] '{vibe_phrase}'...")
            
            results = self.phase2_scrape_for_vibe(vibe_phrase, max_posts=posts_per_vibe)
            all_results.extend(results)
            
            print(f"      Found {len(results)} songs")
            time.sleep(2)
        
        # Save results
        if all_results:
            results_df = pd.DataFrame(all_results)
            
            # Add empty columns for Ananki
            results_df['vibe_category'] = None
            results_df['genre_category'] = None
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'discovered_vibes_songs_{timestamp}.csv'
            results_df.to_csv(filename, index=False)
            
            print(f"\n[OK] Saved: {filename}")
            print(f"     Total songs: {len(results_df)}")
            print(f"     For {len(top_vibes)} discovered vibes")
            print(f"     Ready for Ananki to map to tapestry!")
            
            return filename
        
        return None


def main():
    print("="*70)
    print("ANANKI VIBE DISCOVERY SCRAPER")
    print("="*70)
    print("\nTwo-phase approach:")
    print("  Phase 1: Discover vibe phrases from human language")
    print("  Phase 2: Scrape songs for those discovered vibes")
    print()
    
    scraper = VibeDiscoveryScraper()
    
    # Phase 1
    discovered_file, vibes = scraper.phase1_discover_vibes(posts_per_subreddit=50)
    
    # Phase 2  
    if discovered_file and vibes:
        songs_file = scraper.phase2_scrape_all_vibes(
            discovered_file,
            max_vibes=20,  # Top 20 discovered vibes
            posts_per_vibe=5
        )
        
        if songs_file:
            print("\n" + "="*70)
            print("DISCOVERY COMPLETE!")
            print("="*70)
            print(f"\nFiles created:")
            print(f"  1. {discovered_file} - Discovered vibe phrases")
            print(f"  2. {songs_file} - Songs for those vibes")
            print(f"\nNext: Ask Ananki to:")
            print(f"  - Analyze emotional meaning of new vibes")
            print(f"  - Map to existing tapestry or create new nodes")
            print(f"  - Update tapestry with discovered vibes!")


if __name__ == "__main__":
    main()
