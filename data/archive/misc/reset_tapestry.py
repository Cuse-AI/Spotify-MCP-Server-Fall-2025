"""
Reset tapestry to empty structure, then re-inject with full context
"""
import json
from pathlib import Path
import shutil

# Load current tapestry
tapestry_file = Path(__file__).parent.parent / 'ananki_outputs' / 'tapestry_VALIDATED_ONLY.json'
with open(tapestry_file, 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Backup
backup = tapestry_file.parent / 'tapestry_BEFORE_CONTEXT_REINJECTION.json'
shutil.copy(tapestry_file, backup)

# Empty all songs but keep structure
for vibe in tapestry['vibes'].values():
    vibe['songs'] = []

# Save empty tapestry
with open(tapestry_file, 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print("Tapestry reset - all songs removed, structure preserved")
print(f"Backup: {backup}")
print("Ready for re-injection with full context!")
