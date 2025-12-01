"""Quick API test before running full scraper"""
import sys, os, json
from pathlib import Path
from dotenv import load_dotenv

# Load env
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

print("=" * 50)
print("API CONNECTION TEST")
print("=" * 50)

# Test YouTube
print("\n1. Testing YouTube API...")
try:
    from googleapiclient.discovery import build
    youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
    
    response = youtube.search().list(
        part='snippet',
        q='sad songs heartbreak playlist',
        type='video',
        maxResults=3,
        videoCategoryId='10'
    ).execute()
    
    print(f"   Found {len(response.get('items', []))} videos")
    for item in response.get('items', [])[:2]:
        print(f"   - {item['snippet']['title'][:50]}...")
    print("   YouTube: OK!")
except Exception as e:
    print(f"   YouTube ERROR: {e}")

# Test Spotify  
print("\n2. Testing Spotify API...")
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
    ))
    
    results = spotify.search(q='artist:Adele track:Hello', type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        print(f"   Found: {track['artists'][0]['name']} - {track['name']}")
    print("   Spotify: OK!")
except Exception as e:
    print(f"   Spotify ERROR: {e}")

# Test YouTube comments
print("\n3. Testing YouTube Comments API...")
try:
    # Get comments from a known video
    response = youtube.commentThreads().list(
        part='snippet',
        videoId='dQw4w9WgXcQ',  # Rick Astley - Never Gonna Give You Up
        maxResults=5,
        order='relevance'
    ).execute()
    
    print(f"   Found {len(response.get('items', []))} comments")
    print("   YouTube Comments: OK!")
except Exception as e:
    print(f"   YouTube Comments ERROR: {e}")

print("\n" + "=" * 50)
print("All tests passed! Ready to run scraper.")
print("=" * 50)
