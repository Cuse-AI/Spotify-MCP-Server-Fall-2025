"""
STEP 0: Pre-process Songs Before Spotify Validation
Cleans artist/song fields to fix common parsing errors from Reddit scraping
Rescues songs that would otherwise have low confidence matches
"""
import json
import re
from collections import defaultdict

class SongPreprocessor:
    def __init__(self):
        self.fixes_applied = defaultdict(int)

    def clean_whitespace(self, text):
        """Remove extra whitespace, newlines, and normalize"""
        if not text:
            return ""
        # Replace newlines with spaces
        text = text.replace('\n', ' ').replace('\r', ' ')
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()

    def detect_artist_song_swap(self, artist, song):
        """
        Detect if artist and song are likely swapped
        Common pattern: lowercase artist, capitalized song = probably swapped
        """
        if not artist or not song:
            return False

        # If artist is all lowercase and song starts with capital, likely swapped
        if artist.islower() and song[0].isupper():
            return True

        # If artist has common song words (the, a, an, my, your, etc.)
        song_words = ['the', 'a', 'an', 'my', 'your', 'our', 'their', 'his', 'her', 'i', 'me', 'you']
        artist_first_word = artist.split()[0].lower()
        if artist_first_word in song_words and not song.split()[0].lower() in song_words:
            return True

        return False

    def fix_multiple_artists(self, artist, song):
        """
        Fix cases where multiple artists are mashed together
        Pattern: "Artist1 \nArtist2" or "Artist1 Artist2"
        Take the first artist only
        """
        if not artist:
            return artist, song, False

        # Check for newlines indicating multiple artists
        if '\n' in artist:
            parts = [p.strip() for p in artist.split('\n') if p.strip()]
            if len(parts) > 1:
                # Take the first artist
                self.fixes_applied['multiple_artists_newline'] += 1
                return parts[0], song, True

        # Check for "and" or "&" or "feat" indicating multiple artists
        # But only if song field seems wrong too
        if any(word in artist.lower() for word in [' and ', ' & ', ' feat', ' ft.', ' featuring']):
            # Split and take first artist
            for sep in [' and ', ' & ', ' feat', ' ft.', ' featuring']:
                if sep in artist.lower():
                    parts = re.split(re.escape(sep), artist, flags=re.IGNORECASE)
                    self.fixes_applied['multiple_artists_separator'] += 1
                    return parts[0].strip(), song, True

        return artist, song, False

    def fix_song_in_artist_field(self, artist, song):
        """
        Fix cases where song name leaked into artist field
        Pattern: "Artist - SongName" in artist field, "Something else" in song field
        """
        if not artist or not song:
            return artist, song, False

        # Check if artist field has a dash indicating song name
        if ' - ' in artist and ' - ' not in song:
            parts = artist.split(' - ', 1)
            if len(parts) == 2:
                # Likely: parts[0] = artist, parts[1] = song
                # Current song field might be description or wrong
                self.fixes_applied['song_in_artist_field'] += 1
                return parts[0].strip(), parts[1].strip(), True

        return artist, song, False

    def standardize_featuring(self, artist):
        """Standardize featuring notation (feat, ft., featuring -> feat.)"""
        if not artist:
            return artist

        # Replace variations of featuring with standard "feat."
        artist = re.sub(r'\s+feat\s+', ' feat. ', artist, flags=re.IGNORECASE)
        artist = re.sub(r'\s+ft\.?\s+', ' feat. ', artist, flags=re.IGNORECASE)
        artist = re.sub(r'\s+featuring\s+', ' feat. ', artist, flags=re.IGNORECASE)

        return artist

    def remove_bracketed_info(self, text):
        """Remove [remaster], (live), etc. from song names"""
        if not text:
            return text

        # Remove content in brackets/parentheses
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)

        return text.strip()

    def preprocess_song(self, artist, song):
        """
        Main preprocessing pipeline
        Returns: (cleaned_artist, cleaned_song, fixes_applied_list)
        """
        fixes = []

        # Step 1: Clean whitespace
        original_artist = artist
        original_song = song
        artist = self.clean_whitespace(artist)
        song = self.clean_whitespace(song)

        if artist != original_artist or song != original_song:
            fixes.append('whitespace_cleaned')
            self.fixes_applied['whitespace_cleaned'] += 1

        # Step 2: Fix multiple artists
        artist, song, fixed = self.fix_multiple_artists(artist, song)
        if fixed:
            fixes.append('multiple_artists_fixed')

        # Step 3: Fix song in artist field
        artist, song, fixed = self.fix_song_in_artist_field(artist, song)
        if fixed:
            fixes.append('song_in_artist_field_fixed')

        # Step 4: Check for swap
        if self.detect_artist_song_swap(artist, song):
            artist, song = song, artist
            fixes.append('artist_song_swapped')
            self.fixes_applied['artist_song_swapped'] += 1

        # Step 5: Standardize featuring notation
        original = artist
        artist = self.standardize_featuring(artist)
        if artist != original:
            fixes.append('featuring_standardized')
            self.fixes_applied['featuring_standardized'] += 1

        # Step 6: Remove bracketed info
        original_song = song
        song = self.remove_bracketed_info(song)
        if song != original_song:
            fixes.append('bracketed_info_removed')
            self.fixes_applied['bracketed_info_removed'] += 1

        return artist, song, fixes


def preprocess_tapestry(input_file, output_file):
    """
    Preprocess all songs in the tapestry
    Returns: stats about fixes applied
    """
    # Load tapestry
    with open(input_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)

    preprocessor = SongPreprocessor()
    total_songs = 0
    songs_fixed = 0

    print('='*80)
    print('STEP 0: PRE-PROCESSING SONGS')
    print('='*80)
    print(f'Loading from: {input_file}')

    # Process all songs
    for vibe_name, vibe_data in tapestry['vibes'].items():
        for song in vibe_data['songs']:
            total_songs += 1

            original_artist = song.get('artist', '')
            original_song = song.get('song', '')

            # Preprocess
            cleaned_artist, cleaned_song, fixes = preprocessor.preprocess_song(
                original_artist, original_song
            )

            # Update if changed
            if cleaned_artist != original_artist or cleaned_song != original_song:
                songs_fixed += 1
                song['artist'] = cleaned_artist
                song['song'] = cleaned_song
                song['preprocessing_fixes'] = fixes
                song['original_artist'] = original_artist
                song['original_song'] = original_song

    # Save preprocessed tapestry
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)

    print(f'\n[COMPLETE]')
    print(f'Total songs: {total_songs}')
    print(f'Songs fixed: {songs_fixed} ({songs_fixed/total_songs*100:.1f}%)')
    print(f'\n[FIX BREAKDOWN]')
    for fix_type, count in sorted(preprocessor.fixes_applied.items(), key=lambda x: x[1], reverse=True):
        print(f'  {fix_type}: {count}')

    print(f'\n[SAVED] {output_file}')

    return {
        'total_songs': total_songs,
        'songs_fixed': songs_fixed,
        'fixes_breakdown': dict(preprocessor.fixes_applied)
    }


def main():
    input_file = '../ananki_outputs/tapestry_CLEANED.json'
    output_file = '../ananki_outputs/tapestry_PREPROCESSED.json'

    stats = preprocess_tapestry(input_file, output_file)

    print(f'\n[NEXT STEP]')
    print('Run step1_spotify_validate_v2.py with the PREPROCESSED tapestry')
    print('This should significantly improve match quality!')


if __name__ == '__main__':
    main()
