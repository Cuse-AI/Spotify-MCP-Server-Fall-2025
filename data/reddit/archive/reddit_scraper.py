"""
Reddit Vibe Scraper V4 - DIVERSE & CLEAN
Target: Wide genre diversity including edge cases
Focus: Jazz, experimental, noise, world music, and everything in between
"""

import praw
import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import time
import re

load_dotenv()


class RedditVibeScraperV4:
    def __init__(self):
        """Initialize Reddit API with better error handling"""
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )

        # Track scraped posts to avoid duplicates
        self.scraped_post_ids = set()

        # DIVERSE genre-specific search queries
        self.search_queries = {
            # Edge cases - Jazz & Experimental
            'free_jazz': ['free jazz recommendations', 'spiritual jazz', 'avant-garde jazz', 'Albert Ayler type music'],
            'experimental': ['experimental music recommendations', 'noise music', 'avant-garde music', 'musique concrète'],
            'contemporary_classical': ['contemporary classical', 'modern composition', 'minimalist music', 'Steve Reich type music'],

            # World & Folk
            'world_music': ['world music recommendations', 'African music', 'Middle Eastern music', 'traditional music'],
            'folk_deep': ['obscure folk', 'traditional folk', 'Appalachian music', 'sea shanties serious'],

            # Electronic deep cuts
            'ambient': ['ambient music recommendations', 'drone music', 'dark ambient', 'Brian Eno type'],
            'idm': ['IDM recommendations', 'intelligent dance music', 'Aphex Twin type', 'glitch music'],

            # Rock/Metal diversity
            'prog': ['progressive rock', 'krautrock', 'psychedelic rock obscure', 'space rock'],
            'metal_variety': ['doom metal', 'post-metal', 'black metal atmospheric', 'sludge metal'],

            # Hip-hop depth
            'underground_hiphop': ['underground hip hop', 'experimental hip hop', 'abstract hip hop', 'instrumental hip hop'],

            # Emotional/vibe-based (across genres)
            'grief': ['music for grieving', 'sad music cathartic', 'music for loss', 'emotional release music'],
            'introspection': ['introspective music', 'contemplative music', 'music for thinking', 'philosophical music'],
            'energy': ['high energy music', 'adrenaline music', 'pump up music non-mainstream'],
            'nostalgia': ['nostalgic music', 'bittersweet music', 'melancholic but beautiful'],
            'meditation': ['meditative music', 'transcendent music', 'spiritual music non-religious'],

            # Discovery-focused
            'hidden_gems': ['hidden gem albums', 'underrated artists', 'deep cuts', 'lesser known music'],
            'best_unknown': ['best unknown songs', 'obscure recommendations', 'music nobody knows'],
        }

        # Subreddits with diverse tastes
        self.subreddits = [
            'musicsuggestions',
            'ifyoulikeblank',
            'ListenToThis',
            'jazz',
            'experimentalmusic',
            'ambientmusic',
            'electronicmusic',
            'Metal',
            'hiphopheads',
            'indieheads',
            'psychedelicrock',
            'LetsTalkMusic',
            'FolkPunk',
            'WorldMusic'
        ]

    def is_valid_song_name(self, song):
        """Strict validation for song names"""
        if not song or len(song) < 3 or len(song) > 150:
            return False

        # No URLs or URL fragments
        if 'http' in song.lower() or 'www.' in song.lower():
            return False

        # No long random strings (URL fragments)
        if re.search(r'[A-Za-z0-9]{20,}', song):
            return False

        # No markdown artifacts
        if '[' in song or ']' in song:
            return False

        # Must start with alphanumeric or quote
        if not re.match(r'^[A-Za-z0-9\"\']', song):
            return False

        return True

    def is_valid_artist_name(self, artist):
        """Strict validation for artist names"""
        if not artist or len(artist) < 2 or len(artist) > 100:
            return False

        # No URLs
        if 'http' in artist.lower() or 'www.' in artist.lower():
            return False

        # No long random strings
        if re.search(r'[A-Za-z0-9]{15,}', artist):
            return False

        # No sentence fragments (common parsing error)
        sentence_words = ['is', 'the', 'was', 'from', 'does', 'has', 'movie', 'song', 'album', 'similar', 'like']
        words = artist.lower().split()
        if len(words) > 4:
            if sum(1 for w in words if w in sentence_words) > 2:
                return False

        # No markdown
        if '[' in artist or ']' in artist:
            return False

        return True

    def extract_songs_improved(self, text):
        """
        Improved song/artist extraction with multiple patterns
        Priority order ensures best matches first
        """
        songs = []
        text = text.replace('\n\n', ' ').replace('\n', ' ')  # Clean newlines

        # Priority 1: Quoted song with "by"
        # "Song Name" by Artist Name
        pattern1 = r'"([^"]{3,100})"\s+by\s+([A-Z][A-Za-z\s\'\-&\.]{1,50})'
        matches = re.findall(pattern1, text, re.IGNORECASE)
        for song, artist in matches:
            song, artist = song.strip(), artist.strip()
            if self.is_valid_song_name(song) and self.is_valid_artist_name(artist):
                songs.append({
                    'song': song,
                    'artist': artist,
                    'confidence': 'high',
                    'method': 'quoted_by'
                })

        # Priority 2: Artist - Song (with proper capitalization)
        # Artist Name - Song Title
        pattern2 = r'([A-Z][A-Za-z\s&\'\-\.]{2,50})\s+-\s+([A-Z][^,\n\(\)]{3,100}?)(?=\s*[,\.\n]|$)'
        matches = re.findall(pattern2, text)
        for artist, song in matches:
            artist, song = artist.strip(), song.strip()
            if self.is_valid_song_name(song) and self.is_valid_artist_name(artist):
                # Check if not already added (might match pattern1 too)
                if not any(s['song'] == song and s['artist'] == artist for s in songs):
                    songs.append({
                        'song': song,
                        'artist': artist,
                        'confidence': 'medium',
                        'method': 'dash_format'
                    })

        # Priority 3: Unquoted "Song by Artist"
        pattern3 = r'([A-Z][A-Za-z0-9\s\'\-]{3,100})\s+by\s+([A-Z][A-Za-z\s\'\-&\.]{2,50})'
        matches = re.findall(pattern3, text)
        for song, artist in matches:
            song, artist = song.strip(), artist.strip()
            # Extra validation - no periods mid-sentence
            if '.' in song[:-1] or '.' in artist[:-1]:
                continue
            if self.is_valid_song_name(song) and self.is_valid_artist_name(artist):
                if not any(s['song'] == song and s['artist'] == artist for s in songs):
                    songs.append({
                        'song': song,
                        'artist': artist,
                        'confidence': 'medium',
                        'method': 'unquoted_by'
                    })

        return songs

    def search_diverse_queries(self, max_posts_per_query=10):
        """
        Search for diverse genre-specific queries
        Ensures we get edge cases and variety
        """
        all_posts = []

        for genre, queries in self.search_queries.items():
            print(f"\n[>>] Searching {genre}...")

            for query in queries:
                try:
                    # Search across multiple subreddits
                    subreddit_query = '+'.join(self.subreddits[:5])  # Top 5 diverse subs
                    subreddit = self.reddit.subreddit(subreddit_query)

                    search_results = subreddit.search(
                        query,
                        limit=max_posts_per_query,
                        time_filter='year',
                        sort='relevance'
                    )

                    for post in search_results:
                        # Skip if already scraped
                        if post.id in self.scraped_post_ids:
                            continue

                        # Skip non-music posts
                        if any(word in post.title.lower() for word in ['concert', 'tour', 'drama', 'died', 'lawsuit']):
                            continue

                        # Must have comments to be useful
                        if post.num_comments < 3:
                            continue

                        self.scraped_post_ids.add(post.id)

                        post_data = {
                            'post_id': post.id,
                            'subreddit': post.subreddit.display_name,
                            'title': post.title,
                            'selftext': post.selftext,
                            'score': post.score,
                            'num_comments': post.num_comments,
                            'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
                            'permalink': f"https://reddit.com{post.permalink}",
                            'genre_category': genre,
                            'search_query': query,
                            'comments': []
                        }

                        # Get comments
                        post.comments.replace_more(limit=0)
                        for comment in post.comments.list()[:30]:  # Top 30 comments
                            if comment.score >= 1 and len(comment.body) > 20:
                                # Extract songs from comment
                                extracted_songs = self.extract_songs_improved(comment.body)

                                if extracted_songs:
                                    post_data['comments'].append({
                                        'comment_id': comment.id,
                                        'body': comment.body[:500],  # Truncate long comments
                                        'score': comment.score,
                                        'extracted_songs': extracted_songs
                                    })

                        # Only keep posts with useful comments
                        if len(post_data['comments']) >= 2:
                            all_posts.append(post_data)
                            print(f"  [+] {post.title[:60]}... ({len(post_data['comments'])} recommendations)")

                    time.sleep(1)  # Rate limiting

                except Exception as e:
                    print(f"  [X] Error with query '{query}': {e}")
                    continue

        print(f"\n[STATS] Total posts collected: {len(all_posts)}")
        print(f"        Unique posts: {len(self.scraped_post_ids)}")

        return all_posts

    def create_training_format(self, posts_data):
        """Convert to flat training format"""
        rows = []

        for post in posts_data:
            vibe_request = post['title']
            if post['selftext']:
                vibe_request += f" | {post['selftext'][:200]}"

            for comment in post['comments']:
                for song_data in comment['extracted_songs']:
                    row = {
                        'source': 'reddit_v4',
                        'genre_category': post['genre_category'],
                        'subreddit': post['subreddit'],
                        'vibe_request': vibe_request,
                        'song_name': song_data['song'],
                        'artist_name': song_data['artist'],
                        'extraction_confidence': song_data['confidence'],
                        'extraction_method': song_data['method'],
                        'comment_context': comment['body'][:300],
                        'comment_score': comment['score'],
                        'post_score': post['score'],
                        'search_query': post['search_query'],
                        'permalink': post['permalink']
                    }
                    rows.append(row)

        return pd.DataFrame(rows)

    def save_data(self, posts_data):
        """Save both JSON and CSV formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Full JSON
        json_path = f"reddit_v4_diverse_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Saved JSON: {json_path}")

        # Training CSV
        df = self.create_training_format(posts_data)
        csv_path = f"reddit_v4_training_{timestamp}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"[OK] Saved CSV: {csv_path}")

        # Stats
        print(f"\n📊 STATISTICS:")
        print(f"   Total songs extracted: {len(df)}")
        print(f"   Unique songs: {len(df[['song_name', 'artist_name']].drop_duplicates())}")
        print(f"   Genre categories: {df['genre_category'].nunique()}")
        print(f"\nGenre distribution:")
        for genre, count in df['genre_category'].value_counts().items():
            print(f"   {genre}: {count} songs")

        return json_path, csv_path


def main():
    print("=" * 70)
    print("REDDIT VIBE SCRAPER V4 - DIVERSE & CLEAN")
    print("=" * 70)
    print("\nGoals:")
    print("  [OK] Wide genre diversity (jazz, experimental, world, etc.)")
    print("  [OK] Edge cases included (Albert Ayler, noise music, etc.)")
    print("  [OK] Better parsing (no flipped names, no gibberish)")
    print("  [OK] Deduplication (no repeated posts)")
    print("  [OK] Quality filters built-in")
    print()

    scraper = RedditVibeScraperV4()

    print("Starting diverse data collection...")
    posts_data = scraper.search_diverse_queries(max_posts_per_query=10)

    if len(posts_data) > 0:
        json_path, csv_path = scraper.save_data(posts_data)
        print()
        print("=" * 70)
        print("[OK] SCRAPING COMPLETE!")
        print("=" * 70)
        print(f"\nFiles created:")
        print(f"  {json_path}")
        print(f"  {csv_path}")
        print()
        print("Next steps:")
        print("  1. Review the CSV for quality")
        print("  2. Run 1_extract_clean.py to add to master file")
        print("  3. Check genre diversity coverage")
    else:
        print("\n[!] No data collected. Check API credentials and search queries.")


if __name__ == "__main__":
    main()
