import json

with open('ananki_outputs/tapestry_complete.json', encoding='utf-8') as f:
    t = json.load(f)

print(f'\n=== TAPESTRY STRUCTURE CHECK ===')
print(f'Type: {type(t)}')
print(f'Keys: {list(t.keys())}')
print(f'\nFirst value structure:')
first_key = list(t.keys())[0]
print(f'Key: {first_key}')
print(f'Value type: {type(t[first_key])}')
if isinstance(t[first_key], dict):
    print(f'Value keys: {list(t[first_key].keys())[:10]}')
