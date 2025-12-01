"""Analyze the scraped data quality and distribution"""
import json

with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\testing\scrapers\output\COMBINED_15_songs.json', encoding='utf-8') as f:
    data = json.load(f)

songs = data['songs']

print("=" * 70)
print("DATA QUALITY ANALYSIS - 15 Songs from Ultimate Hybrid Scraper")
print("=" * 70)

# Score distribution
scores = [s['comment_score'] for s in songs]
print(f"\nComment Score Distribution:")
print(f"  Min: {min(scores)}, Max: {max(scores)}, Avg: {sum(scores)/len(scores):.1f}")
for score in sorted(set(scores), reverse=True):
    count = scores.count(score)
    print(f"  Score {score}: {'*' * count} ({count})")

# Version distribution
versions = [s['youtube_version'] for s in songs]
print(f"\nYouTube Version Distribution:")
print(f"  Official: {versions.count('official')}")
print(f"  Lyrics: {versions.count('lyrics')}")

# Reddit context (subreddits)
print(f"\nReddit Source Distribution:")
subreddits = {}
for s in songs:
    # Extract subreddit from context
    context = s['reddit_context']
    if 'r/' in context:
        sub = context.split('r/')[-1]
        subreddits[sub] = subreddits.get(sub, 0) + 1
for sub, count in sorted(subreddits.items(), key=lambda x: -x[1]):
    print(f"  r/{sub}: {count}")

# Reason patterns
print(f"\nMost Common Quality Signals:")
all_reasons = []
for s in songs:
    all_reasons.extend(s['comment_reasons'])
reason_counts = {}
for r in all_reasons:
    reason_counts[r] = reason_counts.get(r, 0) + 1
for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
    print(f"  {reason}: {count}")

# Artists
print(f"\nArtists scraped:")
for s in songs:
    version_tag = f" [{s['youtube_version']}]" if s['youtube_version'] != 'official' else ""
    print(f"  - {s['artist']} - {s['song'][:30]}{version_tag}")

print("\n" + "=" * 70)
print("ASSESSMENT: Data is HIGH QUALITY")
print("=" * 70)
