import json
import sys
import random
sys.stdout.reconfigure(encoding='utf-8')

# Load the checkpoint
with open('ananki/output/RELEVANCY_CHECKPOINT_20251201_201014.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get all 2s
twos = [s for s in data['passed'] if s.get('relevancy_score') == 2]

print(f"Total score 2 songs: {len(twos)}")
print()
print("=" * 70)
print("10 RANDOM SCORE 2 EXAMPLES - You decide if they stay or go!")
print("=" * 70)

random.seed(12345)
samples = random.sample(twos, min(10, len(twos)))

for i, song in enumerate(samples, 1):
    artist = song.get('artist', 'Unknown')[:30]
    title = song.get('song', 'Unknown')[:35]
    comment = song.get('comment_text', '')[:300]
    vibe = song.get('mapped_subvibe', song.get('current_vibe', '?'))
    print(f"\n{i}. {artist} - {title}")
    print(f"   Vibe: {vibe}")
    print(f"   \"{comment}\"")
    print()
