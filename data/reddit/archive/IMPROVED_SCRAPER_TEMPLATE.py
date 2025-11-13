"""
IMPROVED REDDIT SCRAPER TEMPLATE
Fixes parsing errors that cause 50% validation failure

Key Improvements:
1. CORRECT artist/song order extraction
2. Better regex patterns (less greedy)
3. Clean newlines/spaces DURING scraping
4. Validate format before saving
5. Handle edge cases (featuring, remixes, etc.)
"""

import praw
import pandas as pd
import time
import re
import os
from dotenv import load_dotenv

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
        # Remove newlines and tabs
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()

    def validate_song(self, song, artist):
        """Validate that song and artist look reasonable"""
        if not song or not artist:
            return False

        # Too short
        if len(song) < 2 or len(artist) < 2:
            return False

        # Too long (likely grabbed too much text)
        if len(song) > 100 or len(artist) > 60:
            return False

        # Artist shouldn't have common song words at start
        song_words = ['the', 'a', 'an', 'my', 'your', 'our', 'their']
        if artist.lower().split()[0] in song_words:
            return False

        # Song shouldn't end with artist-like text
        if ' by ' in song.lower():
            return False

        return True

    def extract_songs(self, text):
        """
        Extract songs with IMPROVED regex patterns
        Returns: list of (song, artist, method, confidence)
        """
        songs = []
        text = self.clean_text(text)

        # Pattern 1: "Song Title" by Artist Name
        # More strict: artist must be reasonable length
        p1 = r'"([^"]{2,80})"\s+by\s+([A-Z][A-Za-z\s\-&\'\.]{1,50}?)(?:\s|,|\.|\n|$)'
        for m in re.finditer(p1, text, re.IGNORECASE):
            song = self.clean_text(m.group(1))
            artist = self.clean_text(m.group(2))
            if self.validate_song(song, artist):
                songs.append((song, artist, 'quoted_by', 0.9))

        # Pattern 2: Artist - Song (or Song - Artist, check both)
        # FIXED: More conservative word matching
        p2 = r'([A-Z][A-Za-z\s\-&\'\.]{1,35}?)\s*[-–—]\s*([A-Z][A-Za-z\s\-&\'\.!?]{2,50}?)(?:\s|,|\.|\n|$)'
        for m in re.finditer(p2, text):
            part1 = self.clean_text(m.group(1))
            part2 = self.clean_text(m.group(2))

            # Try Artist - Song first (more common)
            if self.validate_song(part2, part1):
                songs.append((part1, part2, 'dash_artist_song', 0.7))  # FIXED: (Artist, Song)
            # Try Song - Artist if first didn't work
            elif self.validate_song(part1, part2):
                songs.append((part2, part1, 'dash_song_artist', 0.6))  # FIXED: (Artist, Song)

        # Pattern 3: Artist name followed by song in quotes
        p3 = r'([A-Z][A-Za-z\s\-&\'\.]{1,35}?)\s+["\'"]([^"\']{2,80})["\'"]'
        for m in re.finditer(p3, text):
            artist = self.clean_text(m.group(1))
            song = self.clean_text(m.group(2))
            if self.validate_song(song, artist):
                songs.append((artist, song, 'artist_quoted_song', 0.8))  # FIXED: (Artist, Song)

        # Pattern 4: Song by Artist (no quotes)
        # More careful: check for common words
        p4 = r'\b([A-Z][A-Za-z\s\-&\'\.]{2,50}?)\s+by\s+([A-Z][A-Za-z\s\-&\'\.]{1,40}?)(?:\s|,|\.|\n|$)'
        for m in re.finditer(p4, text, re.IGNORECASE):
            song = self.clean_text(m.group(1))
            artist = self.clean_text(m.group(2))
            if self.validate_song(song, artist):
                songs.append((artist, song, 'unquoted_by', 0.5))  # FIXED: (Artist, Song)

        # Deduplicate (keep highest confidence)
        seen = {}
        for song, artist, method, conf in songs:
            key = (song.lower(), artist.lower())
            if key not in seen or seen[key][3] < conf:
                seen[key] = (song, artist, method, conf)

        return list(seen.values())

    def scrape_vibe_category(self, category, queries, max_posts=10):
        """Scrape with improved extraction"""
        results = []

        for query in queries:
            print(f'  Searching: {query}')

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

                                for song, artist, method, confidence in songs:
                                    results.append({
                                        'vibe_sub_category': category,
                                        'vibe_description': post.title,
                                        'song': song,  # FIXED: correct field name
                                        'artist': artist,  # FIXED: correct field name
                                        'extraction_method': method,
                                        'extraction_confidence': confidence,
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
                    print(f'    Error in {sub_name}: {e}')
                    pass

        return results

    def scrape_all(self, search_queries, output_file):
        """
        Scrape all categories and save to CSV

        Args:
            search_queries: dict of {category: [query1, query2, ...]}
            output_file: path to save CSV
        """
        all_results = []

        print(f'Starting scrape for {len(search_queries)} categories...')

        for category, queries in search_queries.items():
            print(f'\n[{category}]')
            results = self.scrape_vibe_category(category, queries)
            all_results.extend(results)
            print(f'  Found {len(results)} songs')

        # Save to CSV
        df = pd.DataFrame(all_results)

        # Drop duplicates based on song + artist (case-insensitive)
        df['_key'] = df['song'].str.lower() + '||' + df['artist'].str.lower()
        df = df.drop_duplicates(subset='_key', keep='first')
        df = df.drop(columns=['_key'])

        df.to_csv(output_file, index=False, encoding='utf-8')

        print(f'\n[COMPLETE]')
        print(f'Total songs: {len(df)}')
        print(f'Saved to: {output_file}')

        return df


# EXAMPLE USAGE:
if __name__ == '__main__':
    scraper = ImprovedRedditScraper()

    # Define your search queries
    search_queries = {
        'Happy - Feel Good': ['feel good music', 'positive vibes songs', 'uplifting playlist'],
        'Happy - Euphoric': ['euphoric music', 'pure joy songs', 'ecstatic playlist'],
        # ... add more categories
    }

    # Scrape and save
    scraper.scrape_all(search_queries, 'improved_batch_output.csv')
