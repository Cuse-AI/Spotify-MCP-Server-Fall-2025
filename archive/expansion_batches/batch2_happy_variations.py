"""
Reddit Massive Expansion Scraper - BATCH 2
Targeting: Happy variations (5 sub-vibes)
"""

import praw
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import time
import re

load_dotenv('../.env')


class RedditExpansionBatch2:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        # BATCH 2: Happy sub-vibes
        self.search_queries = {
            'Happy - Euphoric': ['euphoric music', 'pure joy songs', 'ecstatic playlist', 'blissful music'],
            'Happy - Feel Good': ['feel good music', 'positive vibes songs', 'uplifting playlist', 'good mood music'],
            'Happy - Celebration': ['celebration music', 'victory songs', 'triumph playlist', 'achievement music'],
            'Happy - Sunshine': ['sunshine music', 'bright songs', 'sunny day playlist', 'summer happiness'],
            'Happy - Carefree': ['carefree music', 'worry free songs', 'light hearted playlist', 'no worries music'],
        }
        
        self.subreddits = ['musicsuggestions', 'ifyoulikeblank', 'listentothis', 'Music']
        self.scraped_post_ids = set()
    
    def extract_songs(self, text):
        songs = []
        p1 = r'"([^"]{3,100})"\s+by\s+([A-Z][^,.\n]{2,50}?)'
        for m in re.finditer(p1, text, re.IGNORECASE):
            songs.append((m.group(1).strip(), m.group(2).strip(), 'quoted'))
        p2 = r'([A-Z][A-Za-z\s&]{2,40}?)\s*-\s*([A-Z][^-\n]{3,50}?)(?:\s|,|\.|\n|$)'
        for m in re.finditer(p2, text):
            if len(m.group(2)) < 50:
                songs.append((m.group(2).strip(), m.group(1).strip(), 'dash'))
        return songs
    
    def scrape_vibe_category(self, category, queries, max_posts=10):
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
                                        'vibe_description': post.title,
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
                except: pass
        return results
    
    def run_batch(self):
        print(f"\n[SCRAPING] Batch 2: Happy variations...")
        all_results = []
        for category, queries in self.search_queries.items():
            print(f"\n  Category: {category}")
            results = self.scrape_vibe_category(category, queries, max_posts=10)
            all_results.extend(results)
            print(f"    Found: {len(results)} songs")
            time.sleep(2)
        return all_results
    
    def save_for_ananki(self, data):
        if not data:
            return None
        df = pd.DataFrame(data)
        df['vibe_category'] = None
        df['genre_category'] = None
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reddit_batch2_happy_variations_{timestamp}.csv'
        df.to_csv(filename, index=False)
        print(f"\n[OK] Saved: {filename}")
        print(f"     Songs: {len(df)}, Unique: {len(df[['song_name','artist_name']].drop_duplicates())}")
        return filename

def main():
    print("="*70)
    print("REDDIT EXPANSION - BATCH 2: HAPPY")
    print("="*70)
    scraper = RedditExpansionBatch2()
    data = scraper.run_batch()
    if data:
        scraper.save_for_ananki(data)

if __name__ == "__main__":
    main()
