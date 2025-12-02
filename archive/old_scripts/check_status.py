import json
from pathlib import Path

# Tapestry count
t = json.load(open('core/tapestry.json', encoding='utf-8'))
total = sum(len(v['songs']) for v in t['vibes'].values())
print(f'Tapestry: {total:,} songs')

# Files in 2_deduped ready to process
print('\n=== DEDUPED FILES (ready for Ananki) ===')
deduped_dir = Path('data/2_deduped')
total_ready = 0
for f in sorted(deduped_dir.glob('*.json')):
    if 'CHECKPOINT' in f.name:
        continue
    try:
        data = json.load(open(f, encoding='utf-8'))
        count = len(data.get('songs', []))
        total_ready += count
        print(f'{f.name}: {count} songs')
    except:
        pass

print(f'\nTOTAL READY: {total_ready} songs (~${total_ready * 0.003:.2f} Ananki cost)')
