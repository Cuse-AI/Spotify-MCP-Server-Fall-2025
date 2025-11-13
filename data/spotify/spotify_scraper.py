"""
Spotify Playlist Scraper for VibeCheck - VERSION 2
Improved: Better playlist filtering + richer vibe descriptions
Focus: High-quality editorial playlists with real music (not meditation tones)
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

class SpotifyScraperV2:
    def __init__(self):
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("Spotify credentials not found in .env file")
        
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # IMPROVED: Better search queries focusing on real music playlists
        self.playlist_searches = [
            # Emotional/mood
            ('sad songs that hit different', 'sad vibes'),
            ('confidence boost anthems', 'confidence'),
            ('angry workout energy', 'gym motivation'),
            ('feel good happy vibes', 'happy energy'),
            ('cozy rainy day music', 'cozy feels'),
            
            # Contextual
            ('late night driving music', 'driving at night'),
            ('3am thoughts playlist', '3am thoughts'),
            ('sunday morning coffee', 'sunday morning'),
            ('party pregame hype', 'party vibes'),
            ('study focus concentration', 'study focus'),
            
            # Aesthetic
            ('main character energy', 'main character energy'),
            ('villain arc songs', 'villain arc'),
            ('dark academia aesthetic', 'dark academia'),
            ('ethereal dream pop', 'ethereal'),
            
            # Discovery
            ('indie deep cuts', 'indie'),
            ('underground hip hop gems', 'hip hop'),
            ('alternative rock hidden gems', 'rock')
        ]
        
        # SKIP these low-quality playlist types
        self.skip_keywords = [
            '528 hz', 'frequency', 'meditation', 'sleep',
            'binaural', 'alpha waves', 'relaxation music',
            'yoga', 'spa', 'massage', 'healing'
        ]
    
    def is_quality_playlist(self, playlist_name, playlist_desc):
        \"\"\"Filter out low-quality playlists\"\"\"
        combined = (playlist_name + ' ' + (playlist_desc or '')).lower()
        
        # Skip meditation/frequency playlists
        if any(skip in combined for skip in self.skip_keywords):
            return False
        
        # Skip very short playlists
        return True
    
    def scrape_playlist_with_context(self, playlist_id):
        \"\"\"Get playlist with full metadata as context\"\"\"
        try:
            playlist = self.sp.playlist(playlist_id)
            
            # Check quality
            if not self.is_quality_playlist(playlist['name'], playlist.get('description', '')):
                return None
            
            # Get tracks
            tracks = []
            for item in playlist['tracks']['items'][:100]:  # Limit to 100 tracks
                track = item['track']
                if track and track.get('id'):
                    tracks.append({
                        'song_name': track['name'],
                        'artist_name': ', '.join([a['name'] for a in track['artists']]),
                        'spotify_id': track['id'],
                        'popularity': track.get('popularity', 0),
                        'duration_ms': track.get('duration_ms', 0)
                    })
            
            if not tracks:
                return None
            
            return {
                'playlist_id': playlist_id,
                'name': playlist['name'],
                'description': playlist.get('description', ''),
                'owner': playlist['owner']['display_name'],
                'followers': playlist['followers']['total'],
                'tracks': tracks,
                'track_count': len(tracks),
                'is_public': playlist['public']
            }
        except Exception as e:
            return None
    
    def search_and_scrape(self, query, vibe_category, max_playlists=3):
        \"\"\"Search for playlists and scrape them\"\"\"
        try:
            results = self.sp.search(q=query, type='playlist', limit=10)
            playlists_data = []
            
            for item in results['playlists']['items'][:max_playlists * 2]:  # Get extra for filtering
                playlist_data = self.scrape_playlist_with_context(item['id'])
                
                if playlist_data:
                    playlist_data['vibe_category'] = vibe_category
                    playlist_data['search_query'] = query
                    playlists_data.append(playlist_data)
                    print(f\"    [OK] '{playlist_data['name'][:40]}': {playlist_data['track_count']} tracks\")
                
                if len(playlists_data) >= max_playlists:
                    break
                
                time.sleep(0.5)
            
            return playlists_data
        except Exception as e:
            print(f\"  [ERROR] Query '{query}': {e}\")
            return []
    
    def scrape_all_categories(self, playlists_per_category=3):
        \"\"\"Scrape all vibe categories\"\"\"
        all_playlists = []
        
        for query, category in self.playlist_searches:
            print(f\"\\nSearching for '{category}' playlists...\")
            playlists = self.search_and_scrape(query, category, max_playlists=playlists_per_category)
            all_playlists.extend(playlists)
            print(f\"  Progress: {len(all_playlists)} playlists, {sum(p['track_count'] for p in all_playlists)} total tracks\")
            time.sleep(1)
        
        return all_playlists
    
    def create_training_dataset(self, playlists_data):
        \"\"\"Create training CSV\"\"\"
        rows = []
        
        for playlist in playlists_data:
            for track in playlist['tracks']:
                row = {
                    'source': 'spotify',
                    'vibe_category': playlist['vibe_category'],
                    'playlist_name': playlist['name'],
                    'playlist_description': playlist['description'][:200],
                    
                    # Song data
                    'song_name': track['song_name'],
                    'artist_name': track['artist_name'],
                    'spotify_id': track['spotify_id'],
                    
                    # Quality signals
                    'popularity': track['popularity'],
                    'playlist_followers': playlist['followers'],
                    
                    # Metadata
                    'playlist_id': playlist['playlist_id'],
                    'search_query': playlist['search_query']
                }
                rows.append(row)
        
        return pd.DataFrame(rows)
    
    def save_data(self, playlists_data, filename_prefix='spotify_vibe_context'):
        \"\"\"Save data\"\"\"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON
        json_path = f\"{filename_prefix}_{timestamp}.json\"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(playlists_data, f, indent=2, ensure_ascii=False)
        print(f\"[OK] Full data: {json_path}\")
        
        # CSV
        df = self.create_training_dataset(playlists_data)
        csv_path = f\"{filename_prefix}_training_{timestamp}.csv\"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f\"[OK] Training data: {csv_path}\")
        
        print(f\"\\n[STATS] {len(playlists_data)} playlists -> {len(df)} verified tracks\")
        print(f\"[STATS] Avg tracks per playlist: {len(df)/len(playlists_data):.1f}\")
        
        return json_path, csv_path


def main():
    print(\"=\" * 70)
    print(\"VibeCheck Spotify Scraper V2 - QUALITY-FOCUSED\")
    print(\"=\" * 70)
    print(\"\\nGoal: Curated playlists with verified tracks (skip meditation/tones)\\n\")
    
    scraper = SpotifyScraperV2()
    print(\"Starting quality-focused Spotify scraping...\")
    playlists = scraper.scrape_all_categories(playlists_per_category=3)
    
    print(\"\\n\" + \"=\" * 70)
    scraper.save_data(playlists)
    print(\"*** Spotify V2 Complete!\")
    print(\"=\" * 70)


if __name__ == \"__main__\":
    main()
