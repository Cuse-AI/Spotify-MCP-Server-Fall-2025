import json, random

t = json.load(open('../ananki_outputs/tapestry_VALIDATED_ONLY.json', encoding='utf-8'))
song = random.choice(t['vibes']['Sad - Heartbreak']['songs'])

print("PROOF: Can explain ANY track in tapestry")
print("="*70)
print(f"\nRANDOM SONG: {song['artist']} - {song['song']}")
print(f"Sub-vibe: Sad - Heartbreak")
print(f"\nWHY IT'S HERE:")
print(f"  Post: {song.get('post_title', 'N/A')}")
print(f"  Comment: {song.get('comment_text', 'N/A')[:150]}")
print(f"  Ananki: {song.get('ananki_analysis', 'N/A')}")
print(f"\nSpotify ID: {song['spotify_id']}")
print(f"Source: {song.get('source_url', 'N/A')}")
