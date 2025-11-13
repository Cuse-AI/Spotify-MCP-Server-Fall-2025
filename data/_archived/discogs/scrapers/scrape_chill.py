"""
Discogs Smart Scraper - CHILL Meta-Vibe  
Created: Nov 10, 2025

Uses Discogs API to find songs with emotional context from:
- User reviews
- Style/genre tags
- Album descriptions

Workflow: Scrape → TRUE Ananki Analysis → Inject to Tapestry
"""

import discogs_client
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import time
from dotenv import load_dotenv
from pathlib import Path
from checkpoint_utils import CheckpointManager

load_dotenv()
load_dotenv(Path(__file__).parent.parent / '.env')

class ChillDiscogsScraper:
    def __init__(self):
        # Initialize Spotify
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
        )

        # Initialize Discogs with Personal Access Token
        self.discogs = discogs_client.Client(
            'VibeCheck/1.0',
            user_token=os.getenv('DISCOGS_USER_TOKEN')
        )

        self.scraped_tracks = set()

    def search_spotify(self, query_text):
        """Search Spotify with validation"""
        try:
            results = self.sp.search(q=query_text, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                return {
                    'artist': track['artists'][0]['name'],
                    'song': track['name'],
                    'spotify_id': track['id'],
                    'spotify_uri': track['uri'],
                    'query_used': query_text[:100]
                }
            return None
        except:
            return None

    def get_release_context(self, release):
        """Get emotional context from Discogs release"""
        try:
            context_parts = []
            
            # Get styles/genres
            if hasattr(release, 'styles') and release.styles:
                context_parts.append(f"Styles: {', '.join(release.styles[:5])}")
            if hasattr(release, 'genres') and release.genres:
                context_parts.append(f"Genres: {', '.join(release.genres[:3])}")
            
            # Get notes if available
            if hasattr(release, 'notes') and release.notes:
                context_parts.append(f"Notes: {release.notes[:200]}")
            
            return " | ".join(context_parts) if context_parts else "Discogs release"
        
        except Exception as e:
            return f"Discogs release (error: {str(e)[:50]})"

    def scrape_by_style(self, style_name, cp, max_results=50):
        """Scrape releases with specific style"""
        print(f"\nSearching style: '{style_name}'")
        
        try:
            results = self.discogs.search('', type='release', style=style_name)
            
            count = 0
            for release in results:
                if len(cp.all_results) >= 500 or count >= max_results:
                    break
                
                try:
                    # Get tracklist
                    if hasattr(release, 'tracklist'):
                        for track in release.tracklist[:5]:  # First 5 tracks
                            if len(cp.all_results) >= 500:
                                break
                            
                            artist_name = release.artists[0].name if release.artists else "Unknown"
                            track_name = track.title
                            
                            track_key = (artist_name.lower(), track_name.lower())
                            if track_key in self.scraped_tracks:
                                continue
                            
                            self.scraped_tracks.add(track_key)
                            
                            # Get Spotify validation
                            spotify_result = self.search_spotify(f"{artist_name} {track_name}")
                            
                            if spotify_result:
                                context = self.get_release_context(release)
                                
                                song_data = {
                                    **spotify_result,
                                    'source_url': release.url if hasattr(release, 'url') else 'https://www.discogs.com',
                                    'source': 'discogs',
                                    'style': style_name,
                                    'post_title': f'Discogs Style: {style_name}',
                                    'comment_text': context,
                                    'comment_score': 50
                                }
                                
                                cp.update_progress([song_data])
                            
                            time.sleep(0.3)  # Discogs rate limiting
                    
                    count += 1
                    time.sleep(1)  # Between releases
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"  Error with style '{style_name}': {e}")

    def scrape_chill_vibes(self, target_songs=500):
        """Scrape Chill meta-vibe from Discogs"""
        cp = CheckpointManager('Chill')
        
        # Chill-related styles
        styles = [
            'Chillout',
            'Ambient',
            'Downtempo',
            'Lounge',
            'Easy Listening',
            'Chill-Out',
            'Smooth Jazz'
        ]

        print("\n" + "="*70)
        print("DISCOGS SCRAPING - CHILL VIBES")
        print("="*70)
        print(f"Target: {target_songs} songs")
        print("Workflow: Scrape -> TRUE Ananki -> Tapestry")
        print("="*70)

        for style in styles:
            if len(cp.all_results) >= target_songs:
                break
            
            self.scrape_by_style(style, cp, max_results=50)

        # Finalize
        output = Path('../test_results/chill_discogs_extraction.json')
        results = cp.finalize(output, target_songs)
        return results


if __name__ == '__main__':
    scraper = ChillDiscogsScraper()
    results = scraper.scrape_chill_vibes(target_songs=500)

    print(f"\n{'='*70}")
    print(f"SCRAPING COMPLETE!")
    print(f"{'='*70}")
    print(f"Total unique songs: {len(results)}")
    print(f"All validated with Spotify IDs!")
    print(f"\nSaved to: test_results/chill_discogs_extraction.json")
    print("\nNext: python ../../reddit/true_ananki_claude_api.py test_results/chill_discogs_extraction.json")
