"""
Reddit Vibe Scraper - INTEGRATED WITH AUTO-PIPELINE
Outputs clean CSV ready for Ananki analysis and tapestry integration
"""

import praw
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import time
import re
import sys

load_dotenv()


class RedditScraperIntegrated:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        self.scraped_post_ids = set()
        
        # Diverse search queries for different vibes/moods
        self.search_queries = {
            # Underrepresented vibes that need boosting
            'focus_study': ['music for studying', 'concentration music', 'focus playlist', 'work from home music'],
            'rainy_cozy': ['rainy day music', 'cozy vibes', 'grey day playlist', 'sweater weather songs'],
            'innovative': ['weird music', 'experimental songs', 'unique sound', 'unconventional music'],
            'rebellious': ['punk music', 'anarchist songs', 'protest music', 'anti-establishment'],
            'epic': ['epic music', 'cinematic songs', 'orchestral dramatic', 'movie soundtrack vibes'],
            'motivational': ['workout motivation', 'pump up music', 'hype songs', 'confidence music'],
            
            # Well-represented but always good to have more
            'emotional_sad': ['sad songs', 'heartbreak music', 'crying playlist', 'melancholic songs'],
            'introspective': ['introspective music', 'thoughtful songs', 'contemplative playlist'],
            'night_sleep': ['late night music', '3am playlist', 'insomnia songs', 'midnight vibes'],
            'chill': ['chill music', 'relaxing songs', 'laid back playlist', 'mellow vibes'],
        }
        
        self.subreddits = [
            'musicsuggestions',
            'ifyoulikeblank',
            'listentothis',
            'Music',
        ]
    
    def is_valid_song_name(self, text):
        """Validate song name"""
        if not text or len(text) < 3 or len(text) > 150:
            return False
        if re.match(r'^[\d\s\-_]+$', text):
            return False
        reject = ['spotify', 'youtube', 'playlist', 'http', 'reddit']
        return not any(r in text.lower() for r in reject)
    
    def is_valid_artist_name(self, text):
        """Validate artist name"""
        if not text or len(text) < 2 or len(text) > 100:
            return False
        if re.match(r'^[\d\s\-_]+$', text):
            return False
        reject = ['spotify', 'youtube', 'http', 'reddit', 'give me', 'looking for', 'songs for']
        return not any(r in text.lower() for r in reject)
    
    def extract_songs_from_comment(self, comment_text):
        """Extract song/artist pairs from Reddit comment"""
        songs = []
        
        # Pattern 1: "Song" by Artist
        p1 = r'"([^"]+)"\s+by\s+([A-Z][^,.\n]+?)'
        for match in re.finditer(p1, comment_text, re.IGNORECASE):
            song = match.group(1).strip()
            artist = match.group(2).strip()
            if self.is_valid_song_name(song) and self.is_valid_artist_name(artist):
                songs.append((song, artist, 'quoted_by'))
        
        # Pattern 2: Artist - Song (only if not title-like)
        p2 = r'([A-Z][A-Za-z\s&]+?)\s*-\s*([A-Z][^-\n]{3,50}?)(?:\s|,|\.|\n|$)'
        for match in re.finditer(p2, comment_text):
            artist = match.group(1).strip()
            song = match.group(2).strip()
            if self.is_valid_song_name(song) and self.is_valid_artist_name(artist):
                # Skip if looks like title format
                if len(song) < 50:
                    songs.append((song, artist, 'dash_format'))
        
        # Pattern 3: Song by Artist (unquoted)
        p3 = r'\b([A-Z][A-Za-z\s]+?)\s+by\s+([A-Z][^,.\n!?]+?)(?:\s|,|\.|\n|$)'
        for match in re.finditer(p3, comment_text):
            song = match.group(1).strip()
            artist = match.group(2).strip()
            if self.is_valid_song_name(song) and self.is_valid_artist_name(artist):
                songs.append((song, artist, 'unquoted_by'))
        
        return songs
    
    def scrape_query(self, query, category, max_posts=5):
        """Scrape posts for a specific query"""
        results = []
        
        for subreddit_name in self.subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.search(query, limit=max_posts, time_filter='month')
                
                for post in posts:
                    if post.id in self.scraped_post_ids:
                        continue
                    
                    self.scraped_post_ids.add(post.id)
                    
                    # Get comments
                    post.comments.replace_more(limit=0)
                    for comment in post.comments.list()[:30]:
                        if hasattr(comment, 'body') and comment.score >= 1:
                            songs = self.extract_songs_from_comment(comment.body)
                            
                            for song, artist, method in songs:
                                results.append({
                                    'vibe_description': f"{post.title} - {post.selftext[:100]}",
                                    'song_name': song,
                                    'artist_name': artist,
                                    'recommendation_reasoning': comment.body[:500],
                                    'subreddit': subreddit_name,
                                    'comment_score': comment.score,
                                    'extraction_confidence': 'high' if method == 'quoted_by' else 'medium',
                                    'extraction_method': method,
                                    'source_url': f"https://reddit.com{comment.permalink}",
                                    'data_source': 'reddit',
                                    'search_query': query,
                                    'vibe_category_hint': category,
                                })
                
                time.sleep(1)
            except Exception as e:
                print(f"  [ERROR] {subreddit_name}: {e}")
        
        return results
    
    def run_scrape(self, posts_per_query=5):
        """Run full scraping across all queries"""
        print("\n[SCRAPING] Collecting diverse vibe-song pairs...")
        
        all_results = []
        for category, queries in self.search_queries.items():
            print(f"\n  Category: {category}")
            for query in queries:
                print(f"    Query: '{query}'...")
                results = self.scrape_query(query, category, max_posts=posts_per_query)
                all_results.extend(results)
                print(f"      Found {len(results)} songs")
                time.sleep(2)
        
        return all_results
    
    def save_for_ananki(self, data):
        """Save in format ready for Ananki analysis"""
        if not data:
            print("[WARNING] No data to save")
            return None
        
        df = pd.DataFrame(data)
        
        # Add empty columns that Ananki will fill
        df['vibe_category'] = None  # Ananki determines this
        df['genre_category'] = None  # Ananki infers this
        df['relation_type'] = None
        df['anchor_reference_artist'] = None
        df['anchor_reference_song'] = None
        df['delta_description'] = None
        df['reasoning_text'] = None
        df['sequence_order'] = None
        
        # Reorder to match expected format
        column_order = [
            'vibe_category', 'vibe_description', 'song_name', 'artist_name',
            'recommendation_reasoning', 'genre_category', 'subreddit', 
            'comment_score', 'extraction_confidence', 'source_url', 'data_source',
            'relation_type', 'anchor_reference_artist', 'anchor_reference_song',
            'delta_description', 'reasoning_text', 'sequence_order'
        ]
        
        df = df[column_order + [c for c in df.columns if c not in column_order]]
        
        # Save with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reddit_for_ananki_{timestamp}.csv'
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"\n[OK] Saved: {filename}")
        print(f"     Total songs: {len(df)}")
        print(f"     Unique songs: {len(df[['song_name', 'artist_name']].drop_duplicates())}")
        print(f"     Ready for Ananki analysis!")
        
        return filename


def main():
    print("="*70)
    print("REDDIT SCRAPER - INTEGRATED")
    print("="*70)
    print("\nThis scraper:")
    print("  [OK] Targets diverse vibes (especially underrepresented ones)")
    print("  [OK] Validates and cleans data automatically")
    print("  [OK] Outputs CSV ready for Ananki analysis")
    print()
    
    scraper = RedditScraperIntegrated()
    
    # Scrape
    data = scraper.run_scrape(posts_per_query=5)
    
    if data:
        # Save for Ananki
        filename = scraper.save_for_ananki(data)
        
        print("\n" + "="*70)
        print("COMPLETE!")
        print("="*70)
        print(f"\nNext: Ask Ananki to analyze {filename}")
        print("      Ananki will determine vibe_category, genre_category, etc.")
        print("      Then merge into tapestry_map.json")
    else:
        print("\n[ERROR] No data collected")


if __name__ == "__main__":
    main()
