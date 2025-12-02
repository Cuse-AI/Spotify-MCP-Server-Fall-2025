import json

# Load the data
with open('ananki_outputs/emotional_manifold_COMPLETE.json', 'r', encoding='utf-8') as f:
    manifold = json.load(f)

with open('ananki_outputs/central_vibe_relationships.json', 'r', encoding='utf-8') as f:
    relationships = json.load(f)

# Read the HTML template
with open('create_interactive_map.html', 'r', encoding='utf-8') as f:
    html_template = f.read()

# Inject the data
html_with_data = html_template.replace(
    'MANIFOLD_DATA_PLACEHOLDER',
    json.dumps(manifold)
).replace(
    'RELATIONSHIPS_DATA_PLACEHOLDER',
    json.dumps(relationships)
)

# Save the complete HTML file
with open('ananki_outputs/interactive_tapestry_map.html', 'w', encoding='utf-8') as f:
    f.write(html_with_data)

print('\nInteractive map created!')
print('Open this file in your browser:')
print('ananki_outputs/interactive_tapestry_map.html')
