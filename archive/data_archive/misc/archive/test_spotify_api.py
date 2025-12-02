import os
import sys
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Force output to flush immediately
sys.stdout.reconfigure(line_buffering=True)

load_dotenv(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\spotify\.env')

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

print(f'Testing Spotify API connection...', flush=True)
print(f'Client ID found: {bool(client_id)}', flush=True)
print(f'Client Secret found: {bool(client_secret)}', flush=True)

if not client_id or not client_secret:
    print('ERROR: Credentials not loaded!', flush=True)
    exit(1)

# Test connection
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
))

print('Spotify client created!', flush=True)

# Test search
print('Testing search with "Alice in Chains Nutshell"...', flush=True)
results = sp.search(q='Alice in Chains Nutshell', type='track', limit=1)

if results['tracks']['items']:
    track = results['tracks']['items'][0]
    print(f'MATCH FOUND!', flush=True)
    print(f'  Clean name: {track["artists"][0]["name"]} - {track["name"]}', flush=True)
    print(f'  Spotify ID: {track["id"]}', flush=True)
else:
    print('No match found', flush=True)

print('Test complete! API is working!', flush=True)
