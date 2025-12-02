import json
from pathlib import Path

# Load checkpoint
checkpoint_path = "ananki/output/RELEVANCY_CHECKPOINT_20251201_201014.json"
with open(checkpoint_path, 'r', encoding='utf-8') as f:
    checkpoint = json.load(f)

print(f"Checkpoint processed: {checkpoint['processed']} / {checkpoint['total']}")
print(f"Passed in checkpoint: {len(checkpoint['passed'])}")
print(f"Failed in checkpoint: {len(checkpoint['failed'])}")

# Load tapestry
tapestry_path = "core/tapestry.json"
with open(tapestry_path, 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Count songs in tapestry
total_songs = 0
for vibe_name, vibe_data in tapestry['vibes'].items():
    total_songs += len(vibe_data.get('songs', []))

print(f"\nCurrent tapestry total songs: {total_songs}")

if total_songs == checkpoint['total']:
    print("✅ Tapestry matches checkpoint - safe to resume!")
else:
    print("⚠️ Tapestry has changed since checkpoint was created")
