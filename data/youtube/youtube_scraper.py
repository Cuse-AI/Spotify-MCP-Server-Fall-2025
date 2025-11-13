"""
YouTube Scraper V2 - Creative Vibe Hunter
Finds: Playlists, music videos, lyric videos - extracts vibes from comments
"""

from googleapiclient.discovery import build
import pandas as pd
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import re

load_dotenv()

class YouTubeVibeHunter:
    def __init__(self):
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY not found")
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Diverse search strategies
        self.searches = [
            # Playlist compilations
            ('sad songs playlist 2024', 'playlist'),
            ('chill vibes mix', 'playlist'),
            ('angry workout music', 'playlist'),
            ('driving at night playlist', 'playlist'),
            ('main character energy songs', 'playlist'),
            
            # Specific vibes
            ('songs that make you cry', 'vibe'),
            ('music for 3am thoughts', 'vibe'),
            ('villain arc playlist', 'vibe'),
            
            # Discovery focused
            ('underrated songs you need to hear', 'discovery'),
            ('hidden gem songs', 'discovery')
        ]
    
    def get_video_info(self, video_id):
        """Get video details"""
        try:
            response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            
            if not response['items']:
                return None
            
            item = response['items'][0]
            snippet = item['snippet']
            
            return {
                'id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel': snippet['channelTitle'],
                'views': int(item['statistics'].get('viewCount', 0)),
                'likes': int(item['statistics'].get('likeCount', 0)),
                'duration': item['contentDetails']['duration']
            }
        except:
            return None
    
    def extract_tracklist(self, description):
        """Extract songs from description (if it's a playlist)"""
        tracks = []
        
        # Pattern: 0:00 Artist - Song or 1:23 Song by Artist
        patterns = [
            r'(\d{1,2}:\d{2})\s+([A-Z][^-\n]{2,40})\s*[-–]\s*([^\n]{3,60})',
            r'(\d{1,2}:\d{2})\s+([^\n]{3,60})\s+by\s+([A-Z][^\n]{2,40})'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, description):
                if pattern.endswith('by'):
                    time, song, artist = match.groups()
                else:
                    time, artist, song = match.groups()
                
                tracks.append({
                    'timestamp': time,
                    'artist': artist.strip(),
                    'song': song.strip()
                })
        
        return tracks
    
    def get_vibe_comments(self, video_id, max_comments=50):
        """Get comments and extract vibe descriptions"""
        try:
            response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_comments,
                order='relevance'
            ).execute()
            
            vibe_comments = []
            
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                text = comment['textDisplay']
                
                # Look for vibe language
                vibe_phrases = [
                    'feel', 'vibe', 'mood', 'makes me',
                    'perfect for', 'when you', 'reminds me'
                ]
                
                if any(phrase in text.lower() for phrase in vibe_phrases):
                    vibe_comments.append({
                        'text': text[:200],
                        'likes': comment['likeCount'],
                        'author': comment['authorDisplayName']
                    })
            
            return vibe_comments
        except:
            return []
    
    def scrape_video(self, video_id, search_type):
        """Scrape one video completely"""
        info = self.get_video_info(video_id)
        if not info:
            return None
        
        # Extract tracks (if playlist)
        tracks = self.extract_tracklist(info['description'])
        
        # Get vibe comments
        comments = self.get_vibe_comments(video_id)
        
        # For single songs/music videos, treat as 1 track
        if not tracks and 'official' in info['title'].lower():
            # Try to parse Artist - Song from title
            match = re.search(r'([A-Z][^-\n]{2,40})\s*[-–]\s*([^\n\(\[]{3,60})', info['title'])
            if match:
                tracks = [{
                    'artist': match.group(1).strip(),
                    'song': match.group(2).strip(),
                    'timestamp': '0:00'
                }]
        
        if not tracks and not comments:
            return None
        
        return {
            'video_id': video_id,
            'title': info['title'],
            'type': search_type,
            'views': info['views'],
            'tracks': tracks,
            'vibe_comments': comments
        }
    
    def search_and_collect(self, query, search_type, max_videos=5):
        """Search YouTube and collect videos"""
        print(f"\nSearching: '{query}'...")
        
        try:
            results = self.youtube.search().list(
                q=query,
                part='id',
                type='video',
                maxResults=max_videos,
                videoDuration='medium'
            ).execute()
            
            videos = []
            for item in results.get('items', []):
                video_id = item['id']['videoId']
                data = self.scrape_video(video_id, search_type)
                
                if data:
                    videos.append(data)
                    print(f"  [OK] {data['title'][:50]} -> {len(data['tracks'])} tracks, {len(data['vibe_comments'])} vibe comments")
                
                time.sleep(1)
            
            return videos
        except Exception as e:
            print(f"  [ERROR] {e}")
            return []
    
    def run(self):
        """Run full YouTube scrape"""
        all_videos = []
        
        for query, search_type in self.searches:
            videos = self.search_and_collect(query, search_type, max_videos=5)
            all_videos.extend(videos)
            time.sleep(2)
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with open(f'youtube_v2_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(all_videos, f, indent=2, ensure_ascii=False)
        
        # Create training CSV
        rows = []
        for video in all_videos:
            for track in video['tracks']:
                # Add top vibe comments as context
                contexts = [c['text'] for c in video['vibe_comments'][:3]]
                
                rows.append({
                    'source': 'youtube',
                    'playlist_title': video['title'],
                    'artist': track['artist'],
                    'song': track['song'],
                    'vibe_context_1': contexts[0] if len(contexts) > 0 else '',
                    'vibe_context_2': contexts[1] if len(contexts) > 1 else '',
                    'vibe_context_3': contexts[2] if len(contexts) > 2 else '',
                    'views': video['views']
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(f'youtube_v2_{timestamp}.csv', index=False, encoding='utf-8')
        
        print(f"\n[DONE] {len(all_videos)} videos -> {len(df)} tracks with vibe context")


if __name__ == "__main__":
    print("="*70)
    print("YouTube Vibe Hunter V2")
    print("="*70)
    YouTubeVibeHunter().run()
