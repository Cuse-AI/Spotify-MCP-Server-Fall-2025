"""
Tapestry Analysis - Assess data quality and validation coverage
"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_tapestry():
    tapestry_file = Path('C:/Users/sw13t/Desktop/Coding/CuseAI/SpotifyMSP/Spotify-MCP-Server-Fall-2025/data/ananki_outputs/tapestry_CLEANED_WITH_SPOTIFY.json')
    
    with open(tapestry_file, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Overall stats
    vibe_stats = {}
    total_songs = 0
    validated_songs = 0
    
    for vibe, data in tapestry['vibes'].items():
        songs = data.get('songs', [])
        vibe_stats[vibe] = {
            'total': len(songs),
            'validated': sum(1 for s in songs if s.get('spotify_id') or s.get('youtube_id')),
            'unvalidated': sum(1 for s in songs if not s.get('spotify_id') and not s.get('youtube_id'))
        }
        total_songs += len(songs)
        validated_songs += vibe_stats[vibe]['validated']
    
    print("\n" + "="*70)
    print("TAPESTRY HEALTH REPORT")
    print("="*70)
    print(f"\nTotal vibes: {len(tapestry['vibes'])}")
    print(f"Total songs: {total_songs:,}")
    print(f"Validated songs: {validated_songs:,} ({validated_songs/total_songs*100:.1f}%)")
    print(f"Unvalidated songs: {total_songs - validated_songs:,} ({(total_songs-validated_songs)/total_songs*100:.1f}%)")
    
    # Top vibes by size
    print("\n" + "="*70)
    print("TOP 15 VIBES BY SONG COUNT:")
    print("="*70)
    sorted_vibes = sorted(vibe_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:15]
    for vibe, stats in sorted_vibes:
        val_pct = stats['validated']/stats['total']*100 if stats['total'] > 0 else 0
        print(f"{vibe[:45]:45s} {stats['total']:5,d} songs  ({stats['validated']:4d} validated = {val_pct:5.1f}%)")
    
    # Quality issues analysis
    print("\n" + "="*70)
    print("DATA QUALITY INDICATORS:")
    print("="*70)
    
    # Sample some unvalidated songs to check quality
    sample_issues = []
    for vibe, data in list(tapestry['vibes'].items())[:5]:  # Check first 5 vibes
        for song in data.get('songs', [])[:10]:  # Check first 10 songs per vibe
            if not song.get('spotify_id'):
                # Check for quality issues
                artist = song.get('artist', '')
                song_name = song.get('song', '')
                
                issues = []
                if len(artist) < 2:
                    issues.append("Artist name too short")
                if len(song_name) < 2:
                    issues.append("Song name too short")
                if len(artist.split()) > 5:
                    issues.append("Artist name likely garbled")
                if any(c in artist.lower() for c in ['adjacent', 'named', 'colored']):
                    issues.append("Extraction artifact detected")
                
                if issues:
                    sample_issues.append({
                        'vibe': vibe,
                        'artist': artist[:40],
                        'song': song_name[:40],
                        'issues': issues
                    })
    
    if sample_issues:
        print(f"\nFound {len(sample_issues)} quality issues in sample:")
        for issue in sample_issues[:5]:
            print(f"  [{issue['vibe'][:30]}] \"{issue['artist']}\" - \"{issue['song']}\"")
            print(f"    Issues: {', '.join(issue['issues'])}")
    
    # Validation rate comparison
    print("\n" + "="*70)
    print("VALIDATION SUCCESS RATES BY VIBE CATEGORY:")
    print("="*70)
    
    sad_vibes = {k: v for k, v in vibe_stats.items() if k.startswith('Sad')}
    for vibe, stats in sorted(sad_vibes.items(), key=lambda x: x[1]['total'], reverse=True):
        val_rate = stats['validated']/stats['total']*100 if stats['total'] > 0 else 0
        print(f"{vibe[:45]:45s} {val_rate:5.1f}% validated")
    
    return {
        'total_songs': total_songs,
        'validated_songs': validated_songs,
        'validation_rate': validated_songs/total_songs*100,
        'vibe_stats': vibe_stats
    }


if __name__ == '__main__':
    stats = analyze_tapestry()
