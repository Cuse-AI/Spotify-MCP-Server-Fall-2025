"""
UPDATE MANIFOLD - Apply new emotional positions
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

NEW_POSITIONS = {
    "Happy":    {"x": 500, "y": 200},
    "Party":    {"x": 300, "y": 250},
    "Chill":    {"x": 700, "y": 250},
    "Energy":   {"x": 250, "y": 450},
    "Romantic": {"x": 750, "y": 450},
    "Sad":      {"x": 500, "y": 600},
    "Drive":    {"x": 200, "y": 650},
    "Dark":     {"x": 350, "y": 800},
    "Night":    {"x": 550, "y": 850},
}

project_root = Path(__file__).parent
manifold_path = project_root / "data" / "manifold" / "emotional_manifold_COMPLETE.json"
backup_path = project_root / "data" / "manifold" / f"emotional_manifold_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# Load current manifold
with open(manifold_path, 'r', encoding='utf-8') as f:
    manifold = json.load(f)

# Backup
shutil.copy2(manifold_path, backup_path)
print(f"[BACKUP] Saved to {backup_path.name}")

# Update meta-vibe positions
print("\n[UPDATE] Meta-vibe positions:")
for vibe, pos in NEW_POSITIONS.items():
    old = manifold['central_vibes']['positions'].get(vibe, {})
    print(f"  {vibe}: ({old.get('x',0):.0f},{old.get('y',0):.0f}) -> ({pos['x']},{pos['y']})")

manifold['central_vibes']['positions'] = NEW_POSITIONS

# Recalculate all sub-vibe coordinates
print("\n[RECALCULATE] Sub-vibe coordinates:")
count = 0
for sv_name, sv_data in manifold['sub_vibes'].items():
    composition = sv_data.get('emotional_composition', {})
    
    if composition:
        total_x = 0
        total_y = 0
        total_weight = 0
        
        for meta_vibe, weight in composition.items():
            if meta_vibe in NEW_POSITIONS:
                pos = NEW_POSITIONS[meta_vibe]
                total_x += pos['x'] * weight
                total_y += pos['y'] * weight
                total_weight += weight
        
        if total_weight > 0:
            new_x = round(total_x / total_weight, 2)
            new_y = round(total_y / total_weight, 2)
            sv_data['coordinates'] = {'x': new_x, 'y': new_y}
            count += 1

print(f"  Updated {count} sub-vibes")

# Update metadata
manifold['metadata']['last_updated'] = datetime.now().isoformat()
manifold['metadata']['manifold_version'] = "2.0"
manifold['metadata']['redesign_note'] = "Repositioned meta-vibes for emotional adjacency logic"

# Save
with open(manifold_path, 'w', encoding='utf-8') as f:
    json.dump(manifold, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] Updated manifold!")
print(f"\n[NEXT STEPS]")
print(f"  1. Run sync_to_webapp.py to push to webapp")
print(f"  2. Run coordinate helper on tapestry to update all song coordinates")
