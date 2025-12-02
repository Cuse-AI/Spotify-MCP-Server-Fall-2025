import json

with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\testing\scraper_test_2024_11_30\RAW_hybrid_scraper_20251130_013915.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("METADATA:")
for k, v in data['metadata'].items():
    print(f"  {k}: {v}")

print()
print("SAMPLE SONGS (first 5):")
print("=" * 70)
for song in data['songs'][:5]:
    print()
    print(f"Artist: {song['artist']}")
    print(f"Song: {song['song']}")
    print(f"Score: {song['comment_score']}")
    print(f"Reasons: {song['comment_reasons']}")
    comment = song['comment_text'][:200].replace('\n', ' ')
    print(f"Comment: {comment}...")
    print("-" * 70)
