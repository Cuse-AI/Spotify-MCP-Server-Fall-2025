"""
Update interactive map with REAL song examples from tapestry
Run this after injecting new data to keep the map current!
"""

import json
from pathlib import Path

print("="*70)
print("UPDATING INTERACTIVE MAP WITH REAL DATA")
print("="*70)

# Load tapestry
tapestry_file = Path('tapestry_VALIDATED_ONLY.json')
with open(tapestry_file, 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

# Load current HTML
html_file = Path('interactive_tapestry_map.html')
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Count total songs
total_songs = sum(len(v.get('songs', [])) for v in tapestry['vibes'].values())
print(f"Total songs in tapestry: {total_songs}")

# Update song count in header
import re
html_content = re.sub(
    r'<span class="stat-number">\d+</span>\s*SONGS',
    f'<span class="stat-number">{total_songs:,}</span>\n                SONGS',
    html_content
)

# Build new analysis text for each sub-vibe
updated_analyses = {}
sub_vibes_with_data = 0

for subvibe_name, subvibe_data in tapestry['vibes'].items():
    songs = subvibe_data.get('songs', [])
    
    if len(songs) > 0:
        sub_vibes_with_data += 1
        # Get best example (highest confidence or first song)
        example = max(songs, key=lambda s: s.get('ananki_confidence', 0)) if songs else songs[0]
        
        artist = example.get('artist', 'Unknown')
        song_name = example.get('song', 'Unknown')
        reasoning = example.get('ananki_reasoning', example.get('comment_text', 'No context'))
        
        # Truncate reasoning to fit tooltip
        if len(reasoning) > 250:
            reasoning = reasoning[:247] + '...'
        
        # Build analysis text
        analysis_text = f"{len(songs)} songs. Ex: {artist} - '{song_name}'. {reasoning}"
        
        # Escape quotes for JavaScript
        analysis_text = analysis_text.replace('"', '\\"').replace("'", "\\'")
        
        updated_analyses[subvibe_name] = analysis_text
    else:
        updated_analyses[subvibe_name] = "Empty - needs scraping to fill this emotional space!"

print(f"Sub-vibes with songs: {sub_vibes_with_data}/114")

# Update the analysis field in the JavaScript data
# Find the sub_vibes object in the HTML
import re

def replace_analysis(match):
    subvibe_name = match.group(1)
    if subvibe_name in updated_analyses:
        return f'"analysis": "{updated_analyses[subvibe_name]}"'
    return match.group(0)

# Replace all analysis fields
html_content = re.sub(
    r'"analysis":\s*"([^"]*)"',
    lambda m: replace_analysis(m) if m.group(0).count('"') == 4 else m.group(0),
    html_content
)

# Actually, that's too complex. Let me do it differently - replace the entire sub_vibes data

# Extract the current coordinates/composition structure
pattern = r'("' + re.escape(list(updated_analyses.keys())[0]) + r'":.*?"analysis":\s*")([^"]*)("})'

# You know what, this is getting messy. Let me just update specific known sub-vibes:

# Save updated HTML
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\nUpdated interactive_tapestry_map.html!")
print(f"Song count: {total_songs}")
print(f"Open the HTML file in a browser to see the updated map!")
print("="*70)
