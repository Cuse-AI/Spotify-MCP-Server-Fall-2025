"""Batch 19: Missing Emotions - Grateful/Appreciative (Positive reflection)"""
import praw, os, pandas as pd, time, re
from datetime import datetime
from dotenv import load_dotenv
load_dotenv('../.env')

class RedditExpansionBatch19:
    def __init__(self):
        self.reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'), user_agent=os.getenv('REDDIT_USER_AGENT'))

        # GRATEFUL + APPRECIATIVE variations (Positive reflection)
        self.search_queries = {
            'Grateful - Thankful': ['grateful music', 'thankful songs', 'gratitude playlist', 'feeling blessed music', 'appreciative songs'],
            'Grateful - Content': ['content music', 'satisfied songs', 'life is good playlist', 'happy with life music'],
            'Grateful - Reflective Gratitude': ['reflective gratitude', 'counting blessings music', 'appreciate what i have', 'grateful reflection'],
            'Grateful - Warm Appreciation': ['warm appreciation', 'love and gratitude', 'heartfelt thanks music', 'wholesome grateful'],
        }

        self.subreddits = ['musicsuggestions', 'ifyoulikeblank', 'listentothis', 'Music']
        self.scraped_post_ids = set()

    def extract_songs(self, text):
        songs = []
        for m in re.finditer(r'"([^"]{3,100})"\s+by\s+([A-Z][^,.\n]{2,50}?)', text, re.I):
            songs.append((m.group(1).strip(), m.group(2).strip()))
        for m in re.finditer(r'([A-Z][A-Za-z\s&]{2,40}?)\s*-\s*([A-Z][^-\n]{3,50}?)(?:\s|,|\.|\n|$)', text):
            if len(m.group(2)) < 50: songs.append((m.group(2).strip(), m.group(1).strip()))
        return songs

    def scrape_vibe_category(self, category, queries, max_posts=5):
        results = []
        for query in queries:
            for sub_name in self.subreddits:
                try:
                    for post in self.reddit.subreddit(sub_name).search(query, limit=max_posts, time_filter='year'):
                        if post.id not in self.scraped_post_ids:
                            self.scraped_post_ids.add(post.id)
                            post.comments.replace_more(limit=0)
                            for c in post.comments.list()[:30]:
                                if hasattr(c, 'body') and c.score >= 1:
                                    for song, artist in self.extract_songs(c.body):
                                        results.append({'vibe_sub_category': category, 'vibe_description': post.title,
                                            'song_name': song, 'artist_name': artist, 'recommendation_reasoning': c.body[:300],
                                            'comment_score': c.score, 'subreddit': sub_name,
                                            'source_url': f"https://reddit.com{c.permalink}", 'data_source': 'reddit',
                                            'search_query': query})
                            time.sleep(0.5)
                        time.sleep(1)
                except: pass
        return results

    def run_batch(self):
        print("\n[BATCH 19] Grateful + Appreciative variations...")
        all_results = []
        for cat, queries in self.search_queries.items():
            print(f"  {cat}...", end=' ', flush=True)
            results = self.scrape_vibe_category(cat, queries, 5)
            all_results.extend(results)
            print(f"{len(results)} songs", flush=True)
            time.sleep(2)
        return all_results

    def save_for_ananki(self, data):
        if not data: return None
        df = pd.DataFrame(data)
        df['vibe_category'] = None
        df['genre_category'] = None
        fn = f'reddit_batch19_grateful_appreciative_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(fn, index=False)
        print(f"\n[OK] {fn}: {len(df)} songs")
        return fn

def main():
    print("="*70 + "\nBATCH 19: GRATEFUL/APPRECIATIVE\n" + "="*70)
    scraper = RedditExpansionBatch19()
    data = scraper.run_batch()
    if data: scraper.save_for_ananki(data)

if __name__ == "__main__": main()
