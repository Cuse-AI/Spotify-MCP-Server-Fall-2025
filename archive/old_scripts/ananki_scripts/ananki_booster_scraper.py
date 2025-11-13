"""
Ananki Booster Scraper System
==============================

Targeted scrapers to fill gaps in the tapestry.
Each booster targets specific vibes that need more songs/artists.

USAGE:
  python ananki_booster_scraper.py --vibe "Focus/Study" --count 50
  python ananki_booster_scraper.py --vibe "Rainy/Cozy" --count 30

This will:
1. Generate targeted Reddit queries for that vibe
2. Scrape human recommendations
3. Attach new songs/artists to the vibe node
4. Update tapestry_map.json
"""

import praw
import pandas as pd
import json
import re
import time
import argparse
from collections import defaultdict
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('reddit/.env')

# ============================================================================
# VIBE-SPECIFIC SEARCH QUERIES
# ============================================================================

# Ananki's curated search queries for each vibe
VIBE_QUERY_MAP = {
    'Focus/Study': [
        'music for studying and concentration',
        'focus music recommendations',
        'best study playlist songs',
        'concentration music no lyrics',
        'productive work music',
        'ambient music for focus',
        'lo-fi study beats alternatives',
    ],
    
    'Rainy/Cozy': [
        'rainy day music recommendations',
        'cozy music for rainy weather',
        'music for grey days',
        'rainy afternoon playlist',
        'comfort music for rain',
        'songs that feel like sweater weather',
    ],
    
    'Innovative/Unique': [
        'weird unique music recommendations',
        'experimental music suggestions',
        'strange beautiful songs',
        'unconventional music',
        'avant-garde recommendations',
        'music that sounds like nothing else',
    ],
    
    'Rebellious/Punk': [
        'punk rock recommendations',
        'rebellious music',
        'anti-establishment songs',
        'punk alternatives',
        'protest music modern',
        'anarchist punk bands',
    ],
    
    'Epic/Cinematic': [
        'epic cinematic music',
        'orchestral dramatic songs',
        'music that feels like a movie',
        'sweeping cinematic tracks',
        'post-rock epic builds',
        'soundtrack-like music',
    ],
    
    'Energetic/Motivational': [
        'motivational workout music',
        'hype songs for exercise',
        'pump up music recommendations',
        'confidence boosting songs',
        'empowering music',
        'badass energy songs',
    ],
    
    'Nostalgic': [
        'nostalgic music recommendations',
        '90s throwback songs',
        '2000s nostalgia playlist',
        'childhood memory songs',
        'music that brings you back',
    ],
    
    'Ethereal/Dreamy': [
        'ethereal dreamy music',
        'shoegaze recommendations',
        'ambient dreamy songs',
        'floating atmospheric music',
        'celestial music',
        'music that sounds like dreams',
    ],
    
    'Introspective/Thoughtful': [
        'introspective music recommendations',
        'thoughtful deep songs',
        'philosophical music',
        'contemplative playlist',
        'reflective music',
    ],
    
    'Dark/Atmospheric': [
        'dark atmospheric music',
        'brooding moody songs',
        'gothic atmospheric recommendations',
        'dark ambient music',
        'haunting music',
    ],
    
    'Party/Dance': [
        'party music recommendations',
        'dance floor bangers',
        'club music playlist',
        'groovy dance songs',
        'music for house parties',
    ],
    
    'Night/Sleep': [
        'late night music',
        '3am playlist songs',
        'midnight music recommendations',
        'insomnia music',
        'nocturnal listening',
    ],
    
    'Driving/Travel': [
        'road trip music',
        'driving playlist recommendations',
        'highway cruising songs',
        'long drive music',
        'adventure travel soundtrack',
    ],
    
    'Romantic/Sensual': [
        'romantic music recommendations',
        'sensual songs',
        'intimate music playlist',
        'love songs not cheesy',
        'seductive music',
    ],
    
    'Happy/Upbeat': [
        'happy upbeat music',
        'feel good songs',
        'positive energy music',
        'cheerful playlist',
        'uplifting music',
    ],
    
    'Chill/Relaxing': [
        'chill relaxing music',
        'laid back songs',
        'mellow music recommendations',
        'relaxation playlist',
        'calm vibes music',
    ],
    
    'Angry/Intense': [
        'angry intense music',
        'aggressive songs',
        'rage music recommendations',
        'heavy intense tracks',
        'cathartic angry music',
    ],
    
    'Emotional/Sad': [
        'sad emotional music',
        'heartbreak songs',
        'melancholic music recommendations',
        'crying music playlist',
        'beautiful sad songs',
    ],
    
    'Discovery/Exploration': [
        'hidden gem music recommendations',
        'underrated songs',
        'obscure music discoveries',
        'unknown artist recommendations',
        'deep cuts music',
    ],
}

# ============================================================================
# REDDIT SCRAPING
# ============================================================================

class BoosterScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        self.subreddits = [
            'musicsuggestions',
            'ifyoulikeblank',
            'listentothis',
            'Music',
        ]
    
    def extract_songs_from_comment(self, comment_text):
        """Extract song/artist pairs from comment text"""
        songs = []
        
        # Pattern 1: "Song" by Artist
        pattern1 = r'"([^"]+)"\s+by\s+([A-Z][^,.\n]+)'
        matches1 = re.finditer(pattern1, comment_text, re.IGNORECASE)
        for match in matches1:
            songs.append((match.group(1).strip(), match.group(2).strip()))
        
        # Pattern 2: Artist - Song
        pattern2 = r'([A-Z][A-Za-z\s&]+?)\s*-\s*([A-Z][^-\n]+?)(?:\s|,|\.|\n|$)'
        matches2 = re.finditer(pattern2, comment_text, re.IGNORECASE)
        for match in matches2:
            # Skip if looks like title format
            if len(match.group(2)) > 50:
                continue
            songs.append((match.group(2).strip(), match.group(1).strip()))
        
        return songs
    
    def scrape_for_vibe(self, vibe, target_count=50):
        """Scrape Reddit for songs matching a specific vibe"""
        
        queries = VIBE_QUERY_MAP.get(vibe, [])
        if not queries:
            print(f"[WARNING] No queries defined for vibe: {vibe}")
            return []
        
        print(f"\n[SCRAPING] {vibe} (target: {target_count} songs)")
        
        all_songs = []
        seen_songs = set()
        
        for query in queries:
            if len(all_songs) >= target_count:
                break
            
            print(f"  Searching: '{query}'...")
            
            try:
                # Search across subreddits
                for subreddit_name in self.subreddits:
                    if len(all_songs) >= target_count:
                        break
                    
                    subreddit = self.reddit.subreddit(subreddit_name)
                    posts = subreddit.search(query, limit=5, time_filter='year')
                    
                    for post in posts:
                        # Get comments
                        post.comments.replace_more(limit=0)
                        for comment in post.comments.list()[:20]:
                            if hasattr(comment, 'body'):
                                songs = self.extract_songs_from_comment(comment.body)
                                
                                for song, artist in songs:
                                    song_key = (song.lower(), artist.lower())
                                    if song_key not in seen_songs:
                                        all_songs.append({
                                            'song': song,
                                            'artist': artist,
                                            'vibe': vibe,
                                            'query': query,
                                            'comment_score': comment.score,
                                            'subreddit': subreddit_name,
                                            'source_url': f"https://reddit.com{comment.permalink}"
                                        })
                                        seen_songs.add(song_key)
                                        
                                        if len(all_songs) >= target_count:
                                            break
                    
                    time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"    [ERROR] {e}")
                continue
        
        print(f"  Found {len(all_songs)} new songs for {vibe}")
        return all_songs

# ============================================================================
# TAPESTRY UPDATE
# ============================================================================

def update_tapestry(new_songs):
    """Add new songs to the tapestry map"""
    
    # Load existing tapestry
    tapestry_file = 'ananki_outputs/tapestry_map.json'
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Group new songs by vibe
    songs_by_vibe = defaultdict(list)
    for song_data in new_songs:
        songs_by_vibe[song_data['vibe']].append(song_data)
    
    # Add to tapestry
    for vibe, songs in songs_by_vibe.items():
        if vibe not in tapestry['vibes']:
            print(f"[WARNING] Vibe '{vibe}' not in tapestry")
            continue
        
        # Add songs (avoid duplicates)
        existing_songs = {(s['song'].lower(), s['artist'].lower()) 
                         for s in tapestry['vibes'][vibe]['songs']}
        
        new_count = 0
        for song in songs:
            song_key = (song['song'].lower(), song['artist'].lower())
            if song_key not in existing_songs:
                tapestry['vibes'][vibe]['songs'].append(song)
                new_count += 1
        
        # Update artist list
        all_artists = {s['artist'] for s in tapestry['vibes'][vibe]['songs']}
        tapestry['vibes'][vibe]['artists'] = sorted(list(all_artists))
        
        # Update counts
        tapestry['vibes'][vibe]['song_count'] = len(tapestry['vibes'][vibe]['songs'])
        tapestry['vibes'][vibe]['artist_count'] = len(tapestry['vibes'][vibe]['artists'])
        
        print(f"  Added {new_count} new songs to {vibe}")
    
    # Update stats
    tapestry['stats']['total_songs'] = sum(v['song_count'] for v in tapestry['vibes'].values())
    tapestry['stats']['total_artists'] = sum(v['artist_count'] for v in tapestry['vibes'].values())
    
    # Save
    with open(tapestry_file, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Updated tapestry: {tapestry_file}")
    return tapestry

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Boost specific vibes in the tapestry')
    parser.add_argument('--vibe', type=str, help='Vibe to boost')
    parser.add_argument('--count', type=int, default=50, help='Target number of songs')
    parser.add_argument('--all-low', action='store_true', help='Boost all vibes with <30 songs')
    
    args = parser.parse_args()
    
    print("="*70)
    print("ANANKI BOOSTER SCRAPER")
    print("="*70)
    
    scraper = BoosterScraper()
    all_new_songs = []
    
    if args.all_low:
        # Auto-boost all low-count vibes
        print("\n[MODE] Boosting all vibes with <30 songs")
        
        with open('ananki_outputs/tapestry_map.json', 'r') as f:
            tapestry = json.load(f)
        
        for vibe, data in tapestry['vibes'].items():
            if data['song_count'] < 30:
                needed = 30 - data['song_count']
                print(f"\n{vibe}: {data['song_count']} songs (needs {needed} more)")
                new_songs = scraper.scrape_for_vibe(vibe, target_count=needed)
                all_new_songs.extend(new_songs)
                time.sleep(2)
    
    elif args.vibe:
        # Boost specific vibe
        new_songs = scraper.scrape_for_vibe(args.vibe, target_count=args.count)
        all_new_songs = new_songs
    
    else:
        print("[ERROR] Must specify --vibe or --all-low")
        exit(1)
    
    # Update tapestry
    if all_new_songs:
        tapestry = update_tapestry(all_new_songs)
        
        print(f"\n" + "="*70)
        print("BOOST COMPLETE")
        print("="*70)
        print(f"\nTotal new songs added: {len(all_new_songs)}")
        print(f"Total songs in tapestry: {tapestry['stats']['total_songs']}")
        print(f"Total artists in tapestry: {tapestry['stats']['total_artists']}")
    else:
        print("\n[WARNING] No new songs found")
