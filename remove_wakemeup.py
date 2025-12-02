import json

t = json.load(open('core/tapestry.json', encoding='utf-8'))
vibe = 'Chill - Sunday'
original = len(t['vibes'][vibe]['songs'])
t['vibes'][vibe]['songs'] = [s for s in t['vibes'][vibe]['songs'] if not ('Wake Me Up' in s.get('song','') and 'PANG' in s.get('song',''))]
removed = original - len(t['vibes'][vibe]['songs'])
print(f'Removed {removed} song(s) from {vibe}')

json.dump(t, open('core/tapestry.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('Saved tapestry.json!')
