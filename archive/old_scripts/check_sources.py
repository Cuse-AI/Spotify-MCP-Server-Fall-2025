import json
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

songs = [s for v in tapestry['vibes'].values() for s in v.get('songs', [])]

reddit = [s for s in songs if 'reddit' in s.get('source_url', '').lower()]
yt = [s for s in songs if 'youtube' in s.get('source_url', '').lower()]

print(f"Reddit songs: {len(reddit)}")
print(f"YouTube songs: {len(yt)}")
print(f"Total: {len(songs)}")

print("\n" + "="*60)
print("SAMPLE YOUTUBE COMMENTS:")
print("="*60)

for s in yt[:10]:
    comment = s.get('comment_text', '')[:150]
    print(f"\n{s.get('artist')} - {s.get('song')}")
    print(f"  URL: {s.get('source_url', '')}")
    print(f"  Quote: \"{comment}...\"" if len(s.get('comment_text', '')) > 150 else f"  Quote: \"{comment}\"")
