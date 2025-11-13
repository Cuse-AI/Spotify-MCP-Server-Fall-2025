"""
TEST: Improved Scraper on Happy - Feel Good
Goal: Prove the scraper fixes work before full re-scrape
Target: 70%+ validation rate (vs current 48.6%)
"""

import praw
import pandas as pd
import time
import re
import os
import json
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class ImprovedRedditScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        self.subreddits = ['musicsuggestions', 'ifyoulikeblank', 'listentothis', 'Music']
        self.scraped_post_ids = set()

    def clean_text(self, text):
        """Clean text of newlines and extra spaces"""
        if not text:
            return ""
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def validate_song(self, song, artist):
        """Validate that song and artist look reasonable"""
        if not song or not artist:
            return False
        if len(song) < 2 or len(artist) < 2:
            return False
        if len(song) > 100 or len(artist) > 60:
            return False
        
        song_words = ['the', 'a', 'an', 'my', 'your', 'our', 'their']
        if artist.lower().split()[0] in song_words:
            return False
        if ' by ' in song.lower():
            return False
        
        return True

    def extract_songs(self, text):
        """Extract songs with IMPROVED patterns - CORRECT ORDER!"""
        songs = []
        text = self.clean_text(text)

        # Pattern 1: "Song Title" by Artist Name (HIGH CONFIDENCE)
        p1 = r'"([^"]{2,80})"\s+by\s+([A-Z][A-Za-z\s\-&\'\.]{1,50}?)(?:\s|,|\.|\n|$)'
        for m in re.finditer(p1, text, re.IGNORECASE):
            song = self.clean_text(m.group(1))
            artist = self.clean_text(m.group(2))
            if self.validate_song(song, artist):
                songs.append((artist, song, 'quoted_by', 0.9))  # CORRECT: (Artist, Song)

        # Pattern 2: Artist - Song (FIXED ORDER!)
        p2 = r'([A-Z][A-Za-z\s\-&\'\.]{1,35}?)\s*[-–—]\s*([A-Z][A-Za-z\s\-&\'\.!?]{2,50}?)(?:\s|,|\.|\n|$)'
        for m in re.finditer(p2, text):
            part1 = self.clean_text(m.group(1))
            part2 = self.clean_text(m.group(2))
            
            # FIXED: Correct order - (Artist, Song)
            if self.validate_song(part2, part1):
                songs.append((part1, part2, 'dash', 0.7))  # FIXED!

        # Pattern 3: Artist "Song Title"
        p3 = r'([A-Z][A-Za-z\s\-&\'\.]{1,35}?)\s+["\'"]([^"\']{2,80})["\'"]'
        for m in re.finditer(p3, text):
            artist = self.clean_text(m.group(1))
            song = self.clean_text(m.group(2))
            if self.validate_song(song, artist):
                songs.append((artist, song, 'artist_quoted', 0.8))

        # Deduplicate (keep highest confidence)
        seen = {}
        for artist, song, method, conf in songs:
            key = (artist.lower(), song.lower())
            if key not in seen or seen[key][3] < conf:
                seen[key] = (artist, song, method, conf)

        return list(seen.values())

    def scrape_happy_feel_good(self, max_posts=15):
        """Test scraper on Happy - Feel Good"""
        queries = [
            'happy feel good songs',
            'uplifting music',
            'songs that make you smile',
            'mood boosting music',
            'feel good playlist'
        ]
        
        results = []
        print(f"\nScraping Happy - Feel Good with IMPROVED patterns...")
        print("="*70)
        
        for query in queries:
            print(f"\n  Query: {query}")
            
            for sub_name in self.subreddits:
                try:
                    sub = self.reddit.subreddit(sub_name)
                    posts = sub.search(query, limit=max_posts, time_filter='year')
                    
                    for post in posts:
                        if post.id in self.scraped_post_ids:
                            continue
                        
                        self.scraped_post_ids.add(post.id)
                        post.comments.replace_more(limit=0)
                        
                        for comment in post.comments.list()[:30]:
                            if hasattr(comment, 'body') and comment.score >= 1:
                                songs = self.extract_songs(comment.body)
                                
                                for artist, song, method, confidence in songs:
                                    results.append({
                                        'artist': artist,
                                        'song': song,
                                        'vibe': 'Happy - Feel Good',
                                        'extraction_method': method,
                                        'extraction_confidence': confidence,
                                        'comment_score': comment.score,
                                        'source_url': f'https://reddit.com{comment.permalink}',
                                        'data_source': 'reddit_improved_v2'
                                    })
                    
                    time.sleep(2)  # Rate limiting
                
                except Exception as e:
                    print(f"    Error in r/{sub_name}: {e}")
                    continue
        
        return results


def main():
    print("\n" + "="*70)
    print("TESTING IMPROVED SCRAPER - HAPPY FEEL GOOD")
    print("="*70)
    
    scraper = ImprovedRedditScraper()
    
    # Scrape Happy - Feel Good
    results = scraper.scrape_happy_feel_good(max_posts=15)
    
    # Save results
    output_file = Path(__file__).parent / 'test_results' / 'happy_feel_good_IMPROVED.json'
    output_file.parent.mkdir(exist_ok=True)
    
    # Deduplicate
    seen = set()
    unique_results = []
    for r in results:
        key = (r['artist'].lower(), r['song'].lower())
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'vibe': 'Happy - Feel Good',
            'total_songs': len(unique_results),
            'duplicates_removed': len(results) - len(unique_results),
            'songs': unique_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print("SCRAPING COMPLETE!")
    print(f"{'='*70}")
    print(f"Total songs scraped: {len(results)}")
    print(f"Unique songs: {len(unique_results)}")
    print(f"Duplicates removed: {len(results) - len(unique_results)}")
    print(f"\nSaved to: {output_file}")
    print(f"\nNEXT: Validate these {len(unique_results)} songs against Spotify!")
    print("Expected: 70%+ high confidence (vs 48.6% with old scraper)")
    
    return unique_results

if __name__ == '__main__':
    songs = main()
