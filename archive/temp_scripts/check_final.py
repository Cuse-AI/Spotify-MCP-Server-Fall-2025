import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load the FINAL output file
with open('ananki/output/RELEVANCY_PASSED_20251201_222203.json', 'r', encoding='utf-8') as f:
    passed_data = json.load(f)

print("=" * 60)
print("FINAL RELEVANCY CHECK RESULTS")
print("=" * 60)

songs = passed_data.get('songs', [])
score_counts = passed_data.get('score_counts', {})

print(f"\nTotal PASSED songs: {len(songs)}")
print(f"\nScore Distribution:")

total_by_score = {5: 0, 4: 0, 3: 0, 2: 0}
for song in songs:
    score = song.get('relevancy_score', 0)
    if score in total_by_score:
        total_by_score[score] += 1

for score in [5, 4, 3, 2]:
    count = total_by_score[score]
    pct = (count / len(songs) * 100) if songs else 0
    print(f"  Score {score}: {count} ({pct:.1f}%)")

three_plus = total_by_score[5] + total_by_score[4] + total_by_score[3]
two_plus = three_plus + total_by_score[2]

print(f"\n" + "=" * 60)
print(f"If we keep 3+ only: {three_plus} songs")
print(f"If we keep 2+ (current): {two_plus} songs")
print("=" * 60)
