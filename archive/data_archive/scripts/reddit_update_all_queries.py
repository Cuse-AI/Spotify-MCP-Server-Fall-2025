"""
Update all Reddit scrapers with better emotional context queries
Focus on posts where people DESCRIBE their feelings, not just ask for genre lists
"""

from pathlib import Path

# Better queries for each vibe - focusing on emotional states
BETTER_QUERIES = {
    'angry': [
        'pissed off need angry music',
        'furious need aggressive songs',
        'rage workout music',
        'angry breakup songs',
        'frustrated need heavy metal',
        'mad need loud music',
    ],
    'dark': [
        'feeling depressed need dark music',
        'going through dark time need songs',
        'gothic moody music',
        'haunting atmospheric songs',
        'eerie unsettling music',
        'black metal recommendations',
    ],
    'drive': [
        'road trip hype music',
        'driving fast need adrenaline songs',
        'highway cruising music',
        'long drive energetic playlist',
        'car rides motivation music',
        'need pump up driving songs',
    ],
    'happy': [
        'feeling great need upbeat music',
        'celebrating good news songs',
        'cheerful positive vibes',
        'happy mood boost music',
        'feeling optimistic need happy songs',
        'good day uplifting music',
    ],
    'night': [
        'late night driving alone music',
        'midnight melancholic songs',
        '3am cant sleep music',
        'nighttime introspective playlist',
        'dark night atmospheric music',
        'nocturnal moody vibes',
    ],
    'party': [
        'pregame hype music',
        'getting ready to go out songs',
        'club bangers playlist',
        'party starter high energy',
        'drunk dancing music',
        'house party playlist',
    ],
    'romantic': [
        'falling in love songs',
        'first date music',
        'crush butterflies music',
        'romantic evening dinner songs',
        'love confession music',
        'slow dance romantic',
    ],
    'sad': [
        'heartbroken need sad songs',
        'crying in my room music',
        'breakup devastated playlist',
        'grieving loss sad music',
        'feeling lonely depressing songs',
        'tears emotional music',
    ],
}

# Update each scraper
scraper_dir = Path(__file__).parent

for vibe, new_queries in BETTER_QUERIES.items():
    scraper_file = scraper_dir / f'scrape_{vibe}.py'

    if not scraper_file.exists():
        print(f"SKIP: {vibe} (file doesn't exist)")
        continue

    print(f"Updating: {vibe}")

    # Read file
    with open(scraper_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the queries list
    in_queries = False
    start_line = None
    end_line = None
    indent = None

    for i, line in enumerate(lines):
        if 'queries = [' in line:
            in_queries = True
            start_line = i
            # Detect indentation
            indent = len(line) - len(line.lstrip())
            continue

        if in_queries and ']' in line and 'queries' not in line:
            end_line = i
            break

    if start_line is None or end_line is None:
        print(f"  ERROR: Couldn't find queries list")
        continue

    # Build new queries section
    indent_str = ' ' * indent
    new_lines = [f"{indent_str}queries = [\n"]
    new_lines.append(f"{indent_str}    # Emotional state descriptions (better context!)\n")
    for query in new_queries:
        new_lines.append(f"{indent_str}    '{query}',\n")
    new_lines.append(f"{indent_str}]\n")

    # Replace old queries with new
    new_file_lines = lines[:start_line] + new_lines + lines[end_line+1:]

    # Write updated file
    with open(scraper_file, 'w', encoding='utf-8') as f:
        f.writelines(new_file_lines)

    print(f"  UPDATED with {len(new_queries)} emotional queries")

print("\nAll scrapers updated with better emotional context queries!")
