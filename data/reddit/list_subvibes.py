"""Extract all sub-vibes from tapestry"""
import json
from pathlib import Path

tapestry_file = Path('../ananki_outputs/tapestry_VALIDATED_ONLY.json')
with open(tapestry_file, 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

all_subvibes = sorted(tapestry['vibes'].keys())

print(f"ALL {len(all_subvibes)} SUB-VIBES:\n")

grouped = {}
for sv in all_subvibes:
    central = sv.split(' - ')[0] if ' - ' in sv else 'Other'
    if central not in grouped:
        grouped[central] = []
    grouped[central].append(sv)

for central, subvibes in sorted(grouped.items()):
    print(f"\n{central} ({len(subvibes)}):")
    for sv in subvibes:
        print(f"  {sv}")
