import json

# Check original tapestry backup
original = json.load(open('core/tapestry_backup_4976.json', encoding='utf-8'))
original_vibes = set(original['vibes'].keys())
print(f"Original tapestry: {len(original_vibes)} vibes")

# Check current quality tapestry
current = json.load(open('core/tapestry.json', encoding='utf-8'))
current_vibes = set(current['vibes'].keys())
print(f"Current tapestry: {len(current_vibes)} vibes")

# Which vibes were lost?
lost_vibes = original_vibes - current_vibes
print(f"\nLost {len(lost_vibes)} vibes:")
for v in sorted(lost_vibes):
    # Check how many songs were in each lost vibe
    count = len(original['vibes'][v].get('songs', []))
    print(f"  - {v} ({count} songs)")
