"""Batch 13 Part 2: Hopeful & Excited variations"""
import praw, os, pandas as pd, time, re
from datetime import datetime
from dotenv import load_dotenv
load_dotenv('../.env')

class Batch13Part2:
    def __init__(self):
        self.reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'), user_agent=os.getenv('REDDIT_USER_AGENT'))
        self.search_queries = {
            'Hopeful - Optimistic': ['hopeful music', 'optimistic songs', 'better days ahead', 'hope playlist'],
            'Hopeful - Healing': ['healing music', 'getting better songs', 'recovery playlist', 'moving forward music'],
            'Hopeful - New Beginnings': ['new beginning music', 'fresh start songs', 'new chapter playlist'],
            'Excited - Anticipation': ['anticipation music', 'excited waiting', 'before the event', 'cant wait songs'],
            'Excited - Adventure': ['adventure music', 'new adventure songs', 'exploring playlist', 'journey excitement'],
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
    
    def scrape_vibe_category(self, category, queries, max_posts=10):
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
        print("\n[BATCH 13 PART 2] Hopeful & Excited...")
        all_results = []
        for cat, queries in self.search_queries.items():
            print(f"  {cat}...", end=' ')
            results = self.scrape_vibe_category(cat, queries, 10)
            all_results.extend(results)
            print(f"{len(results)} songs")
            time.sleep(2)
        return all_results
    
    def save(self, data):
        if not data: return None
        df = pd.DataFrame(data)
        fn = f'reddit_batch13_part2_hopeful_excited_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(fn, index=False)
        print(f"\n[OK] {fn}")
        return fn

def main():
    print("="*70 + "\nBATCH 13 PART 2\n" + "="*70)
    s = Batch13Part2()
    data = s.run_batch()
    if data: s.save(data)

if __name__ == "__main__": main()
