"""
Last.fm Smart Scraper - CHILL Meta-Vibe
Created: Nov 10, 2025

Uses Last.fm API to find songs with emotional context from:
- User reviews
- Tags (chill, relaxing, ambient, etc.)
- Album/track descriptions  
- User "love" comments

Workflow: Scrape → TRUE Ananki Analysis → Inject to Tapestry
"""

import pylast
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import re
import json
import time
from dotenv import load_dotenv
from pathlib import Path
from checkpoint_utils import CheckpointManager

load_dotenv()
load_dotenv(Path(__file__).parent.parent / '.env')

class ChillLastFMScraper:
    def __init__(self):
        # Initialize Spotify
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
        )

        # Initialize Last.fm
        self.network = pylast.LastFMNetwork(
            api_key=os.getenv('LASTFM_API_KEY'),
            api_secret=os.getenv('LASTFM_API_SECRET')
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

    def get_track_context(self, track):
        """Get emotional context from Last.fm track"""
        try:
            context_parts = []
            
            # Get tags (emotional descriptors)
            try:
                tags = track.get_top_tags(limit=10)
                tag_names = [tag.item.name for tag in tags if tag.weight > 50]
                if tag_names:
                    context_parts.append(f"Tags: {', '.join(tag_names)}")
            except:
                pass
            
            # Get wiki/description
            try:
                wiki = track.get_wiki_summary()
                if wiki:
                    context_parts.append(f"Description: {wiki[:300]}")
            except:
                pass
            
            return " | ".join(context_parts) if context_parts else "Last.fm track"
        
        except Exception as e:
            return f"Last.fm track (error: {str(e)[:50]})"

    def scrape_by_tag(self, tag_name, cp, max_tracks=100):
        """Scrape tracks with specific tag"""
        print(f"\nSearching tag: '{tag_name}'")
        
        try:
            tag = self.network.get_tag(tag_name)
            top_tracks = tag.get_top_tracks(limit=max_tracks)
            
            for track in top_tracks:
                if len(cp.all_results) >= 500:  # Target limit
                    break
                
                artist_name = str(track.item.artist)
                track_name = str(track.item.title)
                
                track_key = (artist_name.lower(), track_name.lower())
                if track_key in self.scraped_tracks:
                    continue
                
                self.scraped_tracks.add(track_key)
                
                # Get Spotify validation
                spotify_result = self.search_spotify(f"{artist_name} {track_name}")
                
                if spotify_result:
                    # Get emotional context
                    context = self.get_track_context(track.item)
                    
                    song_data = {
                        **spotify_result,
                        'source_url': f'https://www.last.fm/music/{artist_name}/_/{track_name}',
                        'source': 'lastfm',
                        'tag': tag_name,
                        'post_title': f'Last.fm Tag: {tag_name}',
                        'comment_text': context,
                        'comment_score': int(track.weight) if hasattr(track, 'weight') else 100
                    }
                    
                    cp.update_progress([song_data])
                
                time.sleep(0.2)  # Rate limiting
                
        except Exception as e:
            print(f"  Error with tag '{tag_name}': {e}")

    def scrape_chill_vibes(self, target_songs=500):
        """Scrape Chill meta-vibe from Last.fm"""
        cp = CheckpointManager('Chill')
        
        # Chill-related tags
        tags = [
            'chill',
            'chillout',
            'relaxing',
            'ambient',
            'calm',
            'peaceful',
            'mellow',
            'downtempo',
            'lounge',
            'easy listening'
        ]

        print("\n" + "="*70)
        print("LAST.FM SCRAPING - CHILL VIBES")
        print("="*70)
        print(f"Target: {target_songs} songs")
        print("Workflow: Scrape -> TRUE Ananki -> Tapestry")
        print("="*70)

        for tag in tags:
            if len(cp.all_results) >= target_songs:
                break
            
            self.scrape_by_tag(tag, cp, max_tracks=100)

        # Finalize
        output = Path('../test_results/chill_lastfm_extraction.json')
        results = cp.finalize(output, target_songs)
        return results


if __name__ == '__main__':
    scraper = ChillLastFMScraper()
    results = scraper.scrape_chill_vibes(target_songs=500)

    print(f"\n{'='*70}")
    print(f"SCRAPING COMPLETE!")
    print(f"{'='*70}")
    print(f"Total unique songs: {len(results)}")
    print(f"All validated with Spotify IDs!")
    print(f"\nSaved to: test_results/chill_lastfm_extraction.json")
    print("\nNext: python ../../reddit/true_ananki_claude_api.py test_results/chill_lastfm_extraction.json")
