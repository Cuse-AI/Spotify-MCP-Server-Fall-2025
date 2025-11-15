"""
YouTube Smart Scraper - CHILL Meta-Vibe
Created: Nov 10, 2025

Gets REAL HUMAN EMOTIONAL CONTEXT from:
- Playlist titles and descriptions  
- YouTube comments with high likes
- Emotional expressions about songs

Workflow: Scrape → TRUE Ananki Analysis → Inject to Tapestry
"""

from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import re
import json
import time
from dotenv import load_dotenv
from pathlib import Path
from checkpoint_utils import CheckpointManager
from improved_search_utils import load_tapestry_spotify_ids, diversify_queries, get_diverse_search_params
import random

load_dotenv()
load_dotenv(Path(__file__).parent.parent / '.env')

class SadYouTubeScraper:
    def __init__(self):
        # Initialize YouTube
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY not found in .env")
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Initialize Spotify
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
        )
        
        self.scraped_videos = set()
        
        # Pre-load tapestry to skip existing songs
        self.existing_spotify_ids = load_tapestry_spotify_ids()

    def clean_song_title(self, title):
        """Clean YouTube video title to get actual song name"""
        title = re.sub(r'\s*\(Official.*?\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\[Official.*?\]', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(Lyrics?\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\[Lyrics?\]', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(Lyric Video\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(Audio\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\(Visuali[sz]er\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^\d+[\.\)]\s*', '', title)
        return title.strip()

    def parse_video_title(self, title):
        """Extract artist and song from YouTube title"""
        title = self.clean_song_title(title)
        
        # Pattern: Artist - Song
        if ' - ' in title:
            parts = title.split(' - ', 1)
            return parts[0].strip(), parts[1].strip()
        
        # Pattern: "Song" by Artist
        by_match = re.search(r'["\'](.+?)["\'] by (.+)', title, re.IGNORECASE)
        if by_match:
            return by_match.group(2).strip(), by_match.group(1).strip()
        
        return None, None

    def search_spotify(self, artist, song):
        """Validate with Spotify"""
        try:
            query = f"{artist} {song}"
            results = self.sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                return {
                    'artist': track['artists'][0]['name'],
                    'song': track['name'],
                    'spotify_id': track['id'],
                    'spotify_uri': track['uri']
                }
            return None
        except:
            return None

    def get_playlist_videos(self, playlist_id):
        """Get all videos from a playlist"""
        try:
            videos = []
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50
            )
            
            while request and len(videos) < 100:  # Limit to 100 videos per playlist
                response = request.execute()
                videos.extend(response.get('items', []))
                request = self.youtube.playlistItems().list_next(request, response)
            
            return videos
        except Exception as e:
            print(f"  Error getting playlist: {e}")
            return []

    def get_video_comments(self, video_id, max_comments=20):
        """Get top comments from a video"""
        try:
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                order='relevance',
                maxResults=max_comments,
                textFormat='plainText'
            )
            response = request.execute()
            
            comments = []
            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'text': snippet['textDisplay'],
                    'likes': snippet['likeCount']
                })
            
            return comments
        except:
            return []

    def search_playlists(self, query, max_results=10):
        """Search for playlists"""
        try:
            # Get diverse search parameters
            params = get_diverse_search_params()

            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='playlist',
                maxResults=max_results * 2,  # Get more, then randomize
                order=params['order'],  # Varies each run
                regionCode=params['regionCode']  # Regional diversity
            )
            response = request.execute()
            
            playlists = []
            for item in response.get('items', []):
                playlists.append({
                    'id': item['id']['playlistId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description']
                })
            
            return playlists
        except Exception as e:
            print(f"  Error searching playlists: {e}")
            return []

    def scrape_sad_vibes(self, target_songs=1000):
        """Scrape Sad vibes from YouTube - including consolidated Nostalgic sub-vibes"""
        cp = CheckpointManager('Sad')

        queries = [
            # Standard terms
            'sad music playlist',
            'crying songs',
            'heartbreak music',
            'melancholic playlist',
            'depressing songs',
            'sadness music',
            'nostalgic music playlist',
            
            # Creative Sad terms (Solution B!)
            'songs for crying in the shower',
            'breakup anthems that hit different',
            'rainy day feels music',
            'songs that make you ugly cry',
            'heartache playlist 3am',
            'post breakup healing songs',
            'emotional damage playlist',
            'songs for when everything hurts',
            
            # Nostalgic variations (creative!)
            'songs that bring back memories',
            'throwback hits that hit different',
            'childhood soundtrack playlist',
            'songs from simpler times',
            'music that takes you back',
            'nostalgia trip playlist',
            'remember when music',
            'songs your younger self loved'
        ]

        # Add diversity modifiers (time, quality, etc.)
        queries = diversify_queries(queries)

        print("\n" + "="*70)
        print("YOUTUBE SCRAPING - SAD VIBES")
        print("="*70)
        print(f"Target: {target_songs} songs")
        print("Workflow: Scrape -> TRUE Ananki -> Tapestry")
        print("="*70)

        for query in queries:
            if len(cp.all_results) >= target_songs:
                break
                
            print(f"\nSearching: '{query}'")

            # Find playlists (increased from 5 to 10 for better coverage)
            playlists = self.search_playlists(query, max_results=10)
            
            # Randomize playlist selection for diversity
            random.shuffle(playlists)
            playlists = playlists[:10]  # Take random subset

            for playlist in playlists:

            
                if len(cp.all_results) >= target_songs:

            
                    break

            
            

            
                playlist_id = playlist['id']

            
            

            
                # SKIP if we've already processed this playlist

            
                if cp.is_playlist_processed(playlist_id):

            
                    print(f"  SKIP (already processed): {playlist['title'][:50].encode('ascii', 'ignore').decode()}...")

            
                    continue

            
            

            
                print(f"  Playlist: {playlist['title'][:50].encode('ascii', 'ignore').decode()}...")
                
                # Get videos from playlist
                videos = self.get_playlist_videos(playlist_id)
                
                for video in videos[:30]:  # First 30 songs per playlist
                    if len(cp.all_results) >= target_songs:
                        break
                    
                    video_id = video['snippet']['resourceId']['videoId']
                    video_url = f"https://youtube.com/watch?v={video_id}"
                    
                    if video_url in cp.scraped_urls:
                        continue
                    
                    cp.scraped_urls.add(video_url)
                    
                    # Parse song info
                    title = video['snippet']['title']
                    artist, song = self.parse_video_title(title)
                    
                    if not artist or not song:
                        continue
                    
                    # Validate with Spotify
                    spotify_result = self.search_spotify(artist, song)
                    
                    if spotify_result:
                        # Get comments for emotional context
                        comments = self.get_video_comments(video_id, max_comments=10)
                        
                        # Find best emotional comment
                        best_comment = ""
                        best_likes = 0
                        for comment in comments:
                            if comment['likes'] > best_likes and len(comment['text']) > 20:
                                best_comment = comment['text']
                                best_likes = comment['likes']
                        
                        song_data = {
                            **spotify_result,
                            'source_url': video_url,
                            'source': 'youtube',
                            'post_title': playlist['title'],
                            'comment_text': best_comment if best_comment else playlist['description'][:500],
                            'comment_score': best_likes,
                            'playlist_id': playlist_id
                        }
                        
                        cp.update_progress([song_data])
                    
                    time.sleep(0.3)  # YouTube API rate limiting
                
                cp.mark_playlist_processed(playlist_id)

                
                time.sleep(1)  # Between playlists

        # Finalize
        output = Path('../test_results/sad_youtube_extraction.json')
        results = cp.finalize(output, target_songs)
        return results


if __name__ == '__main__':
    scraper = SadYouTubeScraper()
    results = scraper.scrape_sad_vibes(target_songs=1000)

    print(f"\n{'='*70}")
    print(f"SCRAPING COMPLETE!")
    print(f"{'='*70}")
    print(f"Total unique songs: {len(results)}")
    print(f"All validated with Spotify IDs!")
    print(f"\nSaved to: test_results/sad_youtube_extraction.json")
    print("\nNext: python ../../reddit/true_ananki_claude_api.py test_results/sad_youtube_extraction.json")
