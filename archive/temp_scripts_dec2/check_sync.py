import json

# Check main tapestry
main = json.load(open('core/tapestry.json', encoding='utf-8'))
main_count = sum(len(v.get('songs', [])) for v in main['vibes'].values())
print(f'Main tapestry: {main_count} songs')

# Check web tapestry
web = json.load(open('code/web/core/tapestry.json', encoding='utf-8'))
web_count = sum(len(v.get('songs', [])) for v in web['vibes'].values())
print(f'Web tapestry: {web_count} songs')

print(f'Match: {main_count == web_count}')
