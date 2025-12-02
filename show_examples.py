import json
import sys
import random
sys.stdout.reconfigure(encoding='utf-8')

# Load the checkpoint
with open('ananki/output/RELEVANCY_CHECKPOINT_20251201_201014.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Group ALL passed songs by score
by_score = {5: [], 4: [], 3: [], 2: []}
for song in data['passed']:
    score = song.get('relevancy_score', 0)
    if score in by_score:
        by_score[score].append(song)

print(f"Total songs per score: 5={len(by_score[5])}, 4={len(by_score[4])}, 3={len(by_score[3])}, 2={len(by_score[2])}")
print()

# Shuffle and pick random ones
random.seed(42069)  # reproducible but different

print("=" * 70)
print("RANDOM SLICE OF EXAMPLES")
print("=" * 70)

for score in [5, 4, 3, 2]:
    print(f"\n{'='*70}")
    print(f"SCORE {score} - Random samples from {len(by_score[score])} songs:")
    print("=" * 70)
    
    # Pick 3 random from middle/end
    if len(by_score[score]) > 6:
        samples = random.sample(by_score[score][len(by_score[score])//2:], min(3, len(by_score[score])//2))
    else:
        samples = by_score[score][:3]
    
    for song in samples:
        artist = song.get('artist', 'Unknown')[:30]
        title = song.get('song', 'Unknown')[:35]
        comment = song.get('comment_text', '')[:250]
        vibe = song.get('mapped_subvibe', song.get('current_vibe', '?'))
        print(f"\n>> {artist} - {title}")
        print(f"   Vibe: {vibe}")
        print(f"   \"{comment}\"")

# Also show random FAILs from different part
print(f"\n{'='*70}")
print(f"SCORE 1 (FAIL) - Random samples from {len(data['failed'])} failed:")
print("=" * 70)

failed_samples = random.sample(data['failed'][len(data['failed'])//2:], min(4, len(data['failed'])//2))
for item in failed_samples:
    song = item['song']
    artist = song.get('artist', 'Unknown')[:30]
    title = song.get('song', 'Unknown')[:35]
    comment = song.get('comment_text', '')[:200]
    reason = item.get('reason', 'No reason')
    print(f"\n>> {artist} - {title}")
    print(f"   Reason: {reason}")
    print(f"   \"{comment}\"")
