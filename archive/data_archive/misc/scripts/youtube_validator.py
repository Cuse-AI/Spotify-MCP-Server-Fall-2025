"""
YouTube Validator - Fallback validation for songs that didn't match on Spotify

This script:
1. Takes the CHECK_YOUTUBE songs from our analysis
2. Searches YouTube for each song
3. Validates if it's a real song (not a random video)
4. Returns clean metadata if found

Critical: We need to be careful not to match random YouTube videos
"""

import json
import time
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# You'll need to set your YouTube API key
YOUTUBE_API_KEY = None  # Set this from environment or config

def search_youtube(artist, song, max_results=5):
    """
    Search YouTube for a song and return video results.
    
    Returns: List of dicts with video info
    """
    if not YOUTUBE_API_KEY:
        raise ValueError("YouTube API key not set!")
    
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    # Construct search query
    query = f"{artist} {song}"
    
    try:
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results,
            videoCategoryId='10'  # Music category
        )
        response = request.execute()
        
        results = []
        for item in response.get('items', []):
            snippet = item['snippet']
            results.append({
                'video_id': item['id']['videoId'],
                'title': snippet['title'],
                'channel': snippet['channelTitle'],
                'description': snippet.get('description', ''),
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            })
        
        return results
    
    except HttpError as e:
        print(f"YouTube API error: {e}")
        return []


def validate_youtube_match(artist, song, video_result):
    """
    Determine if a YouTube video is actually the song we're looking for.
    
    Returns: (is_match: bool, confidence: float, reason: str)
    """
    title = video_result['title'].lower()
    channel = video_result['channel'].lower()
    artist_lower = artist.lower()
    song_lower = song.lower()
    
    # Red flags - likely NOT the song
    red_flags = [
        'lyrics',
        'karaoke',
        'cover',
        'tutorial',
        'lesson',
        'reaction',
        'review',
        'instrumental',
        'remix',
        'live',
        'acoustic',
        'unplugged',
        'mashup',
        'playlist',
        'compilation',
        'best of',
    ]
    
    # Green flags - likely the actual song
    green_flags = [
        'official',
        'audio',
        'music video',
        'mv',
        'vevo',
    ]
    
    confidence = 0.5  # Start neutral
    reasons = []
    
    # Check if artist name appears in title or channel
    if artist_lower in title or artist_lower in channel:
        confidence += 0.2
        reasons.append("Artist name in title/channel")
    
    # Check if song name appears in title
    if song_lower in title:
        confidence += 0.2
        reasons.append("Song name in title")
    
    # Check for red flags
    red_flag_count = sum(1 for flag in red_flags if flag in title)
    if red_flag_count > 0:
        confidence -= 0.15 * red_flag_count
        reasons.append(f"Red flags detected: {red_flag_count}")
    
    # Check for green flags
    green_flag_count = sum(1 for flag in green_flags if flag in title)
    if green_flag_count > 0:
        confidence += 0.1 * green_flag_count
        reasons.append(f"Green flags detected: {green_flag_count}")
    
    # Channel name matching artist is VERY good signal
    if artist_lower == channel or channel in artist_lower or artist_lower in channel:
        confidence += 0.2
        reasons.append("Channel matches artist")
    
    # Clamp confidence between 0 and 1
    confidence = max(0.0, min(1.0, confidence))
    
    # Decision threshold
    is_match = confidence >= 0.6
    
    return (is_match, confidence, "; ".join(reasons))


def validate_song_on_youtube(artist, song):
    """
    Main validation function - searches YouTube and returns best match.
    
    Returns: dict with validation results or None if no good match
    """
    print(f"  Searching YouTube: '{artist}' - '{song}'")
    
    results = search_youtube(artist, song)
    
    if not results:
        return None
    
    # Check each result
    best_match = None
    best_confidence = 0.0
    
    for video in results:
        is_match, confidence, reasons = validate_youtube_match(artist, song, video)
        
        if is_match and confidence > best_confidence:
            best_confidence = confidence
            best_match = {
                'artist': artist,
                'song': song,
                'matched': True,
                'confidence': confidence,
                'validation_reason': reasons,
                'youtube_id': video['video_id'],
                'youtube_url': video['url'],
                'video_title': video['title'],
                'channel_name': video['channel']
            }
    
    return best_match


def process_check_youtube_songs():
    """
    Process all songs flagged for YouTube checking.
    """
    base_dir = Path(__file__).parent
    analysis_file = base_dir / 'low_confidence_analysis.json'
    
    if not analysis_file.exists():
        print("ERROR: Run analyze_low_confidence.py first!")
        return
    
    # Load analysis results
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    check_youtube = analysis_data['results']['CHECK_YOUTUBE']
    
    print(f"\nValidating {len(check_youtube)} songs on YouTube...")
    print("=" * 60)
    
    validated = []
    failed = []
    
    for i, entry in enumerate(check_youtube, 1):
        print(f"\n[{i}/{len(check_youtube)}] {entry['original_artist']} - {entry['original_song']}")
        
        try:
            result = validate_song_on_youtube(entry['original_artist'], entry['original_song'])
            
            if result:
                validated.append({
                    **entry,
                    'youtube_validation': result
                })
                print(f"  ✓ FOUND on YouTube (conf: {result['confidence']:.2f})")
            else:
                failed.append(entry)
                print(f"  ✗ No good match found")
            
            # Rate limiting - YouTube API has quotas
            time.sleep(1)
        
        except Exception as e:
            print(f"  ERROR: {e}")
            failed.append(entry)
            continue
    
    # Save results
    output_file = base_dir / 'youtube_validation_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_checked': len(check_youtube),
            'validated': len(validated),
            'failed': len(failed),
            'validated_songs': validated,
            'failed_songs': failed
        }, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("YOUTUBE VALIDATION COMPLETE")
    print("=" * 60)
    print(f"Total checked: {len(check_youtube)}")
    print(f"Validated: {len(validated)} ({len(validated)/len(check_youtube)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(check_youtube)*100:.1f}%)")
    print(f"\nSaved to: {output_file}")
    
    return validated, failed


if __name__ == '__main__':
    # Check if API key is set
    if not YOUTUBE_API_KEY:
        print("\nERROR: YouTube API key not set!")
        print("\nTo use this script:")
        print("1. Get a YouTube Data API v3 key from Google Cloud Console")
        print("2. Set YOUTUBE_API_KEY in this file or as environment variable")
        print("\nAlternatively, we can skip YouTube validation and just use Spotify matches.")
    else:
        validated, failed = process_check_youtube_songs()
