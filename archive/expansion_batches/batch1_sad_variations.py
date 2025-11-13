"""
Reddit Massive Expansion Scraper - BATCH 1
Targeting: Sad variations (7 sub-vibes)
"""

import praw
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import time
import re

load_dotenv()


class RedditMassiveExpansion:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        # BATCH 1: Emotional/Sad sub-vibes (7 variations)
        self.search_queries = {
            'Sad - Heartbreak': ['heartbreak songs', 'breakup playlist', 'post breakup music', 'getting over ex'],
            'Sad - Crying': ['songs that make you cry', 'crying music', 'tear jerker songs'],
            'Sad - Lonely': ['lonely music', 'feeling alone songs', 'isolation playlist'],
            'Sad - Melancholic': ['melancholic music', 'bittersweet songs', 'wistful music'],
            'Sad - Grief': ['grief music', 'loss songs', 'mourning playlist', 'missing someone'],
            'Sad - Depressive': ['depressing music', 'heavy sad songs', 'dark sadness'],
            'Sad - Nostalgic Sad': ['sad nostalgia', 'missing the past', 'used to be songs'],
        }
        
        self.subreddits = ['musicsuggestions', 'ifyoulikeblank', 'listentothis', 'Music']
        self.scraped_post_ids = set()
    
    def extract_songs(self, text):
        """Extract songs from text"""
        songs = []
        
        # "Song" by Artist
        p1 = r'"([^"]{3,100})"\s+by\s+([A-Z][^,.\n]{2,50}?)'
        for m in re.finditer(p1, text, re.IGNORECASE):
            songs.append((m.group(1).strip(), m.group(2).strip(), 'quoted'))
        
        # Artist - Song  
        p2 = r'([A-Z][A-Za-z\s&]{2,40}?)\s*-\s*([A-Z][^-\n]{3,50}?)(?:\s|,|\.|\n|$)'
        for m in re.finditer(p2, text):
            if len(m.group(2)) < 50:  # Not a title
                songs.append((m.group(2).strip(), m.group(1).strip(), 'dash'))
        
        return songs
    
    def scrape_vibe_category(self, category, queries, max_posts=10):
        """Scrape one vibe category"""
        results = []
        
        for query in queries:
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
                                
                                for song, artist, method in songs:
                                    results.append({
                                        'vibe_sub_category': category,
                                        'vibe_description': f"{post.title}",
                                        'song_name': song,
                                        'artist_name': artist,
                                        'recommendation_reasoning': comment.body[:300],
                                        'comment_score': comment.score,
                                        'subreddit': sub_name,
                                        'source_url': f"https://reddit.com{comment.permalink}",
                                        'data_source': 'reddit',
                                        'search_query': query,
                                    })
                        time.sleep(0.5)
                    time.sleep(1)
                except Exception as e:
                    print(f"      [ERROR] {e}")
        
        return results
    
    def run_batch(self):
        """Run batch 1 scraping"""
        print(f"\n[SCRAPING] Batch 1: Emotional/Sad variations...")
        
        all_results = []
        for category, queries in self.search_queries.items():
            print(f"\n  Category: {category}")
            print(f"    Queries: {queries}")
            results = self.scrape_vibe_category(category, queries, max_posts=10)
            all_results.extend(results)
            print(f"    Found: {len(results)} songs")
            time.sleep(2)
        
        return all_results
    
    def save_for_ananki(self, data):
        """Save for Ananki analysis"""
        if not data:
            print("[WARNING] No data")
            return None
        
        df = pd.DataFrame(data)
        
        # Add Ananki columns
        df['vibe_category'] = None
        df['genre_category'] = None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reddit_batch1_sad_variations_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        print(f"\n[OK] Saved: {filename}")
        print(f"     Songs: {len(df)}")
        print(f"     Unique: {len(df[['song_name','artist_name']].drop_duplicates())}")
        print(f"     Sub-vibes: {df['vibe_sub_category'].nunique()}")
        
        return filename


def main():
    print("="*70)
    print("REDDIT MASSIVE EXPANSION - BATCH 1")
    print("="*70)
    print("\nTarget: Emotional/Sad sub-vibe variations")
    print("Expected: 7 sub-vibes with 100+ songs total")
    print()
    
    scraper = RedditMassiveExpansion()
    data = scraper.run_batch()
    
    if data:
        scraper.save_for_ananki(data)
        print("\n[NEXT] Run Batch 2 (Happy variations)")
    else:
        print("\n[ERROR] No data collected")


if __name__ == "__main__":
    main()
