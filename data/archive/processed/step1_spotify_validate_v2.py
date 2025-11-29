"""
STEP 1: Spotify Validation v2 - WITH CONFIDENCE SCORING
Validates songs against Spotify API with match quality checks
Filters out bad matches that don't actually match the query
"""
import json
import time
import os
from difflib import SequenceMatcher
from dotenv import load_dotenv

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    print('ERROR: spotipy not installed!')
    print('Run: pip install spotipy --break-system-packages')
    exit(1)

load_dotenv(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\spotify\.env')

class SpotifyValidatorV2:
    def __init__(self):
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

        if not client_id or not client_secret:
            raise ValueError('Spotify credentials not found')

        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        ))
        self.request_count = 0
        self.batch_size = 500

    def calculate_similarity(self, str1, str2):
        """Calculate similarity between two strings (0.0 to 1.0)"""
        if not str1 or not str2:
            return 0.0
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def calculate_confidence(self, original_artist, original_song, matched_artist, matched_song):
        """
        Calculate confidence score for a match
        Returns: (confidence_score, explanation)
        """
        # Calculate similarities
        artist_sim = self.calculate_similarity(original_artist, matched_artist)
        song_sim = self.calculate_similarity(original_song, matched_song)

        # Check for artist/song swap (common with Reddit data)
        swap_artist_sim = self.calculate_similarity(original_artist, matched_song)
        swap_song_sim = self.calculate_similarity(original_song, matched_artist)

        # If swapped version is better, use that
        if (swap_artist_sim + swap_song_sim) > (artist_sim + song_sim):
            artist_sim, song_sim = swap_artist_sim, swap_song_sim
            swapped = True
        else:
            swapped = False

        # Calculate overall confidence (weighted: artist 40%, song 60%)
        confidence = (artist_sim * 0.4) + (song_sim * 0.6)

        # Explanation
        if confidence >= 0.8:
            quality = "EXCELLENT"
        elif confidence >= 0.6:
            quality = "GOOD"
        elif confidence >= 0.4:
            quality = "QUESTIONABLE"
        else:
            quality = "POOR"

        explanation = f"{quality} - Artist: {artist_sim:.2f}, Song: {song_sim:.2f}"
        if swapped:
            explanation += " (swapped)"

        return confidence, explanation

    def search_song(self, artist, song):
        """Search for a song on Spotify with confidence scoring"""
        try:
            # Clean up the query
            query = f"{artist} {song}".strip()

            # Rate limiting
            if self.request_count % 100 == 0 and self.request_count > 0:
                print(f'  [Rate limit pause at {self.request_count} requests...]')
                time.sleep(30)

            results = self.sp.search(q=query, type='track', limit=1)
            self.request_count += 1
            time.sleep(0.35)

            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                matched_artist = track['artists'][0]['name']
                matched_song = track['name']

                # Calculate confidence
                confidence, explanation = self.calculate_confidence(
                    artist, song, matched_artist, matched_song
                )

                return {
                    'matched': True,
                    'confidence': confidence,
                    'confidence_explanation': explanation,
                    'spotify_id': track['id'],
                    'spotify_uri': track['uri'],
                    'clean_artist': matched_artist,
                    'clean_song': matched_song,
                    'original_artist': artist,
                    'original_song': song
                }

            return None

        except Exception as e:
            print(f'  ERROR searching "{artist} - {song}": {str(e)}')
            return None

    def validate_batch(self, songs, batch_num, total_batches, min_confidence=0.6):
        """
        Validate a batch of songs
        min_confidence: minimum confidence score to accept a match (default 0.6)
        """
        print(f'\n[BATCH {batch_num}/{total_batches}] Validating {len(songs)} songs...')
        print(f'Minimum confidence threshold: {min_confidence}')

        matched_good = []
        matched_questionable = []
        unmatched = []

        for i, song_entry in enumerate(songs, 1):
            if i % 50 == 0:
                print(f'  Progress: {i}/{len(songs)}...')

            result = self.search_song(song_entry['artist'], song_entry['song'])

            if result:
                if result['confidence'] >= min_confidence:
                    matched_good.append({**song_entry, **result})
                else:
                    # Low confidence - treat as questionable
                    matched_questionable.append({**song_entry, **result})
            else:
                unmatched.append(song_entry)

        return matched_good, matched_questionable, unmatched

def main():
    # Load PREPROCESSED tapestry (cleaned + fixed parsing errors)
    with open('../ananki_outputs/tapestry_PREPROCESSED.json', 'r', encoding='utf-8') as f:
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

    validator = SpotifyValidatorV2()
    matched_good, matched_questionable, unmatched = validator.validate_batch(
        batch_songs, 1, 1, min_confidence=0.6
    )

    # Save results
    results = {
        'batch_num': 1,
        'total_processed': len(batch_songs),
        'matched_good': len(matched_good),
        'matched_questionable': len(matched_questionable),
        'unmatched': len(unmatched),
        'match_rate_good': f'{(len(matched_good)/len(batch_songs)*100):.1f}%',
        'match_rate_questionable': f'{(len(matched_questionable)/len(batch_songs)*100):.1f}%',
        'good_matches': matched_good,
        'questionable_matches': matched_questionable,
        'unmatched_songs': unmatched
    }

    with open('spotify_batch_1_results_v2.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f'\n' + '='*80)
    print('BATCH 1 COMPLETE - WITH CONFIDENCE SCORING')
    print('='*80)
    print(f'Processed: {len(batch_songs)} songs')
    print(f'High Confidence Matches: {len(matched_good)} ({(len(matched_good)/len(batch_songs)*100):.1f}%)')
    print(f'Low Confidence Matches: {len(matched_questionable)} ({(len(matched_questionable)/len(batch_songs)*100):.1f}%)')
    print(f'Unmatched: {len(unmatched)} ({(len(unmatched)/len(batch_songs)*100):.1f}%)')
    print(f'\nSaved to: spotify_batch_1_results_v2.json')
    print(f'API requests made: {validator.request_count}')

    # Show some examples
    if matched_questionable:
        print(f'\n[EXAMPLES OF QUESTIONABLE MATCHES]:')
        for match in matched_questionable[:5]:
            print(f"  '{match['original_artist']} - {match['original_song']}'")
            print(f"  -> '{match['clean_artist']} - {match['clean_song']}'")
            print(f"  Confidence: {match['confidence']:.2f} - {match['confidence_explanation']}")
            print()

if __name__ == '__main__':
    main()
