import re

files_to_update = {
    'scrape_sad.py': ['childhood nostalgia music', '90s nostalgia songs', '2000s throwback', 'yearning for the past'],
    'scrape_night.py': ['introspective deep thoughts', 'philosophical music', 'existential songs', 'soul searching'],
    'scrape_energy.py': ['angry workout music', 'confident boss songs', 'chaotic energy music', 'excited hype'],
    'scrape_happy.py': ['grateful thankful music', 'hopeful optimistic songs', 'playful fun music'],
    'scrape_chill.py': ['peaceful meditative music', 'serene calm songs']
}

for filename, new_queries in files_to_update.items():
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the queries list
        match = re.search(r'(queries = \[)(.*?)(\])', content, re.DOTALL)
        if match:
            start, queries_text, end = match.groups()
            
            # Add new queries before the closing bracket
            for query in new_queries:
                queries_text += f",\n            '{query}'"
            
            # Replace in content
            new_content = content.replace(match.group(0), start + queries_text + end)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Updated {filename} - added {len(new_queries)} queries")
        else:
            print(f"Could not find queries in {filename}")
            
    except Exception as e:
        print(f"Error updating {filename}: {e}")

print("\nAll Reddit scrapers updated!")
