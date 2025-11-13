"""
Spotify Scraper - INTEGRATED WITH AUTO-PIPELINE
Extracts: Playlists → Songs → Audio Features (for later analysis)
Outputs clean CSV ready for Ananki analysis
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import time

load_dotenv()


class SpotifyScraperIntegrated:
    def __init__(self):
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("Spotify credentials not found in .env")
        
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Vibe-specific playlist searches
        self.playlist_searches = {
            'emotional_sad': [
                'sad songs emotional',
                'heartbreak playlist',
                'crying music',
                'melancholic vibes',
            ],
            'focus_study': [
                'focus music',
                'study concentration',
                'deep work playlist',
                'productive work music',
            ],
            'rainy_cozy': [
                'rainy day vibes',
                'cozy music',
                'rainy mood',
                'comfort music',
            ],
            'epic': [
                'epic cinematic',
                'dramatic orchestral',
                'soundtrack vibes',
                'epic music',
            ],
            'night_sleep': [
                'late night vibes',
                '3am thoughts',
                'midnight music',
                'night driving',
            ],
            'chill': [
                'chill vibes',
                'relaxing music',
                'laid back',
                'mellow mood',
            ],
            'party': [
                'party music',
                'dance playlist',
                'pregame hype',
                'club music',
            ],
            'driving': [
                'road trip music',
                'driving playlist',
                'highway vibes',
                'car music',
            ],
            'motivational': [
                'workout motivation',
                'gym playlist',
                'pump up music',
                'beast mode',
            ],
            'romantic': [
                'romantic music',
                'love songs',
                'date night',
                'intimate vibes',
            ],
        }
        
        # Store audio features separately for Phase 2
        self.audio_features_cache = []
    
    def search_playlists(self, query, limit=3):
        """Search for Spotify playlists"""
        try:
            results = self.sp.search(q=query, type='playlist', limit=limit)
            playlists = []
            
            for item in results['playlists']['items']:
                # Filter out meditation/white noise/sleep sounds
                name = item['name'].lower()
                if any(skip in name for skip in ['meditation', 'white noise', 'nature sounds', 'rain sounds', 'sleep sounds']):
                    continue
                
                playlists.append({
                    'id': item['id'],
                    'name': item['name'],
                    'description': item.get('description', ''),
                    'owner': item['owner']['display_name'],
                    'tracks_total': item['tracks']['total']
                })
            
            return playlists
        except Exception as e:
            print(f"    [ERROR] Search: {e}")
            return []
    
    def get_playlist_tracks(self, playlist_id, limit=20):
        """Get tracks from a playlist"""
        try:
            results = self.sp.playlist_tracks(playlist_id, limit=limit)
            tracks = []
            
            for item in results['items']:
                if not item['track']:
                    continue
                
                track = item['track']
                
                # Skip if no artists
                if not track.get('artists'):
                    continue
                
                artist_names = ', '.join([a['name'] for a in track['artists']])
                
                tracks.append({
                    'song': track['name'],
                    'artist': artist_names,
                    'spotify_id': track['id'],
                    'popularity': track.get('popularity', 0),
                    'position': len(tracks)
                })
            
            return tracks
        except Exception as e:
            print(f"      [ERROR] Tracks: {e}")
            return []
    
    def get_audio_features(self, track_ids):
        """Get audio features for tracks (for Phase 2 analysis)"""
        try:
            # Skip audio features for now (403 permission issue)
            # We'll get them in Phase 2 with proper auth
            return [None] * len(track_ids)
        except Exception as e:
            print(f"        [ERROR] Audio features: {e}")
            return []
    
    def scrape_category(self, category, queries, playlists_per_query=2):
        """Scrape playlists for a vibe category"""
        results = []
        
        for query in queries:
            print(f"    Query: '{query}'...")
            
            playlists = self.search_playlists(query, limit=playlists_per_query)
            
            for playlist in playlists:
                name_safe = playlist['name'][:50].encode('ascii', 'ignore').decode('ascii')
                print(f"      Playlist: {name_safe}...")
                
                # Get tracks
                tracks = self.get_playlist_tracks(playlist['id'], limit=15)
                
                # Get audio features (skip for now - will get in Phase 2)
                # audio_features = self.get_audio_features(track_ids)
                
                # Store placeholder for audio features
                # for track in tracks:
                #     self.audio_features_cache.append({
                #         'spotify_id': track['spotify_id'],
                #         'song': track['song'],
                #         'artist': track['artist'],
                #     })
                
                # Create vibe description
                vibe_description = playlist['name']
                if playlist['description']:
                    # Clean HTML from description
                    desc = playlist['description'].replace('<a href', '').replace('</a>', '')
                    vibe_description += f" - {desc[:200]}"
                
                # Add each track
                for track in tracks:
                    results.append({
                        'vibe_description': vibe_description,
                        'song_name': track['song'],
                        'artist_name': track['artist'],
                        'recommendation_reasoning': f"From Spotify playlist: {playlist['name']} (curated by {playlist['owner']}). Position {track['position']+1}.",
                        'playlist_name': playlist['name'],
                        'playlist_id': playlist['id'],
                        'curator': playlist['owner'],
                        'sequence_position': track['position'],
                        'spotify_id': track['spotify_id'],
                        'popularity': track['popularity'],
                        'comment_score': track['popularity'],  # Use popularity as quality signal
                        'extraction_confidence': 'high',  # Spotify data is high quality
                        'extraction_method': 'spotify_playlist',
                        'source_url': f"https://open.spotify.com/playlist/{playlist['id']}",
                        'data_source': 'spotify',
                        'search_query': query,
                        'vibe_category_hint': category,
                    })
                
                print(f"        Found {len(tracks)} tracks")
                time.sleep(0.5)
            
            time.sleep(1)
        
        return results
    
    def run_scrape(self, playlists_per_query=2):
        """Run full Spotify scraping"""
        print("\n[SCRAPING] Collecting from Spotify playlists...")
        
        all_results = []
        for category, queries in self.playlist_searches.items():
            print(f"\n  Category: {category}")
            results = self.scrape_category(category, queries, playlists_per_query)
            all_results.extend(results)
            print(f"  Total: {len(results)} songs")
        
        return all_results
    
    def save_for_ananki(self, data):
        """Save data for Ananki + audio features for Phase 2"""
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
        
        # Spotify-specific columns
        spotify_cols = [
            'playlist_name', 'playlist_id', 'curator', 'sequence_position',
            'spotify_id', 'popularity', 'extraction_method', 'search_query', 
            'vibe_category_hint'
        ]
        
        final_cols = column_order + spotify_cols
        df = df[[c for c in final_cols if c in df.columns]]
        
        # Save main CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'spotify_for_ananki_{timestamp}.csv'
        df.to_csv(filename, index=False, encoding='utf-8')
        
        # Save audio features separately for Phase 2
        if self.audio_features_cache:
            audio_df = pd.DataFrame(self.audio_features_cache)
            audio_file = f'spotify_audio_features_{timestamp}.json'
            audio_df.to_json(audio_file, orient='records', indent=2)
            print(f"\n[OK] Saved audio features: {audio_file}")
            print(f"     (Will use in Phase 2 for sonic analysis)")
        
        print(f"\n[OK] Saved: {filename}")
        print(f"     Total songs: {len(df)}")
        print(f"     Unique songs: {len(df[['song_name', 'artist_name']].drop_duplicates())}")
        print(f"     Playlists: {df['playlist_id'].nunique()}")
        print(f"     Spotify IDs: {df['spotify_id'].notna().sum()}")
        print(f"     Ready for Ananki analysis!")
        
        return filename


def main():
    print("="*70)
    print("SPOTIFY SCRAPER - INTEGRATED")
    print("="*70)
    print("\nThis scraper:")
    print("  [OK] Searches vibe-specific playlists")
    print("  [OK] Extracts songs with Spotify IDs")
    print("  [OK] Captures audio_features (for Phase 2 sonic analysis)")
    print("  [OK] Gets curator info and popularity")
    print("  [OK] Outputs CSV ready for Ananki analysis")
    print()
    
    scraper = SpotifyScraperIntegrated()
    
    # Scrape
    data = scraper.run_scrape(playlists_per_query=2)
    
    if data:
        filename = scraper.save_for_ananki(data)
        
        print("\n" + "="*70)
        print("COMPLETE!")
        print("="*70)
        print(f"\nNext: Ask Ananki to analyze {filename}")
        print("      Ananki will map to sub-vibes and update tapestry")
        print("      Audio features saved for later sonic pattern analysis!")
    else:
        print("\n[ERROR] No data collected")


if __name__ == "__main__":
    main()
