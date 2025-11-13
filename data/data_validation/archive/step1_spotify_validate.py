"""
STEP 1: Spotify Validation
Validates songs against Spotify API in batches of 500
Saves: matched (with Spotify ID), unmatched (for YouTube check)
"""
import json
import time
import os
from dotenv import load_dotenv

# Check if spotipy is available
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    print('ERROR: spotipy not installed!')
    print('Run: pip install spotipy --break-system-packages')
    exit(1)

load_dotenv(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\spotify\.env')

class SpotifyValidator:
    def __init__(self):
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print(f'ERROR: Missing Spotify credentials!')
            print(f'CLIENT_ID: {client_id}')
            print(f'CLIENT_SECRET: {client_secret}')
            raise ValueError('Spotify credentials not found')
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        ))
        self.request_count = 0
        self.batch_size = 500
    
    def search_song(self, artist, song):
        """Search for a song on Spotify, return match data or None"""
        try:
            # Clean up the query
            query = f"{artist} {song}".strip()
            
            # Rate limiting
            if self.request_count % 100 == 0 and self.request_count > 0:
                print(f'  [Rate limit pause at {self.request_count} requests...]')
                time.sleep(30)  # 30 sec pause every 100 requests
            
            results = self.sp.search(q=query, type='track', limit=1)
            self.request_count += 1
            time.sleep(0.35)  # ~170 requests/minute
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                return {
                    'matched': True,
                    'spotify_id': track['id'],
                    'spotify_uri': track['uri'],
                    'clean_artist': track['artists'][0]['name'],
                    'clean_song': track['name'],
                    'original_artist': artist,
                    'original_song': song
                }
            
            return None
            
        except Exception as e:
            print(f'  ERROR searching "{artist} - {song}": {str(e)}')
            return None
    
    def validate_batch(self, songs, batch_num, total_batches):
        """Validate a batch of songs"""
        print(f'\n[BATCH {batch_num}/{total_batches}] Validating {len(songs)} songs...')
        
        matched = []
        unmatched = []
        
        for i, song_entry in enumerate(songs, 1):
            if i % 50 == 0:
                print(f'  Progress: {i}/{len(songs)}...')
            
            result = self.search_song(song_entry['artist'], song_entry['song'])
            
            if result:
                matched.append({**song_entry, **result})
            else:
                unmatched.append(song_entry)
        
        return matched, unmatched

def main():
    # Load cleaned tapestry
    with open('ananki_outputs/tapestry_CLEANED.json', 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Collect all songs
    all_songs = []
    for vibe_name, vibe_data in tapestry['vibes'].items():
        for song in vibe_data['songs']:
            all_songs.append({
                'artist': song.get('artist', ''),
                'song': song.get('song', ''),
                'vibe': vibe_name
            })
    
    print(f'\nTotal songs to validate: {len(all_songs)}')
    
    # Process first batch only (500 songs)
    batch_size = 500
    batch_songs = all_songs[:batch_size]
    
    validator = SpotifyValidator()
    matched, unmatched = validator.validate_batch(batch_songs, 1, 1)
    
    # Save results
    results = {
        'batch_num': 1,
        'total_processed': len(batch_songs),
        'matched': len(matched),
        'unmatched': len(unmatched),
        'match_rate': f'{(len(matched)/len(batch_songs)*100):.1f}%',
        'matched_songs': matched,
        'unmatched_songs': unmatched
    }
    
    with open('data_validation/spotify_batch_1_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f'\n' + '='*80)
    print('BATCH 1 COMPLETE')
    print('='*80)
    print(f'Processed: {len(batch_songs)} songs')
    print(f'Matched: {len(matched)} ({(len(matched)/len(batch_songs)*100):.1f}%)')
    print(f'Unmatched: {len(unmatched)} ({(len(unmatched)/len(batch_songs)*100):.1f}%)')
    print(f'\nSaved to: data_validation/spotify_batch_1_results.json')
    print(f'API requests made: {validator.request_count}')

if __name__ == '__main__':
    main()
