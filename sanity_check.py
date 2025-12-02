import json

t = json.load(open('core/tapestry.json', encoding='utf-8'))
total = sum(len(v.get('songs', [])) for v in t['vibes'].values())
print(f'Tapestry: {total} songs')

s = list(t['vibes'].values())[0]['songs'][0]
print(f'Has coordinates: {bool(s.get("coordinates"))}')
print(f'Has emotional_composition: {bool(s.get("emotional_composition"))}')

# Check webapp copies
import os
webapp_server = 'code/web/server/core/tapestry.json'
webapp_public = 'code/web/public/static/tapestry.json'
print(f'Webapp server copy exists: {os.path.exists(webapp_server)}')
print(f'Webapp public copy exists: {os.path.exists(webapp_public)}')
