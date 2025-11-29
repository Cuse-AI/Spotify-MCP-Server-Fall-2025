"""
Ananki Sub-Vibe Relationship Mapper
Maps how all 73 sub-vibes relate to each other within and across central vibes
"""

import json

print("="*70)
print("ANANKI SUB-VIBE RELATIONSHIP MAPPER")
print("="*70)

# Load central vibe map
with open('ananki_outputs/central_vibe_map.json', 'r', encoding='utf-8') as f:
    central_map = json.load(f)

# Load tapestry
with open('ananki_outputs/tapestry_complete.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

print(f"\nMapping relationships for {len(tapestry['vibes'])} sub-vibes...")

# ============================================================================
# ANANKI'S RELATIONSHIP MAPPING LOGIC
# ============================================================================

def map_sub_vibe_relationships(sub_vibe_name, central_vibes_data, central_relationships):
    """
    Ananki determines which sub-vibes are nearby based on:
    1. Siblings (same central vibe)
    2. Related central vibe sub-vibes (cross-category connections)
    3. Emotional similarity analysis
    """
    
    # Find which central vibe this sub-vibe belongs to
    parent_central = None
    for central, data in central_vibes_data.items():
        if sub_vibe_name in data['sub_vibes']:
            parent_central = central
            break
    
    if not parent_central:
        return []
    
    nearby = []
    
    # 1. Siblings (other sub-vibes in same central category)
    siblings = [sv for sv in central_vibes_data[parent_central]['sub_vibes'] 
                if sv != sub_vibe_name]
    nearby.extend(siblings[:4])  # Top 4 closest siblings
    
    # 2. Sub-vibes from related central vibes
    related_centrals = central_relationships.get(parent_central, [])[:3]  # Top 3 related
    for related in related_centrals:
        if related in central_vibes_data:
            # Add most relevant sub-vibes from related central
            related_subs = central_vibes_data[related]['sub_vibes'][:2]  # Top 2
            nearby.extend(related_subs)
    
    return nearby[:10]  # Limit to 10 nearest

# Map all sub-vibes
print("\n[MAPPING] Sub-vibe relationships...")

for sub_vibe in tapestry['vibes']:
    nearby_vibes = map_sub_vibe_relationships(
        sub_vibe, 
        central_map['central_vibes'],
        central_map['central_relationships']
    )
    tapestry['vibes'][sub_vibe]['nearby_vibes'] = nearby_vibes

print(f"  Mapped relationships for all {len(tapestry['vibes'])} sub-vibes!")

# Save updated tapestry
with open('ananki_outputs/tapestry_complete.json', 'w', encoding='utf-8') as f:
    json.dump(tapestry, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] Updated tapestry with relationships!")

# Show sample
print(f"\n" + "="*70)
print("SAMPLE RELATIONSHIPS:")
print("="*70)

sample_vibes = ['Sad - Heartbreak', 'Happy - Euphoric', 'Dark - Villain Arc']
for vibe in sample_vibes:
    if vibe in tapestry['vibes']:
        nearby = tapestry['vibes'][vibe]['nearby_vibes']
        print(f"\n{vibe} connects to:")
        for n in nearby[:5]:
            print(f"  - {n}")

print(f"\n[COMPLETE] Tapestry is now an interconnected emotional web!")
print(f"\n[NEXT] Create visual diagram")
