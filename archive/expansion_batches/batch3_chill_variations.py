"""Batch 3: Chill variations (8 sub-vibes)"""
import praw, os, pandas as pd, time, re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('../.env')

class RedditExpansionBatch3:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT'))
        self.search_queries = {
            'Chill - Morning Coffee': ['morning coffee music', 'breakfast vibes', 'gentle morning songs'],
            'Chill - Rainy Day': ['rainy day chill', 'rain music calm', 'cozy rain music'],
            'Chill - Beach/Summer': ['beach chill music', 'summer relaxation', 'tropical vibes'],
            'Chill - Evening': ['evening wind down', 'after work relax', 'sunset music'],
            'Chill - Sunday': ['sunday morning music', 'lazy sunday', 'weekend chill'],
            'Chill - Lofi': ['lofi hip hop', 'chill beats', 'lofi vibes study'],
            'Chill - Jazz': ['chill jazz', 'smooth jazz', 'jazz lounge music'],
            'Chill - Ambient': ['ambient chill', 'atmospheric calm', 'ambient relax'],
        }
        self.subreddits = ['musicsuggestions', 'ifyoulikeblank', 'listentothis', 'Music']
        self.scraped_post_ids = set()
    
    def extract_songs(self, text):
        songs = []
        p1 = r'"([^"]{3,100})"\s+by\s+([A-Z][^,.\n]{2,50}?)'
        for m in re.finditer(p1, text, re.IGNORECASE):
            songs.append((m.group(1).strip(), m.group(2).strip()))
        p2 = r'([A-Z][A-Za-z\s&]{2,40}?)\s*-\s*([A-Z][^-\n]{3,50}?)(?:\s|,|\.|\n|$)'
        for m in re.finditer(p2, text):
            if len(m.group(2)) < 50:
                songs.append((m.group(2).strip(), m.group(1).strip()))
        return songs
    
    def scrape_vibe_category(self, category, queries, max_posts=10):
        results = []
        for query in queries:
            for sub_name in self.subreddits:
                try:
                    sub = self.reddit.subreddit(sub_name)
                    for post in sub.search(query, limit=max_posts, time_filter='year'):
                        if post.id in self.scraped_post_ids:
                            continue
                        self.scraped_post_ids.add(post.id)
                        post.comments.replace_more(limit=0)
                        for comment in post.comments.list()[:30]:
                            if hasattr(comment, 'body') and comment.score >= 1:
                                for song, artist in self.extract_songs(comment.body):
                                    results.append({
                                        'vibe_sub_category': category, 'vibe_description': post.title,
                                        'song_name': song, 'artist_name': artist,
                                        'recommendation_reasoning': comment.body[:300],
                                        'comment_score': comment.score, 'subreddit': sub_name,
                                        'source_url': f"https://reddit.com{comment.permalink}",
                                        'data_source': 'reddit', 'search_query': query})
                        time.sleep(0.5)
                    time.sleep(1)
                except: pass
        return results
    
    def run_batch(self):
        print("\n[BATCH 3] Chill variations...")
        all_results = []
        for cat, queries in self.search_queries.items():
            print(f"  {cat}...", end=' ')
            results = self.scrape_vibe_category(cat, queries, 10)
            all_results.extend(results)
            print(f"{len(results)} songs")
            time.sleep(2)
        return all_results
    
    def save_for_ananki(self, data):
        if not data: return None
        df = pd.DataFrame(data)
        df['vibe_category'] = None
        df['genre_category'] = None
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        fn = f'reddit_batch3_chill_variations_{ts}.csv'
        df.to_csv(fn, index=False)
        print(f"\n[OK] {fn}: {len(df)} songs")
        return fn

def main():
    print("="*70 + "\nBATCH 3: CHILL\n" + "="*70)
    scraper = RedditExpansionBatch3()
    data = scraper.run_batch()
    if data: scraper.save_for_ananki(data)

if __name__ == "__main__": main()
