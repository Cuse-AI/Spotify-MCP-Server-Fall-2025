import json

# Load updated data
with open('ananki_outputs/emotional_manifold_COMPLETE.json', 'r', encoding='utf-8') as f:
    manifold = json.load(f)

with open('ananki_outputs/central_vibe_relationships.json', 'r', encoding='utf-8') as f:
    relationships = json.load(f)

# Read template
with open('scripts/visualization/tapestry_demo_template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Inject data
html = html.replace('MANIFOLD_DATA_PLACEHOLDER', json.dumps(manifold))
html = html.replace('RELATIONSHIPS_DATA_PLACEHOLDER', json.dumps(relationships))

# Save to SAME location
with open('ananki_outputs/interactive_tapestry_map.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated map with drag-to-pan and scroll-to-zoom!')
print('SAME FILE - just refresh your browser!')
