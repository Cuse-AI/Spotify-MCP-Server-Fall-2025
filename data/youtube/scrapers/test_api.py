from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('..') / '.env')
api_key = os.getenv('YOUTUBE_API_KEY')
print(f'Testing API Key: {api_key[:20]}...')

youtube = build('youtube', 'v3', developerKey=api_key)

try:
    response = youtube.search().list(
        part='snippet',
        q='test music',
        type='video',
        maxResults=1
    ).execute()
    print('✅ API key works! Got response')
    print(f'Found: {response["items"][0]["snippet"]["title"]}')
except Exception as e:
    print(f'❌ Error: {e}')
