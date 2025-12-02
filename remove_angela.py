import json

# Load tapestry
with open('core/tapestry.json', 'r', encoding='utf-8') as f:
    t = json.load(f)

# Find and remove Angela by The Lumineers
vibe = 'Sad - Nostalgic Sad'
if vibe in t['vibes']:
    original_count = len(t['vibes'][vibe]['songs'])
    t['vibes'][vibe]['songs'] = [s for s in t['vibes'][vibe]['songs'] 
                                  if not (s.get('song') == 'Angela' and 'Lumineers' in s.get('artist', ''))]
    new_count = len(t['vibes'][vibe]['songs'])
    print(f"Removed {original_count - new_count} song(s) from {vibe}")

# Save
with open('core/tapestry.json', 'w', encoding='utf-8') as f:
    json.dump(t, f, indent=2, ensure_ascii=False)

print("Done! Saved tapestry.json")
