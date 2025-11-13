"""
Extract Clean, High-Quality Data from All Scraped Sources
Filters out noise, gibberish, and low-quality entries
Creates a master clean dataset ready for use
"""

import pandas as pd
import json
import re
from datetime import datetime
import os

print("=" * 70)
print("EXTRACTING CLEAN DATA FROM ALL SOURCES")
print("=" * 70)
print()

class DataCleaner:
    def __init__(self):
        self.clean_data = []

    def is_valid_song_name(self, song):
        """Check if song name looks legitimate"""
        if not song or pd.isna(song):
            return False

        song = str(song).strip()

        # Too short or too long
        if len(song) < 3 or len(song) > 150:
            return False

        # Contains URLs
        if 'http' in song.lower() or 'www.' in song.lower():
            return False

        # Contains weird URL fragments
        if re.search(r'[A-Za-z0-9]{20,}', song):  # Long random strings
            return False

        # Contains markdown artifacts
        if '[' in song or ']' in song or song.startswith('(') or song.endswith(')'):
            return False

        # Starts with weird characters
        if re.match(r'^[^A-Za-z0-9\"\']', song):
            return False

        # Too many special characters
        special_count = sum(1 for c in song if not c.isalnum() and c not in ' \'-.,!?&()"')
        if special_count > len(song) * 0.3:
            return False

        return True

    def is_valid_artist_name(self, artist):
        """Check if artist name looks legitimate"""
        if not artist or pd.isna(artist):
            return False

        artist = str(artist).strip()

        # Too short or too long
        if len(artist) < 2 or len(artist) > 100:
            return False

        # Contains URLs or fragments
        if 'http' in artist.lower() or 'www.' in artist.lower():
            return False

        if re.search(r'[A-Za-z0-9]{15,}', artist):  # Long random strings
            return False

        # Contains sentence fragments (common parsing error)
        sentence_words = ['is', 'the', 'was', 'from', 'does', 'has', 'movie', 'song', 'album']
        words = artist.lower().split()
        if len(words) > 4 and any(w in sentence_words for w in words):
            return False

        # Contains markdown
        if '[' in artist or ']' in artist:
            return False

        return True

    def clean_reddit_data(self, filepath):
        """Extract clean data from Reddit CSV files"""
        print(f"Processing: {filepath}")

        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            print(f"  Total rows: {len(df)}")

            # Filter for valid entries
            valid_mask = (
                df['song_name'].apply(self.is_valid_song_name) &
                df['artist_name'].apply(self.is_valid_artist_name) &
                (df['comment_score'].notna()) &
                (df['comment_score'] >= 1)  # At least 1 upvote
            )

            clean_df = df[valid_mask].copy()
            print(f"  Clean rows: {len(clean_df)}")

            # Add source info
            clean_df['data_source'] = 'reddit'
            clean_df['quality_score'] = clean_df['comment_score']

            # Keep only essential columns
            essential_cols = [
                'vibe_request_title', 'vibe_request_full', 'song_name',
                'artist_name', 'comment_score', 'subreddit',
                'extraction_method', 'permalink', 'data_source', 'quality_score'
            ]

            available_cols = [col for col in essential_cols if col in clean_df.columns]
            return clean_df[available_cols]

        except Exception as e:
            print(f"  ERROR: {e}")
            return pd.DataFrame()

    def analyze_diversity(self, df):
        """Analyze genre and artist diversity"""
        print()
        print("=" * 70)
        print("DIVERSITY ANALYSIS")
        print("=" * 70)

        # Top artists (to see if we're too focused)
        print("\nTop 20 Most Recommended Artists:")
        top_artists = df['artist_name'].value_counts().head(20)
        for i, (artist, count) in enumerate(top_artists.items(), 1):
            print(f"  {i:2d}. {artist}: {count} recommendations")

        # Subreddit diversity
        if 'subreddit' in df.columns:
            print("\nSubreddit Distribution:")
            for sub, count in df['subreddit'].value_counts().items():
                print(f"  r/{sub}: {count} songs")

        # Check for repetition
        unique_songs = len(df[['song_name', 'artist_name']].drop_duplicates())
        total_songs = len(df)
        repetition_rate = (1 - unique_songs / total_songs) * 100

        print(f"\nRepetition Analysis:")
        print(f"  Total entries: {total_songs}")
        print(f"  Unique songs: {unique_songs}")
        print(f"  Repetition rate: {repetition_rate:.1f}%")

        if repetition_rate > 30:
            print(f"  WARNING: High repetition! Same songs appearing multiple times")

        return {
            'top_artists': top_artists,
            'unique_songs': unique_songs,
            'repetition_rate': repetition_rate
        }

    def flag_edge_cases(self, df):
        """Identify underrepresented genres/artists that should be included"""
        print()
        print("=" * 70)
        print("EDGE CASE DETECTION")
        print("=" * 70)

        # Keywords that indicate interesting edge cases
        edge_case_keywords = [
            'jazz', 'experimental', 'noise', 'avant', 'free jazz',
            'classical', 'opera', 'world', 'folk', 'bluegrass',
            'metal', 'doom', 'black metal', 'death metal',
            'ambient', 'drone', 'minimalist', 'contemporary classical',
            'obscure', 'underground', 'lesser known', 'hidden gem',
            'deep cut', 'b-side', 'rare'
        ]

        # Search in vibe requests
        edge_cases = []
        for keyword in edge_case_keywords:
            if 'vibe_request_full' in df.columns:
                matches = df[df['vibe_request_full'].str.contains(keyword, case=False, na=False)]
                if len(matches) > 0:
                    edge_cases.append({
                        'keyword': keyword,
                        'count': len(matches),
                        'examples': matches['artist_name'].head(3).tolist()
                    })

        print("\nEdge Case Genres Found:")
        edge_cases_sorted = sorted(edge_cases, key=lambda x: x['count'], reverse=True)
        for case in edge_cases_sorted[:15]:
            print(f"  '{case['keyword']}': {case['count']} mentions")
            # Clean examples for printing (remove emojis/special chars)
            clean_examples = [ex.encode('ascii', 'ignore').decode('ascii') for ex in case['examples']]
            print(f"    Examples: {', '.join(clean_examples)}")

        if len(edge_cases) < 5:
            print("\n  WARNING: Very few edge cases found!")
            print("  Consider adding more diverse genre queries to scraper")

        return edge_cases

    def create_master_clean_file(self, all_data):
        """Create the final master clean file"""
        print()
        print("=" * 70)
        print("CREATING MASTER CLEAN FILE")
        print("=" * 70)

        # Combine all clean data
        master_df = pd.concat(all_data, ignore_index=True)

        # Remove exact duplicates
        print(f"\nBefore deduplication: {len(master_df)} rows")
        master_df = master_df.drop_duplicates(subset=['song_name', 'artist_name', 'vibe_request_title'])
        print(f"After deduplication: {len(master_df)} rows")

        # Sort by quality score
        if 'quality_score' in master_df.columns:
            master_df = master_df.sort_values('quality_score', ascending=False)

        # Save master file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"MASTER_CLEAN_VIBES_{timestamp}.csv"
        master_df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n[OK] Saved: {filename}")

        # Create summary
        summary_file = f"MASTER_CLEAN_SUMMARY_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("VIBECHECK MASTER CLEAN DATA SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total Clean Entries: {len(master_df)}\n")
            f.write(f"Unique Songs: {len(master_df[['song_name', 'artist_name']].drop_duplicates())}\n\n")

            if 'subreddit' in master_df.columns:
                f.write("Source Distribution:\n")
                for source, count in master_df['subreddit'].value_counts().items():
                    f.write(f"  {source}: {count}\n")

            f.write("\nTop 50 Artists:\n")
            for i, (artist, count) in enumerate(master_df['artist_name'].value_counts().head(50).items(), 1):
                f.write(f"  {i:2d}. {artist}: {count}\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("QUALITY FILTERS APPLIED:\n")
            f.write("=" * 70 + "\n")
            f.write("[X] Removed URL fragments and markdown artifacts\n")
            f.write("[X] Removed gibberish and random character strings\n")
            f.write("[X] Validated song names (3-150 chars)\n")
            f.write("[X] Validated artist names (2-100 chars)\n")
            f.write("[X] Removed low-score recommendations\n")
            f.write("[X] Removed exact duplicates\n")

        print(f"[OK] Saved summary: {summary_file}")

        return master_df, filename


def main():
    cleaner = DataCleaner()
    all_clean_data = []

    # Process Reddit files
    reddit_files = [
        'reddit/reddit_clean_master.csv',
        'reddit/reddit_vibe_context_training_20251107_135330.csv',
        'reddit/reddit_v2_20251107_135216.csv'
    ]

    print("STEP 1: EXTRACTING CLEAN DATA")
    print("-" * 70)
    for filepath in reddit_files:
        if os.path.exists(filepath):
            clean_df = cleaner.clean_reddit_data(filepath)
            if len(clean_df) > 0:
                all_clean_data.append(clean_df)
        else:
            print(f"  Skipping (not found): {filepath}")

    if not all_clean_data:
        print("\n[X] ERROR: No clean data extracted!")
        return

    # Combine and analyze
    print("\nSTEP 2: COMBINING DATA")
    print("-" * 70)
    combined_df = pd.concat(all_clean_data, ignore_index=True)
    print(f"Total combined rows: {len(combined_df)}")

    # Analyze diversity
    print("\nSTEP 3: ANALYZING DIVERSITY")
    print("-" * 70)
    diversity_stats = cleaner.analyze_diversity(combined_df)

    # Flag edge cases
    print("\nSTEP 4: DETECTING EDGE CASES")
    print("-" * 70)
    edge_cases = cleaner.flag_edge_cases(combined_df)

    # Create master file
    print("\nSTEP 5: CREATING MASTER FILE")
    print("-" * 70)
    master_df, filename = cleaner.create_master_clean_file(all_clean_data)

    print()
    print("=" * 70)
    print("[DONE] EXTRACTION COMPLETE!")
    print("=" * 70)
    print(f"\nClean data saved to: {filename}")
    print(f"Total clean entries: {len(master_df)}")
    print(f"Unique songs: {len(master_df[['song_name', 'artist_name']].drop_duplicates())}")
    print()
    print("Next steps:")
    print("1. Review the master file for quality")
    print("2. Check the diversity analysis")
    print("3. Identify missing genres for next scrape")
    print("4. Run improved scraper with diverse queries")


if __name__ == "__main__":
    main()
