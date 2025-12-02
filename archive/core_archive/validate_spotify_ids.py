"""
Validate Spotify IDs in the tapestry by checking random batches.
Outputs validation report to file.
"""

import json
import random

def main():
    # Load tapestry
    with open('tapestry_quality_final.json', 'r', encoding='utf-8') as f:
        tapestry = json.load(f)

    vibes = tapestry.get('vibes', {})

    # Collect all songs
    all_songs = []
    for vibe_name, vibe_data in vibes.items():
        if isinstance(vibe_data, dict) and 'songs' in vibe_data:
            for song in vibe_data['songs']:
                all_songs.append({
                    'artist': song.get('artist', 'Unknown'),
                    'song': song.get('song', 'Unknown'),
                    'spotify_id': song.get('spotify_id', ''),
                    'vibe': vibe_name,
                    'comment_score': song.get('comment_score', 0),
                    'spotify_url': f"https://open.spotify.com/track/{song.get('spotify_id', '')}"
                })

    total_songs = len(all_songs)

    # Get random sample
    sample_size = 50
    sample = random.sample(all_songs, min(sample_size, total_songs))

    # Get high priority songs (high comment scores)
    priority = sorted(all_songs, key=lambda x: x['comment_score'], reverse=True)[:20]

    # Write report
    with open('spotify_validation_report.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("SPOTIFY ID VALIDATION REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total songs in tapestry: {total_songs}\n\n")

        f.write("RANDOM SAMPLE (50 songs to test):\n")
        f.write("=" * 70 + "\n\n")

        for i, song in enumerate(sample, 1):
            f.write(f"{i}. {song['artist']} - {song['song']}\n")
            f.write(f"   Vibe: {song['vibe']}\n")
            f.write(f"   URL: {song['spotify_url']}\n\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("HIGH-PRIORITY SONGS (Top 20 by comment score):\n")
        f.write("=" * 70 + "\n\n")

        for i, song in enumerate(priority, 1):
            f.write(f"{i}. {song['artist']} - {song['song']}\n")
            f.write(f"   Score: {song['comment_score']:,}\n")
            f.write(f"   URL: {song['spotify_url']}\n\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("VALIDATION INSTRUCTIONS:\n")
        f.write("=" * 70 + "\n\n")
        f.write("1. Copy each URL and paste into your browser\n")
        f.write("2. Check if the song loads correctly on Spotify\n")
        f.write("3. Verify artist and song name match\n")
        f.write("4. Note any broken links or mismatches\n\n")
        f.write("If you find broken IDs:\n")
        f.write("- Search for correct song on Spotify\n")
        f.write("- Extract track ID from URL\n")
        f.write("- Update tapestry_quality_final.json\n")
        f.write("- Run sync_to_webapp.py\n")

    print("[OK] Validation report saved to: spotify_validation_report.txt")
    print(f"[OK] Total songs: {total_songs}")
    print(f"[OK] Random sample: {len(sample)} songs")
    print(f"[OK] Priority songs: {len(priority)} songs")

if __name__ == '__main__':
    main()
