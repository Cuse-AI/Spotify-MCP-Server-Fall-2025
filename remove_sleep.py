import json

t = json.load(open('core/tapestry.json', encoding='utf-8'))
vibe = 'Night - Sleep'
original = len(t['vibes'][vibe]['songs'])
t['vibes'][vibe]['songs'] = [s for s in t['vibes'][vibe]['songs'] if 'Sleep Instantly' not in s.get('song','')]
removed = original - len(t['vibes'][vibe]['songs'])
print(f'Removed {removed} song(s) from {vibe}')

json.dump(t, open('core/tapestry.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('Saved!')
