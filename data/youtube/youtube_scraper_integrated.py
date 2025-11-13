"""
YouTube Scraper - ENHANCED WITH COMMENTS & FLOW ANALYSIS
Captures the temporal lens: sequences, transitions, emotional arcs
"""

from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import re

load_dotenv()


class YouTubeScraperEnhanced:
    def __init__(self):
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY not found in .env")
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Same vibe-specific searches as before
        self.playlist_searches = {
            'focus_study': [
                'study music playlist',
                'focus concentration music',
                'work from home playlist',
                'productive music mix',
            ],
            'rainy_cozy': [
                'rainy day playlist',
                'cozy vibes music',
                'rainy mood songs',
                'grey day music',
            ],
            'epic': [
                'epic cinematic music',
                'dramatic playlist',
                'movie soundtrack vibes',
                'orchestral epic songs',
            ],
            'night_sleep': [
                'late night vibes',
                '3am playlist',
                'midnight music',
                'insomnia playlist',
            ],
            'emotional_sad': [
                'sad songs playlist',
                'crying music',
                'heartbreak playlist',
                'melancholic vibes',
            ],
            'chill': [
                'chill vibes playlist',
                'relaxing music mix',
                'laid back songs',
                'mellow playlist',
            ],
            'driving': [
                'driving music playlist',
                'road trip vibes',
                'highway music',
                'cruising playlist',
            ],
            'party': [
                'party music playlist',
                'dance vibes',
                'club music mix',
                'hype playlist',
            ],
        }
    
    def clean_song_title(self, title):
        """Clean YouTube video title to get actual song name"""
        # Remove common video suffixes
        title = re.sub(r'\s*\(Official.*?\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\[Official.*?\]', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(Lyrics?\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\[Lyrics?\]', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(Lyric Video\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(Audio\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(Visuali[sz]er\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(Extended\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(Music Video\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(HD\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(HQ\)', '', title, flags=re.IGNORECASE)
        
        # Remove track numbers
        title = re.sub(r'^\d+[\.\)]\s*', '', title)
        title = re.sub(r'^\d+\s+-\s+', '', title)
        
        # Remove prefixes
        title = re.sub(r'^\[.*?\]\s*', '', title)
        
        return title.strip()
    
    def parse_video_title(self, title):
        """Parse 'Artist - Song' from YouTube video title"""
        # Clean first
        title = self.clean_song_title(title)
        
        # Try Artist - Song format
        if ' - ' in title:
            parts = title.split(' - ', 1)
            if len(parts) == 2:
                artist = parts[0].strip()
                song = parts[1].strip()
                
                # Validate lengths
                if 2 < len(artist) < 50 and 2 < len(song) < 100:
                    # Check for weird patterns
                    if '/' in artist or '/' in song:
                        # Might be misparse like "Song / Artist"
                        return None, None
                    return song, artist
        
        return None, None
    
    def search_playlists(self, query, max_results=3):
        """Search for playlists"""
        try:
            response = self.youtube.search().list(
                part='snippet',
                q=query,
                type='playlist',
                maxResults=max_results,
                relevanceLanguage='en'
            ).execute()
            
            playlists = []
            for item in response.get('items', []):
                playlists.append({
                    'playlist_id': item['id']['playlistId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet'].get('description', ''),
                    'channel': item['snippet']['channelTitle']
                })
            
            return playlists
        except Exception as e:
            print(f"    [ERROR] Search: {e}")
            return []
    
    def get_playlist_items(self, playlist_id, max_results=20):
        """Get songs from playlist with video IDs"""
        try:
            response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=max_results
            ).execute()
            
            songs = []
            for item in response.get('items', []):
                title = item['snippet']['title']
                video_id = item['snippet']['resourceId']['videoId']
                
                # Parse artist - song
                song, artist = self.parse_video_title(title)
                
                if song and artist:
                    songs.append({
                        'song': song,
                        'artist': artist,
                        'video_id': video_id,
                        'position': item['snippet']['position'],
                        'original_title': title
                    })
            
            return songs
        except Exception as e:
            print(f"      [ERROR] Items: {e}")
            return []
    
    def get_video_comments(self, video_id, max_comments=10):
        """Get comments from a video for vibe context"""
        try:
            response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_comments,
                order='relevance',
                textFormat='plainText'
            ).execute()
            
            comments = []
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'text': comment['textDisplay'],
                    'likes': comment['likeCount'],
                    'author': comment['authorDisplayName']
                })
            
            return comments
        except Exception as e:
            # Many videos have comments disabled
            return []
    
    def extract_vibe_context_from_comments(self, comments):
        """Extract emotional/vibe language from comments"""
        vibe_phrases = []
        
        vibe_patterns = [
            r'(?:feels? like|sounds? like|reminds me of|vibes? like)\s+([^.!?\n]+)',
            r'(?:perfect for|great for|good for)\s+([^.!?\n]+)',
            r'this (?:song|track|music)\s+(?:is|makes me feel?)\s+([^.!?\n]+)',
            r'when (?:you\'re|im|i\'m)\s+([^.!?\n]+)',
        ]
        
        for comment in comments:
            text = comment['text']
            for pattern in vibe_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    phrase = match.group(1).strip()
                    if len(phrase) > 5 and len(phrase) < 100:
                        vibe_phrases.append({
                            'phrase': phrase,
                            'likes': comment['likes'],
                            'full_comment': text[:200]
                        })
        
        return vibe_phrases
    
    def scrape_category(self, category, queries, playlists_per_query=2):
        """Scrape playlists with comment analysis"""
        results = []
        
        for query in queries:
            print(f"    Query: '{query}'...")
            
            playlists = self.search_playlists(query, max_results=playlists_per_query)
            
            for playlist in playlists:
                title_safe = playlist['title'][:50].encode('ascii', 'ignore').decode('ascii')
                print(f"      Playlist: {title_safe}...")
                
                # Get songs
                songs = self.get_playlist_items(playlist['playlist_id'], max_results=15)
                print(f"        Songs: {len(songs)}")
                
                # For each song, try to get video comments
                for song_data in songs:
                    # Get comments for this specific video
                    comments = self.get_video_comments(song_data['video_id'], max_comments=10)
                    
                    # Extract vibe context from comments
                    vibe_contexts = self.extract_vibe_context_from_comments(comments)
                    
                    # Build rich vibe description
                    vibe_description = f"{playlist['title']}"
                    if playlist['description']:
                        vibe_description += f" - {playlist['description'][:200]}"
                    
                    # Build reasoning with comment context
                    reasoning_parts = [f"From YouTube playlist: {playlist['title']}. Position {song_data['position']+1} in sequence."]
                    
                    # Add best comment context if available
                    if vibe_contexts:
                        # Sort by likes
                        best_context = sorted(vibe_contexts, key=lambda x: x['likes'], reverse=True)[0]
                        reasoning_parts.append(f"Listener context: \"{best_context['phrase']}\" ({best_context['likes']} likes)")
                    
                    recommendation_reasoning = " ".join(reasoning_parts)
                    
                    results.append({
                        'vibe_description': vibe_description,
                        'song_name': song_data['song'],
                        'artist_name': song_data['artist'],
                        'recommendation_reasoning': recommendation_reasoning,
                        'playlist_title': playlist['title'],
                        'playlist_id': playlist['playlist_id'],
                        'sequence_position': song_data['position'],
                        'comment_contexts': len(vibe_contexts),
                        'comment_score': max([v['likes'] for v in vibe_contexts]) if vibe_contexts else 0,
                        'extraction_confidence': 'high' if vibe_contexts else 'medium',
                        'extraction_method': 'youtube_playlist_with_comments',
                        'source_url': f"https://youtube.com/playlist?list={playlist['playlist_id']}",
                        'video_url': f"https://youtube.com/watch?v={song_data['video_id']}",
                        'data_source': 'youtube',
                        'search_query': query,
                        'vibe_category_hint': category,
                    })
                    
                    time.sleep(0.5)  # Rate limiting for comments
                
                print(f"        Comments: {sum(1 for r in results[-len(songs):] if r['comment_contexts'] > 0)}/{len(songs)} songs")
                time.sleep(1)
            
            time.sleep(2)
        
        return results
    
    def run_scrape(self, playlists_per_query=2):
        """Run enhanced YouTube scraping with comments"""
        print("\n[SCRAPING] Collecting from YouTube with comment analysis...")
        
        all_results = []
        for category, queries in self.playlist_searches.items():
            print(f"\n  Category: {category}")
            results = self.scrape_category(category, queries, playlists_per_query)
            all_results.extend(results)
            
            with_comments = sum(1 for r in results if r['comment_contexts'] > 0)
            print(f"  Total: {len(results)} songs ({with_comments} with comment context)")
        
        return all_results
    
    def save_for_ananki(self, data):
        """Save enhanced format for Ananki"""
        if not data:
            print("[WARNING] No data to save")
            return None
        
        df = pd.DataFrame(data)
        
        # Add empty columns for Ananki
        df['vibe_category'] = None
        df['genre_category'] = None
        df['relation_type'] = None
        df['anchor_reference_artist'] = None
        df['anchor_reference_song'] = None
        df['delta_description'] = None
        df['reasoning_text'] = None
        
        # Column order
        column_order = [
            'vibe_category', 'vibe_description', 'song_name', 'artist_name',
            'recommendation_reasoning', 'genre_category',
            'comment_score', 'extraction_confidence', 'source_url', 'data_source',
            'relation_type', 'anchor_reference_artist', 'anchor_reference_song',
            'delta_description', 'reasoning_text'
        ]
        
        # YouTube-specific columns
        youtube_cols = [
            'playlist_title', 'playlist_id', 'sequence_position', 'comment_contexts',
            'video_url', 'extraction_method', 'search_query', 'vibe_category_hint'
        ]
        
        final_cols = column_order + youtube_cols
        df = df[[c for c in final_cols if c in df.columns]]
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'youtube_for_ananki_enhanced_{timestamp}.csv'
        df.to_csv(filename, index=False, encoding='utf-8')
        
        with_comments = (df['comment_contexts'] > 0).sum()
        comment_pct = (with_comments / len(df)) * 100
        
        print(f"\n[OK] Saved: {filename}")
        print(f"     Total songs: {len(df)}")
        print(f"     Unique songs: {len(df[['song_name', 'artist_name']].drop_duplicates())}")
        print(f"     Playlists: {df['playlist_id'].nunique()}")
        print(f"     With comments: {with_comments}/{len(df)} ({comment_pct:.1f}%)")
        print(f"     Ready for Ananki analysis!")
        
        return filename


def main():
    print("="*70)
    print("YOUTUBE SCRAPER - ENHANCED WITH COMMENTS")
    print("="*70)
    print("\nEnhancements:")
    print("  [OK] Cleans song titles (removes Lyrics, Official Video, etc.)")
    print("  [OK] Scrapes video comments for vibe context")
    print("  [OK] Extracts emotional language from comments")
    print("  [OK] Tracks sequence positions for flow analysis")
    print("  [OK] Captures temporal transitions")
    print()
    
    scraper = YouTubeScraperEnhanced()
    
    # Scrape
    print("[NOTE] This will take longer due to comment scraping...")
    print("       But the data will be MUCH richer!")
    data = scraper.run_scrape(playlists_per_query=2)
    
    if data:
        filename = scraper.save_for_ananki(data)
        
        print("\n" + "="*70)
        print("COMPLETE!")
        print("="*70)
        print(f"\nNext: Ask Ananki to analyze {filename}")
        print("      Much richer temporal/emotional context now!")
    else:
        print("\n[ERROR] No data collected")


if __name__ == "__main__":
    main()
